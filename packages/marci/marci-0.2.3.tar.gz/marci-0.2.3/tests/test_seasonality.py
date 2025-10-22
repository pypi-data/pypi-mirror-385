import numpy as np
import pandas as pd
import pytest
from marci import Seasonality


def test_seasonality_basic_functionality():
    s = Seasonality(seed=42)
    index = pd.date_range("2023-01-01", periods=365, freq="D")

    # Test values method
    values = s.values(index)
    assert len(values) == 365
    assert isinstance(values, pd.Series)
    assert np.isclose(values.mean(), 1.0, atol=1e-10)
    assert values.index.equals(index)

    # Test raw_standardized method
    raw_std = s.raw_standardized(index)
    assert len(raw_std) == 365
    assert isinstance(raw_std, pd.Series)
    assert np.isclose(raw_std.mean(), 0.0, atol=1e-10)
    assert np.isclose(raw_std.std(), 1.0, atol=1e-2)  # More tolerant for std


def test_seasonality_cv_zero():
    s = Seasonality(cv=0.0, seed=42)
    index = pd.date_range("2023-01-01", periods=100, freq="D")

    values = s.values(index)
    # With CV=0, values should be close to 1.0 (normalized)
    assert np.isclose(values.mean(), 1.0, atol=1e-10)


def test_seasonality_invalid_index():
    s = Seasonality(seed=42)

    with pytest.raises(TypeError, match="index must be a pandas.DatetimeIndex"):
        s.values([1, 2, 3])


def test_seasonality_harmonics_zero():
    s = Seasonality(
        weekly_harmonics=0, monthly_harmonics=0, annual_harmonics=0, seed=42
    )
    index = pd.date_range("2023-01-01", periods=100, freq="D")

    values = s.values(index)
    # Should still return valid output (all ones when cv=0, or normalized when cv>0)
    assert len(values) == 100
    assert isinstance(values, pd.Series)


# Note: Seasonality class doesn't have a plot method, so no plot test
