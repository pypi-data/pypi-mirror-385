from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
from .simulated_data import SimulatedData
from .utils.performance_stats import PerformanceStats

from .utils.conversion_delay import Conversion_Delay
from .utils.elasticity import Elasticity
from .utils.distributions import (
    Lognormal,
    Beta,
    safe_poisson,
    safe_binomial,
)
from .utils.seasonality import Seasonality


class Campaign:
    def __init__(
        self,
        name: str = "Campaign",
        start_date: str = "2025-01-01",
        duration: int = 90,
        budget: float = 1000,
        cpm: float = 10,
        cvr: float = 1e-3,
        aov: float = 10,
        cv: float = 0.1,
        seasonality_cv: float = 0.2,
        conv_delay: float = 0.3,
        conv_delay_duration: int = 7,
        elasticity: float = 0.8,
        base: float = None,
        is_organic: bool = False,
    ):
        if base is None and budget is None:
            raise ValueError("Either base or budget must be provided.")
        self.name = name
        self.start_date = start_date
        self.duration = duration
        self.budget = budget if budget is not None else base
        self.cpm = cpm
        self.cvr = cvr
        self.aov = aov
        self.cv = cv
        self.Seasonality = Seasonality(cv=seasonality_cv)
        self.Delay = Conversion_Delay(p=conv_delay, duration=conv_delay_duration)
        self.Elasticity = Elasticity(elasticity_coef=elasticity)
        self.base = base if base is not None else budget
        self.is_organic = is_organic
        self._Sim_Data = None
        self._Sim_Stats = None

        self.CPM = Lognormal(
            mean=self.cpm * (1 + cv**2), cv=cv, name=f"{self.name}_CPM"
        )
        self.CVR = Beta(mean=self.cvr, cv=cv, name=f"{self.name}_CVR")
        self.AOV = Lognormal(mean=self.aov, cv=cv, name=f"{self.name}_AOV")

    @property
    def sim_data(self):
        if self._Sim_Data is None:
            self.sim_outcomes()
        return self._Sim_Data

    def __repr__(self):
        return f"Campaign({self.name!r}, budget=${self.budget:,.0f}, duration={self.duration}, exp_roas={self.exp_roas():.0%}, cv={self.cv:.0%})"

    def exp_tot_budget(self, budget: float = None, duration: int = None):
        if budget is None:
            budget = self.budget
        if duration is None:
            duration = self.duration
        return self.budget * self.duration

    def exp_roas(self, budget: float = None):
        if budget is None:
            budget = self.budget
        elasticity = self.Elasticity.roas(budget / self.base)
        return 1000 * self.cvr * self.aov / self.cpm * elasticity

    def exp_daily_sales(self, budget: float = None):
        if budget is None:
            budget = self.budget
        return self.exp_roas(budget) * budget

    def exp_tot_sales(self, budget: float = None, duration: int = None):
        if budget is None:
            budget = self.budget
        if duration is None:
            duration = self.duration
        return self.exp_daily_sales(budget) * duration

    # ---------------------------------------- PERFORMANCE STATS ----------------------------------------
    def exp_stats(self, budget: float = None, duration: int = None):
        if budget is None:
            budget = self.budget
        if duration is None:
            duration = self.duration
        organic_sales = self.exp_tot_sales(budget, duration) if self.is_organic else 0
        paid_sales = 0 if self.is_organic else self.exp_tot_sales(budget, duration)
        paid_budget = 0 if self.is_organic else budget * duration
        perf_stats = PerformanceStats(
            self.name,
            "Expected",
            organic_sales=organic_sales,
            paid_sales=paid_sales,
            paid_budget=paid_budget,
        )
        return perf_stats

    def sim_stats(self, budget: float = None, duration: int = None):
        if budget is None and duration is None:
            return self.sim_data._Sim_Stats
        if budget is None:
            budget = self.budget
        if duration is None:
            duration = self.duration
        self.sim_outcomes(budget, duration)
        return self.sim_data._Sim_Stats

    def print_stats(self, budget: float = None, duration: int = None):
        stats = PerformanceStats.from_list(
            self.name,
            [self.exp_stats(budget, duration), self.sim_stats(budget, duration)],
        )
        print(stats)

    # ---------------------------------------- SIMULATION ----------------------------------------
    def sim_outcomes(
        self,
        budget: float = None,
        start_date: str = None,
        duration: int = None,
        cv: float = None,
        verbose: bool = False,
        plot: bool = False,
    ):
        if start_date is None:
            start_date = self.start_date
        if duration is None:
            duration = self.duration
        if budget is None:
            budget = self.budget
        if cv is None:
            cv = self.cv
        print(f"Simulating {self}")
        date_range = pd.date_range(start=start_date, periods=duration, name="date")
        df = pd.DataFrame(index=date_range)
        df["base"] = self.base
        df["seasonality"] = self.Seasonality.values(date_range)

        if budget == 0:
            df["budget"] = 0
        else:
            Budget = Lognormal(mean=budget, cv=cv, name=f"{self.name}_Budget")
            df["budget"] = Budget.generate(duration) * df["seasonality"]
        df["elastic_budget"] = df["budget"] / self.base
        elastic_roas = self.Elasticity.roas(df["elastic_budget"])
        df["elastic_returns"] = self.Elasticity.total_return(df["elastic_budget"])
        elasticity = elastic_roas ** (1 / 2)

        df["imps"] = safe_poisson(
            1000 * df["budget"] / self.CPM.generate(duration) * elasticity
        )
        df["raw_convs"] = safe_binomial(
            df["imps"], self.CVR.generate(duration) * elasticity
        )

        attr_convs = self.Delay.delay(df["raw_convs"])
        df = df.join(attr_convs, how="outer")
        df["convs"] = df["attr_convs"].fillna(0)
        df["aov"] = self.AOV.generate(len(df))
        df["sales"] = df["convs"] * df["aov"]

        df["date"] = df.index
        df["name"] = self.name
        df["is_organic"] = self.is_organic

        self._Sim_Data = SimulatedData(df.reset_index(drop=True), self.name)
        self._Sim_Stats = self._Sim_Data._Sim_Stats
        if verbose:
            self.print()

        if plot:
            self.plot()

        return self._Sim_Data

    def plot(self):
        self.sim_data.plot(include_organic=True)
        plt.show()

    def plot_elasticity_and_delay(self, max_x: float = 4):
        fig, axs = plt.subplots(1, 2, figsize=(8, 4))
        ax = axs.ravel()
        self.Elasticity.plot(ax[1], max_x=max_x)
        self.Delay.plot(ax[0])
        plt.show()
