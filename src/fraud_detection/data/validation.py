import pandas as pd

REQUIRED_COLUMNS = {
    "amount",
    "oldbalance_org",
    "newbalance_orig",
    "oldbalance_dest",
    "newbalance_dest",
    "transaction_type",
    "hour",
}


def validate_training_frame(frame: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.union({"is_fraud"}) - set(frame.columns)
    if missing:
        raise ValueError(f"Training data is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Training data is empty")
    if frame["is_fraud"].nunique() < 2:
        raise ValueError("Training target must contain both fraud and non-fraud examples")
    validate_feature_frame(frame)


def validate_feature_frame(frame: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Feature data is missing required columns: {sorted(missing)}")
    numeric_columns = [
        "amount",
        "oldbalance_org",
        "newbalance_orig",
        "oldbalance_dest",
        "newbalance_dest",
        "hour",
    ]
    if frame[numeric_columns].isna().any().any():
        raise ValueError("Feature data contains null numeric values")
    if (frame[numeric_columns] < 0).any().any():
        raise ValueError("Feature data contains negative numeric values")
    if not frame["hour"].between(0, 23).all():
        raise ValueError("hour must be between 0 and 23")
