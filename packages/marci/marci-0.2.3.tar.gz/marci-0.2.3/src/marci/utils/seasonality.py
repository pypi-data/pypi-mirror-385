from __future__ import annotations

import math
import warnings
from typing import Optional, Union

import numpy as np
import pandas as pd


class Seasonality:
    """
    Seasonal multiplier generator with strictly-positive outputs.

    Core idea:
      1) Build a raw seasonal signal from Fourier bases (weekly/monthly/annual).
      2) Standardize it to z (mean≈0, std≈1 over a 4-year cycle).
      3) Map via a log-link: u = exp(s * z), which guarantees u > 0.
      4) Choose scale s so CV(u) ~= target cv on the same 4-year cycle.
      5) Store mean-one normalized u for fast lookup.

    Use .values(index) to retrieve a mean-one seasonal series for any DatetimeIndex.
    """

    def __init__(
        self,
        cv: float = 0.2,
        anchor_date: Union[str, pd.Timestamp] = "2000-01-01",
        weekly_harmonics: int = 4,
        monthly_harmonics: int = 1,
        annual_harmonics: int = 5,
        weekly_prominance: float = 1.5,
        monthly_prominance: float = 1.5,
        annual_prominance: float = 4.0,
        seed: Optional[Union[int, np.random.Generator]] = None,
        month_days: float = 30.4375,
        year_days: float = 365.2425,
    ):
        # -------- parameter validation --------
        if cv < 0:
            raise ValueError("cv must be >= 0.")
        if weekly_harmonics < 0 or monthly_harmonics < 0 or annual_harmonics < 0:
            raise ValueError("harmonics must be >= 0.")
        if (
            not np.isfinite(weekly_prominance)
            or not np.isfinite(monthly_prominance)
            or not np.isfinite(annual_prominance)
        ):
            raise ValueError("prominance weights must be finite.")
        if month_days <= 0 or year_days <= 0:
            raise ValueError("month_days and year_days must be > 0.")

        self.cv = float(cv)
        self.anchor_date = pd.Timestamp(anchor_date)
        self.Kw, self.Km, self.Ky = map(
            int, (weekly_harmonics, monthly_harmonics, annual_harmonics)
        )
        self.ww, self.wm, self.wy = (
            float(weekly_prominance),
            float(monthly_prominance),
            float(annual_prominance),
        )
        self.W, self.M, self.Y = 7.0, float(month_days), float(year_days)

        if isinstance(seed, np.random.Generator):
            self.rng = seed
        else:
            self.rng = np.random.default_rng(seed)

        def ab(K: int):
            if K <= 0:
                return None, None
            k = np.arange(1, K + 1, dtype=float)
            s = 1 / np.sqrt(k)  # decay higher harmonics
            return self.rng.normal(0.0, s), self.rng.normal(0.0, s)

        self.aw, self.bw = ab(self.Kw)
        self.am, self.bm = ab(self.Km)
        self.ay, self.by = ab(self.Ky)

        # Pre-calculate normalized seasonalities on a 4-year leap cycle
        self._precalculate_seasonalities()

    # ---------------- internal: fourier construction ----------------

    def _fourier(
        self, t: np.ndarray, period: float, K: Optional[int], a, b, weight: float
    ) -> np.ndarray:
        if (K is None) or (K <= 0) or (weight == 0):
            return np.zeros_like(t, dtype=float)
        k = np.arange(1, K + 1, dtype=float)  # (K,)
        omega = 2 * np.pi * k / period  # (K,)
        C = np.cos(t[:, None] * omega[None, :])  # (N, K)
        S = np.sin(t[:, None] * omega[None, :])  # (N, K)
        return weight * (C @ a + S @ b)  # (N,)

    def _raw(self, index: pd.DatetimeIndex) -> np.ndarray:
        # Global phase anchored to fixed epoch
        t = ((index - self.anchor_date) / pd.Timedelta(days=1)).to_numpy(dtype=float)
        y = (
            self._fourier(t, self.W, self.Kw, self.aw, self.bw, self.ww)
            + self._fourier(t, self.M, self.Km, self.am, self.bm, self.wm)
            + self._fourier(t, self.Y, self.Ky, self.ay, self.by, self.wy)
        )
        return y

    # ---------------- log-link normalization with CV calibration ----------------

    @staticmethod
    def _cv_of_exp(z: np.ndarray, s: float) -> float:
        """Empirical CV of exp(s*z) for given standardized z."""
        u = np.exp(s * z)
        m = float(u.mean())
        if not np.isfinite(m) or m == 0.0:
            return float("inf")
        return float(u.std(ddof=0) / m)

    def _precalculate_seasonalities(self):
        """
        Compute normalized seasonalities on a 4-year (1461-day) cycle.
        Steps:
          - Build raw y on the cycle.
          - If cv==0 or y is flat, store ones.
          - Else standardize to z, find s with binary search so CV(exp(s*z)) ~= cv.
          - Store u/mean(u) for fast lookup (strictly positive, mean 1).
        """
        cycle_start = pd.Timestamp("2000-01-01")  # leap-year cycle anchor
        cycle_days = 365 * 4 + 1  # 1461
        idx = pd.date_range(cycle_start, periods=cycle_days, freq="D")

        y = self._raw(idx)
        sd = float(y.std(ddof=0))

        if self.cv == 0.0 or sd == 0.0 or not np.isfinite(sd):
            self._normalized_seasonalities = np.ones(cycle_days, dtype=float)
            return

        z = (y - float(y.mean())) / sd  # empirical mean 0, std 1

        target = float(self.cv)

        # Analytic warm-start assuming z ~ N(0,1):
        # CV(exp(sZ)) = sqrt(exp(s^2) - 1)  =>  s0 = sqrt(log(1 + target^2))
        s0 = math.sqrt(max(0.0, math.log1p(target * target)))

        def cv_s(s: float) -> float:
            return self._cv_of_exp(z, s)

        # Bracket s where CV crosses target
        lo, hi = 0.0, max(1.0, 2.0 * s0 + 1e-6)
        for _ in range(60):  # expand if needed
            if cv_s(hi) >= target:
                break
            hi *= 2.0
            if hi > 1e6:  # safety
                break

        if cv_s(hi) < target:
            warnings.warn(
                "Seasonality: unable to reach requested CV with log-link; using maximum attainable scale.",
                RuntimeWarning,
            )
            s = hi
        else:
            # Binary search for s
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if cv_s(mid) < target:
                    lo = mid
                else:
                    hi = mid
            s = 0.5 * (lo + hi)

        u = np.exp(s * z)  # strictly positive
        self._normalized_seasonalities = u / float(u.mean())  # mean = 1

    # ---------------- public API ----------------

    def values(self, index: pd.DatetimeIndex) -> pd.Series:
        """
        Return seasonal multipliers for `index` with mean=1 on the requested window.

        Implementation:
          - Wrap precomputed 1461-day normalized seasonalities using modulo day index.
          - Renormalize the returned window to mean exactly 1 (preserves positivity).
        """
        if not isinstance(index, pd.DatetimeIndex):
            raise TypeError("index must be a pandas.DatetimeIndex")

        cycle_start = pd.Timestamp("2000-01-01")
        days_from_start = ((index - cycle_start) / pd.Timedelta(days=1)).astype(int)
        cycle_days = 1461
        cycle_idx = np.mod(days_from_start, cycle_days)

        vals = self._normalized_seasonalities[cycle_idx]

        mean_val = float(np.mean(vals)) or 1.0
        vals = vals / mean_val

        return pd.Series(vals, index=index)

    def raw_standardized(self, index: pd.DatetimeIndex) -> pd.Series:
        """
        Window-local z-scored raw signal (mean 0, std 1 on the window).
        Useful for diagnostics; not used in the positive mapping.
        """
        y = self._raw(index)
        sd = float(y.std(ddof=0)) or 1.0
        return pd.Series((y - float(y.mean())) / sd, index=index)
