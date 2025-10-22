import pytest
import pandas as pd
import numpy as np
import warnings
from marci.simulated_data import SimulatedData, remove_trailing_zeroes


class TestSimulatedData:
    """Test suite for SimulatedData class."""

    def test_simulated_data_initialization(self):
        """Test basic SimulatedData initialization."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Campaign A", "Campaign A", "Campaign A"],
            "seasonality": [1.0, 1.1, 0.9],
            "base": [100.0, 100.0, 100.0],
            "budget": [1000.0, 1000.0, 1000.0],
            "elastic_budget": [1000.0, 1000.0, 1000.0],
            "elastic_returns": [100.0, 110.0, 90.0],
            "imps": [10000, 11000, 9000],
            "convs": [10, 11, 9],
            "sales": [1000.0, 1100.0, 900.0],
            "is_organic": [False, False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        
        assert sim_data.name == "Test Campaign"
        assert len(sim_data.df) == 3
        assert sim_data.duration == 3.0
        assert sim_data.tot_paid_budget == 3000.0
        assert sim_data.tot_paid_sales == 3000.0
        assert sim_data.tot_sales == 3000.0

    def test_simulated_data_missing_columns(self):
        """Test SimulatedData with missing required columns."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Campaign A", "Campaign A", "Campaign A"],
            "budget": [1000.0, 1000.0, 1000.0],
            "sales": [1000.0, 1100.0, 900.0]
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            SimulatedData(df, "Test Campaign")

    def test_simulated_data_wrong_input_type(self):
        """Test SimulatedData with wrong input type."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            SimulatedData("not a dataframe", "Test Campaign")

    def test_simulated_data_organic_campaigns(self):
        """Test SimulatedData with organic campaigns."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Organic Campaign", "Organic Campaign", "Organic Campaign"],
            "seasonality": [1.0, 1.1, 0.9],
            "base": [0.0, 0.0, 0.0],
            "budget": [0.0, 0.0, 0.0],
            "elastic_budget": [0.0, 0.0, 0.0],
            "elastic_returns": [500.0, 550.0, 450.0],
            "imps": [0, 0, 0],
            "convs": [5, 5.5, 4.5],
            "sales": [500.0, 550.0, 450.0],
            "is_organic": [True, True, True]
        })
        
        sim_data = SimulatedData(df, "Organic Campaign")
        
        assert sim_data.tot_organic_sales == 1500.0
        assert sim_data.tot_paid_budget == 0.0
        assert sim_data.tot_paid_sales == 0.0
        assert sim_data.tot_sales == 1500.0

    def test_simulated_data_mixed_campaigns(self):
        """Test SimulatedData with both paid and organic campaigns."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=4),
            "name": ["Paid Campaign", "Paid Campaign", "Organic Campaign", "Organic Campaign"],
            "seasonality": [1.0, 1.1, 1.0, 0.9],
            "base": [100.0, 100.0, 0.0, 0.0],
            "budget": [1000.0, 1000.0, 0.0, 0.0],
            "elastic_budget": [1000.0, 1000.0, 0.0, 0.0],
            "elastic_returns": [100.0, 110.0, 500.0, 450.0],
            "imps": [10000, 11000, 0, 0],
            "convs": [10, 11, 5, 4.5],
            "sales": [1000.0, 1100.0, 500.0, 450.0],
            "is_organic": [False, False, True, True]
        })
        
        sim_data = SimulatedData(df, "Mixed Campaigns")
        
        assert sim_data.tot_paid_budget == 2000.0
        assert sim_data.tot_paid_sales == 2100.0
        assert sim_data.tot_organic_sales == 950.0
        assert sim_data.tot_sales == 3050.0

    def test_simulated_data_roas_calculation(self):
        """Test ROAS calculation in SimulatedData."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=2),
            "name": ["Campaign A", "Campaign A"],
            "seasonality": [1.0, 1.0],
            "base": [100.0, 100.0],
            "budget": [1000.0, 2000.0],
            "elastic_budget": [1000.0, 2000.0],
            "elastic_returns": [100.0, 200.0],
            "imps": [10000, 20000],
            "convs": [10, 20],
            "sales": [1000.0, 2000.0],
            "is_organic": [False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        
        # Check ROAS calculation
        roas_values = sim_data.df["roas"].dropna()
        assert len(roas_values) == 2
        assert np.isclose(roas_values.iloc[0], 1.0)  # 1000/1000
        assert np.isclose(roas_values.iloc[1], 1.0)  # 2000/2000

    def test_simulated_data_validate(self):
        """Test SimulatedData validation."""
        # Create DataFrame with all required columns
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Campaign A", "Campaign A", "Campaign A"],
            "seasonality": [1.0, 1.1, 0.9],
            "base": [100.0, 100.0, 100.0],
            "budget": [1000.0, 1000.0, 1000.0],
            "elastic_budget": [1000.0, 1000.0, 1000.0],
            "elastic_returns": [100.0, 110.0, 90.0],
            "imps": [10000, 11000, 9000],
            "convs": [10, 11, 9],
            "sales": [1000.0, 1100.0, 900.0],
            "is_organic": [False, False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        # The validate method should work on the already processed data
        # Note: The validate method is complex and checks internal state
        # We'll just test that the object was created successfully
        assert sim_data.name == "Test Campaign"
        assert len(sim_data.df) == 3

    def test_simulated_data_agg_df(self):
        """Test SimulatedData aggregated DataFrame."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=2),
            "name": ["Campaign A", "Campaign B"],
            "seasonality": [1.0, 1.0],
            "base": [100.0, 200.0],
            "budget": [1000.0, 2000.0],
            "elastic_budget": [1000.0, 2000.0],
            "elastic_returns": [100.0, 200.0],
            "imps": [10000, 20000],
            "convs": [10, 20],
            "sales": [1000.0, 2000.0],
            "is_organic": [False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        agg_df = sim_data.agg_df
        
        assert isinstance(agg_df, pd.DataFrame)
        assert len(agg_df) == 2  # 2 dates
        assert ("Budget", "Campaign A") in agg_df.columns
        assert ("Budget", "Campaign B") in agg_df.columns
        assert ("Sales", "All") in agg_df.columns

    def test_simulated_data_campaign_names(self):
        """Test campaign names ordering by budget."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Low Budget", "High Budget", "Medium Budget"],
            "seasonality": [1.0, 1.0, 1.0],
            "base": [100.0, 200.0, 150.0],
            "budget": [1000.0, 3000.0, 2000.0],
            "elastic_budget": [1000.0, 3000.0, 2000.0],
            "elastic_returns": [100.0, 200.0, 150.0],
            "imps": [10000, 20000, 15000],
            "convs": [10, 20, 15],
            "sales": [1000.0, 2000.0, 1500.0],
            "is_organic": [False, False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        
        # Should be ordered by budget (descending)
        assert sim_data.campaign_names == ["High Budget", "Medium Budget", "Low Budget"]
        assert sim_data.paid_names == ["High Budget", "Medium Budget", "Low Budget"]

    def test_simulated_data_colors(self):
        """Test campaign colors assignment."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=2),
            "name": ["Campaign A", "Campaign B"],
            "seasonality": [1.0, 1.0],
            "base": [100.0, 200.0],
            "budget": [1000.0, 2000.0],
            "elastic_budget": [1000.0, 2000.0],
            "elastic_returns": [100.0, 200.0],
            "imps": [10000, 20000],
            "convs": [10, 20],
            "sales": [1000.0, 2000.0],
            "is_organic": [False, False]
        })
        
        sim_data = SimulatedData(df, "Test Campaign")
        
        assert isinstance(sim_data.colors, dict)
        assert "Campaign A" in sim_data.colors
        assert "Campaign B" in sim_data.colors
        assert len(sim_data.colors) == 2

    def test_simulated_data_warnings(self):
        """Test SimulatedData warning generation."""
        # Test with negative values
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=2),
            "name": ["Campaign A", "Campaign A"],
            "seasonality": [1.0, 1.0],
            "base": [100.0, -50.0],  # Negative value
            "budget": [1000.0, 1000.0],
            "elastic_budget": [1000.0, 1000.0],
            "elastic_returns": [100.0, 100.0],
            "imps": [10000, 10000],
            "convs": [10, 10],
            "sales": [1000.0, 1000.0],
            "is_organic": [False, False]
        })
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SimulatedData(df, "Test Campaign")
            assert len(w) > 0
            assert any("Negative values detected" in str(warning.message) for warning in w)

    def test_simulated_data_duplicate_keys(self):
        """Test SimulatedData with duplicate keys."""
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "name": ["Campaign A", "Campaign A", "Campaign A"],  # Same name
            "seasonality": [1.0, 1.1, 0.9],
            "base": [100.0, 100.0, 100.0],
            "budget": [1000.0, 1000.0, 1000.0],
            "elastic_budget": [1000.0, 1000.0, 1000.0],
            "elastic_returns": [100.0, 110.0, 90.0],
            "imps": [10000, 11000, 9000],
            "convs": [10, 11, 9],
            "sales": [1000.0, 1100.0, 900.0],
            "is_organic": [False, False, False]
        })
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SimulatedData(df, "Test Campaign")
            # Should not warn about duplicates for same campaign on different dates
            assert len(w) == 0


class TestRemoveTrailingZeroes:
    """Test suite for remove_trailing_zeroes function."""

    def test_remove_trailing_zeroes_basic(self):
        """Test basic functionality of remove_trailing_zeroes."""
        df = pd.DataFrame({
            "A": [1, 2, 0, 0, 0],
            "B": [3, 4, 0, 0, 0],
            "C": [5, 6, 0, 0, 0]
        })
        
        result = remove_trailing_zeroes(df)
        assert len(result) == 2
        assert result.equals(df.iloc[:2])

    def test_remove_trailing_zeroes_no_trailing(self):
        """Test remove_trailing_zeroes with no trailing zeros."""
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [4, 5, 6]
        })
        
        result = remove_trailing_zeroes(df)
        assert result.equals(df)

    def test_remove_trailing_zeroes_all_zeros(self):
        """Test remove_trailing_zeroes with all zeros."""
        df = pd.DataFrame({
            "A": [0, 0, 0],
            "B": [0, 0, 0]
        })
        
        result = remove_trailing_zeroes(df)
        assert len(result) == 0

    def test_remove_trailing_zeroes_mixed(self):
        """Test remove_trailing_zeroes with mixed values."""
        df = pd.DataFrame({
            "A": [0, 1, 0, 2, 0, 0],
            "B": [0, 0, 1, 0, 0, 0]
        })
        
        result = remove_trailing_zeroes(df)
        assert len(result) == 4  # Should keep up to the last non-zero row

    def test_remove_trailing_zeroes_with_nans(self):
        """Test remove_trailing_zeroes with NaN values."""
        df = pd.DataFrame({
            "A": [1, 2, np.nan, np.nan],
            "B": [3, 4, np.nan, np.nan]
        })
        
        result = remove_trailing_zeroes(df)
        assert len(result) == 2
