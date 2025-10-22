from __future__ import annotations


import numpy as np
import pandas as pd


class PerformanceStats:
    COLUMNS = [
        ("meta", "name"),
        ("meta", "kind"),
        ("budget", "paid"),
        ("sales", "organic"),
        ("sales", "paid"),
        ("sales", "total"),
        ("roas", "paid"),
        ("roas", "total"),
    ]
    META = COLUMNS[:2]

    def __init__(
        self,
        name: str,
        kind: str = "Expected",
        organic_sales: float = 0.0,
        paid_sales: float = 0.0,
        paid_budget: float = 0.0,
    ):
        row = {
            ("meta", "name"): name,
            ("meta", "kind"): kind,
            ("sales", "organic"): float(organic_sales or 0.0),
            ("budget", "paid"): float(paid_budget or 0.0),
            ("sales", "paid"): float(paid_sales or 0.0),
        }
        df = pd.DataFrame([row])
        df.columns = pd.MultiIndex.from_tuples(df.columns, names=["group", "metric"])
        self.df = df

    @staticmethod
    def _fmt_money(x: float) -> str:
        return f"${x:,.0f}" if x > 0 else ""

    @staticmethod
    def _fmt_pct(x: float) -> str:
        return f"{x:.0%}" if x > 0 else ""

    @classmethod
    def from_list(cls, name: str, stats_list: list["PerformanceStats"]):
        """Combine multiple PerformanceStats by summing numeric metrics grouped by meta."""
        if not stats_list:
            raise ValueError("stats_list cannot be empty.")

        df = pd.concat([s.df for s in stats_list], ignore_index=True)
        df[("meta", "name")] = name
        pt = df.groupby([("meta", "name"), ("meta", "kind")], as_index=False).sum()
        new = cls(name=name)
        new.df = pt
        return new

    def __str__(self) -> None:
        # aggregate
        pt = self.df.groupby(self.META, as_index=False).sum()

        # totals & ratios
        pt[("sales", "total")] = pt["sales"].sum(axis=1)
        denom_paid = pt[("budget", "paid")].replace(0, np.nan)
        pt[("roas", "paid")] = pt[("sales", "paid")] / denom_paid
        pt[("roas", "total")] = pt[("sales", "total")] / denom_paid

        # ensure all expected columns exist (fill missing with NaN)
        for col in self.COLUMNS:
            if col not in pt.columns:
                pt[col] = np.nan

        # reorder columns
        pt = pt.loc[:, self.COLUMNS]

        # format columns
        money_cols = list(filter(lambda x: x[0] in ["budget", "sales"], self.COLUMNS))
        pct_cols = list(filter(lambda x: x[0] == "roas", self.COLUMNS))

        for col in money_cols:
            pt[col] = pt[col].map(self._fmt_money)
        for col in pct_cols:
            pt[col] = pt[col].map(self._fmt_pct)
        return pt.to_string()


if __name__ == "__main__":
    A = PerformanceStats(name="A", organic_sales=100)
    B = PerformanceStats(name="B", paid_budget=2000, paid_sales=2000)
    C = PerformanceStats(
        name="B", kind="Simulated", organic_sales=200, paid_budget=2000, paid_sales=2000
    )
    print(A)
    print(B)
    D = PerformanceStats.from_list("C", [A, B, C])
    print(C)
