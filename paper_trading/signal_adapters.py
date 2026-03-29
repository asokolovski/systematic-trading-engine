"""
Adapters that let the paper-trading layer reuse existing research strategies.
"""

from __future__ import annotations

from collections import Counter

import pandas as pd

from paper_trading.base import LiveSignalStrategy
from strategies.base import Strategy


class StrategySignalAdapter(LiveSignalStrategy):
    """
    Adapter from a Phase 1 batch Strategy to a Phase 2 live signal strategy.

    The adapter reruns the strategy over the history observed so far and reads
    the latest raw signal as the current desired position.
    """

    def __init__(self, strategy: Strategy) -> None:
        self.strategy = strategy

    def evaluate_signal(self, price_history: pd.DataFrame) -> float:
        if price_history.empty:
            return 0.0

        evaluated = self.strategy.generate_signals(price_history.copy())
        return float(evaluated["raw_signal"].iloc[-1])


class CompositeSignalStrategy(LiveSignalStrategy):
    """
    Combine multiple live signal strategies into one decision.

    Supported modes:
    - all: every underlying strategy must agree on long
    - any: at least one underlying strategy votes long
    - majority: more than half of strategies vote long
    """

    def __init__(self, strategies: list[LiveSignalStrategy], mode: str = "all") -> None:
        if not strategies:
            raise ValueError("CompositeSignalStrategy requires at least one strategy.")
        if mode not in {"all", "any", "majority"}:
            raise ValueError("mode must be one of: 'all', 'any', 'majority'.")

        self.strategies = strategies
        self.mode = mode

    def evaluate_signal(self, price_history: pd.DataFrame) -> float:
        votes = [strategy.evaluate_signal(price_history) for strategy in self.strategies]

        if self.mode == "all":
            return 1.0 if all(vote >= 1.0 for vote in votes) else 0.0

        if self.mode == "any":
            return 1.0 if any(vote >= 1.0 for vote in votes) else 0.0

        long_votes = Counter(vote >= 1.0 for vote in votes)[True]
        return 1.0 if long_votes > len(votes) / 2 else 0.0
