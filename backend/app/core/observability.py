"""
Observability — per-query tracing and timeout wrapper.

PipelineTrace:
    Tracks timing of each pipeline stage (retrieval, rerank, generation).
    Attached to every query response as `_trace` for debugging and monitoring.

with_timeout:
    Wraps any coroutine with a configurable timeout.
    Raises TimeoutError with a descriptive message on expiry.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict

logger = logging.getLogger("docqa.observability")


# ─── Pipeline Trace ──────────────────────────────────────────────────────────

class PipelineTrace:
    """
    Lightweight per-query telemetry container.
    Records wall-clock timing (ms) for each pipeline stage.

    Usage:
        trace = PipelineTrace(tenant_id="t1", vertical="law", query_hash="abc123")
        t0 = asyncio.get_running_loop().time()
        # ... do retrieval ...
        trace.record("retrieval_ms", (asyncio.get_running_loop().time() - t0) * 1000)
        trace.add_meta("chunks_retrieved", 12)
        trace.log_summary()
    """

    def __init__(self, tenant_id: str, vertical: str, query_hash: str):
        self.tenant_id   = tenant_id
        self.vertical    = vertical
        self.query_hash  = query_hash
        self.timings:  Dict[str, float] = {}
        self.metadata: Dict[str, Any]   = {}
        self._wall_start = time.perf_counter()

    def record(self, stage: str, duration_ms: float) -> None:
        """Record the duration of a named pipeline stage in milliseconds."""
        self.timings[stage] = round(duration_ms, 2)

    def add_meta(self, key: str, value: Any) -> None:
        """Attach arbitrary metadata (chunk counts, flags, etc.)."""
        self.metadata[key] = value

    def total_ms(self) -> float:
        """Wall-clock time since trace was created."""
        return round((time.perf_counter() - self._wall_start) * 1000, 2)

    def log_summary(self) -> None:
        """Emit a single INFO log line summarising the full query trace."""
        stage_str = " | ".join(f"{k}={v}ms" for k, v in self.timings.items())
        meta_str  = " | ".join(f"{k}={v}" for k, v in self.metadata.items())
        logger.info(
            "[%s/%s] query=%s | total=%sms | %s | %s",
            self.vertical,
            self.tenant_id,
            self.query_hash,
            self.total_ms(),
            stage_str,
            meta_str,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON embedding in API response."""
        return {
            "query_hash": self.query_hash,
            "vertical":   self.vertical,
            "total_ms":   self.total_ms(),
            "stages":     self.timings,
            "meta":       self.metadata,
        }


# ─── Timeout Wrapper ─────────────────────────────────────────────────────────

async def with_timeout(coro: Any, timeout_s: float, stage: str) -> Any:
    """
    Awaits a coroutine with a hard timeout.

    Args:
        coro:      The coroutine to await.
        timeout_s: Seconds before raising asyncio.TimeoutError.
        stage:     Human-readable stage name for error messages.

    Raises:
        asyncio.TimeoutError: if the coroutine exceeds timeout_s.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_s)
    except asyncio.TimeoutError:
        logger.error("Stage '%s' timed out after %.1fs", stage, timeout_s)
        raise asyncio.TimeoutError(
            f"Pipeline stage '{stage}' exceeded {timeout_s}s timeout."
        )


# ─── Prometheus Metrics Registry & Sovereign Observability ───────────────────

import threading
from collections import defaultdict


class PrometheusMetricsRegistry:
    """
    Lightweight, thread-safe, zero-dependency Prometheus exposition collector.
    Formats live runtime telemetry in official Prometheus text format (RFC 0004).
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Counters: (name, label_tuple) -> count
        self.counters: Dict[str, Dict[tuple, int]] = defaultdict(lambda: defaultdict(int))
        # Gauges: (name, label_tuple) -> float
        self.gauges: Dict[str, Dict[tuple, float]] = defaultdict(lambda: defaultdict(float))
        # Histograms / Summaries: (name, label_tuple) -> [sum, count]
        self.durations: Dict[str, Dict[tuple, list]] = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))

    def inc_counter(self, name: str, labels: Dict[str, str] = None, amount: int = 1) -> None:
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self.counters[name][key] += amount

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self.gauges[name][key] = value

    def observe_duration(self, name: str, duration_s: float, labels: Dict[str, str] = None) -> None:
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            stat = self.durations[name][key]
            stat[0] += duration_s
            stat[1] += 1

    def export_text(self) -> str:
        """Render all metrics in standard Prometheus line-based exposition format."""
        lines = []

        # Document metric types & help text
        descriptions = {
            "http_requests_total": ("counter", "Total HTTP requests handled by the API."),
            "http_request_duration_seconds": ("summary", "HTTP request processing latency in seconds."),
            "jansetu_queries_total": ("counter", "Total sovereign RAG inquiries segmented by vertical domain."),
            "jansetu_abstentions_total": ("counter", "Total calibrated abstentions triggered by the defensibility engine."),
            "jansetu_cache_hits_total": ("counter", "Total semantic cache hits avoiding LLM re-synthesis."),
            "jansetu_nli_entailment_score": ("gauge", "Most recent claim-level NLI entailment score."),
            "jansetu_graph_nodes_total": ("gauge", "Total entities indexed in the in-process NetworkX graph."),
            "jansetu_undertrial_reviews_total": ("counter", "Total BNSS Section 479 undertrial bail eligibility screenings."),
        }

        with self._lock:
            # Export Counters
            for name, items in self.counters.items():
                mtype, help_text = descriptions.get(name, ("counter", f"Metric {name}"))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {mtype}")
                for labels, val in items.items():
                    lbl_str = ",".join(f'{k}="{v}"' for k, v in labels)
                    lbl_part = f"{{{lbl_str}}}" if lbl_str else ""
                    lines.append(f"{name}{lbl_part} {val}")

            # Export Gauges
            for name, items in self.gauges.items():
                mtype, help_text = descriptions.get(name, ("gauge", f"Metric {name}"))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {mtype}")
                for labels, val in items.items():
                    lbl_str = ",".join(f'{k}="{v}"' for k, v in labels)
                    lbl_part = f"{{{lbl_str}}}" if lbl_str else ""
                    lines.append(f"{name}{lbl_part} {val:.4f}")

            # Export Summaries (durations)
            for name, items in self.durations.items():
                mtype, help_text = descriptions.get(name, ("summary", f"Duration summary for {name}"))
                lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} {mtype}")
                for labels, (total_s, count) in items.items():
                    lbl_str = ",".join(f'{k}="{v}"' for k, v in labels)
                    prefix = f"{lbl_str}," if lbl_str else ""
                    lines.append(f"{name}_sum{{{prefix}}} {total_s:.4f}".replace(",}", "}"))
                    lines.append(f"{name}_count{{{prefix}}} {count}".replace(",}", "}"))

        # Default empty fallback if no queries yet
        if not lines:
            lines.append("# HELP jansetu_system_status Sovereign system active state.")
            lines.append("# TYPE jansetu_system_status gauge")
            lines.append("jansetu_system_status 1.0")

        return "\n".join(lines) + "\n"


# Global singleton metrics collector
metrics = PrometheusMetricsRegistry()

