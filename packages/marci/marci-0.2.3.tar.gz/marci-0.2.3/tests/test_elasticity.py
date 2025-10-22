import numpy as np
import pytest
from marci import Elasticity


def test_elasticity_saturation_zero():
    e = Elasticity(elasticity_coef=0.5, saturation_rate=0.0)
    # Test at x=1 should give k slope
    assert np.isclose(e.margin_return(1.0), 0.5)

    x = np.array([0.0, 1.0, 2.0])
    mr = e.margin_return(x)
    tr = e.total_return(x)
    r = e.roas(x)

    # Shapes should match input
    assert mr.shape == x.shape
    assert tr.shape == x.shape
    assert r.shape == x.shape


def test_elasticity_with_saturation():
    e = Elasticity(elasticity_coef=0.3, saturation_rate=1.0)
    x = np.array([0.0, 1.0, 2.0, 3.0])

    mr = e.margin_return(x)
    tr = e.total_return(x)
    roas_vals = e.roas(x)

    # Shapes
    assert mr.shape == x.shape
    assert tr.shape == x.shape
    assert roas_vals.shape == x.shape

    # ROAS at x=0 should be finite (not NaN)
    assert np.isfinite(roas_vals[0])

    # Values should be finite for x > 0
    assert np.all(np.isfinite(mr[1:]))
    assert np.all(np.isfinite(tr[1:]))
    assert np.all(np.isfinite(roas_vals[1:]))


def test_elasticity_coef_constraint():
    # Valid values should work
    Elasticity(elasticity_coef=0.1, saturation_rate=1.0)
    Elasticity(elasticity_coef=1.0, saturation_rate=0.0)

    # Invalid values should raise ValueError
    with pytest.raises(ValueError, match="elasticity_coef must be > 0"):
        Elasticity(elasticity_coef=0.0)

    with pytest.raises(ValueError, match="elasticity_coef must be > 0"):
        Elasticity(elasticity_coef=-0.5)
