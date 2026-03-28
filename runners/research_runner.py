"""
Runnable Phase 1 demo.
"""

from __future__ import annotations

from backtesting.engine import VectorizedBacktester
from strategies.moving_average import MovingAverageCrossStrategy


def run() -> None:
    """
    Run a simple moving-average crossover backtest on SPY.
    """

    ticker = "SPY"
    strategy = MovingAverageCrossStrategy(fast_window=50, slow_window=200)
    backtester = VectorizedBacktester(strategy=strategy, transaction_cost=0.0005)

    price_data = backtester.fetch_data(ticker=ticker, start="2015-01-01")
    result = backtester.run_backtest(price_data)

    print(f"Backtest completed for {ticker}")
    print(f"Strategy return: {result.summary['final_strategy_return']:.2%}")
    print(f"Buy/Hold return: {result.summary['final_buy_hold_return']:.2%}")
    print(f"Total trades: {result.summary['total_trades']:.0f}")
    print()
    print("Preview of the research dataframe:")
    print(
        result.data[
            [
                "Close",
                "fast_sma",
                "slow_sma",
                "raw_signal",
                "position",
                "asset_return",
                "strategy_return",
                "cumulative_strategy",
                "cumulative_buy_hold",
            ]
        ].tail(10)
    )
