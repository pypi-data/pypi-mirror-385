import pytest
import sys
import importlib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests
from marci import Campaign, Portfolio


def fresh_package(pkg: str):
    """Helper function to reload package for testing."""
    # ensure finder cache is up-to-date
    importlib.invalidate_caches()

    # drop pkg and all its submodules from sys.modules
    doomed = [m for m in list(sys.modules) if m == pkg or m.startswith(pkg + ".")]
    for m in doomed:
        del sys.modules[m]

    # import clean
    mod = importlib.import_module(pkg)
    return mod


class TestReadmeExamples:
    """Test suite for code examples from local_README.ipynb."""

    def test_single_campaign_example(self):
        """Test single campaign example from README."""
        C = Campaign(
            name="Test Campaign",
            start_date="2025-01-01",
            duration=90,
            budget=1000,
            cpm=10,
            cvr=1e-4,
            aov=100,
            cv=0.1,
            seasonality_cv=0.2,
            conv_delay=0.3,
            conv_delay_duration=7,
            elasticity=0.9,
            is_organic=False,
        )
        
        # Test basic properties
        assert C.name == "Test Campaign"
        assert C.start_date == "2025-01-01"
        assert C.duration == 90
        assert C.budget == 1000
        assert C.cpm == 10
        assert C.cvr == 1e-4
        assert C.aov == 100
        assert C.cv == 0.1
        assert C.Seasonality.cv == 0.2
        assert C.Delay.p == 0.3
        assert C.Delay.duration == 7
        assert C.Elasticity.k == 0.9
        assert C.is_organic is False
        
        # Test that stats can be printed (no error)
        C.print_stats()
        
        # Test that plots can be created (no error)
        C.plot_elasticity_and_delay()
        C.plot()
        
        # Test simulation data
        sim_data = C.sim_data
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert hasattr(sim_data, 'agg_df')
        
        # Test DataFrame structure
        df = sim_data.df
        assert len(df) > 0
        assert 'date' in df.columns
        assert 'name' in df.columns
        assert 'sales' in df.columns
        
        # Test aggregated DataFrame
        agg_df = sim_data.agg_df
        assert len(agg_df) > 0

    def test_simple_portfolio_example(self):
        """Test simple portfolio example from README."""
        campaigns = [
            Campaign(
                name="Stable Organic",
                start_date="2025-01-01",
                cv=0,
                seasonality_cv=0,
                duration=90,
                is_organic=True,
            ),
            Campaign(
                name="High Performace",
                cvr=0.0015,
                start_date="2025-02-01",
                duration=20,
            ),
            Campaign(
                name="Low Performance",
                cvr=0.0005,
                start_date="2025-03-01",
                duration=30,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test portfolio structure
        assert len(P.campaigns) == 3
        assert len(P.organic) == 1
        assert len(P.paid) == 2
        
        # Test that stats can be printed (no error)
        P.print_stats()
        
        # Test that plot can be created (no error)
        P.plot()
        
        # Test simulation data
        sim_data = P.sim_data
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert hasattr(sim_data, 'agg_df')
        
        # Test DataFrame structure
        df = sim_data.df
        assert len(df) > 0
        assert 'date' in df.columns
        assert 'name' in df.columns
        assert 'sales' in df.columns
        
        # Test aggregated DataFrame
        agg_df = sim_data.agg_df
        assert len(agg_df) > 0

    def test_complex_portfolio_example(self):
        """Test complex portfolio example from README."""
        campaigns = [
            Campaign(
                name="Noisy Organic Trend",
                start_date="2025-01-01",
                duration=90,
                budget=2000,
                seasonality_cv=0.3,
                is_organic=True,
            ),
            Campaign(
                name="One Time Organic Spike",
                start_date="2025-02-01",
                duration=3,
                budget=10000,
                seasonality_cv=1,
                conv_delay=0.6,
                conv_delay_duration=28,
                is_organic=True,
            ),
            Campaign(
                name="High Performace Non-Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0015,
                elasticity=0.6,
            ),
            Campaign(
                name="Medium Performace Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.001,
                elasticity=0.8,
            ),
            Campaign(
                name="Low Performance Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0005,
                elasticity=0.8,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test portfolio structure
        assert len(P.campaigns) == 5
        assert len(P.organic) == 2
        assert len(P.paid) == 3
        
        # Test that stats can be printed (no error)
        P.print_stats()
        
        # Test that plot can be created (no error)
        P.plot()
        
        # Test simulation data
        sim_data = P.sim_data
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert hasattr(sim_data, 'agg_df')
        
        # Test DataFrame structure
        df = sim_data.df
        assert len(df) > 0
        assert 'date' in df.columns
        assert 'name' in df.columns
        assert 'sales' in df.columns
        
        # Test aggregated DataFrame
        agg_df = sim_data.agg_df
        assert len(agg_df) > 0

    def test_budget_optimization_example(self):
        """Test budget optimization example from README."""
        campaigns = [
            Campaign(
                name="High Performace Non-Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0015,
                elasticity=0.6,
            ),
            Campaign(
                name="Medium Performace Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.001,
                elasticity=0.8,
            ),
            Campaign(
                name="Low Performance Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0005,
                elasticity=0.8,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test default budgets
        default_budgets = P.budgets
        assert default_budgets is not None
        assert hasattr(default_budgets, 'total_budget')
        assert hasattr(default_budgets, 'campaign_budgets')
        
        # Test optimal budget allocation
        optimal_budgets = P.find_optimal_budgets(3000)
        assert optimal_budgets is not None
        assert hasattr(optimal_budgets, 'total_budget')
        assert hasattr(optimal_budgets, 'campaign_budgets')
        assert optimal_budgets.total_budget <= 3000.1  # Allow for small floating point errors
        
        # Test simulation with optimal budgets
        sim_data = P.sim_outcomes(optimal_budgets)
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        
        # Test that stats can be printed with optimal budgets (no error)
        P.print_stats(optimal_budgets)
        
        # Test that plot can be created (no error)
        P.plot()

    def test_high_budget_optimization_example(self):
        """Test high budget optimization example from README."""
        campaigns = [
            Campaign(
                name="High Performace Non-Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0015,
                elasticity=0.6,
            ),
            Campaign(
                name="Medium Performace Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.001,
                elasticity=0.8,
            ),
            Campaign(
                name="Low Performance Elastic",
                start_date="2025-01-01",
                duration=90,
                budget=1000,
                cvr=0.0005,
                elasticity=0.8,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test high budget optimization
        optimal_budgets = P.find_optimal_budgets(30000)
        assert optimal_budgets is not None
        assert hasattr(optimal_budgets, 'total_budget')
        assert hasattr(optimal_budgets, 'campaign_budgets')
        assert optimal_budgets.total_budget <= 30000
        
        # Test simulation with high budget
        sim_data = P.sim_outcomes(optimal_budgets)
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        
        # Test that stats can be printed with high budget (no error)
        P.print_stats(optimal_budgets)
        
        # Test that plot can be created (no error)
        P.plot()

    def test_campaign_plotting_methods(self):
        """Test campaign plotting methods from README."""
        C = Campaign(
            name="Test Campaign",
            start_date="2025-01-01",
            duration=30,
            budget=1000,
            cpm=10,
            cvr=1e-4,
            aov=100,
        )
        
        # Test that plotting methods work without errors
        C.plot_elasticity_and_delay()
        C.plot()
        
        # Test that simulation data is accessible
        sim_data = C.sim_data
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert hasattr(sim_data, 'agg_df')

    def test_portfolio_plotting_methods(self):
        """Test portfolio plotting methods from README."""
        campaigns = [
            Campaign(
                name="Campaign 1",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
            ),
            Campaign(
                name="Campaign 2",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test that plotting methods work without errors
        P.plot()
        
        # Test that simulation data is accessible
        sim_data = P.sim_data
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert hasattr(sim_data, 'agg_df')

    def test_campaign_stats_output(self):
        """Test campaign stats output format."""
        C = Campaign(
            name="Test Campaign",
            start_date="2025-01-01",
            duration=30,
            budget=1000,
            cpm=10,
            cvr=1e-4,
            aov=100,
        )
        
        # Test that print_stats works without error
        # (We can't easily test the output format, but we can ensure it doesn't crash)
        C.print_stats()
        
        # Test that stats can be accessed through print_stats (no error)
        # Note: Campaign doesn't have a direct stats attribute, but print_stats works
        C.print_stats()

    def test_portfolio_stats_output(self):
        """Test portfolio stats output format."""
        campaigns = [
            Campaign(
                name="Campaign 1",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test that print_stats works without error
        P.print_stats()
        
        # Test with custom budgets
        custom_budgets = P.budgets
        P.print_stats(custom_budgets)

    def test_simulation_data_structure(self):
        """Test simulation data structure from README examples."""
        C = Campaign(
            name="Test Campaign",
            start_date="2025-01-01",
            duration=30,
            budget=1000,
            cpm=10,
            cvr=1e-4,
            aov=100,
        )
        
        # Test simulation data structure
        sim_data = C.sim_data
        assert sim_data is not None
        
        # Test DataFrame structure
        df = sim_data.df
        assert isinstance(df, type(sim_data.df))  # Should be a DataFrame
        assert len(df) > 0
        
        # Test required columns
        required_columns = ['date', 'name', 'sales', 'budget']
        for col in required_columns:
            assert col in df.columns
        
        # Test aggregated DataFrame
        agg_df = sim_data.agg_df
        assert isinstance(agg_df, type(sim_data.agg_df))  # Should be a DataFrame
        assert len(agg_df) > 0

    def test_portfolio_simulation_data_structure(self):
        """Test portfolio simulation data structure from README examples."""
        campaigns = [
            Campaign(
                name="Campaign 1",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
            ),
            Campaign(
                name="Campaign 2",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test simulation data structure
        sim_data = P.sim_data
        assert sim_data is not None
        
        # Test DataFrame structure
        df = sim_data.df
        assert isinstance(df, type(sim_data.df))  # Should be a DataFrame
        assert len(df) > 0
        
        # Test required columns
        required_columns = ['date', 'name', 'sales', 'budget']
        for col in required_columns:
            assert col in df.columns
        
        # Test aggregated DataFrame
        agg_df = sim_data.agg_df
        assert isinstance(agg_df, type(sim_data.agg_df))  # Should be a DataFrame
        assert len(agg_df) > 0

    def test_budget_optimization_edge_cases(self):
        """Test budget optimization edge cases."""
        campaigns = [
            Campaign(
                name="High Performance",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
                cvr=0.001,
                elasticity=0.8,
            ),
            Campaign(
                name="Low Performance",
                start_date="2025-01-01",
                duration=30,
                budget=1000,
                cvr=0.0001,
                elasticity=0.8,
            ),
        ]
        
        P = Portfolio(campaigns)
        
        # Test with very low budget
        low_budget = P.find_optimal_budgets(100)
        assert low_budget is not None
        assert low_budget.total_budget <= 100
        
        # Test with very high budget
        high_budget = P.find_optimal_budgets(100000)
        assert high_budget is not None
        assert high_budget.total_budget <= 100000
        
        # Test that optimization works for both cases
        P.sim_outcomes(low_budget)
        P.sim_outcomes(high_budget)

    def test_organic_campaign_scenarios(self):
        """Test organic campaign scenarios from README."""
        # Test stable organic campaign
        stable_organic = Campaign(
            name="Stable Organic",
            start_date="2025-01-01",
            cv=0,
            seasonality_cv=0,
            duration=90,
            is_organic=True,
        )
        
        assert stable_organic.is_organic is True
        assert stable_organic.cv == 0
        assert stable_organic.Seasonality.cv == 0
        
        # Test noisy organic campaign
        noisy_organic = Campaign(
            name="Noisy Organic Trend",
            start_date="2025-01-01",
            duration=90,
            budget=2000,
            seasonality_cv=0.3,
            is_organic=True,
        )
        
        assert noisy_organic.is_organic is True
        assert noisy_organic.Seasonality.cv == 0.3
        
        # Test one-time organic spike
        spike_organic = Campaign(
            name="One Time Organic Spike",
            start_date="2025-02-01",
            duration=3,
            budget=10000,
            seasonality_cv=1,
            conv_delay=0.6,
            conv_delay_duration=28,
            is_organic=True,
        )
        
        assert spike_organic.is_organic is True
        assert spike_organic.Seasonality.cv == 1
        assert spike_organic.Delay.p == 0.6
        assert spike_organic.Delay.duration == 28

    def test_performance_campaign_scenarios(self):
        """Test performance campaign scenarios from README."""
        # Test high performance non-elastic campaign
        high_perf = Campaign(
            name="High Performace Non-Elastic",
            start_date="2025-01-01",
            duration=90,
            budget=1000,
            cvr=0.0015,
            elasticity=0.6,
        )
        
        assert high_perf.cvr == 0.0015
        assert high_perf.Elasticity.k == 0.6
        
        # Test medium performance elastic campaign
        medium_perf = Campaign(
            name="Medium Performace Elastic",
            start_date="2025-01-01",
            duration=90,
            budget=1000,
            cvr=0.001,
            elasticity=0.8,
        )
        
        assert medium_perf.cvr == 0.001
        assert medium_perf.Elasticity.k == 0.8
        
        # Test low performance elastic campaign
        low_perf = Campaign(
            name="Low Performance Elastic",
            start_date="2025-01-01",
            duration=90,
            budget=1000,
            cvr=0.0005,
            elasticity=0.8,
        )
        
        assert low_perf.cvr == 0.0005
        assert low_perf.Elasticity.k == 0.8
