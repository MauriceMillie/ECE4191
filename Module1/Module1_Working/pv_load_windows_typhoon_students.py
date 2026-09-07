#!/usr/bin/env python3
"""
pv_load_typhoon.py  —  ECE4191 Module 1: Load + PV Playback

Reads agg_jan2013_students.csv and writes each 30-minute load and PV
setpoint to the Typhoon HIL model via the Typhoon Python API.

Also records measured node voltages and measured load powers to two
separate CSV files during playback:
    measured_voltages.csv   — one row per 30-min step, one column per node voltage
    measured_powers.csv     — one row per 30-min step, one column per node active power

If either output CSV already exists it is NOT overwritten.  A timestamp
is appended to the filename instead, e.g.
    measured_voltages_20260624_153012.csv

Run from the Typhoon HIL Python environment on the Windows HIL machine:

    python pv_load_typhoon.py

Dry-run (no HIL connection needed, prints intended writes):

    python pv_load_typhoon.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


# ── Default settings ─────────────────────────────────────────────────────────
INPUT_CSV    = "agg_jan2013_students.csv"
START_DATE   = "7-Jan-13"
END_DATE     = "11-Jan-13"
STEP_SECONDS = 2.0      # wall-clock seconds per 30-minute data step
POWER_SCALE  = 1000.0   # CSV values are in kW; Typhoon SCADA inputs expect W
# ─────────────────────────────────────────────────────────────────────────────


# ── Signal map (from Monash_13NodeFeeder.tse) ────────────────────────────────
# Key   : (Node, Phase_ABC)
# Value : (subsystem, Pref_signal, Qref_signal, PV_signal, Battery_signal)
# None  = signal does not exist in this model for that node.
SIGNAL_MAP: Dict[Tuple[str, str], Tuple[str, str, str, Optional[str], Optional[str]]] = {
    # Single-phase nodes — no phase suffix in signal name
    ("646", "B"): ("Time Varying Load 646", "Pref646",    "Qref646",    "PVpanel_power646",    "Battery_Power646"),
    ("645", "B"): ("Time Varying Load 645", "Pref645",    "Qref645",    "PVpanel_power645",    "Battery_Power645"),
    ("611", "C"): ("Time Varying Load 611", "Pref611",    "Qref611",    "PVpanel_power611",    "Battery_Power611"),
    ("652", "A"): ("Time Varying Load 652", "Pref652",    "Qref652",    "PVpanel_power652",    "Battery_Power652"),
    # Three-phase nodes — PhA / PhB / PhC suffix
    ("671", "A"): ("Time Varying Load 671", "Pref671PhA", "Qref671PhA", "PVpanel_power671PhA", "Battery_Power671PhA"),
    ("671", "B"): ("Time Varying Load 671", "Pref671PhB", "Qref671PhB", "PVpanel_power671PhB", "Battery_Power671PhB"),
    ("671", "C"): ("Time Varying Load 671", "Pref671PhC", "Qref671PhC", "PVpanel_power671PhC", "Battery_Power671PhC"),
    ("692", "A"): ("Time Varying Load 692", "Pref692PhA", "Qref692PhA", None,                  None),
    ("692", "B"): ("Time Varying Load 692", "Pref692PhB", "Qref692PhB", None,                  None),
    ("692", "C"): ("Time Varying Load 692", "Pref692PhC", "Qref692PhC", None,                  None),
    ("675", "A"): ("Time Varying Load 675", "Pref675PhA", "Qref675PhA", "PVpanel_power675PhA", "Battery_Power675PhA"),
    ("675", "B"): ("Time Varying Load 675", "Pref675PhB", "Qref675PhB", "PVpanel_power675PhB", "Battery_Power675PhB"),
    ("675", "C"): ("Time Varying Load 675", "Pref675PhC", "Qref675PhC", "PVpanel_power675PhC", "Battery_Power675PhC"),
    ("634", "A"): ("Time Varying Load 634", "Pref634PhA", "Qref634PhA", "PVpanel_power634PhA", "Battery_Power634PhA"),
    ("634", "B"): ("Time Varying Load 634", "Pref634PhB", "Qref634PhB", "PVpanel_power634PhB", "Battery_Power634PhB"),
    ("634", "C"): ("Time Varying Load 634", "Pref634PhC", "Qref634PhC", "PVpanel_power634PhC", "Battery_Power634PhC"),
}

PHASE_TO_ABC = {
    "Ph1": "A", "Ph2": "B", "Ph3": "C",
    "A": "A",   "B": "B",   "C": "C",
}

TIME_COL_RE = re.compile(r"^\d{1,2}:\d{2}$")


# ── Measured signal maps (mirrored from clean version) ────────────────────────

DEFAULT_VOLTAGE_SIGNALS: Dict[str, str] = {
    "v_632_A_rms_V": "Node 632.V1_rms",
    "v_632_B_rms_V": "Node 632.V2_rms",
    "v_632_C_rms_V": "Node 632.V3_rms",
    "v_633_A_rms_V": "Node 633.V1_rms",
    "v_633_B_rms_V": "Node 633.V2_rms",
    "v_633_C_rms_V": "Node 633.V3_rms",
    "v_634_A_rms_V": "Node 634.V1_rms",
    "v_634_B_rms_V": "Node 634.V2_rms",
    "v_634_C_rms_V": "Node 634.V3_rms",
    "v_645_B_rms_V": "Node 645.V2_rms",
    "v_645_C_rms_V": "Node 645.V3_rms",
    "v_646_B_rms_V": "Node 646.V2_rms",
    "v_646_C_rms_V": "Node 646.V3_rms",
    "v_652_A_rms_V": "Node 652.V1_rms",
    "v_671_A_rms_V": "Node 671.V1_rms",
    "v_671_B_rms_V": "Node 671.V2_rms",
    "v_671_C_rms_V": "Node 671.V3_rms",
    "v_675_A_rms_V": "Node 675.V1_rms",
    "v_675_B_rms_V": "Node 675.V2_rms",
    "v_675_C_rms_V": "Node 675.V3_rms",
    "v_680_A_rms_V": "Node 680.V1_rms",
    "v_680_B_rms_V": "Node 680.V2_rms",
    "v_680_C_rms_V": "Node 680.V3_rms",
    "v_684_A_rms_V": "Node 684.V1_rms",
    "v_684_C_rms_V": "Node 684.V3_rms",
    "v_692_A_rms_V": "Node 692.V1_rms",
    "v_692_B_rms_V": "Node 692.V2_rms",
    "v_692_C_rms_V": "Node 692.V3_rms",
    "v_611_C_rms_V": "Node 611.V3_rms",
}

DEFAULT_POWER_SIGNALS: Dict[str, object] = {
    "p_634_A_W": "Time Varying Load 634.Single phase time-varying load with the Master PulseA.P_measured",
    "p_634_B_W": [
        "Time Varying Load 634.Single phase time-varying load with the Master PulseB.P_measured",
    ],
    "p_634_C_W": [
        "Time Varying Load 634.Single phase time-varying load with the Master PulseC.P_measured",
    ],
    "p_645_B_W": "Time Varying Load 645.Single phase time-varying load645.P_measured",
    "p_646_B_W": "Time Varying Load 646.Single phase time-varying load646.P_measured",
    "p_652_A_W": "Time Varying Load 652.Single phase time-varying load652.P_measured",
    "p_671_A_W": "Time Varying Load 671.Single phase time-varying loadA.P_measured",
    "p_671_B_W": "Time Varying Load 671.Single phase time-varying loadA1.P_measured",
    "p_671_C_W": "Time Varying Load 671.Single phase time-varying loadA2.P_measured",
    "p_675_A_W": "Time Varying Load 675.Single phase time-varying loadA.P_measured",
    "p_675_B_W": "Time Varying Load 675.Single phase time-varying loadB.P_measured",
    "p_675_C_W": "Time Varying Load 675.Single phase time-varying loadC.P_measured",
    "p_692_C_W": [
        "Time Varying Load 692.Single phase time-varying loadC.P_measured",
        "Time Varying Load 692.Single phase time-varying loadA.P_measured",   # fallback
    ],
    "p_611_C_W": "Time Varying Load 611.Single phase time-varying load1.P_measured",
}


# ── CSV helpers ───────────────────────────────────────────────────────────────

def parse_date(s: str) -> pd.Timestamp:
    return pd.to_datetime(str(s), format="%d-%b-%y")


def next_day_label(date_label: str) -> str:
    """Return the calendar-date label for the day after ``date_label``,
    formatted the same way as the input CSV's Date column (e.g. '8-Jan-13',
    no leading zero on the day)."""
    ts = parse_date(date_label) + pd.Timedelta(days=1)
    return f"{ts.day}-{ts.strftime('%b-%y')}"


def clean_number(value, default: float = 0.0) -> float:
    try:
        f = float(value)
        return default if math.isnan(f) else f
    except Exception:
        return default


def load_csv(path: Path, start_date: str, end_date: str):
    df = pd.read_csv(path)

    required = {"Date", "Node", "Phase", "Profile"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")

    time_cols = [str(c) for c in df.columns if TIME_COL_RE.match(str(c))]
    if len(time_cols) != 48:
        raise ValueError(f"Expected 48 half-hour time columns, found {len(time_cols)}.")

    df["_dp"] = df["Date"].astype(str).apply(parse_date)
    df = df[(df["_dp"] >= parse_date(start_date)) & (df["_dp"] <= parse_date(end_date))].copy()
    if df.empty:
        raise ValueError(f"No data found for {start_date} to {end_date}.")

    date_order = (
        df[["Date", "_dp"]].drop_duplicates().sort_values("_dp")["Date"].astype(str).tolist()
    )
    return df, date_order, time_cols


# ── Non-overwriting path helper (from clean version) ─────────────────────────

def make_non_overwriting_path(path: Path) -> Path:
    """Return a path that will not overwrite an existing file.

    If the requested path exists, append a timestamp before the suffix, e.g.
    measured_voltages.csv -> measured_voltages_20260624_153012.csv.
    If the timestamped file also exists, append an incrementing counter.
    """
    if not path.exists():
        return path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}_{timestamp}_{counter:02d}{path.suffix}")
        counter += 1
    return candidate


# ── HIL write helpers ─────────────────────────────────────────────────────────

def hil_write(hil, signal_path: str, value: float, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN]  {signal_path}  =  {value:.1f}")
        return
    try:
        hil.set_scada_input_value(signal_path, float(value))
    except Exception:
        hil.model_write(signal_path, float(value))


def write_node(hil, node: str, phase_abc: str,
               pref_W: float, pv_W: float, dry_run: bool) -> None:
    key = (node, phase_abc)
    if key not in SIGNAL_MAP:
        print(f"  WARNING: no signal mapping for Node {node} Phase {phase_abc} — skipped.")
        return
    subsystem, pref_sig, qref_sig, pv_sig, batt_sig = SIGNAL_MAP[key]
    hil_write(hil, f"{subsystem}.{pref_sig}", pref_W, dry_run)
    hil_write(hil, f"{subsystem}.{qref_sig}", 0.0,    dry_run)
    if pv_sig:
        hil_write(hil, f"{subsystem}.{pv_sig}",   pv_W, dry_run)
    if batt_sig:
        hil_write(hil, f"{subsystem}.{batt_sig}", 0.0,  dry_run)


def clear_all(hil, dry_run: bool) -> None:
    for (node, phase_abc), (subsystem, pref_sig, qref_sig, pv_sig, batt_sig) in SIGNAL_MAP.items():
        hil_write(hil, f"{subsystem}.{pref_sig}", 0.0, dry_run)
        hil_write(hil, f"{subsystem}.{qref_sig}", 0.0, dry_run)
        if pv_sig:
            hil_write(hil, f"{subsystem}.{pv_sig}",   0.0, dry_run)
        if batt_sig:
            hil_write(hil, f"{subsystem}.{batt_sig}", 0.0, dry_run)


# ── Measurement logger (ported from clean version) ───────────────────────────

class SplitMeasurementLogger:
    """Log measured node voltages and load powers to two separate CSV files.

    Output files are never overwritten: if the requested filename already
    exists a timestamp suffix is added automatically (see make_non_overwriting_path).
    """

    _BASE_FIELDS = ["step", "date_label", "profile_time"]

    def __init__(self, hil, voltage_csv: str, power_csv: str, enabled: bool):
        self.hil = hil
        self.enabled = enabled

        requested_v = Path(voltage_csv) if voltage_csv else None
        requested_p = Path(power_csv)   if power_csv   else None

        self.voltage_csv = make_non_overwriting_path(requested_v) if requested_v else None
        self.power_csv   = make_non_overwriting_path(requested_p) if requested_p else None

        # Warn when a name collision triggered a rename
        if requested_v and self.voltage_csv != requested_v:
            print(f"Voltage CSV already exists; writing to: {self.voltage_csv}")
        if requested_p and self.power_csv != requested_p:
            print(f"Power CSV already exists; writing to: {self.power_csv}")

        self.valid_voltage_signals: Dict[str, str] = {}
        self.valid_power_signals:   Dict[str, str] = {}

        self._voltage_fp     = None
        self._power_fp       = None
        self._voltage_writer = None
        self._power_writer   = None

    # ── signal resolution ────────────────────────────────────────────────────

    def _read_one(self, signal: str) -> float:
        """Read a single analog signal from the live HIL model."""
        if hasattr(self.hil, "read_analog_signal"):
            return float(self.hil.read_analog_signal(signal))
        if hasattr(self.hil, "read_analog_signals"):
            return float(self.hil.read_analog_signals([signal])[0])
        raise RuntimeError("No supported Typhoon analog read API found.")

    def _resolve_signals(self, signal_map: Dict[str, object], label: str) -> Dict[str, str]:
        """Return {col: signal} for every signal that can be successfully read."""
        valid: Dict[str, str] = {}
        for col, candidates in signal_map.items():
            if isinstance(candidates, str):
                candidates = [candidates]
            for sig in candidates:
                try:
                    self._read_one(sig)
                    valid[col] = sig
                    break
                except Exception:
                    pass
        if not valid:
            print(f"WARNING: No {label} signals could be read. {label.capitalize()} CSV "
                  f"will contain metadata columns only.")
        else:
            print(f"  {label.capitalize()} signals resolved: {len(valid)}/{len(signal_map)}")
        return valid

    # ── CSV open ─────────────────────────────────────────────────────────────

    def _open_csv(self, path: Path, extra_fields: List[str]):
        """Open a CSV for writing and return (file_handle, DictWriter)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        fp = path.open("w", newline="", encoding="utf-8")
        writer = csv.DictWriter(fp, fieldnames=self._BASE_FIELDS + extra_fields)
        writer.writeheader()
        fp.flush()
        return fp, writer

    # ── public API ───────────────────────────────────────────────────────────

    def start(self) -> None:
        """Resolve signals and open output CSVs.  Call once before the playback loop."""
        if not self.enabled:
            return
        if self.hil is None:
            print("WARNING: Measurement logging requested but Typhoon HIL API is not available.")
            self.enabled = False
            return

        if self.voltage_csv:
            print("\nResolving voltage measurement signals...")
            self.valid_voltage_signals = self._resolve_signals(DEFAULT_VOLTAGE_SIGNALS, "voltage")
            self._voltage_fp, self._voltage_writer = self._open_csv(
                self.voltage_csv, list(self.valid_voltage_signals.keys())
            )
            print(f"Voltage CSV: {self.voltage_csv}")

        if self.power_csv:
            print("\nResolving power measurement signals...")
            self.valid_power_signals = self._resolve_signals(DEFAULT_POWER_SIGNALS, "power")
            self._power_fp, self._power_writer = self._open_csv(
                self.power_csv, list(self.valid_power_signals.keys())
            )
            print(f"Power CSV: {self.power_csv}")

    def log_step(self, step: int, date_label: str, time_col: str) -> None:
        """Read all resolved signals and append one row to each CSV."""
        if not self.enabled:
            return

        base = {"step": step, "date_label": date_label, "profile_time": time_col}

        if self._voltage_writer is not None:
            row = dict(base)
            for col, sig in self.valid_voltage_signals.items():
                try:
                    row[col] = self._read_one(sig)
                except Exception:
                    row[col] = ""
            self._voltage_writer.writerow(row)
            self._voltage_fp.flush()

        if self._power_writer is not None:
            row = dict(base)
            for col, sig in self.valid_power_signals.items():
                try:
                    row[col] = self._read_one(sig)
                except Exception:
                    row[col] = ""
            self._power_writer.writerow(row)
            self._power_fp.flush()

    def close(self) -> None:
        """Flush and close both CSV files."""
        for fp in (self._voltage_fp, self._power_fp):
            if fp is not None:
                try:
                    fp.flush()
                    fp.close()
                except Exception:
                    pass
        self._voltage_fp = self._power_fp = None
        self._voltage_writer = self._power_writer = None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ECE4191 Module 1 — Load + PV playback via Typhoon HIL API."
    )
    parser.add_argument("--input",        default=INPUT_CSV,
                        help=f"Input CSV. Default: {INPUT_CSV}")
    parser.add_argument("--start-date",   default=START_DATE,
                        help=f"Start date. Default: {START_DATE}")
    parser.add_argument("--end-date",     default=END_DATE,
                        help=f"End date. Default: {END_DATE}")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS,
                        help=f"Real-time seconds per 30-min data step. Default: {STEP_SECONDS}")
    parser.add_argument("--no-wait",    action="store_true",
                        help="Skip sleep between steps (fast test mode).")
    parser.add_argument("--no-prompt",  action="store_true",
                        help="Skip the pre-start confirmation prompt.")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Print all writes without connecting to HIL.")
    parser.add_argument("--keep-final", action="store_true",
                        help="Leave final values in HIL after playback ends.")
    # ── Measurement CSV options ───────────────────────────────────────────────
    parser.add_argument("--voltage-csv", default="measured_voltages.csv",
                        help="Output CSV for measured node voltages. "
                             "If file exists a timestamp is added. Default: measured_voltages.csv")
    parser.add_argument("--power-csv",   default="measured_powers.csv",
                        help="Output CSV for measured load powers. "
                             "If file exists a timestamp is added. Default: measured_powers.csv")
    parser.add_argument("--no-measurements", action="store_true",
                        help="Disable voltage/power CSV logging entirely.")
    parser.add_argument("--measurement-delay", type=float, default=0.2,
                        help="Seconds to wait after each input write before reading "
                             "measured signals. Default: 0.2")
    args = parser.parse_args()

    # ── Connect to HIL ────────────────────────────────────────────────────────
    hil = None
    if not args.dry_run:
        try:
            import typhoon.api.hil as _hil  # type: ignore
            hil = _hil
        except ImportError:
            raise RuntimeError(
                "Cannot import typhoon.api.hil.\n"
                "Run this script from the Typhoon HIL Python environment, "
                "or use --dry-run to test without HIL."
            )
        if not hil.is_simulation_running():
            raise RuntimeError(
                "No simulation is running.\n"
                "Compile and start the model in Typhoon HIL Control Center first."
            )

    # ── Load CSV ──────────────────────────────────────────────────────────────
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"CSV not found: {input_path}")

    df, date_order, time_cols = load_csv(input_path, args.start_date, args.end_date)
    total_steps = len(date_order) * len(time_cols)

    # ── Measurement logger ────────────────────────────────────────────────────
    log_enabled = not args.no_measurements and not args.dry_run
    measurement_logger = SplitMeasurementLogger(
        hil=hil,
        voltage_csv=args.voltage_csv,
        power_csv=args.power_csv,
        enabled=log_enabled,
    )

    # ── Banner ────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("ECE4191 Module 1  |  Load + PV Playback")
    print("=" * 70)
    print(f"  CSV          : {input_path}")
    print(f"  Dates        : {', '.join(date_order)}")
    print(f"  Total steps  : {total_steps}  ({len(time_cols)} steps/day × {len(date_order)} days)")
    print(f"  Step size    : {args.step_seconds} s real time = 30 min simulated time")
    print(f"  Voltage CSV  : {args.voltage_csv if log_enabled else 'disabled'}")
    print(f"  Power CSV    : {args.power_csv   if log_enabled else 'disabled'}")
    print(f"  Meas. delay  : {args.measurement_delay} s after each input write")
    if args.dry_run:
        print("  *** DRY-RUN MODE — no HIL writes will occur ***")
    print("=" * 70)

    # ── Pre-start prompt ──────────────────────────────────────────────────────
    if not args.no_prompt and not args.dry_run:
        print("\nBefore starting:")
        print("  1. Model is compiled and running in Typhoon HIL Control Center.")
        print("  2. SCADA is open.")
        print("  3. Control type is set to LOCAL CONTROL.")
        input("\nPress Enter to start playback...\n")

    # ── Set local control mode ────────────────────────────────────────────────
    if not args.dry_run:
        try:
            hil.set_scada_input_value("Local-Remote Control", 0.0)
            print("Control mode: LOCAL")
        except Exception as e:
            print(f"WARNING: Could not set Local-Remote Control ({e})")

    # ── Clear all inputs to zero ──────────────────────────────────────────────
    print("\nClearing all load inputs...")
    clear_all(hil, args.dry_run)
    print("Done.")

    # ── Settle ────────────────────────────────────────────────────────────────
    settle = 12
    if args.no_wait:
        print("Settle delay skipped (--no-wait).")
    else:
        print(f"\nWaiting {settle} seconds for model to settle...")
        for i in range(settle, 0, -1):
            print(f"  Starting in {i}s...", end="\r")
            time.sleep(1)
        print(" " * 30)
    print("Ready.\n")

    # ── Start measurement logger ──────────────────────────────────────────────
    measurement_logger.start()

    # ── Playback ──────────────────────────────────────────────────────────────
    step_idx = 0
    try:
        for date_label in date_order:
            day_df  = df[df["Date"].astype(str) == date_label].copy()
            gc_rows = day_df[day_df["Profile"] == "GC_Load_kW"]
            pv_rows = day_df[day_df["Profile"] == "PV_Generation_kW"]

            for time_col in time_cols:
                t0 = time.time()
                step_idx += 1

                total_load = 0.0
                total_pv   = 0.0

                for _, gc in gc_rows.iterrows():
                    node      = str(gc["Node"]).strip()
                    phase_abc = PHASE_TO_ABC.get(str(gc["Phase"]).strip(), "")
                    pref_kw   = clean_number(gc[time_col])

                    pv_match = pv_rows[
                        (pv_rows["Node"].astype(str).str.strip() == node) &
                        (pv_rows["Phase"].astype(str).str.strip() == str(gc["Phase"]).strip())
                    ]
                    pv_kw = clean_number(pv_match.iloc[0][time_col]) if not pv_match.empty else 0.0

                    write_node(hil, node, phase_abc,
                               pref_kw * POWER_SCALE,
                               pv_kw   * POWER_SCALE,
                               args.dry_run)

                    total_load += pref_kw
                    total_pv   += pv_kw

                # The input CSV's time columns are interval-ending labels
                # (0:30, 1:00, ..., 23:30, 0:00), so the final "0:00" column of
                # each day is midnight at the *end* of that day, i.e. the
                # start of the next calendar day. Roll the displayed/logged
                # date label over accordingly so it stays chronological.
                log_date_label = next_day_label(date_label) if time_col == "0:00" else date_label

                print(
                    f"Step {step_idx:03d}/{total_steps}  |  {log_date_label}  {time_col}  |  "
                    f"Load = {total_load:7.1f} kW  |  "
                    f"PV = {total_pv:7.1f} kW  |  "
                    f"Net = {total_load - total_pv:7.1f} kW"
                )

                # Wait briefly so HIL model output settles before reading back
                if not args.no_wait and args.measurement_delay > 0:
                    time.sleep(args.measurement_delay)

                # ── Log measured voltages and powers ──────────────────────────
                measurement_logger.log_step(step_idx, log_date_label, time_col)

                if step_idx < total_steps and not args.no_wait:
                    elapsed = time.time() - t0
                    time.sleep(max(0.0, args.step_seconds - elapsed))

    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")

    # ── Final cleanup ─────────────────────────────────────────────────────────
    finally:
        if args.keep_final:
            print("\nFinal HIL state kept.")
        else:
            print("\nClearing all load inputs...")
            clear_all(hil, args.dry_run)
            print("Done.")
        measurement_logger.close()

    print("\nPlayback complete.")


if __name__ == "__main__":
    main()