import pytest
import numpy as np
from marci import Budgets


class TestBudgets:
    """Test suite for Budgets class."""

    def test_budgets_initialization(self):
        """Test basic Budgets initialization."""
        budgets = Budgets("Test Budget", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        
        assert budgets.name == "Test Budget"
        assert budgets.campaign_names == ["Campaign A", "Campaign B"]
        assert budgets.campaign_budgets == {"Campaign A": 1000.0, "Campaign B": 2000.0}
        assert budgets.total_budget == 3000.0

    def test_budgets_empty(self):
        """Test Budgets with empty campaign budgets."""
        budgets = Budgets("Empty Budget", {})
        
        assert budgets.name == "Empty Budget"
        assert budgets.campaign_names == []
        assert budgets.campaign_budgets == {}
        assert budgets.total_budget == 0.0

    def test_budgets_single_campaign(self):
        """Test Budgets with single campaign."""
        budgets = Budgets("Single Campaign", {"Only Campaign": 5000.0})
        
        assert budgets.name == "Single Campaign"
        assert budgets.campaign_names == ["Only Campaign"]
        assert budgets.campaign_budgets == {"Only Campaign": 5000.0}
        assert budgets.total_budget == 5000.0

    def test_budgets_getitem(self):
        """Test Budgets item access."""
        budgets = Budgets("Test Budget", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        
        assert budgets["Campaign A"] == 1000.0
        assert budgets["Campaign B"] == 2000.0
        
        with pytest.raises(KeyError):
            budgets["Non-existent Campaign"]

    def test_budgets_repr(self):
        """Test Budgets string representation."""
        budgets = Budgets("Test Budget", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        repr_str = repr(budgets)
        
        assert "Budgets" in repr_str
        assert "Test Budget" in repr_str
        assert "total=$3,000" in repr_str
        assert "Campaign A" in repr_str
        assert "Campaign B" in repr_str

    def test_budgets_len(self):
        """Test Budgets length."""
        budgets = Budgets("Test Budget", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        assert len(budgets) == 2
        
        empty_budgets = Budgets("Empty", {})
        assert len(empty_budgets) == 0

    def test_budgets_iter(self):
        """Test Budgets iteration."""
        budgets = Budgets("Test Budget", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        campaign_names = list(budgets)
        
        assert campaign_names == ["Campaign A", "Campaign B"]

    def test_budgets_from_list_empty(self):
        """Test from_list with empty list."""
        result = Budgets.from_list("Empty", [])
        
        assert result.name == "Empty"
        assert result.campaign_budgets == {}
        assert result.total_budget == 0.0

    def test_budgets_from_list_single(self):
        """Test from_list with single Budgets object."""
        budget1 = Budgets("Budget 1", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        result = Budgets.from_list("Combined", [budget1])
        
        assert result.name == "Combined"
        assert result.campaign_budgets == {"Campaign A": 1000.0, "Campaign B": 2000.0}
        assert result.total_budget == 3000.0

    def test_budgets_from_list_multiple(self):
        """Test from_list with multiple Budgets objects."""
        budget1 = Budgets("Budget 1", {"Campaign A": 1000.0, "Campaign B": 2000.0})
        budget2 = Budgets("Budget 2", {"Campaign B": 1500.0, "Campaign C": 2500.0})
        result = Budgets.from_list("Combined", [budget1, budget2])
        
        # Should keep first occurrence of Campaign B
        assert result.name == "Combined"
        assert result.campaign_budgets == {
            "Campaign A": 1000.0, 
            "Campaign B": 2000.0,  # First occurrence
            "Campaign C": 2500.0
        }
        assert result.total_budget == 5500.0

    def test_budgets_from_list_overlapping_campaigns(self):
        """Test from_list with overlapping campaign names."""
        budget1 = Budgets("Budget 1", {"Campaign A": 1000.0})
        budget2 = Budgets("Budget 2", {"Campaign A": 2000.0, "Campaign B": 3000.0})
        budget3 = Budgets("Budget 3", {"Campaign B": 4000.0, "Campaign C": 5000.0})
        result = Budgets.from_list("Combined", [budget1, budget2, budget3])
        
        # Should keep first occurrence of each campaign
        assert result.campaign_budgets == {
            "Campaign A": 1000.0,  # First occurrence
            "Campaign B": 3000.0,  # First occurrence
            "Campaign C": 5000.0
        }
        assert result.total_budget == 9000.0

    def test_budgets_numeric_types(self):
        """Test Budgets with different numeric types."""
        budgets = Budgets("Test Budget", {
            "Int Campaign": 1000,
            "Float Campaign": 2000.5,
            "Numpy Campaign": np.float64(3000.0)
        })
        
        assert budgets.total_budget == 6000.5
        assert budgets["Int Campaign"] == 1000
        assert budgets["Float Campaign"] == 2000.5
        assert budgets["Numpy Campaign"] == 3000.0

    def test_budgets_zero_budgets(self):
        """Test Budgets with zero budgets."""
        budgets = Budgets("Zero Budget", {"Campaign A": 0.0, "Campaign B": 0.0})
        
        assert budgets.total_budget == 0.0
        assert budgets["Campaign A"] == 0.0
        assert budgets["Campaign B"] == 0.0

    def test_budgets_negative_budgets(self):
        """Test Budgets with negative budgets."""
        budgets = Budgets("Negative Budget", {"Campaign A": -1000.0, "Campaign B": 2000.0})
        
        assert budgets.total_budget == 1000.0
        assert budgets["Campaign A"] == -1000.0
        assert budgets["Campaign B"] == 2000.0

    def test_budgets_large_numbers(self):
        """Test Budgets with large numbers."""
        budgets = Budgets("Large Budget", {"Campaign A": 1e6, "Campaign B": 2e6})
        
        assert budgets.total_budget == 3e6
        assert budgets["Campaign A"] == 1e6
        assert budgets["Campaign B"] == 2e6

    def test_budgets_special_characters_in_names(self):
        """Test Budgets with special characters in campaign names."""
        budgets = Budgets("Special Names", {
            "Campaign-With-Dashes": 1000.0,
            "Campaign_With_Underscores": 2000.0,
            "Campaign With Spaces": 3000.0,
            "Campaign@With#Symbols": 4000.0
        })
        
        assert len(budgets) == 4
        assert budgets.total_budget == 10000.0
        assert "Campaign-With-Dashes" in budgets.campaign_names
        assert "Campaign_With_Underscores" in budgets.campaign_names
        assert "Campaign With Spaces" in budgets.campaign_names
        assert "Campaign@With#Symbols" in budgets.campaign_names
