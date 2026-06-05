import pandas as pd
import pytest

from fraud_detection.data.ingestion import generate_synthetic_transactions
from fraud_detection.data.validation import validate_feature_frame, validate_training_frame


def test_generated_training_data_is_valid():
    frame = generate_synthetic_transactions(rows=200, seed=7)
    validate_training_frame(frame)
    assert {"amount", "transaction_type", "is_fraud"}.issubset(frame.columns)


def test_negative_amount_is_rejected():
    frame = generate_synthetic_transactions(rows=50, seed=7).drop(columns=["is_fraud"])
    frame.loc[0, "amount"] = -1
    with pytest.raises(ValueError, match="negative"):
        validate_feature_frame(frame)


def test_missing_training_target_is_rejected():
    frame = pd.DataFrame({"amount": [1]})
    with pytest.raises(ValueError, match="missing"):
        validate_training_frame(frame)
