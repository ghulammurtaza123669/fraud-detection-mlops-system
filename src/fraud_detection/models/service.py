import logging
from functools import lru_cache

try:
    import joblib
except ModuleNotFoundError:
    from fraud_detection.models.fallback import PickleJoblib as joblib
import pandas as pd

from fraud_detection.api.schemas import PredictionResponse, Transaction
from fraud_detection.core.config import get_settings
from fraud_detection.data.validation import validate_feature_frame
from fraud_detection.features.preprocessing import FEATURE_COLUMNS, add_engineered_features
from fraud_detection.models.metadata import read_metadata

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.metadata = read_metadata(self.settings.model_metadata_path)
        self.load()

    def load(self) -> None:
        if self.settings.model_path.exists():
            self.model = joblib.load(self.settings.model_path)
            self.metadata = read_metadata(self.settings.model_metadata_path)
            logger.info("loaded model version=%s", self.model_version)
        else:
            logger.warning("model file not found at %s", self.settings.model_path)

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    @property
    def model_version(self) -> str:
        return str(self.metadata.get("model_version", "untrained"))

    def predict(self, transaction: Transaction) -> PredictionResponse:
        return self.predict_batch([transaction])[0]

    def predict_batch(self, transactions: list[Transaction]) -> list[PredictionResponse]:
        if self.model is None:
            raise RuntimeError("model is not loaded; run training first")
        frame = pd.DataFrame([item.model_dump() for item in transactions])
        validate_feature_frame(frame)
        frame = add_engineered_features(frame)
        probabilities = self.model.predict_proba(frame[FEATURE_COLUMNS])[:, 1]
        responses: list[PredictionResponse] = []
        for transaction, probability in zip(transactions, probabilities, strict=True):
            prediction = int(probability >= self.settings.fraud_threshold)
            confidence = probability if prediction == 1 else 1 - probability
            responses.append(
                PredictionResponse(
                    transaction_id=transaction.transaction_id,
                    prediction=prediction,
                    fraud_probability=round(float(probability), 6),
                    confidence_score=round(float(confidence), 6),
                    model_version=self.model_version,
                )
            )
        return responses


@lru_cache
def get_model_service() -> ModelService:
    return ModelService()
