import argparse
import logging

try:
    import joblib
except ModuleNotFoundError:
    from fraud_detection.models.fallback import PickleJoblib as joblib

try:
    import mlflow
    import mlflow.sklearn
except ModuleNotFoundError:
    from fraud_detection.models.fallback import NoopMlflow as mlflow

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, average_precision_score, f1_score, roc_auc_score
    from sklearn.model_selection import GridSearchCV, train_test_split
except ModuleNotFoundError:
    RandomForestClassifier = None
    GridSearchCV = None
    from fraud_detection.models.fallback import SimpleFraudModel, binary_metrics

from fraud_detection.core.config import get_settings
from fraud_detection.core.logging import configure_logging
from fraud_detection.data.ingestion import load_transactions
from fraud_detection.data.validation import validate_training_frame
from fraud_detection.features.preprocessing import (
    FEATURE_COLUMNS,
    add_engineered_features,
    build_feature_pipeline,
)
from fraud_detection.models.metadata import write_metadata

logger = logging.getLogger(__name__)


def train_model(data_path: str | None = None, tune: bool = True) -> dict:
    configure_logging()
    settings = get_settings()
    frame = load_transactions(data_path)
    validate_training_frame(frame)
    frame = add_engineered_features(frame)

    x = frame[FEATURE_COLUMNS]
    y = frame["is_fraud"].astype(int)
    if RandomForestClassifier is None:
        split = int(len(x) * 0.8)
        x_train, x_test = x.iloc[:split], x.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]
    else:
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y
        )

    if RandomForestClassifier is None:
        pipeline = SimpleFraudModel()
    else:
        base_model = RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        pipeline = build_feature_pipeline(base_model)
    params = {
        "model__n_estimators": [120, 180],
        "model__max_depth": [10, 14],
        "model__min_samples_split": [2, 4],
    }

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)
    with mlflow.start_run(run_name="random-forest-fraud-detector") as run:
        if tune and GridSearchCV is not None:
            search = GridSearchCV(
                pipeline,
                params,
                cv=3,
                scoring="average_precision",
                n_jobs=-1,
            )
            search.fit(x_train, y_train)
            fitted = search.best_estimator_
            best_params = search.best_params_
        else:
            fitted = pipeline.fit(x_train, y_train)
            best_params = pipeline.get_params()

        probabilities = fitted.predict_proba(x_test)[:, 1]
        predictions = (probabilities >= settings.fraud_threshold).astype(int)
        if RandomForestClassifier is None:
            metrics = binary_metrics(y_test, probabilities, settings.fraud_threshold)
        else:
            metrics = {
                "accuracy": float(accuracy_score(y_test, predictions)),
                "f1": float(f1_score(y_test, predictions)),
                "roc_auc": float(roc_auc_score(y_test, probabilities)),
                "average_precision": float(average_precision_score(y_test, probabilities)),
            }

        mlflow.log_params({k: str(v) for k, v in best_params.items()})
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(fitted, artifact_path="model")
        if settings.mlflow_register_model:
            mlflow.sklearn.log_model(
                fitted,
                artifact_path="registered_model",
                registered_model_name="FraudDetectionRandomForest",
            )

        settings.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(fitted, settings.model_path)
        model_version = run.info.run_id
        write_metadata(
            settings.model_metadata_path,
            model_version=model_version,
            metrics=metrics,
            params={k: str(v) for k, v in best_params.items()},
        )
        logger.info("trained fraud model version=%s metrics=%s", model_version, metrics)
        return {"model_version": model_version, "metrics": metrics, "model_path": str(settings.model_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default=None)
    parser.add_argument("--no-tune", action="store_true")
    args = parser.parse_args()
    print(train_model(args.data_path, tune=not args.no_tune))


if __name__ == "__main__":
    main()
