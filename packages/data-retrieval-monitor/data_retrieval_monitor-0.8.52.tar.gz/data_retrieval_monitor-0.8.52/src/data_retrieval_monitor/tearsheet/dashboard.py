# dashboard.py
from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Callable, Tuple
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import polars as pl
from quantstats import plots as qs_plots

from metrics import metrics_polars as metrics_pl
from metrics import SimpleRegistry 
# =============================================================================
# Helpers (filesystem, conversions, alignment)
# =============================================================================

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _unique(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def _pd_returns_to_pl(returns: Union[pd.Series, pd.DataFrame]) -> pl.DataFrame:
    """
    Convert pandas returns (Series or DataFrame with DatetimeIndex) to
    Polars DataFrame with a 'date' column (pl.Datetime) and one column per strategy.
    """
    if isinstance(returns, pd.Series):
        pdf = returns.to_frame(name=returns.name or "Strategy")
    else:
        pdf = returns.copy()
    idx = pd.DatetimeIndex(pdf.index).tz_localize(None)
    data = {"date": list(idx.to_pydatetime())}
    for c in pdf.columns:
        data[str(c)] = pd.to_numeric(pdf[c], errors="coerce").astype(float).to_numpy()
    return pl.DataFrame(data).with_columns(pl.col("date").cast(pl.Datetime))

# =======================
# New: Polars -> Pandas coercion helpers
# =======================
def _infer_pl_date_col(df: pl.DataFrame) -> str:
    """Find a date/datetime column in a Polars DataFrame."""
    date_cols = [c for c, dt in df.schema.items() if dt in (pl.Date, pl.Datetime)]
    if date_cols:
        return date_cols[0]
    for cand in ("date", "datetime", "dt", "timestamp", "time"):
        if cand in df.columns:
            return cand
    raise ValueError("Could not find a date/datetime column in the provided Polars DataFrame.")
def _pl_df_to_pd_returns(df: pl.DataFrame) -> pd.DataFrame:
    """
    Polars DF with a date/datetime column + one or more numeric strategy columns
    -> Pandas DataFrame with DatetimeIndex and float columns.
    """
    date_col = _infer_pl_date_col(df)
    cols = [c for c in df.columns if c != date_col]
    if not cols:
        raise ValueError("Polars DataFrame must contain at least one strategy column besides the date column.")

    pdf = df.select([date_col] + cols).to_pandas()

    # Robust datetime handling
    date_vals = pdf[date_col]
    # Always go through pd.to_datetime; then build a DatetimeIndex and strip tz if present.
    idx = pd.to_datetime(date_vals, errors="coerce")
    idx = pd.DatetimeIndex(idx)
    try:
        # if tz-aware, drop tz; if tz-naive, this raises -> we ignore
        idx = idx.tz_localize(None)  # type: ignore[attr-defined]
    except Exception:
        pass
    if pd.isna(idx).any():
        raise ValueError("Invalid date values in the Polars DataFrame.")

    out = pdf.drop(columns=[date_col])
    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype(float)
    out.index = idx
    out = out.sort_index()
    return out
def _pl_series_to_pd_returns(series: pl.Series, default_name: str = "Strategy") -> pd.DataFrame:
    """
    Accept a Polars Series for returns:
    - Struct series where each row is {'date': ..., '<value_name>': float}.
    """
    if series.dtype == pl.Struct:
        rows = series.to_list()
        if not rows:
            return pd.DataFrame({default_name: []}, index=pd.DatetimeIndex([]))
        keys = list(rows[0].keys())
        if "date" not in keys:
            raise ValueError("Struct Series must contain a 'date' field.")
        val_cols = [k for k in keys if k != "date"]
        if not val_cols:
            raise ValueError("Struct Series must contain a value field besides 'date'.")
        val_col = val_cols[0]

        pdf = pd.DataFrame(rows)
        idx = pd.to_datetime(pdf["date"], errors="coerce")
        idx = pd.DatetimeIndex(idx)
        try:
            idx = idx.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        if pd.isna(idx).any():
            raise ValueError("Invalid 'date' values in Struct Series.")

        name = series.name or val_col or default_name
        out = pd.DataFrame({str(name): pd.to_numeric(pdf[val_col], errors="coerce").astype(float).values}, index=idx)
        return out.sort_index()

    raise ValueError(
        "Unsupported Polars Series for returns. "
        "Pass a Struct Series with fields {'date', '<value>'} or use a Polars DataFrame with a 'date' column."
    )

def _coerce_returns_to_pd(returns_obj: Union[pd.Series, pd.DataFrame, pl.Series, pl.DataFrame, pl.LazyFrame]) -> pd.DataFrame:
    """Accept Pandas or Polars (LazyFrame/DataFrame/Series) and return a Pandas DataFrame (DatetimeIndex)."""
    # Pandas
    if isinstance(returns_obj, pd.Series):
        df = returns_obj.to_frame(name=returns_obj.name or "Strategy")
        df.index = pd.DatetimeIndex(pd.to_datetime(df.index, errors="coerce"))
        try:
            df.index = df.index.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
        return df.sort_index()

    if isinstance(returns_obj, pd.DataFrame):
        out = returns_obj.copy()
        out.index = pd.DatetimeIndex(pd.to_datetime(out.index, errors="coerce"))
        try:
            out.index = out.index.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        for c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").astype(float)
        return out.sort_index()

    # Polars
    if isinstance(returns_obj, pl.LazyFrame):
        returns_obj = returns_obj.collect()
    if isinstance(returns_obj, pl.DataFrame):
        return _pl_df_to_pd_returns(returns_obj)
    if isinstance(returns_obj, pl.Series):
        return _pl_series_to_pd_returns(returns_obj)

    raise TypeError("Unsupported type for returns_df. Provide Pandas DataFrame/Series or Polars DataFrame/LazyFrame/Series.")
def _coerce_bench_to_pd(bench_obj: Optional[Union[pd.Series, pl.Series, pl.DataFrame, pl.LazyFrame]]) -> Optional[pd.Series]:
    """Accept Pandas or Polars (LazyFrame/DataFrame/Series) for benchmark and return a Pandas Series (DatetimeIndex)."""
    if bench_obj is None:
        return None

    # Pandas
    if isinstance(bench_obj, pd.Series):
        s = bench_obj.copy()
        idx = pd.DatetimeIndex(pd.to_datetime(s.index, errors="coerce"))
        try:
            idx = idx.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        s.index = idx
        s.name = s.name or "Benchmark"
        s = pd.to_numeric(s, errors="coerce").astype(float)
        return s.sort_index()

    if isinstance(bench_obj, pd.DataFrame):
        if bench_obj.shape[1] == 0:
            return None
        col = bench_obj.columns[0]
        s = bench_obj[col].copy()
        idx = pd.DatetimeIndex(pd.to_datetime(bench_obj.index, errors="coerce"))
        try:
            idx = idx.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        s.index = idx
        s.name = str(col) or "Benchmark"
        s = pd.to_numeric(s, errors="coerce").astype(float)
        return s.sort_index()

    # Polars
    if isinstance(bench_obj, pl.LazyFrame):
        bench_obj = bench_obj.collect()
    if isinstance(bench_obj, pl.DataFrame):
        date_col = _infer_pl_date_col(bench_obj)
        value_cols = [c for c in bench_obj.columns if c != date_col]
        if not value_cols:
            return None
        val = value_cols[0]
        pdf = bench_obj.select([date_col, val]).to_pandas()
        idx = pd.DatetimeIndex(pd.to_datetime(pdf[date_col], errors="coerce"))
        try:
            idx = idx.tz_localize(None)  # type: ignore[attr-defined]
        except Exception:
            pass
        s = pd.Series(pd.to_numeric(pdf[val], errors="coerce").astype(float).values, index=idx, name=str(val) or "Benchmark")
        return s.sort_index()

    if isinstance(bench_obj, pl.Series):
        if bench_obj.dtype == pl.Struct:
            rows = bench_obj.to_list()
            if not rows:
                return None
            keys = list(rows[0].keys())
            if "date" not in keys:
                raise ValueError("Struct Series for benchmark must contain a 'date' field.")
            val_cols = [k for k in keys if k != "date"]
            if not val_cols:
                raise ValueError("Struct Series for benchmark must contain a value field besides 'date'.")
            val_col = val_cols[0]
            pdf = pd.DataFrame(rows)
            idx = pd.DatetimeIndex(pd.to_datetime(pdf["date"], errors="coerce"))
            try:
                idx = idx.tz_localize(None)  # type: ignore[attr-defined]
            except Exception:
                pass
            s = pd.Series(pd.to_numeric(pdf[val_col], errors="coerce").astype(float).values, index=idx, name=bench_obj.name or "Benchmark")
            return s.sort_index()

        raise ValueError(
            "Unsupported Polars Series for benchmark. "
            "Pass a Struct Series with fields {'date','<value>'} or use a Polars DataFrame with a 'date' column."
        )

    raise TypeError("Unsupported type for benchmark. Provide Pandas Series/DataFrame or Polars DataFrame/LazyFrame/Series.")
def _pd_bench_to_pl(bench: Optional[pd.Series]) -> Optional[pl.DataFrame]:
    if bench is None:
        return None
    s = bench.copy()
    s.name = s.name or "Benchmark"
    idx = pd.DatetimeIndex(s.index).tz_localize(None)
    data = {
        "date": list(idx.to_pydatetime()),
        str(s.name): pd.to_numeric(s, errors="coerce").astype(float).to_numpy(),
    }
    return pl.DataFrame(data).with_columns(pl.col("date").cast(pl.Datetime))

def _pl_frame_from_index(idx: pd.DatetimeIndex, values: np.ndarray,
                         date_col: str = "date", val_col: str = "ret") -> pl.DataFrame:
    idx = pd.DatetimeIndex(idx).tz_localize(None)
    py_dt = list(idx.to_pydatetime())
    date_s = pl.Series(date_col, py_dt).cast(pl.Datetime)
    val_s  = pl.Series(val_col, np.asarray(values, dtype=np.float64))
    return pl.DataFrame({date_col: date_s, val_col: val_s})

def _align_like(obj: Union[pd.Series, pd.DataFrame, float, int],
                index: pd.DatetimeIndex,
                fill: float = 0.0) -> pd.Series:
    """Align rf-like object to index."""
    if isinstance(obj, (float, int)):
        return pd.Series(float(obj), index=index, name="rf")
    if isinstance(obj, pd.DataFrame):
        s = obj.iloc[:, 0] if obj.shape[1] > 1 else obj.squeeze("columns")
        s = s.reindex(index).fillna(fill)
        s.name = "rf"
        return s
    if isinstance(obj, pd.Series):
        s = obj.reindex(index).fillna(fill)
        s.name = "rf"
        return s
    return pd.Series(fill, index=index, name="rf")

def _maybe_excess_returns(returns_pd: pd.DataFrame,
                          rf: Optional[Union[float, int, pd.Series, pd.DataFrame]],
                          periods_per_year: int) -> pd.DataFrame:
    """Convert returns to excess returns if rf provided."""
    rets = returns_pd.copy()
    try:
        rets.index = rets.index.tz_localize(None)
    except Exception:
        pass

    if rf is None:
        return rets

    if isinstance(rf, (float, int)):
        pprf = (1.0 + float(rf)) ** (1.0 / periods_per_year) - 1.0
        return rets - pprf

    rf_series = _align_like(rf, rets.index, fill=0.0)
    return rets.sub(rf_series, axis=0)

# =============================================================================
# Default figure/table keys
# =============================================================================

DEFAULT_FIGURES = [
    "snapshot",
    "earnings",
    "returns",
    "log_returns",
    "yearly_returns",
    "daily_returns",
    "rolling_beta",
    "rolling_volatility",
    "rolling_sharpe",
    "rolling_sortino",
    "drawdowns_periods",
    "drawdown",
    "monthly_heatmap",
    "histogram",
    "distribution",
]

ALL_TABLES = ["metrics", "eoy", "monthly_returns", "drawdown_details"]

# =============================================================================
# Custom extension points
# =============================================================================

@dataclass
class CustomTable:
    key: str
    title: str
    builder: Callable[[pd.DataFrame, Optional[pd.Series]], pd.DataFrame]  # returns pandas DF ready to render
    controlled: bool = True   # if True, attached to right slider width

@dataclass
class CustomFigure:
    key: str
    title: str
    builder: Callable[..., plt.Figure]  # see per_strategy flag below
    per_strategy: bool = True           # True: builder(series, bench_series|None) -> Figure; False: builder(df, bench_series|None) -> Figure


@dataclass
class DashboardManifest:
    figures: Optional[List[str]] = None
    metric_rows: Optional[List[str]] = None
    metric_cols: Optional[List[str]] = None
    tables: Optional[List[str]] = None
    metric_groups: Optional[List[Dict[str, List[str]]]] = None
    composites: Optional[Dict[str, Union[str, Dict[str, float]]]] = None
    strategy_filter: Optional[List[str]] = None
    tables_controlled_by_slider: Optional[List[str]] = None
    custom_tables: Optional[List["CustomTable"]] = None
    custom_figures: Optional[List["CustomFigure"]] = None

    # NEW:
    display_name_overrides: Optional[Dict[str, Tuple[str, bool]]] = None  # {"corr_vs_bench": ("Correlation vs Bench", False)}
    custom_metric_registry: Optional["SimpleRegistry"] = None             # scores.metrics_pl3.SimpleRegistry
    strict_metric_groups: bool = True                                     # if True, render ONLY metrics listed in metric_groups
# =============================================================================
# Main Dashboard
# =============================================================================

class QuantStatsDashboard:
    # -----------------------
    # Small helpers
    # -----------------------
    @staticmethod
    def _norm_key(s: str) -> str:
        try:
            return "".join(ch.lower() for ch in str(s) if ch.isalnum())
        except Exception:
            return str(s).lower()

    def _norm_name_list(self, names: List[str], pool: List[str]) -> List[str]:
        want = {n.lower() for n in names}
        return [p for p in pool if p.lower() in want]
    def _string_metric_keys(self) -> set[str]:
        # internal metric keys that are *strings* (dates/labels) coming from metrics_pl3
        return {"max_dd_date", "max_dd_start", "max_dd_end"}

    def _int_metric_labels(self) -> set[str]:
        # display labels that should be rendered as integers
        return {"Avg. Drawdown Days", "Longest DD Days"}
        # ---- Display map for metrics (internal key -> (Display Label, is_percent))
    def _display_name_map(self) -> Dict[str, Tuple[str, bool]]:
        # internal_key -> (Display Label, is_percent)
        base = {
            # Risk/Return base
            "comp": ("Cumulative Return", True),
            "cagr": ("CAGR﹪", True),
            "sharpe": ("Sharpe", False),
            "sortino": ("Sortino", False),
            "vol_ann": ("Volatility (ann.)", True),
            "calmar": ("Calmar", False),

            # Extremes / distribution
            "best_day": ("Best Day", True),
            "worst_day": ("Worst Day", True),
            "best_month": ("Best Month", True),
            "worst_month": ("Worst Month", True),
            "best_year": ("Best Year", True),
            "worst_year": ("Worst Year", True),
            "skew": ("Skew", False),
            "kurtosis": ("Kurtosis", False),

            # Drawdowns
            "max_drawdown": ("Max Drawdown", True),
            "avg_drawdown": ("Avg. Drawdown", True),
            "ulcer": ("Ulcer Index", True),
            "longest_dd_days": ("Longest DD Days", False),
            "avg_dd_days": ("Avg. Drawdown Days", False),
            "max_dd_date": ("Max DD Date", False),
            "max_dd_start": ("Max DD Period Start", False),
            "max_dd_end": ("Max DD Period End", False),

            # Tails
            "VaR_5": ("Daily Value-at-Risk", True),
            "CVaR_5": ("Expected Shortfall (cVaR)", True),
            "omega_0": ("Omega", False),

            # Period slices
            "mtd": ("MTD", True),
            "3m": ("3M", True),
            "6m": ("6M", True),
            "ytd": ("YTD", True),
            "1y": ("1Y", True),
            "3y_ann": ("3Y (ann.)", True),
            "5y_ann": ("5Y (ann.)", True),
            "10y_ann": ("10Y (ann.)", True),
            "alltime_ann": ("All-time (ann.)", True),

            # Extras
            "exposure": ("Time in Market", True),
            "avg_win": ("Avg. Win", True),
            "avg_loss": ("Avg. Loss", True),
            "payoff": ("Payoff Ratio", False),
            "win_rate": ("Win Days", True),
        }
        # merge user overrides (also used for custom metrics)
        base.update(self.display_overrides)
        return base

    def _default_metric_groups(self) -> List[Dict[str, List[str]]]:
        RR  = ["Cumulative Return","CAGR﹪","Sharpe","Sortino","Volatility (ann.)","Calmar","Time in Market", "Avg. Win","Avg. Loss","Payoff Ratio","Win Days"]
        DD  = ["Max Drawdown","Max DD Date","Max DD Period Start","Max DD Period End","Longest DD Days","Avg. Drawdown","Avg. Drawdown Days","Ulcer Index"]
        EXT = ["Best Day","Worst Day","Best Month","Worst Month","Best Year","Worst Year","Skew","Kurtosis"]
        TL  = ["Daily Value-at-Risk","Expected Shortfall (cVaR)","Omega"]
        PD  = ["MTD","3M","6M","YTD","1Y","3Y (ann.)","5Y (ann.)","10Y (ann.)","All-time (ann.)"]
        return [
            {"Risk/Return": RR},
            {"Drawdowns": DD},
            {"Extremes": EXT},
            {"Tails": TL},
            {"Periods": PD},
        ]

    def _is_percent_label(self, display_label: str) -> bool:
        # exact lookup from display map
        dm = self._display_name_map()
        for _, (lbl, is_pct) in dm.items():
            if lbl == display_label:
                return is_pct
        # conservative fallback heuristic
        s = display_label.lower()
        hints = ("return", "volatility", "ytd", "mtd", "ann.", "month", "year", "win", "%")
        anti  = ("skew", "kurtosis", "omega", "calmar", "sharpe", "sortino", "payoff", "days")
        return any(h in s for h in hints) and not any(a in s for a in anti)
    
    def _format_number(self, v: object, is_pct: bool) -> str:
        """
        Format a single value:
        - coerce numeric-like strings (incl. ones with '%' or commas)
        - 2 decimals everywhere
        - add '%' for percent metrics
        - show '-' for NaN/inf/None
        """
        if v is None:
            return "-"

        # Try to coerce any string to float (handle "12.34", "12.34%", "1,234.5")
        if isinstance(v, str):
            raw = v.strip()
            had_pct = raw.endswith("%")
            raw = raw.replace(",", "").replace("%", "")
            try:
                x = float(raw)
            except Exception:
                return v  # not numeric-looking
            if not np.isfinite(x):
                return "-"
            # If the original string already had a percent symbol, x is already scaled.
            if had_pct:
                return f"{x:.2f}%" if is_pct else f"{x:.2f}"
            # Otherwise numbers are fractions for percent metrics.
            return f"{x*100:.2f}%" if is_pct else f"{x:.2f}"

        # Numeric
        if isinstance(v, (int, float, np.integer, np.floating)):
            if not np.isfinite(float(v)):
                return "-"
            x = float(v)
            return f"{x*100:.2f}%" if is_pct else f"{x:.2f}"

        return str(v)

    def _format_df_2dp(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format every cell to 2 decimals, add '%' for percent-marked rows.
        Works even if some cells are strings.
        """
        if df is None or df.empty:
            return df
        out = df.copy()
        for label in out.index:
            is_pct = self._is_percent_label(label)
            out.loc[label] = out.loc[label].map(lambda v: self._format_number(v, is_pct))
        return out.astype(str)

    def _compute_composites(
        self, df: pd.DataFrame, spec: Optional[Dict[str, Union[str, Dict[str, float]]]]
    ) -> pd.DataFrame:
        if not spec:
            return df
        base = df.copy()
        cols = list(base.columns)
        for name, rule in spec.items():
            if isinstance(rule, str) and rule.lower() in ("equal","ew","eq"):
                w = pd.DataFrame(1.0 / len(cols), index=base.index, columns=cols)
                comp = (base * w).sum(axis=1, min_count=1)
            elif isinstance(rule, dict):
                use = {k: float(v) for k, v in rule.items() if k in cols}
                if not use: continue
                s = sum(use.values())
                if s == 0: continue
                use = {k: v/s for k, v in use.items()}
                comp = sum(base[k] * w for k, w in use.items())
            else:
                continue
            comp.name = name
            base[name] = comp
        return base

    # -----------------------
    # Lifecycle
    # -----------------------
    def __init__(
        self,
        returns_df: Union[pd.DataFrame, pd.Series, pl.DataFrame, pl.LazyFrame, pl.Series],
        benchmark: Optional[Union[pd.Series, pl.Series, pl.DataFrame, pl.LazyFrame]] = None,
        rf: Optional[Union[float, int, pd.Series, pd.DataFrame]] = None,
        title: str = "Strategy Tearsheet",
        output_dir: str = "output/comprehensive_reports",
        manifest: Optional[DashboardManifest] = None,
        periods_per_year: int = 252,
    ) -> None:
        self.ppy = periods_per_year
        self.title = title
        self.output_dir = output_dir
        self.manifest = manifest or DashboardManifest()
        self.display_overrides = self.manifest.display_name_overrides or {}
        self.strict_groups = bool(self.manifest.strict_metric_groups)
        self.custom_registry = self.manifest.custom_metric_registry
        _ensure_dir(self.output_dir)

        # --- normalize inputs: NOW supports Polars (DF/LazyFrame/Series) or Pandas
        self.returns_pd = _coerce_returns_to_pd(returns_df)
        # ensure column names are strings
        self.returns_pd.columns = [str(c) for c in self.returns_pd.columns]

        self.benchmark = _coerce_bench_to_pd(benchmark)
        if self.benchmark is not None:
            self.benchmark.name = self.benchmark.name or "Benchmark"

        # composites on ORIGINAL returns if requested
        if self.manifest.composites:
            self.returns_pd = self._compute_composites(self.returns_pd, self.manifest.composites)

        self.strategies = list(self.returns_pd.columns)

        # Align with benchmark if present
        if self.benchmark is not None:
            common_idx = self.returns_pd.index.intersection(self.benchmark.index)
            self.returns_pd = self.returns_pd.loc[common_idx]
            self.benchmark = self.benchmark.loc[common_idx]

        # Convert to EXCESS once
        self.returns_excess = _maybe_excess_returns(self.returns_pd, rf, self.ppy)
        self.benchmark_excess = None
        if self.benchmark is not None:
            self.benchmark_excess = _maybe_excess_returns(self.benchmark.to_frame("Benchmark"), rf, self.ppy)["Benchmark"]

        # Strategy subset to render
        if self.manifest.strategy_filter:
            self.render_strategies = self._norm_name_list(self.manifest.strategy_filter, self.strategies) or self.strategies[:]
        else:
            self.render_strategies = self.strategies[:]

        # date range
        self.start = self.returns_excess.index.min().strftime("%Y-%m-%d")
        self.end = self.returns_excess.index.max().strftime("%Y-%m-%d")
        self.date_range_str = f"{self.start} — {self.end}"

        # figures list
        self.fig_list = (self.manifest.figures if self.manifest.figures else DEFAULT_FIGURES)

        # tables subset
        if self.manifest.tables:
            self.tables_list = [t for t in self.manifest.tables if t in ALL_TABLES]
            if not self.tables_list:
                self.tables_list = ALL_TABLES.copy()
        else:
            self.tables_list = ALL_TABLES.copy()

        # Which tables are controlled by right slider
        if self.manifest.tables_controlled_by_slider:
            self.tables_controlled = [t for t in self.manifest.tables_controlled_by_slider]
        else:
            self.tables_controlled = ["metrics","eoy","drawdown_details"]

        # metric columns: default = Benchmark + render_strategies
        self.default_metric_cols = (["Benchmark"] if self.benchmark_excess is not None else []) + self.render_strategies
        self.metric_cols_filter = None
        if self.manifest.metric_cols:
            # validate against available (Benchmark + all strategies)
            avail = (["Benchmark"] if self.benchmark_excess is not None else []) + self.strategies
            self.metric_cols_filter = self._norm_name_list(self.manifest.metric_cols, avail)

        # metric groups
        self.metric_groups = self.manifest.metric_groups or self._default_metric_groups()

        # custom extensions
        self.custom_tables = self.manifest.custom_tables or []
        self.custom_figs   = self.manifest.custom_figures or []

        # output paths
        self.fig_dir = os.path.join(self.output_dir, "figures")
        _ensure_dir(self.fig_dir)
        self.html_path = os.path.join(self.output_dir, "dashboard.html")
        self.manifest_path = os.path.join(self.output_dir, "available_manifest.json")

        # build
        self._save_manifest()
        self._build_figures()
        self._build_tables()
        self._write_html()

    # -----------------------
    # Manifest / metrics compute
    # -----------------------
    def _save_manifest(self) -> None:
        full_metrics = self._compute_metrics_table(full=True)
        keys = list(full_metrics.index)
        manifest = {
            "figures_available": DEFAULT_FIGURES,
            "tables_available": ALL_TABLES,
            "metric_rows": keys,
            "metric_cols": (["Benchmark"] if self.benchmark_excess is not None else []) + self.strategies,
            "date_range": [self.start, self.end],
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"[manifest] wrote: {self.manifest_path}")

    def _compute_metrics_table(self, full: bool = False) -> pd.DataFrame:
        # pandas -> Polars
        ret_pl = _pd_returns_to_pl(self.returns_excess)
        bench_pl = _pd_bench_to_pl(self.benchmark_excess) if self.benchmark_excess is not None else None

        out_pl = metrics_pl(
            returns=ret_pl,
            benchmark=bench_pl,
            rf=0.0,
            mode="full" if full else "basic",
            registry=self.custom_registry,   # <--- enables custom metrics
        )

        df = out_pl.to_pandas() if isinstance(out_pl, pl.DataFrame) else pd.DataFrame(out_pl)
        if "metric" in df.columns:
            df = df.set_index("metric")

        # map internal keys -> display labels (includes overrides)
        dm = self._display_name_map()
        df.index = [dm.get(str(raw), (str(raw), False))[0] for raw in df.index]
        df.index.name = "Metric"

        # Put 'Benchmark' first if present
        cols = list(df.columns)
        if "benchmark" in cols:
            df = df.rename(columns={"benchmark": "Benchmark"})
        if "Benchmark" in df.columns:
            df = df[["Benchmark"] + [c for c in df.columns if c != "Benchmark"]]

        return df
    # -----------------------
    # Per-strategy tables (EOY / Monthly / Drawdowns)
    # -----------------------
    def _eoy_table(self) -> Dict[str, pd.DataFrame]:
        out: Dict[str, pd.DataFrame] = {}
        bench_map: Dict[int, float] = {}
        if self.benchmark_excess is not None:
            b = self.benchmark_excess.dropna()
            if not b.empty:
                bpl = _pl_frame_from_index(b.index, b.values)
                by = (
                    bpl.with_columns(pl.col("date").dt.year().alias("year"))
                       .group_by("year")
                       .agg(((pl.col("ret") + 1.0).product() - 1.0).alias("bench_eoy"))
                       .sort("year")
                )
                bench_map = dict(zip(by["year"].to_list(), by["bench_eoy"].to_list()))

        for col in self.render_strategies:
            s = self.returns_excess[col].dropna()
            if s.empty:
                out[col] = pd.DataFrame(columns=["Year","Benchmark","Strategy","Multiplier","Won"])
                continue

            spl = _pl_frame_from_index(s.index, s.values)
            sy = (
                spl.with_columns(pl.col("date").dt.year().alias("year"))
                   .group_by("year")
                   .agg(((pl.col("ret") + 1.0).product() - 1.0).alias("strat_eoy"))
                   .sort("year")
            )

            df = sy.to_pandas().rename(columns={"year":"Year","strat_eoy":"Strategy"})
            if bench_map:
                df["Benchmark"] = df["Year"].map(bench_map).astype(float)
            else:
                df["Benchmark"] = np.nan

            bench = df["Benchmark"].to_numpy()
            strat = df["Strategy"].to_numpy()
            with np.errstate(divide="ignore", invalid="ignore"):
                mult = np.where(np.isfinite(bench) & (np.abs(bench) > 1e-12), strat / bench, np.nan)
            df["Multiplier"] = mult
            df["Won"] = np.where(np.isfinite(strat) & np.isfinite(bench),
                                 np.where(strat > bench, "+", "–"), "")
            out[col] = df[["Year","Benchmark","Strategy","Multiplier","Won"]].reset_index(drop=True)
        return out

    def _monthly_tables(self) -> Dict[str, pd.DataFrame]:
        res: Dict[str, pd.DataFrame] = {}
        for col in self.render_strategies:
            ser = self.returns_excess[col].dropna()
            if ser.empty:
                res[col] = pd.DataFrame()
                continue
            dfpl = _pl_frame_from_index(ser.index, ser.values)
            m = (
                dfpl.with_columns([
                        pl.col("date").dt.year().alias("year"),
                        pl.col("date").dt.month().alias("month"),
                    ])
                    .group_by(["year","month"])
                    .agg(((pl.col("ret") + 1.0).product() - 1.0).alias("mret"))
                    .sort(["year","month"])
            )
            wide = m.pivot(index="year", columns="month", values="mret").sort("year")
            pdf = wide.to_pandas().set_index("year")
            from datetime import datetime as _dt
            pdf.columns = [_dt(2000, int(c), 1).strftime("%b") for c in pdf.columns]
            res[col] = pdf
        return res

    def _drawdown_tables(self) -> Dict[str, pd.DataFrame]:
        out: Dict[str, pd.DataFrame] = {}
        for col in self.render_strategies:
            s = self.returns_excess[col].dropna()
            if s.empty:
                out[col] = pd.DataFrame()
                continue
            dfpl = _pl_frame_from_index(s.index, s.values).sort("date")
            dfpl = (
                dfpl
                .with_columns((1.0 + pl.col("ret")).cum_prod().alias("equity"))
                .with_columns(pl.col("equity").cum_max().alias("peak"))
                .with_columns((pl.col("equity") / pl.col("peak") - 1.0).alias("dd"))
                .with_columns((pl.col("dd") < -1e-12).alias("is_dd"))
                .with_columns(((pl.col("is_dd") & (~pl.col("is_dd").shift(1).fill_null(False))).cast(pl.Int64).alias("start_flag")))
                .with_columns(pl.col("start_flag").cum_sum().alias("grp"))
            )
            dd_only = dfpl.filter(pl.col("is_dd"))
            if dd_only.height == 0:
                out[col] = pd.DataFrame()
                continue
            blocks = (
                dd_only
                .group_by("grp")
                .agg([
                    pl.col("date").first().alias("Started"),
                    pl.col("date").last().alias("EndBlock"),
                    pl.col("date").sort_by(pl.col("dd")).first().alias("Trough"),
                    pl.col("dd").min().alias("min_dd"),
                    pl.count().alias("Days"),
                ])
                .sort("min_dd")
            )
            zeros = (
                dfpl
                .filter(pl.col("dd") >= -1e-12)
                .select([pl.col("date").alias("join_key"), pl.col("date").alias("Recovered")])
                .sort("join_key")
            )
            joined = (
                blocks
                .with_columns(pl.col("EndBlock").alias("join_key"))
                .sort("join_key")
                .join_asof(zeros, on="join_key", strategy="forward")
            )
            pdf = (
                joined
                .select([
                    pl.col("Started"),
                    pl.col("Recovered"),
                    (pl.col("min_dd") * 100.0).alias("Drawdown"),
                    pl.col("Days"),
                ])
                .head(10)
                .to_pandas()
            )
            def _fmt_date_left(x):
                if pd.isna(x): return "-"
                d = pd.to_datetime(x)
                return f"<span style='display:block;text-align:left'>{d.strftime('%Y-%m-%d')}</span>"

            if "Recovered" in pdf.columns:
                pdf["Recovered"] = pdf["Recovered"].map(_fmt_date_left)

            new_cols = []
            for c in pdf.columns:
                if c == "Recovered":
                    new_cols.append("<span style='display:block;text-align:left'>Recovered</span>")
                else:
                    new_cols.append(c)
            pdf.columns = new_cols
            out[col] = pdf
        return out

    # -----------------------
    # Figures
    # -----------------------
    def _build_figures(self) -> None:
        self.fig_paths: Dict[str, Dict[str, str]] = {col: {} for col in self.render_strategies}
        bench = self.benchmark_excess  # may be None

        def _save(fig, fname: str):
            if fig is None:
                return
            p = os.path.join(self.fig_dir, fname)
            fig.savefig(p, dpi=144, bbox_inches="tight")
            try:
                plt.close(fig)
            except Exception:
                pass
            return p

        # default QS figures per strategy
        for col in self.render_strategies:
            s = self.returns_excess[col].dropna()
            if s.empty:
                continue
            for f in self.fig_list:
                fig_obj = None
                try:
                    if f == "snapshot":
                        fig_obj = qs_plots.snapshot(s, show=False)
                    elif f == "earnings":
                        fig_obj = qs_plots.earnings(s, show=False)
                    elif f == "returns":
                        fig_obj = qs_plots.returns(s, benchmark=bench, show=False)
                    elif f == "log_returns":
                        fig_obj = qs_plots.log_returns(s, benchmark=bench, show=False)
                    elif f == "yearly_returns":
                        fig_obj = qs_plots.yearly_returns(s, benchmark=bench, show=False)
                    elif f == "daily_returns":
                        fig_obj = qs_plots.daily_returns(s, benchmark=bench, show=False)
                    elif f == "rolling_beta":
                        if bench is not None:
                            fig_obj = qs_plots.rolling_beta(s, bench, show=False)
                    elif f == "rolling_volatility":
                        try:
                            fig_obj = qs_plots.rolling_volatility(s, benchmark=bench, show=False)
                        except TypeError:
                            fig_obj = qs_plots.rolling_volatility(s, show=False)
                    elif f == "rolling_sharpe":
                        fig_obj = qs_plots.rolling_sharpe(s, show=False)
                    elif f == "rolling_sortino":
                        fig_obj = qs_plots.rolling_sortino(s, show=False)
                    elif f == "drawdowns_periods":
                        fig_obj = qs_plots.drawdowns_periods(s, show=False)
                    elif f == "drawdown":
                        fig_obj = qs_plots.drawdown(s, show=False)
                    elif f == "monthly_heatmap":
                        if bench is not None:
                            try:
                                fig_obj = qs_plots.monthly_heatmap(s, benchmark=bench, show=False)
                            except TypeError:
                                fig_obj = qs_plots.monthly_heatmap(s, show=False)
                        else:
                            fig_obj = qs_plots.monthly_heatmap(s, show=False)
                    elif f == "histogram":
                        fig_obj = qs_plots.histogram(s, benchmark=bench, show=False)
                    elif f == "distribution":
                        fig_obj = qs_plots.distribution(s, show=False)
                    else:
                        continue
                    if fig_obj is not None:
                        fp = _save(fig_obj, f"{f}_{col}.png")
                        if fp:
                            self.fig_paths[col][f] = fp
                except Exception as e:
                    print(f"[plot] failed: {f}({col}) -> {e}")

        # custom figures
        self.custom_fig_paths: Dict[str, List[Tuple[str, str]]] = {}  # key -> list of (label, path)
        for cf in self.custom_figs:
            tiles: List[Tuple[str, str]] = []
            try:
                if cf.per_strategy:
                    for col in self.render_strategies:
                        s = self.returns_excess[col].dropna()
                        if s.empty: continue
                        fig = cf.builder(s, self.benchmark_excess)
                        if fig is None: continue
                        fp = _save(fig, f"custom_{cf.key}_{col}.png")
                        if fp: tiles.append((f"{cf.title} — {col}", fp))
                else:
                    fig = cf.builder(self.returns_excess[self.render_strategies], self.benchmark_excess)
                    if fig is not None:
                        fp = _save(fig, f"custom_{cf.key}.png")
                        if fp: tiles.append((cf.title, fp))
            except Exception as e:
                print(f"[custom figure] {cf.key} failed: {e}")
            self.custom_fig_paths[cf.key] = tiles

    # -----------------------
    # Tables (metrics + others) + HTML fragments
    # -----------------------
    def _build_tables(self) -> None:
        # Metrics (raw -> display labels)
        full_m = self._compute_metrics_table(full=True)

        # Column filter
        if self.metric_cols_filter:
            keep_cols = [c for c in self.metric_cols_filter if c in full_m.columns]
        else:
            keep_cols = [c for c in self.default_metric_cols if c in full_m.columns]
        keep_cols = _unique(keep_cols)
        if keep_cols:
            metrics_df = full_m[keep_cols]
        else:
            metrics_df = full_m

        # Ensure Benchmark first
        cols = list(metrics_df.columns)
        if "Benchmark" in cols:
            cols = ["Benchmark"] + [c for c in cols if c != "Benchmark"]
            metrics_df = metrics_df[cols]

        self.metrics_df_raw = metrics_df.copy()

        # Optional row filter (by display names)
        if self.manifest.metric_rows:
            idx_map = {self._norm_key(i): i for i in self.metrics_df_raw.index}
            want = [idx_map[self._norm_key(k)] for k in self.manifest.metric_rows if self._norm_key(k) in idx_map]
            if want:
                self.metrics_df_raw = self.metrics_df_raw.loc[want]

        # --- NEW: Enforce strict metric_groups (your groups are the SOURCE OF TRUTH)
        def _flatten_groups(grps: List[Dict[str, List[str]]]) -> List[str]:
            out = []
            for g in grps or []:
                (_, keys) = next(iter(g.items()))
                out.extend(keys or [])
            return out

        if self.metric_groups:
            group_labels = _flatten_groups(self.metric_groups)
            if self.strict_groups:
                # keep only labels you listed in groups (order within groups handled in renderer)
                index_norm_to_label = {self._norm_key(lbl): lbl for lbl in self.metrics_df_raw.index}
                keep_norm = [self._norm_key(lbl) for lbl in group_labels]
                keep_actual = [index_norm_to_label[nk] for nk in keep_norm if nk in index_norm_to_label]
                if keep_actual:
                    self.metrics_df_raw = self.metrics_df_raw.loc[_unique(keep_actual)]

        # Pretty grouped metrics HTML (2dp + %)
        self.metrics_html = self._render_metrics_grouped(self.metrics_df_raw, self.metric_groups)

        # EOY
        self.eoy_map = self._eoy_table()
        # Monthly
        self.monthly_map = self._monthly_tables()
        # Drawdowns
        self.dd_map = self._drawdown_tables()

        # Custom tables (precompute)
        self.custom_tables_html: List[Tuple[str, str, bool]] = []  # (title, html, controlled)
        for ct in self.custom_tables:
            try:
                pdf = ct.builder(self.returns_excess, self.benchmark_excess)
                if not isinstance(pdf, pd.DataFrame):
                    pdf = pd.DataFrame(pdf)
                # format 2dp for custom tables (no percent inference here)
                pdf2 = pdf.copy()
                for c in pdf2.columns:
                    pdf2[c] = pdf2[c].map(
                        lambda v: "-" if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v)))
                                else (f"{float(v):.2f}" if isinstance(v, (int, float, np.floating)) else v)
                    )
                html = pdf2.to_html(border=0, escape=False, index=True)
                self.custom_tables_html.append((ct.title, html, ct.controlled))
            except Exception as e:
                print(f"Custom table failed ({ct.key}): {e}")

    def _render_metrics_grouped(self, df: pd.DataFrame, groups: List[Dict[str, List[str]]]) -> str:
        if df is None or df.empty:
            return "<div style='color:#888;'>No metrics.</div>"

        pretty = self._format_df_2dp(df)  # 2dp + % applied
        cols = list(pretty.columns)
        # maps normalized label -> actual label present in df
        idx_labels = {self._norm_key(lbl): lbl for lbl in pretty.index}

        html = []
        html.append('<table class="metrics-grouped">')
        html.append('<thead><tr>')
        html.append('<th class="sticky-col">Metric</th>')
        for c in cols:
            html.append(f'<th>{c}</th>')
        html.append('</tr></thead><tbody>')

        used: set[str] = set()
        first_group = True

        # Render ONLY what is requested in groups (when strict_groups=True)
        for grp in groups or []:
            (gname, keys) = next(iter(grp.items()))
            # add separator between groups
            if not first_group:
                html.append(f'<tr class="sep"><td colspan="{len(cols)+1}"></td></tr>')
            first_group = False
            # group title
            html.append(f'<tr class="glabel"><td class="gtitle sticky-col" colspan="{len(cols)+1}">{gname}</td></tr>')

            for key in (keys or []):
                nk = self._norm_key(key)
                if nk not in idx_labels:
                    # skip unknown/missing labels silently
                    continue
                label = idx_labels[nk]
                if label in used:
                    # avoid duplicates if label appears in multiple groups
                    continue
                used.add(label)
                row = pretty.loc[label]
                html.append('<tr>')
                html.append(f'<td class="mname sticky-col">{label}</td>')
                for c in cols:
                    html.append(f'<td class="mval">{str(row.get(c, "-"))}</td>')
                html.append('</tr>')

        # If STRICT, do NOT append leftovers at all
        if not self.strict_groups:
            leftovers = [lbl for lbl in pretty.index if lbl not in used]
            if leftovers:
                html.append(f'<tr class="sep"><td colspan="{len(cols)+1}"></td></tr>')
                html.append(f'<tr class="glabel"><td class="gtitle sticky-col" colspan="{len(cols)+1}">Other</td></tr>')
                for label in leftovers:
                    row = pretty.loc[label]
                    html.append('<tr>')
                    html.append(f'<td class="mname sticky-col">{label}</td>')
                    for c in cols:
                        html.append(f'<td class="mval">{str(row.get(c, "-"))}</td>')
                    html.append('</tr>')

        html.append('</tbody></table>')
        return "".join(html)

    # -----------------------
    # HTML writer
    # -----------------------
    def _write_html(self) -> None:
        # Initial left/right split based on # of strategies (cap left at 75%)
        n = max(1, len(self.render_strategies))
        left_pct = min(round(min(n, 3) * (100.0 / 3.0), 2), 75.0)
        right_pct = round(100.0 - left_pct, 2)

        # ---------- FIGURES HTML ----------
        fig_rows_html = []
        # Default QS figures
        for f in self.fig_list:
            tiles, have = [], 0
            for col in self.render_strategies:
                p = self.fig_paths.get(col, {}).get(f)
                if p and os.path.isfile(p):
                    have += 1
                    tiles.append(
                        f"""<div class="thumb">
                            <div class="fig-header">{f.replace('_',' ').title()} — {col}</div>
                            <img src="{os.path.relpath(p, self.output_dir)}" alt="{f} - {col}" data-zoom="1"/>
                        </div>"""
                    )
            if have == 0:
                continue
            fig_rows_html.append(f"""
                <div class="fig-row">
                    <div class="fig-title">{f.replace('_',' ').title()}</div>
                    <div class="fig-grid" style="grid-template-columns: repeat({have}, 1fr);">
                        {''.join(tiles)}
                    </div>
                </div>
            """)

        # Custom figures (pad single global tile so it occupies one column width)
        for key, tiles in self.custom_fig_paths.items():
            if not tiles:
                continue

            # If we have only one tile (global), make grid as wide as #strategies and pad with hidden placeholders
            total_cols = len(self.render_strategies) if len(tiles) == 1 else len(tiles)

            blocks = []
            if len(tiles) == 1 and total_cols > 1:
                label, path = tiles[0]
                blocks.append(
                    f"""<div class="thumb">
                        <div class="fig-header">{label}</div>
                        <img src="{os.path.relpath(path, self.output_dir)}" alt="{label}" data-zoom="1"/>
                    </div>"""
                )
                for _ in range(total_cols - 1):
                    blocks.append('<div class="thumb placeholder"></div>')
            else:
                for (label, path) in tiles:
                    blocks.append(
                        f"""<div class="thumb">
                            <div class="fig-header">{label}</div>
                            <img src="{os.path.relpath(path, self.output_dir)}" alt="{label}" data-zoom="1"/>
                            </div>"""
                    )

            fig_rows_html.append(f"""
                <div class="fig-row">
                    <div class="fig-title">Custom — {key}</div>
                    <div class="fig-grid" style="grid-template-columns: repeat({total_cols}, 1fr);">
                        {''.join(blocks)}
                    </div>
                </div>
            """)

        figures_html = "\n".join(fig_rows_html) if fig_rows_html else "<div style='padding:12px;color:#888;'>No figures generated.</div>"

        # ---------- TABLES HTML ----------
        def _as_pct(df: pd.DataFrame, sig: int = 2) -> pd.DataFrame:
            if df is None or df.empty:
                return pd.DataFrame()
            d = df.copy()
            def fmt(x):
                if pd.isna(x): return "-"
                if isinstance(x, (int, float, np.floating)): return f"{x*100.0:.{sig}f}%"
                return str(x)
            try:
                return d.map(fmt)
            except Exception:
                return d.applymap(fmt)

        blocks = []

        # Metrics (grouped, already pretty)
        if "metrics" in self.tables_list:
            blocks.append(f"""
            <div class="table-block" data-table="metrics" data-group="{'controlled' if 'metrics' in self.tables_controlled else 'free'}">
                <h3>Key Performance Metrics</h3>
                {self.metrics_html}
            </div>
            """)

        # EOY tables
        if "eoy" in self.tables_list and getattr(self, "eoy_map", None):
            for col, df in self.eoy_map.items():
                if df is None or df.empty or (col not in self.render_strategies):
                    continue
                disp = df.copy()
                if "Benchmark" in disp.columns: disp["Benchmark"] = disp["Benchmark"].map(lambda v: "-" if pd.isna(v) else f"{v*100:.2f}%")
                if "Strategy" in disp.columns: disp["Strategy"] = disp["Strategy"].map(lambda v: "-" if pd.isna(v) else f"{v*100:.2f}%")
                if "Multiplier" in disp.columns: disp["Multiplier"] = disp["Multiplier"].map(lambda v: "-" if pd.isna(v) else f"{v:.2f}x")
                eoy_html = disp.to_html(border=0, escape=False, index=False)
                blocks.append(f"""
                <div class="table-block" data-table="eoy" data-group="{'controlled' if 'eoy' in self.tables_controlled else 'free'}">
                    <h3>End of Year — {col}</h3>
                    {eoy_html}
                </div>
                """)

        # Monthly Returns
        if "monthly_returns" in self.tables_list and getattr(self, "monthly_map", None):
            for col in self.render_strategies:
                m = self.monthly_map.get(col, pd.DataFrame())
                if m is None or m.empty:
                    continue
                m_disp = _as_pct(m, sig=2).to_html(border=0, escape=False)
                blocks.append(f"""
                <div class="table-block" data-table="monthly_returns" data-group="{'controlled' if 'monthly_returns' in self.tables_controlled else 'free'}">
                    <h3>Monthly Returns — {col}</h3>
                    {m_disp}
                </div>
                """)

        # Drawdown details
        if "drawdown_details" in self.tables_list and getattr(self, "dd_map", None):
            for col in self.render_strategies:
                ddf = self.dd_map.get(col, pd.DataFrame())
                if ddf is None or ddf.empty:
                    continue
                ddisp = ddf.copy()
                if "Drawdown" in ddisp.columns:
                    ddisp["Drawdown"] = ddisp["Drawdown"].map(lambda v: f"{v:.2f}%" if isinstance(v, (int, float, np.floating)) else v)
                dd_html = ddisp.to_html(border=0, escape=False, index=False)
                blocks.append(f"""
                <div class="table-block" data-table="drawdown_details" data-group="{'controlled' if 'drawdown_details' in self.tables_controlled else 'free'}">
                    <h3>Worst 10 Drawdowns — {col}</h3>
                    {dd_html}
                </div>
                """)

        # Custom tables
        for (title, html_table, controlled) in self.custom_tables_html:
            blocks.append(f"""
            <div class="table-block" data-table="custom" data-group="{'controlled' if controlled else 'free'}">
                <h3>{title}</h3>
                {html_table}
            </div>
            """)

        tables_html = "\n".join(blocks) if blocks else "<div style='padding:12px;color:#888;'>No tables selected.</div>"

        # ---------- CSS (template replace to avoid f-string brace issues) ----------
        css_tpl = r"""
    <style>
    :root {
    --gutter: 10px;
    --left-col: __LEFT__;
    --right-col: __RIGHT__;
    --tables-w: 720px;           /* content width governed by handle */
    --handle-left: var(--tables-w);
    }
    * { box-sizing: border-box; }
    body { margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif; background:#fff; }

    .page { padding: 16px; }
    .titlebar { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }
    .titlebar h1 { margin:0; font-size:20px; }
    .titlebar .sub { color:#555; font-size:13px; }
    .meta { margin: 4px 0 0 0; color:#666; font-size:12px; }
    .meta-bench { margin: 4px 0 8px 0; color:#555; font-size:12px; }

    /* --- panes + splitters --- */
    .outer-split{display:grid;grid-template-columns:var(--left-col) var(--gutter) var(--right-col);width:100%;height:calc(100vh - 120px);min-height:540px}
    .left-pane,.right-pane{overflow:auto}

    /* Left gutter: invisible until hover anywhere on the split */
    .gutter{background:transparent;cursor:col-resize;width:var(--gutter);opacity:0;transition:opacity .12s ease}
    .outer-split:hover .gutter{opacity:.18}
    .gutter:hover{opacity:.28}

    /* Tables wrapper + right handle */
    .tables-wrap {
    position: relative;
    height: 100%;
    overflow: hidden;
    }
    .tables-content {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: calc(var(--tables-w) + 40px);   /* extra for padding so content never hides */
    overflow: auto;
    padding: 4px 28px 12px 10px;           /* RIGHT PADDING keeps content away from handle */
    background: transparent;
    }
    .right-handle {
    position: absolute;
    top: 0; bottom: 0;
    left: var(--handle-left);
    width: 8px;
    cursor: col-resize;
    background: transparent;
    z-index: 5;
    opacity: 0;                            /* invisible by default */
    transition: opacity .12s ease;
    pointer-events: none;                  /* off by default */
    }
    .tables-wrap:hover .right-handle {
    opacity: .18;                          /* subtle hint on hover */
    pointer-events: auto;
    }
    body.dragging-right .right-handle {
    background: rgba(0,0,0,0.06);
    opacity: .35;
    pointer-events: auto;
    }

    /* Figures */
    .fig-row { margin: 6px 8px 18px 2px; }
    .fig-title { font-size:14px; font-weight:600; margin: 4px 2px 8px 2px; color:#333; }
    .fig-grid {
    display: grid;
    gap: 10px;
    }
    .thumb {
    border: 1px solid #e4e4e4;
    border-radius: 6px;
    overflow: hidden;
    background:#fff;
    padding: 6px;
    }
    .thumb.placeholder { visibility: hidden; }   /* <--- added */
    .thumb .fig-header {
    font-size: 12px; font-weight: 600; margin: 0 0 6px 0; color:#333; text-align:left;
    }
    .thumb img { display:block; width:100%; height:auto; cursor: zoom-in; }

    /* Base table style: header shading only, single header row */
    .table-block { margin: 8px 4px 18px 4px; }
    .table-block h3 { font-size:14px; margin: 0 0 6px 0; color:#222; }
    .table-block table {
    border-collapse: collapse; background:#fff; width: auto; table-layout: auto; font-size:12px;
    }
    .table-block thead th {
    background:#f6f6f6; color:#333; padding: 6px 10px; border: none; text-align: right; font-weight:600;
    }
    .table-block thead th:first-child { text-align: left; }
    .table-block tbody td {
    padding: 6px 10px; border: none; text-align: right;
    }
    .table-block tbody td:first-child { text-align: left; }

    /* Grouped metrics table: sticky first column, distinct group title */
    .metrics-grouped {
    border-collapse: collapse; background:#fff; width: auto; table-layout: auto; font-size:12px;
    }
    .metrics-grouped thead th {
    background:#f6f6f6; font-weight:600; padding:6px 10px; border:none; text-align:right; font-size:12px;
    }
    .metrics-grouped thead th.sticky-col {
    text-align:left; position: sticky; left: 0; background:#f6f6f6; z-index:2;
    }
    .metrics-grouped tbody td { padding:6px 10px; border:none; font-size:12px; }
    .metrics-grouped td.mname.sticky-col {
    position: sticky; left: 0; background:#fff; z-index:1; color:#333; font-weight:500;
    }
    .metrics-grouped tr.sep td { border-bottom:1px solid #d0d0d0; height:6px; padding:0; }
    .metrics-grouped tr.glabel td.gtitle {
    color:#222; font-size:13px; font-weight:700; letter-spacing: .2px;
    padding: 6px 4px 4px 4px; border-top: 1px solid #ddd;
    }

    /* Controlled tables: width governed by --tables-w */
    .table-block[data-group="controlled"] table {
    width: var(--tables-w);
    white-space: nowrap;
    }

    /* Zoom modal */
    .modal {
    position: fixed; inset: 0; display:none; align-items:center; justify-content:center;
    background: rgba(0,0,0,0.76); z-index: 1000;
    }
    .modal img {
    max-width: 98vw; max-height: 96vh; display:block; box-shadow:0 10px 26px rgba(0,0,0,0.45); border-radius: 10px;
    }
    .modal.show { display:flex; }
    </style>
    """
        css = (css_tpl
            .replace("__LEFT__", f"{left_pct}%")
            .replace("__RIGHT__", f"{right_pct}%"))

        # ---------- JS ----------
        js = """
    <script>
    (function(){
    const root   = document.documentElement;
    const outer  = document.querySelector('.outer-split');
    const gutter = document.getElementById('left-gutter');
    const wrap   = document.getElementById('tables-wrap');
    const handle = document.getElementById('right-handle');

    function cssPx(name, fallback=0){
        const v = getComputedStyle(root).getPropertyValue(name).trim();
        if (!v) return fallback;
        return v.endsWith('px') ? parseFloat(v) : (parseFloat(v) || fallback);
    }
    function setVarPx(name, px){ root.style.setProperty(name, px + 'px'); }
    function setLeftRightPx(leftPx, rightPx){
        const total = leftPx + cssPx('--gutter',10) + rightPx;
        root.style.setProperty('--left-col',  (leftPx/total*100) + '%');
        root.style.setProperty('--right-col', (rightPx/total*100) + '%');
    }
    function clampTablesW(px){
        const r = wrap.getBoundingClientRect();
        const minW = 420;
        const maxW = Math.max(minW, r.width - 42);
        return Math.max(minW, Math.min(maxW, px));
    }
    function positionHandle(){
        const r  = wrap.getBoundingClientRect();
        const tw = cssPx('--tables-w', 720);
        const left = Math.max(0, Math.min(r.width - 8, tw));
        setVarPx('--handle-left', left);
    }
    function initTablesWidthToContent(){
        // choose the widest of controlled tables and set --tables-w
        let maxW = 480;
        document.querySelectorAll('.table-block[data-group="controlled"] table').forEach(t => {
        maxW = Math.max(maxW, t.scrollWidth + 12);
        });
        setVarPx('--tables-w', maxW);
        positionHandle();
    }

    // Left splitter drag
    let dragL=false;
    gutter.addEventListener('mousedown', e => { dragL=true; e.preventDefault(); document.body.style.userSelect='none'; });
    window.addEventListener('mousemove', e => {
        if (!dragL) return;
        const rect = outer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const minL = 260, maxL = rect.width - 360;
        const clamped = Math.max(minL, Math.min(maxL, x));
        const leftPx = clamped;
        const rightPx = rect.width - clamped - cssPx('--gutter',10);
        setLeftRightPx(leftPx, rightPx);
        positionHandle();
    });
    window.addEventListener('mouseup', () => { if (dragL){ dragL=false; document.body.style.userSelect=''; } });

    // Right handle (drag)
    let dragR=false;
    handle.addEventListener('mousedown', e => { dragR=true; e.preventDefault(); document.body.style.userSelect='none'; document.body.classList.add('dragging-right'); });
    window.addEventListener('mousemove', e => {
        if (!dragR) return;
        const r = wrap.getBoundingClientRect();
        let x = e.clientX - r.left;
        x = clampTablesW(x);
        setVarPx('--tables-w', x);
        positionHandle();
    });
    window.addEventListener('mouseup', () => { if (dragR){ dragR=false; document.body.style.userSelect=''; document.body.classList.remove('dragging-right'); } });

    // Init + resize
    window.addEventListener('load', () => { initTablesWidthToContent(); });
    window.addEventListener('resize', () => { positionHandle(); });

    // Zoom modal
    const modal = document.getElementById('zoom-modal');
    const modalImg = document.getElementById('zoom-image');
    document.querySelectorAll('img[data-zoom="1"]').forEach(img => {
        img.addEventListener('click', () => { modalImg.src = img.src; modal.classList.add('show'); });
    });
    modal.addEventListener('click', (e) => { if (e.target === modal || e.target.id === 'zoom-image') modal.classList.remove('show'); });
    window.addEventListener('keydown', (e) => { if (e.key === 'Escape') modal.classList.remove('show'); });
    })();
    </script>
    """

        bench_name = (self.benchmark.name if self.benchmark is not None and getattr(self.benchmark, "name", None) else "—")
        tz = datetime.now().astimezone().tzinfo
        generated_str = datetime.now().astimezone().strftime(f"%Y-%m-%d %H:%M:%S {tz}")

        html = f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <title>{self.title}</title>
    {css}
    </head>
    <body>
    <div class="page">
    <div class="titlebar">
        <h1>{self.title}</h1>
    </div>
    <div class="meta"> <strong>Benchmark: {bench_name}</strong> &nbsp;&nbsp; Sample Period: {self.date_range_str} &nbsp;&nbsp; Generated: {generated_str}</div>

    <div class="outer-split">
        <div class="left-pane">
        {figures_html}
        </div>
        <div class="gutter" id="left-gutter" title="Drag to resize"></div>
        <div class="right-pane">
        <div class="tables-wrap" id="tables-wrap">
            <div class="tables-content" id="tables-content">
            {tables_html}
            </div>
            <div class="right-handle" id="right-handle" title="Drag to resize"></div>
        </div>
        </div>
    </div>
    </div>

    <div class="modal" id="zoom-modal">
    <img id="zoom-image" src="" alt="Zoom"/>
    </div>

    {js}
    </body>
    </html>
    """
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Dashboard written to: {self.html_path}")