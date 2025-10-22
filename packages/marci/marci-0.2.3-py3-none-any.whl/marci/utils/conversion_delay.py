from __future__ import annotations

import matplotlib.pyplot as plt
from typing import Union

import numpy as np
import pandas as pd

from .math_utils import antidiag_sums
from .plot_utils import style


class Conversion_Delay:
    def __init__(self, p: float = 0.3, duration: int = 7):
        if not (0 <= p <= 1):
            raise ValueError("p must be in [0, 1].")
        if duration < 1:
            raise ValueError("duration must be >= 1.")
        self.p = float(p)
        self.duration = int(duration)

    @property
    def probs(self) -> np.ndarray:
        if self.duration == 1:
            return np.array([1.0], dtype=float)

        p = np.zeros(self.duration, dtype=float)
        p[0] = 1 - self.p
        rem = self.p
        k = np.arange(1, self.duration)
        power = min(self.p, 1 - self.p) if self.p not in (0.0, 1.0) else 1.0
        u = np.exp(-(k**power))
        tail = rem * (u / u.sum())
        p[1:] = tail
        p[-1] += 1.0 - p.sum()
        return p

    @staticmethod
    def _normalize_daily(series: pd.Series) -> pd.Series:
        """
        Coerce to strictly daily DatetimeIndex, sum duplicates, sort, and fill gaps with zeros.
        Handles unsorted input and tz-aware indices.
        """
        if not isinstance(series.index, pd.DatetimeIndex):
            idx = pd.to_datetime(series.index, errors="raise")
        else:
            idx = series.index

        if idx.tz is not None:
            idx = idx.tz_convert("UTC").tz_localize(None)
        idx = idx.normalize()

        s = pd.Series(series.to_numpy(dtype=float), index=idx, dtype="float64")
        s = s.groupby(level=0).sum().sort_index()
        full_idx = pd.date_range(s.index.min(), s.index.max(), freq="D")
        s = s.reindex(full_idx, fill_value=0.0)

        if (s < 0).any():
            raise ValueError("Input conversions must be non-negative.")
        return s

    def delay(
        self, convs: Union[pd.Series, np.ndarray, list[int], list[float]]
    ) -> pd.Series:
        """
        Apply conversion delay. Returns a daily pd.Series of realized conversions
        with zero rows removed. Handles unsorted Series with skipped/duplicate days.
        """
        probs = self.probs

        if isinstance(convs, pd.Series):
            convs_daily = self._normalize_daily(convs)
            x = convs_daily.values.astype(float)
            start = convs_daily.index[0]
        else:
            x = np.asarray(convs, dtype=float).ravel()
            if x.ndim != 1:
                x = x.ravel()
            if np.any(x < 0):
                raise ValueError("x must be non-negative.")
            start = pd.Timestamp.today().normalize()

        n_days_in = len(x)

        attr_convs = np.empty((n_days_in, self.duration), dtype=np.int64)
        for i, n in enumerate(x):
            n_int = int(np.round(n))
            if n_int < 0:
                raise ValueError("x must be non-negative after rounding.")
            attr_convs[i] = np.random.multinomial(n_int, probs)

        realized = antidiag_sums(attr_convs).astype(np.int64)
        out_index = pd.date_range(
            start=start, periods=n_days_in + self.duration - 1, freq="D"
        )
        out = pd.Series(realized, index=out_index, name="attr_convs")

        # Remove zero-conversion days
        out = out[out.ne(0)]
        # Ensure dtype int64 even if empty
        return out.astype("int64", copy=False)

    def plot(self, ax=None, bar_width=0.8):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 5))

        probs = self.probs
        days = np.arange(1, self.duration + 1)
        ax.bar(days, probs, width=bar_width, alpha=0.7, color="dodgerblue")
        for day, prob in zip(days, probs):
            ax.text(
                day, prob + 0.01, f"{prob:.2%}", ha="center", va="bottom", fontsize=9
            )

        style(
            ax,
            y_fmt="%",
            x_label="Day",
            y_label="Probability",
            title="Conversion Delay",
            legend=False,
        )
        return ax
