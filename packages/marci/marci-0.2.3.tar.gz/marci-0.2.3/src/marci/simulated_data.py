import warnings
import pandas as pd
import numpy as np
from .utils import fmt, style, get_campaign_colors, PerformanceStats
import matplotlib.pyplot as plt


def remove_trailing_zeroes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove trailing rows that are entirely zeros or NaNs.
    Keeps leading zero/NaN rows.
    """
    mask = df.replace(0, np.nan).notna().any(axis=1)
    if mask.any():
        last_valid_idx = mask[::-1].idxmax()
        return df.loc[:last_valid_idx]
    else:
        return df.iloc[0:0]  # all rows empty


class SimulatedData:
    # exact schema + order
    required_cols = {
        "date": "datetime64[ns]",
        "name": "string",
        "seasonality": "float64",
        "base": "float64",
        "budget": "float64",
        "elastic_budget": "float64",
        "elastic_returns": "float64",
        "imps": "float64",
        "convs": "float64",
        "sales": "float64",
        "is_organic": "bool",
    }
    key_cols = ("date", "name", "is_organic")
    numeric_cols = [
        "seasonality",
        "base",
        "budget",
        "elastic_budget",
        "elastic_returns",
        "imps",
        "convs",
        "sales",
    ]

    def __init__(self, df: pd.DataFrame, name="Simulated Data"):
        self.name = name
        self._check_input_type(df)
        df = df.copy()

        # 1) schema + cleaning
        self._ensure_columns(df)
        df = self._coerce_dtypes(df)
        self._warn_on_null_keys(df)
        self._warn_on_negative_numerics(df)
        self._warn_on_duplicates(df)

        # 2) enforce column order and sort by keys
        # df = df.reset_index(drop=True)
        df = df[list(self.required_cols.keys())]
        df = df.sort_values(list(self.key_cols)).reset_index(drop=True)

        self.df = df
        self._compute_metrics()

    # ----------------- helpers -----------------
    @classmethod
    def _check_input_type(cls, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")

    @classmethod
    def _ensure_columns(cls, df: pd.DataFrame) -> None:
        miss = set(cls.required_cols) - set(df.columns)
        if miss:
            raise ValueError(f"Missing required columns: {sorted(miss)}")

    @classmethod
    def _coerce_dtypes(cls, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for col, dtype in cls.required_cols.items():
            if dtype.startswith("datetime"):
                out[col] = pd.to_datetime(out[col], errors="raise")
            elif dtype == "string":
                out[col] = out[col].astype("string")
            else:
                out[col] = pd.to_numeric(out[col], errors="coerce").astype(
                    dtype, copy=False
                )
        return out

    @classmethod
    def _warn_on_null_keys(cls, df: pd.DataFrame) -> None:
        mask = df[list(cls.key_cols)].isna().any(axis=1)
        if mask.any():
            warnings.warn(
                f"{int(mask.sum())} rows have nulls in key columns {cls.key_cols}.",
                RuntimeWarning,
            )

    @classmethod
    def _warn_on_negative_numerics(cls, df: pd.DataFrame) -> None:
        neg = {c: int((df[c] < 0).sum()) for c in cls.numeric_cols if (df[c] < 0).any()}
        if neg:
            details = ", ".join(f"{c}: {n}" for c, n in neg.items())
            warnings.warn(
                f"Negative values detected (should be non-negative): {details}.",
                RuntimeWarning,
            )

    @classmethod
    def _warn_on_duplicates(cls, df: pd.DataFrame) -> None:
        if df.duplicated(subset=list(cls.key_cols)).any():
            examples = (
                df.loc[
                    df.duplicated(subset=list(cls.key_cols), keep=False), cls.key_cols
                ]
                .drop_duplicates()
                .head(10)
                .to_dict(orient="records")
            )
            warnings.warn(
                f"Duplicate keys {cls.key_cols} detected. Examples: {examples}.",
                RuntimeWarning,
            )

    # ----------------- metrics & validation -----------------
    def _compute_metrics(self) -> None:
        mask = self.df["budget"] > 0
        self.df.loc[mask, "roas"] = (
            self.df.loc[mask, "sales"] / self.df.loc[mask, "budget"]
        )
        self.duration = float(self.df[self.df["budget"] > 0]["date"].nunique())
        self.tot_paid_budget = float(self.df[~self.df["is_organic"]]["budget"].sum())
        self.tot_organic_sales = float(self.df[self.df["is_organic"]]["sales"].sum())
        self.tot_paid_sales = float(self.df[~self.df["is_organic"]]["sales"].sum())
        self.tot_sales = float(self.df["sales"].sum())
        self.campaign_names = list(
            self.df.groupby("name")["budget"].sum().sort_values(ascending=False).index
        )
        self.paid_names = list(
            self.df[~self.df["is_organic"]]
            .groupby("name")["budget"]
            .sum()
            .sort_values(ascending=False)
            .index
        )
        self.colors = get_campaign_colors(self.campaign_names)
        self._Sim_Stats = PerformanceStats(
            self.name,
            "Simulated",
            organic_sales=self.tot_organic_sales,
            paid_sales=self.tot_paid_sales,
            paid_budget=self.tot_paid_budget,
        )

    def validate(self) -> bool:
        df = self.df
        if set(self.required_cols) - set(df.columns):
            raise ValueError("Required columns missing after operation.")
        if not pd.api.types.is_datetime64_ns_dtype(df["date"]):
            raise ValueError("'date' must be datetime64[ns]")
        if df[list(self.key_cols)].isna().any().any():
            warnings.warn("Nulls in key columns remain.", RuntimeWarning)
        neg = {
            c: int((df[c] < 0).sum()) for c in self.numeric_cols if (df[c] < 0).any()
        }
        if neg:
            warnings.warn(f"Negative values remain in numerics: {neg}.", RuntimeWarning)
        if df.duplicated(subset=list(self.key_cols)).any():
            warnings.warn(f"Non-unique keys {self.key_cols} remain.", RuntimeWarning)
        if list(df.columns) != list(self.required_cols.keys()):
            raise ValueError("Column order was lost.")
        return True

    # aggregate data

    @property
    def agg_df(self, include_organic=False):
        df = self.df.copy()
        df.loc[df["is_organic"], "budget"] = 0
        budget = (
            df.pivot_table("budget", "date", "name", "sum", 0, 1).drop("All")
        ).fillna(0)
        sales = df.groupby("date", as_index=True)["sales"].sum().rename("Total")

        pt = budget.join(sales)

        pt.columns = pd.MultiIndex.from_tuples(
            [("Budget", c) for c in budget.columns] + [("Sales", "All")],
            names=["Metric", "Name"],
        )
        return pt

    # ----------------- plotting -----------------

    def plot_lines(self, metric, ax, y_fmt="%", include_organic=False):
        pt = self.df.pivot_table(metric, "date", "name", "sum").replace(0, np.nan)
        for col in self.campaign_names:
            label = f"{col.replace('_', ' ').title()}: {fmt(pt[col].mean(), y_fmt)}"
            ax.plot(pt.index, pt[col], label=label, color=self.colors[col])
        style(
            ax,
            x_fmt="d",
            y_fmt=y_fmt,
            x_label="Date",
            y_label=metric.replace("_", " ").title(),
            title=f"{metric.replace('_', ' ').title()}",
            legend_loc="r",
        )

    def plot_scatter(self, metric, ax, y_fmt="%", title=None, include_organic=False):
        campaigns = self.campaign_names if include_organic else self.paid_names
        mask = self.df["name"].isin(campaigns)
        pt = self.df[mask].pivot_table(metric, "date", "name", "sum").replace(0, np.nan)
        for col in campaigns:
            label = f"{col.replace('_', ' ').title()}: {fmt(pt[col].mean(), y_fmt)}"
            rolling = pt[col].rolling(window=7).mean()
            ax.scatter(pt.index, pt[col], color=self.colors[col], alpha=0.3)
            ax.plot(pt.index, rolling, label=label, color=self.colors[col], lw=2)
        style(
            ax,
            x_fmt="d",
            y_fmt=y_fmt,
            x_label="Date",
            y_label=metric.replace("_", " ").title(),
            title=title,
            legend_loc="r",
        )

    def plot_bars(
        self,
        metric,
        ax,
        y_fmt="$",
        title=None,
        include_organic=False,
    ):
        campaigns = self.campaign_names if include_organic else self.paid_names
        mask = self.df["name"].isin(campaigns)
        pt = self.df[mask].pivot_table(metric, "date", "name", "sum", 0)
        pt = remove_trailing_zeroes(pt)
        bottom = pd.Series(0, index=pt.index)

        for col in campaigns:
            tot = pt[col].sum()
            label = f"{col.replace('_', ' ').title()}: {fmt(tot, y_fmt)}"
            ax.bar(
                pt.index,
                pt[col],
                width=1,
                bottom=bottom,
                color=self.colors[col],
                label=label,
                alpha=0.5,
            )
            bottom += pt[col]
        tot = pt.sum(axis=1)
        ax.scatter(pt.index, tot, color="black", marker="+", alpha=0.5)
        tot_rolling = tot.rolling(window=7).mean()
        ax.plot(
            pt.index,
            tot_rolling,
            lw=2,
            label=f"Total:\n{tot.sum():,.0f}",
            color="black",
        )
        style(
            ax,
            x_fmt="d",
            y_fmt=y_fmt,
            x_label="Date",
            title=title,
            legend_loc="r",
        )

    def plot_dist(self, metric, ax, title=None, include_organic=False):
        pt = self.df.groupby("date")[metric].sum()
        ax.hist(pt, bins=30, alpha=0.5, color="black", label="Total Daily Sales")
        style(
            ax,
            x_fmt="$",
            y_fmt=".0f",
            x_label="Daily Sales",
            y_label="Frequency (days)",
            title=title,
            legend_loc="r",
        )

    def plot_elasticity(self, ax, include_organic=False):
        campaigns = self.campaign_names if include_organic else self.paid_names
        mask = self.df["name"].isin(campaigns)
        for name in campaigns:
            mask = self.df["name"] == name
            _df = self.df[mask].sort_values("elastic_budget")
            ax.plot(
                _df["elastic_budget"],
                _df["elastic_returns"],
                label=name,
                color=self.colors[name],
            )
        style(
            ax,
            x_fmt=".0%",
            y_fmt=".0%",
            x_label="Elastic Budget",
            y_label="Elastic Returns",
            title="Elasticity",
            legend_loc="r",
        )

    def plot(self, include_organic=False):
        fig, ax = plt.subplots(3, 2, figsize=(16, 12))
        ax = ax.ravel()
        self.plot_lines("seasonality", ax[0], include_organic=True)
        self.plot_elasticity(ax[1], include_organic=include_organic)
        self.plot_bars("budget", ax[2], title="Budget", include_organic=include_organic)
        self.plot_bars("sales", ax[3], title="Sales", include_organic=True)
        self.plot_scatter("roas", ax[4], title="ROAS", include_organic=include_organic)
        self.plot_dist("sales", ax[5], title="Sales Distribution", include_organic=True)

    def plot_agg_data(self):
        fig, ax = plt.subplots(1, 2, figsize=(16, 9))
        ax = ax.ravel()
        self.plot_stacked("budget", ax[0])
        self.plot_stacked("sales", ax[1])
        plt.show()
