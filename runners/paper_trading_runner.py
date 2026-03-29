"""
Runnable Phase 2 paper-trading demo.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from backtesting.engine import VectorizedBacktester
from paper_trading.market_feed import MarketFeed
from paper_trading.signal_adapters import CompositeSignalStrategy, StrategySignalAdapter
from paper_trading.trading_bot import TradingBot
from strategies.base import Strategy
from strategies.moving_average import MovingAverageCrossStrategy
from strategies.zscore_mean_reversion import ZScoreMeanReversionStrategy


@dataclass(frozen=True)
class PaperTradingStrategyConfig:
    """
    Metadata needed to expose a paper-trading strategy in the CLI.
    """

    name: str
    builder: Callable[[], Strategy]


PAPER_TRADING_STRATEGIES: dict[str, PaperTradingStrategyConfig] = {
    "1": PaperTradingStrategyConfig(
        name="Moving Average Cross Strategy",
        builder=lambda: MovingAverageCrossStrategy(fast_window=50, slow_window=200),
    ),
    "2": PaperTradingStrategyConfig(
        name="Z-Score Mean Reversion Strategy",
        builder=lambda: ZScoreMeanReversionStrategy(
            lookback_window=20,
            entry_zscore=-2.0,
            exit_zscore=0.0,
        ),
    ),
    "3": PaperTradingStrategyConfig(
        name="Composite Confirmation Strategy",
        builder=lambda: MovingAverageCrossStrategy(fast_window=50, slow_window=200),
    ),
}


def prompt_with_default(prompt_text: str, default_value: str) -> str:
    response = input(f"{prompt_text} [{default_value}]: ").strip()
    return response or default_value


def prompt_for_strategy() -> str:
    print("Available paper-trading strategies:")
    for key, config in PAPER_TRADING_STRATEGIES.items():
        print(f"  {key}. {config.name}")

    while True:
        choice = prompt_with_default("Choose a strategy by number", "1")
        if choice in PAPER_TRADING_STRATEGIES:
            return choice
        print("Invalid selection. Please choose one of the listed numbers.")


def build_live_signal_strategy(choice: str):
    """
    Wrap one or more research strategies for live event-driven evaluation.
    """

    if choice == "3":
        return CompositeSignalStrategy(
            strategies=[
                StrategySignalAdapter(
                    MovingAverageCrossStrategy(fast_window=50, slow_window=200)
                ),
                StrategySignalAdapter(
                    ZScoreMeanReversionStrategy(
                        lookback_window=20,
                        entry_zscore=-2.0,
                        exit_zscore=0.0,
                    )
                ),
            ],
            mode="all",
        )

    return StrategySignalAdapter(PAPER_TRADING_STRATEGIES[choice].builder())


def stream_prices(feed: MarketFeed, prices: pd.Series) -> None:
    """
    Replay historical closes as if they were live market ticks.
    """

    for timestamp, price in prices.items():
        feed.update_price(new_price=float(price), timestamp=pd.Timestamp(timestamp))


def run() -> None:
    """
    Simulate a live paper-trading session by streaming historical daily closes.
    """

    strategy_choice = prompt_for_strategy()
    start_date = prompt_with_default("Start date (YYYY-MM-DD)", "2025-01-01")
    end_date_input = prompt_with_default(
        "End date (YYYY-MM-DD or NONE for latest available)",
        "NONE",
    )
    end_date = None if end_date_input.upper() == "NONE" else end_date_input

    ticker = "SPY"
    loader = VectorizedBacktester(strategy=MovingAverageCrossStrategy())
    price_data = loader.fetch_data(ticker=ticker, start=start_date, end=end_date)

    live_strategy = build_live_signal_strategy(strategy_choice)
    feed = MarketFeed(ticker=ticker)
    bot = TradingBot(
        name=f"{PAPER_TRADING_STRATEGIES[strategy_choice].name} Bot",
        strategy=live_strategy,
    )
    feed.subscribe(bot)
    stream_prices(feed, price_data["Close"])

    print()
    print(f"Paper-trading simulation completed for {ticker}")
    print(f"Data range: {price_data.index.min().date()} to {price_data.index.max().date()}")
    print()
    print(bot.status())
    print()
    print(pd.DataFrame(bot.event_log).tail(10))
