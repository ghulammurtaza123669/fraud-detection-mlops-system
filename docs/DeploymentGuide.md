# Deployment Guide

## Local Python

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m fraud_detection.models.train --no-tune
python -m uvicorn fraud_detection.api.main:app --host 0.0.0.0 --port 8000
```

## Docker Compose

```powershell
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- MLflow: `http://localhost:5000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` with `admin/admin`

## Kubernetes

```powershell
docker build -t fraud-detection-api:latest .
kubectl apply -f infra/kubernetes/
kubectl rollout status deployment/fraud-detection-api -n fraud-detection
kubectl port-forward service/fraud-detection-api 8000:80 -n fraud-detection
```

## Terraform

Install Terraform, select a Kubernetes context, then run:

```powershell
cd infra/terraform
terraform init
terraform validate
terraform apply -var image=fraud-detection-api:latest
```

## Jenkins

Create Jenkins credentials for Docker registry access if pushing images. The `Jenkinsfile` stages are lint, test, model build, Docker build, optional Docker push, Kubernetes deploy, and rollout verification.
