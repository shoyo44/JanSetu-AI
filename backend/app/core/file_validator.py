"""
File Magic & MIME Validator.

Validates uploaded document files via binary magic byte inspection, path traversal
checks, double-extension detection, and size limits to prevent malicious executable
uploads and file spoofing attacks.

Runs completely cross-platform without external C-library / DLL dependencies.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Optional, Set, Tuple

logger = logging.getLogger("docqa.security.file_validator")

# Default file size limit: 50MB
DEFAULT_MAX_SIZE_MB = 50.0

# Permitted file types
ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # docx
    "text/plain",
    "text/markdown",
    "application/json",
    "text/csv",
}

# Dangerous executable and binary signatures
MALICIOUS_MAGIC_SIGNATURES: List[Tuple[bytes, str]] = [
    (b"MZ", "Windows Portable Executable (EXE/DLL)"),
    (b"\x7fELF", "Linux ELF Executable/Binary"),
    (b"\xfe\xed\xfa\xce", "macOS Mach-O 32-bit"),
    (b"\xce\xfa\xed\xfe", "macOS Mach-O 32-bit"),
    (b"\xfe\xed\xfa\xcf", "macOS Mach-O 64-bit"),
    (b"\xcf\xfa\xed\xfe", "macOS Mach-O 64-bit"),
    (b"\x4c\x00\x00\x00\x01\x14\x02\x00", "Windows Shell Link / Shortcut (LNK)"),
    (b"MSCF", "Microsoft Cabinet Archive"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "OLE2 Compound File (legacy MS Office doc with macro capability)"),
]


@dataclass
class FileValidationResult:
    is_valid: bool
    mime_type: str
    file_size_bytes: int
    detected_format: str
    error_message: Optional[str] = None


def sanitize_filename(filename: str) -> str:
    """Neutralize path traversal characters and dangerous control characters."""
    # Strip null bytes and directory components
    clean = filename.replace("\x00", "").strip()
    clean = os.path.basename(clean)
    # Remove potentially dangerous characters
    clean = re.sub(r"[^\w\.\-\s]", "_", clean)
    return clean or "unnamed_document"


def detect_magic_mime(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Inspects header bytes to accurately identify the file's real MIME type.
    Returns (mime_type, format_name).
    """
    if len(file_bytes) == 0:
        return "empty", "Empty File"

    # 1. PDF detection: starts with %PDF-
    if file_bytes.startswith(b"%PDF-"):
        return "application/pdf", "PDF Document"

    # 2. Check for DOCX: ZIP archive starting with PK\x03\x04
    if file_bytes.startswith(b"PK\x03\x04"):
        # Check if it contains word/ in first 4096 bytes (standard OpenXML docx)
        if b"word/" in file_bytes[:4096] or b"[Content_Types].xml" in file_bytes[:4096]:
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Microsoft Word (DOCX)"
        return "application/zip", "Generic ZIP Archive"

    # 3. Check for obvious malicious executable headers
    for sig, desc in MALICIOUS_MAGIC_SIGNATURES:
        if file_bytes.startswith(sig):
            return "application/x-executable", desc

    # 4. Text-based detection (txt, md, json, csv)
    # Check if first 4096 bytes are valid UTF-8/ASCII without null bytes
    sample = file_bytes[:4096]
    if b"\x00" not in sample:
        try:
            decoded = sample.decode("utf-8")
            # If valid JSON
            stripped = decoded.strip()
            if (stripped.startswith("{") and "}" in stripped) or (stripped.startswith("[") and "]" in stripped):
                return "application/json", "JSON Document"
            # Markdown or Plain text
            ext = os.path.splitext(filename.lower())[1]
            if ext in (".md", ".markdown"):
                return "text/markdown", "Markdown Document"
            if ext == ".csv":
                return "text/csv", "CSV Spreadsheet"
            return "text/plain", "Plain Text Document"
        except UnicodeDecodeError:
            pass

    return "application/octet-stream", "Unknown Binary"


def validate_uploaded_file(
    file_bytes: bytes,
    filename: str,
    max_size_mb: Optional[float] = None,
) -> FileValidationResult:
    """
    Comprehensive validation of an uploaded file buffer.

    Checks:
    1. Size limit (default 50MB)
    2. Path traversal & filename spoofing (e.g. evil.exe.pdf)
    3. Magic header byte verification against allowed MIME types
    4. Malicious executable signature blocking
    """
    clean_name = sanitize_filename(filename)
    file_size = len(file_bytes)
    max_bytes = int((max_size_mb or float(os.getenv("MAX_UPLOAD_SIZE_MB", DEFAULT_MAX_SIZE_MB))) * 1024 * 1024)

    # 1. File size checks
    if file_size == 0:
        return FileValidationResult(
            is_valid=False,
            mime_type="empty",
            file_size_bytes=0,
            detected_format="Empty",
            error_message="Uploaded file is empty (0 bytes).",
        )

    if file_size > max_bytes:
        limit_mb = max_bytes / (1024 * 1024)
        actual_mb = round(file_size / (1024 * 1024), 2)
        return FileValidationResult(
            is_valid=False,
            mime_type="oversized",
            file_size_bytes=file_size,
            detected_format="Oversized",
            error_message=f"File exceeds maximum size limit of {limit_mb}MB (Received: {actual_mb}MB).",
        )

    # 2. Check for suspicious double extensions (e.g., payload.sh.pdf or malware.exe.docx)
    lower_name = clean_name.lower()
    dangerous_sub_exts = [".exe.", ".dll.", ".sh.", ".bat.", ".cmd.", ".vbs.", ".ps1.", ".bin."]
    for sub in dangerous_sub_exts:
        if sub in lower_name:
            return FileValidationResult(
                is_valid=False,
                mime_type="application/x-executable",
                file_size_bytes=file_size,
                detected_format="Disguised Executable",
                error_message=f"Dangerous double extension pattern detected in filename: '{clean_name}'.",
            )

    # 2b. Check file extension against permitted extensions
    ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md", ".markdown", ".json", ".csv"}
    file_ext = os.path.splitext(lower_name)[1]
    if file_ext not in ALLOWED_EXTS:
        return FileValidationResult(
            is_valid=False,
            mime_type="application/octet-stream",
            file_size_bytes=file_size,
            detected_format=f"Disallowed extension ({file_ext})",
            error_message=f"File extension '{file_ext}' is not permitted. Supported: PDF, DOCX, TXT, MD, CSV, JSON.",
        )

    # 3. Detect Magic MIME
    mime_type, format_desc = detect_magic_mime(file_bytes, clean_name)

    # 4. Check for executable or banned formats
    if mime_type.startswith("application/x-executable"):
        return FileValidationResult(
            is_valid=False,
            mime_type=mime_type,
            file_size_bytes=file_size,
            detected_format=format_desc,
            error_message=f"Executable file types are strictly prohibited ({format_desc}).",
        )

    # 5. Check against allowed MIME types
    if mime_type not in ALLOWED_MIME_TYPES:
        return FileValidationResult(
            is_valid=False,
            mime_type=mime_type,
            file_size_bytes=file_size,
            detected_format=format_desc,
            error_message=(
                f"Unsupported file format: {format_desc} ({mime_type}). "
                "Supported formats: PDF (.pdf), Word (.docx), Plain Text (.txt), Markdown (.md), CSV (.csv)."
            ),
        )

    return FileValidationResult(
        is_valid=True,
        mime_type=mime_type,
        file_size_bytes=file_size,
        detected_format=format_desc,
        error_message=None,
    )
