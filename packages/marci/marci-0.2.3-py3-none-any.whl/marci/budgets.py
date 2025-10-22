class Budgets:
    def __init__(self, name: str, campaign_budgets: dict[str, float]):
        self.name = name
        self.campaign_names = list(campaign_budgets.keys())
        self.campaign_budgets = campaign_budgets
        self.total_budget = sum(campaign_budgets.values())

    def __getitem__(self, key: str):
        return self.campaign_budgets[key]

    def __repr__(self):
        cls = self.__class__.__name__
        inner = ", ".join(f"{k!r}: ${v:,.0f}" for k, v in self.campaign_budgets.items())
        return f"{cls}({self.name!r}, total=${self.total_budget:,.0f}, {{{inner}}})"

    def __len__(self):
        return len(self.campaign_budgets)

    def __iter__(self):
        return iter(self.campaign_names)

    # --- MERGE FUNCTION ---
    @staticmethod
    def from_list(name: str, budgets_list: list["Budgets"]) -> "Budgets":
        merged = {}
        for b in budgets_list:
            for k, v in b.campaign_budgets.items():
                if k not in merged:
                    merged[k] = v  # keep first occurrence
        return Budgets(name, merged)
