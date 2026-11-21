"""
Ollama On-Premise Client.

Provides an on-premise, data-sovereign LLM and embedding client implementing
the same interface as CloudflareAI. Designed for enterprise legal/government
deployments where documents cannot leave local infrastructure (e.g. India DPDPA compliance).

Default Configuration:
  OLLAMA_HOST       -> http://localhost:11434
  OLLAMA_LLM_MODEL  -> qwen2.5:7b (or llama3.1:8b)
  OLLAMA_EMBED_MODEL-> nomic-embed-text (or bge-m3)
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

logger = logging.getLogger("docqa.ollama_client")

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_LLM_MODEL   = "qwen2.5:7b"
DEFAULT_EMBED_MODEL = "nomic-embed-text"
TARGET_EMBED_DIMS   = 768


class OllamaClient:
    """
    Async client for on-premise Ollama daemon.
    Drop-in replacement for CloudflareAI.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        llm_model: Optional[str] = None,
        embed_model: Optional[str] = None,
        timeout: float = 90.0,
    ):
        self.host = (host or os.getenv("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST).rstrip("/")
        self.llm_model = llm_model or os.getenv("OLLAMA_LLM_MODEL") or DEFAULT_LLM_MODEL
        self.embed_model = embed_model or os.getenv("OLLAMA_EMBED_MODEL") or DEFAULT_EMBED_MODEL
        self._timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.host,
            timeout=httpx.Timeout(timeout, connect=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )

    async def close(self) -> None:
        """Close persistent HTTP client connections."""
        await self._client.aclose()

    async def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable and running."""
        try:
            resp = await self._client.get("/api/tags", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """Return list of locally installed model tags."""
        try:
            resp = await self._client.get("/api/tags", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception as exc:
            logger.warning("Failed to list Ollama models: %s", exc)
        return []

    # ─── Chat / Generation ────────────────────────────────────────────────────

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> str:
        """
        Non-streaming chat completion via Ollama /api/chat.
        Returns the raw string output.
        """
        payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            resp = await self._client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "").strip()
        except httpx.ConnectError:
            err_msg = (
                f"Ollama connection refused at {self.host}. "
                "Ensure Ollama is running ('ollama serve') or set LLM_BACKEND=cloudflare."
            )
            logger.error(err_msg)
            raise ConnectionError(err_msg)
        except Exception as exc:
            logger.error("Ollama chat error: %s", exc)
            raise

    async def stream_chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> AsyncIterator[str]:
        """
        Streaming chat completion yielding text tokens in real time.
        """
        payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with self._client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.error("Ollama stream error: %s", exc)
            yield f"\n[Ollama Streaming Error: {exc}]"

    # ─── Embeddings ───────────────────────────────────────────────────────────

    def _normalize_dim(self, vec: List[float], target_dim: int = TARGET_EMBED_DIMS) -> List[float]:
        """Pads or truncates vector to exactly target_dim dimensions."""
        if len(vec) == target_dim:
            return vec
        if len(vec) > target_dim:
            return vec[:target_dim]
        # Pad with zeros
        return vec + [0.0] * (target_dim - len(vec))

    async def embed(self, text: str) -> List[float]:
        """Generate a normalized 768-dim float vector for a text string."""
        # Try /api/embed (Ollama v0.1.34+) first, then fallback to /api/embeddings
        try:
            resp = await self._client.post(
                "/api/embed",
                json={"model": self.embed_model, "input": text},
            )
            if resp.status_code == 200:
                data = resp.json()
                embeddings = data.get("embeddings", [])
                if embeddings:
                    return self._normalize_dim(embeddings[0])
        except Exception:
            pass

        # Fallback to classic /api/embeddings
        resp = await self._client.post(
            "/api/embeddings",
            json={"model": self.embed_model, "prompt": text},
        )
        resp.raise_for_status()
        vec = resp.json().get("embedding", [])
        return self._normalize_dim(vec)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts."""
        if not texts:
            return []

        # Try batch /api/embed
        try:
            resp = await self._client.post(
                "/api/embed",
                json={"model": self.embed_model, "input": texts},
            )
            if resp.status_code == 200:
                data = resp.json()
                embeddings = data.get("embeddings", [])
                if len(embeddings) == len(texts):
                    return [self._normalize_dim(v) for v in embeddings]
        except Exception:
            pass

        # Fallback: sequential embedding calls
        results: List[List[float]] = []
        for text in texts:
            results.append(await self.embed(text))
        return results
