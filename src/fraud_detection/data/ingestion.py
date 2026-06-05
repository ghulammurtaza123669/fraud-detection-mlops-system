from pathlib import Path

import numpy as np
import pandas as pd

TRANSACTION_TYPES = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]


def load_transactions(path: Path | str | None = None) -> pd.DataFrame:
    if path and Path(path).exists():
        return pd.read_csv(path)
    return generate_synthetic_transactions()


def generate_synthetic_transactions(rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    transaction_type = rng.choice(TRANSACTION_TYPES, rows, p=[0.16, 0.27, 0.12, 0.30, 0.15])
    amount = rng.lognormal(mean=8.2, sigma=1.0, size=rows).round(2)
    old_org = rng.lognormal(mean=9.0, sigma=1.15, size=rows).round(2)
    balance_delta_noise = rng.normal(0, amount * 0.08)
    new_orig = np.maximum(old_org - amount + balance_delta_noise, 0).round(2)
    old_dest = rng.lognormal(mean=8.7, sigma=1.25, size=rows).round(2)
    new_dest = np.maximum(old_dest + amount + rng.normal(0, amount * 0.12), 0).round(2)
    hour = rng.integers(0, 24, rows)

    high_risk_type = np.isin(transaction_type, ["TRANSFER", "CASH_OUT"])
    emptied_origin = (old_org > 0) & (new_orig / np.maximum(old_org, 1) < 0.05)
    amount_pressure = amount > np.quantile(amount, 0.92)
    odd_hour = np.isin(hour, [0, 1, 2, 3, 4])
    probability = (
        0.015
        + high_risk_type * 0.08
        + emptied_origin * 0.23
        + amount_pressure * 0.17
        + odd_hour * 0.04
    )
    is_fraud = rng.binomial(1, np.clip(probability, 0, 0.9))

    fraud_idx = np.where(is_fraud == 1)[0]
    new_orig[fraud_idx] = 0
    transaction_type[fraud_idx] = rng.choice(["TRANSFER", "CASH_OUT"], len(fraud_idx))

    return pd.DataFrame(
        {
            "transaction_id": [f"txn_{i:06d}" for i in range(rows)],
            "amount": amount,
            "oldbalance_org": old_org,
            "newbalance_orig": new_orig,
            "oldbalance_dest": old_dest,
            "newbalance_dest": new_dest,
            "transaction_type": transaction_type,
            "hour": hour,
            "is_fraud": is_fraud,
        }
    )
