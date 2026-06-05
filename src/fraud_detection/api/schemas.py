from typing import Annotated

from pydantic import BaseModel, Field, field_validator

NonNegativeFloat = Annotated[float, Field(ge=0)]


class Transaction(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=100)
    amount: NonNegativeFloat
    oldbalance_org: NonNegativeFloat
    newbalance_orig: NonNegativeFloat
    oldbalance_dest: NonNegativeFloat
    newbalance_dest: NonNegativeFloat
    transaction_type: str = Field(..., min_length=1, max_length=20)
    hour: int = Field(..., ge=0, le=23)

    @field_validator("transaction_type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        value = value.upper().strip()
        allowed = {"CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"}
        if value not in allowed:
            raise ValueError(f"transaction_type must be one of {sorted(allowed)}")
        return value


class PredictionResponse(BaseModel):
    transaction_id: str
    prediction: int
    fraud_probability: float
    confidence_score: float
    model_version: str


class BatchPredictionRequest(BaseModel):
    transactions: list[Transaction] = Field(..., min_length=1, max_length=1000)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    model_loaded: bool
    model_version: str
