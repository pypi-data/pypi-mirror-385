import pytest
import pandas as pd
import numpy as np
from marci.utils.performance_stats import PerformanceStats


class TestPerformanceStats:
    """Test suite for PerformanceStats class."""

    def test_performance_stats_initialization(self):
        """Test basic PerformanceStats initialization."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 1000.0)
        
        assert stats.df is not None
        assert len(stats.df) == 1
        assert stats.df[("meta", "name")].iloc[0] == "Test Campaign"
        assert stats.df[("meta", "kind")].iloc[0] == "Expected"
        assert stats.df[("sales", "organic")].iloc[0] == 100.0
        assert stats.df[("sales", "paid")].iloc[0] == 200.0
        assert stats.df[("budget", "paid")].iloc[0] == 1000.0

    def test_performance_stats_default_values(self):
        """Test PerformanceStats with default values."""
        stats = PerformanceStats("Test Campaign")
        
        assert stats.df[("meta", "name")].iloc[0] == "Test Campaign"
        assert stats.df[("meta", "kind")].iloc[0] == "Expected"
        assert stats.df[("sales", "organic")].iloc[0] == 0.0
        assert stats.df[("sales", "paid")].iloc[0] == 0.0
        assert stats.df[("budget", "paid")].iloc[0] == 0.0

    def test_performance_stats_zero_values(self):
        """Test PerformanceStats with zero values."""
        stats = PerformanceStats("Test Campaign", "Expected", 0.0, 0.0, 0.0)
        
        assert stats.df[("sales", "organic")].iloc[0] == 0.0
        assert stats.df[("sales", "paid")].iloc[0] == 0.0
        assert stats.df[("budget", "paid")].iloc[0] == 0.0

    def test_performance_stats_none_values(self):
        """Test PerformanceStats with None values."""
        stats = PerformanceStats("Test Campaign", "Expected", None, None, None)
        
        assert stats.df[("sales", "organic")].iloc[0] == 0.0
        assert stats.df[("sales", "paid")].iloc[0] == 0.0
        assert stats.df[("budget", "paid")].iloc[0] == 0.0

    def test_performance_stats_from_list_empty(self):
        """Test from_list with empty list."""
        with pytest.raises(ValueError, match="stats_list cannot be empty"):
            PerformanceStats.from_list("Combined", [])

    def test_performance_stats_from_list_single(self):
        """Test from_list with single PerformanceStats."""
        stats1 = PerformanceStats("Campaign A", "Expected", 100.0, 200.0, 1000.0)
        result = PerformanceStats.from_list("Combined", [stats1])
        
        assert result.df[("meta", "name")].iloc[0] == "Combined"
        assert result.df[("sales", "organic")].iloc[0] == 100.0
        assert result.df[("sales", "paid")].iloc[0] == 200.0
        assert result.df[("budget", "paid")].iloc[0] == 1000.0

    def test_performance_stats_from_list_multiple(self):
        """Test from_list with multiple PerformanceStats."""
        stats1 = PerformanceStats("Campaign A", "Expected", 100.0, 200.0, 1000.0)
        stats2 = PerformanceStats("Campaign B", "Expected", 150.0, 300.0, 1500.0)
        result = PerformanceStats.from_list("Combined", [stats1, stats2])
        
        assert result.df[("meta", "name")].iloc[0] == "Combined"
        assert result.df[("sales", "organic")].iloc[0] == 250.0  # 100 + 150
        assert result.df[("sales", "paid")].iloc[0] == 500.0  # 200 + 300
        assert result.df[("budget", "paid")].iloc[0] == 2500.0  # 1000 + 1500

    def test_performance_stats_from_list_different_kinds(self):
        """Test from_list with different kinds of stats."""
        stats1 = PerformanceStats("Campaign A", "Expected", 100.0, 200.0, 1000.0)
        stats2 = PerformanceStats("Campaign A", "Simulated", 120.0, 250.0, 1000.0)
        result = PerformanceStats.from_list("Combined", [stats1, stats2])
        
        # Should have 2 rows (one for each kind)
        assert len(result.df) == 2
        assert "Expected" in result.df[("meta", "kind")].values
        assert "Simulated" in result.df[("meta", "kind")].values

    def test_performance_stats_str_formatting(self):
        """Test PerformanceStats string formatting."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 1000.0)
        result_str = str(stats)
        
        assert isinstance(result_str, str)
        assert "Test Campaign" in result_str
        assert "Expected" in result_str
        # Check for formatted money values
        assert "$" in result_str
        # Check for percentage values
        assert "%" in result_str

    def test_performance_stats_str_with_zero_budget(self):
        """Test PerformanceStats string formatting with zero budget."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 0.0)
        result_str = str(stats)
        
        assert isinstance(result_str, str)
        assert "Test Campaign" in result_str
        # Should handle division by zero gracefully
        assert "Expected" in result_str

    def test_performance_stats_str_roas_calculation(self):
        """Test ROAS calculation in string representation."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 1000.0)
        result_str = str(stats)
        
        # ROAS should be 200/1000 = 0.2 = 20%
        assert "20%" in result_str or "0.2" in result_str

    def test_performance_stats_str_total_sales(self):
        """Test total sales calculation in string representation."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 1000.0)
        result_str = str(stats)
        
        # Total sales should be 100 + 200 = 300
        assert "$300" in result_str or "300" in result_str

    def test_performance_stats_large_numbers(self):
        """Test PerformanceStats with large numbers."""
        stats = PerformanceStats("Big Campaign", "Expected", 1e6, 2e6, 1e7)
        result_str = str(stats)
        
        assert isinstance(result_str, str)
        assert "Big Campaign" in result_str
        # Should format large numbers with commas
        assert "," in result_str

    def test_performance_stats_negative_values(self):
        """Test PerformanceStats with negative values."""
        stats = PerformanceStats("Test Campaign", "Expected", -100.0, -200.0, 1000.0)
        
        assert stats.df[("sales", "organic")].iloc[0] == -100.0
        assert stats.df[("sales", "paid")].iloc[0] == -200.0
        assert stats.df[("budget", "paid")].iloc[0] == 1000.0

    def test_performance_stats_float_precision(self):
        """Test PerformanceStats with float precision."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.5, 200.7, 1000.3)
        
        assert stats.df[("sales", "organic")].iloc[0] == 100.5
        assert stats.df[("sales", "paid")].iloc[0] == 200.7
        assert stats.df[("budget", "paid")].iloc[0] == 1000.3

    def test_performance_stats_mixed_types(self):
        """Test PerformanceStats with mixed data types."""
        stats = PerformanceStats("Test Campaign", "Expected", 100, 200.5, 1000)
        
        # Should convert to float
        assert isinstance(stats.df[("sales", "organic")].iloc[0], float)
        assert isinstance(stats.df[("sales", "paid")].iloc[0], float)
        assert isinstance(stats.df[("budget", "paid")].iloc[0], float)

    def test_performance_stats_dataframe_structure(self):
        """Test PerformanceStats DataFrame structure."""
        stats = PerformanceStats("Test Campaign", "Expected", 100.0, 200.0, 1000.0)
        df = stats.df
        
        # Check column structure
        assert isinstance(df.columns, pd.MultiIndex)
        assert df.columns.names == ["group", "metric"]
        
        # Check required columns exist
        required_columns = [
            ("meta", "name"),
            ("meta", "kind"),
            ("sales", "organic"),
            ("budget", "paid"),
            ("sales", "paid")
        ]
        for col in required_columns:
            assert col in df.columns

    def test_performance_stats_aggregation(self):
        """Test PerformanceStats aggregation in from_list."""
        stats1 = PerformanceStats("Campaign A", "Expected", 100.0, 200.0, 1000.0)
        stats2 = PerformanceStats("Campaign B", "Expected", 150.0, 300.0, 1500.0)
        stats3 = PerformanceStats("Campaign C", "Expected", 50.0, 100.0, 500.0)
        
        result = PerformanceStats.from_list("Portfolio", [stats1, stats2, stats3])
        
        # Should aggregate all values
        assert result.df[("sales", "organic")].iloc[0] == 300.0  # 100 + 150 + 50
        assert result.df[("sales", "paid")].iloc[0] == 600.0  # 200 + 300 + 100
        assert result.df[("budget", "paid")].iloc[0] == 3000.0  # 1000 + 1500 + 500
