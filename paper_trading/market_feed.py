"""
Market feed subject for the Observer Pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from paper_trading.base import MarketObserver


@dataclass
class MarketFeed:
    """
    Subject that stores the latest market state and notifies subscribers.
    """

    ticker: str
    price_history: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame(columns=["Close"])
    )
    current_price: float | None = None
    subscribers: list[MarketObserver] = field(default_factory=list)

    def subscribe(self, observer: MarketObserver) -> None:
        """
        Register an observer to receive future price updates.
        """

        if observer not in self.subscribers:
            self.subscribers.append(observer)

    def unsubscribe(self, observer: MarketObserver) -> None:
        """
        Remove an observer from the notification list.
        """

        if observer in self.subscribers:
            self.subscribers.remove(observer)

    def notify_all(self) -> None:
        """
        Push the latest market update to every registered observer.
        """

        if self.current_price is None:
            return

        for observer in self.subscribers:
            observer.update(
                ticker=self.ticker,
                current_price=self.current_price,
                price_history=self.price_history.copy(),
            )

    def update_price(self, new_price: float, timestamp: pd.Timestamp | None = None) -> None:
        """
        Append a new observed price and notify all observers.
        """

        if new_price <= 0:
            raise ValueError("new_price must be positive.")

        if timestamp is None:
            if self.price_history.empty:
                timestamp = pd.Timestamp.utcnow().normalize()
            else:
                timestamp = self.price_history.index[-1] + pd.Timedelta(days=1)

        timestamp = pd.Timestamp(timestamp)
        self.current_price = float(new_price)
        self.price_history.loc[timestamp, "Close"] = self.current_price
        self.notify_all()
