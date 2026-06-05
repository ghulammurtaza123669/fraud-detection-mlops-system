import pytest


@pytest.fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    from fraud_detection.core.config import get_settings
    from fraud_detection.models.service import get_model_service

    get_settings.cache_clear()
    get_model_service.cache_clear()
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "fraud_model.joblib"))
    monkeypatch.setenv("MODEL_METADATA_PATH", str(tmp_path / "model_metadata.json"))
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file:{tmp_path / 'mlruns'}")
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "pytest-fraud-detection")
    monkeypatch.setenv("MLFLOW_REGISTER_MODEL", "false")
    yield
    get_settings.cache_clear()
    get_model_service.cache_clear()


@pytest.fixture
def sample_transaction():
    return {
        "transaction_id": "txn_api_001",
        "amount": 9800.0,
        "oldbalance_org": 9800.0,
        "newbalance_orig": 0.0,
        "oldbalance_dest": 120.0,
        "newbalance_dest": 9920.0,
        "transaction_type": "TRANSFER",
        "hour": 2,
    }
