# MLOps Workflow

1. Data ingestion loads a configured CSV if provided or generates realistic synthetic transaction data for reproducible local development.
2. Validation checks schema, nulls, numeric ranges, hours, and target quality.
3. Feature engineering adds origin balance delta, destination balance delta, and amount-to-balance ratios.
4. Training uses a scikit-learn Pipeline containing preprocessing and Random Forest classification.
5. Hyperparameter tuning uses `GridSearchCV` when enabled. CI uses `--no-tune` to keep builds fast.
6. Evaluation records accuracy, F1, ROC AUC, and average precision.
7. MLflow logs parameters, metrics, and model artifacts. Optional registry logging is controlled by `MLFLOW_REGISTER_MODEL`.
8. The selected model is serialized to `models/fraud_model.joblib`; metadata is written to `models/model_metadata.json`.
9. FastAPI loads the serialized pipeline at startup and serves real-time and batch predictions.
10. Prometheus and Grafana monitor service behavior and container health.

## Retraining

```powershell
python -m fraud_detection.models.train --data-path data/raw/transactions.csv
```

The CSV must include all API request fields plus `is_fraud`.
