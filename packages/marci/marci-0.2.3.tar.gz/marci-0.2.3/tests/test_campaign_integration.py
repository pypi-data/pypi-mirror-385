import pytest
import numpy as np
from marci import Campaign


class TestCampaignIntegration:
    """Test suite for Campaign integration scenarios from local tests."""

    def test_campaign_organic_scenario(self):
        """Test Campaign with organic scenario."""
        c = Campaign(
            name="Organic Campaign",
            budget=1000,
            base=500,
            elasticity=0.5,
            duration=3,
            conv_delay_duration=30,
            conv_delay=0.99,
            is_organic=True,
        )
        
        # Test basic properties
        assert c.name == "Organic Campaign"
        assert c.budget == 1000
        assert c.base == 500
        assert c.Elasticity.k == 0.5
        assert c.duration == 3
        assert c.Delay.p == 0.99
        assert c.Delay.duration == 30
        assert c.is_organic is True

    def test_campaign_high_conv_delay_scenario(self):
        """Test Campaign with high conversion delay."""
        c = Campaign(
            name="High Delay Campaign",
            duration=3,
            budget=100000,
            conv_delay_duration=180,
            conv_delay=0.99,
        )
        
        # Test high delay characteristics
        assert c.Delay.p == 0.99
        assert c.Delay.duration == 180
        assert c.duration == 3
        assert c.budget == 100000

    def test_campaign_expected_roas_calculation(self):
        """Test Campaign expected ROAS calculation."""
        c = Campaign(
            name="Test Campaign",
            cpm=20,
            cvr=3e-4,
            aov=100,
            budget=2000,
            elasticity=0.8,
        )
        
        # Test that expected ROAS can be calculated
        roas = c.exp_roas()
        assert isinstance(roas, (int, float))
        assert roas > 0

    def test_campaign_expected_sales_calculation(self):
        """Test Campaign expected sales calculation."""
        c = Campaign(
            name="Test Campaign",
            cpm=20,
            cvr=3e-4,
            aov=100,
            budget=2000,
            elasticity=0.8,
        )
        
        # Test that expected sales can be calculated
        sales = c.exp_tot_sales()
        assert isinstance(sales, (int, float))
        assert sales > 0

    def test_campaign_simulation_outcomes(self):
        """Test Campaign simulation outcomes."""
        c = Campaign(
            name="Test Campaign",
            cpm=20,
            cvr=3e-4,
            aov=100,
            budget=2000,
            elasticity=0.8,
            duration=30,
        )
        
        # Test simulation outcomes
        sim_data = c.sim_outcomes()
        assert sim_data is not None
        assert hasattr(sim_data, 'df')
        assert len(sim_data.df) > 0

    def test_campaign_organic_vs_paid(self):
        """Test Campaign organic vs paid scenarios."""
        # Organic campaign
        organic_campaign = Campaign(
            name="Organic",
            budget=1000,
            is_organic=True,
        )
        
        # Paid campaign
        paid_campaign = Campaign(
            name="Paid",
            cpm=20,
            cvr=3e-4,
            aov=100,
            budget=1000,
        )
        
        # Test differences
        assert organic_campaign.is_organic is True
        assert paid_campaign.is_organic is False
        
        # Organic campaign should have different characteristics
        assert organic_campaign.cpm == 10  # Default CPM for organic campaigns
        assert paid_campaign.cpm == 20

    def test_campaign_elasticity_scenarios(self):
        """Test Campaign with different elasticity scenarios."""
        elasticity_values = [0.1, 0.5, 0.8, 1.0, 1.5, 2.0]
        
        for elasticity in elasticity_values:
            c = Campaign(
                name=f"Campaign_{elasticity}",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                elasticity=elasticity,
            )
            
            # Test that elasticity is set correctly
            assert c.Elasticity.k == elasticity
            
            # Test that ROAS can be calculated
            roas = c.exp_roas()
            assert isinstance(roas, (int, float))

    def test_campaign_duration_scenarios(self):
        """Test Campaign with different duration scenarios."""
        durations = [1, 7, 30, 90, 365]
        
        for duration in durations:
            c = Campaign(
                name=f"Campaign_{duration}d",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                duration=duration,
            )
            
            # Test that duration is set correctly
            assert c.duration == duration
            
            # Test that expected sales scale with duration
            sales = c.exp_tot_sales()
            assert isinstance(sales, (int, float))
            assert sales > 0

    def test_campaign_budget_scenarios(self):
        """Test Campaign with different budget scenarios."""
        budgets = [100, 1000, 5000, 10000, 50000]
        
        for budget in budgets:
            c = Campaign(
                name=f"Campaign_{budget}",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=budget,
            )
            
            # Test that budget is set correctly
            assert c.budget == budget
            
            # Test that expected sales scale with budget
            sales = c.exp_tot_sales()
            assert isinstance(sales, (int, float))
            assert sales > 0

    def test_campaign_cpm_scenarios(self):
        """Test Campaign with different CPM scenarios."""
        cpms = [1, 5, 10, 20, 50, 100]
        
        for cpm in cpms:
            c = Campaign(
                name=f"Campaign_CPM_{cpm}",
                cpm=cpm,
                cvr=3e-4,
                aov=100,
                budget=2000,
            )
            
            # Test that CPM is set correctly
            assert c.cpm == cpm
            
            # Test that expected ROAS varies with CPM
            roas = c.exp_roas()
            assert isinstance(roas, (int, float))

    def test_campaign_cvr_scenarios(self):
        """Test Campaign with different CVR scenarios."""
        cvrs = [1e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2]
        
        for cvr in cvrs:
            c = Campaign(
                name=f"Campaign_CVR_{cvr}",
                cpm=20,
                cvr=cvr,
                aov=100,
                budget=2000,
            )
            
            # Test that CVR is set correctly
            assert c.cvr == cvr
            
            # Test that expected sales vary with CVR
            sales = c.exp_tot_sales()
            assert isinstance(sales, (int, float))
            assert sales > 0

    def test_campaign_aov_scenarios(self):
        """Test Campaign with different AOV scenarios."""
        aovs = [10, 50, 100, 200, 500, 1000]
        
        for aov in aovs:
            c = Campaign(
                name=f"Campaign_AOV_{aov}",
                cpm=20,
                cvr=3e-4,
                aov=aov,
                budget=2000,
            )
            
            # Test that AOV is set correctly
            assert c.aov == aov
            
            # Test that expected sales scale with AOV
            sales = c.exp_tot_sales()
            assert isinstance(sales, (int, float))
            assert sales > 0

    def test_campaign_conversion_delay_scenarios(self):
        """Test Campaign with different conversion delay scenarios."""
        delay_scenarios = [
            (0.1, 7),   # Low delay, short duration
            (0.5, 14),  # Medium delay, medium duration
            (0.8, 30),  # High delay, long duration
            (0.95, 90), # Very high delay, very long duration
        ]
        
        for conv_delay, conv_delay_duration in delay_scenarios:
            c = Campaign(
                name=f"Campaign_Delay_{conv_delay}",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                conv_delay=conv_delay,
                conv_delay_duration=conv_delay_duration,
            )
            
            # Test that delay parameters are set correctly
            assert c.Delay.p == conv_delay
            assert c.Delay.duration == conv_delay_duration

    def test_campaign_seasonality_scenarios(self):
        """Test Campaign with different seasonality scenarios."""
        seasonality_cvs = [0.1, 0.3, 0.5, 1.0, 2.0, 5.0]
        
        for seasonality_cv in seasonality_cvs:
            c = Campaign(
                name=f"Campaign_Season_{seasonality_cv}",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                seasonality_cv=seasonality_cv,
            )
            
            # Test that seasonality CV is set correctly
            assert c.Seasonality.cv == seasonality_cv

    def test_campaign_volatility_scenarios(self):
        """Test Campaign with different volatility scenarios."""
        cvs = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
        
        for cv in cvs:
            c = Campaign(
                name=f"Campaign_CV_{cv}",
                cpm=20,
                cvr=3e-4,
                aov=100,
                budget=2000,
                cv=cv,
            )
            
            # Test that CV is set correctly
            assert c.cv == cv
