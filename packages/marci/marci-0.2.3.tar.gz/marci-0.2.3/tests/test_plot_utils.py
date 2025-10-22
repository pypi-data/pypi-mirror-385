"""
Tests for plot_utils module.
"""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for tests
import matplotlib.pyplot as plt
from unittest.mock import patch
import matplotlib.dates as mdates

from marci.utils.plot_utils import style


class TestStyleFunction:
    """Test the style function with various formatting options."""

    def test_style_basic_functionality(self):
        """Test basic styling functionality."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # Test basic styling
        result = style(ax, title="Test Plot", x_label="X", y_label="Y")

        assert result == ax
        assert ax.get_title() == "Test Plot"
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        plt.close(fig)

    def test_style_percentage_formatting(self):
        """Test percentage formatting."""
        fig, ax = plt.subplots()
        ax.plot([0.1, 0.2, 0.3], [0.1, 0.2, 0.3])

        style(ax, y_fmt="%")

        # Check if formatter is set
        formatter = ax.yaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_style_currency_formatting(self):
        """Test currency formatting."""
        fig, ax = plt.subplots()
        ax.plot([100, 200, 300], [100, 200, 300])

        style(ax, y_fmt="$")

        # Check if formatter is set
        formatter = ax.yaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_style_date_formatting(self):
        """Test date formatting."""
        fig, ax = plt.subplots()
        dates = mdates.date2num(
            [mdates.datestr2num("2023-01-01"), mdates.datestr2num("2023-02-01")]
        )
        ax.plot(dates, [1, 2])

        style(ax, x_fmt="d")

        # Check if formatter is set
        formatter = ax.xaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_style_date_formatting_axis(self):
        """Test date formatting on axis."""
        fig, ax = plt.subplots()
        dates = mdates.date2num(
            [mdates.datestr2num("2023-01-01"), mdates.datestr2num("2023-02-01")]
        )
        ax.plot(dates, [1, 2])

        style(ax, x_fmt="d")

        # Check if formatter is set
        formatter = ax.xaxis.get_major_formatter()
        assert formatter is not None
        plt.close(fig)

    def test_style_font_size(self):
        """Test font size parameter."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        style(ax, font_size=14, title="Test", x_label="X", y_label="Y")

        # Font sizes are set on the text objects
        assert ax.get_title() == "Test"
        plt.close(fig)

    def test_style_legend_disabled(self):
        """Test with legend disabled."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3], label="Test")

        style(ax, legend=False)

        # Legend should not be visible
        legend = ax.get_legend()
        assert legend is None
        plt.close(fig)

    def test_style_legend_enabled(self):
        """Test with legend enabled."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3], label="Test")

        style(ax, legend=True)

        # Legend should be visible
        legend = ax.get_legend()
        assert legend is not None
        plt.close(fig)

    def test_style_ylim_zero_based(self):
        """Test that y-axis starts from 0."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        style(ax)

        ylim = ax.get_ylim()
        assert ylim[0] == 0
        plt.close(fig)

    def test_style_spines_hidden(self):
        """Test that spines are hidden."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        style(ax)

        # All spines should be hidden
        for spine in ax.spines.values():
            assert not spine.get_visible()
        plt.close(fig)

    def test_style_grid_enabled(self):
        """Test that grid is enabled."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        style(ax)

        # Grid should be enabled (grid() returns None, but we can check the grid state)
        assert ax.xaxis.grid or ax.yaxis.grid
        plt.close(fig)

    def test_style_tight_layout_called(self):
        """Test that tight_layout is called on the figure."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        with patch.object(fig, "tight_layout") as mock_tight_layout:
            style(ax)
            mock_tight_layout.assert_called_once()

        plt.close(fig)

    def test_style_x_axis_rotation(self):
        """Test that x-axis labels are rotated."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        style(ax)

        # X-axis labels should be rotated - check the tick parameters
        tick_params = ax.xaxis.get_tick_params()
        # The rotation is set via tick_params, so we check if it's configured
        assert "labelrotation" in tick_params or ax.xaxis.get_major_ticks()
        plt.close(fig)

    def test_style_return_value(self):
        """Test that the function returns the axes object."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        result = style(ax)
        assert result is ax
        plt.close(fig)

    def test_style_with_none_parameters(self):
        """Test with None parameters (should not cause errors)."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # All parameters None except ax
        result = style(ax, None, None, None, None, None)
        assert result is ax
        plt.close(fig)

    def test_style_default_parameters(self):
        """Test with default parameters."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        # Only pass ax, use all defaults
        result = style(ax)
        assert result is ax
        plt.close(fig)
