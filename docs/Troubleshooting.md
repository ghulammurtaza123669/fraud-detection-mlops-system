# Troubleshooting

## Model is not loaded

Run training first:

```powershell
python -m fraud_detection.models.train --no-tune
```

## `ModuleNotFoundError`

Install dependencies and make sure the local source tree is importable:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
```

## Docker API starts but model is missing

Train locally before building the image, or add a build stage that trains inside CI before `docker build`.

## Kubernetes image pull fails

For Docker Desktop Kubernetes, build `fraud-detection-api:latest` locally and use `imagePullPolicy: IfNotPresent`. For managed clusters, push the image to a registry and update the image field.

## Terraform not found

Install Terraform and rerun `terraform init` and `terraform validate` from `infra/terraform`.

## Grafana has no data

Confirm the API is running, Prometheus can scrape `api:8000/metrics`, and dashboard provisioning mounted correctly.
