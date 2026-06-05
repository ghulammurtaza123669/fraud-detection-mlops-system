from fraud_detection.data.ingestion import generate_synthetic_transactions
from fraud_detection.features.preprocessing import FEATURE_COLUMNS, add_engineered_features


def test_engineered_features_are_added():
    frame = generate_synthetic_transactions(rows=10, seed=1)
    transformed = add_engineered_features(frame)
    assert set(FEATURE_COLUMNS).issubset(transformed.columns)
    assert transformed["origin_balance_delta"].notna().all()
