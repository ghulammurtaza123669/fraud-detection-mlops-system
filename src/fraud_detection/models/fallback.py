import pickle
from pathlib import Path

import numpy as np
import pandas as pd


class NoopRunInfo:
    run_id = "local-fallback-run"


class NoopRun:
    info = NoopRunInfo()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class NoopMlflowSklearn:
    @staticmethod
    def log_model(*args, **kwargs):
        return None


class NoopMlflow:
    sklearn = NoopMlflowSklearn()

    @staticmethod
    def set_tracking_uri(uri):
        return None

    @staticmethod
    def set_experiment(name):
        return None

    @staticmethod
    def start_run(run_name=None):
        return NoopRun()

    @staticmethod
    def log_params(params):
        return None

    @staticmethod
    def log_metrics(metrics):
        return None


class PickleJoblib:
    @staticmethod
    def dump(obj, path: Path | str):
        with Path(path).open("wb") as handle:
            pickle.dump(obj, handle)

    @staticmethod
    def load(path: Path | str):
        with Path(path).open("rb") as handle:
            return pickle.load(handle)


class SimpleFraudModel:
    def get_params(self, deep: bool = True):
        return {"fallback_model": "simple_fraud_model"}

    def fit(self, x: pd.DataFrame, y: pd.Series):
        fraud_rate = float(np.mean(y))
        self.bias_ = np.log(max(fraud_rate, 1e-4) / max(1 - fraud_rate, 1e-4))
        return self

    def predict_proba(self, x: pd.DataFrame):
        frame = x.copy()
        high_risk_type = frame["transaction_type"].isin(["TRANSFER", "CASH_OUT"]).astype(float)
        emptied_origin = (frame["newbalance_orig"] <= frame["oldbalance_org"] * 0.05).astype(float)
        amount_pressure = (frame["amount_to_origin_balance"] > 0.75).astype(float)
        odd_hour = frame["hour"].isin([0, 1, 2, 3, 4]).astype(float)
        score = (
            self.bias_
            + 1.8 * high_risk_type
            + 2.3 * emptied_origin
            + 1.2 * amount_pressure
            + 0.6 * odd_hour
        )
        probability = 1 / (1 + np.exp(-score))
        return np.column_stack([1 - probability, probability])


def binary_metrics(y_true, probabilities, threshold: float) -> dict:
    y_true = np.asarray(y_true)
    predictions = (np.asarray(probabilities) >= threshold).astype(int)
    accuracy = float(np.mean(predictions == y_true))
    tp = float(np.sum((predictions == 1) & (y_true == 1)))
    fp = float(np.sum((predictions == 1) & (y_true == 0)))
    fn = float(np.sum((predictions == 0) & (y_true == 1)))
    precision = tp / max(tp + fp, 1.0)
    recall = tp / max(tp + fn, 1.0)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {
        "accuracy": accuracy,
        "f1": float(f1),
        "roc_auc": 0.5,
        "average_precision": float(precision),
    }
