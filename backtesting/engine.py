"""
Vectorized backtester for historical daily data.

Key interview talking points:
- No Python for-loops over rows.
- Signals are shifted by one bar to eliminate lookahead bias.
- Transaction costs are applied only when the position changes.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from strategies.base import Strategy


@dataclass
class BacktestResult:
    """
    Container for both the full timeseries and a compact performance summary.
    """

    data: pd.DataFrame
    summary: dict[str, float]


class VectorizedBacktester:
    """
    Historical backtester that is agnostic to the specific trading strategy.

    It asks the injected Strategy object for raw signals, then handles
    execution timing, return calculation, and basic costs.
    """

    def __init__(self, strategy: Strategy, transaction_cost: float = 0.0005) -> None:
        if transaction_cost < 0:
            raise ValueError("transaction_cost must be non-negative.")

        self.strategy = strategy
        self.transaction_cost = transaction_cost

    def fetch_data(
        self,
        ticker: str,
        start: str = "2015-01-01",
        end: str | None = None,
    ) -> pd.DataFrame:
        """
        Download historical daily OHLCV data from yfinance.
        """

        data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

        if data.empty:
            raise ValueError(f"No data returned for ticker '{ticker}'.")

        # yfinance occasionally returns a multi-index shape depending on the query.
        # This keeps the output predictable for the rest of the pipeline.
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def run_backtest(self, price_data: pd.DataFrame) -> BacktestResult:
        """
        Run the vectorized research backtest.

        Steps:
        1. Ask the strategy to compute its raw signal.
        2. Shift the signal by one day to model execution on the next bar.
        3. Compute daily asset returns.
        4. Apply position, then subtract transaction costs when position changes.
        """

        results = self.strategy.generate_signals(price_data)

        results["asset_return"] = results["Close"].pct_change().fillna(0.0)

        # This is the most important anti-lookahead line in the system.
        # If Tuesday's close generates a long signal, we can only hold that
        # position for Wednesday's return, not Tuesday's already-finished move.
        results["position"] = results["raw_signal"].shift(1).fillna(0.0)

        # Turnover captures when we move from one position to another.
        # For a long/flat strategy, this is 1.0 when we enter or exit.
        results["trade_size"] = results["position"].diff().abs().fillna(0.0)

        gross_strategy_return = results["position"] * results["asset_return"]
        transaction_costs = results["trade_size"] * self.transaction_cost

        results["strategy_return"] = gross_strategy_return - transaction_costs
        results["buy_hold_return"] = results["asset_return"]

        results["cumulative_strategy"] = (1 + results["strategy_return"]).cumprod()
        results["cumulative_buy_hold"] = (1 + results["buy_hold_return"]).cumprod()

        summary = {
            "final_strategy_return": results["cumulative_strategy"].iloc[-1] - 1,
            "final_buy_hold_return": results["cumulative_buy_hold"].iloc[-1] - 1,
            "total_trades": results["trade_size"].sum(),
        }

        return BacktestResult(data=results, summary=summary)
