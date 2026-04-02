"""
FastAPI application exposing the research backtester as a small REST API.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from api.schemas import BacktestRunRequest, BacktestRunResponse, HealthResponse
from backtesting.service import BacktestRequest, run_default_backtest

app = FastAPI(
    title="Systematic Trading Engine API",
    version="0.1.0",
    description="Minimal REST API for running the default research backtest.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Lightweight health check for local testing and containers.
    """

    return HealthResponse(status="ok")


@app.post("/backtests/run", response_model=BacktestRunResponse)
def run_backtest(payload: BacktestRunRequest) -> BacktestRunResponse:
    """
    Execute the default backtest for the requested ticker and date range.
    """

    request = BacktestRequest(
        ticker=payload.ticker,
        start_date=payload.start_date.isoformat(),
        end_date=payload.end_date.isoformat() if payload.end_date else None,
    )

    try:
        result = run_default_backtest(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Backtest execution failed.") from exc

    return BacktestRunResponse.model_validate(result)
