
# # QuantStats Dashboard — Advanced Tutorial

# This notebook shows:

# 1. **Minimal** dashboard (few figures/tables)  
# 2. **Full** dashboard (all built-ins)  
# 3. **Custom metrics in existing block** (e.g., add *Correlation vs Bench* under **Risk/Return**)  
# 4. **Custom metric block** ("Custom") next to the built-in blocks  
# 5. **Custom table** and controlling **which tables** the right slider governs  
# 6. **Choosing a subset** of figures/tables via the manifest  
# 7. **Custom figure per strategy** (one figure tile per strategy)  
# 8. **Custom figure for all strategies** (single tile across all strategies)

## Setup — imports and synthetic data (a) Pandas

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dashboard import QuantStatsDashboard, DashboardManifest, CustomTable, CustomFigure
from metrics import SimpleRegistry

np.random.seed(7)

dates = pd.date_range("2020-01-01", "2023-12-31", freq="B")
n = len(dates)

# two strategies + benchmark (simple gaussian toy)
s1 = 0.0003 + 0.01*np.random.randn(n)     # Strategy1
s2 = 0.0005 + 0.012*np.random.randn(n)    # Strategy2
b  = 0.00025 + 0.009*np.random.randn(n)   # Benchmark

returns = pd.DataFrame({
    "Strategy1": s1,
    "Strategy2": s2,
}, index=dates)
bench = pd.Series(b, index=dates, name="Benchmark")

returns.head(), bench.head()

## Setup — imports and synthetic data (b) Polars

import numpy as np
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
from dashboard import QuantStatsDashboard, DashboardManifest, CustomTable, CustomFigure
from metrics import SimpleRegistry

np.random.seed(7)

# Business-day date range
dates = pl.date_range(start=pl.datetime(2020,1,1), end=pl.datetime(2023,12,31), interval="1d", eager=True)
# filter to business days only (Mon-Fri)
dates = dates.filter(dates.dt.weekday() < 5)

n = len(dates)
s1 = 0.0003 + 0.01*np.random.randn(n)     # Strategy1
s2 = 0.0005 + 0.012*np.random.randn(n)    # Strategy2
b  = 0.00025 + 0.009*np.random.randn(n)   # Benchmark

# Polars DataFrame with a 'date' column + one column per series
returns = pl.DataFrame({
    "date": dates,
    "Strategy1": s1,
    "Strategy2": s2,
})
bench = pl.DataFrame({
    "date": dates,
    "Benchmark": b,
})

returns.head(), bench.head()

## Helper — default metric groups (copy of library defaults)


def default_metric_groups_copy():
    RR  = ["Cumulative Return","CAGR﹪","Sharpe","Sortino","Volatility (ann.)","Calmar","Time in Market"]
    DD  = ["Max Drawdown","Max DD Date","Max DD Period Start","Max DD Period End","Longest DD Days","Avg. Drawdown","Avg. Drawdown Days","Ulcer Index"]
    EXT = ["Best Day","Worst Day","Best Month","Worst Month","Best Year","Worst Year","Skew","Kurtosis"]
    TL  = ["Daily Value-at-Risk","Expected Shortfall (cVaR)","Omega"]
    PD  = ["MTD","3M","6M","YTD","1Y","3Y (ann.)","5Y (ann.)","10Y (ann.)","All-time (ann.)"]
    return [
        {"": RR},
        {"Drawdowns": DD},
        {"Extremes": EXT},
        {"Tails": TL},
        {"Periods": PD},
    ]

## 1) Minimal dashboard


manifest_min = DashboardManifest(
    figures=["snapshot","returns","monthly_heatmap"],
    tables=["metrics","eoy"],
)

dash_min = QuantStatsDashboard(
    returns_df=returns,
    benchmark=bench,
    rf=0.0,
    manifest=manifest_min,
    periods_per_year=252,
    title="Tutorial — Minimal",
    output_dir="output/tutorial_min",
)
dash_min.html_path

## 2) Full dashboard (all built-ins)

manifest_full = DashboardManifest(
    figures=None,           # None -> all default figures
    tables=None,            # None -> all default tables
)

dash_full = QuantStatsDashboard(
    returns_df=returns,
    benchmark=bench,
    rf=0.0,
    manifest=manifest_full,
    periods_per_year=252,
    title="Tutorial — Full",
    output_dir="output/tutorial_full",
)
dash_full.html_path


# ## 3) Custom metrics in an **existing** block

# We add two custom metrics and place them inside **Risk/Return**:

# - `corr_vs_bench`: correlation of excess returns with the benchmark  
# - `calmness`: `1 / (1 + annualized_vol)`

# We register them via `SimpleRegistry`, set `display_name_overrides`, and **append their labels** to the Risk/Return group while keeping the other default groups intact.

from metrics import SimpleRegistry
import polars as pl

# 1) Register your custom metrics
reg = SimpleRegistry()
reg.register(lambda r, b: pl.corr(r, b), name="corr_vs_bench")  # needs benchmark
reg.register(lambda r: (1.0 / (pl.col("r").abs().rolling_mean(21))).mean(), name="calmness")

# 2) Define groups and include the display names where you want them to appear
groups = [
    {"Risk/Return": [
        "Cumulative Return","CAGR﹪","Sharpe","Sortino","Volatility (ann.)","Calmar","Time in Market",
        "Correlation vs Bench","Calmness"     # <- add them here
    ]},
    {"Drawdowns": ["Max Drawdown","Max DD Date","Max DD Period Start","Max DD Period End","Longest DD Days"]},
    {"Extremes": ["Best Day","Worst Day","Best Month","Worst Month","Best Year","Worst Year"]},
    {"Tails": ["Daily Value-at-Risk","Expected Shortfall (cVaR)","Omega"]},
    {"Periods": ["MTD","3M","6M","YTD","1Y","3Y (ann.)","5Y (ann.)","10Y (ann.)","All-time (ann.)"]},
]

# 3) IMPORTANT: map internal keys -> display labels (and percent flags)
manifest_custom_in_rr = DashboardManifest(
    figures=["snapshot","returns","monthly_heatmap"],
    tables=["metrics","eoy"],
    metric_groups=groups,
    custom_metric_registry=reg,  # <-- this is the correct field name
    display_name_overrides={
        "corr_vs_bench": ("Correlation vs Bench", False),
        "calmness": ("Calmness", False),
    },
    strict_metric_groups=True,   # render ONLY what’s listed in `metric_groups`
)

# 4) Build the dashboard as usual
dash_custom_in_rr = QuantStatsDashboard(
    returns_df=returns,
    benchmark=bench,             # required for corr_vs_bench
    rf=0.0,
    periods_per_year=252,
    title="Custom Metrics inside Risk/Return",
    output_dir="output/tutorial_custom_in_rr",
    manifest=manifest_custom_in_rr,
)

print("HTML:", dash_custom_in_rr.html_path)


# ## 4) Separate **Custom** block

# If you prefer a dedicated section, keep the default blocks **unchanged** and **append** a new `"Custom"` group with your labels.  
# This avoids accidentally dragging built-in rows (like *1Y*, *10Y (ann.)*) under the Custom header.

from metrics import SimpleRegistry
import polars as pl

reg = SimpleRegistry()

# needs benchmark (binary metric): Pearson correlation
reg.register(lambda r, b: pl.corr(r, b), name="corr_vs_bench")

# unary metric: a simple “calmness” proxy (higher = smoother)
# avg( 1 / 21-day avg absolute return )
reg.register(lambda r: (1.0 / (r.abs().rolling_mean(21))).mean(), name="calmness")

# another example that should render as a PERCENT:
reg.register(lambda r: (r > 0).mean(), name="hit_rate")  # fraction ∈ [0,1]

display_map = {
    "corr_vs_bench": ("Correlation vs Bench", False),
    "calmness":      ("Calmness", False),
    "hit_rate":      ("Hit Rate", True),    # render 0.5331 → "53.31%"
}

custom_groups = [
    {"Risk/Return": [
        "Cumulative Return","CAGR﹪","Sharpe","Sortino","Volatility (ann.)","Calmar","Time in Market", 
        "Avg. Loss"
    ]},
    {"Drawdowns": [
        "Max Drawdown","Max DD Date","Max DD Period Start","Max DD Period End","Longest DD Days",
        "Avg. Drawdown","Avg. Drawdown Days",
    ]},
    {"Custom-DG": [                      # <-- your new block
        "Correlation vs Bench",
        "Calmness",
        "Hit Rate",
    ]},
    {"Extremes": [
        "Best Day","Worst Day","Best Month","Worst Month","Best Year","Worst Year","Skew","Kurtosis"
    ]},
    {"Tails": [
        "Daily Value-at-Risk","Expected Shortfall (cVaR)","Omega"
    ]},
    {"Periods": [
        "MTD","3M","6M","YTD","1Y","3Y (ann.)","5Y (ann.)","10Y (ann.)","All-time (ann.)"
    ]},
]

from dashboard import DashboardManifest, QuantStatsDashboard

manifest = DashboardManifest(
    figures=["snapshot","returns","monthly_heatmap"],
    tables=["metrics","eoy","drawdown_details"],
    metric_groups=custom_groups,
    custom_metric_registry=reg,           # <-- required so your metrics are computed
    display_name_overrides=display_map,   # <-- ensures labels + % flags
    strict_metric_groups=True,            # <-- render ONLY the metrics listed in your groups
)

dash = QuantStatsDashboard(
    returns_df=returns,           # pandas DataFrame of returns
    benchmark=bench,              # pandas Series (needed for corr_vs_bench)
    rf=0.0,
    periods_per_year=252,
    title="Dashboard with Custom Block",
    output_dir="output/custom_block",
    manifest=manifest,
)
print("HTML:", dash.html_path)


# ## 5) Custom table and right-slider control

# The `controlled` flag on `CustomTable` decides whether the **right slider** controls that table's width.

# We build a small *Winning/Losing Streaks* table and **exclude** it from slider control.


import numpy as np
import pandas as pd

def streaks_table(returns_df: pd.DataFrame, bench: pd.Series|None) -> pd.DataFrame:
    # simple daily streaks on Strategy1
    s = returns_df["Strategy1"].dropna()
    sign = np.sign(s.values)
    streaks = []
    cur = sign[0]; run = 1
    for x in sign[1:]:
        if x == cur:
            run += 1
        else:
            streaks.append((cur, run))
            cur = x; run = 1
    streaks.append((cur, run))
    wins  = max((r for (sgn, r) in streaks if sgn > 0), default=0)
    loss  = max((r for (sgn, r) in streaks if sgn < 0), default=0)
    return pd.DataFrame({"Max Winning Streak (days)":[wins], "Max Losing Streak (days)":[loss]}).T

ct = CustomTable(
    key="streaks",
    title="Winning/Losing Streaks (days)",
    builder=streaks_table,
    controlled=False,   # not governed by the right slider
)

manifest_custom_table = DashboardManifest(
    figures=["snapshot","returns"],
    tables=["metrics","eoy", "drawdown_details"],
    custom_tables=[ct],
    tables_controlled_by_slider=["metrics","eoy"],   # slider controls only these
)

dash_custom_table = QuantStatsDashboard(
    returns_df=returns, benchmark=bench, rf=0.0,
    manifest=manifest_custom_table,
    periods_per_year=252,
    title="Tutorial — Custom Table & Slider Control",
    output_dir="output/tutorial_custom_table",
)
dash_custom_table.html_path

## 6) Choosing subsets of figures/tables


manifest_subset = DashboardManifest(
    figures=["snapshot"],
    tables=["drawdown_details"],
    metric_cols=["Benchmark","Strategy1"],   # columns to show in KPI table
)

dash_subset = QuantStatsDashboard(
    returns_df=returns, benchmark=bench, rf=0.0,
    manifest=manifest_subset,
    periods_per_year=252,
    title="Tutorial — Subsets",
    output_dir="output/tutorial_subset",
)
dash_subset.html_path


# ## 7) Custom figure **per strategy** (one tile per strategy)

# We build a simple *cumulative equity* figure using Matplotlib.

import pandas as pd
def fig_equity(series: pd.Series, bench: pd.Series|None):
    eq = (1.0 + series.fillna(0)).cumprod()
    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(eq.index, eq.values, linewidth=1.5)
    ax.set_title(series.name)
    ax.grid(True, alpha=.3)
    return fig

cf_per = CustomFigure(
    key="equity_panel",
    title="Equity (custom)",
    builder=fig_equity,
    per_strategy=True,
)

manifest_cf_per = DashboardManifest(
    figures=["snapshot"],
    custom_figures=[cf_per],
    tables=["metrics"],
)

dash_cf_per = QuantStatsDashboard(
    returns_df=returns, benchmark=bench, rf=0.0,
    manifest=manifest_cf_per,
    periods_per_year=252,
    title="Tutorial — Custom Figure per Strategy",
    output_dir="output/tutorial_cf_per",
)
dash_cf_per.html_path


# ## 8) Custom figure for **all strategies** (single tile)

# We plot all equity curves on one axes.



def fig_all_equity(df: pd.DataFrame, bench: pd.Series|None):
    eq = (1.0 + df.fillna(0)).cumprod()
    fig, ax = plt.subplots(figsize=(5,3))
    for c in eq.columns:
        ax.plot(eq.index, eq[c].values, label=c, linewidth=1.3)
    if bench is not None:
        bq = (1.0 + bench.fillna(0)).cumprod()
        ax.plot(bq.index, bq.values, label="Benchmark", linewidth=1.3, linestyle="--")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=.3)
    ax.set_title("All equity (custom)")
    return fig

cf_all = CustomFigure(
    key="all_equity",
    title="All Equity (custom)",
    builder=fig_all_equity,
    per_strategy=False,
)

manifest_cf_all = DashboardManifest(
    figures=["snapshot"],
    custom_figures=[cf_all],
    tables=["metrics"],
)

dash_cf_all = QuantStatsDashboard(
    returns_df=returns, benchmark=bench, rf=0.0,
    manifest=manifest_cf_all,
    periods_per_year=252,
    title="Tutorial — Custom Global Figure",
    output_dir="output/tutorial_cf_all",
)
dash_cf_all.html_path
