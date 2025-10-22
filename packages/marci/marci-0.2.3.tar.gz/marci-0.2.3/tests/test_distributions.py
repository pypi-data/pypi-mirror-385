import numpy as np
import pytest
from marci import Lognormal
from marci.utils.distributions import (
    Distribution,
    Lognormal_Ratio,
    Poisson,
    Poisson_Lognormal,
    Poisson_Lognormal_Ratio,
    Binomial,
    Beta,
    Binomial_Poisson_Beta,
    Binomial_Poisson_Lognormal_Beta,
    Binomial_Poisson_Lognormal_Ratio_Beta,
    BPLRB_Lognormal_Product,
    safe_poisson,
    safe_binomial,
)


# Test utility functions
def test_safe_poisson():
    """Test the safe_poisson function."""
    # Test normal case
    samples = safe_poisson(5.0, size=1000)
    assert len(samples) == 1000
    assert np.all(samples >= 0)

    # Test with very large lambda
    samples = safe_poisson(1e6, size=100)
    assert len(samples) == 100
    assert np.all(samples >= 0)


def test_safe_binomial():
    """Test the safe_binomial function."""
    # Test normal case
    samples = safe_binomial(100, 0.3, size=1000)
    assert len(samples) == 1000
    assert np.all(samples >= 0)
    assert np.all(samples <= 100)

    # Test edge cases
    samples = safe_binomial(10, 0.0, size=100)
    assert np.all(samples == 0)

    samples = safe_binomial(10, 1.0, size=100)
    assert np.all(samples == 10)


# Test base Distribution class
def test_distribution_abstract():
    """Test that Distribution is abstract and cannot be instantiated."""
    with pytest.raises(TypeError):
        Distribution(mean=1.0, cv=0.5)


# Test Lognormal distribution
def test_lognormal_basic():
    """Test basic Lognormal functionality."""
    mean = 10.0
    cv = 0.5
    d = Lognormal(mean=mean, cv=cv)

    assert d.mean == mean
    assert d.cv == cv
    assert d.std == mean * cv
    assert d.var == (mean * cv) ** 2


def test_lognormal_generate():
    """Test Lognormal sample generation."""
    mean = 10.0
    cv = 0.5
    d = Lognormal(mean=mean, cv=cv)
    size = 100_000
    samples = d.generate(size)

    assert samples.shape == (size,)
    assert np.all(samples > 0)

    # Empirical stats should be close to target
    emp_mean = float(np.mean(samples))
    emp_std = float(np.std(samples, ddof=0))
    emp_cv = emp_std / emp_mean

    assert abs(emp_mean - mean) / mean < 0.03  # within 3%
    assert abs(emp_cv - cv) / cv < 0.08  # within 8%


def test_lognormal_zero_mean():
    """Test Lognormal with zero mean."""
    d = Lognormal(mean=0.0, cv=0.5)
    samples = d.generate(1000)
    # When mean is 0, the distribution should return very small values (not exactly 0)
    assert np.all(samples >= 0)  # Should be non-negative
    assert np.all(samples < 1e-5)  # Should be very small values


def test_lognormal_invalid_size():
    """Test Lognormal with invalid size parameters."""
    d = Lognormal(mean=1.0, cv=0.2)
    for bad in [0, -1, 1.5, None]:
        with pytest.raises(ValueError):
            d.generate(bad)  # type: ignore[arg-type]


# Test Lognormal_Ratio distribution
def test_lognormal_ratio():
    """Test Lognormal_Ratio distribution."""
    A_mean, A_cv = 100.0, 0.2
    B_mean, B_cv = 50.0, 0.3
    d = Lognormal_Ratio(A_mean=A_mean, A_cv=A_cv, B_mean=B_mean, B_cv=B_cv)

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples > 0)

    # Check that the ratio is approximately correct
    expected_ratio = A_mean / B_mean
    emp_ratio = np.mean(samples)
    assert abs(emp_ratio - expected_ratio) / expected_ratio < 0.1


# Test Poisson distribution
def test_poisson():
    """Test Poisson distribution."""
    mean = 5.0
    d = Poisson(mean=mean)

    assert d.mean == mean
    assert d.lambda_ == mean

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers

    emp_mean = np.mean(samples)
    assert abs(emp_mean - mean) / mean < 0.05


# Test Poisson_Lognormal distribution
def test_poisson_lognormal():
    """Test Poisson_Lognormal distribution."""
    lognormal_mean = 5.0
    lognormal_cv = 0.3
    d = Poisson_Lognormal(lognormal_mean=lognormal_mean, lognormal_cv=lognormal_cv)

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers


# Test Poisson_Lognormal_Ratio distribution
def test_poisson_lognormal_ratio():
    """Test Poisson_Lognormal_Ratio distribution."""
    A_mean, A_cv = 100.0, 0.2
    B_mean, B_cv = 50.0, 0.3
    d = Poisson_Lognormal_Ratio(A_mean=A_mean, A_cv=A_cv, B_mean=B_mean, B_cv=B_cv)

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers


# Test Binomial distribution
def test_binomial():
    """Test Binomial distribution."""
    mean = 0.3
    cv = 0.2
    d = Binomial(mean=mean, cv=cv)

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers

    # Check that samples are within expected range
    assert np.all(samples <= d.n)


# Test Beta distribution
def test_beta():
    """Test Beta distribution."""
    mean = 0.3
    cv = 0.2
    d = Beta(mean=mean, cv=cv)

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples <= 1)  # Beta is bounded [0,1]

    emp_mean = np.mean(samples)
    assert abs(emp_mean - mean) / mean < 0.1


# Test Binomial_Poisson_Beta distribution
def test_binomial_poisson_beta():
    """Test Binomial_Poisson_Beta distribution."""
    poisson_mean = 5.0
    beta_mean = 0.3
    beta_cv = 0.2
    d = Binomial_Poisson_Beta(
        poisson_mean=poisson_mean, beta_mean=beta_mean, beta_cv=beta_cv
    )

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers


# Test Binomial_Poisson_Lognormal_Beta distribution
def test_binomial_poisson_lognormal_beta():
    """Test Binomial_Poisson_Lognormal_Beta distribution."""
    lognormal_mean = 5.0
    lognormal_cv = 0.3
    beta_mean = 0.3
    beta_cv = 0.2
    d = Binomial_Poisson_Lognormal_Beta(
        lognormal_mean=lognormal_mean,
        lognormal_cv=lognormal_cv,
        beta_mean=beta_mean,
        beta_cv=beta_cv,
    )

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers


# Test Binomial_Poisson_Lognormal_Ratio_Beta distribution
def test_binomial_poisson_lognormal_ratio_beta():
    """Test Binomial_Poisson_Lognormal_Ratio_Beta distribution."""
    A_mean, A_cv = 100.0, 0.2
    B_mean, B_cv = 50.0, 0.3
    beta_mean = 0.3
    beta_cv = 0.2
    d = Binomial_Poisson_Lognormal_Ratio_Beta(
        A_mean=A_mean,
        A_cv=A_cv,
        B_mean=B_mean,
        B_cv=B_cv,
        beta_mean=beta_mean,
        beta_cv=beta_cv,
    )

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)
    assert np.all(samples == samples.astype(int))  # Should be integers


# Test BPLRB_Lognormal_Product distribution
def test_bplrb_lognormal_product():
    """Test BPLRB_Lognormal_Product distribution."""
    A_mean, A_cv = 100.0, 0.2
    B_mean, B_cv = 50.0, 0.3
    beta_mean = 0.3
    beta_cv = 0.2
    lognormal_mean = 100.0
    lognormal_cv = 0.1
    d = BPLRB_Lognormal_Product(
        A_mean=A_mean,
        A_cv=A_cv,
        B_mean=B_mean,
        B_cv=B_cv,
        beta_mean=beta_mean,
        beta_cv=beta_cv,
        lognormal_mean=lognormal_mean,
        lognormal_cv=lognormal_cv,
    )

    samples = d.generate(10000)
    assert len(samples) == 10000
    assert np.all(samples >= 0)


# Test error handling for all distributions
def test_distribution_error_handling():
    """Test error handling for invalid parameters."""
    # Test negative size
    d = Lognormal(mean=1.0, cv=0.2)
    with pytest.raises(ValueError):
        d.generate(-1)

    with pytest.raises(ValueError):
        d.generate(0)

    with pytest.raises(ValueError):
        d.generate(1.5)


# Integration test with realistic parameters
def test_distributions_integration():
    """Test various distribution classes with realistic parameters."""
    cv_multiplier = 1
    budget_mean, budget_cv = 1000, 0.1 * cv_multiplier
    cpm_mean, cpm_cv = 1e-2, 0.001 * cv_multiplier
    cvr_mean, cvr_cv = 1e-4, 0.1 * cv_multiplier
    aov_mean, aov_cv = 100, 0.1 * cv_multiplier

    budget = Lognormal(mean=budget_mean, cv=budget_cv)
    print("BUDGET".center(80, "="))
    budget.test()
    imps = Poisson_Lognormal_Ratio(
        A_mean=budget_mean, A_cv=budget_cv, B_mean=cpm_mean, B_cv=cpm_cv
    )

    print("IMPS".center(80, "="))
    imps.test()
    convs = Binomial_Poisson_Lognormal_Ratio_Beta(
        A_mean=budget_mean,
        A_cv=budget_cv,
        B_mean=cpm_mean,
        B_cv=cpm_cv,
        beta_mean=cvr_mean,
        beta_cv=cvr_cv,
    )
    print("CONVS".center(80, "="))
    convs.test()

    sales = BPLRB_Lognormal_Product(
        A_mean=budget_mean,
        A_cv=budget_cv,
        B_mean=cpm_mean,
        B_cv=cpm_cv,
        beta_mean=cvr_mean,
        beta_cv=cvr_cv,
        lognormal_mean=aov_mean,
        lognormal_cv=aov_cv,
    )
    print("SALES".center(80, "="))
    sales.test()


# Test edge cases and boundary conditions
def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Test very small means
    d = Lognormal(mean=1e-10, cv=0.1)
    samples = d.generate(1000)
    assert len(samples) == 1000

    # Test very large means
    d = Lognormal(mean=1e6, cv=0.1)
    samples = d.generate(1000)
    assert len(samples) == 1000
    assert np.all(samples > 0)

    # Test very small CV
    d = Lognormal(mean=10.0, cv=1e-10)
    samples = d.generate(1000)
    assert len(samples) == 1000

    # Test very large CV
    d = Lognormal(mean=10.0, cv=10.0)
    samples = d.generate(1000)
    assert len(samples) == 1000
    assert np.all(samples > 0)


# Test distribution properties
def test_distribution_properties():
    """Test that distributions have expected properties."""
    # Test that all distributions inherit from Distribution
    distributions = [
        Lognormal(mean=1.0, cv=0.5),
        Lognormal_Ratio(A_mean=1.0, A_cv=0.5, B_mean=1.0, B_cv=0.5),
        Poisson(mean=1.0),
        Poisson_Lognormal(lognormal_mean=1.0, lognormal_cv=0.5),
        Binomial(mean=0.5, cv=0.2),
        Beta(mean=0.5, cv=0.2),
    ]

    for dist in distributions:
        assert hasattr(dist, "mean")
        assert hasattr(dist, "cv")
        assert hasattr(dist, "std")
        assert hasattr(dist, "var")
        assert hasattr(dist, "generate")
        assert hasattr(dist, "__repr__")
        assert hasattr(dist, "test")

        # Test that generate returns numpy array
        samples = dist.generate(100)
        assert isinstance(samples, np.ndarray)
        assert len(samples) == 100


# Test distribution string representations
def test_distribution_repr():
    """Test that distributions have proper string representations."""
    d = Lognormal(mean=10.0, cv=0.5)
    repr_str = repr(d)
    assert "Lognormal" in repr_str
    assert "mean=10.0" in repr_str
    assert "cv=0.5" in repr_str


# Test distribution test method
def test_distribution_test_method():
    """Test the built-in test method of distributions."""
    d = Lognormal(mean=10.0, cv=0.5)

    # Test with small sample size
    d.test(size=1000, verbose=False)

    # Test with default parameters
    d.test(verbose=False)
