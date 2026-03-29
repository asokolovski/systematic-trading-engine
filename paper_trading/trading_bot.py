"""
Trading bot observer for the paper-trading event-driven layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from paper_trading.base import LiveSignalStrategy, MarketObserver


@dataclass
class TradingBot(MarketObserver):
    """
    Observer that wakes up on every market tick and evaluates its strategy.
    """

    name: str
    strategy: LiveSignalStrategy
    current_position: float = 0.0
    latest_signal: float = 0.0
    last_action: str = "HOLD"
    last_price: float | None = None
    last_ticker: str | None = None
    evaluation_status: str = "Waiting for market data"
    event_log: list[dict[str, object]] = field(default_factory=list)

    def update(self, ticker: str, current_price: float, price_history: pd.DataFrame) -> None:
        """
        Evaluate the latest signal after receiving a new market tick.
        """

        self.last_ticker = ticker
        self.last_price = current_price
        self.latest_signal = self.strategy.evaluate_signal(price_history)

        previous_position = self.current_position
        self.current_position = self.latest_signal

        if previous_position == 0.0 and self.current_position == 1.0:
            self.last_action = "BUY"
        elif previous_position == 1.0 and self.current_position == 0.0:
            self.last_action = "SELL"
        else:
            self.last_action = "HOLD"

        self.evaluation_status = (
            f"Evaluated {len(price_history)} ticks. "
            f"Signal={self.latest_signal:.1f}, action={self.last_action}."
        )
        self.event_log.append(
            {
                "timestamp": price_history.index[-1],
                "ticker": ticker,
                "price": current_price,
                "signal": self.latest_signal,
                "action": self.last_action,
                "position": self.current_position,
            }
        )

    def status(self) -> dict[str, object]:
        """
        Return the bot's current state for logging or future API exposure.
        """

        return {
            "name": self.name,
            "ticker": self.last_ticker,
            "last_price": self.last_price,
            "current_position": self.current_position,
            "latest_signal": self.latest_signal,
            "last_action": self.last_action,
            "evaluation_status": self.evaluation_status,
            "events_processed": len(self.event_log),
        }
