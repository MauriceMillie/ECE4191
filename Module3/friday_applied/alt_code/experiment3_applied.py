"""
Experiment 3 -- MPC-CIL:
Implement a Controller-in-the-Loop (CIL) MPC experiment for the battery at Node 646
(Phase B), using the objective function developed in Module 2. The entire MIEEE-13NF
remains in operation, with load, PV generation and reactive-power inputs applied across
all node-phase combinations. However, ONLY the battery at Node 646 (Phase B) is
controlled via the CIL MPC algorithm; the battery commands at all other node-phase
combinations are set to zero. At each time step t, the MEASURED Node 646 battery SoC is
read from the Typhoon HIL 101 (Modbus input register 3000) to update the initial
state-of-charge input to the MPC algorithm -- this is the "controller-in-the-loop"
feedback path shown in Figure 14 of the Module 3 manual.

This script is a direct adaptation of experiment1.py (feeder-wide QP) and
experiment2.py (feeder-wide MPC), but narrowed to a single controllable battery:

    1. All 16 node-phase combinations still receive their real-time actual load and
       PV signals every step (the feeder keeps running exactly as in Experiment 1/2).
    2. Every node's battery command is written as 0 kW EXCEPT Node 646 (Phase B),
       whose command comes from a receding-horizon MPC solve that uses NODE 646's own
       10 kWh/customer-equivalent battery parameters (capacity 1020 kWh, +/-510 kW,
       initial SoC 510 kWh/50%) -- the same design parameters used for the guided
       toy QP/MPC walkthrough in Section 7 of the manual.
    3. Unlike Experiment 2, the initial SoC fed into EVERY MPC solve is the *measured*
       SoC read back from Modbus input register 3000 at the end of the previous step
       (Eq. 13: SoC(t|t) = SoC(t)), not a purely model-predicted value. This is what
       makes the experiment "controller-in-the-loop": measurement error / battery-model
       mismatch on the real HIL battery is fed back into the next optimisation.
    4. The playback period defaults to 4 days (192 steps), matching Experiment 2 and
       Experiment 3 in Section 8 of the manual.

ASSUMPTIONS / TODOs the group should check before submitting:
    * QREF_MAP: as in experiment1.py/experiment2.py, only Node 646's reactive power
      (132 kVAr) is specified by the manual; every other node defaults to 0 kVAr.
      Update QREF_MAP if your data supplies real per-node reactive power.
    * NODE-646 FORECAST: the MPC needs a day-ahead load/PV forecast for Node 646
      specifically (not the feeder aggregate). If you have a genuine Node-646 forecast
      CSV (2-row wide format, e.g. an extended version of
      toy_example_N646_students.csv covering the full playback + 1 lookahead day),
      pass it with --forecast. If you don't supply one, the script falls back to a
      PERFECT-FORECAST assumption (Pˆload = Pload, PˆPV = PPV, taken directly from the
      actual Node-646 data) -- the manual explicitly allows this simplification
      ("Notation Mapping" / Section 4), but note it will make the MPC look artificially
      good since it always knows the future perfectly. Swap in a real forecast file
      for a more meaningful comparison against Experiment 2.
"""
from __future__ import annotations

import argparse
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
# 1. Settings (all nodes) -- identical to experiment1.py / experiment2.py
# ============================================================

N_STEPS      = 48
DELTA_HOURS  = 0.5
STEP_SECONDS = 2.0

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
    "A": "A", "B": "B", "C": "C",
    "Ph1": "A", "Ph2": "B", "Ph3": "C",
}

CIL_NODE = "646_B"

QREF_646_KVAR = 132
QREF_MAP = {node: 0.0 for node in NODE_MAP}
QREF_MAP[CIL_NODE] = QREF_646_KVAR

# Node-646-specific battery parameters (from Section 7's guided toy walkthrough).
# NOTE: these are independent of the aggregate 1330-customer feeder battery used
# in Experiments 1 and 2.
NODE646_CAPACITY_KWH  = 1020.0
NODE646_BATT_POWER_KW = 510.0
NODE646_INITIAL_SOC_KWH = 510.0   # 50%

DEFAULT_WEIGHT = 0.01

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

DEFAULT_PLAYBACK_DAYS = 4


# ============================================================
# 2. CSV loaders
# ============================================================

def _pick_row(frame: pd.DataFrame, needle: str):
    for key in frame.index:
        if needle in str(key).lower():
            return key
    return None


def load_forecast_csv(path: Path):
    """Read a 2-row wide load/PV forecast CSV (same format as
    toy_example_N646_students.csv) and return per-day arrays (kW), shape (n_days, 48)."""
    raw = pd.read_csv(path, header=None, index_col=0)
    raw.index = [str(i).strip() for i in raw.index]

    pv_key = _pick_row(raw, "pv")
    ld_key = _pick_row(raw, "load")
    if ld_key is None:
        raise ValueError("Could not find a 'P_load' row in the forecast CSV.")
    if pv_key is None:
        others = [k for k in raw.index if k != ld_key]
        if not others:
            raise ValueError("Could not find a PV row in the forecast CSV.")
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
# 3. Tariff, QP/MPC solver
# ============================================================

def make_eta_array(n_steps_total: int) -> np.ndarray:
    pattern = np.zeros(N_STEPS)
    pattern[np.r_[0:14, 44:48]] = 0.03
    pattern[np.r_[14:28, 40:44]] = 0.06
    pattern[28:40] = 0.30
    reps = int(np.ceil(n_steps_total / N_STEPS)) + 1
    return np.tile(pattern, reps)[:n_steps_total]


def pad_to_length(arr: np.ndarray, target_len: int) -> np.ndarray:
    """Extend `arr` to at least `target_len` samples by repeating its final 24 h
    block, so the MPC look-ahead window never runs off the end of the data."""
    if len(arr) >= target_len:
        return arr
    if len(arr) == 0:
        return np.zeros(target_len)
    pad_block = arr[-N_STEPS:] if len(arr) >= N_STEPS else arr[-1:]
    out = arr.copy()
    while len(out) < target_len:
        out = np.concatenate([out, pad_block])
    return out[:target_len]


def solve_daily_qp(p_load, p_pv, eta, weight, batt_power_kw, capacity_kwh,
                    soc0_kwh, solver):
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
    """pbat_nodes must supply a value for every node in NODE_MAP -- in Experiment 3
    every entry other than CIL_NODE ('646_B') should be 0.0."""
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


def read_node646_soc_pct(conn) -> float | None:
    """Read Node 646's measured SoC (%) from Modbus input register 3000."""
    try:
        rr = conn.client.read_input_registers(address=SOC_INPUT_REGISTER, count=1)
        if rr is None or rr.isError():
            raise IOError(f"Failed to read SoC input register {SOC_INPUT_REGISTER}")
        return rr.registers[0] / 100.0
    except Exception:
        return None


# ============================================================
# 5. Console output
# ============================================================

_HDR = (f"{'Step':>5} {'Day':>3} {'k':>3} {'Load646':>8} {'PV646':>7} "
        f"{'Batt646':>8} {'Action':>10} {'Grid646':>9} "
        f"{'SoC%pred':>9} {'SoC%meas':>9}")


def print_step(step, day, k, load, pv, batt, grid, soc_pred, soc_meas):
    meas = f"{soc_meas:9.2f}" if soc_meas is not None else f"{'-':>9}"
    print(f"{step:5d} {day:3d} {k:3d} {load:8.1f} {pv:7.1f} "
          f"{batt:8.2f} {_action(batt):>10} {grid:9.2f} "
          f"{soc_pred:9.2f} {meas}")


# ============================================================
# 6. Main -- Node 646 controller-in-the-loop MPC
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ECE4191 Module 3 -- Experiment 3: Node 646 CIL MPC over Modbus TCP"
    )
    parser.add_argument("--forecast", default=None,
                        help="Node-646-specific day-ahead forecast CSV (2-row wide "
                             "format). If omitted, a perfect-forecast assumption is "
                             "used (forecast = actual Node 646 data).")
    parser.add_argument("--actual", default="agg_jan2013_students.csv",
                        help="Per-node actual load/PV CSV (fed to the whole feeder).")
    parser.add_argument("--playback-days", type=int, default=DEFAULT_PLAYBACK_DAYS,
                        help=f"Number of days to play back (default {DEFAULT_PLAYBACK_DAYS}).")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS)
    parser.add_argument("--weight", type=float, default=DEFAULT_WEIGHT,
                        help=f"QP objective weight w (default {DEFAULT_WEIGHT}).")
    parser.add_argument("--node646-capacity", type=float, default=NODE646_CAPACITY_KWH,
                        help=f"Node 646 battery capacity in kWh (default {NODE646_CAPACITY_KWH:.0f}).")
    parser.add_argument("--node646-batt-power", type=float, default=NODE646_BATT_POWER_KW,
                        help=f"Node 646 battery power limit in kW (default {NODE646_BATT_POWER_KW:.0f}).")
    parser.add_argument("--node646-initial-soc", type=float, default=NODE646_INITIAL_SOC_KWH,
                        help=f"Fallback initial SoC in kWh if the first Modbus read "
                             f"fails or --dry-run is used (default {NODE646_INITIAL_SOC_KWH:.0f} = 50%%).")
    parser.add_argument("--solver", default="OSQP")
    parser.add_argument("--no-wait", action="store_true")
    parser.add_argument("--no-prompt", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-final", action="store_true")
    parser.add_argument("--ip", default=DEFAULT_HIL_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_HIL_PORT)
    parser.add_argument("--measurement-delay", type=float, default=0.2,
                        help="Seconds to wait after a write before reading the CIL SoC feedback.")
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # ── Connect ───────────────────────────────────────────────────────────────
    conn = None
    if not args.dry_run:
        conn = ModbusConnection(args.ip, args.port)
        print(f"\nConnecting to HIL Modbus server at {args.ip}:{args.port} ...")
        conn.connect()
        print("  Connected.")

    # ── Load the full-feeder actual CSV (drives all 16 nodes) ───────────────────
    act_path = Path(args.actual)
    if not act_path.exists():
        raise FileNotFoundError(f"Actual CSV not found: {act_path}")

    print(f"\nLoading actual   CSV: {act_path.name}")
    node_data, total_load_act, total_pv_act, dates = load_actual_feeder_csv(act_path)
    n_days_act = len(dates)

    playback_days = min(args.playback_days, n_days_act)
    total_steps = playback_days * N_STEPS
    print(f"  Actual days available   : {n_days_act}")
    print(f"  Playback days used      : {playback_days}  ({total_steps} steps)")

    load646_act = node_data[CIL_NODE]["load_kw"]
    pv646_act   = node_data[CIL_NODE]["pv_kw"]

    # ── Node-646 forecast (real file, or perfect-forecast fallback) ────────────
    if args.forecast is not None:
        fc_path = Path(args.forecast)
        if not fc_path.exists():
            raise FileNotFoundError(f"Node-646 forecast CSV not found: {fc_path}")
        print(f"Loading forecast CSV: {fc_path.name}  (Node 646 specific)")
        pv_days, load_days, n_days_fc = load_forecast_csv(fc_path)
        load646_fc = load_days.flatten()
        pv646_fc   = pv_days.flatten()
    else:
        print("No --forecast supplied: assuming PERFECT FORECAST "
              "(Pˆload = Pload, PˆPV = PPV) from the actual Node 646 data.")
        load646_fc = load646_act.copy()
        pv646_fc   = pv646_act.copy()

    needed_len = total_steps + N_STEPS
    if len(load646_fc) < needed_len:
        load646_fc = pad_to_length(load646_fc, needed_len)
        pv646_fc   = pad_to_length(pv646_fc,   needed_len)

    eta_flat = make_eta_array(needed_len)

    # ── Banner ────────────────────────────────────────────────────────────────
    print("=" * 78)
    print("ECE4191 Module 3  |  Experiment 3 -- Node 646 CIL MPC Playback (Modbus TCP)")
    print("=" * 78)
    print(f"  HIL target        : {args.ip}:{args.port}")
    print(f"  Actual CSV        : {act_path.name}  (all 16 nodes driven; only 646 has a battery)")
    print(f"  Node 646 battery  : {args.node646_capacity:,.0f} kWh   "
          f"+/-{args.node646_batt_power:,.0f} kW")
    print(f"  Objective weight  : w = {args.weight}")
    print(f"  Playback period   : {playback_days} day(s), {total_steps} steps")
    if args.dry_run:
        print("  *** DRY-RUN MODE -- no Modbus writes will occur ***")
    print("=" * 78)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. Model compiled and running in Typhoon HIL Control Center.")
        print("  2. SCADA open; Control Type = REMOTE CONTROL.")
        print("  3. BusSplitMap holding registers 2000-2063 enabled.")
        print("  4. Only Node 646 has an operational battery for this experiment.")
        print("  5. Voltage/active-power Signal Analyzer export ready (see Appendix B).")
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

    # ── Initial SoC: read the real measurement if we can (CIL feedback) ────────
    soc0_kwh = args.node646_initial_soc
    if not args.dry_run:
        pct = read_node646_soc_pct(conn)
        if pct is not None:
            soc0_kwh = pct / 100.0 * args.node646_capacity
            print(f"  Initial Node-646 SoC read from HIL: {pct:.2f}%  ({soc0_kwh:.1f} kWh).")
        else:
            print(f"  WARNING: could not read initial Node-646 SoC; "
                  f"falling back to {args.node646_initial_soc:.0f} kWh.")

    # ── Receding-horizon CIL MPC playback ───────────────────────────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False

    if args.verbose or args.progress_every > 0:
        print(_HDR)
        print("-" * len(_HDR))

    try:
        for i in range(total_steps):
            t0 = time.time()
            step = i + 1
            day_num = (i // N_STEPS) + 1
            k = (i % N_STEPS) + 1

            window_end = min(i + N_STEPS, len(load646_fc))
            p_load_win = load646_fc[i:window_end]
            p_pv_win   = pv646_fc[i:window_end]
            eta_win    = eta_flat[i:window_end]

            batt_traj, grid_traj, soc_traj, status, obj_val = solve_daily_qp(
                p_load_win, p_pv_win, eta_win,
                weight=args.weight,
                batt_power_kw=args.node646_batt_power,
                capacity_kwh=args.node646_capacity,
                soc0_kwh=soc0_kwh,
                solver=args.solver,
            )

            if status not in ("optimal", "optimal_inaccurate"):
                print(f"  WARNING: MPC status = {status} at step {step}; "
                      "applying zero battery command for this step.")
                p_bat_646 = 0.0
                soc_pred_next_kwh = soc0_kwh
                grid_forecast_kw = float(p_load_win[0] - p_pv_win[0])
            else:
                p_bat_646 = float(batt_traj[0])
                soc_pred_next_kwh = float(soc_traj[1])
                grid_forecast_kw = float(grid_traj[0])

            # Only Node 646 gets a nonzero battery command; every other node is 0 kW,
            # i.e. no CIL/battery functionality at any other node (Section 4).
            pbat_nodes = {node: 0.0 for node in NODE_MAP}
            pbat_nodes[CIL_NODE] = p_bat_646

            payload = build_feeder_payload(node_data, i, pbat_nodes)
            modbus_write_feeder(conn, payload, args.dry_run, args.verbose)

            if not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                time.sleep(args.measurement_delay)

            # CIL feedback: read the REAL Node 646 SoC and use it as SoC(t|t) for the
            # next MPC solve (Eq. 13). Fall back to the model-predicted value only if
            # the read fails (or in --dry-run, where there is no live HIL to read).
            measured_soc_pct = None if args.dry_run else read_node646_soc_pct(conn)
            if measured_soc_pct is not None:
                soc0_kwh = measured_soc_pct / 100.0 * args.node646_capacity
            else:
                soc0_kwh = soc_pred_next_kwh

            soc_pred_pct = 100.0 * soc_pred_next_kwh / args.node646_capacity

            load_act_i = float(load646_act[i])
            pv_act_i   = float(pv646_act[i])
            grid_646_actual_kw = load_act_i - pv_act_i - p_bat_646

            total_load_i = float(total_load_act[i])
            total_pv_i   = float(total_pv_act[i])

            sched_rows.append({
                "step": step, "day": day_num, "k": k,
                "p_load_fc_646_kw": round(float(p_load_win[0]), 4),
                "p_pv_fc_646_kw":   round(float(p_pv_win[0]), 4),
                "p_load_646_kw":    round(load_act_i, 4),
                "p_pv_646_kw":      round(pv_act_i, 4),
                "baseline_grid_646_kw": round(load_act_i - pv_act_i, 4),
                "battery_646_kw": round(p_bat_646, 4),
                "battery_action": _action(p_bat_646),
                "grid_646_kw": round(grid_646_actual_kw, 4),
                "grid_646_forecast_kw": round(grid_forecast_kw, 4),
                "soc_predicted_pct": round(soc_pred_pct, 4),
                "soc_measured_pct": "" if measured_soc_pct is None else round(float(measured_soc_pct), 4),
                "feeder_baseline_grid_kw": round(total_load_i - total_pv_i, 4),
                "feeder_grid_with_cil_kw": round(total_load_i - total_pv_i - p_bat_646, 4),
                "mpc_status": status,
            })

            if args.verbose or (args.progress_every > 0 and
                                (step in (1, total_steps) or step % args.progress_every == 0)):
                print_step(step, day_num, k, load_act_i, pv_act_i, p_bat_646,
                           grid_646_actual_kw, soc_pred_pct, measured_soc_pct)

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
        if conn is not None:
            conn.close()
        print("Done.")

    print("-" * len(_HDR))

    if sched_rows:
        sched_path = Path(f"mpc_cil_node646_schedule_{ts}.csv")
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        print(f"MPC-CIL schedule saved : {sched_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()
