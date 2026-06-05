# API Documentation

FastAPI publishes interactive Swagger UI at `/docs` and OpenAPI JSON at `/openapi.json`.

## `GET /health`

Returns service status, app name, whether the model is loaded, and the model version.

## `POST /predict`

Request:

```json
{
  "transaction_id": "txn_001",
  "amount": 9800,
  "oldbalance_org": 9800,
  "newbalance_orig": 0,
  "oldbalance_dest": 120,
  "newbalance_dest": 9920,
  "transaction_type": "TRANSFER",
  "hour": 2
}
```

Response:

```json
{
  "transaction_id": "txn_001",
  "prediction": 1,
  "fraud_probability": 0.92,
  "confidence_score": 0.92,
  "model_version": "mlflow-run-id"
}
```

## `POST /batch-predict`

Request body is `{ "transactions": [ ... ] }`, where each item matches the `/predict` schema. Maximum batch size is 1000.

## `GET /metrics`

Prometheus metrics include request count, error count, request latency, and prediction counts.
