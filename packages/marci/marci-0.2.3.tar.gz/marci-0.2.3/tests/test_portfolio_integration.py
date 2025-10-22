import pytest
import numpy as np
from marci import Portfolio, Campaign, Budgets


class TestPortfolioIntegration:
    """Test suite for Portfolio integration scenarios from local tests."""

    def test_portfolio_complex_campaigns(self):
        """Test Portfolio with complex campaign scenarios."""
        campaigns = [
            Campaign(
                name="Organic Low Volatility",
                budget=1000,
                is_organic=True,
            ),
            Campaign(
                name="Organic High Volatility",
                start_date="2025-01-15",
                cv=10,
                budget=100,
                is_organic=True,
            ),
            Campaign(
                name="Organic Peak Event",
                start_date="2025-01-15",
                cv=1,
                seasonality_cv=10,
                duration=3,
                budget=5000,
                is_organic=True,
                conv_delay=0.95,
                conv_delay_duration=28,
            ),
            Campaign(
                name="Google Search",
                cpm=30,
                cvr=5e-4,
                aov=100,
                elasticity=0.9,
                budget=2000,
            ),
            Campaign(
                name="Google Display",
                cpm=10,
                cvr=1e-4,
                aov=80,
                elasticity=0.6,
                budget=500,
            ),
            Campaign(
                name="Meta",
                cpm=10,
                cvr=2e-4,
                aov=80,
                elasticity=0.8,
                budget=1000,
                conv_delay=0.95,
                conv_delay_duration=28,
            ),
            Campaign(
                name="Youtube",
                cpm=9,
                cvr=1e-4,
                aov=90,
                elasticity=0.7,
                budget=1000,
            ),
            Campaign(
                name="TikTok",
                cpm=5,
                cvr=1e-4,
                aov=60,
                elasticity=0.7,
                budget=500,
            ),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test basic portfolio functionality
        assert len(portfolio.campaigns) == 8
        assert len(portfolio.organic) == 3
        assert len(portfolio.paid) == 5
        
        # Test that we can access campaigns by name
        assert "Organic Low Volatility" in portfolio.campaigns
        assert "Google Search" in portfolio.campaigns
        assert "TikTok" in portfolio.campaigns

    def test_portfolio_optimal_budget_allocation(self):
        """Test Portfolio optimal budget allocation."""
        campaigns = [
            Campaign(
                name="Organic",
                cv=0.1,
                seasonality_cv=0.3,
                budget=5000,
                is_organic=True,
                elasticity=0.9,
                duration=30,
                conv_delay=0.3,
            ),
            Campaign(
                name="Google Search",
                cpm=30,
                cvr=5e-4,
                aov=100,
                cv=0.1,
                seasonality_cv=0.3,
                elasticity=0.9,
                budget=500,
                base=2000,
                duration=30,
                conv_delay=0.3,
            ),
            Campaign(
                name="Google Display",
                cpm=10,
                cvr=1e-4,
                aov=80,
                cv=0.1,
                seasonality_cv=0.3,
                elasticity=0.6,
                budget=2000,
                base=500,
                duration=30,
                conv_delay=0.3,
            ),
            Campaign(
                name="Meta",
                cpm=10,
                cvr=2e-4,
                aov=80,
                cv=0.1,
                seasonality_cv=0.3,
                elasticity=0.8,
                budget=1000,
                duration=30,
                conv_delay=0.3,
            ),
            Campaign(
                name="Youtube",
                cpm=9,
                cvr=1e-4,
                aov=90,
                cv=0.1,
                seasonality_cv=0.3,
                elasticity=0.7,
                budget=1000,
                duration=30,
                conv_delay=0.3,
            ),
            Campaign(
                name="TikTok",
                cpm=5,
                cvr=1e-4,
                aov=60,
                cv=0.1,
                seasonality_cv=0.3,
                elasticity=0.7,
                budget=500,
                duration=30,
                conv_delay=0.3,
            ),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test optimal budget allocation
        optimal_budgets = portfolio.find_optimal_budgets(5000)
        
        assert isinstance(optimal_budgets, Budgets)
        assert optimal_budgets.total_budget <= 5000.1  # Allow for small floating point errors
        
        # Test that all paid campaigns have budgets allocated
        for campaign in portfolio.paid:
            campaign_name = campaign.name
            assert campaign_name in optimal_budgets

    def test_portfolio_custom_budget_scenarios(self):
        """Test Portfolio with custom budget scenarios."""
        campaigns = [
            Campaign(name="Google Search", cpm=30, cvr=5e-4, aov=100, budget=2000),
            Campaign(name="Meta", cpm=10, cvr=2e-4, aov=80, budget=1000),
            Campaign(name="Google Display", cpm=10, cvr=1e-4, aov=80, budget=500),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test custom budget allocation
        custom_budgets = Budgets(
            "Custom Budget",
            {
                "Google Search": 2000,
                "Meta": 1000,
                "Google Display": 10000,
            }
        )
        
        # Test that portfolio can handle custom budgets
        result = portfolio.sim_outcomes(custom_budgets)
        assert result is not None
        assert hasattr(result, 'df')

    def test_portfolio_mixed_organic_paid_campaigns(self):
        """Test Portfolio with mixed organic and paid campaigns."""
        campaigns = [
            Campaign(
                name="Organic Campaign",
                budget=1000,
                is_organic=True,
                elasticity=0.9,
                duration=30,
            ),
            Campaign(
                name="Paid Campaign 1",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                elasticity=0.8,
                duration=30,
            ),
            Campaign(
                name="Paid Campaign 2",
                cpm=15,
                cvr=2e-4,
                aov=80,
                budget=1500,
                elasticity=0.7,
                duration=30,
            ),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test portfolio structure
        assert len(portfolio.campaigns) == 3
        assert len(portfolio.organic) == 1
        assert len(portfolio.paid) == 2
        
        # Test that organic campaigns are identified correctly
        assert any(c.is_organic for c in portfolio.organic)
        assert not any(c.is_organic for c in portfolio.paid)

    def test_portfolio_high_volatility_campaigns(self):
        """Test Portfolio with high volatility campaigns."""
        campaigns = [
            Campaign(
                name="High Volatility Organic",
                budget=100,
                is_organic=True,
                cv=10,  # High volatility
                seasonality_cv=5,  # High seasonality
            ),
            Campaign(
                name="High Volatility Paid",
                cpm=30,
                cvr=5e-4,
                aov=100,
                budget=2000,
                cv=5,  # High volatility
                seasonality_cv=3,  # High seasonality
            ),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test that high volatility campaigns are handled
        assert len(portfolio.campaigns) == 2
        assert portfolio.campaigns["High Volatility Organic"].cv == 10
        assert portfolio.campaigns["High Volatility Paid"].cv == 5

    def test_portfolio_peak_event_campaigns(self):
        """Test Portfolio with peak event campaigns."""
        campaigns = [
            Campaign(
                name="Peak Event Campaign",
                start_date="2025-01-15",
                cv=1,
                seasonality_cv=10,
                duration=3,
                budget=5000,
                is_organic=True,
                conv_delay=0.95,
                conv_delay_duration=28,
            ),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test peak event campaign characteristics
        campaign = portfolio.campaigns["Peak Event Campaign"]
        assert campaign.duration == 3
        # Note: seasonality_cv is accessed through the Seasonality object
        assert campaign.Seasonality.cv == 10
        # Note: conv_delay is accessed through the Delay object
        assert campaign.Delay.p == 0.95
        assert campaign.Delay.duration == 28

    def test_portfolio_different_platforms(self):
        """Test Portfolio with different advertising platforms."""
        campaigns = [
            Campaign(name="Google Search", cpm=30, cvr=5e-4, aov=100, budget=2000),
            Campaign(name="Google Display", cpm=10, cvr=1e-4, aov=80, budget=500),
            Campaign(name="Meta", cpm=10, cvr=2e-4, aov=80, budget=1000),
            Campaign(name="Youtube", cpm=9, cvr=1e-4, aov=90, budget=1000),
            Campaign(name="TikTok", cpm=5, cvr=1e-4, aov=60, budget=500),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test that all platforms are represented
        platform_names = ["Google Search", "Google Display", "Meta", "Youtube", "TikTok"]
        for name in platform_names:
            assert name in portfolio.campaigns
        
        # Test platform-specific characteristics
        assert portfolio.campaigns["Google Search"].cpm == 30
        assert portfolio.campaigns["TikTok"].cpm == 5
        assert portfolio.campaigns["Meta"].cvr == 2e-4

    def test_portfolio_budget_optimization_scenarios(self):
        """Test Portfolio budget optimization with different scenarios."""
        campaigns = [
            Campaign(name="Campaign A", cpm=20, cvr=3e-4, aov=100, budget=1000, elasticity=0.8),
            Campaign(name="Campaign B", cpm=15, cvr=2e-4, aov=80, budget=1500, elasticity=0.6),
            Campaign(name="Campaign C", cpm=25, cvr=4e-4, aov=120, budget=800, elasticity=0.9),
        ]
        
        portfolio = Portfolio(campaigns)
        
        # Test different budget scenarios
        budget_scenarios = [1000, 5000, 10000, 20000]
        
        for total_budget in budget_scenarios:
            optimal_budgets = portfolio.find_optimal_budgets(total_budget)
            
            assert isinstance(optimal_budgets, Budgets)
            assert optimal_budgets.total_budget <= total_budget
            
            # Test that all paid campaigns have budgets
            for campaign in portfolio.paid:
                campaign_name = campaign.name
                assert campaign_name in optimal_budgets
                assert optimal_budgets[campaign_name] >= 0
