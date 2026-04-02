"""
Pydantic contracts for the REST API.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class BacktestRunRequest(BaseModel):
    """
    Request contract for executing the default backtest.
    """

    ticker: str = Field(..., min_length=1, max_length=10)
    start_date: date
    end_date: date | None = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("ticker must not be empty.")
        return cleaned

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, value: date | None, info) -> date | None:
        start_date = info.data.get("start_date")
        if value is not None and start_date is not None and value < start_date:
            raise ValueError("end_date must be on or after start_date.")
        return value


class BacktestSummary(BaseModel):
    final_strategy_return: float
    final_buy_hold_return: float
    total_trades: float
    sharpe_ratio: float


class BacktestRunResponse(BaseModel):
    """
    Response contract for the default backtest result.
    """

    ticker: str
    strategy: str
    start_date: date
    end_date: date | None = None
    data_start: date
    data_end: date
    summary: BacktestSummary


class HealthResponse(BaseModel):
    status: str
