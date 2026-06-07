# Real-Time Fraud Detection System with MLOps

Production-ready fraud scoring service using Python, scikit-learn Random Forest, FastAPI, MLflow, Docker, Kubernetes, Terraform, Jenkins, Prometheus, and Grafana.

## Features

- Synthetic or CSV-based transaction ingestion
- Data validation, preprocessing, feature engineering, train/test split, Random Forest training, and metrics
- MLflow experiment tracking, parameters, metrics, artifacts, and optional model registry
- FastAPI endpoints: `GET /health`, `POST /predict`, `POST /batch-predict`, `GET /metrics`
- Unit, integration, API, and model tests
- Docker Compose stack with API, MLflow, Prometheus, and Grafana
- Kubernetes manifests with namespace, Deployment, Service, ReplicaSet reference, ConfigMap, Secret, Ingress, and ServiceMonitor
- Terraform Kubernetes deployment module
- Jenkins and GitHub Actions CI/CD pipelines

## Quick Start

```powershell
$env:PYTHONPATH="src"
python -m pip install -r requirements.txt
python -m fraud_detection.models.train --no-tune
python -m uvicorn fraud_detection.api.main:app --host 0.0.0.0 --port 8000
```

Swagger UI: `http://localhost:8000/docs`

Sample request:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/predict -ContentType "application/json" -Body '{
  "transaction_id": "txn_001",
  "amount": 9800,
  "oldbalance_org": 9800,
  "newbalance_orig": 0,
  "oldbalance_dest": 120,
  "newbalance_dest": 9920,
  "transaction_type": "TRANSFER",
  "hour": 2
}'
```

## Validation

```powershell
python -m ruff check src tests
python -m pytest
docker compose up --build
kubectl apply -f infra/kubernetes/
```

See the `docs/` folder for architecture, deployment, API, workflow, and troubleshooting details.

## Graphs

Visible model and monitoring graph evidence is documented in `docs/Graphs.md`.
