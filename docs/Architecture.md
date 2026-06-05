# Architecture

The system has five production layers:

1. Data and model layer: Pandas and NumPy load/produce transactions, validate schema and values, engineer balance and ratio features, split data, train a scikit-learn Random Forest, and serialize the full preprocessing/model pipeline.
2. MLOps layer: MLflow logs parameters, metrics, model artifacts, and optional registry entries. Local default tracking uses `file:./mlruns`; Docker Compose points the API toward the MLflow service.
3. Serving layer: FastAPI exposes `/health`, `/predict`, `/batch-predict`, `/metrics`, generated OpenAPI documentation, typed Pydantic validation, structured errors, and logs.
4. Platform layer: Docker packages the API, Docker Compose runs API/MLflow/Prometheus/Grafana, Kubernetes deploys replicas, and Terraform can manage equivalent Kubernetes resources.
5. Operations layer: Prometheus scrapes API metrics and Grafana provisions a dashboard for request rate, errors, latency, predictions, CPU, and memory.

## Runtime Flow

Transaction JSON enters FastAPI, Pydantic validates it, the model service converts it to a DataFrame, feature engineering runs, the serialized scikit-learn pipeline scores fraud probability, and the API returns prediction, fraud probability, confidence score, and model version.

## Security Posture

Runtime configuration is externalized through environment variables, Kubernetes ConfigMaps, and Kubernetes Secrets. The container runs as a non-root user, Kubernetes drops Linux capabilities, and input validation rejects invalid transaction types, negative numeric values, and invalid hours.
