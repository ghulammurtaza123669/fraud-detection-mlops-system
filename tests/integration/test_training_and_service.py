from fraud_detection.api.schemas import Transaction
from fraud_detection.core.config import get_settings
from fraud_detection.models.service import ModelService
from fraud_detection.models.train import train_model


def test_training_creates_model_and_service_predicts(sample_transaction):
    result = train_model(tune=False)
    settings = get_settings()
    assert settings.model_path.exists()
    assert "average_precision" in result["metrics"]

    service = ModelService()
    response = service.predict(Transaction(**sample_transaction))
    assert response.transaction_id == sample_transaction["transaction_id"]
    assert response.prediction in {0, 1}
    assert 0 <= response.fraud_probability <= 1
    assert response.model_version != "untrained"
