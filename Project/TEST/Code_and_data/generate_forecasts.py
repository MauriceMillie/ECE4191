#!/usr/bin/env python3
"""ECE4191 Extension 1: causal, all-node load/PV forecasting.

Place this file in the repository's Project/ directory.
Run: python generate_forecasts.py
Requires: Python >= 3.9, numpy. matplotlib is optional for --plots.

This module does NOT run a controller, connect to HIL, or write Modbus registers.
It uses the course's aggregated *kW* data, NOT unconverted household energy data.

Methods are transparent statistical baselines, NOT trained AI models:
  persistence : previous complete day's same half-hour value
  mean        : mean of up to `window` previous complete days
  weighted    : weighted mean, with newest-to-oldest weights 1, decay, decay**2,...

Time convention: forecasts are issued at 00:00 in the dataset's own clock, after
all of the preceding day is assumed available. A row's final 0:00 column means
24:00 at the end of that row's date. No timezone/DST conversion is performed.

IMPORTANT: concatenated day-ahead CSVs are for QP/evaluation. A rolling MPC must
use the issue-safe windows in mpc_forecast_windows.npz, not slice tomorrow's
newly-issued forecast before its issue time. The windows freeze the current
issue's profile and repeat it for a provisional second forecast day.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

STEPS = 48
PROFILES = ("GC_Load_kW", "PV_Generation_kW")
PHASES = {"A": "A", "B": "B", "C": "C", "Ph1": "A", "Ph2": "B", "Ph3": "C",
          "1": "A", "2": "B", "3": "C"}
COURSE_CUSTOMERS = {
    "646_B": 102, "645_B": 63, "611_C": 68, "652_A": 46,
    "671_A": 159, "671_B": 155, "671_C": 159,
    "692_C": 66, "692_B": 0, "692_A": 0,
    "675_C": 119, "675_B": 36, "675_A": 191,
    "634_C": 52, "634_B": 45, "634_A": 69,
}
TIME_LABELS = [f"{m // 60}:{m % 60:02d}" for m in range(30, 1440, 30)] + ["0:00"]
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


@dataclass
class CourseData:
    dates: list[date]
    groups: list[str]
    customers: np.ndarray
    # Axis order: date, node-phase, profile (load/PV), half-hour interval.
    values: np.ndarray
    source: Path


def parse_date(text: str) -> date:
    """Accept ISO YYYY-MM-DD or the course's D-Mon-YY, without locale dependence."""
    text = text.strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        match = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})-(\d{2}|\d{4})", text)
        if not match:
            raise ValueError(f"Invalid date {text!r}; use YYYY-MM-DD or D-Mon-YY.")
        day, mon, year = match.groups()
        try:
            month = [m.lower() for m in MONTHS].index(mon.lower()) + 1
        except ValueError as exc:
            raise ValueError(f"Invalid month in {text!r}.") from exc
        y = int(year)
        y = 2000 + y if len(year) == 2 else y
        return date(y, month, int(day))


def course_date(d: date) -> str:
    return f"{d.day}-{MONTHS[d.month - 1]}-{d.year % 100:02d}"


def time_columns(headers: Sequence[str]) -> list[str]:
    """Return columns in true interval-ending order, putting 0:00 LAST."""
    found: dict[int, str] = {}
    for field in headers:
        if not re.fullmatch(r"\d{1,2}:\d{2}", field):
            continue
        h, m = map(int, field.split(":"))
        if h > 24 or m >= 60 or (h == 24 and m != 0):
            raise ValueError(f"Invalid time column: {field!r}")
        minute = h * 60 + m
        minute = 1440 if minute == 0 else minute
        if minute not in range(30, 1441, 30) or minute in found:
            raise ValueError(f"Unexpected/duplicate half-hour column: {field!r}")
        found[minute] = field
    if set(found) != set(range(30, 1441, 30)):
        raise ValueError("Expected exactly 48 interval-ending columns: 0:30 ... 23:30, 0:00.")
    return [found[m] for m in range(30, 1441, 30)]


def read_course_csv(path: Path, require_course_nodes: bool = True) -> CourseData:
    """Strict loader: no silent imputation, duplicated rows, or future backfill."""
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Input not found: {path}\nSupply --input or place the course CSV in Code_and_data/.")
    rows: dict[tuple[date, str, str], np.ndarray] = {}
    counts: dict[str, int] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = [s.strip() for s in (reader.fieldnames or [])]
        reader.fieldnames = headers
        if len(headers) != len(set(headers)):
            raise ValueError("Duplicate CSV headers.")
        required = {"Date", "Node", "Phase", "N_Customers", "Profile"}
        if not required.issubset(headers):
            raise ValueError(
                "This script expects the course node-aggregated kW CSV with "
                "Date,Node,Phase,N_Customers,Profile. A RIS citation, a central-total "
                "CSV, or raw household data is not that input; household data needs "
                "documented node mapping and unit conversion first."
            )
        slots = time_columns(headers)
        for line, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"Line {line}: more data fields than headers.")
            try:
                d = parse_date(row["Date"])
                nf = float(row["Node"])
                cf = float(row["N_Customers"])
                if not nf.is_integer() or not cf.is_integer() or cf < 0:
                    raise ValueError("Node and N_Customers must be integers; count cannot be negative.")
                group = f"{int(nf)}_{PHASES[row['Phase'].strip()]}"
                profile = row["Profile"].strip()
                if profile not in PROFILES:
                    raise ValueError(f"Unexpected Profile {profile!r}.")
                value = np.array([float(row[c]) for c in slots], dtype=float)
                if not np.isfinite(value).all() or (value < 0).any():
                    raise ValueError("Missing, non-finite, or negative load/PV values; review the input.")
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"Line {line}: {exc}") from exc
            key = (d, group, profile)
            if key in rows:
                raise ValueError(f"Duplicate record: {key}")
            if group in counts and counts[group] != int(cf):
                raise ValueError(f"N_Customers changes for {group}; a time-varying mapping needs explicit handling.")
            if cf == 0 and np.any(value != 0):
                raise ValueError(f"{group} has zero customers but nonzero load/PV; check the node mapping.")
            counts[group] = int(cf)
            rows[key] = value
    if not rows:
        raise ValueError("Empty dataset.")
    dates = sorted({k[0] for k in rows})
    if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ValueError("Calendar days are missing. Do not silently treat a gap as yesterday.")
    if require_course_nodes and counts != COURSE_CUSTOMERS:
        raise ValueError(
            "Node-phase/customer mapping differs from the checked Module 3 mapping. "
            "Review it; use --allow-partial only for a documented subset/custom mapping. "
            f"Found {counts}"
        )
    groups = sorted(counts, key=lambda g: (int(g.split('_')[0]), g.split('_')[1]))
    values = np.empty((len(dates), len(groups), 2, STEPS), dtype=float)
    for di, d in enumerate(dates):
        for gi, group in enumerate(groups):
            for pi, profile in enumerate(PROFILES):
                key = (d, group, profile)
                if key not in rows:
                    raise ValueError(f"Missing record {key}; no implicit zero-fill is performed.")
                values[di, gi, pi] = rows[key]
    return CourseData(dates, groups, np.array([counts[g] for g in groups]), values, path)


def forecast_profile(history: np.ndarray, method: str = "persistence",
                     window: int = 3, decay: float = 0.5) -> np.ndarray:
    """Forecast a daily profile. Caller supplies PAST days only.

    history shape is (history_days, groups, 2, 48); result is (groups, 2, 48).
    Changing this function is the main place to implement another algorithm.
    """
    history = np.asarray(history, dtype=float)
    if history.ndim != 4 or history.shape[0] < 1 or history.shape[-2:] != (2, STEPS):
        raise ValueError("history must have shape (at least 1 day, groups, 2, 48).")
    if not np.isfinite(history).all() or (history < 0).any():
        raise ValueError("Invalid history values.")
    if window < 1 or not math.isfinite(decay) or not 0 < decay <= 1:
        raise ValueError("window >= 1 and 0 < decay <= 1 are required.")
    if method == "persistence":
        return history[-1].copy()
    recent = history[-window:]
    if method == "mean":
        return recent.mean(axis=0)
    if method == "weighted":
        # recent is oldest -> newest, so the newest value gets weight 1.
        weights = decay ** np.arange(len(recent) - 1, -1, -1, dtype=float)
        weights /= weights.sum()
        return np.tensordot(weights, recent, axes=(0, 0))
    raise ValueError(f"Unknown forecast method {method!r}.")


def predict_issue(data: CourseData, issue_index: int, method: str,
                  window: int, decay: float) -> np.ndarray:
    """At target-day midnight only Date < target-day enters the model."""
    if not 1 <= issue_index <= len(data.dates):
        raise ValueError("Need at least one previous complete day.")
    return forecast_profile(data.values[:issue_index], method, window, decay)


def write_csv(path: Path, header: Sequence[str], rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def write_node_profiles(path: Path, data: CourseData,
                        dates: list[date], values: np.ndarray) -> None:
    def rows():
        for di, d in enumerate(dates):
            for gi, group in enumerate(data.groups):
                node, phase = group.split("_")
                for pi, profile in enumerate(PROFILES):
                    yield [course_date(d), node, phase, int(data.customers[gi]), profile,
                           *values[di, gi, pi].tolist()]
    write_csv(path, ["Date", "Node", "Phase", "N_Customers", "Profile", *TIME_LABELS], rows())


def write_central_profiles(path: Path, dates: list[date], values: np.ndarray,
                           customers: int) -> None:
    # `values` is already the sum over groups: (days, profiles, half-hours).
    rows = ([course_date(d), customers, profile, *values[di, pi].tolist()]
            for di, d in enumerate(dates) for pi, profile in enumerate(PROFILES))
    write_csv(path, ["Date", "N_Customers", "Profile", *TIME_LABELS], rows)


def error_metrics(actual: np.ndarray, forecast: np.ndarray) -> dict:
    actual, forecast = np.asarray(actual).ravel(), np.asarray(forecast).ravel()
    if actual.shape != forecast.shape or len(actual) == 0:
        raise ValueError("Metrics need matching, nonempty arrays.")
    err = forecast - actual
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    mean_abs = float(np.mean(np.abs(actual)))
    return {"Samples": len(err), "MAE_kW": mae, "RMSE_kW": rmse,
            "Bias_kW": float(np.mean(err)),
            "NMAE_pct_mean_abs_actual": 100 * mae / mean_abs if mean_abs > 1e-12 else None,
            "NRMSE_pct_mean_abs_actual": 100 * rmse / mean_abs if mean_abs > 1e-12 else None}


def make_mpc_windows(dates: list[date], predicted: np.ndarray,
                     groups: list[str]) -> dict[str, np.ndarray]:
    """Issue-safe 48-step windows, updated daily, not intra-day.

    For each issued date, repeat THAT issue's daily forecast to 96 steps. At
    half-hour k, take k:k+48. Never use tomorrow's newer forecast early. The
    second-day repeat is an explicit baseline assumption, not an observation.
    """
    starts, issues, ends, node_load, node_pv = [], [], [], [], []
    for di, d in enumerate(dates):
        issue = np.datetime64(d.isoformat(), "m")
        version = np.tile(predicted[di], (1, 1, 2))
        for k in range(STEPS):
            start = issue + np.timedelta64(30 * k, "m")
            starts.append(start)
            issues.append(issue)
            ends.append(start + np.arange(1, STEPS + 1) * np.timedelta64(30, "m"))
            node_load.append(version[:, 0, k:k + STEPS])
            node_pv.append(version[:, 1, k:k + STEPS])
    node_load, node_pv = np.asarray(node_load), np.asarray(node_pv)
    return {"step_start": np.asarray(starts, dtype="datetime64[m]"),
            "issued_at": np.asarray(issues, dtype="datetime64[m]"),
            "target_end": np.asarray(ends, dtype="datetime64[m]"),
            "groups": np.asarray(groups, dtype=str),
            "node_load_kw": node_load, "node_pv_kw": node_pv,
            "load_kw": node_load.sum(axis=1), "pv_kw": node_pv.sum(axis=1)}


def load_mpc_windows(path: Path) -> dict[str, np.ndarray]:
    """Optional controller-side loader. Arrays are ordered by `step_start`."""
    with np.load(path, allow_pickle=False) as archive:
        arrays = {k: archive[k] for k in archive.files}
    required = {"load_kw", "pv_kw", "step_start", "issued_at", "target_end",
                "groups", "node_load_kw", "node_pv_kw"}
    if not required.issubset(arrays):
        raise ValueError("Incomplete MPC forecast archive.")
    n = len(arrays["step_start"])
    for key in ("load_kw", "pv_kw"):
        if arrays[key].shape != (n, STEPS) or not np.isfinite(arrays[key]).all():
            raise ValueError(f"Invalid shape/values for {key}.")
    if n == 0 or np.any(arrays["issued_at"] > arrays["step_start"]):
        raise ValueError("Invalid forecast issue times.")
    if not np.all(np.diff(arrays["step_start"]) == np.timedelta64(30, "m")):
        raise ValueError("MPC control steps are not contiguous half-hours.")
    expected = arrays["step_start"][:, None] + np.arange(1, 49) * np.timedelta64(30, "m")
    if not np.array_equal(arrays["target_end"], expected):
        raise ValueError("Target interval ends do not match the MPC control clock.")
    return arrays


def save_plots(out: Path, dates: list[date], predicted: np.ndarray,
               actual: np.ndarray, groups: list[str], method: str,
               aggregate_scope: str = "input_total") -> None:
    """Optional separate figures; no subplots or custom colours."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("WARNING: matplotlib not installed. Data saved; install matplotlib for --plots.")
        return
    folder = out / "plots"
    folder.mkdir(exist_ok=True)
    x = [datetime.combine(d, time()) + timedelta(minutes=30 * k)
         for d in dates for k in range(1, 49)]
    series = [(aggregate_scope, actual.sum(axis=1), predicted.sum(axis=1))]
    # Plot every node-phase group, not only the Node 646 example.
    # This changes plotting only: forecasts, metrics and CSV outputs are unchanged.
    for gi, group in enumerate(groups):
        series.append((group, actual[:, gi], predicted[:, gi]))
    for name, act, pred in series:
        for pi, profile in enumerate(PROFILES):
            fig, ax = plt.subplots(figsize=(11, 4.4))
            ax.plot(x, act[:, pi].reshape(-1), label="Actual", linewidth=1.7)
            ax.plot(x, pred[:, pi].reshape(-1), label=f"Forecast: {method}", linestyle="--", linewidth=1.5)
            ax.set(title=f"{name} | {profile} | day-ahead backtest", ylabel="Power (kW)",
                   xlabel="Interval-ending time (dataset clock)")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d Jan\n%H:%M")
                                         if all(d.month == 1 for d in dates)
                                         else mdates.DateFormatter("%d %b\n%H:%M"))
            ax.grid(True, alpha=0.25)
            ax.legend()
            fig.tight_layout()
            fig.savefig(folder / f"{name}_{profile}.png", dpi=160)
            plt.close(fig)


def run_forecasts(data: CourseData, out: Path, method: str = "persistence",
                  window: int = 3, decay: float = 0.5,
                  start: Optional[date] = None, end: Optional[date] = None,
                  plots: bool = False, overwrite: bool = False) -> dict:
    if len(data.dates) < 2:
        raise ValueError("Need at least two complete days for a historical backtest.")
    if window < 1 or not math.isfinite(decay) or not 0 < decay <= 1:
        raise ValueError("window >= 1 and 0 < decay <= 1 are required.")
    start = start or data.dates[1]
    end = end or data.dates[-1]
    if start <= data.dates[0] or start not in data.dates or end not in data.dates or end < start:
        raise ValueError("Choose test dates in the dataset with at least one earlier complete day.")
    indices = [i for i, d in enumerate(data.dates) if start <= d <= end]
    dates = [data.dates[i] for i in indices]
    predicted = np.stack([predict_issue(data, i, method, window, decay) for i in indices])
    actual = data.values[indices].copy()
    out = Path(out).expanduser().resolve()
    if out == data.source.parent:
        raise ValueError("Use a separate output subfolder so source files cannot be overwritten.")
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise FileExistsError(f"Output folder is not empty: {out}. Use a new folder or --overwrite.")
    out.mkdir(parents=True, exist_ok=True)

    write_node_profiles(out / "forecast_nodes_ext1.csv", data, dates, predicted)
    write_node_profiles(out / "actual_test_nodes_ext1.csv", data, dates, actual)
    write_central_profiles(out / "forecast_central_ext1.csv", dates,
                           predicted.sum(axis=1), int(data.customers.sum()))
    write_central_profiles(out / "perfect_central_reference.csv", dates,
                           actual.sum(axis=1), int(data.customers.sum()))

    # Record exact forecast origin and amount of history available for every day.
    write_csv(out / "forecast_issues.csv",
              ["TargetDate", "IssuedAt", "HistoryStartDate", "HistoryEndDate", "HistoryDaysUsed", "Method"],
              ([d.isoformat(), d.isoformat() + "T00:00:00",
                data.dates[max(0, i - (1 if method == 'persistence' else window))].isoformat(),
                data.dates[i - 1].isoformat(), min(i, 1 if method == 'persistence' else window), method]
               for d, i in zip(dates, indices)))
    course_mapping_verified = dict(zip(data.groups, map(int, data.customers))) == COURSE_CUSTOMERS
    aggregate_scope = "feeder_total" if course_mapping_verified else "input_total"
    metrics = []
    for gi, group in enumerate(data.groups):
        for pi, profile in enumerate(PROFILES):
            metrics.append({"Scope": group, "Profile": profile, "Method": method,
                            **error_metrics(actual[:, gi, pi], predicted[:, gi, pi])})
    act_total, fc_total = actual.sum(axis=1), predicted.sum(axis=1)
    for pi, profile in enumerate(PROFILES):
        metrics.append({"Scope": aggregate_scope, "Profile": profile, "Method": method,
                        **error_metrics(act_total[:, pi], fc_total[:, pi])})
    metrics.append({"Scope": aggregate_scope, "Profile": "Net_Load_kW", "Method": method,
                    **error_metrics(act_total[:, 0] - act_total[:, 1], fc_total[:, 0] - fc_total[:, 1])})
    write_csv(out / "forecast_metrics.csv", list(metrics[0]), (list(row.values()) for row in metrics))

    def comparisons():
        for di, d in enumerate(dates):
            midnight = datetime.combine(d, time())
            for gi, group in enumerate(data.groups):
                for pi, profile in enumerate(PROFILES):
                    for k in range(STEPS):
                        act = float(actual[di, gi, pi, k])
                        fc = float(predicted[di, gi, pi, k])
                        yield [d.isoformat(), midnight.isoformat(), group, profile, k + 1,
                               (midnight + timedelta(minutes=30 * (k + 1))).isoformat(),
                               fc, act, fc - act, abs(fc - act)]
    write_csv(out / "forecast_vs_actual.csv",
              ["Date", "IssuedAt", "NodePhase", "Profile", "Step", "IntervalEnd",
               "Forecast_kW", "Actual_kW", "Error_forecast_minus_actual_kW", "AbsoluteError_kW"],
              comparisons())
    mpc = make_mpc_windows(dates, predicted, data.groups)
    np.savez_compressed(out / "mpc_forecast_windows.npz", **mpc)
    write_csv(out / "mpc_step_index.csv", ["ArrayIndex", "StepStart", "IssuedAt", "FirstIntervalEnd", "LastIntervalEnd"],
              ([i, str(s), str(mpc['issued_at'][i]), str(mpc['target_end'][i, 0]), str(mpc['target_end'][i, -1])]
               for i, s in enumerate(mpc['step_start'])))
    # Forecast one next unseen day. This is NOT part of the backtest metrics.
    future_date = data.dates[-1] + timedelta(days=1)
    future = predict_issue(data, len(data.dates), method, window, decay)[None, ...]
    write_node_profiles(out / "next_day_nodes.csv", data, [future_date], future)
    write_central_profiles(out / "next_day_central.csv", [future_date], future.sum(axis=1), int(data.customers.sum()))

    manifest = {"method": method, "window_days": window, "decay": decay,
                "input_path": str(data.source),
                "input_sha256": hashlib.sha256(data.source.read_bytes()).hexdigest(),
                "source_first_date": data.dates[0].isoformat(), "source_last_date": data.dates[-1].isoformat(),
                "source_days": len(data.dates), "groups": data.groups,
                "course_mapping_verified": course_mapping_verified, "aggregate_scope": aggregate_scope,
                "customers": dict(zip(data.groups, map(int, data.customers))),
                "test_first_date": dates[0].isoformat(), "test_last_date": dates[-1].isoformat(),
                "test_days": len(dates), "step_count": len(dates) * STEPS,
                "units": "kW (half-hour interval average); input is not multiplied by 2",
                "forecast_issue_assumption": "00:00 dataset clock; previous entire day available immediately",
                "mpc": "daily-issued, fixed-origin 48-step windows; same profile repeated provisionally into second day; no intra-day forecast correction",
                "uncertainty": "deterministic forecasts; errors arise from held-out actual data, no artificial noise added",
                "not_completed": ["trained AI model", "QP/MPC controller execution", "HIL/Modbus validation", "cost/voltage comparison"],
                "next_day_unscored": future_date.isoformat(),
                "warnings": ["Short-history statistical baselines, not evidence of annual generalisation.",
                             "Do not slice concatenated daily forecasts into a rolling horizon: future issue leakage.",
                             "perfect_central_reference.csv is a hindsight-only comparison, not a deployable forecast.",
                             "Use actual_test_nodes_ext1.csv to align controller playback dates."]}
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if plots:
        save_plots(out, dates, predicted, actual, data.groups, method, aggregate_scope)
    return {"manifest": manifest, "metrics": metrics, "output_dir": str(out)}


def main(argv: Optional[Sequence[str]] = None) -> int:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=base / "Code_and_data" / "agg_jan2013_students.csv")
    parser.add_argument("--out-dir", type=Path, help="Default: script's Code_and_data/Extension1/<method>/")
    parser.add_argument("--method", choices=("persistence", "mean", "weighted"), default="persistence")
    parser.add_argument("--window", type=int, default=3, help="Maximum previous full days; early dates use fewer, logged explicitly.")
    parser.add_argument("--decay", type=float, default=0.5, help="For weighted: weight multiplier per older day (0 < decay <= 1).")
    parser.add_argument("--start-date", type=parse_date, help="First scored date; default second date in input.")
    parser.add_argument("--end-date", type=parse_date, help="Last scored date; default final date in input.")
    parser.add_argument("--plots", action="store_true", help="Also save separate load/PV forecast plots (requires matplotlib).")
    parser.add_argument("--allow-partial", action="store_true", help="Allow non-course/subset topology; not all-node demonstration evidence.")
    parser.add_argument("--overwrite", action="store_true", help="Replace generated files in the selected output folder.")
    args = parser.parse_args(argv)
    out = args.out_dir or base / "Code_and_data" / "Extension1" / args.method
    try:
        data = read_course_csv(args.input, require_course_nodes=not args.allow_partial)
        result = run_forecasts(data, out, args.method, args.window, args.decay,
                               args.start_date, args.end_date, args.plots, args.overwrite)
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    m = result['manifest']
    print(f"Forecasts saved: {result['output_dir']}")
    print(f"Method={m['method']} | {len(m['groups'])} node-phase groups | "
          f"{m['test_first_date']} to {m['test_last_date']} | {m['step_count']} half-hours")
    if args.allow_partial:
        print("WARNING: subset/custom topology enabled; not a verified all-node test.")
    for row in result['metrics']:
        if row['Scope'] in ('feeder_total', 'input_total'):
            print(f"{row['Profile']}: MAE={row['MAE_kW']:.4f} kW; RMSE={row['RMSE_kW']:.4f} kW")
    print("No QP/MPC or hardware test was run. Read README_Extension1.md before integration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
