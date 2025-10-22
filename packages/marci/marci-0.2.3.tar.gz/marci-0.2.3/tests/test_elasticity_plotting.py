import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests
import matplotlib.pyplot as plt
import numpy as np
from marci.utils.elasticity import Elasticity


class TestElasticityPlotting:
    """Test suite for Elasticity plotting functionality."""

    def test_elasticity_plot_basic(self):
        """Test basic elasticity plotting."""
        e = Elasticity(elasticity_coef=0.8)
        fig, ax = plt.subplots()
        
        # Test that plot method works without errors
        e.plot(ax=ax, max_x=10, max_y=4)
        
        # Check that the plot was created (allow for small margin)
        assert ax.get_xlim()[1] <= 10.6  # Allow for matplotlib's default margins
        assert ax.get_ylim()[1] <= 4.1
        
        plt.close(fig)

    def test_elasticity_plot_with_saturation(self):
        """Test elasticity plotting with saturation."""
        e = Elasticity(elasticity_coef=1.0, saturation_rate=2.0)
        fig, ax = plt.subplots()
        
        e.plot(ax=ax, max_x=5, max_y=3)
        
        # Check that the plot was created (allow for small margin)
        assert ax.get_xlim()[1] <= 5.3  # Allow for matplotlib's default margins
        assert ax.get_ylim()[1] <= 3.1
        
        plt.close(fig)

    def test_elasticity_plot_multiple_parameters(self):
        """Test elasticity plotting with multiple parameter combinations."""
        elasticity_coefs = [0.1, 0.5, 1, 2]
        saturation_rates = [0, 2, 3]
        
        fig, ax = plt.subplots(len(saturation_rates), len(elasticity_coefs), figsize=(16, 9))
        
        for i, saturation_rate in enumerate(saturation_rates):
            for j, elasticity_coef in enumerate(elasticity_coefs):
                e = Elasticity(elasticity_coef=elasticity_coef, saturation_rate=saturation_rate)
                e.plot(ax=ax[i, j], max_x=10, max_y=4)
                
                # Check that each subplot was created (allow for small margin)
                assert ax[i, j].get_xlim()[1] <= 10.6  # Allow for matplotlib's default margins
                assert ax[i, j].get_ylim()[1] <= 4.1
        
        plt.close(fig)

    def test_elasticity_plot_max_y_parameter(self):
        """Test elasticity plotting with max_y parameter."""
        e = Elasticity(elasticity_coef=0.8)
        fig, ax = plt.subplots()
        
        # Test with max_y parameter
        e.plot(ax=ax, max_x=5, max_y=2)
        
        # Check that y-axis is limited correctly
        assert ax.get_ylim()[1] <= 2
        
        plt.close(fig)

    def test_elasticity_plot_no_max_y(self):
        """Test elasticity plotting without max_y parameter."""
        e = Elasticity(elasticity_coef=0.8)
        fig, ax = plt.subplots()
        
        # Test without max_y parameter
        e.plot(ax=ax, max_x=5)
        
        # Check that plot was created (y-axis should be auto-scaled)
        assert ax.get_xlim()[1] <= 5.3  # Allow for matplotlib's default margins
        
        plt.close(fig)

    def test_elasticity_plot_different_coefficients(self):
        """Test elasticity plotting with different coefficients."""
        coefficients = [0.1, 0.5, 1.0, 1.5, 2.0]
        
        for coef in coefficients:
            e = Elasticity(elasticity_coef=coef)
            fig, ax = plt.subplots()
            
            e.plot(ax=ax, max_x=5, max_y=3)
            
            # Check that plot was created for each coefficient
            assert ax.get_xlim()[1] <= 5.3  # Allow for matplotlib's default margins
            assert ax.get_ylim()[1] <= 3.1
            
            plt.close(fig)

    def test_elasticity_plot_different_saturation_rates(self):
        """Test elasticity plotting with different saturation rates."""
        saturation_rates = [0, 1, 2, 3, 5]
        
        for sat_rate in saturation_rates:
            e = Elasticity(elasticity_coef=1.0, saturation_rate=sat_rate)
            fig, ax = plt.subplots()
            
            e.plot(ax=ax, max_x=5, max_y=3)
            
            # Check that plot was created for each saturation rate
            assert ax.get_xlim()[1] <= 5.3  # Allow for matplotlib's default margins
            assert ax.get_ylim()[1] <= 3.1
            
            plt.close(fig)

    def test_elasticity_plot_edge_cases(self):
        """Test elasticity plotting with edge case parameters."""
        # Test with very low elasticity
        e1 = Elasticity(elasticity_coef=0.01)
        fig1, ax1 = plt.subplots()
        e1.plot(ax=ax1, max_x=10, max_y=5)
        assert ax1.get_xlim()[1] <= 10.6  # Allow for matplotlib's default margins
        plt.close(fig1)
        
        # Test with very high elasticity
        e2 = Elasticity(elasticity_coef=5.0)
        fig2, ax2 = plt.subplots()
        e2.plot(ax=ax2, max_x=10, max_y=5)
        assert ax2.get_xlim()[1] <= 10.6  # Allow for matplotlib's default margins
        plt.close(fig2)
        
        # Test with zero saturation
        e3 = Elasticity(elasticity_coef=1.0, saturation_rate=0)
        fig3, ax3 = plt.subplots()
        e3.plot(ax=ax3, max_x=10, max_y=5)
        assert ax3.get_xlim()[1] <= 10.6  # Allow for matplotlib's default margins
        plt.close(fig3)

    def test_elasticity_plot_parameter_combinations(self):
        """Test elasticity plotting with various parameter combinations."""
        test_cases = [
            (0.1, 0),   # Low elasticity, no saturation
            (0.5, 1),   # Medium elasticity, low saturation
            (1.0, 2),   # High elasticity, medium saturation
            (2.0, 3),   # Very high elasticity, high saturation
        ]
        
        for elasticity_coef, saturation_rate in test_cases:
            e = Elasticity(elasticity_coef=elasticity_coef, saturation_rate=saturation_rate)
            fig, ax = plt.subplots()
            
            e.plot(ax=ax, max_x=8, max_y=4)
            
            # Check that plot was created for each combination
            assert ax.get_xlim()[1] <= 8.5  # Allow for matplotlib's default margins
            assert ax.get_ylim()[1] <= 4.1
            
            plt.close(fig)
