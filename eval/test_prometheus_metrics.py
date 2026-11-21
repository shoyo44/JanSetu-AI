"""
Unit Test Suite for JanSetu AI Prometheus Metrics & Sovereign Observability Exporter.
Verifies RFC-compliant exposition format for telemetry ingestion by Prometheus.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.observability import PrometheusMetricsRegistry


def test_prometheus_registry():
    reg = PrometheusMetricsRegistry()

    # 1. Test Counters
    reg.inc_counter("http_requests_total", {"method": "GET", "endpoint": "/health", "status": "200"}, 10)
    reg.inc_counter("http_requests_total", {"method": "POST", "endpoint": "/api/v1/query", "status": "200"}, 5)
    reg.inc_counter("jansetu_abstentions_total", {"vertical": "governance"}, 2)
    reg.inc_counter("jansetu_undertrial_reviews_total", {"vertical": "law"}, 4)

    # 2. Test Gauges
    reg.set_gauge("jansetu_graph_nodes_total", 142.0)
    reg.set_gauge("jansetu_nli_entailment_score", 0.884, {"vertical": "judgment"})

    # 3. Test Durations (Summaries)
    reg.observe_duration("http_request_duration_seconds", 0.045, {"endpoint": "/api/v1/query"})
    reg.observe_duration("http_request_duration_seconds", 0.055, {"endpoint": "/api/v1/query"})

    # 4. Export Text
    text = reg.export_text()

    assert "# HELP http_requests_total" in text, "Missing counter HELP"
    assert "# TYPE http_requests_total counter" in text, "Missing counter TYPE"
    assert 'http_requests_total{endpoint="/health",method="GET",status="200"} 10' in text
    assert 'jansetu_graph_nodes_total 142.0000' in text
    assert 'jansetu_nli_entailment_score{vertical="judgment"} 0.8840' in text
    assert 'http_request_duration_seconds_count{endpoint="/api/v1/query"} 2' in text
    assert 'http_request_duration_seconds_sum{endpoint="/api/v1/query"} 0.1000' in text

    print("✅ All Prometheus Metrics Registry Tests Passed (100.0%)!")


if __name__ == "__main__":
    test_prometheus_registry()
