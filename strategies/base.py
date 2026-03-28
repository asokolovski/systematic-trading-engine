"""
Abstract strategy definitions for the research backtester.

This file contains only the interface so the contract is easy to locate during
an interview discussion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """
    Abstract trading strategy contract.

    Any new strategy can plug into the backtester as long as it implements
    generate_signals. This keeps signal logic separate from portfolio math.
    """

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Return a copy of the input data with strategy-specific columns added.

        Expected output:
        - raw_signal: desired position generated using information available
          at the close of the current bar.

        The backtester will later shift this signal by one bar to prevent
        lookahead bias before applying returns.
        """
