#!/usr/bin/env python3
"""
ECE4191 Module 3 -- Node-646 Toy MPC (receding horizon) over Modbus TCP
=======================================================================

Single-node (Node 646) receding-horizon MPC counterpart of
``central_qp_modbus_toy_n646.py``, for "triangle / square" unit test.
Same input CSV, same Node-646 register map, same trimmed output columns as the
toy QP -- the only difference is the controller.

D-RHO controller (per Ratnam & Weller, Section 3.1) -- CLOSED LOOP
------------------------------------------------------------------
At each executed half-hour step j the same load-levelling QP is solved over a
rolling look-ahead window of length H (default 48 steps = 24 h) starting at j,
and ONLY the first action batt[0] is applied; the horizon then rolls forward
one step. The initial state ``soc0`` for each solve is the MEASURED Node-646 SoC
read back from input register 3000 that step (not the algorithm's own predicted
SoC) -- i.e. the loop is closed through the HIL. In --dry-run the SoC is
simulated internally so the loop still runs. If a live read fails, the step
falls back to the internal model SoC. The daily terminal SoC constraint
(``sum(batt) == 0``) is NOT enforced -- SoC is only bounded 0 <= SoC <= C.
(This is the one structural difference from the toy QP, which fixes SoC back to
50% each day.)

The schedule still logs an independent open-loop model SoC as ``soc_predicted_pct``
alongside ``soc_measured_pct`` purely as a tracking diagnostic; only the measured
value feeds the solver.

    minimize   sum_squares(grid_win)          # load-levelling, "x^2 only"
    s.t.       grid_win == load_win - pv_win - batt_win
               -Pb <= batt_win <= Pb
               0   <= soc0 - cumsum(batt_win*dt) <= C
               [ p_lower <= grid_win <= p_upper ]     (optional feeder bounds)

Forecast vs actual (this variant)
---------------------------------
The horizon QP is solved on the FORECAST CSV (``--input``); only the first
action of each solve is applied, giving the battery command X1 = batt[0].
That solve's forecast grid (X2) is discarded. The ACTUAL CSV (``--actual``)
supplies the load/PV written to Node 646, and the optimised grid power is
recomputed against the actual data:
    X2 = P_load - P_PV - batt        (actual load/PV, forecast batt command).
The SoC feedback loop is unchanged -- soc0 for each solve is still the
MEASURED Node-646 SoC.

One-day output
--------------
The MPC plays back only day 1 (48 steps). With the 96-step (2-day) toy CSV,
    playback = forecast_steps - horizon = 96 - 48 = 48 steps  (= day 1).
Every played-back step therefore has a FULL 24-hour (48-step) rolling look-ahead
window; day 2 is never executed -- it exists only as the predicted forecast that
the horizon reaches into for the back half of day 1. The written schedule and
output CSV cover exactly ONE day (48 steps).

Node 646 : 102 customers -> 1020 kWh capacity, +/-510 kW power (5 kW/customer),
           initial SoC 510 kWh (50%). Battery sign: +ve = discharge, direct kW,
           no *1000, no sign flip.  SoC read from input register 3000 (/100).

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
# 1. Settings  (Node 646 only)
# ============================================================

N_STEPS      = 48         # executed (played-back) steps = 1 day
DELTA_HOURS  = 0.5
STEP_SECONDS = 2.0        # wall-clock seconds per 30-min data step
HORIZON_STEPS_DEFAULT = 48   # 24-hour rolling look-ahead window (D-RHO, s = 48)

# --- Node 646 -----------------------------------------------------------------
NODE_LABEL          = ("646", "B")
NODE_REGISTER_START = 2000          # holding 2000..2003
NODE_REGISTER_ORDER = "normal"      # [Pref, Qref, PV, Batt]
QREF_646_KVAR       = 132           # fixed Qref for Node 646 (kVAr, direct value)

N_CUSTOMERS_646      = 102
BATTERY_CAPACITY_KWH = 10.0 * N_CUSTOMERS_646   # 1020 kWh
BATTERY_POWER_KW     = 5.0  * N_CUSTOMERS_646   # 510 kW  (derived; --batt-power)
INITIAL_SOC_KWH      = 0.5  * BATTERY_CAPACITY_KWH   # 510 kWh (50%)

# Optional feeder bounds on grid power. Wide by default (pure load-levelling toy).
P_UPPER_KW = 1e6
P_LOWER_KW = -1e6

# --- Modbus -------------------------------------------------------------------
DEFAULT_HIL_IP   = "192.168.1.210"
DEFAULT_HIL_PORT = 502

HOLDING_START = 2000
HOLDING_COUNT = 64          # cleared to zero so no other node injects power

SIGNED_16BIT_MIN = -32768
SIGNED_16BIT_MAX = 32767

SOC_INPUT_REGISTER = 3000   # Node 646 SoC, value = registers[0] / 100.0

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0


# ============================================================
# 2. Toy CSV loader (2-row wide format -> flat 2-day series)
# ============================================================

def _pick_row(frame: pd.DataFrame, needle: str):
    for key in frame.index:
        if needle in str(key).lower():
            return key
    return None


def load_toy_series(path: Path):
    """Read the 2-row wide toy CSV and return flat continuous series.

    Returns
    -------
    p_load : np.ndarray (n,) kW      (n = 96 for the 2-day toy)
    p_pv   : np.ndarray (n,) kW
    """
    raw = pd.read_csv(path, header=None, index_col=0)
    raw.index = [str(i).strip() for i in raw.index]

    ld_key = _pick_row(raw, "load")
    if ld_key is None:
        raise ValueError("Could not find a 'P_load' row in the toy CSV.")
    pv_key = _pick_row(raw, "pv")
    if pv_key is None:
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
    return load, pv


# ============================================================
# 3. Receding-horizon MPC (minimize grid^2, no terminal SoC)
# ============================================================

def solve_mpc_horizon(load_win, pv_win, soc0, capacity_kwh, batt_lim,
                      p_upper_kw, p_lower_kw, solver):
    """Solve the load-levelling QP over one look-ahead window and return the
    full open-loop sequence (only element [0] is applied by the loop)."""
    H    = len(load_win)
    batt = cp.Variable(H)
    grid = cp.Variable(H)

    soc_after = soc0 - cp.cumsum(batt * DELTA_HOURS)

    constraints = [
        grid == load_win - pv_win - batt,   # A2: grid definition
        batt <=  batt_lim,                  # A1
        batt >= -batt_lim,                  # A1
        soc_after >= 0.0,                   # A1
        soc_after <= capacity_kwh,          # A1
        grid <= p_upper_kw,                 # A1 (wide by default)
        grid >= p_lower_kw,                 # A1
        # NOTE: no sum(batt) == 0 terminal constraint (D-RHO online procedure).
    ]

    prob = cp.Problem(cp.Minimize(cp.sum_squares(grid)), constraints)
    prob.solve(solver=getattr(cp, solver), verbose=False)

    if batt.value is None:
        # Rare with box constraints only; fall back to "do nothing" this step.
        return np.zeros(H), (load_win - pv_win), "solver_failed"
    return (np.asarray(batt.value, float).flatten(),
            np.asarray(grid.value, float).flatten(),
            str(prob.status))


# NOTE: the receding-horizon MPC is now run CLOSED-LOOP inside main()'s playback
# loop. At each step the measured Node-646 SoC is read back from register 3000
# and used as soc0 for that step's horizon solve (see the playback loop below).
# There is no up-front open-loop schedule computation.



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


def build_node_payload(pref_kw: float, qref_kvar: float,
                       pv_kw: float, batt_kw: float) -> list:
    """4-register payload for Node 646 in NODE_REGISTER_ORDER."""
    regs = [pref_kw, qref_kvar, pv_kw, batt_kw]        # normal: [Pref, Qref, PV, Batt]
    if NODE_REGISTER_ORDER == "reversed":
        regs = list(reversed(regs))
    return [signed_to_register(v) for v in regs]


def modbus_write_node(conn: ModbusConnection, payload: list,
                      dry_run: bool, verbose: bool = False) -> None:
    if dry_run:
        if verbose:
            print(f"    [DRY-RUN] holding[{NODE_REGISTER_START}:"
                  f"{NODE_REGISTER_START+4}] = {payload}")
        return
    try:
        result = conn.client.write_registers(address=NODE_REGISTER_START, values=payload)
        if result is None or result.isError():
            raise IOError("write_registers returned an error result")
        return
    except Exception as e:
        print(f"  WARNING: Modbus write failed ({e}).")
    try:
        conn.reconnect()
        result = conn.client.write_registers(address=NODE_REGISTER_START, values=payload)
        if result is None or result.isError():
            print("  ERROR: Modbus write failed again after reconnection.")
    except Exception as e:
        print(f"  ERROR: Reconnection failed ({e}). Step write dropped.")


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
    SoC CSV -- the measured SoC lives only in toy_mpc_schedule_<ts>.csv."""

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

    def read_pct(self, dry_run: bool, sim_pct: float):
        """Return Node-646 SoC (%) for the closed loop. In dry-run, return the
        internally simulated value so the loop still runs without a HIL. Live:
        read register 3000, with one reconnect-retry. Returns None if a live
        read ultimately fails (caller then falls back to its model SoC)."""
        if dry_run:
            return sim_pct
        if self.conn is None or self.conn.client is None:
            return None
        try:
            return self._read_soc()
        except Exception:
            print("  WARNING: SoC read failed; retrying after reconnect ...")
        try:
            self.conn.reconnect()
            return self._read_soc()
        except Exception as e:
            print(f"  ERROR: SoC re-read failed ({e}).")
            return None

    def close(self) -> None:
        pass


# ============================================================
# 6. Console output
# ============================================================

def print_run_summary(horizon, playback, batt_kw, grid_kw, soc_kwh,
                      p_load, p_pv, statuses, capacity_kwh):
    base_g = (p_load - p_pv)[:playback]
    n_bad  = sum(s not in ("optimal", "optimal_inaccurate") for s in statuses)
    W = 74
    print("=" * W)
    print("ECE4191 Module 3 -- Node-646 Toy MPC  |  1-day playback (day 1)")
    print("=" * W)
    print(f"  Customers / capacity   : {N_CUSTOMERS_646}  /  {capacity_kwh:,.0f} kWh")
    print(f"  Look-ahead horizon     : {horizon} steps ({horizon*DELTA_HOURS:.1f} h), "
          f"re-solved every step")
    print(f"  Executed steps         : {playback} ({playback*DELTA_HOURS:.1f} h)")
    print(f"  Daily terminal SoC     : NOT enforced (D-RHO online procedure)")
    print(f"  Non-optimal solves     : {n_bad} / {playback}")
    print(f"  Objective sum(grid^2)  : {float(np.sum(grid_kw**2)):,.2f}")
    print(f"  Baseline grid range    : {base_g.min():.1f} to {base_g.max():.1f} kW")
    print(f"  MPC grid range         : {grid_kw.min():.1f} to {grid_kw.max():.1f} kW  "
          f"(mean {grid_kw.mean():.1f})")
    print(f"  Peak reduction         : {base_g.max() - grid_kw.max():.1f} kW")
    print(f"  Battery range          : {batt_kw.min():.1f} to {batt_kw.max():.1f} kW")
    print(f"  SoC range              : {soc_kwh.min():.1f} to {soc_kwh.max():.1f} kWh "
          f"(end {soc_kwh[-1]:.1f})")
    print("=" * W)


_HDR = (f"{'Step':>4} {'Load kW':>9} {'PV kW':>8} {'Net kW':>8} "
        f"{'Batt kW':>10} {'Action':>10} {'Grid kW':>10} "
        f"{'SoC% pred':>10} {'SoC% meas':>10}")


def print_step(step, load, pv, batt, grid, soc_pred, soc_meas):
    meas = f"{soc_meas:10.2f}" if soc_meas is not None else f"{'-':>10}"
    print(f"{step:4d} {load:9.1f} {pv:8.1f} {load-pv:8.1f} "
          f"{batt:10.2f} {_action(batt):>10} {grid:10.2f} "
          f"{soc_pred:10.2f} {meas}")


# ============================================================
# 7. Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ECE4191 Module 3 -- Node-646 toy MPC over Modbus TCP (Raspberry Pi)"
    )
    parser.add_argument("--input",         default="toy_example_N646_students.csv",
                        help="Forecast CSV (drives the MPC horizon / battery scheduling).")
    parser.add_argument("--actual",        default="actual_N646_students.csv",
                        help="Actual CSV (load/PV fed to Node 646; sets the optimised grid).")
    parser.add_argument("--horizon-steps", type=int, default=HORIZON_STEPS_DEFAULT,
                        help=f"Look-ahead window in steps (default {HORIZON_STEPS_DEFAULT} = 24 h).")
    parser.add_argument("--step-seconds",  type=float, default=STEP_SECONDS)
    parser.add_argument("--batt-power",    type=float, default=BATTERY_POWER_KW,
                        help=f"Battery power limit in kW (default {BATTERY_POWER_KW:.0f}).")
    parser.add_argument("--capacity",      type=float, default=BATTERY_CAPACITY_KWH,
                        help=f"Battery capacity in kWh (default {BATTERY_CAPACITY_KWH:.0f}).")
    parser.add_argument("--initial-soc",   type=float, default=INITIAL_SOC_KWH,
                        help=f"Initial SoC in kWh (default {INITIAL_SOC_KWH:.0f} = 50%%).")
    parser.add_argument("--p-upper",       type=float, default=P_UPPER_KW)
    parser.add_argument("--p-lower",       type=float, default=P_LOWER_KW)
    parser.add_argument("--solver",        default="OSQP")
    parser.add_argument("--no-wait",       action="store_true",
                        help="Skip sleep between steps (fast test mode).")
    parser.add_argument("--no-prompt",     action="store_true",
                        help="Skip pre-start confirmation prompt.")
    parser.add_argument("--dry-run",       action="store_true",
                        help="Run without connecting to the HIL.")
    parser.add_argument("--keep-final",    action="store_true",
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
    p_load, p_pv = load_toy_series(csv_path)
    print(f"Loading actual   CSV: {act_path.name}")
    p_load_act, p_pv_act = load_toy_series(act_path)
    forecast_steps = len(p_load)

    # One-day playback: execute only the steps that have a FULL 24 h look-ahead
    # window available -- i.e. day 1 (48 steps). Day 2 is NOT played back; it
    # exists only as the rolling forecast that the 48-step horizon reaches into
    # for the back half of day 1. So the output CSV covers day 1 (48 steps).
    playback = min(N_STEPS, forecast_steps - args.horizon_steps)
    if playback < 1:
        raise ValueError(
            f"Not enough data: need horizon + 1 <= {forecast_steps}; "
            f"horizon={args.horizon_steps}."
        )
    if len(p_load_act) < playback:
        raise ValueError(
            f"Actual CSV has {len(p_load_act)} step(s) but {playback} are played back; "
            f"it must cover at least the executed steps."
        )
    if playback < N_STEPS:
        print(f"  [NOTE] Only {playback} steps have a full {args.horizon_steps}-step "
              f"horizon available (<1 day); output covers {playback} steps.")
    print(f"  Forecast steps: {forecast_steps}   Horizon: {args.horizon_steps}   "
          f"Playback: {playback}  (day 1; day 2 = predicted look-ahead only)")

    # ── Banner ────────────────────────────────────────────────────────────────
    print("=" * 74)
    print("ECE4191 Module 3  |  Node-646 Toy MPC Playback (Modbus TCP)")
    print("=" * 74)
    print(f"  HIL target   : {args.ip}:{args.port}")
    print(f"  Forecast CSV : {Path(args.input).name}  (MPC / scheduling)")
    print(f"  Actual   CSV : {Path(args.actual).name}  (fed to Node 646)")
    print(f"  Node         : {NODE_LABEL[0]} phase {NODE_LABEL[1]}  "
          f"(holding {NODE_REGISTER_START}-{NODE_REGISTER_START+3}, {NODE_REGISTER_ORDER})")
    print(f"  Capacity     : {args.capacity:,.0f} kWh   Power: +/-{args.batt_power:,.0f} kW")
    print(f"  Controller   : CLOSED-LOOP receding-horizon MPC, minimize sum(grid^2)")
    print(f"  SoC feedback : measured (reg {SOC_INPUT_REGISTER}) used as soc0 for each horizon solve")
    if args.dry_run:
        print("  *** DRY-RUN MODE -- no Modbus writes will occur ***")
    print("=" * 74)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. Model compiled and running in Typhoon HIL Control Center.")
        print("  2. SCADA open; Control Type = REMOTE CONTROL.")
        print("  3. BusSplitMap holding registers 2000-2063 enabled.")
        print("  4. Node 646 battery starts at 50% SoC; not forced back at midnight.")
        print("  5. SoC is read from register 3000 BEFORE each new command is written.")
        input("\nPress Enter to start playback ...\n")

    # ── Closed-loop MPC ───────────────────────────────────────────────────────
    # The 24 h horizon QP is solved INSIDE the playback loop below, each step
    # seeded with the MEASURED Node-646 SoC (register 3000). No up-front solve.
    print("\nClosed-loop MPC: each 24 h horizon is solved from the MEASURED SoC.")

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

    # ── SoC reader (closed-loop feedback) ─────────────────────────────────────
    soc_logger = SocLogger(conn, enabled=not args.dry_run)
    soc_logger.start()

    # ── Playback (write applied schedule + read measured SoC) ─────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False

    if args.verbose or args.progress_every > 0:
        print(_HDR)
        print("-" * len(_HDR))

    # Closed-loop state: internal model SoC (dry-run sim + predicted diagnostic),
    # aligned to the first measured reading so later divergence is model error.
    soc_model_kwh = None
    batt_hist, grid_hist, soc_traj = [], [], []
    grid_act_hist = []
    statuses = []

    try:
        for k in range(playback):
            t0 = time.time()
            step = k + 1

            # 1) READ measured SoC (%) BEFORE computing this step's command.
            sim_pct = 100.0 * (args.initial_soc if soc_model_kwh is None
                               else soc_model_kwh) / args.capacity
            meas_pct = soc_logger.read_pct(args.dry_run, sim_pct)

            # soc0 fed to the solver = MEASURED SoC (fall back to model if read failed).
            if meas_pct is not None:
                soc0_kwh = max(0.0, min(args.capacity, meas_pct / 100.0 * args.capacity))
            else:
                soc0_kwh = args.initial_soc if soc_model_kwh is None else soc_model_kwh

            if soc_model_kwh is None:
                soc_model_kwh = soc0_kwh            # align model trajectory at step 0
            soc_model_pct = 100.0 * soc_model_kwh / args.capacity
            soc_traj.append(soc_model_kwh)

            # 2) SOLVE the 24 h horizon from the MEASURED soc0; apply first action only.
            end = min(k + args.horizon_steps, len(p_load))
            batt_seq, _grid_seq, status = solve_mpc_horizon(
                p_load[k:end], p_pv[k:end], soc0_kwh,
                args.capacity, args.batt_power, args.p_upper, args.p_lower, args.solver,
            )
            statuses.append(status)
            # X1 = battery command from the forecast MPC solve (first action).
            # The forecast grid is discarded; the optimised grid is recomputed
            # against the ACTUAL load/PV.
            b0       = float(batt_seq[0])
            grid_fc  = float(p_load[k]     - p_pv[k]     - b0)   # forecast grid (discarded)
            grid_act = float(p_load_act[k] - p_pv_act[k] - b0)   # optimised grid on ACTUAL

            # 3) WRITE the Node-646 command: ACTUAL load/PV, Batt = X1.
            payload = build_node_payload(
                pref_kw   = float(p_load_act[k]),  # Pref  (kW)  actual load
                qref_kvar = QREF_646_KVAR,         # Qref  (kVAr)
                pv_kw     = float(p_pv_act[k]),    # PV    (kW)  actual PV
                batt_kw   = b0,                    # Batt  (kW, discharge +ve)
            )
            modbus_write_node(conn, payload, args.dry_run, args.verbose)

            # 4) LOG (soc0 used = measured; soc_predicted = independent model trajectory).
            batt_hist.append(b0); grid_hist.append(grid_fc); grid_act_hist.append(grid_act)
            sched_rows.append({
                "step":                step,
                # forecast inputs the MPC scheduled against
                "p_load_fc_kw":        round(float(p_load[k]),     4),
                "p_pv_fc_kw":          round(float(p_pv[k]),       4),
                # actual inputs fed to Node 646
                "p_load_kw":           round(float(p_load_act[k]), 4),
                "p_pv_kw":             round(float(p_pv_act[k]),   4),
                "baseline_grid_kw":    round(float(p_load_act[k] - p_pv_act[k]), 4),
                # X1 = battery command (forecast MPC), X2 = optimised grid on ACTUAL
                "X1_battery_kw":       round(b0, 4),
                "battery_action":      _action(b0),
                "X2_grid_kw":          round(grid_act, 4),
                "X2_grid_forecast_kw": round(grid_fc,  4),
                "soc_predicted_pct":   round(soc_model_pct, 4),
                "soc_measured_pct":    "" if meas_pct is None else round(float(meas_pct), 4),
            })

            if args.verbose or (args.progress_every > 0 and
                                (step in (1, playback) or step % args.progress_every == 0)):
                print_step(step, float(p_load_act[k]), float(p_pv_act[k]), b0, grid_act,
                           soc_model_pct, meas_pct)

            # 5) Advance the internal model SoC by the applied command.
            soc_model_kwh = max(0.0, min(args.capacity, soc_model_kwh - b0 * DELTA_HOURS))

            # Pace: let the HIL settle before the NEXT read, then real-time map.
            if not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                time.sleep(args.measurement_delay)
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

    if args.verbose or args.progress_every > 0:
        print("-" * len(_HDR))

    # ── Summary (from the executed closed-loop run) ───────────────────────────
    if batt_hist:
        soc_traj.append(soc_model_kwh)      # final model SoC -> length = steps+1
        print_run_summary(args.horizon_steps, len(batt_hist),
                          np.array(batt_hist), np.array(grid_hist),
                          np.array(soc_traj), p_load, p_pv, statuses, args.capacity)
        ga = np.array(grid_act_hist)
        print(f"  Actual grid range      : {ga.min():.1f} to {ga.max():.1f} kW  "
              f"(mean {ga.mean():.1f})   [X2 on actual; forecast grid above discarded]")

    # ── Save schedule ─────────────────────────────────────────────────────────
    if sched_rows:
        sched_path = Path(f"toy_mpc_schedule_{ts}.csv")
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        print(f"MPC schedule saved    : {sched_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()