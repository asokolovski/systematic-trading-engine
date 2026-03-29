"""
Abstract interfaces for the paper-trading event-driven layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class MarketObserver(ABC):
    """
    Observer contract for objects that react to live market updates.
    """

    @abstractmethod
    def update(self, ticker: str, current_price: float, price_history: pd.DataFrame) -> None:
        """
        React to a new market tick pushed by the MarketFeed subject.
        """


class LiveSignalStrategy(ABC):
    """
    Strategy contract for event-driven signal evaluation.

    Unlike the Phase 1 batch strategy contract, this interface answers the
    question: "Given the price history observed so far, what position do we
    want right now?"
    """

    @abstractmethod
    def evaluate_signal(self, price_history: pd.DataFrame) -> float:
        """
        Return the desired position for the latest observed market state.

        Convention:
        - 1.0 means long
        - 0.0 means flat
        """
