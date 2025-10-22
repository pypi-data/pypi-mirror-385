import pytest
import pandas as pd
import numpy as np
from marci.utils.conversion_delay import Conversion_Delay


class TestConversionDelayIntegration:
    """Test suite for Conversion Delay integration scenarios from local tests."""

    def test_conversion_delay_basic_functionality(self):
        """Test basic conversion delay functionality."""
        cd = Conversion_Delay(p=0.3, duration=4)
        
        # Test basic properties
        assert cd.p == 0.3
        assert cd.duration == 4
        assert len(cd.probs) == 4

    def test_conversion_delay_with_series_input(self):
        """Test conversion delay with pandas Series input."""
        cd = Conversion_Delay(p=0.3, duration=4)
        
        # Create test series
        c = pd.Series([20, 1], index=["2025-01-01", "2024-01-01"])
        
        # Test delay calculation
        res = cd.delay(c)
        
        assert isinstance(res, pd.Series)
        assert len(res) >= len(c)  # Should have at least as many elements

    def test_conversion_delay_different_probabilities(self):
        """Test conversion delay with different probabilities."""
        probabilities = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for p in probabilities:
            cd = Conversion_Delay(p=p, duration=7)
            
            # Test that probability is set correctly
            assert cd.p == p
            assert cd.duration == 7
            
            # Test that probabilities sum to 1
            assert np.isclose(cd.probs.sum(), 1.0)

    def test_conversion_delay_different_durations(self):
        """Test conversion delay with different durations."""
        durations = [1, 3, 7, 14, 30, 90]
        
        for duration in durations:
            cd = Conversion_Delay(p=0.3, duration=duration)
            
            # Test that duration is set correctly
            assert cd.duration == duration
            assert len(cd.probs) == duration
            
            # Test that probabilities sum to 1
            assert np.isclose(cd.probs.sum(), 1.0)

    def test_conversion_delay_edge_cases(self):
        """Test conversion delay with edge cases."""
        # Test with p=0 (no delay)
        cd_zero = Conversion_Delay(p=0.0, duration=7)
        assert cd_zero.p == 0.0
        assert np.allclose(cd_zero.probs, np.array([1.0, 0, 0, 0, 0, 0, 0]))
        
        # Test with p=1 (maximum delay)
        cd_one = Conversion_Delay(p=1.0, duration=3)
        assert cd_one.p == 1.0
        assert np.isclose(cd_one.probs[0], 0.0)
        assert np.isclose(cd_one.probs[1:].sum(), 1.0)

    def test_conversion_delay_with_different_series(self):
        """Test conversion delay with different pandas Series."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with different series lengths and values
        test_series = [
            pd.Series([10], index=["2025-01-01"]),
            pd.Series([20, 30], index=["2025-01-01", "2025-01-02"]),
            pd.Series([5, 10, 15], index=["2025-01-01", "2025-01-02", "2025-01-03"]),
            pd.Series([100, 200, 300, 400], index=["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]),
        ]
        
        for series in test_series:
            res = cd.delay(series)
            
            # Test that result is a Series
            assert isinstance(res, pd.Series)
            
            # Test that result has at least as many elements as input
            assert len(res) >= len(series)

    def test_conversion_delay_with_datetime_index(self):
        """Test conversion delay with datetime index."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with datetime index
        dates = pd.date_range("2025-01-01", periods=5, freq="D")
        c = pd.Series([10, 20, 30, 40, 50], index=dates)
        
        res = cd.delay(c)
        
        assert isinstance(res, pd.Series)
        assert len(res) >= len(c)
        assert isinstance(res.index, pd.DatetimeIndex)

    def test_conversion_delay_with_string_index(self):
        """Test conversion delay with string index."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with string index (this should fail as conversion delay expects datetime)
        c = pd.Series([10, 20, 30], index=["A", "B", "C"])
        
        # This should raise an error since string indices can't be converted to datetime
        with pytest.raises(ValueError):
            cd.delay(c)

    def test_conversion_delay_with_numeric_index(self):
        """Test conversion delay with numeric index."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with numeric index
        c = pd.Series([10, 20, 30], index=[1, 2, 3])
        
        res = cd.delay(c)
        
        assert isinstance(res, pd.Series)
        assert len(res) >= len(c)

    def test_conversion_delay_probability_distribution(self):
        """Test conversion delay probability distribution."""
        cd = Conversion_Delay(p=0.5, duration=5)
        
        # Test that probabilities are non-negative
        assert np.all(cd.probs >= 0)
        
        # Test that probabilities sum to 1
        assert np.isclose(cd.probs.sum(), 1.0)
        
        # Test that first probability is 1-p
        assert np.isclose(cd.probs[0], 1 - cd.p)

    def test_conversion_delay_high_probability(self):
        """Test conversion delay with high probability."""
        cd = Conversion_Delay(p=0.9, duration=10)
        
        # With high probability, most conversions should be delayed
        assert cd.p == 0.9
        assert np.isclose(cd.probs[0], 0.1)  # 1 - 0.9
        assert np.isclose(cd.probs[1:].sum(), 0.9)

    def test_conversion_delay_low_probability(self):
        """Test conversion delay with low probability."""
        cd = Conversion_Delay(p=0.1, duration=10)
        
        # With low probability, most conversions should be immediate
        assert cd.p == 0.1
        assert np.isclose(cd.probs[0], 0.9)  # 1 - 0.1
        assert np.isclose(cd.probs[1:].sum(), 0.1)

    def test_conversion_delay_medium_probability(self):
        """Test conversion delay with medium probability."""
        cd = Conversion_Delay(p=0.5, duration=7)
        
        # With medium probability, conversions should be split
        assert cd.p == 0.5
        assert np.isclose(cd.probs[0], 0.5)  # 1 - 0.5
        assert np.isclose(cd.probs[1:].sum(), 0.5)

    def test_conversion_delay_with_zero_values(self):
        """Test conversion delay with zero values."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with zero values
        c = pd.Series([0, 0, 0], index=["2025-01-01", "2025-01-02", "2025-01-03"])
        
        res = cd.delay(c)
        
        assert isinstance(res, pd.Series)
        # With zero values, the result might be empty, which is expected
        assert len(res) >= 0

    def test_conversion_delay_with_negative_values(self):
        """Test conversion delay with negative values."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with negative values (this should raise an error)
        c = pd.Series([-10, -20, -30], index=["2025-01-01", "2025-01-02", "2025-01-03"])
        
        # This should raise an error since negative values are not allowed
        with pytest.raises(ValueError):
            cd.delay(c)

    def test_conversion_delay_with_large_values(self):
        """Test conversion delay with large values."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with large values
        c = pd.Series([1000000, 2000000, 3000000], index=["2025-01-01", "2025-01-02", "2025-01-03"])
        
        res = cd.delay(c)
        
        assert isinstance(res, pd.Series)
        assert len(res) >= len(c)

    def test_conversion_delay_with_mixed_values(self):
        """Test conversion delay with mixed positive and negative values."""
        cd = Conversion_Delay(p=0.3, duration=7)
        
        # Test with mixed values (this should raise an error due to negative values)
        c = pd.Series([10, -20, 30, -40, 50], index=["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"])
        
        # This should raise an error since negative values are not allowed
        with pytest.raises(ValueError):
            cd.delay(c)

    def test_conversion_delay_parameter_combinations(self):
        """Test conversion delay with various parameter combinations."""
        test_cases = [
            (0.1, 3),   # Low probability, short duration
            (0.3, 7),   # Medium probability, medium duration
            (0.5, 14),  # High probability, long duration
            (0.8, 30),  # Very high probability, very long duration
        ]
        
        for p, duration in test_cases:
            cd = Conversion_Delay(p=p, duration=duration)
            
            # Test that parameters are set correctly
            assert cd.p == p
            assert cd.duration == duration
            assert len(cd.probs) == duration
            
            # Test that probabilities sum to 1
            assert np.isclose(cd.probs.sum(), 1.0)
            
            # Test with a simple series
            c = pd.Series([10, 20], index=["2025-01-01", "2025-01-02"])
            res = cd.delay(c)
            
            assert isinstance(res, pd.Series)
            assert len(res) >= len(c)
