import pytest
import pandas as pd
import numpy as np
from marci.utils.seasonality import Seasonality


class TestSeasonalityIntegration:
    """Test suite for Seasonality integration scenarios from local tests."""

    def test_seasonality_basic_functionality(self):
        """Test basic seasonality functionality."""
        s = Seasonality(cv=1)
        index = pd.date_range("2023-01-01", periods=365, freq="D")
        values = s.values(index)
        
        # Test basic properties
        assert len(values) == 365
        assert isinstance(values, pd.Series)
        assert values.index.equals(index)
        
        # Test statistical properties
        assert np.isclose(values.mean(), 1.0, atol=1e-10)
        assert values.std() > 0

    def test_seasonality_different_cv_values(self):
        """Test seasonality with different CV values."""
        cv_values = [0.1, 0.5, 1.0, 2.0, 5.0]
        index = pd.date_range("2023-01-01", periods=365, freq="D")
        
        for cv in cv_values:
            s = Seasonality(cv=cv)
            values = s.values(index)
            
            # Test that values are generated
            assert len(values) == 365
            assert isinstance(values, pd.Series)
            
            # Test that mean is close to 1
            assert np.isclose(values.mean(), 1.0, atol=1e-10)

    def test_seasonality_different_periods(self):
        """Test seasonality with different time periods."""
        s = Seasonality(cv=1)
        
        periods = [30, 90, 180, 365, 730]
        
        for period in periods:
            index = pd.date_range("2023-01-01", periods=period, freq="D")
            values = s.values(index)
            
            # Test that values are generated for each period
            assert len(values) == period
            assert isinstance(values, pd.Series)
            assert values.index.equals(index)
            
            # Test that mean is close to 1
            assert np.isclose(values.mean(), 1.0, atol=1e-10)

    def test_seasonality_different_frequencies(self):
        """Test seasonality with different frequencies."""
        s = Seasonality(cv=1)
        
        frequencies = ["D", "W", "M", "Q", "Y"]
        
        for freq in frequencies:
            index = pd.date_range("2023-01-01", periods=100, freq=freq)
            values = s.values(index)
            
            # Test that values are generated for each frequency
            assert len(values) == 100
            assert isinstance(values, pd.Series)
            assert values.index.equals(index)

    def test_seasonality_consistency(self):
        """Test seasonality consistency across multiple calls."""
        s = Seasonality(cv=1, seed=42)  # Fixed seed for consistency
        index = pd.date_range("2023-01-01", periods=365, freq="D")
        
        # Test that multiple calls with same seed produce same results
        values1 = s.values(index)
        values2 = s.values(index)
        
        assert values1.equals(values2)

    def test_seasonality_different_seeds(self):
        """Test seasonality with different seeds."""
        index = pd.date_range("2023-01-01", periods=365, freq="D")
        
        s1 = Seasonality(cv=1, seed=42)
        s2 = Seasonality(cv=1, seed=123)
        
        values1 = s1.values(index)
        values2 = s2.values(index)
        
        # Test that different seeds produce different results
        assert not values1.equals(values2)
        
        # But both should have similar statistical properties
        assert np.isclose(values1.mean(), 1.0, atol=1e-10)
        assert np.isclose(values2.mean(), 1.0, atol=1e-10)

    def test_seasonality_edge_cases(self):
        """Test seasonality with edge cases."""
        # Test with very low CV
        s_low = Seasonality(cv=0.01)
        index = pd.date_range("2023-01-01", periods=100, freq="D")
        values_low = s_low.values(index)
        
        assert len(values_low) == 100
        assert np.isclose(values_low.mean(), 1.0, atol=1e-10)
        
        # Test with very high CV
        s_high = Seasonality(cv=10.0)
        values_high = s_high.values(index)
        
        assert len(values_high) == 100
        assert np.isclose(values_high.mean(), 1.0, atol=1e-10)

    def test_seasonality_zero_cv(self):
        """Test seasonality with zero CV."""
        s = Seasonality(cv=0.0)
        index = pd.date_range("2023-01-01", periods=100, freq="D")
        values = s.values(index)
        
        # With zero CV, all values should be 1.0
        assert np.allclose(values, 1.0)

    def test_seasonality_raw_standardized(self):
        """Test seasonality raw standardized method."""
        s = Seasonality(cv=1)
        index = pd.date_range("2023-01-01", periods=365, freq="D")
        
        values = s.values(index)
        raw_std = s.raw_standardized(index)
        
        # Test that raw_standardized produces different results
        assert not values.equals(raw_std)
        
        # Test statistical properties of raw_standardized
        assert np.isclose(raw_std.mean(), 0.0, atol=1e-10)
        assert np.isclose(raw_std.std(), 1.0, atol=1e-2)

    def test_seasonality_with_campaign_integration(self):
        """Test seasonality integration with campaign scenarios."""
        # Test seasonality with different campaign parameters
        seasonality_scenarios = [
            {"cv": 0.1, "name": "Low Seasonality"},
            {"cv": 0.5, "name": "Medium Seasonality"},
            {"cv": 1.0, "name": "High Seasonality"},
            {"cv": 2.0, "name": "Very High Seasonality"},
        ]
        
        for scenario in seasonality_scenarios:
            s = Seasonality(cv=scenario["cv"])
            index = pd.date_range("2023-01-01", periods=365, freq="D")
            values = s.values(index)
            
            # Test that seasonality values are generated
            assert len(values) == 365
            assert isinstance(values, pd.Series)
            assert np.isclose(values.mean(), 1.0, atol=1e-10)
            
            # Test that higher CV produces more variation
            if scenario["cv"] > 0:
                assert values.std() > 0

    def test_seasonality_long_term_patterns(self):
        """Test seasonality with long-term patterns."""
        s = Seasonality(cv=1)
        
        # Test with multiple years
        index = pd.date_range("2020-01-01", periods=1095, freq="D")  # 3 years
        values = s.values(index)
        
        assert len(values) == 1095
        assert isinstance(values, pd.Series)
        assert values.index.equals(index)
        assert np.isclose(values.mean(), 1.0, atol=1e-10)

    def test_seasonality_monthly_patterns(self):
        """Test seasonality with monthly patterns."""
        s = Seasonality(cv=1)
        
        # Test with monthly frequency
        index = pd.date_range("2023-01-01", periods=12, freq="M")
        values = s.values(index)
        
        assert len(values) == 12
        assert isinstance(values, pd.Series)
        assert values.index.equals(index)
        assert np.isclose(values.mean(), 1.0, atol=1e-10)

    def test_seasonality_quarterly_patterns(self):
        """Test seasonality with quarterly patterns."""
        s = Seasonality(cv=1)
        
        # Test with quarterly frequency
        index = pd.date_range("2023-01-01", periods=4, freq="Q")
        values = s.values(index)
        
        assert len(values) == 4
        assert isinstance(values, pd.Series)
        assert values.index.equals(index)
        assert np.isclose(values.mean(), 1.0, atol=1e-10)
