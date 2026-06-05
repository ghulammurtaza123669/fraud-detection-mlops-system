from fastapi.testclient import TestClient

from fraud_detection.api.main import app
from fraud_detection.models.train import train_model


def test_health_predict_batch_and_metrics(sample_transaction):
    train_model(tune=False)
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    prediction = client.post("/predict", json=sample_transaction)
    assert prediction.status_code == 200
    payload = prediction.json()
    assert payload["transaction_id"] == sample_transaction["transaction_id"]
    assert "fraud_probability" in payload

    batch = client.post("/batch-predict", json={"transactions": [sample_transaction]})
    assert batch.status_code == 200
    assert len(batch.json()["predictions"]) == 1

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "fraud_api_requests_total" in metrics.text
