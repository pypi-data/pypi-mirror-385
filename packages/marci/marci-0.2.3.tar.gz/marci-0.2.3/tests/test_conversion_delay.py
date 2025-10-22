import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests
from marci import Conversion_Delay


def test_probs_sum_and_limits():
    cd = Conversion_Delay(p=0.3, duration=7)
    probs = cd.probs
    assert probs.shape == (7,)
    assert np.isclose(probs.sum(), 1.0)
    assert np.all(probs >= 0)

    cd1 = Conversion_Delay(p=0.0, duration=5)
    assert np.allclose(cd1.probs, np.array([1.0, 0, 0, 0, 0]))

    cd2 = Conversion_Delay(p=1.0, duration=3)
    assert np.isclose(cd2.probs[0], 0.0)
    assert np.isclose(cd2.probs[1:].sum(), 1.0)


def test_delay_shapes_and_index():
    np.random.seed(42)
    cd = Conversion_Delay(p=0.4, duration=4)
    convs = pd.Series(
        [10, 20, 30], index=pd.date_range("2025-01-01", periods=3, freq="D")
    )
    result = cd.delay(convs)

    # Length should be N + duration - 1
    assert len(result) == len(convs) + 4 - 1
    assert result.index[0] == convs.index.min()
    assert result.name == "attr_convs"
    assert np.issubdtype(result.dtype, np.integer)


def test_delay_non_series_input():
    np.random.seed(123)
    cd = Conversion_Delay(p=0.2, duration=3)
    arr = np.array([5, 0, 10])
    res = cd.delay(arr)
    assert len(res) >= len(arr)  # Should have at least the original length


def test_conversion_delay_plot():
    cd = Conversion_Delay(p=0.4, duration=5)

    # Test plot function returns ax
    ax = cd.plot()
    assert ax is not None

    # Test with custom bar width
    ax2 = cd.plot(bar_width=0.6)
    assert ax2 is not None
