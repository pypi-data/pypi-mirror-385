from __future__ import annotations

import matplotlib.pyplot as plt
from typing import Union
from .plot_utils import style
import numpy as np


class Elasticity:
    def __init__(self, elasticity_coef: float, saturation_rate: float = 0.0):
        """
        Elasticity-based return function with safe handling of saturation_rate -> 0.

        Parameters
        ----------
        elasticity_coef : float
            Target slope at x=1 (k). Must be > 0.
        saturation_rate : float, default=0.0
            Controls speed of saturation. Larger values -> faster saturation.
        tol : float
            Numerical tolerance for treating saturation_rate as 0.
        """
        if elasticity_coef <= 0:
            raise ValueError("elasticity_coef must be > 0")

        self.tol = 1e-3
        self.k = max(elasticity_coef, self.tol)
        self.saturation_rate = max(saturation_rate, self.k)

        # Detect saturation_rate ≈ 0 -> use limit formulas
        self.use_limit = abs(self.saturation_rate) < self.tol

        if not self.use_limit:
            self.exp_alpha = np.exp(-self.saturation_rate)
            denom = 1 - self.exp_alpha

            if np.isclose(self.k, 0):
                self.c = 0.0
            else:
                self.c = (self.saturation_rate * self.exp_alpha) / (
                    self.k * denom**2
                ) - 1 / denom

            self.a = (1 + self.c * denom) / denom

    def roas(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Total returns T(x)."""
        x = np.asarray(x, dtype=float).clip(min=self.tol)
        return np.power(x, self.k - 1)

    def total_return(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Total returns T(x)."""
        x = np.asarray(x, dtype=float).clip(min=self.tol)
        return np.power(x, self.k)

    def margin_return(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Marginal returns T'(x)."""
        x = np.asarray(x, dtype=float).clip(min=self.tol)
        return self.k * np.power(x, self.k - 1)

    # def total_return(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    #     """Total returns T(x)."""
    #     x = np.asarray(x, dtype=float)

    #     if self.use_limit:
    #         return x / (self.k + (1 - self.k) * x)

    #     u = 1 - np.exp(-self.saturation_rate * x)
    #     return self.a * u / (1 + self.c * u)

    # def margin_return(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    #     """Marginal returns T'(x)."""
    #     x = np.asarray(x, dtype=float)

    #     if self.use_limit:
    #         return self.k / (self.k + (1 - self.k) * x) ** 2

    #     u = 1 - np.exp(-self.saturation_rate * x)
    #     return (self.a * self.saturation_rate * np.exp(-self.saturation_rate * x)) / (
    #         1 + self.c * u
    #     ) ** 2

    # def roas(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    #     """Return on ad spend = TR(x)/x."""
    #     x = np.asarray(x, dtype=float)

    #     if self.use_limit:
    #         with np.errstate(divide="ignore", invalid="ignore"):
    #             roas = 1 / (self.k + (1 - self.k) * x)
    #             roas = np.where(x == 0, self.margin_return(0), roas)
    #         return roas

    #     with np.errstate(divide="ignore", invalid="ignore"):
    #         roas = self.total_return(x) / x
    #         roas = np.where(x == 0, self.margin_return(0), roas)
    #     return roas

    def plot(
        self,
        ax=None,
        max_x: float = 4,
        max_y: float = None,
        num: int = 200,
    ):
        """Plot TR, MR, and ROAS curves."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(7, 5))

        x = np.linspace(0, max_x, num)
        ax.plot([0, 2], [2, 0], lw=1, ls="--", color="gray")
        ax.plot([0, max_x], [1, 1], lw=1, ls="--", color="gray")
        ax.plot([0, max_x], [0, max_x], lw=1, ls="--", color="gray")
        ax.plot(
            x, self.total_return(x), label="Total Returns", lw=2, color="dodgerblue"
        )
        ax.plot(
            x,
            self.margin_return(x),
            label=f"Marginal Returns\nMR(1)={self.margin_return(1):.2%}",
            lw=2,
            color="orangered",
        )

        ax.plot(x, self.roas(x), label="ROAS", lw=2, color="limegreen")

        style(
            ax,
            "%",
            "%",
            "Budget",
            title="Elasticity Curves",
        )
        # Set y-limits after style() to avoid tight_layout() override
        if max_y is not None:
            ax.set_ylim(0, max_y)
        return ax
