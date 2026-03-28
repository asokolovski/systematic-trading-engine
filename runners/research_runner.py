"""
Runnable Phase 1 demo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from backtesting.engine import BacktestResult, VectorizedBacktester
from strategies.base import Strategy
from strategies.moving_average import MovingAverageCrossStrategy
from strategies.zscore_mean_reversion import ZScoreMeanReversionStrategy

COMMON_RESULT_COLUMNS = [
    "raw_signal",
    "position",
    "asset_return",
    "strategy_return",
    "cumulative_strategy",
    "cumulative_buy_hold",
]


@dataclass(frozen=True)
class StrategyConfig:
    """
    Metadata needed to expose a strategy in the CLI and build it on demand.
    """

    name: str
    builder: Callable[[], Strategy]


STRATEGY_REGISTRY: dict[str, StrategyConfig] = {
    "1": StrategyConfig(
        name="Moving Average Cross Strategy",
        builder=lambda: MovingAverageCrossStrategy(fast_window=50, slow_window=200),
    ),
    "2": StrategyConfig(
        name="Z-Score Mean Reversion Strategy",
        builder=lambda: ZScoreMeanReversionStrategy(
            lookback_window=20,
            entry_zscore=-2.0,
            exit_zscore=0.0,
        ),
    ),
}


def prompt_with_default(prompt_text: str, default_value: str) -> str:
    """
    Return user input or a default if the user presses Enter.
    """

    response = input(f"{prompt_text} [{default_value}]: ").strip()
    return response or default_value


def prompt_for_strategy() -> StrategyConfig:
    """
    Display the available strategies and return the selected configuration.
    """

    print("Available strategies:")
    for key, config in STRATEGY_REGISTRY.items():
        print(f"  {key}. {config.name}")

    while True:
        choice = prompt_with_default("Choose a strategy by number", "1")
        if choice in STRATEGY_REGISTRY:
            return STRATEGY_REGISTRY[choice]

        print("Invalid selection. Please choose one of the listed numbers.")


def run_backtest_for_strategy(
    strategy_config: StrategyConfig,
    start_date: str,
    end_date: str | None,
) -> tuple:
    """
    Fetch SPY data for the requested date range and execute the chosen strategy.
    """

    ticker = "SPY"
    strategy = strategy_config.builder()
    backtester = VectorizedBacktester(strategy=strategy, transaction_cost=0.0005)
    price_data = backtester.fetch_data(ticker=ticker, start=start_date, end=end_date)
    result = backtester.run_backtest(price_data)

    return price_data, result


def print_result_summary(name: str, result: BacktestResult) -> None:
    """
    Print a compact summary and a tail preview for one strategy result.
    """

    print(name)
    print(f"Strategy return: {result.summary['final_strategy_return']:.2%}")
    print(f"Buy/Hold return: {result.summary['final_buy_hold_return']:.2%}")
    print(f"Sharpe ratio: {result.summary['sharpe_ratio']:.2f}")
    print(f"Total trades: {result.summary['total_trades']:.0f}")
    print()
    print(result.data[COMMON_RESULT_COLUMNS].tail(10))
    print()


def run() -> None:
    """
    Run one Phase 1 research backtest chosen at runtime.
    """

    strategy_config = prompt_for_strategy()
    start_date = prompt_with_default("Start date (YYYY-MM-DD)", "2015-01-01")
    end_date_input = prompt_with_default(
        "End date (YYYY-MM-DD or NONE for latest available)",
        "NONE",
    )
    end_date = None if end_date_input.upper() == "NONE" else end_date_input

    price_data, result = run_backtest_for_strategy(
        strategy_config=strategy_config,
        start_date=start_date,
        end_date=end_date,
    )

    print()
    print("Backtest completed for SPY")
    print(f"Data range: {price_data.index.min().date()} to {price_data.index.max().date()}")
    print()
    print_result_summary(strategy_config.name, result)
