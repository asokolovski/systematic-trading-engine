"""
Concrete moving-average strategy implementations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import Strategy


class MovingAverageCrossStrategy(Strategy):
    """
    Simple moving-average crossover strategy.

    Long when the fast SMA is above the slow SMA, otherwise flat.
    """

    def __init__(self, fast_window: int = 50, slow_window: int = 200) -> None:
        if fast_window <= 0 or slow_window <= 0:
            raise ValueError("Moving-average windows must be positive integers.")
        if fast_window >= slow_window:
            raise ValueError("fast_window must be smaller than slow_window.")

        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add moving averages and a vectorized raw trading signal.

        We use rolling means and np.where instead of Python loops so the
        strategy scales well across longer datasets.
        """

        if "Close" not in data.columns:
            raise ValueError("Input data must contain a 'Close' column.")

        signals = data.copy()

        signals["fast_sma"] = (
            signals["Close"].rolling(window=self.fast_window, min_periods=1).mean()
        )
        signals["slow_sma"] = (
            signals["Close"].rolling(window=self.slow_window, min_periods=1).mean()
        )

        # raw_signal is the position the strategy *wants* to hold after seeing
        # today's close. The backtester will shift it by one day before using it.
        signals["raw_signal"] = np.where(
            signals["fast_sma"] > signals["slow_sma"],
            1.0,
            0.0,
        )

        return signals
