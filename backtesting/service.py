"""
Thin application service for running the default research backtest.
"""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.engine import VectorizedBacktester
from strategies.moving_average import MovingAverageCrossStrategy


@dataclass(frozen=True)
class BacktestRequest:
    """
    Minimal inputs accepted by the API-facing backtest flow.
    """

    ticker: str
    start_date: str
    end_date: str | None


def run_default_backtest(request: BacktestRequest) -> dict:
    """
    Execute the default backtest and return a JSON-friendly payload.
    """

    strategy = MovingAverageCrossStrategy(fast_window=50, slow_window=200)
    backtester = VectorizedBacktester(strategy=strategy, transaction_cost=0.0005)

    price_data = backtester.fetch_data(
        ticker=request.ticker,
        start=request.start_date,
        end=request.end_date,
    )
    result = backtester.run_backtest(price_data)

    return {
        "ticker": request.ticker,
        "strategy": "moving_average_cross",
        "start_date": request.start_date,
        "end_date": request.end_date,
        "data_start": str(price_data.index.min().date()),
        "data_end": str(price_data.index.max().date()),
        "summary": result.summary,
    }
