"""
Paper-trading package exports.
"""

from paper_trading.market_feed import MarketFeed
from paper_trading.signal_adapters import CompositeSignalStrategy, StrategySignalAdapter
from paper_trading.trading_bot import TradingBot

__all__ = [
    "CompositeSignalStrategy",
    "MarketFeed",
    "StrategySignalAdapter",
    "TradingBot",
]
