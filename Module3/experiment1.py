"""
Experiment 1 — QP: 
Implement the feeder-wide QP-based day-ahead battery scheduling algorithm as developed in Module 2 on the MIEEE-13NF. 
The QP algorithm will determine the aggregated battery charge/discharge schedule for the entire feeder, which is to 
	be disaggregated across the node-phase battery groups before being applied to the Typhoon HIL 101. 
The resulting battery charge/discharge commands are then played back over the 5-day playback period. 
Prepare the required feeder-wide measurement plots as specified in the following subsection.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

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
# 1. Settings  (All Nodes)
# ============================================================

N_STEPS      = 48
DELTA_HOURS  = 0.5
STEP_SECONDS = 2.0        # wall-clock seconds per 30-min data step

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


PHASE_MAP = {
    "A": "A",
    "B": "B",
    "C": "C",
    "Ph1": "A",
    "Ph2": "B",
    "Ph3": "C",
}

QREF_646_KVAR       = 132           # fixed Qref for Node 646 (kVAr, direct value)

N_CUSTOMERS = {
    "646_B": 102,
    "645_B": 63,
    "611_C": 68,
    "652_A": 46,

    "671_A": 159,
    "671_B": 155,
    "671_C": 159,

    "692_A": 0,
    "692_B": 0,
    "692_C": 66,

    "675_A": 191,
    "675_B": 36,
    "675_C": 119,

    "634_A": 69,
    "634_B": 45,
    "634_C": 52,
}

TOTAL_CUSTOMERS = sum(N_CUSTOMERS.values())   # 1330

BATTERY_CAPACITY_KWH = 10.0 * TOTAL_CUSTOMERS   # 13300 kWh
BATTERY_POWER_KW     = 5.0  * TOTAL_CUSTOMERS   # 6650 kW
INITIAL_SOC_KWH      = 0.5  * BATTERY_CAPACITY_KWH  # 6650 kWh

# Optional feeder bounds on grid power. Wide by default so the pure toy QP is
# just load-levelling; tighten with --p-upper / --p-lower if you want them to bind.
P_UPPER_KW = 1e6
P_LOWER_KW = -1e6

# --- Modbus -------------------------------------------------------------------
DEFAULT_HIL_IP   = "192.168.1.210"
DEFAULT_HIL_PORT = 502

HOLDING_START = 2000
HOLDING_COUNT = 64          # cleared to zero so no other node injects power

SIGNED_16BIT_MIN = -32768
SIGNED_16BIT_MAX = 32767

SOC_INPUT_REGISTER  = 3000  # Node 646 SoC, value = registers[0] / 100.0
SOC_INPUT_REGISTERS = {"soc_646_B_pct": SOC_INPUT_REGISTER}

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0


# ============================================================
# 2. Toy CSV loader (2-row wide format)
# ============================================================

def _pick_row(frame: pd.DataFrame, needle: str):
    for key in frame.index:
        if needle in str(key).lower():
            return key
    return None

def load_forecast_csv(path: Path):
    """Read the 2-row wide toy CSV and return per-day PV / load arrays.

    Returns
    -------
    pv_days   : np.ndarray (n_days, 48) kW
    load_days : np.ndarray (n_days, 48) kW
    n_days    : int
    """
    raw = pd.read_csv(path, header=None, index_col=0)
    raw.index = [str(i).strip() for i in raw.index]

    pv_key = _pick_row(raw, "pv")
    ld_key = _pick_row(raw, "load")

    if ld_key is None:
        raise ValueError("Could not find a 'P_load' row in the toy CSV.")

    if pv_key is None:
        # PV row lost its label (e.g. the stray '\'); it is the other numeric row.
        others = [k for k in raw.index if k != ld_key]
        if not others:
            raise ValueError("Could not find a PV row in the toy CSV.")
        pv_row = raw.loc[others[0]]
    else:
        pv_row = raw.loc[pv_key]

    pv   = pd.to_numeric(pv_row,          errors="coerce").to_numpy(float)
    load = pd.to_numeric(raw.loc[ld_key], errors="coerce").to_numpy(float)
    pv   = pv[~np.isnan(pv)]
    load = load[~np.isnan(load)]

    if len(pv) != len(load):
        raise ValueError(f"PV ({len(pv)}) and load ({len(load)}) lengths differ.")
    if len(pv) % N_STEPS != 0:
        raise ValueError(f"Expected a multiple of {N_STEPS} steps, got {len(pv)}.")

    n_days = len(pv) // N_STEPS
    return pv.reshape(n_days, N_STEPS), load.reshape(n_days, N_STEPS), n_days



def load_actual_feeder_csv(path: Path):
    df = pd.read_csv(path)

    time_cols = list(df.columns[5:53])

    dates = list(dict.fromkeys(df["Date"].astype(str)))
    n_days = len(dates)
    total_steps = n_days * N_STEPS

    node_data = {
        node: {
            "load_kw": np.zeros(total_steps),
            "pv_kw": np.zeros(total_steps),
        }
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

            values = pd.to_numeric(
                row[time_cols],
                errors="raise"
            ).to_numpy(dtype=float)

            start = day_i * N_STEPS
            end = start + N_STEPS

            if row["Profile"] == "GC_Load_kW":
                node_data[node_key]["load_kw"][start:end] = values

            elif row["Profile"] == "PV_Generation_kW":
                node_data[node_key]["pv_kw"][start:end] = values

            else:
                raise ValueError(
                    f"Unexpected Profile value: {row['Profile']}"
                )

    total_load = np.zeros(total_steps)
    total_pv = np.zeros(total_steps)

    for node in node_data:
        total_load += node_data[node]["load_kw"]
        total_pv += node_data[node]["pv_kw"]

    return node_data, total_load, total_pv, dates

# ============================================================
# 3. Toy QP  (minimize grid^2)
# ============================================================
def generate_eta_profiles(days, steps_per_day):
    """Generates the daily time-of-use tariff and copies it
       across the entire multi-day horizon."""
       
    eta_day = np.zeros(steps_per_day)
    eta_day[np.r_[0:14, 44:48]] = 0.03   # Off-peak rate ($/kWh)
    eta_day[np.r_[14:28, 40:44]] = 0.06  # Shoulder rate ($/kWh)
    eta_day[28:40]               = 0.30  # Peak rate ($/kWh)

    eta_profiles = np.tile(eta_day, days)
    return eta_profiles
    
def solve_daily_qp(
    p_load,
    p_pv,
    eta,
    weight,
    batt_power_kw,
    capacity_kwh,
    soc0_kwh,
    solver
):
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

        # Daily terminal condition
        soc[-1] == soc0_kwh,
    ]

    problem = cp.Problem(objective, constraints)
    problem.solve(
        solver=getattr(cp, solver),
        verbose=False
    )

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

def make_tariff():
    eta = np.zeros(N_STEPS)

    eta[np.r_[0:14, 44:48]] = 0.03
    eta[np.r_[14:28, 40:44]] = 0.06
    eta[28:40] = 0.30

    return eta
    
# ============================================================
# 4. Modbus connection + write helpers
# ============================================================

class ModbusConnection:
    """Live ModbusTcpClient with reconnect-on-failure (from the v7/v8 logic)."""

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

        values = [
            p_load,
            q_load,
            p_pv,
            p_bat,
        ]

        if config["order"] == "reversed":
            values.reverse()

        offset = config["start"] - HOLDING_START

        payload[offset:offset + 4] = [
            signed_to_register(v)
            for v in values
        ]

    return payload


def modbus_write_feeder(
    conn,
    payload,
    dry_run,
    verbose=False
):
    if len(payload) != 64:
        raise ValueError(
            f"Expected 64 Modbus registers, got {len(payload)}"
        )

    if dry_run:
        if verbose:
            print(f"[DRY-RUN] holding[2000:2064] = {payload}")
        return

    try:
        result = conn.client.write_registers(
            address=HOLDING_START,
            values=payload
        )

        if result is None or result.isError():
            raise IOError("write_registers returned error")

    except Exception as e:
        print(f"WARNING: Modbus write failed: {e}")
        conn.reconnect()

        result = conn.client.write_registers(
            address=HOLDING_START,
            values=payload
        )

        if result is None or result.isError():
            raise IOError(
                "Modbus write failed after reconnect"
            )

def clear_all_registers(conn: ModbusConnection, dry_run: bool) -> None:
    payload = [0] * HOLDING_COUNT
    if dry_run:
        print(f"    [DRY-RUN] clear holding[{HOLDING_START}:{HOLDING_START+HOLDING_COUNT}]")
        return
    result = conn.client.write_registers(address=HOLDING_START, values=payload)
    if result is None or result.isError():
        print(f"  WARNING: failed to clear registers "
              f"{HOLDING_START}-{HOLDING_START + HOLDING_COUNT - 1}.")
    else:
        print(f"  Registers {HOLDING_START}-{HOLDING_START + HOLDING_COUNT - 1} cleared.")


# ============================================================
# 5. SoC measurement logger (Node 646 only)
# ============================================================

def make_timestamped_path(path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.with_name(f"{path.stem}_{ts}{path.suffix}")


class SocLogger:
    """Read Node-646 SoC (input register 3000, value/100) each step and return
    it so callers can fold it into the schedule. Does NOT write a standalone
    SoC CSV -- the measured SoC lives only in toy_qp_schedule_<ts>.csv."""

    def __init__(self, conn: "ModbusConnection", enabled: bool):
        self.conn = conn
        self.enabled = enabled
        self.path = None            # kept for API compatibility; no file is written

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
            print(f"  SoC register {SOC_INPUT_REGISTER} resolved (logged into schedule only).")
        except Exception:
            print(f"  WARNING: SoC register {SOC_INPUT_REGISTER} did not read back; "
                  "soc_measured_pct will be blank.")

    def log_step(self, step: int, day: int, step_of_day: int):
        """Read SoC and return the value (float %). None when disabled
        (e.g. dry-run) or the read fails."""
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

def print_day_summary(day_num, batt_kw, grid_kw, p_load, p_pv, status, obj_val):
    base_g = p_load - p_pv
    W = 74
    print("=" * W)
    print(f"ECE4191 Module 3 -- Node-646 Toy QP  |  Day {day_num}")
    print("=" * W)
    print(f"  Customers / capacity   : {N_CUSTOMERS_646}  /  {BATTERY_CAPACITY_KWH:,.0f} kWh")
    print(f"  Battery power limit    : +/- {BATTERY_POWER_KW:,.0f} kW")
    print(f"  Initial SoC            : {INITIAL_SOC_KWH:,.0f} kWh "
          f"({100*INITIAL_SOC_KWH/BATTERY_CAPACITY_KWH:.0f}%)")
    print(f"  Solver status          : {status}")
    print(f"  Objective sum(grid^2)  : {obj_val:,.2f}")
    print(f"  Baseline grid range    : {base_g.min():.1f} to {base_g.max():.1f} kW")
    print(f"  QP grid range          : {grid_kw.min():.1f} to {grid_kw.max():.1f} kW  "
          f"(mean {grid_kw.mean():.1f})")
    print(f"  Peak reduction         : {base_g.max() - grid_kw.max():.1f} kW")
    print(f"  Battery range          : {batt_kw.min():.1f} to {batt_kw.max():.1f} kW")
    print("=" * W)


_HDR = (f"{'Step':>4} {'Load kW':>9} {'PV kW':>8} {'Net kW':>8} "
        f"{'Batt kW':>10} {'Action':>10} {'Grid kW':>10} "
        f"{'SoC% pred':>10} {'SoC% meas':>10}")


def print_step(step, load, pv, batt, grid, soc_pred, soc_meas):
    meas = f"{soc_meas:10.2f}" if soc_meas is not None else f"{'-':>10}"
    print(f"{step:4d} {load:9.1f} {pv:8.1f} {load-pv:8.1f} "
          f"{batt:10.2f} {_action(batt):>10} {grid:10.2f} "
          f"{soc_pred:10.2f} {meas}")

def disaggregate_battery(pbat_aggregate_kw: float):
    return {
        node: pbat_aggregate_kw * N_CUSTOMERS[node] / TOTAL_CUSTOMERS
        for node in N_CUSTOMERS
    }

# ============================================================
# 7. Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ECE4191 Module 3 -- Node-646 toy QP over Modbus TCP (Raspberry Pi)"
    )
    parser.add_argument("--input",        default="Code_and_data/central_agg_forecast_data_students.csv",
                        help="Forecast CSV (drives the QP / battery scheduling).")
    parser.add_argument("--actual",       default="Code_and_data/agg_jan2013_students.csv",
                        help="Actual CSV (load/PV fed to Node 646; sets the optimised grid).")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS)
    parser.add_argument("--batt-power",   type=float, default=BATTERY_POWER_KW,
                        help=f"Battery power limit in kW (default {BATTERY_POWER_KW:.0f}).")
    parser.add_argument("--capacity",     type=float, default=BATTERY_CAPACITY_KWH,
                        help=f"Battery capacity in kWh (default {BATTERY_CAPACITY_KWH:.0f}).")
    parser.add_argument("--initial-soc",  type=float, default=INITIAL_SOC_KWH,
                        help=f"Initial SoC in kWh (default {INITIAL_SOC_KWH:.0f} = 50%%).")
    parser.add_argument("--p-upper",      type=float, default=P_UPPER_KW)
    parser.add_argument("--p-lower",      type=float, default=P_LOWER_KW)
    parser.add_argument("--solver",       default="OSQP")
    parser.add_argument("--no-wait",      action="store_true",
                        help="Skip sleep between steps (fast test mode).")
    parser.add_argument("--no-prompt",    action="store_true",
                        help="Skip pre-start confirmation prompt.")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Run without connecting to the HIL.")
    parser.add_argument("--keep-final",   action="store_true",
                        help="Leave final values on the HIL after playback ends.")
    parser.add_argument("--ip",   default=DEFAULT_HIL_IP)
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

    # ── Load forecast + actual CSVs ───────────────────────────────────────────
    csv_path = Path(args.input)
    if not csv_path.exists():
        raise FileNotFoundError(f"Forecast CSV not found: {csv_path}")
    act_path = Path(args.actual)
    if not act_path.exists():
        raise FileNotFoundError(f"Actual CSV not found: {act_path}")

    print(f"\nLoading forecast CSV: {csv_path.name}")
    pv_days, load_days, n_days = load_forecast_csv(csv_path)
    
    print(f"Loading actual   CSV: {act_path.name}")
    pv_act_days, load_act_days, n_days_act = load_actual_csv(act_path)

    if n_days_act != n_days:
        raise ValueError(
            f"Forecast has {n_days} day(s) but actual has {n_days_act}; they must match."
        )

    total_steps = n_days * N_STEPS
    print(f"  Days: {n_days}   Steps/day: {N_STEPS}   Total steps: {total_steps}")

    # ── Banner ────────────────────────────────────────────────────────────────
    print("=" * 74)
    print("ECE4191 Module 3  |  Node-646 Toy QP Playback (Modbus TCP)")
    print("=" * 74)
    print(f"  HIL target   : {args.ip}:{args.port}")
    print(f"  Forecast CSV : {Path(args.input).name}  (QP / scheduling)")
    print(f"  Actual   CSV : {Path(args.actual).name}  (fed to Node 646)")
    print(f"  Node         : {NODE_LABEL[0]} phase {NODE_LABEL[1]}  "
          f"(holding {NODE_REGISTER_START}-{NODE_REGISTER_START+3}, {NODE_REGISTER_ORDER})")
    print(f"  Capacity     : {args.capacity:,.0f} kWh   Power: +/-{args.batt_power:,.0f} kW")
    print(f"  Objective    : minimize sum(grid^2)")
    if args.dry_run:
        print("  *** DRY-RUN MODE -- no Modbus writes will occur ***")
    print("=" * 74)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. Model compiled and running in Typhoon HIL Control Center.")
        print("  2. SCADA open; Control Type = REMOTE CONTROL.")
        print("  3. BusSplitMap holding registers 2000-2063 enabled.")
        print("  4. SoC starts each day at 50% in the optimisation.")
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

    # ── SoC reader (into schedule only) ───────────────────────────────────────
    log_enabled = not args.no_measurements and not args.dry_run
    soc_logger = SocLogger(conn, log_enabled)
    soc_logger.start()

    # ── Playback ──────────────────────────────────────────────────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False

    if args.verbose or args.progress_every > 0:
        print(_HDR)
        print("-" * len(_HDR))

    try:
        for day_num in range(1, n_days + 1):
            # Forecast (QP inputs) -- battery scheduling is derived from these.
            p_load = load_days[day_num - 1]
            p_pv   = pv_days[day_num - 1]
            # Actual (fed to the HIL) -- what Node 646 actually sees.
            p_load_act = load_act_days[day_num - 1]
            p_pv_act   = pv_act_days[day_num - 1]

            print(f"\n[Day {day_num}/{n_days}] solving toy QP on forecast ...")
            batt_kw, grid_kw, status, obj_val = solve_toy_qp(
                p_load, p_pv,
                batt_power_kw=args.batt_power,
                capacity_kwh=args.capacity,
                soc0_kwh=args.initial_soc,
                p_upper_kw=args.p_upper,
                p_lower_kw=args.p_lower,
                solver=args.solver,
            )
            if status not in ("optimal", "optimal_inaccurate"):
                print(f"  ERROR: QP status = {status} for day {day_num}. Skipping.")
                continue

            # X1 = battery command from the forecast QP (this is what we keep).
            # The forecast grid (grid_kw = X2 on forecast) is discarded; the
            # optimised grid power is recomputed against the ACTUAL load/PV.
            grid_act = p_load_act - p_pv_act - batt_kw

            print_day_summary(day_num, batt_kw, grid_kw, p_load, p_pv, status, obj_val)
            print(f"  Actual grid range      : {grid_act.min():.1f} to {grid_act.max():.1f} kW  "
                  f"(mean {grid_act.mean():.1f})")

            # SoC trajectory for logging in the schedule CSV (from the X1 command)
            soc_traj = args.initial_soc - np.cumsum(batt_kw * DELTA_HOURS)

            for k in range(N_STEPS):
                t0 = time.time()
                step = (day_num - 1) * N_STEPS + k + 1

                # Feed ACTUAL load/PV to Node 646; battery command is the QP's X1.
                payload = build_node_payload(
                    pref_kw   = float(p_load_act[k]),  # Pref  (kW)  actual load
                    qref_kvar = QREF_646_KVAR,         # Qref  (kVAr)
                    pv_kw     = float(p_pv_act[k]),    # PV    (kW)  actual PV
                    batt_kw   = float(batt_kw[k]),     # Batt  (kW, discharge +ve)
                )
                modbus_write_node(conn, payload, args.dry_run, args.verbose)

                if not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                    time.sleep(args.measurement_delay)
                measured_soc = soc_logger.log_step(step=step, day=day_num, step_of_day=k)

                soc_pct = 100.0 * float(soc_traj[k]) / args.capacity
                sched_rows.append({
                    "step":                step,
                    # forecast inputs the QP scheduled against
                    "p_load_fc_kw":        round(float(p_load[k]),     4),
                    "p_pv_fc_kw":          round(float(p_pv[k]),       4),
                    # actual inputs fed to Node 646
                    "p_load_kw":           round(float(p_load_act[k]), 4),
                    "p_pv_kw":             round(float(p_pv_act[k]),   4),
                    "baseline_grid_kw":    round(float(p_load_act[k] - p_pv_act[k]), 4),
                    # X1 = battery command (forecast QP), X2 = optimised grid on ACTUAL
                    "X1_battery_kw":       round(float(batt_kw[k]), 4),
                    "battery_action":      _action(batt_kw[k]),
                    "X2_grid_kw":          round(float(grid_act[k]), 4),
                    "X2_grid_forecast_kw": round(float(grid_kw[k]),  4),
                    "soc_predicted_pct":   round(soc_pct, 4),
                    "soc_measured_pct":    "" if measured_soc is None else round(float(measured_soc), 4),
                })

                if args.verbose or (args.progress_every > 0 and
                                    (step in (1, total_steps) or step % args.progress_every == 0)):
                    print_step(step, float(p_load_act[k]), float(p_pv_act[k]),
                               float(batt_kw[k]), float(grid_act[k]),
                               soc_pct, measured_soc)

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

    # ── Save schedule ─────────────────────────────────────────────────────────
    if sched_rows:
        sched_path = Path(f"toy_qp_schedule_{ts}.csv")
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        print(f"QP schedule saved     : {sched_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()
