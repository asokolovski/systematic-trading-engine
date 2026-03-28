"""
Strategy package exports.
"""

from strategies.base import Strategy
from strategies.moving_average import MovingAverageCrossStrategy

__all__ = ["Strategy", "MovingAverageCrossStrategy"]
