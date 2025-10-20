# metrics_pl3.py
# Thin, fast aggregator: single melt/cache/warm; builders return LONG frames; concat -> ONE pivot.

from __future__ import annotations
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Union, Iterable, List, Callable, Dict

import polars as pl


# =========================
# Utilities
# =========================

def _as_lazy(x: Union[pl.DataFrame, pl.LazyFrame]) -> pl.LazyFrame:
    return x.lazy() if isinstance(x, pl.DataFrame) else x

def _schema(lf: pl.LazyFrame):
    sch = lf.collect_schema()
    return sch.names(), sch.dtypes()

def _ensure_datetime_ns(lf: pl.LazyFrame, date_col: str = "date") -> pl.LazyFrame:
    # Ensure datetime type and cast to ns (robust for .dt ops)
    return lf.with_columns(pl.col(date_col).cast(pl.Datetime).dt.cast_time_unit("ns"))

def _to_long_num(df: pl.LazyFrame, cols: List[str]) -> pl.LazyFrame:
    # returns LONG: ["name","metric","value(Float64)"]
    cols = [c for c in cols if c != "name"]
    if not cols:
        return df.select(pl.lit(None).alias("value")).filter(pl.lit(False))
    return df.melt(id_vars="name", value_vars=cols, variable_name="metric", value_name="value")

def _to_long_str(df: pl.LazyFrame, cols: List[str]) -> pl.LazyFrame:
    # returns LONG: ["name","metric","value(Utf8)"]
    cols = [c for c in cols if c != "name"]
    if not cols:
        return df.select(pl.lit(None).alias("value")).filter(pl.lit(False))
    df2 = df.with_columns([pl.col(c).cast(pl.Utf8) for c in cols])
    return df2.melt(id_vars="name", value_vars=cols, variable_name="metric", value_name="value")


# =========================
# Tiny custom-metric registry (numeric only)
# =========================
Expr1 = Callable[[pl.Expr], pl.Expr]             # lambda r: ...
Expr2 = Callable[[pl.Expr, pl.Expr], pl.Expr]    # lambda r, b: ...

class SimpleRegistry:
    """Register easy numeric metrics as Polars Expr lambdas."""
    def __init__(self) -> None:
        self.num1: List[tuple[str, Expr1]] = []  # (name, fn(r))
        self.num2: List[tuple[str, Expr2]] = []  # (name, fn(r,b))

    def register(self, fn: Callable[..., pl.Expr], *, name: Optional[str] = None) -> "SimpleRegistry":
        try:
            ar = fn.__code__.co_argcount
        except Exception:
            ar = 1
        nm = name or getattr(fn, "__name__", None) or f"metric_{len(self.num1)+len(self.num2)}"
        if ar == 1:
            self.num1.append((nm, fn))     # type: ignore[arg-type]
        elif ar == 2:
            self.num2.append((nm, fn))     # type: ignore[arg-type]
        else:
            raise ValueError("Custom metric must be unary (r) or binary (r, b).")
        return self

    def register_map(self, m: Dict[str, Callable[..., pl.Expr]]) -> "SimpleRegistry":
        for k, v in m.items():
            self.register(v, name=k)
        return self

    def empty(self) -> bool:
        return not (self.num1 or self.num2)


# =========================
# THIN, FAST AGGREGATOR (no metric math here)
# =========================
def metrics_polars(
    returns: Union[pl.DataFrame, pl.LazyFrame],
    benchmark: Optional[Union[pl.DataFrame, pl.LazyFrame]] = None,
    *,
    rf: float = 0.0,
    periods_per_year: int = 252,
    dd_batch: int = 512,
    # kept for back-compat with callers — not used here
    mode: str = "full",
    return_long: bool = False,
    builders_num: Optional[Iterable[Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]]] = None,
    builders_str: Optional[Iterable[Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]]] = None,
    registry: Optional[SimpleRegistry] = None,
) -> pl.DataFrame:
    """
    Build the FULL metrics table by concatenating LONG frames from builders, then pivoting once.
    - Accepts an optional `registry` of custom numeric metrics (unary/binary Polars Expr).
    - Robust to accidental duplicates by using `aggregate_function="first"` in pivots.
    """
    # 0) wide -> lazy + ns date
    R = _ensure_datetime_ns(_as_lazy(returns))
    if isinstance(returns, pl.DataFrame):
        ret_cols = [c for c in returns.columns if c != "date"]
    else:
        ret_cols = [c for c in _schema(R)[0] if c != "date"]

    # 1) optional benchmark appended as first column
    B_series: Optional[pl.LazyFrame] = None
    bcol: Optional[str] = None
    if benchmark is not None:
        B = _ensure_datetime_ns(_as_lazy(benchmark))
        bn, _ = _schema(B)
        bnames = [c for c in bn if c != "date"]
        if len(bnames) != 1:
            raise ValueError(f"Benchmark must have exactly one non-'date' column; found {bnames}")
        bcol = bnames[0]
        B_series = B.select(pl.col("date"), pl.col(bcol).alias("b"))
        R = R.join(B_series.select(["date", pl.col("b").alias(bcol)]), on="date", how="left")
        ret_cols = [bcol] + [c for c in ret_cols if c != bcol]

    # 2) melt once & cache
    Rc = (
        R.melt(id_vars=["date"], value_vars=ret_cols, variable_name="name", value_name="r")
         .with_columns([
             (pl.col("r") - rf).alias("r") if rf else pl.col("r"),
             pl.col("name").cast(pl.Categorical()),
         ])
         .cache()
    )
    last_date = Rc.select(pl.max("date").alias("last")).collect()["last"][0]

    # 3) ctx for builders
    ctx = {
        "ppy": periods_per_year,
        "rf": rf,
        "dd_batch": dd_batch,
        "last_date": last_date,
        "ret_cols": ret_cols,
    }

    # 4) run builders -> LONG parts
    num_parts: List[pl.LazyFrame] = []
    str_parts: List[pl.LazyFrame] = []

    # Always start from the module-level defaults unless the caller provided builders
    if builders_num is None and builders_str is None:
        builders_num, builders_str = _DEFAULT_NUM, _DEFAULT_STR

    if builders_num:
        for build in builders_num:
            num_parts.append(build(Rc, B_series, ctx))

    # IMPORTANT: add registry ONLY ONCE here (do NOT also add it inside default pack)
    if registry and (registry.num1 or (registry.num2 and B_series is not None)):
        num_parts.append(expr_long_block(registry)(Rc, B_series, ctx))

    if builders_str:
        for build in builders_str:
            str_parts.append(build(Rc, B_series, ctx))

    if not num_parts and not str_parts:
        return pl.DataFrame({"metric": []})

    # 5) pivot numeric once (be robust to accidental duplicates)
    wide_parts: List[pl.DataFrame] = []
    if num_parts:
        long_num = pl.concat(num_parts).with_columns(pl.col("name").cast(pl.Utf8))
        wide_num = (
            long_num
            .collect()
            .pivot(values="value", index="metric", on="name", aggregate_function="first")
        )
        # cast numeric to Utf8 to permit diagonal concat with string block
        wide_num = wide_num.with_columns([pl.col(c).cast(pl.Utf8) for c in wide_num.columns if c != "metric"])
        wide_parts.append(wide_num)

    # 6) pivot string once (also robust)
    if str_parts:
        long_str = pl.concat(str_parts).with_columns(pl.col("name").cast(pl.Utf8))
        wide_str = (
            long_str
            .collect()
            .pivot(values="value", index="metric", on="name", aggregate_function="first")
        )
        wide_parts.append(wide_str)

    if not wide_parts:
        return pl.DataFrame({"metric": []})

    # 7) assemble diagonally (row-union), benchmark first if present
    wide = pl.concat(wide_parts, how="diagonal")

    if bcol and bcol in wide.columns:
        wide = wide.select(["metric", bcol] + [c for c in wide.columns if c not in ("metric", bcol)])

    if return_long:
        return (
            wide.melt(id_vars="metric", variable_name="name", value_name="value")
                .filter(pl.col("name") != "metric")
                .select(["name","metric","value"])
                .sort(["metric","name"])
        )

    return wide.sort("metric")


# ============================================================
# EXTERNAL BUILDERS (return LONG frames)
# ============================================================

def base_long() -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        ppy = ctx["ppy"]
        base = (
            Rc.group_by("name").agg([
                ((1.0 + pl.col("r")).product() - 1.0).alias("comp"),
                pl.count().alias("_n"),
                pl.col("r").mean().alias("_mu"),
                pl.col("r").std(ddof=1).alias("_sd"),
                (pl.col("r").clip(upper_bound=0.0) ** 2).mean().sqrt().alias("_lpsd"),
                (pl.col("r") != 0).sum().alias("_nz"),
                pl.col("r").filter(pl.col("r") > 0).mean().alias("avg_win"),
                pl.col("r").filter(pl.col("r") < 0).mean().alias("avg_loss"),
                pl.col("r").max().alias("best_day"),
                pl.col("r").min().alias("worst_day"),
                pl.col("r").skew().alias("skew"),
                pl.col("r").kurtosis().alias("kurtosis"),
                ((pl.col("r") > 0).sum() / pl.count()).alias("win_rate"),
            ])
            .with_columns([
                ((1.0 + pl.col("comp")) ** (pl.lit(ppy) / pl.col("_n")) - 1.0).alias("cagr"),
                pl.when(pl.col("_sd") == 0).then(pl.lit(float("nan")))
                  .otherwise(pl.col("_mu") / pl.col("_sd") * math.sqrt(ppy)).alias("sharpe"),
                pl.when(pl.col("_lpsd") == 0).then(pl.lit(float("nan")))
                  .otherwise(pl.col("_mu") / pl.col("_lpsd") * math.sqrt(ppy)).alias("sortino"),
                (pl.col("_sd") * math.sqrt(ppy)).alias("vol_ann"),
                (pl.col("_nz") / pl.col("_n")).alias("exposure"),
                (pl.col("avg_win") / (-pl.col("avg_loss"))).alias("payoff"),
            ])
            .select(["name","comp","cagr","sharpe","sortino","vol_ann","exposure",
                     "avg_win","avg_loss","payoff","best_day","worst_day","skew","kurtosis","win_rate"])
        )
        return _to_long_num(base, [c for c in base.collect_schema().names() if c != "name"])
    return _block


def drawdowns_num_long(dd_batch: Optional[int] = None) -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """Numeric DD metrics only: max_drawdown, avg_drawdown, ulcer, longest_dd_days, avg_dd_days."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        batch = dd_batch or ctx["dd_batch"]
        names_list: List[str] = ctx["ret_cols"]
        long_parts: List[pl.LazyFrame] = []

        for i in range(0, len(names_list), max(1, batch)):
            chunk = names_list[i:i+batch]
            sub = Rc.filter(pl.col("name").is_in(chunk))
            seq = (
                sub
                .with_columns(((1.0 + pl.col("r")).cum_prod().over("name")).alias("eq"))
                .with_columns((pl.col("eq").cum_max().over("name")).alias("peak"))
                .with_columns(((pl.col("eq") / pl.col("peak")) - 1.0).clip(upper_bound=0.0).alias("dd"))
                .with_columns((pl.col("dd") < 0).alias("_in"))
                .with_columns(
                    pl.when(pl.col("_in") & (~pl.col("_in").shift(1).over("name").fill_null(False)))
                      .then(1).otherwise(0).cast(pl.Int64).alias("_start")
                )
                .with_columns(pl.col("_start").cum_sum().over("name").alias("grp"))
            )

            # ulcer (numeric)
            ulcer = seq.group_by("name").agg(((pl.col("dd") ** 2).mean()).sqrt().alias("ulcer"))

            # episode metrics (numeric)
            ep_rows = seq.filter(pl.col("_in"))
            episodes = ep_rows.group_by(["name","grp"]).agg([
                pl.first("date").alias("start"),
                pl.last("date").alias("end"),
                pl.min("dd").alias("min_dd"),
            ])
            ep_num = episodes.with_columns(
                (pl.col("end").cast(pl.Date) - pl.col("start").cast(pl.Date)).dt.total_days().add(1).alias("days")
            )
            dd_chunk = ep_num.group_by("name").agg([
                (-pl.col("min_dd").min()).alias("max_drawdown"),
                (-pl.col("min_dd").mean()).alias("avg_drawdown"),
                pl.col("days").max().alias("longest_dd_days"),
                pl.col("days").mean().round(0).alias("avg_dd_days"),
            ])

            wide_num = dd_chunk.join(ulcer, on="name", how="left")
            long_parts.append(_to_long_num(wide_num, [c for c in wide_num.collect_schema().names() if c != "name"]))

        return pl.concat(long_parts) if long_parts else Rc.select(pl.lit(None).alias("value")).filter(pl.lit(False))
    return _block


def drawdown_dates_long(dd_batch: Optional[int] = None) -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """String DD labels only: max_dd_date, max_dd_start, max_dd_end."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        batch = dd_batch or ctx["dd_batch"]
        names_list: List[str] = ctx["ret_cols"]
        long_parts: List[pl.LazyFrame] = []

        for i in range(0, len(names_list), max(1, batch)):
            chunk = names_list[i:i+batch]
            sub = Rc.filter(pl.col("name").is_in(chunk))
            seq = (
                sub
                .with_columns(((1.0 + pl.col("r")).cum_prod().over("name")).alias("eq"))
                .with_columns((pl.col("eq").cum_max().over("name")).alias("peak"))
                .with_columns(((pl.col("eq") / pl.col("peak")) - 1.0).clip(upper_bound=0.0).alias("dd"))
                .with_columns((pl.col("dd") < 0).alias("_in"))
                .with_columns(
                    pl.when(pl.col("_in") & (~pl.col("_in").shift(1).over("name").fill_null(False)))
                      .then(1).otherwise(0).cast(pl.Int64).alias("_start")
                )
                .with_columns(pl.col("_start").cum_sum().over("name").alias("grp"))
            )

            ep_rows = seq.filter(pl.col("_in"))
            episodes = ep_rows.group_by(["name","grp"]).agg([
                pl.first("date").alias("start"),
                pl.last("date").alias("end"),
                pl.min("dd").alias("min_dd"),
                pl.col("date").sort_by(pl.col("dd")).first().alias("valley"),
            ])

            worst_dates = episodes.group_by("name").agg([
                pl.col("valley").sort_by(pl.col("min_dd")).first().dt.strftime("%Y-%m-%d").alias("max_dd_date"),
                pl.col("start").sort_by(pl.col("min_dd")).first().dt.strftime("%Y-%m-%d").alias("max_dd_start"),
                pl.col("end").sort_by(pl.col("min_dd")).first().dt.strftime("%Y-%m-%d").alias("max_dd_end"),
            ])

            long_parts.append(_to_long_str(worst_dates, ["max_dd_date","max_dd_start","max_dd_end"]))

        return pl.concat(long_parts) if long_parts else Rc.select(pl.lit(None).alias("value")).filter(pl.lit(False))
    return _block


def calmar_long() -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """Calmar (numeric)."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        ppy = ctx["ppy"]
        cagr = (
            Rc.group_by("name").agg([
                ((1.0 + pl.col("r")).product() - 1.0).alias("_comp"),
                pl.count().alias("_n"),
            ])
            .with_columns(((1.0 + pl.col("_comp")) ** (pl.lit(ppy) / pl.col("_n")) - 1.0).alias("cagr"))
            .select(["name","cagr"])
        )
        seq = (
            Rc.with_columns(((1.0 + pl.col("r")).cum_prod().over("name")).alias("eq"))
              .with_columns((pl.col("eq").cum_max().over("name")).alias("peak"))
              .with_columns(((pl.col("eq") / pl.col("peak")) - 1.0).clip(upper_bound=0.0).alias("dd"))
        )
        dd = seq.group_by("name").agg((-pl.col("dd").min()).alias("max_drawdown"))
        cal = (
            dd.join(cagr, on="name", how="inner")
              .with_columns(
                  pl.when(pl.col("max_drawdown") <= 0).then(pl.lit(float("nan")))
                   .otherwise(pl.col("cagr") / pl.col("max_drawdown")).alias("calmar")
              )
              .select(["name","calmar"])
        )
        return _to_long_num(cal, ["calmar"])
    return _block


def extremes_long() -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """Best/worst month & year (numeric)."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        monthly_agg = (
            Rc.with_columns([pl.col("date").dt.year().alias("_y"), pl.col("date").dt.month().alias("_m")])
              .group_by(["name","_y","_m"])
              .agg(((1.0 + pl.col("r")).product() - 1.0).alias("rm"))
        )
        monthly = monthly_agg.group_by("name").agg([
            pl.col("rm").max().alias("best_month"),
            pl.col("rm").min().alias("worst_month"),
        ])
        yearly_agg = (
            Rc.with_columns(pl.col("date").dt.year().alias("_y"))
              .group_by(["name","_y"])
              .agg(((1.0 + pl.col("r")).product() - 1.0).alias("ry"))
        )
        yearly = yearly_agg.group_by("name").agg([
            pl.col("ry").max().alias("best_year"),
            pl.col("ry").min().alias("worst_year"),
        ])
        wide = monthly.join(yearly, on="name", how="left")
        return _to_long_num(wide, [c for c in wide.collect_schema().names() if c != "name"])
    return _block


def tails_long() -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """VaR_5, CVaR_5, Omega_0 (numeric)."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        var5 = Rc.group_by("name").agg(pl.col("r").quantile(0.05, "nearest").alias("VaR_5"))
        cvar5 = (
            Rc.join(var5, on="name", how="inner")
              .filter(pl.col("r") <= pl.col("VaR_5"))
              .group_by("name")
              .agg(pl.col("r").mean().alias("CVaR_5"))
        )
        omega = Rc.group_by("name").agg(
            (pl.col("r").clip(lower_bound=0.0).sum() / (-pl.col("r").clip(upper_bound=0.0).sum())).alias("omega_0")
        )
        wide = var5.join(cvar5, on="name", how="left").join(omega, on="name", how="left")
        return _to_long_num(wide, [c for c in wide.collect_schema().names() if c != "name"])
    return _block


def period_slices_long() -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """MTD, 3m, 6m, YTD, 1y, 3y_ann, 5y_ann, 10y_ann, alltime_ann (numeric)."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        ppy = ctx["ppy"]
        last_date: datetime = ctx["last_date"]

        def _since(start: datetime, out: str) -> pl.LazyFrame:
            return (Rc.filter(pl.col("date") >= pl.lit(start))
                       .group_by("name")
                       .agg(((1.0 + pl.col("r")).product() - 1.0).alias(out)))

        MTD = (
            Rc.with_columns([pl.col("date").dt.year().alias("_y"), pl.col("date").dt.month().alias("_m")])
              .filter((pl.col("_y") == last_date.year) & (pl.col("_m") == last_date.month))
              .group_by("name")
              .agg(((1.0 + pl.col("r")).product() - 1.0).alias("mtd"))
        )
        c3m  = _since(last_date - relativedelta(months=3),  "3m")
        c6m  = _since(last_date - relativedelta(months=6),  "6m")
        cytd = _since(datetime(last_date.year, 1, 1),       "ytd")
        c1y  = _since(last_date - relativedelta(years=1),   "1y")

        def _cagr_since(start: datetime, out: str) -> pl.LazyFrame:
            sub = Rc.filter(pl.col("date") >= pl.lit(start)).group_by("name").agg([
                ((1.0 + pl.col("r")).product() - 1.0).alias("_comp"),
                pl.count().alias("_n"),
            ])
            return sub.with_columns(((1.0 + pl.col("_comp")) ** (pl.lit(ppy)/pl.col("_n")) - 1.0).alias(out)).select(["name", out])

        a3y  = _cagr_since(last_date - relativedelta(years=3),  "3y_ann")
        a5y  = _cagr_since(last_date - relativedelta(years=5),  "5y_ann")
        a10y = _cagr_since(last_date - relativedelta(years=10), "10y_ann")
        allat = (
            Rc.group_by("name").agg([
                ((1.0 + pl.col("r")).product() - 1.0).alias("_comp"),
                pl.count().alias("_n"),
            ])
            .with_columns(((1.0 + pl.col("_comp")) ** (pl.lit(ppy)/pl.col("_n")) - 1.0).alias("alltime_ann"))
            .select(["name","alltime_ann"])
        )

        wide = (MTD
                .join(c3m,  on="name", how="left")
                .join(c6m,  on="name", how="left")
                .join(cytd, on="name", how="left")
                .join(c1y,  on="name", how="left")
                .join(a3y,  on="name", how="left")
                .join(a5y,  on="name", how="left")
                .join(a10y, on="name", how="left")
                .join(allat, on="name", how="left"))
        return _to_long_num(wide, [c for c in wide.collect_schema().names() if c != "name"])
    return _block


def expr_long_block(registry: SimpleRegistry) -> Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]:
    """Compile registered lambdas into one unary and one binary agg, then LONG-ify (numeric only)."""
    def _block(Rc: pl.LazyFrame, B: Optional[pl.LazyFrame], ctx: dict) -> pl.LazyFrame:
        parts: List[pl.LazyFrame] = []
        if registry.num1:
            wide1 = Rc.group_by("name").agg([fn(pl.col("r")).alias(nm) for nm, fn in registry.num1])
            parts.append(_to_long_num(wide1, [c for c in wide1.collect_schema().names() if c != "name"]))
        if registry.num2 and B is not None:
            Rcb = Rc.join(B, on="date", how="inner")
            wide2 = Rcb.group_by("name").agg([fn(pl.col("r"), pl.col("b")).alias(nm) for nm, fn in registry.num2])
            parts.append(_to_long_num(wide2, [c for c in wide2.collect_schema().names() if c != "name"]))
        return pl.concat(parts) if parts else Rc.select(pl.lit(None).alias("value")).filter(pl.lit(False))
    return _block


# =========================
# Convenience: default builders pack
# =========================
def build_default_builders(
    *, registry: Optional[SimpleRegistry] = None, dd_batch: int = 512
) -> tuple[list, list]:
    """Return (builders_num, builders_str)."""
    builders_num = [
        base_long(),
        drawdowns_num_long(dd_batch),
        calmar_long(),
        extremes_long(),
        tails_long(),
        period_slices_long(),
    ]
    if registry and not registry.empty():
        builders_num.append(expr_long_block(registry))

    builders_str = [
        drawdown_dates_long(dd_batch),  # DD dates split to preserve numeric schema
    ]
    return builders_num, builders_str


# --- module-level defaults the dashboard will use
_DEFAULT_NUM, _DEFAULT_STR = build_default_builders(dd_batch=512)


def set_default_builders(
    *,
    builders_num: Optional[Iterable[Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]]] = None,
    builders_str: Optional[Iterable[Callable[[pl.LazyFrame, Optional[pl.LazyFrame], dict], pl.LazyFrame]]] = None,
    registry: Optional[SimpleRegistry] = None,
    dd_batch: int = 512,
) -> None:
    """
    Configure the default builders used by metrics_polars() when none are passed explicitly.
    Call this once in your app before creating the dashboard.
    """
    global _DEFAULT_NUM, _DEFAULT_STR
    if registry is not None and (builders_num is None and builders_str is None):
        _DEFAULT_NUM, _DEFAULT_STR = build_default_builders(registry=registry, dd_batch=dd_batch)
        return
    _DEFAULT_NUM = list(builders_num) if builders_num is not None else _DEFAULT_NUM
    _DEFAULT_STR = list(builders_str) if builders_str is not None else _DEFAULT_STR