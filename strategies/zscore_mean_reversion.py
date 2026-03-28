"""
Concrete z-score mean reversion strategy implementation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import Strategy


class ZScoreMeanReversionStrategy(Strategy):
    """
    Mean reversion strategy using a rolling z-score on price.

    Long/flat rules:
    - Enter long when price is sufficiently below its rolling mean.
    - Exit when price has reverted back toward the mean.
    """

    def __init__(
        self,
        lookback_window: int = 20,
        entry_zscore: float = -2.0,
        exit_zscore: float = 0.0,
    ) -> None:
        if lookback_window <= 1:
            raise ValueError("lookback_window must be greater than 1.")
        if entry_zscore >= exit_zscore:
            raise ValueError("entry_zscore must be smaller than exit_zscore.")

        self.lookback_window = lookback_window
        self.entry_zscore = entry_zscore
        self.exit_zscore = exit_zscore

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute a rolling z-score and turn it into a long/flat position plan.

        The random variable we standardize is the close price relative to its
        recent rolling distribution. A very negative z-score means price is far
        below its local mean, which this strategy treats as a potential bounce.
        """

        if "Close" not in data.columns:
            raise ValueError("Input data must contain a 'Close' column.")

        signals = data.copy()

        signals["rolling_mean"] = (
            signals["Close"].rolling(window=self.lookback_window, min_periods=1).mean()
        )
        signals["rolling_std"] = (
            signals["Close"].rolling(window=self.lookback_window, min_periods=1).std()
        )

        # A zero standard deviation means prices were flat over the window, so
        # the z-score is undefined. We replace those cases with NaN, then treat
        # them as non-signals after the calculation.
        safe_std = signals["rolling_std"].replace(0.0, np.nan)
        signals["z_score"] = (
            (signals["Close"] - signals["rolling_mean"]) / safe_std
        ).fillna(0.0)

        enter_long = signals["z_score"] <= self.entry_zscore
        exit_long = signals["z_score"] >= self.exit_zscore

        # We build the desired regime as a vectorized state machine:
        # - 1.0 means we want to be long.
        # - 0.0 means we want to be flat.
        # Values between explicit entry/exit signals are forward-filled so the
        # position persists until an exit condition occurs.
        desired_state = pd.Series(np.nan, index=signals.index, dtype=float)
        desired_state.loc[enter_long] = 1.0
        desired_state.loc[exit_long] = 0.0

        signals["raw_signal"] = desired_state.ffill().fillna(0.0)

        return signals
