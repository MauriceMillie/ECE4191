
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd

try:
    import cvxpy as cp
except ImportError:
    print("ERROR: cvxpy not found. Install it with:")
    print("  pip install cvxpy --break-system-packages")
    sys.exit(1)

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    print("ERROR: pymodbus not found. Install it with:")
    print("  pip install pymodbus --break-system-packages")
    sys.exit(1)


# ============================================================
# 1. Settings (all nodes) -- identical to experiment1.py
# ============================================================

N_STEPS      = 48
DELTA_HOURS  = 0.5
STEP_SECONDS = 2.0        # wall-clock seconds per 30-min data step

TIME_COL_RE = re.compile(r"^\d{1,2}:\d{2}$")

NODE_MAP = {
    "646_B": {"start": 2000, "order": "normal"},
    "645_B": {"start": 2004, "order": "normal"},
    "611_C": {"start": 2008, "order": "normal"},
    "652_A": {"start": 2012, "order": "normal"},

    "671_A": {"start": 2016, "order": "normal"},
    "671_B": {"start": 2020, "order": "normal"},
    "671_C": {"start": 2024, "order": "normal"},

    "692_C": {"start": 2028, "order": "reversed"},
    "692_B": {"start": 2032, "order": "reversed"},
    "692_A": {"start": 2036, "order": "reversed"},

    "675_C": {"start": 2040, "order": "reversed"},
    "675_B": {"start": 2044, "order": "reversed"},
    "675_A": {"start": 2048, "order": "reversed"},

    "634_C": {"start": 2052, "order": "reversed"},
    "634_B": {"start": 2056, "order": "reversed"},
    "634_A": {"start": 2060, "order": "reversed"},
}


# Real-time reactive power (kVAr) per node. Only Node 646 is specified by the manual;
# all other nodes default to 0 kVAr -- update this if you have per-node Qref data.
QREF_MAP = {
    "646_B": 132,
    "645_B": 125,
    "611_C": 80,
    "652_A": 86,

    "671_A": 220,
    "671_B": 220,
    "671_C": 220,

    "692_C": 151,
    "692_B": 0,
    "692_A": 0,

    "675_C": 212,
    "675_B": 60,
    "675_A": 190,

    "634_C": 90,
    "634_B": 90,
    "634_A": 110,
}

PHASE_MAP = {
    "A": "A", "B": "B", "C": "C",
    "Ph1": "A", "Ph2": "B", "Ph3": "C",
    "1": "A", "2": "B", "3": "C",
}

N_CUSTOMERS = {
    "646_B": 102, "645_B": 63, "611_C": 68, "652_A": 46,
    "671_A": 159, "671_B": 155, "671_C": 159,
    "692_A": 0,   "692_B": 0,  "692_C": 66,
    "675_A": 191, "675_B": 36, "675_C": 119,
    "634_A": 69,  "634_B": 45, "634_C": 52,
}
TOTAL_CUSTOMERS = sum(N_CUSTOMERS.values())   # 1330

BATTERY_CAPACITY_KWH = 10.0 * TOTAL_CUSTOMERS   # 13300 kWh (aggregate feeder battery)
BATTERY_POWER_KW     = 5.0  * TOTAL_CUSTOMERS   # 6650 kW
INITIAL_SOC_KWH      = 0.5  * BATTERY_CAPACITY_KWH

DEFAULT_WEIGHT = 1   # QP objective weight `w` (arbitrage vs. peak-shaving trade-off)

# --- Modbus -------------------------------------------------------------------
DEFAULT_HIL_IP   = "192.168.1.210"
DEFAULT_HIL_PORT = 502

HOLDING_START = 2000
HOLDING_COUNT = 64

SIGNED_16BIT_MIN = -32768
SIGNED_16BIT_MAX = 32767

SOC_INPUT_REGISTER = 3000   # Node 646 SoC, value = registers[0] / 100.0

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0

DEFAULT_PLAYBACK_DAYS = 4   # Experiment 2 uses a 4-day playback period


# ============================================================
# 2. CSV loaders
# ============================================================

def parse_date(value: str) -> pd.Timestamp:
    """Parse supplied date labels such as 7-Jan-13."""
    text = str(value).strip()
    try:
        return pd.to_datetime(text, format="%d-%b-%y")
    except ValueError:
        return pd.to_datetime(text)


def sorted_date_labels(df: pd.DataFrame) -> list[str]:
    temp = pd.DataFrame({
        "Date": df["Date"].astype(str).str.strip(),
    })
    temp["_parsed"] = temp["Date"].map(parse_date)
    return (
        temp.drop_duplicates()
        .sort_values("_parsed")["Date"]
        .tolist()
    )


def next_day_label(date_label: str) -> str:
    ts = parse_date(date_label) + pd.Timedelta(days=1)
    return f"{ts.day}-{ts.strftime('%b-%y')}"

def _pick_row(frame: pd.DataFrame, needle: str):
    for key in frame.index:
        if needle in str(key).lower():
            return key
    return None


def find_time_columns(df: pd.DataFrame) -> list[str]:
    cols = [str(c) for c in df.columns if TIME_COL_RE.match(str(c).strip())]
    if len(cols) != N_STEPS:
        raise ValueError(
            f"Expected {N_STEPS} half-hour time columns, found {len(cols)}: {cols}"
        )
    return cols

def load_forecast_csv(path: Path):
    """
    Read central_agg_forecast_data_students.csv.

    Expected format:
      Date | N_Customers | Profile | ... | 48 half-hour columns

    Returns
    -------
    pv_days, load_days : ndarray (n_days, 48), kW
    dates              : chronological date labels
    time_cols          : 48 interval-ending labels
    """
    df = pd.read_csv(path)

    required = {"Date", "N_Customers", "Profile"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Forecast CSV missing columns: {sorted(missing)}")

    time_cols = find_time_columns(df)
    dates = sorted_date_labels(df)

    load_days = []
    pv_days = []

    for date in dates:
        day = df[df["Date"].astype(str).str.strip() == date]

        load_rows = day[day["Profile"].astype(str).str.strip() == "GC_Load_kW"]
        pv_rows = day[day["Profile"].astype(str).str.strip() == "PV_Generation_kW"]

        if len(load_rows) != 1 or len(pv_rows) != 1:
            raise ValueError(
                f"{date}: expected one GC_Load_kW row and one PV_Generation_kW row; "
                f"found {len(load_rows)} load and {len(pv_rows)} PV rows."
            )

        customers = pd.to_numeric(
            pd.concat([load_rows["N_Customers"], pv_rows["N_Customers"]]),
            errors="coerce",
        ).dropna()

        if not customers.empty and not np.allclose(customers.to_numpy(float), TOTAL_CUSTOMERS):
            raise ValueError(
                f"{date}: central forecast N_Customers is not {TOTAL_CUSTOMERS}: "
                f"{customers.tolist()}"
            )

        load_days.append(
            pd.to_numeric(load_rows.iloc[0][time_cols], errors="raise").to_numpy(float)
        )
        pv_days.append(
            pd.to_numeric(pv_rows.iloc[0][time_cols], errors="raise").to_numpy(float)
        )

    return np.asarray(pv_days), np.asarray(load_days), dates, time_cols


def load_actual_feeder_csv(path: Path):
    """Read the long-format actual load/PV CSV (Date, Node, Phase, Profile, 48 cols)
    and return per-node real-time arrays plus the feeder-wide totals."""
    df = pd.read_csv(path)
    time_cols = list(df.columns[5:53])

    dates = list(dict.fromkeys(df["Date"].astype(str)))
    n_days = len(dates)
    total_steps = n_days * N_STEPS

    node_data = {
        node: {"load_kw": np.zeros(total_steps), "pv_kw": np.zeros(total_steps)}
        for node in NODE_MAP
    }

    for day_i, date in enumerate(dates):
        day_rows = df[df["Date"].astype(str) == date]
        for _, row in day_rows.iterrows():
            phase_raw = str(row["Phase"]).strip()
            if phase_raw not in PHASE_MAP:
                raise ValueError(f"Unknown phase label: {phase_raw}")

            node_key = f"{int(row['Node'])}_{PHASE_MAP[phase_raw]}"
            if node_key not in node_data:
                continue

            values = pd.to_numeric(row[time_cols], errors="raise").to_numpy(dtype=float)
            start = day_i * N_STEPS
            end = start + N_STEPS

            if row["Profile"] == "GC_Load_kW":
                node_data[node_key]["load_kw"][start:end] = values
            elif row["Profile"] == "PV_Generation_kW":
                node_data[node_key]["pv_kw"][start:end] = values
            else:
                raise ValueError(f"Unexpected Profile value: {row['Profile']}")

    total_load = np.zeros(total_steps)
    total_pv = np.zeros(total_steps)
    for node in node_data:
        total_load += node_data[node]["load_kw"]
        total_pv += node_data[node]["pv_kw"]

    return node_data, total_load, total_pv, dates


# ============================================================
# 3. Tariff, QP/MPC solver, disaggregation
# ============================================================

def make_eta_array(n_steps_total: int) -> np.ndarray:
    """Time-of-use tariff, tiled to cover `n_steps_total` half-hourly steps."""
    pattern = np.zeros(N_STEPS)
    pattern[np.r_[0:14, 44:48]] = 0.03   # Off-peak ($/kWh)
    pattern[np.r_[14:28, 40:44]] = 0.06  # Shoulder ($/kWh)
    pattern[28:40] = 0.30                # Peak ($/kWh)
    reps = int(np.ceil(n_steps_total / N_STEPS)) + 1
    return np.tile(pattern, reps)[:n_steps_total]


def solve_daily_qp(p_load, p_pv, eta, weight, batt_power_kw, capacity_kwh,
                    soc0_kwh, solver):
    """Single QP solve over an n-step horizon (n need not be 48 -- this is reused
    for the receding-horizon MPC solves as well as a one-shot day-ahead QP)."""
    n = len(p_load)

    batt = cp.Variable(n)
    grid = cp.Variable(n)
    soc = cp.Variable(n + 1)

    objective = cp.Minimize(
        cp.sum(
            -DELTA_HOURS * cp.multiply(eta, batt)
            + weight * cp.multiply(eta, cp.square(grid))
        )
    )

    constraints = [
        grid == p_load - p_pv - batt,
        batt >= -batt_power_kw,
        batt <=  batt_power_kw,
        soc[0] == soc0_kwh,
        soc[1:] == soc[:-1] - DELTA_HOURS * batt,
        soc >= 0.0,
        soc <= capacity_kwh,
        soc[-1] == soc0_kwh,   # terminal SoC(t+n|t) = SoC(t|t), Eq. (12)
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=getattr(cp, solver), verbose=False)

    if batt.value is None:
        raise RuntimeError(f"QP failed: {problem.status}")

    return (
        np.asarray(batt.value).flatten(),
        np.asarray(grid.value).flatten(),
        np.asarray(soc.value).flatten(),
        str(problem.status),
        float(problem.value),
    )


def _action(v: float) -> str:
    return "Discharge" if v > 0.5 else ("Charge" if v < -0.5 else "Idle")


def disaggregate_battery(pbat_aggregate_kw: float):
    """Split one aggregate battery command across the 16 node-phase groups in
    proportion to the number of customers connected at each node (Section 3)."""
    return {
        node: pbat_aggregate_kw * N_CUSTOMERS[node] / TOTAL_CUSTOMERS
        for node in N_CUSTOMERS
    }


def pad_to_length(arr: np.ndarray, target_len: int) -> np.ndarray:
    """Extend `arr` to at least `target_len` samples by repeating its final
    24 h block (or its last value if shorter than a day). Used so the MPC
    look-ahead window never runs off the end of the forecast data."""
    if len(arr) >= target_len:
        return arr
    if len(arr) == 0:
        return np.zeros(target_len)
    pad_block = arr[-N_STEPS:] if len(arr) >= N_STEPS else arr[-1:] 
    out = arr.copy()
    while len(out) < target_len:
        out = np.concatenate([out, pad_block])
    return out[:target_len]


# ============================================================
# 4. Modbus connection + write helpers
# ============================================================

class ModbusConnection:
    """Live ModbusTcpClient with reconnect-on-failure."""

    def __init__(self, ip: str, port: int, retries: int = RECONNECT_RETRIES,
                 delay: float = RECONNECT_DELAY_S):
        self.ip, self.port = ip, port
        self.retries, self.delay = retries, delay
        self.client: ModbusTcpClient | None = None

    def connect(self) -> None:
        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                client = ModbusTcpClient(self.ip, port=self.port)
                if client.connect():
                    self.client = client
                    return
            except Exception as e:
                last_exc = e
            print(f"  Connection attempt {attempt}/{self.retries} failed"
                  f"{f' ({last_exc})' if last_exc else ''}; retrying in {self.delay}s ...")
            time.sleep(self.delay)
        raise ConnectionError(
            f"Cannot connect to HIL Modbus server at {self.ip}:{self.port} "
            f"after {self.retries} attempts."
        )

    def reconnect(self) -> None:
        try:
            if self.client is not None:
                self.client.close()
        except Exception:
            pass
        self.client = None
        print("  Attempting Modbus reconnection ...")
        self.connect()

    def close(self) -> None:
        try:
            if self.client is not None:
                self.client.close()
        except Exception:
            pass


def signed_to_register(value: float) -> int:
    value = int(round(value))
    if value < SIGNED_16BIT_MIN or value > SIGNED_16BIT_MAX:
        clamped = max(SIGNED_16BIT_MIN, min(SIGNED_16BIT_MAX, value))
        print(f"  WARNING: register value {value} out of signed 16-bit range, "
              f"clamped to {clamped}.")
        value = clamped
    return value & 0xFFFF


def build_feeder_payload(node_data, step_index, pbat_nodes):
    payload = [0] * HOLDING_COUNT

    for node, config in NODE_MAP.items():
        p_load = node_data[node]["load_kw"][step_index]
        p_pv   = node_data[node]["pv_kw"][step_index]
        q_load = QREF_MAP[node]
        p_bat  = pbat_nodes[node]

        values = [p_load, q_load, p_pv, p_bat]
        if config["order"] == "reversed":
            values.reverse()

        offset = config["start"] - HOLDING_START
        payload[offset:offset + 4] = [signed_to_register(v) for v in values]

    return payload


def modbus_write_feeder(conn, payload, dry_run, verbose=False):
    if len(payload) != 64:
        raise ValueError(f"Expected 64 Modbus registers, got {len(payload)}")

    if dry_run:
        if verbose:
            print(f"[DRY-RUN] holding[2000:2064] = {payload}")
        return

    try:
        result = conn.client.write_registers(address=HOLDING_START, values=payload)
        if result is None or result.isError():
            raise IOError("write_registers returned error")
    except Exception as e:
        print(f"WARNING: Modbus write failed: {e}")
        conn.reconnect()
        result = conn.client.write_registers(address=HOLDING_START, values=payload)
        if result is None or result.isError():
            raise IOError("Modbus write failed after reconnect")


def clear_all_registers(conn, dry_run: bool) -> None:
    payload = [0] * HOLDING_COUNT
    if dry_run:
        print(f"    [DRY-RUN] clear holding[{HOLDING_START}:{HOLDING_START + HOLDING_COUNT}]")
        return
    result = conn.client.write_registers(address=HOLDING_START, values=payload)
    if result is None or result.isError():
        print(f"  WARNING: failed to clear registers "
              f"{HOLDING_START}-{HOLDING_START + HOLDING_COUNT - 1}.")
    else:
        print(f"  Registers {HOLDING_START}-{HOLDING_START + HOLDING_COUNT - 1} cleared.")


# ============================================================
# 5. SoC measurement logger (Node 646 only -- comparison/logging use)
# ============================================================

class SocLogger:
    """Read Node-646 SoC (input register 3000, value/100) each step and return it.
    In Experiment 2 this is used for LOGGING/comparison only -- the aggregate
    battery state used by the MPC is advanced using the QP's own predicted
    trajectory, not this measurement (see Section 7/8 -- only Experiment 3 is
    controller-in-the-loop)."""

    def __init__(self, conn, enabled: bool):
        self.conn = conn
        self.enabled = enabled

    def _read_soc(self) -> float:
        rr = self.conn.client.read_input_registers(address=SOC_INPUT_REGISTER, count=1)
        if rr is None or rr.isError():
            raise IOError(f"Failed to read SoC input register {SOC_INPUT_REGISTER}")
        return rr.registers[0] / 100.0

    def start(self) -> None:
        if not self.enabled:
            return
        if self.conn is None or self.conn.client is None:
            print("WARNING: SoC reading requested but Modbus client unavailable.")
            self.enabled = False
            return
        try:
            self._read_soc()
            print(f"  SoC register {SOC_INPUT_REGISTER} resolved (logged for comparison only).")
        except Exception:
            print(f"  WARNING: SoC register {SOC_INPUT_REGISTER} did not read back; "
                  "soc_measured_pct will be blank.")

    def log_step(self):
        if not self.enabled:
            return None
        try:
            return self._read_soc()
        except Exception:
            return None

    def close(self) -> None:
        pass


# ============================================================
# 6. Console output
# ============================================================

_HDR = (f"{'Step':>5} {'Day':>3} {'k':>3} {'Load kW':>9} {'PV kW':>8} "
        f"{'Batt kW':>9} {'Action':>10} {'Grid kW':>10} "
        f"{'SoC% pred':>10} {'SoC% meas(646)':>14}")


def print_step(step, day, k, load, pv, batt, grid, soc_pred, soc_meas):
    meas = f"{soc_meas:14.2f}" if soc_meas is not None else f"{'-':>14}"
    print(f"{step:5d} {day:3d} {k:3d} {load:9.1f} {pv:8.1f} "
          f"{batt:9.2f} {_action(batt):>10} {grid:10.2f} "
          f"{soc_pred:10.2f} {meas}")


# ============================================================
# 7. Main -- feeder-wide receding-horizon MPC
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ECE4191 Module 3 -- Experiment 2: feeder-wide MPC over Modbus TCP"
    )
    parser.add_argument("--forecast", default="central_agg_forecast_data_students.csv",
                        help="Feeder-total day-ahead forecast CSV (drives the MPC).")
    parser.add_argument("--actual", default="agg_jan2013_students.csv",
                        help="Per-node actual load/PV CSV (fed to the feeder in real time).")
    parser.add_argument("--playback-days", type=int, default=DEFAULT_PLAYBACK_DAYS,
                        help=f"Number of days to play back (default {DEFAULT_PLAYBACK_DAYS}).")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS)
    parser.add_argument("--weight", type=float, default=DEFAULT_WEIGHT,
                        help=f"QP objective weight w (default {DEFAULT_WEIGHT}).")
    parser.add_argument("--batt-power", type=float, default=BATTERY_POWER_KW,
                        help=f"Aggregate battery power limit in kW (default {BATTERY_POWER_KW:.0f}).")
    parser.add_argument("--capacity", type=float, default=BATTERY_CAPACITY_KWH,
                        help=f"Aggregate battery capacity in kWh (default {BATTERY_CAPACITY_KWH:.0f}).")
    parser.add_argument("--initial-soc", type=float, default=INITIAL_SOC_KWH,
                        help=f"Initial aggregate SoC in kWh (default {INITIAL_SOC_KWH:.0f} = 50%%).")
    parser.add_argument("--solver", default="OSQP")
    parser.add_argument("--no-wait", action="store_true",
                        help="Skip sleep between steps (fast test mode).")
    parser.add_argument("--no-prompt", action="store_true",
                        help="Skip pre-start confirmation prompt.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without connecting to the HIL.")
    parser.add_argument("--keep-final", action="store_true",
                        help="Leave final values on the HIL after playback ends.")
    parser.add_argument("--ip", default=DEFAULT_HIL_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_HIL_PORT)
    parser.add_argument("--no-measurements", action="store_true",
                        help="Disable reading Node-646 SoC (soc_measured_pct stays blank).")
    parser.add_argument("--measurement-delay", type=float, default=0.2,
                        help="Seconds to wait after a write before reading SoC.")
    parser.add_argument("--progress-every", type=int, default=1,
                        help="Print one row every N steps (0 = summary only).")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full dry-run Modbus payloads.")
    args = parser.parse_args()

    # ── Connect ───────────────────────────────────────────────────────────────
    conn = None
    if not args.dry_run:
        conn = ModbusConnection(args.ip, args.port)
        print(f"\nConnecting to HIL Modbus server at {args.ip}:{args.port} ...")
        conn.connect()
        print("  Connected.")

    # ── Load forecast (feeder-total) + actual (per-node) CSVs ───────────────────
    fc_path = Path(args.forecast)
    if not fc_path.exists():
        raise FileNotFoundError(f"Forecast CSV not found: {fc_path}")
    act_path = Path(args.actual)
    if not act_path.exists():
        raise FileNotFoundError(f"Actual CSV not found: {act_path}")

    print(f"\nLoading forecast CSV : {fc_path.name}")
    pv_days, load_days, n_days_fc, forecast_time_cols = load_forecast_csv(fc_path)
    pv_fc_flat   = pv_days.flatten()
    load_fc_flat = load_days.flatten()

    print(f"Loading actual   CSV: {act_path.name}")
    node_data, total_load_act, total_pv_act, dates = load_actual_feeder_csv(act_path)
    n_days_act = len(dates)

    playback_days = min(args.playback_days, n_days_act)
    total_steps = playback_days * N_STEPS
    print(f"  Forecast days available : {n_days_fc}")
    print(f"  Actual days available   : {n_days_act}")
    print(f"  Playback days used      : {playback_days}  ({total_steps} steps)")

    if len(load_fc_flat) < total_steps + N_STEPS:
        print("  NOTE: forecast CSV is shorter than (playback + 48-step lookahead); "
              "padding by repeating the final day's forecast for the tail steps.")
        load_fc_flat = pad_to_length(load_fc_flat, total_steps + N_STEPS)
        pv_fc_flat   = pad_to_length(pv_fc_flat,   total_steps + N_STEPS)

    eta_flat = make_eta_array(len(load_fc_flat))

    # ── Banner ────────────────────────────────────────────────────────────────
    print("=" * 78)
    print("ECE4191 Module 3  |  Experiment 2 -- Feeder-wide MPC Playback (Modbus TCP)")
    print("=" * 78)
    print(f"  HIL target      : {args.ip}:{args.port}")
    print(f"  Forecast CSV    : {fc_path.name}  (feeder-total, MPC input)")
    print(f"  Actual   CSV    : {act_path.name}  (per-node, fed to all 16 nodes)")
    print(f"  Aggregate batt  : {args.capacity:,.0f} kWh   +/-{args.batt_power:,.0f} kW")
    print(f"  Objective weight: w = {args.weight}")
    print(f"  Playback period : {playback_days} day(s), {total_steps} steps")
    if args.dry_run:
        print("  *** DRY-RUN MODE -- no Modbus writes will occur ***")
    print("=" * 78)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. Model compiled and running in Typhoon HIL Control Center.")
        print("  2. SCADA open; Control Type = REMOTE CONTROL.")
        print("  3. BusSplitMap holding registers 2000-2063 enabled.")
        print("  4. Voltage/active-power Signal Analyzer export ready (see Appendix B).")
        input("\nPress Enter to start playback ...\n")

    # ── Initial clear ─────────────────────────────────────────────────────────
    print("\nClearing all registers ...")
    clear_all_registers(conn, args.dry_run)

    settle = 12
    if args.no_wait or args.dry_run:
        print("Settle delay skipped.")
    else:
        print(f"Waiting {settle} s for model to settle ...")
        for i in range(settle, 0, -1):
            print(f"  Starting in {i}s ...", end="\r")
            time.sleep(1)
        print(" " * 30)
    print("Ready.\n")

    # ── SoC reader (Node 646, logging only) ─────────────────────────────────────
    log_enabled = not args.no_measurements and not args.dry_run
    soc_logger = SocLogger(conn, log_enabled)
    soc_logger.start()

    # ── Receding-horizon MPC playback ────────────────────────────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False
    soc_pred = args.initial_soc

    if args.verbose or args.progress_every > 0:
        print(_HDR)
        print("-" * len(_HDR))

    try:
        for i in range(total_steps):
            t0 = time.time()
            step = i + 1
            day_num = (i // N_STEPS) + 1
            k = (i % N_STEPS) + 1

            # 48-step (or shorter, near the very end) look-ahead window from the
            # forecast CSV, starting at the current step -- Eq. (7)-(13).
            window_end = min(i + N_STEPS, len(load_fc_flat))
            p_load_win = load_fc_flat[i:window_end]
            p_pv_win   = pv_fc_flat[i:window_end]
            eta_win    = eta_flat[i:window_end]

            batt_traj, grid_traj, soc_traj, status, obj_val = solve_daily_qp(
                p_load_win, p_pv_win, eta_win,
                weight=args.weight,
                batt_power_kw=args.batt_power,
                capacity_kwh=args.capacity,
                soc0_kwh=soc_pred,
                solver=args.solver,
            )

            if status not in ("optimal", "optimal_inaccurate"):
                print(f"  WARNING: MPC status = {status} at step {step}; "
                      "applying zero battery command for this step.")
                p_bat_agg = 0.0
                soc_pred_next = soc_pred
                grid_forecast_kw = float(p_load_win[0] - p_pv_win[0])
            else:
                p_bat_agg = float(batt_traj[0])
                soc_pred_next = float(soc_traj[1])
                grid_forecast_kw = float(grid_traj[0])

            pbat_nodes = disaggregate_battery(p_bat_agg)

            payload = build_feeder_payload(node_data, i, pbat_nodes)
            modbus_write_feeder(conn, payload, args.dry_run, args.verbose)

            if not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                time.sleep(args.measurement_delay)
            measured_soc_646 = soc_logger.log_step()

            soc_pred = soc_pred_next
            soc_pred_pct = 100.0 * soc_pred / args.capacity

            load_act_i = float(total_load_act[i])
            pv_act_i   = float(total_pv_act[i])
            grid_act_i = load_act_i - pv_act_i - p_bat_agg

            sched_rows.append({
                "step": step, "day": day_num, "k": k,
                "p_load_fc_kw": round(float(p_load_win[0]), 4),
                "p_pv_fc_kw":   round(float(p_pv_win[0]), 4),
                "p_load_total_actual_kw": round(load_act_i, 4),
                "p_pv_total_actual_kw":   round(pv_act_i, 4),
                "baseline_grid_kw": round(load_act_i - pv_act_i, 4),
                "battery_agg_kw": round(p_bat_agg, 4),
                "battery_action": _action(p_bat_agg),
                "grid_kw": round(grid_act_i, 4),
                "grid_forecast_kw": round(grid_forecast_kw, 4),
                "soc_predicted_pct": round(soc_pred_pct, 4),
                "soc_measured_646_pct": "" if measured_soc_646 is None else round(float(measured_soc_646), 4),
                "mpc_status": status,
            })

            if args.verbose or (args.progress_every > 0 and
                                (step in (1, total_steps) or step % args.progress_every == 0)):
                print_step(step, day_num, k, load_act_i, pv_act_i, p_bat_agg,
                           grid_act_i, soc_pred_pct, measured_soc_646)

            if not args.no_wait and not args.dry_run:
                time.sleep(max(0.0, args.step_seconds - (time.time() - t0)))

    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")
        aborted = True

    finally:
        if args.keep_final:
            print("\nFinal HIL state kept (--keep-final).")
        else:
            print("\nClearing all registers ...")
            clear_all_registers(conn, args.dry_run)
        soc_logger.close()
        if conn is not None:
            conn.close()
        print("Done.")

    print("-" * len(_HDR))

    if sched_rows:
        sched_path = Path(f"mpc_feeder_schedule_{ts}.csv")
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        print(f"MPC schedule saved     : {sched_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()
