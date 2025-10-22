import pytest
from marci.utils.plot_utils import get_campaign_colors


class TestGetCampaignColors:
    """Test suite for get_campaign_colors function."""

    def test_get_campaign_colors_empty_list(self):
        """Test get_campaign_colors with empty list."""
        colors = get_campaign_colors([])
        assert colors == {}

    def test_get_campaign_colors_single_campaign(self):
        """Test get_campaign_colors with single campaign."""
        colors = get_campaign_colors(["Campaign A"])
        
        assert len(colors) == 1
        assert "Campaign A" in colors
        assert isinstance(colors["Campaign A"], str)
        assert colors["Campaign A"].startswith("#")

    def test_get_campaign_colors_multiple_campaigns(self):
        """Test get_campaign_colors with multiple campaigns."""
        campaign_names = ["Campaign A", "Campaign B", "Campaign C"]
        colors = get_campaign_colors(campaign_names)
        
        assert len(colors) == 3
        for name in campaign_names:
            assert name in colors
            assert isinstance(colors[name], str)
            assert colors[name].startswith("#")

    def test_get_campaign_colors_unique_colors(self):
        """Test that get_campaign_colors returns unique colors."""
        campaign_names = ["Campaign A", "Campaign B", "Campaign C", "Campaign D"]
        colors = get_campaign_colors(campaign_names)
        
        color_values = list(colors.values())
        assert len(set(color_values)) == len(color_values)  # All colors should be unique

    def test_get_campaign_colors_many_campaigns(self):
        """Test get_campaign_colors with many campaigns."""
        campaign_names = [f"Campaign {i}" for i in range(20)]
        colors = get_campaign_colors(campaign_names)
        
        assert len(colors) == 20
        for name in campaign_names:
            assert name in colors
            assert isinstance(colors[name], str)
            assert colors[name].startswith("#")

    def test_get_campaign_colors_special_characters(self):
        """Test get_campaign_colors with special characters in names."""
        campaign_names = [
            "Campaign-With-Dashes",
            "Campaign_With_Underscores", 
            "Campaign With Spaces",
            "Campaign@With#Symbols"
        ]
        colors = get_campaign_colors(campaign_names)
        
        assert len(colors) == 4
        for name in campaign_names:
            assert name in colors
            assert isinstance(colors[name], str)
            assert colors[name].startswith("#")

    def test_get_campaign_colors_unicode_names(self):
        """Test get_campaign_colors with unicode names."""
        campaign_names = ["Campaign α", "Campaign β", "Campaign γ"]
        colors = get_campaign_colors(campaign_names)
        
        assert len(colors) == 3
        for name in campaign_names:
            assert name in colors
            assert isinstance(colors[name], str)
            assert colors[name].startswith("#")

    def test_get_campaign_colors_duplicate_names(self):
        """Test get_campaign_colors with duplicate names."""
        campaign_names = ["Campaign A", "Campaign B", "Campaign A"]
        colors = get_campaign_colors(campaign_names)
        
        # Should handle duplicates gracefully
        assert len(colors) == 2  # Only unique names
        assert "Campaign A" in colors
        assert "Campaign B" in colors

    def test_get_campaign_colors_consistency(self):
        """Test that get_campaign_colors returns consistent colors."""
        campaign_names = ["Campaign A", "Campaign B", "Campaign C"]
        
        colors1 = get_campaign_colors(campaign_names)
        colors2 = get_campaign_colors(campaign_names)
        
        # Colors should be consistent across calls
        assert colors1 == colors2

    def test_get_campaign_colors_order_independence(self):
        """Test that get_campaign_colors handles different orders."""
        campaign_names1 = ["Campaign A", "Campaign B", "Campaign C"]
        campaign_names2 = ["Campaign C", "Campaign A", "Campaign B"]
        
        colors1 = get_campaign_colors(campaign_names1)
        colors2 = get_campaign_colors(campaign_names2)
        
        # Both should return valid colors for all campaigns
        for name in campaign_names1:
            assert name in colors1
            assert name in colors2
            assert isinstance(colors1[name], str)
            assert isinstance(colors2[name], str)

    def test_get_campaign_colors_hex_format(self):
        """Test that get_campaign_colors returns valid hex colors."""
        campaign_names = ["Campaign A", "Campaign B", "Campaign C"]
        colors = get_campaign_colors(campaign_names)
        
        for color in colors.values():
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format
            # Check that it's a valid hex color
            hex_part = color[1:]  # Remove #
            assert all(c in "0123456789ABCDEFabcdef" for c in hex_part)

    def test_get_campaign_colors_different_sizes(self):
        """Test get_campaign_colors with different list sizes."""
        # Test with 1 campaign
        colors_1 = get_campaign_colors(["Campaign A"])
        assert len(colors_1) == 1
        
        # Test with 2 campaigns
        colors_2 = get_campaign_colors(["Campaign A", "Campaign B"])
        assert len(colors_2) == 2
        
        # Test with 5 campaigns
        colors_5 = get_campaign_colors([f"Campaign {i}" for i in range(5)])
        assert len(colors_5) == 5
        
        # Test with 10 campaigns
        colors_10 = get_campaign_colors([f"Campaign {i}" for i in range(10)])
        assert len(colors_10) == 10

    def test_get_campaign_colors_none_input(self):
        """Test get_campaign_colors with None input."""
        with pytest.raises(TypeError):
            get_campaign_colors(None)

    def test_get_campaign_colors_non_list_input(self):
        """Test get_campaign_colors with non-list input."""
        # The function might handle non-list inputs gracefully
        # Let's test what actually happens
        try:
            result = get_campaign_colors("not a list")
            # If it doesn't raise an error, check that it returns something reasonable
            assert isinstance(result, dict)
        except (TypeError, AttributeError):
            # If it raises an error, that's also acceptable
            pass
        
        try:
            result = get_campaign_colors(123)
            assert isinstance(result, dict)
        except (TypeError, AttributeError):
            pass

    def test_get_campaign_colors_mixed_types(self):
        """Test get_campaign_colors with mixed types in list."""
        campaign_names = ["Campaign A", 123, "Campaign B", None]
        colors = get_campaign_colors(campaign_names)
        
        # Should handle mixed types gracefully
        assert "Campaign A" in colors
        assert "Campaign B" in colors
        # Non-string items should be converted to strings or handled appropriately
        assert len(colors) >= 2

    def test_get_campaign_colors_very_long_names(self):
        """Test get_campaign_colors with very long campaign names."""
        long_name = "A" * 1000  # Very long name
        campaign_names = [long_name, "Short Name"]
        colors = get_campaign_colors(campaign_names)
        
        assert len(colors) == 2
        assert long_name in colors
        assert "Short Name" in colors
        assert isinstance(colors[long_name], str)
        assert isinstance(colors["Short Name"], str)
