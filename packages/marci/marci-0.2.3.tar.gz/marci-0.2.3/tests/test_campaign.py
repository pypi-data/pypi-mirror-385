import numpy as np
import pandas as pd
from marci import Campaign


def test_campaign_basic_initialization():
    c = Campaign()
    assert c.name == "Campaign"
    assert c.cpm == 10
    assert c.cvr == 1e-3  # Updated to match new default
    assert c.aov == 10    # Updated to match new default
    assert c.cv == 0.1
    assert c.budget == 1000  # Changed from base_budget to budget


def test_campaign_custom_parameters():
    c = Campaign(
        name="Test Campaign",
        start_date="2025-01-01",
        duration=30,
        budget=2000,
        cpm=15,
        cvr=2e-4,
        aov=150,
        elasticity=0.3,
    )
    assert c.name == "Test Campaign"
    assert c.cpm == 15
    assert c.cvr == 2e-4
    assert c.aov == 150
    assert c.budget == 2000


def test_campaign_expected_roas():
    c = Campaign(start_date="2025-01-01", duration=30, budget=1000, cpm=10, cvr=1e-4, aov=100, elasticity=0.2)

    # Test with default spend
    roas = c.exp_roas()
    assert roas > 0


def test_campaign_external_roas():
    c = Campaign(start_date="2025-01-01", duration=30, budget=1000, cpm=1, cvr=1e-4, aov=100, is_organic=True)

    # For organic campaigns, ROAS should be calculated normally
    roas = c.exp_roas()
    # For organic campaigns, we expect a positive ROAS
    assert roas > 0


def test_campaign_expected_sales():
    c = Campaign(start_date="2025-01-01", duration=30, budget=1000, cpm=10, cvr=1e-4, aov=100, elasticity=0.2)

    sales = c.exp_tot_sales()
    assert sales > 0


def test_campaign_sim_outcomes():
    c = Campaign()  # Campaign doesn't take seed parameter

    # Test simulation without plot
    sim_data = c.sim_outcomes()
    df = sim_data.df

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "budget" in df.columns
    assert "imps" in df.columns
    assert "convs" in df.columns
    assert "sales" in df.columns


def test_campaign_simulated_vs_expected_roas():
    """Test that simulated ROAS is reasonably close to expected ROAS."""
    c = Campaign(
        start_date="2025-01-01",
        duration=30,
        budget=1000,
        cpm=15,
        cvr=2e-4,
        aov=120,
        elasticity=0.3,
        cv=0.05,  # Lower CV for more stable results
    )

    # Calculate expected ROAS
    expected_roas = c.exp_roas()

    # Run simulation multiple times and average
    n_sims = 10
    simulated_roas_list = []

    for _ in range(n_sims):
        sim_data = c.sim_outcomes()
        df = sim_data.df

        # Calculate simulated ROAS: total sales / total spend
        total_sales = df["sales"].sum()
        total_spend = df["budget"].sum()
        simulated_roas = total_sales / total_spend if total_spend > 0 else 0
        simulated_roas_list.append(simulated_roas)

    # Average simulated ROAS
    avg_simulated_roas = np.mean(simulated_roas_list)

    # Check that simulated ROAS is within reasonable range of expected
    # Allow for some variance due to randomness and attribution delays
    roas_ratio = avg_simulated_roas / expected_roas

    # Should be within 50% of expected (reasonable for simulation variance)
    assert 0.5 <= roas_ratio <= 2.0, (
        f"Simulated ROAS {avg_simulated_roas:.3f} not close to expected {expected_roas:.3f}"
    )

    # Both should be positive
    assert expected_roas > 0
    assert avg_simulated_roas > 0
