import logging
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from fraud_detection.api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    PredictionResponse,
    Transaction,
)
from fraud_detection.core.config import get_settings
from fraud_detection.core.logging import configure_logging
from fraud_detection.models.service import ModelService, get_model_service
from fraud_detection.monitoring.metrics import (
    ERROR_COUNT,
    PREDICTION_COUNT,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    render_metrics,
)

configure_logging()
settings = get_settings()
logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="Random Forest fraud scoring service with MLOps tracking and production monitoring.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    endpoint = request.url.path
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        ERROR_COUNT.labels(endpoint=endpoint, error_type=exc.__class__.__name__).inc()
        logger.exception("unhandled error path=%s", endpoint)
        raise
    finally:
        elapsed = time.perf_counter() - start
        status = locals().get("response").status_code if "response" in locals() else 500
        REQUEST_COUNT.labels(request.method, endpoint, str(status)).inc()
        REQUEST_LATENCY.labels(request.method, endpoint).observe(elapsed)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_: Request, exc: RuntimeError):
    ERROR_COUNT.labels(endpoint="runtime", error_type=exc.__class__.__name__).inc()
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health(service: ModelService = Depends(get_model_service)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        model_loaded=service.model_loaded,
        model_version=service.model_version,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["fraud"])
def predict(transaction: Transaction, service: ModelService = Depends(get_model_service)) -> PredictionResponse:
    try:
        response = service.predict(transaction)
        PREDICTION_COUNT.labels(prediction=str(response.prediction)).inc()
        return response
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/batch-predict", response_model=BatchPredictionResponse, tags=["fraud"])
def batch_predict(
    request: BatchPredictionRequest,
    service: ModelService = Depends(get_model_service),
) -> BatchPredictionResponse:
    try:
        predictions = service.predict_batch(request.transactions)
        for prediction in predictions:
            PREDICTION_COUNT.labels(prediction=str(prediction.prediction)).inc()
        return BatchPredictionResponse(predictions=predictions)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/metrics", tags=["system"])
def metrics() -> Response:
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
