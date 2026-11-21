"""
Formal Audit & Due-Diligence Report Generator — Phase 3 Reporting.

Produces client-ready formal executive reports in HTML (with Print-to-PDF layout),
Markdown, and JSON formats for:
    - Legal & Contract Red-Flag Audits (with Human-in-the-Loop review stamps)
    - Regulatory Compliance Gap Assessments
    - Indian Court Judgment Case Law Intelligence
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def generate_redflag_report_html(
    report: Dict[str, Any],
    doc_name: str,
    doc_id: str,
    tenant_id: str = "default",
) -> str:
    """Generate an executive-grade HTML audit report with print-to-PDF styles."""
    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y - %H:%M UTC")
    risk_level = report.get("document_risk_level", "LOW")
    flags = report.get("red_flags", [])
    audit_trail = report.get("audit_trail", [])

    risk_colors = {
        "HIGH":   {"badge": "#ef4444", "bg": "#fef2f2", "text": "#991b1b"},
        "MEDIUM": {"badge": "#f59e0b", "bg": "#fffbeb", "text": "#92400e"},
        "LOW":    {"badge": "#10b981", "bg": "#ecfdf5", "text": "#065f46"},
    }
    rc = risk_colors.get(risk_level, risk_colors["LOW"])

    total = len(flags)
    pending = sum(1 for f in flags if f.get("review_status") == "PENDING")
    accepted = sum(1 for f in flags if f.get("review_status") == "ACCEPTED")
    dismissed = sum(1 for f in flags if f.get("review_status") == "DISMISSED")
    remediation = sum(1 for f in flags if f.get("review_status") == "NEEDS_REMEDIATION")

    flags_rows_html = ""
    for f in flags:
        sev = f.get("severity", "LOW")
        sev_color = "#ef4444" if sev == "HIGH" else ("#f59e0b" if sev == "MEDIUM" else "#10b981")
        status = f.get("review_status", "PENDING")
        status_bg = "#dcfce7" if status == "ACCEPTED" else ("#f3f4f6" if status == "DISMISSED" else ("#fee2e2" if status == "NEEDS_REMEDIATION" else "#fef3c7"))
        status_color = "#15803d" if status == "ACCEPTED" else ("#4b5563" if status == "DISMISSED" else ("#b91c1c" if status == "NEEDS_REMEDIATION" else "#b45309"))

        reviewer_note = f.get("review_note") or "None"
        reviewed_by = f.get("reviewed_by") or "Pending Review"

        flags_rows_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 12px; font-weight: 600;">{f.get('type', 'Unknown')}</td>
          <td style="padding: 12px;">
            <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; color: #fff; background-color: {sev_color};">
              {sev}
            </span>
          </td>
          <td style="padding: 12px; font-size: 13px; color: #4b5563;">{f.get('clause_ref') or f"Page {f.get('page', '?')}"}</td>
          <td style="padding: 12px; font-size: 13px; font-style: italic; color: #374151; max-width: 280px;">"{f.get('excerpt', '')}"</td>
          <td style="padding: 12px; font-size: 13px; color: #1e3a8a;">{f.get('recommendation', 'Review standard terms.')}</td>
          <td style="padding: 12px;">
            <span style="display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; background: {status_bg}; color: {status_color};">
              {status}
            </span>
            <div style="font-size: 10px; color: #6b7280; margin-top: 4px;">{reviewed_by}</div>
            {f'<div style="font-size: 11px; color: #111827; margin-top: 2px;">Note: {reviewer_note}</div>' if reviewer_note != 'None' else ''}
          </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Formal Due Diligence Report — {doc_name}</title>
  <style>
    @media print {{
      body {{ font-size: 12pt; background: #fff !important; color: #000 !important; }}
      .no-print {{ display: none !important; }}
      .page-break {{ page-break-before: always; }}
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      color: #111827;
      background: #f9fafb;
      margin: 0;
      padding: 40px 20px;
    }}
    .report-card {{
      max-width: 1000px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
      padding: 48px;
      border: 1px solid #e5e7eb;
    }}
    .report-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid #e5e7eb;
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .header-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .brand-title {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #1e293b;
    }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 24px 0 32px;
    }}
    .metric-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px;
      text-align: center;
    }}
    .metric-value {{
      font-size: 26px;
      font-weight: 800;
      color: #0f172a;
    }}
    .metric-label {{
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
      color: #64748b;
      margin-top: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      margin-top: 16px;
    }}
    th {{
      background: #f1f5f9;
      color: #334155;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 12px;
      border-bottom: 2px solid #cbd5e1;
    }}
    .print-btn {{
      background: #2563eb;
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
  </style>
</head>
<body>
  <div class="report-card">
    <div class="report-header">
      <div>
        <div class="header-brand">
          <span style="font-size: 24px;">⚖️</span>
          <span class="brand-title">DocsAI Enterprise Audit Intelligence</span>
        </div>
        <p style="margin: 6px 0 0; color: #64748b; font-size: 13px;">Confidential Document Risk & Compliance Assessment</p>
      </div>
      <div style="text-align: right;">
        <button class="print-btn no-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
        <div style="font-size: 12px; color: #64748b; margin-top: 8px;">Date: {now_str}</div>
      </div>
    </div>

    <div style="background: {rc['bg']}; border: 1px solid {rc['badge']}; border-radius: 8px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <div>
        <div style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: {rc['text']};">Audited Document</div>
        <div style="font-size: 18px; font-weight: 700; color: #0f172a; margin-top: 2px;">{doc_name}</div>
        <div style="font-size: 12px; color: #64748b; margin-top: 2px;">Document ID: <code>{doc_id}</code> | Tenant: <code>{tenant_id}</code></div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b;">Residual Risk Rating</div>
        <div style="display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 16px; font-weight: 800; color: #fff; background: {rc['badge']}; margin-top: 4px;">
          {risk_level} RISK
        </div>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-box">
        <div class="metric-value">{total}</div>
        <div class="metric-label">Identified Flags</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color: #10b981;">{accepted}</div>
        <div class="metric-label">Accepted Risks</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color: #ef4444;">{remediation}</div>
        <div class="metric-label">Remediations Required</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color: #6b7280;">{dismissed}</div>
        <div class="metric-label">Dismissed (False Pos.)</div>
      </div>
    </div>

    <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 8px;">Executive Summary</h3>
    <p style="font-size: 14px; color: #334155; margin-top: 0; line-height: 1.6; background: #f8fafc; padding: 14px; border-radius: 6px; border-left: 4px solid #3b82f6;">
      {report.get("summary", "Document review completed with autonomous clause analysis.")}
    </p>

    <h3 style="font-size: 16px; font-weight: 700; color: #0f172a; margin-top: 32px; margin-bottom: 8px;">Detected Risk Clauses & Legal Action Items</h3>
    <table>
      <thead>
        <tr>
          <th>Category</th>
          <th>Severity</th>
          <th>Location</th>
          <th>Clause Excerpt</th>
          <th>Legal Recommendation</th>
          <th>Audit Status</th>
        </tr>
      </thead>
      <tbody>
        {flags_rows_html if flags_rows_html else '<tr><td colspan="6" style="padding: 24px; text-align: center; color: #6b7280;">No high-risk clauses detected.</td></tr>'}
      </tbody>
    </table>

    <div style="margin-top: 48px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between;">
      <div>Generated automatically via DocsAI Hybrid Vector-Graph Engine (Reciprocal Rank Fusion + DeBERTa NLI).</div>
      <div>Confidential & Privileged — For Internal Legal Audit Only</div>
    </div>
  </div>
</body>
</html>"""
    return html


def generate_redflag_report_markdown(
    report: Dict[str, Any],
    doc_name: str,
    doc_id: str,
) -> str:
    """Generate Markdown formatted audit report."""
    risk_level = report.get("document_risk_level", "LOW")
    flags = report.get("red_flags", [])

    lines = [
        f"# Formal Document Due-Diligence Audit Report",
        f"**Document Name:** {doc_name}  ",
        f"**Document ID:** `{doc_id}`  ",
        f"**Overall Risk Rating:** **{risk_level}**  ",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}  ",
        "",
        "## Executive Summary",
        report.get("summary", "Autonomous clause scan completed."),
        "",
        "## Risk Clauses Breakdown",
        "",
        "| ID | Risk Type | Severity | Clause / Page | Status | Recommendation |",
        "|---|---|---|---|---|---|",
    ]

    for f in flags:
        lines.append(
            f"| {f.get('id', '-')} | {f.get('type', '-')} | {f.get('severity', '-')} | "
            f"{f.get('clause_ref') or f.get('page', '-')} | {f.get('review_status', 'PENDING')} | "
            f"{f.get('recommendation', '-')} |"
        )

    lines.extend([
        "",
        "## Detailed Excerpts",
        "",
    ])

    for f in flags:
        loc = f.get('clause_ref') or f"Page {f.get('page', '?')}"
        lines.extend([
            f"### {f.get('type')} ({f.get('severity', 'LOW')})",
            f"- **Reference:** {loc}",
            f"- **Audit Status:** {f.get('review_status', 'PENDING')} (Reviewer: {f.get('reviewed_by', 'None')})",
            f"- **Excerpt:** > {f.get('excerpt', '')}",
            f"- **Recommendation:** {f.get('recommendation', '')}",
            f"- **Reviewer Note:** {f.get('review_note', 'None')}",
            "",
        ])

    return "\n".join(lines)
