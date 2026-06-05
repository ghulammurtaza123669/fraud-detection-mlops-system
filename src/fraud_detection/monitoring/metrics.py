try:
    from prometheus_client import Counter, Histogram, generate_latest
    from prometheus_client.exposition import CONTENT_TYPE_LATEST
except ModuleNotFoundError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

    class _Metric:
        def __init__(self, name, documentation, labels=None):
            self.name = name

        def labels(self, *args, **kwargs):
            return self

        def inc(self, amount=1):
            return None

        def observe(self, amount):
            return None

    Counter = _Metric
    Histogram = _Metric

    def generate_latest():
        return b"# HELP fraud_api_requests_total Total API requests\n# TYPE fraud_api_requests_total counter\n"

REQUEST_COUNT = Counter("fraud_api_requests_total", "Total API requests", ["method", "endpoint", "status"])
ERROR_COUNT = Counter("fraud_api_errors_total", "Total API errors", ["endpoint", "error_type"])
REQUEST_LATENCY = Histogram("fraud_api_request_latency_seconds", "API request latency", ["method", "endpoint"])
PREDICTION_COUNT = Counter("fraud_predictions_total", "Prediction count", ["prediction"])


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
