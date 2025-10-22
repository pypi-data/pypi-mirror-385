from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from .budgets import Budgets
from .simulated_data import SimulatedData
from .utils.performance_stats import PerformanceStats


if TYPE_CHECKING:
    from .campaigns import Campaign


class Portfolio:
    def __init__(self, campaigns: list[Campaign], name: str = "Portfolio"):
        self.name = name
        self.campaigns = {c.name: c for c in campaigns}
        self.organic = [c for c in campaigns if c.is_organic]
        self.paid = [c for c in campaigns if not c.is_organic]
        self.paid_names = [c.name for c in self.paid]
        self.budgets = Budgets(
            name="Default Budget",
            campaign_budgets={c.name: c.budget for c in self.paid},
        )
        self.organic_budgets = Budgets(
            name="Organic Budget",
            campaign_budgets={c.name: c.budget for c in self.organic},
        )
        self.all_budgets = Budgets.from_list(
            name="All Budgets",
            budgets_list=[self.budgets, self.organic_budgets],
        )

        self._Sim_Data = None
        self._Sim_Stats = None

    @property
    def sim_data(self):
        if self._Sim_Data is None:
            self.sim_outcomes()
        return self._Sim_Data

    @property
    def agg_data(self):
        return self.sim_data.agg_data

    # ---------------------------------------- PERFORMANCE STATS ----------------------------------------
    def exp_stats(self, budgets: Budgets = None):
        if budgets is None:
            budgets = self.all_budgets
        budgets = Budgets.from_list(
            name=budgets.name,
            budgets_list=[budgets, self.organic_budgets],
        )
        return PerformanceStats.from_list(
            self.name,
            [self.campaigns[name].exp_stats(budgets[name]) for name in budgets],
        )

    def sim_stats(self, budgets: Budgets = None):
        if budgets is None:
            return self.sim_data._Sim_Stats
        budgets = Budgets.from_list(
            name=budgets.name,
            budgets_list=[budgets, self.organic_budgets],
        )
        self.sim_outcomes(budgets)
        return self.sim_data._Sim_Stats

    def print_stats(self, budgets: Budgets = None):
        stats = PerformanceStats.from_list(
            self.name, [self.exp_stats(budgets), self.sim_stats(budgets)]
        )
        print(stats)

    # ---------------------------------------- SIMULATION ----------------------------------------
    def sim_outcomes(self, budgets: Budgets = None, include_organic: bool = True):
        if budgets is None:
            budgets = self.all_budgets
        if include_organic:
            budgets = Budgets.from_list(
                name=budgets.name,
                budgets_list=[budgets, self.organic_budgets],
            )
        print(budgets)
        dfs = []
        for name in budgets:
            campaign = self.campaigns[name]
            campaign.sim_outcomes(budget=budgets[name])
            dfs.append(campaign.sim_data.df)

        self._Sim_Data = SimulatedData(pd.concat(dfs), self.name)
        self._Sim_Stats = PerformanceStats.from_list(
            self.name,
            [self.campaigns[name].sim_stats() for name in budgets],
        )
        return self._Sim_Data

    # ---------------------------------------- OPTIMIZATION ----------------------------------------
    def _obj_exp_paid_daily_sales(self, budgets: Budgets = None):
        if budgets is None:
            budgets = self.budget
        sales = [
            self.campaigns[name].exp_daily_sales(budgets[name]) for name in budgets
        ]
        return np.sum(sales)

    def find_optimal_budgets(self, total_budget: float):
        def obj_fun(share_of_wallet: np.ndarray):
            share_of_wallet = np.asarray(share_of_wallet)
            new_budgets = Budgets(
                name="Optimal Budget",
                campaign_budgets={
                    name: share_of_wallet[i] * total_budget
                    for i, name in enumerate(self.paid_names)
                },
            )
            sales = self._obj_exp_paid_daily_sales(new_budgets)
            roas = sales / total_budget - 1
            return -roas

        x0 = [1 / len(self.paid) for _ in range(len(self.paid))]
        bounds = [(0, 1) for _ in range(len(self.paid))]
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        res = minimize(obj_fun, x0, bounds=bounds, constraints=constraints)
        optimial_budget_allocation = Budgets(
            name="Optimal Budget",
            campaign_budgets={
                name: float(res.x[i] * total_budget)
                for i, name in enumerate(self.paid_names)
            },
        )

        return optimial_budget_allocation

    def compare_budgets(self, budgets_list: list[Budgets]):
        fig, axs = plt.subplots(
            len(budgets_list), 2, figsize=(16, 4 * len(budgets_list))
        )
        for i, budgets in enumerate(budgets_list):
            self.print_stats(budgets)
            self.sim_data.plot_stacked("budget", axs[i, 0])
            self.sim_data.plot_stacked("sales", axs[i, 1])
        plt.show()

    def plot(self):
        self.sim_data.plot()
        plt.show()
