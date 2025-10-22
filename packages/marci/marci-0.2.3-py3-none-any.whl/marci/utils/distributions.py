from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final


import numpy as np
import pandas as pd

TOL = 1e-6


def safe_poisson(lam, size=None):
    lam = np.asarray(lam, dtype=np.float64)
    if size is not None:
        lam = np.broadcast_to(lam, size)

    out = np.empty_like(lam, dtype=np.int64)

    mask = lam < 1 / TOL
    if np.any(mask):
        out[mask] = np.random.poisson(lam[mask])

    if np.any(~mask):
        approx = np.random.normal(lam[~mask], np.sqrt(lam[~mask]))
        out[~mask] = np.maximum(0, np.rint(approx)).astype(np.int64)

    return out


def safe_binomial(n, p, size=None, rng=None):
    """
    Robust Binomial sampler using a single tolerance knob `TOL`.
    - Exact via Generator.binomial by default (64-bit capable).
    - For small p, uses corrected Poisson with λ = -n*log1p(-p) when λ is moderate.
    - Symmetry trick for p > 0.5.
    - Returns int64, clipped to [0, n].
    """
    if rng is None:
        rng = np.random.default_rng()

    p = np.asarray(p, dtype=np.float64)
    n = np.asarray(n)

    # Broadcast
    if size is not None:
        n = np.broadcast_to(n, size)
        p = np.broadcast_to(p, size)
    else:
        n, p = np.broadcast_arrays(n, p)

    # Validate
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p must be finite and in [0, 1].")

    if not np.issubdtype(n.dtype, np.integer):
        n_i64 = n.astype(np.int64, copy=False)
        if np.any((n_i64 < 0) | (n_i64 != n)):
            raise ValueError("n must be nonnegative integers.")
        n = n_i64
    else:
        if np.any(n < 0):
            raise ValueError("n must be nonnegative integers.")
        n = n.astype(np.int64, copy=False)

    out = np.zeros_like(n, dtype=np.int64)

    # Trivial fast paths
    mask_p1 = p == 1.0
    out[mask_p1] = n[mask_p1]
    work = ~((n == 0) | (p == 0.0) | mask_p1)
    if not np.any(work):
        return out

    n_w = n[work]
    p_w = p[work]

    # Symmetry: sample the rarer side
    flip = p_w > 0.5
    p_eff = np.where(flip, 1.0 - p_w, p_w)  # in [0, 0.5]
    n_eff = n_w

    # Single-knob regime selection
    tiny_p = TOL
    lam_max = 1.0 / TOL  # only use Poisson if mean isn't huge
    lam_corr = -n_eff * np.log1p(-p_eff)

    use_poisson = (p_eff <= tiny_p) & (lam_corr <= lam_max)

    samples = np.empty_like(n_eff, dtype=np.int64)

    # Small-p: corrected Poisson (Le Cam)
    if np.any(use_poisson):
        idx = use_poisson
        s = rng.poisson(lam_corr[idx]).astype(np.int64)
        samples[idx] = np.minimum(s, n_eff[idx])  # enforce support

    # Otherwise: exact (Generator API handles 64-bit n)
    if np.any(~use_poisson):
        idx = ~use_poisson
        samples[idx] = rng.binomial(n_eff[idx], p_eff[idx]).astype(np.int64)

    # Undo symmetry
    samples = np.where(flip, n_eff - samples, samples)

    out[work] = samples
    return out


class Distribution(ABC):
    def __init__(self, mean: float, cv: float, name: str = "") -> None:
        mean, cv = self.handle_small_mean_cv(mean, cv, name)
        self.name = name
        self.mean: Final[float] = float(mean)
        self.cv: Final[float] = float(cv)
        self.std: Final[float] = float(mean * cv)
        self.var: Final[float] = float(self.std**2)

    @abstractmethod
    def generate(self, size: int) -> np.ndarray:
        """Generate random samples from the distribution.

        Args:
                        size: Number of samples to generate. Must be a positive integer.

        Returns:
                        A 1D numpy array of random samples.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, mean={self.mean}, cv={self.cv})"

    def handle_small_mean_cv(self, mean, cv, name="", max_mean=None):
        mean = float(mean)
        cv = float(cv)
        if mean < TOL:
            print(f"{self.__class__.__name__}({name}, mean={mean}, cv={cv})")
            print(f"Mean is too small, setting to {TOL} for stability")
            mean = TOL
        if max_mean is not None and mean > max_mean:
            print(f"Mean is too large, setting to {max_mean} for stability")
            mean = max_mean
        if cv < TOL:
            cv = TOL
        return mean, cv

    def test(self, size=1_000_000, verbose=True, digits=4):
        sim = self.generate(size)
        mean = sim.mean()
        std = sim.std()
        cv = std / mean if mean != 0 else 0
        stats = pd.DataFrame(
            {
                "mean": [self.mean, mean],
                "std": [self.std, std],
                "cv": [self.cv, cv],
                "min": [np.nan, sim.min()],
                "max": [np.nan, sim.max()],
            },
            index=["exp", "sim"],
        ).T
        stats["delta"] = stats["sim"] / stats["exp"] - 1
        fmt = {
            "exp": f"{{:,.{digits}f}}".format,
            "sim": f"{{:,.{digits}f}}".format,
            "delta": f"{{:,.{digits}%}}".format,
        }
        if verbose:
            print(self.__repr__())
            print(sim[:10])
            print(stats.to_string(formatters=fmt))


class Lognormal(Distribution):
    def __init__(self, mean: float, cv: float, name: str = "") -> None:
        mean, cv = self.handle_small_mean_cv(mean, cv)
        super().__init__(mean, cv, name)
        self.sigma: Final[float] = float(np.sqrt(np.log(1.0 + cv**2)))
        self.mu: Final[float] = float(np.log(mean) - 0.5 * self.sigma**2)

    def generate(self, size: int) -> np.ndarray:
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size must be a positive integer")
        if self.mu == 0:
            return np.zeros(size)
        return np.random.lognormal(self.mu, self.sigma, size)


class Lognormal_Ratio(Distribution):
    def __init__(
        self, A_mean: float, A_cv: float, B_mean: float, B_cv: float, name: str = ""
    ) -> None:
        A_mean, A_cv = self.handle_small_mean_cv(A_mean, A_cv)
        B_mean, B_cv = self.handle_small_mean_cv(B_mean, B_cv)
        mean = A_mean / B_mean * (1 + B_cv**2)
        cv = np.sqrt((1 + A_cv**2) * (1 + B_cv**2) - 1)
        super().__init__(mean=mean, cv=cv, name=name)
        self.mu = Lognormal(mean=mean, cv=cv).mu
        self.sigma = Lognormal(mean=mean, cv=cv).sigma
        self.A = Lognormal(mean=A_mean, cv=A_cv, name=f"{name}_A")
        self.B = Lognormal(mean=B_mean, cv=B_cv, name=f"{name}_B")

    def generate(self, size: int) -> np.ndarray:
        return self.A.generate(size) / self.B.generate(size)


class Poisson(Distribution):
    def __init__(self, mean: float, name: str = "") -> None:
        mean, cv = self.handle_small_mean_cv(mean, 1 / np.sqrt(mean))
        super().__init__(mean, cv, name)
        self.lambda_ = mean

    def generate(self, size: int) -> np.ndarray:
        return safe_poisson(self.mean, size)


class Poisson_Lognormal(Distribution):
    def __init__(
        self, lognormal_mean: float, lognormal_cv: float, name: str = ""
    ) -> None:
        mean, cv = self.handle_small_mean_cv(lognormal_mean, lognormal_cv)
        self.lambda_ = Lognormal(mean=mean, cv=cv, name=name)
        super().__init__(
            mean=np.exp(self.lambda_.mu + self.lambda_.sigma**2 / 2),
            cv=np.sqrt(
                np.exp(-self.lambda_.mu - self.lambda_.sigma**2 / 2)
                + np.exp(self.lambda_.sigma**2)
                - 1
            ),
        )
        self.lognormal_sigma = self.lambda_.sigma

    def generate(self, size: int) -> np.ndarray:
        return safe_poisson(self.lambda_.generate(size))


class Poisson_Lognormal_Ratio(Distribution):
    def __init__(
        self, A_mean: float, A_cv: float, B_mean: float, B_cv: float, name: str = ""
    ) -> None:
        A_mean, A_cv = self.handle_small_mean_cv(A_mean, A_cv)
        B_mean, B_cv = self.handle_small_mean_cv(B_mean, B_cv)
        self.lambda_ = Lognormal_Ratio(
            A_mean=A_mean, A_cv=A_cv, B_mean=B_mean, B_cv=B_cv, name=name
        )
        super().__init__(
            mean=np.exp(self.lambda_.mu + self.lambda_.sigma**2 / 2),
            cv=np.sqrt(
                np.exp(-self.lambda_.mu - self.lambda_.sigma**2 / 2)
                + np.exp(self.lambda_.sigma**2)
                - 1
            ),
        )
        self.lognormal_sigma = self.lambda_.sigma

    def generate(self, size: int) -> np.ndarray:
        return safe_poisson(self.lambda_.generate(size))


class Binomial(Distribution):
    def __init__(self, mean: float, cv: float, name: str = "") -> None:
        mean, cv = self.handle_small_mean_cv(mean, cv)
        super().__init__(mean, cv, name)
        self.n = mean / (1 - mean * cv**2)
        self.p = mean / self.n

    def generate(self, size: int) -> np.ndarray:
        return safe_binomial(int(round(self.n)), self.p, size)


class Beta(Distribution):
    def __init__(self, mean: float, cv: float, name: str = "") -> None:
        mean, cv = self.handle_small_mean_cv(mean, cv, max_mean=1 - TOL)
        super().__init__(mean, cv, name)

        # Standard Beta parameterization
        t = (1.0 - mean) / (mean * cv * cv) - 1.0
        alpha = mean * t
        beta = (1.0 - mean) * t

        self.alpha = alpha
        self.beta = beta

    def generate(self, size: int) -> np.ndarray:
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size must be a positive integer")
        return np.random.beta(self.alpha, self.beta, size)


class Binomial_Poisson_Beta(Distribution):
    def __init__(
        self, poisson_mean: float, beta_mean: float, beta_cv: float, name: str = ""
    ) -> None:
        self.poisson = Poisson(mean=poisson_mean)
        self.beta = Beta(mean=beta_mean, cv=beta_cv)
        mean = self.poisson.mean * self.beta.mean
        cv = np.sqrt(
            (self.beta.alpha + self.beta.beta) / self.poisson.lambda_ / self.beta.alpha
            + self.beta.beta / self.beta.alpha / (self.beta.alpha + self.beta.beta + 1)
        )
        super().__init__(mean, cv, name)

    def generate(self, size: int) -> np.ndarray:
        n = self.poisson.generate(size)
        p = self.beta.generate(size)
        return safe_binomial(n, p, size)


class Binomial_Poisson_Lognormal_Beta(Distribution):
    def __init__(
        self,
        lognormal_mean: float,
        lognormal_cv: float,
        beta_mean: float,
        beta_cv: float,
        name: str = "",
    ) -> None:
        self.poisson_lognormal = Poisson_Lognormal(
            lognormal_mean=lognormal_mean, lognormal_cv=lognormal_cv, name=name
        )
        self.beta = Beta(mean=beta_mean, cv=beta_cv)
        mean = self.poisson_lognormal.mean * self.beta.mean
        if beta_cv == 0:
            cv = 0
        else:
            cv = np.sqrt(
                1 / mean
                + np.exp(self.poisson_lognormal.lognormal_sigma**2)
                * (self.beta.alpha + 1)
                * (self.beta.alpha + self.beta.beta)
                / self.beta.alpha
                / (self.beta.alpha + self.beta.beta + 1)
                - 1
            )
        super().__init__(mean, cv, name)

    def generate(self, size: int) -> np.ndarray:
        n = self.poisson_lognormal.generate(size)
        p = self.beta.generate(size)
        return safe_binomial(n, p, size)


class Binomial_Poisson_Lognormal_Ratio_Beta(Distribution):
    def __init__(
        self,
        A_mean: float,
        A_cv: float,
        B_mean: float,
        B_cv: float,
        beta_mean: float,
        beta_cv: float,
        name: str = "",
    ) -> None:
        self.poisson_lognormal_ratio = Poisson_Lognormal_Ratio(
            A_mean=A_mean, A_cv=A_cv, B_mean=B_mean, B_cv=B_cv, name=name
        )
        self.beta = Beta(mean=beta_mean, cv=beta_cv)
        mean = self.poisson_lognormal_ratio.mean * self.beta.mean
        cv = np.sqrt(
            1 / mean
            + np.exp(self.poisson_lognormal_ratio.lognormal_sigma**2)
            * (self.beta.alpha + 1)
            * (self.beta.alpha + self.beta.beta)
            / self.beta.alpha
            / (self.beta.alpha + self.beta.beta + 1)
            - 1
        )
        super().__init__(mean, cv, name)

    def generate(self, size: int) -> np.ndarray:
        n = self.poisson_lognormal_ratio.generate(size)
        p = self.beta.generate(size)
        return safe_binomial(n, p, size)


class BPLRB_Lognormal_Product(Distribution):
    def __init__(
        self,
        A_mean: float,
        A_cv: float,
        B_mean: float,
        B_cv: float,
        beta_mean: float,
        beta_cv: float,
        lognormal_mean: float,
        lognormal_cv: float,
        name: str = "",
    ) -> None:
        self.binomial = Binomial_Poisson_Lognormal_Ratio_Beta(
            A_mean=A_mean,
            A_cv=A_cv,
            B_mean=B_mean,
            B_cv=B_cv,
            beta_mean=beta_mean,
            beta_cv=beta_cv,
            name=name,
        )
        self.lognormal = Lognormal(mean=lognormal_mean, cv=lognormal_cv)
        mean = self.binomial.mean * self.lognormal.mean
        cv = np.sqrt(
            (1 + self.binomial.var / self.binomial.mean**2)
            * np.exp(self.lognormal.sigma**2)
            - 1
        )
        super().__init__(mean, cv)

    def generate(self, size: int) -> np.ndarray:
        return self.binomial.generate(size) * self.lognormal.generate(size)
