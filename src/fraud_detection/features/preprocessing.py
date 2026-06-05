import numpy as np
import pandas as pd

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
except ModuleNotFoundError:
    ColumnTransformer = None
    Pipeline = None
    OneHotEncoder = None
    StandardScaler = None

NUMERIC_FEATURES = [
    "amount",
    "oldbalance_org",
    "newbalance_orig",
    "oldbalance_dest",
    "newbalance_dest",
    "hour",
    "origin_balance_delta",
    "dest_balance_delta",
    "amount_to_origin_balance",
    "amount_to_dest_balance",
]
CATEGORICAL_FEATURES = ["transaction_type"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["origin_balance_delta"] = result["oldbalance_org"] - result["newbalance_orig"]
    result["dest_balance_delta"] = result["newbalance_dest"] - result["oldbalance_dest"]
    result["amount_to_origin_balance"] = result["amount"] / np.maximum(result["oldbalance_org"], 1.0)
    result["amount_to_dest_balance"] = result["amount"] / np.maximum(result["oldbalance_dest"], 1.0)
    return result


def build_preprocessor():
    if ColumnTransformer is None:
        raise RuntimeError("scikit-learn is required for the production preprocessing pipeline")
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def build_feature_pipeline(model):
    if Pipeline is None:
        return model
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", model),
        ]
    )
