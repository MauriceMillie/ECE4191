"""
ECE4191 Module 3 - Experiment 2
Feeder-wide MPC battery scheduling over Modbus TCP/IP.

Voltage-aware version: hard battery-hardware limits + soft (slack) voltage limits with an online-learned
voltage-vs-import model.

>>> V19 SWITCHABLE BATTERY-EMULATOR REVISION (14-Oct-2026)
- Node 646 battery feedback can now be selected at the command line with
  --battery-emulator {hil,hardware,none}.
- hil: retains the V18 HIL-internal-battery feedback path (Modbus input register 3000 on the
  physical HIL; the existing API SoC path is retained for --backend api).
- hardware: drives the laboratory physical battery emulator over 9600-8N1 serial using the
  calibrated dynamic Cxxx/Dxxx time-scaling implementation, and uses its measured SoC as the
  Node-646 MPC feedback state. The HIL-internal SoC is still read as an independent comparison.
- none: disables Node-646 measured SoC feedback and propagates the MPC-predicted SoC.
  --no-soc-feedback remains a backwards-compatible override to this mode.
- CSV logging keeps the MPC predicted SoC and HIL measured SoC, and adds a separate
  646_B_soc_hardware_pct column. Measurement columns contain '-' whenever that measurement
  source is not active/available.
- Default battery energy capacity remains 12.5 kWh/customer; power remains 5 kW/customer.
- CLARABEL remains the primary CVXPY solver with OSQP as the automatic backup solver.
- The V17 reserve-lock / ASAP-fill and V16/V15 voltage-security behaviour is otherwise retained.
<<< V19 SWITCHABLE BATTERY-EMULATOR REVISION

>>> V13 CONTINUOUS PRECHARGE / SOC-BALANCE REVISION
- Security pre-charge no longer uses phase-wide charge/idle bang-bang pauses.
- A measured-voltage feedback controller continuously trims charging to hold a configurable pre-charge voltage target.
- Security charging is allocated to individual batteries in proportion to their remaining energy deficit to the reserve target,
  so a nearly-full node cannot absorb charging while a large weak-node battery remains undercharged.
- Actual +/-5% voltage compliance and the +/-3% hard do-not-worsen battery-action band remain separate.
- The existing measured-voltage ride-through controller is intentionally retained; this revision targets the demonstrated
  failure to ENTER the outlier with enough well-balanced Phase-A stored energy.

>>> USER REQUEST CHANGE SUMMARY (12-Oct-2026)
- Nodal battery size/power are configured per customer (V18 defaults 12.5 kWh, 5 kW).
- Aggregate battery CLI arguments were removed.
- --perfect-forecast restored; live forecast remains the default.
- The active controller is one JOINT NODAL MPC QP: every node has its own battery/grid/SoC variables,
  while voltage constraints couple nodes on the same phase.
- Optional --peak-reserve softly reserves >= target SoC before a forecasted extreme feeder peak.
- Voltage control now uses the minimum measured per-unit voltage on each phase by default (including node 634),
  rather than the phase-average primary voltage.
- Optional --local-voltage-support biases the first MPC action toward discharge at locally weak-voltage nodes.
- Extra logging/diagnostics were added so voltage-model misses vs deliberate slack can be distinguished.
<<< USER REQUEST CHANGE SUMMARY
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd

# >>> V19 BATTERY EMULATOR CHANGE 1 START: optional physical-emulator dependency
# Keep pyserial optional so HIL and NONE modes do not require it to be installed.
try:
    import serial
except ImportError:
    serial = None
# <<< V19 BATTERY EMULATOR CHANGE 1 END

# >>> USER REQUEST CHANGE 1 START: remove unused runtime imports
# Model/scikit-learn dependencies belong in live_forecaster.py; this controller only imports what it uses.
# <<< USER REQUEST CHANGE 1 END

# >>> LIVE FORECAST CHANGE 1 START: import the live forecaster <<<
from live_forecaster import WeatherTable, LiveForecaster, WindowForecastCache
# <<< LIVE FORECAST CHANGE 1 END


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
# 1. Settings
# ============================================================

N_STEPS      = 48
DELTA_HOURS  = 0.5
STEP_SECONDS = 2.0        # real seconds per 30-min time step

TIME_COL_RE = re.compile(r"^\d{1,2}:\d{2}$")

NODE_MAP = {
    "646_B": {"start": 2000, "order": "normal", "voltage": 4001},
    "645_B": {"start": 2004, "order": "normal", "voltage": 4002},
    "611_C": {"start": 2008, "order": "normal", "voltage": 4003},
    "652_A": {"start": 2012, "order": "normal", "voltage": 4004},

    "671_A": {"start": 2016, "order": "normal", "voltage": 4005},
    "671_B": {"start": 2020, "order": "normal", "voltage": 4006},
    "671_C": {"start": 2024, "order": "normal", "voltage": 4007},

    "692_C": {"start": 2028, "order": "reversed", "voltage": 4008},
    "692_B": {"start": 2032, "order": "reversed", "voltage": 4009},
    "692_A": {"start": 2036, "order": "reversed", "voltage": 4010},

    "675_C": {"start": 2040, "order": "reversed", "voltage": 4011},
    "675_B": {"start": 2044, "order": "reversed", "voltage": 4012},
    "675_A": {"start": 2048, "order": "reversed", "voltage": 4013},

    "634_C": {"start": 2052, "order": "reversed", "voltage": 4014},
    "634_B": {"start": 2056, "order": "reversed", "voltage": 4015},
    "634_A": {"start": 2060, "order": "reversed", "voltage": 4016},
}


# Real-time reactive power (kVAr) per node
QREF_MAP = {
    "646_B": 0,
    "645_B": 0,
    "611_C": 0,
    "652_A": 0,

    "671_A": 0,
    "671_B": 0,
    "671_C": 0,

    "692_C": 0,
    "692_B": 0,
    "692_A": 0,

    "675_C": 0,
    "675_B": 0,
    "675_A": 0,

    "634_C": 0,
    "634_B": 0,
    "634_A": 0,
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

# >>> USER REQUEST CHANGE 2 START: nodal battery parameters are per customer, not aggregate
DEFAULT_BATTERY_CAPACITY_PER_CUSTOMER_KWH = 12.5   # V18 validated/optimised HIL-battery size
DEFAULT_BATTERY_POWER_PER_CUSTOMER_KW = 5.0
DEFAULT_INITIAL_SOC_PCT = 50.0
# <<< USER REQUEST CHANGE 2 END

NOMINAL_VOLTAGE=2401 #voltage nominal value for most load nodes
NOMINAL_LOW_VOLTAGE=277 #voltage nominal value for node 634

DEFAULT_WEIGHT = 1   # Default weight val

CIL_NODE = "646_B"

# --- Modbus -------------------------------------------------------------------
DEFAULT_HIL_IP   = "192.168.1.210"
DEFAULT_HIL_PORT = 502

HOLDING_START = 2000
HOLDING_COUNT = 64

SIGNED_16BIT_MIN = -32768
SIGNED_16BIT_MAX = 32767

# Node 646 INTERNAL HIL battery SoC feedback.
SOC_INPUT_REGISTER = 3000

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0

DEFAULT_PLAYBACK_DAYS = 4   # Experiment 2 has a 4-day playback period

# >>> V19 BATTERY EMULATOR CHANGE 2 START: laboratory physical battery emulator
# These settings are carried over from the validated Experiment-3 hardware-sync implementation.
DEFAULT_EMULATOR_PORT = "/dev/serial/by-id/usb-FTDI_TTL232R_FTEAE5HE-if00-port0"
EMULATOR_BAUD = 9600
EMULATOR_SOC_MAX_RAW = 65500
EMULATOR_READ_WAIT_S = 1.2
EMULATOR_COMMAND_DEADBAND_KW = 0.5

# Measured laboratory calibration: command 255 changes the raw 0..65500 SoC stream
# at approximately 16 counts/s in either direction.
EMULATOR_DISCHARGE_MAX_RAW_PER_S = 16.0
EMULATOR_CHARGE_MAX_RAW_PER_S = 16.0

# Each controller row still represents DELTA_HOURS = 0.5 simulated hour. In HARDWARE mode
# the wall-clock hold and Cxxx/Dxxx magnitude are chosen together to reproduce that SoC change.
DEFAULT_HARDWARE_MIN_HOLD_S = 30.0
DEFAULT_HARDWARE_MAX_HOLD_S = 500.0
DEFAULT_HARDWARE_IDLE_HOLD_S = 15.0
DEFAULT_HARDWARE_PREFERRED_CODE = 200
DEFAULT_HARDWARE_COMMAND_REFRESH_S = 60.0
DEFAULT_HARDWARE_STALE_LIMIT_S = 3.0
DEFAULT_HARDWARE_HOLD_PROGRESS_S = 30.0
# <<< V19 BATTERY EMULATOR CHANGE 2 END


# ============================================================
# 2. CSV loaders
# ============================================================

def parse_date(value: str) -> pd.Timestamp:
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
    pattern = np.zeros(N_STEPS)
    pattern[np.r_[0:14, 44:48]] = 0.03
    pattern[np.r_[14:28, 40:44]] = 0.06
    pattern[28:40] = 0.30
    reps = int(np.ceil(n_steps_total / N_STEPS)) + 1
    return np.tile(pattern, reps)[:n_steps_total]


# >>> USER REQUEST CHANGE 3 START: legacy independent solver removed
# The active MPC solver is solve_joint_nodal_mpc_qp() below. It still has one battery/grid/SoC
# trajectory per node, but solves them together so feeder-voltage constraints can couple the nodes.
# <<< USER REQUEST CHANGE 3 END


def _action(v: float) -> str:
    return "Discharge" if v > 0.5 else ("Charge" if v < -0.5 else "Idle")



def pad_to_length(arr: np.ndarray, target_len: int) -> np.ndarray:

    if len(arr) >= target_len:
        return arr
    if len(arr) == 0:
        return np.zeros(target_len)
    pad_block = arr[-N_STEPS:] if len(arr) >= N_STEPS else arr[-1:] 
    out = arr.copy()
    while len(out) < target_len:
        out = np.concatenate([out, pad_block])
    return out[:target_len]


# >>> USER REQUEST CHANGE 4 START: exact 48-step horizon helper + per-unit voltage helper
def fixed_horizon_window(arr, start: int, n_steps: int = N_STEPS) -> np.ndarray:
    """Return exactly n_steps values. At the data tail, repeat the final day/block rather than shrinking the MPC horizon."""
    arr = np.asarray(arr, dtype=float).reshape(-1)
    if arr.size == 0:
        return np.zeros(n_steps, dtype=float)
    need = start + n_steps
    if arr.size < need:
        arr = pad_to_length(arr, need)
    return np.asarray(arr[start:start + n_steps], dtype=float)


def nominal_voltage_for_node(node: str) -> float:
    return NOMINAL_LOW_VOLTAGE if node.startswith("634_") else NOMINAL_VOLTAGE


def node_voltage_pu(node: str, voltage_v: float) -> float:
    return float(voltage_v) / nominal_voltage_for_node(node)
# <<< USER REQUEST CHANGE 4 END


# ============================================================
# 4. Modbus connection + write helpers
# ============================================================

class ModbusConnection:

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
    # >>> VHIL CHANGE 4 START: API backend clears its own SCADA inputs <<<
    if isinstance(conn, TyphoonApiConnection):
        conn.clear_all()
        return
    # <<< VHIL CHANGE 4 END
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

def load_real_forecast_data(path):
    df = pd.read_csv(path)
    return df


# ============================================================
# >>> VHIL CHANGE 1 START: Typhoon HIL Python-API backend (works with the Virtual HIL device) <<<
# ============================================================
# The Modbus path above needs the HIL's Modbus server. The Virtual HIL device cannot provide that, so
# --backend api talks to the running model through the Typhoon Python API instead:
#   * writes  -> hil.set_scada_input_value(<SCADA Input name>, value)      (inputs, in W / VAr)
#   * reads   -> hil.read_analog_signal(<signal name>)                      (voltages, optional SoC)
# The model therefore needs SCADA Inputs / probes with the names produced below. Edit the two name
# functions if you name yours differently.

def api_input_names(node_key: str) -> dict:
    """SCADA Input names for one node-phase, e.g. '646_B' -> 'Time Varying Load 646.Pref646'."""
    node, ph = node_key.split("_")
    suffix = f"Ph{ph}" if node in ("671", "692", "675", "634") else ""     # three-phase nodes carry a phase suffix
    sub = f"Time Varying Load {node}"
    return {
        "p":   f"{sub}.Pref{node}{suffix}",               # load active power   (W)
        "q":   f"{sub}.Qref{node}{suffix}",               # load reactive power (VAr)
        "pv":  f"{sub}.PVpanel_power{node}{suffix}",      # PV generation       (W, positive = generating)
        "bat": f"{sub}.Battery_Power{node}{suffix}",      # battery power       (W, positive = discharging)
    }


def api_voltage_name(node_key: str) -> str:
    """Analog signal for a node-phase RMS voltage, e.g. '646_B' -> 'Node 646.V2_rms'."""
    node, ph = node_key.split("_")
    return f"Node {node}.V{ {'A': 1, 'B': 2, 'C': 3}[ph] }_rms"


API_INPUTS = {nk: api_input_names(nk) for nk in NODE_MAP}
API_VOLTAGES = {nk: api_voltage_name(nk) for nk in NODE_MAP}
# SCADA Input min/max (W / VAr) read from Monash_13NodeFeeder.tse. Values outside are clipped before writing.
API_LIMITS = {
    "Time Varying Load 634.Pref634PhA": (0, 500000),
    "Time Varying Load 634.Qref634PhA": (0, 500000),
    "Time Varying Load 634.Battery_Power634PhA": (-345000, 345000),
    "Time Varying Load 634.PVpanel_power634PhA": (0, 150000),
    "Time Varying Load 634.Pref634PhB": (0, 500000),
    "Time Varying Load 634.Qref634PhB": (0, 500000),
    "Time Varying Load 634.Battery_Power634PhB": (-225000, 225000),
    "Time Varying Load 634.PVpanel_power634PhB": (0, 150000),
    "Time Varying Load 634.Pref634PhC": (0, 500000),
    "Time Varying Load 634.Qref634PhC": (0, 500000),
    "Time Varying Load 634.Battery_Power634PhC": (-260000, 260000),
    "Time Varying Load 634.PVpanel_power634PhC": (0, 150000),
    "Time Varying Load 645.Pref645": (0, 500000),
    "Time Varying Load 645.Qref645": (0, 500000),
    "Time Varying Load 645.Battery_Power645": (-315000, 315000),
    "Time Varying Load 645.PVpanel_power645": (0, 150000),
    "Time Varying Load 646.Pref646": (0, 500000),
    "Time Varying Load 646.Qref646": (0, 500000),
    "Time Varying Load 646.Battery_Power646": (-510000, 510000),
    "Time Varying Load 646.PVpanel_power646": (0, 150000),
    "Time Varying Load 652.Pref652": (0, 500000),
    "Time Varying Load 652.Qref652": (0, 500000),
    "Time Varying Load 652.Battery_Power652": (-230000, 230000),
    "Time Varying Load 652.PVpanel_power652": (0, 150000),
    "Time Varying Load 675.Pref675PhA": (0, 500000),
    "Time Varying Load 675.Qref675PhA": (0, 500000),
    "Time Varying Load 675.Battery_Power675PhA": (-955000, 955000),
    "Time Varying Load 675.PVpanel_power675PhA": (0, 500000),
    "Time Varying Load 675.Pref675PhB": (0, 500000),
    "Time Varying Load 675.Qref675PhB": (0, 500000),
    "Time Varying Load 675.Battery_Power675PhB": (-180000, 180000),
    "Time Varying Load 675.PVpanel_power675PhB": (0, 150000),
    "Time Varying Load 675.Pref675PhC": (0, 500000),
    "Time Varying Load 675.Qref675PhC": (0, 500000),
    "Time Varying Load 675.Battery_Power675PhC": (-595000, 595000),
    "Time Varying Load 675.PVpanel_power675PhC": (0, 150000),
    "Time Varying Load 611.Pref611": (0, 500000),
    "Time Varying Load 611.Qref611": (0, 500000),
    "Time Varying Load 611.Battery_Power611": (-340000, 340000),
    "Time Varying Load 611.PVpanel_power611": (0, 150000),
    "Time Varying Load 692.Pref692PhC": (0, 500000),
    "Time Varying Load 692.Qref692PhC": (0, 500000),
    "Time Varying Load 692.Battery_Power692PhC": (-330000, 330000),
    "Time Varying Load 692.PVpanel_power692PhC": (0, 150000),
    "Time Varying Load 692.Pref692PhB": (0, 500000),
    "Time Varying Load 692.Qref692PhB": (0, 500000),
    "Time Varying Load 692.Battery_Power692PhB": (0, 0),
    "Time Varying Load 692.PVpanel_power692PhB": (0, 150000),
    "Time Varying Load 692.Pref692PhA": (0, 500000),
    "Time Varying Load 692.Qref692PhA": (0, 500000),
    "Time Varying Load 692.Battery_Power692PhA": (0, 0),
    "Time Varying Load 692.PVpanel_power692PhA": (0, 150000),
    "Time Varying Load 671.Pref671PhA": (0, 500000),
    "Time Varying Load 671.Qref671PhA": (0, 500000),
    "Time Varying Load 671.Battery_Power671PhA": (-795000, 795000),
    "Time Varying Load 671.PVpanel_power671PhA": (0, 500000),
    "Time Varying Load 671.Pref671PhB": (0, 500000),
    "Time Varying Load 671.Qref671PhB": (0, 500000),
    "Time Varying Load 671.Battery_Power671PhB": (-775000, 775000),
    "Time Varying Load 671.PVpanel_power671PhB": (0, 500000),
    "Time Varying Load 671.Pref671PhC": (0, 500000),
    "Time Varying Load 671.Qref671PhC": (0, 500000),
    "Time Varying Load 671.Battery_Power671PhC": (-795000, 795000),
    "Time Varying Load 671.PVpanel_power671PhC": (0, 500000),
}
API_POWER_SCALE = 1000.0      # controller works in kW / kVAr, the SCADA inputs expect W / VAr


class TyphoonApiConnection:
    """Drop-in for ModbusConnection when --backend api. With dry_run=True it never imports typhoon and
    just prints (so you can check the signal names without a HIL)."""

    def __init__(self, dry_run=False, control_signal=None, control_value=0.0,
                 soc_signal=None, verbose=False):
        self.dry_run = dry_run
        self.control_signal, self.control_value = control_signal, control_value
        self.soc_signal = soc_signal
        self.verbose = verbose
        self.hil = None
        self.missing = {}            # signal name -> reason; written once, then skipped
        self.clipped = {}            # signal name -> number of writes clipped to its SCADA range
        self.last_pbat_kw = {}       # last battery command per node (used by the SoC emulation)

    def connect(self) -> None:
        if self.dry_run:
            print("  [DRY-RUN] Typhoon API backend: nothing imported, nothing written.")
            return
        try:
            import typhoon.api.hil as hil     # type: ignore
        except ImportError:
            raise ConnectionError(
                "Cannot import typhoon.api.hil. Run this script with the Python environment that has the "
                "Typhoon HIL software installed (e.g. the one Control Center uses), or use --dry-run."
            )
        running = hil.is_simulation_running()
        if not running:
            raise ConnectionError(
                "No simulation is running (is_simulation_running() = %r). In Control Center: load the model "
                "on the Virtual HIL device, then start the simulation, then run this script." % (running,)
            )
        self.hil = hil
        if self.control_signal:
            if self._set(self.control_signal, self.control_value, force=True):
                print(f"  Control switch '{self.control_signal}' set to {self.control_value}.")

    def close(self) -> None:
        if self.clipped:
            print("  NOTE: some values were clipped to the SCADA Input ranges in the schematic "
                  "(signal: number of steps):")
            for k, v in sorted(self.clipped.items()):
                print(f"    - {k}: {v}  (range {API_LIMITS[k][0]:.0f}..{API_LIMITS[k][1]:.0f})")

    # --- low level -----------------------------------------------------------------
    def _set(self, name: str, value: float, force: bool = False) -> bool:
        if self.dry_run:
            if self.verbose:
                print(f"[DRY-RUN] set_scada_input_value('{name}', {float(value):.1f})")
            return True
        if name in self.missing and not force:
            return False
        value = float(value)
        if name in API_LIMITS:                       # keep inside the SCADA Input range, count what gets clipped
            lo, hi = API_LIMITS[name]
            if value < lo - 1.0 or value > hi + 1.0:   # ignore solver noise below 1 W
                self.clipped[name] = self.clipped.get(name, 0) + 1
            value = min(max(value, lo), hi)
        try:
            ok = self.hil.set_scada_input_value(name, float(value))
        except Exception as e:
            self.missing[name] = f"exception: {e}"
            return False
        if ok is False:
            self.missing[name] = "set_scada_input_value returned False (no SCADA Input with this name?)"
            return False
        return True

    def read_signal(self, name: str):
        if self.dry_run:
            return None
        try:
            v = self.hil.read_analog_signal(name=name)
        except Exception:
            return None
        return None if v is None else float(v)

    # --- feeder-level ------------------------------------------------------------
    def write_feeder(self, node_data, step_index, pbat_nodes) -> None:
        for nk in NODE_MAP:
            n = API_INPUTS[nk]
            self._set(n["p"],   node_data[nk]["load_kw"][step_index] * API_POWER_SCALE)
            self._set(n["q"],   QREF_MAP[nk] * API_POWER_SCALE)
            self._set(n["pv"],  node_data[nk]["pv_kw"][step_index] * API_POWER_SCALE)
            self._set(n["bat"], pbat_nodes[nk] * API_POWER_SCALE)
        self.last_pbat_kw = dict(pbat_nodes)

    def clear_all(self) -> None:
        for nk in NODE_MAP:
            for sig in API_INPUTS[nk].values():
                self._set(sig, 0.0)
        if self.dry_run:
            print("    [DRY-RUN] clear all SCADA inputs")
        elif self.missing:
            print(f"  WARNING: {len(self.missing)} SCADA input(s) could not be written and will be skipped "
                  "(add them to the model, or fix the names in api_input_names):")
            for name in sorted(self.missing):
                print(f"    - {name}")
        else:
            print("  All SCADA inputs cleared (every expected input exists).")


class ApiSocLogger:
    """Same interface the main loop uses from SocLogger (start / log_step / _read_voltages / close),
    but fed by the API. Node-646 SoC comes from an analog signal if --api-soc-signal is given; otherwise from
    an ideal Python battery emulation (SoC integrates the battery power the controller just commanded)."""

    def __init__(self, conn, enabled, init_soc_pct, cil_capacity_kwh):
        self.conn, self.enabled = conn, enabled
        self.soc_pct, self.cap_kwh = float(init_soc_pct), float(cil_capacity_kwh)
        self.use_probe = conn.soc_signal is not None

    def start(self) -> None:
        if not self.enabled:
            return
        bad = [nm for nm in API_VOLTAGES.values() if self.conn.read_signal(nm) is None]
        if bad:
            print(f"  WARNING: {len(bad)}/{len(API_VOLTAGES)} voltage signal(s) could not be read (they will log as -1): "
                  + ", ".join(bad))
        else:
            print(f"  All {len(API_VOLTAGES)} voltage signals resolved.")
        if self.use_probe:
            v = self.conn.read_signal(self.conn.soc_signal)
            if v is None:
                print(f"  WARNING: SoC signal '{self.conn.soc_signal}' could not be read; using the Python "
                      "battery emulation instead.")
                self.use_probe = False
            else:
                print(f"  SoC signal '{self.conn.soc_signal}' resolved (reads {v:.2f} %).")
        if not self.use_probe:
            print("  SoC for node 646: ideal Python battery emulation (no feedback from the model).")

    def log_step(self):
        if not self.enabled:
            return None
        if self.use_probe:
            v = self.conn.read_signal(self.conn.soc_signal)
            if v is not None:
                self.soc_pct = v
                return self.soc_pct
        p_kw = self.conn.last_pbat_kw.get(CIL_NODE, 0.0)
        self.soc_pct -= 100.0 * p_kw * DELTA_HOURS / self.cap_kwh      # positive = discharging
        self.soc_pct = min(100.0, max(0.0, self.soc_pct))
        return self.soc_pct

    def _read_voltages(self):
        out = [0] * 16                                                # indexed like registers 4001-4016
        for nk, cfg in NODE_MAP.items():
            v = self.conn.read_signal(API_VOLTAGES[nk])
            out[cfg["voltage"] - 4001] = -1 if v is None else v
        return out

    def close(self) -> None:
        pass

# <<< VHIL CHANGE 1 END

# ============================================================
# >>> VOLTAGE CHANGE 1 START: hardware limits, adaptive voltage model, voltage-aware joint QP <<<
# ============================================================
#
# Three things live in this block:
#   (a) get_hardware_limits()      - the HARD limits, taken from the same SCADA ranges the HIL enforces
#   (b) PhaseVoltageEstimator      - voltage = f(net import) per phase; slope learned online (recursive least squares)
#   (c) solve_joint_nodal_mpc_qp() - one nodal MPC QP for the whole feeder: per-node states + coupled soft voltage caps

# ---- (a) Hard limits that mirror the battery hardware / HIL --------------------------------------
# The HIL silently clips any battery command outside its SCADA Input range (see API_LIMITS / TyphoonApiConnection._set).
# If the QP plans beyond that range, the plan and the hardware disagree and the SoC prediction drifts. So the QP's
# power limits are READ FROM API_LIMITS (one source of truth) instead of being typed in a second time.
# The SoC window keeps the planned SoC away from the emulator's 0 % / 100 % end stops (the logged run hit 0.0 %).
# TODO: set these to the real cut-offs of the battery emulator if they are known.
SOC_MIN_PCT_DEFAULT = 2.0
SOC_MAX_PCT_DEFAULT = 98.0


# >>> USER REQUEST CHANGE 5 START: one source of truth for per-customer battery sizing
def get_hardware_limits(
    node: str,
    soc_min_pct: float,
    soc_max_pct: float,
    capacity_per_customer_kwh: float,
    power_per_customer_kw: float,
) -> dict:
    """Effective hard limits for one nodal battery. Positive power = discharging.

    The requested per-customer power limit is additionally clipped to the HIL schematic/SCADA input range,
    because commanding beyond the model's physical input range would make the MPC prediction disagree with HIL.
    """
    customers = N_CUSTOMERS[node]
    cap_kwh = customers * capacity_per_customer_kwh
    requested_power_kw = customers * power_per_customer_kw

    lo_w, hi_w = API_LIMITS[API_INPUTS[node]["bat"]]
    hil_lo_kw = lo_w / API_POWER_SCALE
    hil_hi_kw = hi_w / API_POWER_SCALE

    if customers == 0:
        p_lo_kw = 0.0
        p_hi_kw = 0.0
    else:
        p_lo_kw = max(hil_lo_kw, -requested_power_kw)
        p_hi_kw = min(hil_hi_kw, requested_power_kw)

    return {
        "p_lo_kw": p_lo_kw,
        "p_hi_kw": p_hi_kw,
        "requested_power_kw": requested_power_kw,
        "hil_p_lo_kw": hil_lo_kw,
        "hil_p_hi_kw": hil_hi_kw,
        "cap_kwh": cap_kwh,
        "soc_lo_kwh": cap_kwh * soc_min_pct / 100.0,
        "soc_hi_kwh": cap_kwh * soc_max_pct / 100.0,
    }
# <<< USER REQUEST CHANGE 5 END


# ---- (b) Voltage model: V = V_anchor - rho * (P - P_anchor), rho learned online ---------------------
PHASES = ("A", "B", "C")


def node_phase(node: str) -> str:
    return node.split("_")[1]


def is_primary_node(node: str) -> bool:
    """Node 634 sits behind the 4.16 kV / 480 V transformer (different base voltage), so it is not used as a
    primary-voltage signal. Its power still counts towards the phase import."""
    return not node.startswith("634")


# Starting guess for rho (V per kW of net import on one phase) from the schematic line data (IEEE-13 config 601):
#   dV = R * P / V   ->   rho0 = R_ohm * 1000 / V_nominal,   R = (ohm/mile) * (miles from source to node 671).
LINE_R_OHM_PER_MILE = {"A": 0.3465, "B": 0.3375, "C": 0.3414}
MAIN_PATH_MILES = 4000.0 / 5280.0                              # 650->632 (2000 ft) + 632->671 (2000 ft)
RHO0_V_PER_KW = {ph: LINE_R_OHM_PER_MILE[ph] * MAIN_PATH_MILES * 1000.0 / NOMINAL_VOLTAGE for ph in PHASES}

# >>> V8 ROBUST PRECHARGE CHANGE 1 START
# Predictive MPC voltage band = the actual +/-5% network requirement. The existing
# 0.005 pu planning margin makes the soft predictive target 0.955-1.045 pu.
V_MIN_PU_DEFAULT    = 0.95
V_MAX_PU_DEFAULT    = 1.05
V_MARGIN_PU_DEFAULT = 0.005

# The battery ACTION safety guard is intentionally tighter and independent of the
# MPC planning band: outside 0.97-1.03 pu a battery may not take the action that
# worsens the present violation.
# >>> V14 OUTLIER VOLTAGE HOLD CHANGE 1 START
# Battery-action protection uses +/-4% rather than +/-3%.  The actual network
# requirement remains +/-5%, so this still leaves 0.01 pu of hard headroom while
# giving security pre-charge substantially more usable voltage room.
GUARD_V_MIN_PU_DEFAULT = 0.96
GUARD_V_MAX_PU_DEFAULT = 1.04
# <<< V14 OUTLIER VOLTAGE HOLD CHANGE 1 END
# <<< V8 ROBUST PRECHARGE CHANGE 1 END
# >>> CHATTER/STABILITY CHANGE 1 START
# The very large voltage-slack weights tested previously caused frequent OSQP user_limit fallbacks.
# Use the lower, more numerically stable weighting as the default; it can still be overridden from the CLI.
K_SLACK_DEFAULT     = 3.0e5     # penalty per kW of predictive voltage-cap violation
RLS_FORGET_DEFAULT  = 0.98      # forgetting factor, ~50 steps (about one day) of memory
BIAS_DECAY_DEFAULT  = 0.8       # how fast the last forecast error is assumed to fade over the horizon (0 = ignore it)

# Stateful directional guard. Engage at the actual hard-action thresholds by default
# (0.97/1.03); use hysteresis only for release to avoid chatter.
DIRECTIONAL_GUARD_ENGAGE_MARGIN_PU_DEFAULT = 0.0
# >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 1 START
# The old 0.015 release margin could leave a previous over-voltage "no_discharge"
# guard latched until voltage fell below 1.015 pu. In the latest run Node 646 stayed
# around 1.018-1.022 pu during the main load peak, so its stored energy was stranded.
# Keep hysteresis on release:
#   low engage/release  = 0.970 / 0.978 pu
#   high engage/release = 1.030 / 1.022 pu
# >>> V14 OUTLIER VOLTAGE HOLD CHANGE 2 START
# With the +/-4% action band use a small 0.003-pu release hysteresis:
# low 0.960 -> 0.963, high 1.040 -> 1.037.
DIRECTIONAL_GUARD_RELEASE_MARGIN_PU_DEFAULT = 0.003
# <<< V14 OUTLIER VOLTAGE HOLD CHANGE 2 END
PRIMARY_SOLVER_DEFAULT = "CLARABEL"
SECONDARY_SOLVER_DEFAULT = "OSQP"
# <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 1 END
DIRECTIONAL_GUARD_HOLD_STEPS_DEFAULT = 2

# Mild first-action command smoothing. This is a convex quadratic penalty, not a hard ramp limit.
BATTERY_SMOOTHING_WEIGHT_DEFAULT = 0.25

# >>> V5 NODAL VOLTAGE/RAMP CHANGE 1 START
# Hard asymmetric charge-ramp limit. Negative battery power = charging, so this limits how quickly
# a battery may move in the MORE-NEGATIVE direction from one applied MPC step to the next.
# Discharge can still increase immediately, which is useful during undervoltage.
# 0.5 kW/customer/step is deliberately conservative after the observed ~1 MW phase-A charging jumps.
MAX_CHARGE_RAMP_PER_CUSTOMER_KW_DEFAULT = 0.5

# Predictive voltage-cap architecture remains switchable between phase, nodal, and both.
# >>> V7 ENERGY MANAGEMENT CHANGE 1 START
# Empirical rollback: the original phase-level predictor produced the best minimum-voltage
# result in the test series, while the learned nodal slopes became over-restrictive on weak
# Phase-A nodes. Keep nodal/both modes available for A/B tests, but use phase by default.
VOLTAGE_CAP_MODE_DEFAULT = "phase"
# <<< V7 ENERGY MANAGEMENT CHANGE 1 END
# <<< V5 NODAL VOLTAGE/RAMP CHANGE 1 END
# <<< CHATTER/STABILITY CHANGE 1 END

# >>> USER REQUEST CHANGE 6 START: optional reserve/support features (OFF by default)
# >>> V14 OUTLIER VOLTAGE HOLD CHANGE 3 START
# Security pre-charge is reserved for genuine outlier days so normal-day cost
# optimisation remains active.  This threshold is applied AFTER the forecast
# safety factor (1.35 by default).  The observed real forecast outlier still
# clears this threshold, while ordinary ~1.4-1.6 MW peaks generally do not.
PEAK_RESERVE_THRESHOLD_KW_DEFAULT = 2300.0
# <<< V14 OUTLIER VOLTAGE HOLD CHANGE 3 END
# >>> V9 PHASE EVENT / PRECHARGE FIX 1 START
# Phase A is energy-limited at the extreme peak. Prepare to the configured 98%
# SoC ceiling; measured voltage support can still use this energy down to 2%.
PEAK_RESERVE_TARGET_PCT_DEFAULT = 98.0
PEAK_RESERVE_LEAD_HOURS_DEFAULT = 2.0
# >>> V17 FORECAST RESERVE LOCK CHANGE 0 START
# Optional ASAP fill: once a qualifying extreme peak appears anywhere in the
# forecast horizon, fill reserve as quickly as measured voltage safely allows.
# Once the reserve target is reached, the first battery action is held at zero
# until voltage ride-through is actually needed or the forecast condition clears.
PEAK_RESERVE_FILL_MODE_DEFAULT = "deadline"
# <<< V17 FORECAST RESERVE LOCK CHANGE 0 END
# <<< V9 PHASE EVENT / PRECHARGE FIX 1 END
# >>> CHATTER/STABILITY CHANGE 2 START
# Reserve is deliberately lower priority than voltage compliance.
PEAK_RESERVE_PENALTY_DEFAULT = 5.0e4      # objective penalty per kWh below reserve trajectory
# >>> V8 ROBUST PRECHARGE CHANGE 2 START
# Forecast is used for PREPARATION only. The safety factor helps a systematically
# under-predicting live forecast trigger reserve early enough, but does not dictate
# the amount of battery discharge during the event. Measured voltage does that.
PEAK_RESERVE_FORECAST_SAFETY_FACTOR_DEFAULT = 1.35
# >>> V12 SECURITY RIDE-THROUGH CHANGE 1 START
# Do not spend security energy on harmless ~0.96-pu pre-peak dips.  The actual
# compliance floor is 0.95 pu, so voltage ride-through is armed only very close
# to the limit.  0.958 gives a small feedback margin before 0.95 is reached.
# >>> V13 CONTINUOUS PRECHARGE CHANGE 1 START
# Keep ride-through close to the true 0.95-pu requirement, but do not leave an old
# support event latched for hours. These are the settings that were most promising
# in the v12 tests.
# >>> V14 OUTLIER VOLTAGE HOLD CHANGE 4 START
# Near-peak ride-through begins at 0.958 pu and exits after recovery to 0.964 pu.
# Far from an outlier, a still-compliant 0.95-0.96 pu dip is NOT allowed to consume
# reserve energy; only an actual <0.95-pu emergency can force support.
PEAK_RESERVE_EVENT_RELEASE_PU_DEFAULT = 0.958
PEAK_RESERVE_EVENT_RECOVER_PU_DEFAULT = 0.964
PEAK_RESERVE_EVENT_HOLD_STEPS_DEFAULT = 0
# <<< V14 OUTLIER VOLTAGE HOLD CHANGE 4 END
# <<< V13 CONTINUOUS PRECHARGE CHANGE 1 END
# <<< V12 SECURITY RIDE-THROUGH CHANGE 1 END
# >>> V9 PHASE EVENT / PRECHARGE FIX 2 START
# Charging-induced voltage depression pauses the affected phase rather than falsely
# releasing its reserve. Keep the pause short and hysteretic.
# V12: no artificial multi-step pre-charge pause.  The existing 0.97/0.978
# hard directional guard already provides the required hysteresis.
PEAK_RESERVE_PAUSE_HOLD_STEPS_DEFAULT = 0
# Give the charge-ramp controller enough time to move from ~50% toward ~98%.
# Reach the reserve target earlier so the charger cannot procrastinate into the
# final few hours before the outlier.
PEAK_RESERVE_LEAD_HOURS_DEFAULT = 6.0
# <<< V9 PHASE EVENT / PRECHARGE FIX 2 END
# <<< V8 ROBUST PRECHARGE CHANGE 2 END
# <<< CHATTER/STABILITY CHANGE 2 END

LOCAL_VOLTAGE_SUPPORT_START_PU_DEFAULT = 0.97
LOCAL_VOLTAGE_SUPPORT_PENALTY_DEFAULT = 2.0e4
# >>> V10 HARD PHASE DISPATCH 1 START
# First applied action is constrained from the CURRENT measured/actual phase state,
# rather than relying only on a soft horizon penalty. During voltage support the
# controller supplies approximately the minimum battery power needed to hold the
# dedicated 0.960-pu support target; during reserve preparation it may charge only
# up to a separate 0.970-pu import cap and cannot spend stored energy early.
HARD_PHASE_FIRST_ACTION_DEFAULT = True
# >>> V11 VOLTAGE HOLD CHANGE 1 START
# V10 could hold the weak phase close to the limit until it ran out of energy.
# V12 uses deadline-aware hard security charging and only starts SUPPORT very
# close to the true 0.95-pu limit, so harmless pre-peak dips do not waste stored energy.
# >>> V12 SECURITY RIDE-THROUGH CHANGE 2 START
# >>> V13 CONTINUOUS PRECHARGE CHANGE 2 START
# Aim slightly ABOVE the 0.970 hard no-charge threshold. The feedback loop then
# backs charging off smoothly before the hard guard has to intervene.
# >>> V14 OUTLIER VOLTAGE HOLD CHANGE 5 START
# Follow 0.963 pu while pre-charging: just above the new 0.960 hard no-charge
# boundary, leaving 0.010 pu to the true compliance floor.
PRECHARGE_VOLTAGE_TARGET_PU_DEFAULT = 0.963
PRECHARGE_VOLTAGE_FEEDBACK_GAIN_DEFAULT = 0.70
# Direct measured-voltage ride-through feedback.  This is deliberately independent
# of the forecast magnitude and corrects the learned import-cap drift seen in the
# real-forecast v11 test.
SUPPORT_VOLTAGE_FEEDBACK_GAIN_DEFAULT = 0.85
SUPPORT_MAX_DELTA_PER_CUSTOMER_KW_DEFAULT = 2.0
SUPPORT_RHO_MIN_MULT_DEFAULT = 0.50
SUPPORT_RHO_MAX_MULT_DEFAULT = 2.0
# Do not let a drifting learned phase cap demand export / near-zero import.  The
# feed-forward safe-import floor is scaled by customers and then corrected by
# measured voltage feedback.
SUPPORT_MIN_GRID_IMPORT_PER_CUSTOMER_KW_DEFAULT = 0.50
# Arm near-limit ride-through only close to the forecast outlier or once the ACTUAL
# feeder net demand is already high.  Actual <0.95 pu still overrides this.
SUPPORT_ARM_HOURS_DEFAULT = 6.0
SUPPORT_ARM_LOAD_KW_DEFAULT = 1800.0
# <<< V14 OUTLIER VOLTAGE HOLD CHANGE 5 END

# >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 1 START
# V14's main failure was structural: when measured voltage recovered for one
# sample, the support relay turned OFF. The following sample then had almost
# zero Phase-A support and voltage collapsed, causing support to turn ON again.
#
# V15 replaces that relay with a persistent measured-event supervisor and a
# continuous load-tracking voltage droop. Forecast remains useful for PRE-CHARGE,
# but forecast magnitude never determines ride-through battery power.
SECURITY_EVENT_ENTER_LOAD_KW_DEFAULT = 1800.0
# V16: proactive ride-through entry may occur slightly before the hard
# battery-action guard. This threshold is intentionally separate from both
# the ride-through voltage target and the hard battery guard.
SECURITY_EVENT_ENTER_VOLTAGE_PU_DEFAULT = 0.962
SECURITY_EVENT_EXIT_LOAD_KW_DEFAULT = 1400.0
SECURITY_EVENT_EXIT_STEPS_DEFAULT = 2
SECURITY_SUPPORT_FIXED_RHO_MULT_DEFAULT = 3.0
SECURITY_SUPPORT_GAIN_DEFAULT = 0.70
SECURITY_PRECHARGE_FIXED_RHO_MULT_DEFAULT = 3.0
SECURITY_PRECHARGE_GAIN_DEFAULT = 0.70
# <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 1 END
# Clamp the RLS slope used by the pre-charge feedback controller to a sane band
# around the schematic initial slope so a noisy learned slope cannot create a huge
# one-step charging correction.
PRECHARGE_RHO_MIN_MULT_DEFAULT = 0.25
PRECHARGE_RHO_MAX_MULT_DEFAULT = 4.0
# <<< V13 CONTINUOUS PRECHARGE CHANGE 2 END
# Hold the outlier just above the real 0.95-pu limit instead of spending the
# finite battery trying to maintain an unnecessarily high 0.960 pu.
PHASE_SUPPORT_VOLTAGE_TARGET_PU_DEFAULT = 0.958
# <<< V12 SECURITY RIDE-THROUGH CHANGE 2 END
# Additional robust ceiling on aggregate charging while security reserve is active.
# The voltage cap still limits charging further when necessary.  0.5 kW/customer
# gives Phase A <=232.5 kW charging at once: slow enough not to cause the previous
# one-step voltage collapses, but enough to replenish ~2.7 MWh over the preparation
# window in the measured outlier test.
# The authoritative pre-charge scheduler normally requests much less than this;
# 1 kW/customer simply gives it catch-up headroom if voltage permits.
SECURITY_MAX_CHARGE_PER_CUSTOMER_KW_DEFAULT = 1.00
PHASE_SUPPORT_DISCHARGE_BUFFER_KW_DEFAULT = 0.0
# <<< V11 VOLTAGE HOLD CHANGE 1 END
# <<< V10 HARD PHASE DISPATCH 1 END
# <<< USER REQUEST CHANGE 6 END


class PhaseVoltageEstimator:
    """One scalar recursive-least-squares estimator per phase.

    Model:   V_drop = rho * dP      (voltage drop in V caused by a change of dP kW in net import on this phase)
    Data:    successive measured pairs (V_k, P_k)  ->  y = V_{k-1} - V_k,  x = P_k - P_{k-1}
    Using DIFFERENCES means the unknown voltage offset (source voltage, tap position, capacitors...) cancels, so only
    the slope rho has to be learned. The offset is "anchored" to the latest measured voltage instead.
    """

    def __init__(self, rho0, forget=RLS_FORGET_DEFAULT, prior_steps=10.0, x_ref_kw=50.0,
                 min_dp_kw=5.0, max_innov_v=60.0, rho_floor_mult=0.05, rho_ceil_mult=10.0):
        self.rho0 = float(rho0)
        self.rho = float(rho0)
        self.lam = float(forget)
        # Initial covariance: the schematic value is worth about `prior_steps` typical steps of data (|dP| ~ x_ref_kw).
        self.p0 = 1.0 / (prior_steps * x_ref_kw ** 2)
        self.p = self.p0
        self.min_dp = min_dp_kw
        self.max_innov = max_innov_v
        self.rho_lo = rho_floor_mult * self.rho0     # sanity bounds around the schematic value
        self.rho_hi = rho_ceil_mult * self.rho0
        self.v_last = None
        self.p_last = None
        self.n_updates = 0

    def update(self, v_volts: float, p_kw: float) -> None:
        if not (np.isfinite(v_volts) and np.isfinite(p_kw)):
            return
        if self.v_last is not None:
            x = p_kw - self.p_last
            y = self.v_last - v_volts
            if abs(x) >= self.min_dp:                       # skip steps that carry no information about the slope
                gain = self.p * x / (self.lam + x * self.p * x)
                innov = float(np.clip(y - x * self.rho, -self.max_innov, self.max_innov))   # guards against tap jumps
                self.rho = float(np.clip(self.rho + gain * innov, self.rho_lo, self.rho_hi))
                self.p = min((self.p - gain * x * self.p) / self.lam, self.p0)
                self.n_updates += 1
        self.v_last, self.p_last = float(v_volts), float(p_kw)

    def caps(self, n: int, v_lo_volts: float, v_hi_volts: float, bias_kw: float, bias_decay: float):
        """Phase net-import limits (kW) for the next n steps, or None until the first measurement exists.
        hi: import must stay <= hi  (keeps voltage >= v_lo).   lo: import must stay >= lo  (keeps voltage <= v_hi)."""
        if self.v_last is None:
            return None
        hi0 = self.p_last + (self.v_last - v_lo_volts) / self.rho
        lo0 = self.p_last - (v_hi_volts - self.v_last) / self.rho
        # The QP plans with the FORECAST import, the real import will be off by roughly the last forecast error,
        # fading with time. Shift both limits by that expected error so the plan is judged on the real import.
        e = bias_kw * bias_decay ** (np.arange(n) + 1)
        hi = np.clip(hi0 - e, -1e5, 1e5)
        lo = np.clip(lo0 - e, -1e5, 1e5)
        return hi, lo


# >>> V5 NODAL VOLTAGE/RAMP CHANGE 2 START
class NodeVoltageEstimator(PhaseVoltageEstimator):
    """Local first-order voltage-vs-grid-import estimator for one monitored node.

    It deliberately reuses the same RLS machinery as the older phase estimator, but each node now has
    its own anchor voltage, local grid import and learned slope. This is still an approximation because
    distribution-feeder voltages are coupled across nodes; however it lets the joint QP place a voltage
    limit on the node that is actually weak instead of only constraining the whole phase-total import.
    """


def node_rho0_v_per_kw(node: str) -> float:
    """Initial nodal slope using the old phase schematic estimate expressed on the node's voltage base."""
    ph = node_phase(node)
    rho_pu_per_kw = RHO0_V_PER_KW[ph] / NOMINAL_VOLTAGE
    return rho_pu_per_kw * nominal_voltage_for_node(node)
# <<< V5 NODAL VOLTAGE/RAMP CHANGE 2 END


# ---- (c) Joint nodal MPC QP -------------------------------------------------------------------------
# >>> USER REQUEST CHANGE 7 START: clarify nodal MPC + add optional peak reserve/local voltage support
def solve_joint_nodal_mpc_qp(
    p_load,
    p_pv,
    eta,
    weight,
    hw,
    soc0,
    phase_caps,
    node_caps,
    k_slack,
    solver,
    peak_reserve=None,
    local_voltage_deficit=None,
    local_voltage_support_penalty=0.0,
    directional_voltage_guard=None,
    previous_batt_kw=None,
    battery_smoothing_weight=0.0,
    charge_ramp_kw=None,
    secondary_solver=None,
    rescue_directional_voltage_guard=None,
    phase_first_action_bounds=None,
    node_first_action_bounds=None,
):
    """Solve ONE receding-horizon QP containing a separate battery, grid and SoC trajectory for every node.

    This remains nodal MPC: each node has its own battery/grid/SoC decision variables. The nodes are solved
    together so that feeder-voltage constraints can coordinate them.

    Predictive voltage constraints may be supplied in two forms:
      * phase_caps[phase] = (import_hi, import_lo): legacy phase-total approximation.
      * node_caps[node]   = (import_hi, import_lo): NEW local nodal voltage->grid-power approximation.

    The nodal caps are normally preferable for this project because they respond to the voltage and power at
    the specific weak node instead of assuming every kW on the same phase has the same voltage effect.

    peak_reserve (optional dict):
        Robust PRE-CHARGE reserve. For nodes whose phase has not entered measured voltage-support
        mode, SoC is softly ramped toward target_pct by target_state and then held there. As soon
        as measured voltage releases that phase for support, the reserve constraint is removed
        completely so voltage support may use the battery down to the ordinary SoC floor.

    directional_voltage_guard (optional dict node -> mode):
        "no_charge"    -> HARD batt[node][0] >= 0
        "no_discharge" -> HARD batt[node][0] <= 0
        "idle"         -> HARD batt[node][0] == 0

        V9 uses "idle" during a charging-induced pre-charge voltage dip: stop
        harmful charging without needlessly spending stored peak-support energy.

    previous_batt_kw + battery_smoothing_weight:
        Convex first-action penalty on changes from the previously applied battery command.

    charge_ramp_kw (optional dict node -> kW/step):
        Asymmetric HARD first-action charging ramp. Positive=discharge, negative=charge.
        The correct floor is:
            batt[node][0] >= min(0, previous_batt_kw[node]) - charge_ramp_kw[node]
        so a battery may immediately reduce/stop discharge, but may only become MORE negative
        (increase charging) by the configured ramp. Over-voltage no-discharge mode bypasses this
        ramp so corrective charging is not artificially delayed.

    secondary_solver:
        Optional backup CVXPY solver. It is tried before predictive voltage caps are discarded.

    rescue_directional_voltage_guard:
        Instantaneous do-not-worsen guard used only if the normal no-cap fallback is still infeasible.

    phase_first_action_bounds (optional dict phase -> (batt_lo_kw, batt_hi_kw)):
        HARD first-action aggregate battery-power band derived from the current phase state.

    node_first_action_bounds (optional dict node -> (batt_lo_kw, batt_hi_kw)):
        V13 security-precharge allocation. During reserve preparation the aggregate
        voltage-following charge request is split across nodes by SoC energy deficit,
        then imposed as hard first-action node bounds. This prevents a nearly-full
        small battery from continuing to charge while a large weak-node battery remains low.
    """
    nodes = list(p_load)
    n = len(p_load[nodes[0]])
    eta = np.asarray(eta, dtype=float).reshape(-1)
    if len(eta) != n:
        raise ValueError(f"MPC input length mismatch: load={n}, eta={len(eta)}")

    for nd in nodes:
        if len(np.asarray(p_load[nd]).reshape(-1)) != n or len(np.asarray(p_pv[nd]).reshape(-1)) != n:
            raise ValueError(f"MPC horizon mismatch at {nd}: expected {n} samples.")

    # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 2 START
    def build_and_solve(active_phase_caps, active_node_caps, active_guard, active_charge_ramp):
    # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 2 END
        batt = {nd: cp.Variable(n) for nd in nodes}
        grid = {nd: cp.Variable(n) for nd in nodes}
        soc = {nd: cp.Variable(n + 1) for nd in nodes}
        cost = 0
        cons = []
        reserve_slack = {}

        for nd in nodes:
            h = hw[nd]
            pl = np.asarray(p_load[nd], dtype=float).reshape(-1)
            pv = np.asarray(p_pv[nd], dtype=float).reshape(-1)
            soc_lo = min(h["soc_lo_kwh"], soc0[nd])
            soc_hi = max(h["soc_hi_kwh"], soc0[nd])

            cost += cp.sum(
                -DELTA_HOURS * cp.multiply(eta, batt[nd])
                + weight * cp.multiply(eta, cp.square(grid[nd]))
            )

            cons += [
                grid[nd] == pl - pv - batt[nd],
                grid[nd] <= 3000,
                grid[nd] >= -1500,
                batt[nd] >= h["p_lo_kw"],
                batt[nd] <= h["p_hi_kw"],
                soc[nd][0] == soc0[nd],
                soc[nd][1:] == soc[nd][:-1] - DELTA_HOURS * batt[nd],
                soc[nd][1:] >= soc_lo,
                soc[nd][1:] <= soc_hi,
            ]

            guard_mode = None if not active_guard else active_guard.get(nd)
            if guard_mode == "no_charge":
                cons += [batt[nd][0] >= 0.0]
            elif guard_mode == "no_discharge":
                cons += [batt[nd][0] <= 0.0]
            elif guard_mode == "idle":
                cons += [batt[nd][0] == 0.0]

            # >>> V7 ENERGY MANAGEMENT CHANGE 3 START
            # FIX: the old p_prev-ramp formula also restricted how quickly a positive
            # DISCHARGE command could reduce, which could force continued discharge near
            # the SoC floor and make the QP infeasible. Only previous CHARGING is remembered.
            if active_charge_ramp and h["cap_kwh"] > 0 and guard_mode != "no_discharge":
                ramp = max(0.0, float(active_charge_ramp.get(nd, 0.0)))
                if ramp > 0.0:
                    p_prev = 0.0 if previous_batt_kw is None else float(previous_batt_kw.get(nd, 0.0))
                    charge_ramp_floor = min(0.0, p_prev) - ramp
                    cons += [batt[nd][0] >= charge_ramp_floor]
            # <<< V7 ENERGY MANAGEMENT CHANGE 3 END

            if battery_smoothing_weight > 0.0 and h["cap_kwh"] > 0:
                p_prev = 0.0 if previous_batt_kw is None else float(previous_batt_kw.get(nd, 0.0))
                cost += float(battery_smoothing_weight) * cp.square(batt[nd][0] - p_prev)

            if local_voltage_deficit and h["cap_kwh"] > 0:
                deficit = max(0.0, float(local_voltage_deficit.get(nd, 0.0)))
                if deficit > 0.0:
                    cost += -float(local_voltage_support_penalty) * deficit * batt[nd][0]

            # >>> V8 ROBUST PRECHARGE CHANGE 3 START
            # Forecast is used only to PREPARE energy. It must never strand energy once the
            # real feeder voltage says support is needed. Reserve is therefore phase-selective:
            # a measured low-voltage event releases the affected phase completely.
            if peak_reserve and peak_reserve.get("active") and h["cap_kwh"] > 0:
                released_phases = set(peak_reserve.get("release_phases", ()))
                if node_phase(nd) not in released_phases:
                    target_pct = float(peak_reserve["target_pct"])
                    target_state = int(peak_reserve["target_state"])
                    current_pct = 100.0 * float(soc0[nd]) / h["cap_kwh"]
                    start_pct = min(current_pct, target_pct)

                    floor_states = []
                    floor_pcts = []

                    # Before the target point, require steady progress so receding-horizon
                    # MPC cannot repeatedly decide to "charge later".
                    if target_state >= 1:
                        prep_end = min(target_state, n)
                        for j in range(1, prep_end + 1):
                            frac = j / max(1, target_state)
                            floor_states.append(j)
                            floor_pcts.append(start_pct + frac * (target_pct - start_pct))
                        # Once prepared, HOLD the target until a real voltage event releases
                        # this phase. Only the first MPC action is applied, so this is a robust
                        # way of preventing premature discharge without predicting peak size.
                        for j in range(prep_end + 1, n + 1):
                            floor_states.append(j)
                            floor_pcts.append(target_pct)
                    else:
                        # We are already inside/past the nominal lead point but the measured
                        # voltage has not yet requested support: keep the energy available.
                        for j in range(1, n + 1):
                            floor_states.append(j)
                            floor_pcts.append(target_pct)

                    if floor_states:
                        idx = np.asarray(floor_states, dtype=int)
                        floor_kwh = h["cap_kwh"] * np.asarray(floor_pcts, dtype=float) / 100.0
                        s = cp.Variable(nonneg=True)
                        cons += [soc[nd][idx] + s >= floor_kwh]
                        cost += float(peak_reserve["penalty"]) * s
                        reserve_slack[nd] = s
            # <<< V8 ROBUST PRECHARGE CHANGE 3 END

        # >>> V10 HARD PHASE DISPATCH 2 START
        # Hard CURRENT-action phase dispatch. Unlike the horizon voltage caps below,
        # these constraints cannot be traded away with voltage slack. They are based
        # on actual present load/PV and therefore also protect against a poor forecast.
        if phase_first_action_bounds:
            for ph, (b_lo, b_hi) in phase_first_action_bounds.items():
                members = [nd for nd in nodes if node_phase(nd) == ph and hw[nd]["cap_kwh"] > 0]
                if not members:
                    continue
                p_bat_phase0 = sum(batt[nd][0] for nd in members)
                cons += [p_bat_phase0 >= float(b_lo), p_bat_phase0 <= float(b_hi)]
        # <<< V10 HARD PHASE DISPATCH 2 END

        # >>> V13 CONTINUOUS PRECHARGE CHANGE 3 START
        # Per-node hard first action used only for security pre-charge balancing.
        if node_first_action_bounds:
            for nd, (b_lo, b_hi) in node_first_action_bounds.items():
                if nd not in batt or hw[nd]["cap_kwh"] <= 0:
                    continue
                cons += [batt[nd][0] >= float(b_lo), batt[nd][0] <= float(b_hi)]
        # <<< V13 CONTINUOUS PRECHARGE CHANGE 3 END

        phase_slack = {}
        if active_phase_caps:
            for ph, (c_hi, c_lo) in active_phase_caps.items():
                members = [nd for nd in nodes if node_phase(nd) == ph]
                p_phase = sum(grid[nd] for nd in members)
                s_hi = cp.Variable(n, nonneg=True)
                s_lo = cp.Variable(n, nonneg=True)
                cons += [p_phase <= c_hi + s_hi,
                         p_phase >= c_lo - s_lo]
                cost += k_slack * (cp.sum(s_hi) + cp.sum(s_lo))
                phase_slack[ph] = (s_hi, s_lo)

        # >>> V5 NODAL VOLTAGE/RAMP CHANGE 4 START
        # Local predictive voltage constraints. Each controlled node receives its own allowable grid-import
        # band inferred from its latest measured voltage and learned local V-vs-P slope.
        node_slack = {}
        if active_node_caps:
            for nd, (c_hi, c_lo) in active_node_caps.items():
                if nd not in grid:
                    continue
                s_hi = cp.Variable(n, nonneg=True)
                s_lo = cp.Variable(n, nonneg=True)
                cons += [grid[nd] <= c_hi + s_hi,
                         grid[nd] >= c_lo - s_lo]
                cost += k_slack * (cp.sum(s_hi) + cp.sum(s_lo))
                node_slack[nd] = (s_hi, s_lo)
        # <<< V5 NODAL VOLTAGE/RAMP CHANGE 4 END

        problem = cp.Problem(cp.Minimize(cost), cons)

        # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 3 START
        # Try the configured primary solver first (V19 default CLARABEL), then the optional
        # secondary solver (V19 default OSQP) before throwing away predictive voltage constraints.
        installed = {str(s).upper() for s in cp.installed_solvers()}

        def _try_solver(solver_name):
            if not solver_name:
                return False, "not_requested"
            solver_name = str(solver_name).upper()
            if solver_name not in installed:
                return False, f"{solver_name}_not_installed"
            kwargs = {"max_iter": 50000} if solver_name == "OSQP" else {}
            try:
                problem.solve(solver=getattr(cp, solver_name), verbose=False, **kwargs)
            except Exception as e:
                return False, f"solver_error[{solver_name}]: {e}"
            solved = (
                problem.status in ("optimal", "optimal_inaccurate")
                and all(batt[nd].value is not None for nd in nodes)
            )
            return solved, str(problem.status)

        primary_name = str(solver).upper()
        solved, primary_status = _try_solver(primary_name)
        solver_used = primary_name

        secondary_status = ""
        secondary_name = "" if secondary_solver is None else str(secondary_solver).upper()
        if not solved and secondary_name and secondary_name != primary_name:
            solved2, secondary_status = _try_solver(secondary_name)
            if solved2:
                solved = True
                solver_used = secondary_name

        if not solved:
            final_status = secondary_status if secondary_status else primary_status
            return {
                "status": final_status,
                "primary_solver_status": primary_status,
                "secondary_solver_status": secondary_status,
                "solver_used": solver_used,
            }, None
        # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 3 END

        res = {
            "status": str(problem.status),
            "obj": float(problem.value),
            "solver_used": solver_used,
            "primary_solver_status": primary_status,
            "secondary_solver_status": secondary_status,
            "batt": {nd: np.asarray(batt[nd].value).flatten() for nd in nodes},
            "grid": {nd: np.asarray(grid[nd].value).flatten() for nd in nodes},
            "soc": {nd: np.asarray(soc[nd].value).flatten() for nd in nodes},
            "slack": {ph: (np.maximum(np.asarray(s[0].value).flatten(), 0.0),
                            np.maximum(np.asarray(s[1].value).flatten(), 0.0))
                      for ph, s in phase_slack.items()},
            "node_slack": {nd: (np.maximum(np.asarray(s[0].value).flatten(), 0.0),
                                np.maximum(np.asarray(s[1].value).flatten(), 0.0))
                           for nd, s in node_slack.items()},
            "reserve_slack": {nd: np.maximum(np.asarray(s.value).flatten(), 0.0)
                              for nd, s in reserve_slack.items()},
        }
        return res, True

    predictive_caps_requested = bool(phase_caps) or bool(node_caps)
    res, ok = build_and_solve(
        phase_caps, node_caps, directional_voltage_guard, charge_ramp_kw
    )
    voltage_fallback = False
    safety_rescue = False
    voltage_cap_failure_status = ""

    if ok is None and predictive_caps_requested:
        voltage_cap_failure_status = str(res.get("status", "unknown"))
        print(f"  WARNING: predictive voltage-cap solve failed ({voltage_cap_failure_status}); "
              "re-solving without predictive voltage caps for this step. "
              "Hard directional guards and hard charge-ramp limits remain active.")
        voltage_fallback = True
        res, ok = build_and_solve(
            None, None, directional_voltage_guard, charge_ramp_kw
        )

    # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 4 START
    # A second failure previously caused EVERY battery command to be set to zero.
    # Retry once with only the instantaneous actual-violation safety guard and no
    # charging-ramp memory. Battery power/SoC bounds remain hard.
    if ok is None and (directional_voltage_guard or charge_ramp_kw):
        safety_rescue = True
        failed_status = str(res.get("status", "unknown"))
        print(f"  WARNING: guarded fallback also failed ({failed_status}); "
              "retrying emergency MPC with instantaneous voltage guard and no charge-ramp.")
        res, ok = build_and_solve(
            None, None, rescue_directional_voltage_guard or {}, None
        )
    # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 4 END

    if ok is None:
        return {
            "status": res["status"], "obj": float("nan"), "batt": None, "grid": None,
            "soc": None, "slack": {}, "node_slack": {}, "reserve_slack": {},
            "voltage_caps_used": False, "voltage_fallback": voltage_fallback,
            "safety_rescue": safety_rescue,
            "voltage_cap_failure_status": voltage_cap_failure_status,
            "solver_used": res.get("solver_used", ""),
            "primary_solver_status": res.get("primary_solver_status", ""),
            "secondary_solver_status": res.get("secondary_solver_status", ""),
        }

    res["voltage_caps_used"] = predictive_caps_requested and not voltage_fallback
    res["voltage_fallback"] = voltage_fallback
    res["safety_rescue"] = safety_rescue
    res["voltage_cap_failure_status"] = voltage_cap_failure_status
    return res
# <<< USER REQUEST CHANGE 7 END

# <<< VOLTAGE CHANGE 1 END


# ============================================================
# 5. SoC measurement logger
# ============================================================

class SocLogger:

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
            print(f"  HIL internal-battery SoC register {SOC_INPUT_REGISTER} resolved (used for Node-646 MPC SoC feedback).")
        except Exception:
            print(f"  WARNING: HIL internal-battery SoC register {SOC_INPUT_REGISTER} did not read back; "
                  "Node-646 measured SoC feedback will be unavailable.")

    def log_step(self):
        if not self.enabled:
            return None
        try:
            return self._read_soc()
        except Exception:
            return None

    def _read_voltages(self):
        rr = self.conn.client.read_input_registers(address=4001, count=16)
        if rr is None or rr.isError():
            raise IOError(f"Failed to read Voltage input registers 4001-4016")
        return rr.registers

    def _read_voltage(self, voltage_reg) -> float:
        rr = self.conn.client.read_input_registers(address=voltage_reg, count=1)
        if rr is None or rr.isError():
            raise IOError(f"Failed to read Voltage input register {voltage_reg}")
        return rr.registers[0]

    def voltage_log_step(self,voltage_reg):
        if not self.enabled:
            return None
        try:
            return self._read_voltage(voltage_reg)
        except Exception:
            return None    
    

    def close(self) -> None:
        pass


# >>> V19 BATTERY EMULATOR CHANGE 3 START: physical battery emulator serial interface
class HardwareBatteryEmulator:
    """Interface to the laboratory grid-interactive physical battery emulator.

    Protocol used by the existing ECE4191 hardware-sync implementation:
      * serial 9600 baud, 8 data bits, no parity, 1 stop bit;
      * unsolicited five-digit ASCII SoC samples, raw range 00000..65500;
      * charge/discharge commands Cxxx / Dxxx, xxx = 000..255;
      * controller convention +Pbat = discharge, -Pbat = charge.

    The dynamic command mapper preserves the MPC energy meaning of one data row
    (DELTA_HOURS = 0.5 h) by selecting the real hold duration and command code together.
    """

    def __init__(self, port: str):
        if serial is None:
            raise RuntimeError(
                "Hardware battery-emulator mode requires pyserial. Install it with "
                "'sudo apt install python3-serial' or 'pip install pyserial --break-system-packages'."
            )
        self.port = port
        self.ser = serial.Serial(
            port=port,
            baudrate=EMULATOR_BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.05,
        )
        self.buffer = ""
        self.latest_raw = None
        self.latest_rx_monotonic = None
        self.ser.reset_input_buffer()
        print(f"  Physical battery emulator serial connected: {port}")

    def _consume_available(self) -> bool:
        """Drain serial bytes and return True when at least one new valid SoC arrived."""
        got_new = False
        waiting = self.ser.in_waiting
        data = self.ser.read(waiting) if waiting > 0 else self.ser.read(1)
        if data:
            self.buffer += data.decode("ascii", errors="ignore")

        matches = list(re.finditer(r"\d{5}", self.buffer))
        if matches:
            last_end = 0
            for match in matches:
                value = int(match.group(0))
                last_end = match.end()
                if 0 <= value <= EMULATOR_SOC_MAX_RAW:
                    self.latest_raw = value
                    self.latest_rx_monotonic = time.monotonic()
                    got_new = True
            self.buffer = self.buffer[last_end:]

        if len(self.buffer) > 100:
            self.buffer = self.buffer[-20:]
        return got_new

    def read_latest(self, max_wait_s: float = EMULATOR_READ_WAIT_S):
        """Return (raw, percent, sample_age_s, fresh)."""
        deadline = time.monotonic() + max(0.0, float(max_wait_s))
        fresh = False
        while True:
            if self._consume_available():
                fresh = True
                break
            if time.monotonic() >= deadline:
                break
            time.sleep(0.02)

        raw = self.latest_raw
        if raw is None:
            return None, None, None, False
        pct = 100.0 * raw / EMULATOR_SOC_MAX_RAW
        age_s = (None if self.latest_rx_monotonic is None
                 else max(0.0, time.monotonic() - self.latest_rx_monotonic))
        return raw, pct, age_s, fresh

    def send_command(self, command: str) -> None:
        self.ser.write(command.encode("ascii"))
        self.ser.flush()

    def power_to_dynamic_command(
        self,
        p_bat_kw: float,
        capacity_kwh: float,
        min_hold_s: float,
        max_hold_s: float,
        idle_hold_s: float,
        preferred_code: int,
        charge_max_raw_per_s: float,
        discharge_max_raw_per_s: float,
    ) -> dict:
        """Map one MPC battery action to a dynamically time-scaled Cxxx/Dxxx command."""
        if capacity_kwh <= 0:
            raise ValueError("capacity_kwh must be > 0")
        if min_hold_s <= 0 or max_hold_s <= 0 or idle_hold_s <= 0:
            raise ValueError("Hardware-emulator hold durations must be > 0")
        if min_hold_s > max_hold_s:
            raise ValueError("hardware min hold cannot exceed hardware max hold")
        if not 1 <= preferred_code <= 255:
            raise ValueError("hardware preferred code must be in 1..255")

        p = float(p_bat_kw)
        if abs(p) <= EMULATOR_COMMAND_DEADBAND_KW:
            return {
                "command": "D000", "code": 0, "saturated": False,
                "target_delta_raw": 0.0, "target_delta_pct": 0.0,
                "hold_seconds": float(idle_hold_s),
                "unclamped_hold_seconds": 0.0,
                "required_rate_raw_per_s": 0.0,
                "max_rate_raw_per_s": (discharge_max_raw_per_s if p >= 0
                                        else charge_max_raw_per_s),
                "equivalent_power_kw": 0.0,
            }

        discharge = p > 0
        max_rate = discharge_max_raw_per_s if discharge else charge_max_raw_per_s
        if max_rate <= 0:
            raise ValueError("Hardware-emulator calibrated max rate must be > 0")

        target_delta_raw = abs(p) * DELTA_HOURS / capacity_kwh * EMULATOR_SOC_MAX_RAW
        target_delta_pct = 100.0 * target_delta_raw / EMULATOR_SOC_MAX_RAW

        preferred_rate = max_rate * (preferred_code / 255.0)
        unclamped_hold = target_delta_raw / preferred_rate
        hold_seconds = min(max(unclamped_hold, min_hold_s), max_hold_s)

        required_rate = target_delta_raw / hold_seconds
        code_float = 255.0 * required_rate / max_rate
        saturated = code_float > 255.0
        code = int(round(min(255.0, max(1.0, code_float))))

        prefix = "D" if discharge else "C"
        command = f"{prefix}{code:03d}"

        achieved_raw_delta = max_rate * (code / 255.0) * hold_seconds
        equiv_mag_kw = achieved_raw_delta / EMULATOR_SOC_MAX_RAW * capacity_kwh / DELTA_HOURS
        equivalent_power_kw = equiv_mag_kw if discharge else -equiv_mag_kw

        return {
            "command": command,
            "code": code,
            "saturated": saturated,
            "target_delta_raw": target_delta_raw,
            "target_delta_pct": target_delta_pct,
            "hold_seconds": hold_seconds,
            "unclamped_hold_seconds": unclamped_hold,
            "required_rate_raw_per_s": required_rate,
            "max_rate_raw_per_s": max_rate,
            "equivalent_power_kw": equivalent_power_kw,
        }

    def send_dynamic_power_command(self, p_bat_kw: float, capacity_kwh: float, **kwargs) -> dict:
        info = self.power_to_dynamic_command(p_bat_kw, capacity_kwh, **kwargs)
        self.send_command(info["command"])
        return info

    def hold_and_read(
        self,
        duration_s: float,
        wait_s: float,
        progress_every_s: float,
        refresh_command: str | None = None,
        refresh_every_s: float = 0.0,
    ):
        """Hold the current step while continuously receiving physical-emulator SoC."""
        start = time.monotonic()
        next_progress = progress_every_s if progress_every_s > 0 else float("inf")
        next_refresh = (refresh_every_s if refresh_command and refresh_every_s > 0
                        else float("inf"))
        latest_raw = latest_pct = latest_age = None
        any_fresh = False
        refresh_count = 0

        while True:
            elapsed = time.monotonic() - start
            remaining = duration_s - elapsed
            if remaining <= 0:
                break

            if elapsed >= next_refresh:
                self.send_command(refresh_command)
                refresh_count += 1
                next_refresh += refresh_every_s

            wait_now = min(max(0.05, wait_s), max(0.05, remaining))
            raw, pct, age_s, fresh = self.read_latest(wait_now)
            if raw is not None:
                latest_raw, latest_pct, latest_age = raw, pct, age_s
            if fresh:
                any_fresh = True

            elapsed = time.monotonic() - start
            if elapsed >= next_progress:
                text = "no SoC sample" if latest_raw is None else f"SoC {latest_raw:05d} ({latest_pct:.3f}%)"
                print(f"    hardware hold {min(elapsed, duration_s):6.1f}/{duration_s:.1f} s | {text}")
                next_progress += progress_every_s

        raw, pct, age_s, fresh = self.read_latest(min(0.25, max(0.05, wait_s)))
        if raw is not None:
            latest_raw, latest_pct, latest_age = raw, pct, age_s
        any_fresh = any_fresh or fresh
        return latest_raw, latest_pct, latest_age, any_fresh, refresh_count

    def stop(self) -> None:
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.write(b"D000")
                self.ser.flush()
        except Exception:
            pass

    def close(self) -> None:
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
# <<< V19 BATTERY EMULATOR CHANGE 3 END


# >>> USER REQUEST CHANGE 13 START: robust voltage snapshots and weakest-node phase reference
def refresh_voltage_snapshot(soc_logger, dry_run, node_voltage, node_v_valid, fallback_warned):
    """Refresh all 16 voltages. Failed/missing channels fall back to nominal for logging but are marked invalid."""
    if dry_run:
        for nd in NODE_MAP:
            node_voltage[nd] = nominal_voltage_for_node(nd)
            node_v_valid[nd] = False
        return fallback_warned

    try:
        values = soc_logger._read_voltages()
    except Exception as exc:
        values = None
        if not fallback_warned:
            print(f"  WARNING: voltage block read failed ({exc}); using nominal fallback until a valid read returns.")
            fallback_warned = True

    for nd in NODE_MAP:
        v = None
        if values is not None:
            idx = NODE_MAP[nd]["voltage"] - 4001
            if 0 <= idx < len(values):
                v = values[idx]
        if v is None or not np.isfinite(v) or float(v) <= 0.0:
            node_voltage[nd] = nominal_voltage_for_node(nd)
            node_v_valid[nd] = False
            if not fallback_warned:
                print(f"  WARNING: no valid voltage reading for {nd}; using nominal "
                      f"{nominal_voltage_for_node(nd)} V (further fallbacks not printed).")
                fallback_warned = True
        else:
            node_voltage[nd] = float(v)
            node_v_valid[nd] = True
    return fallback_warned


def phase_voltage_measurement(ph, node_voltage, node_v_valid, reference_mode="minimum"):
    """Return (control_pu, minimum_pu, minimum_node, average_pu), including node 634 on its own per-unit base."""
    vals = [(nd, node_voltage_pu(nd, node_voltage[nd])) for nd in NODE_MAP
            if node_phase(nd) == ph and node_v_valid.get(nd, False)]
    if not vals:
        return None, None, None, None
    min_node, min_pu = min(vals, key=lambda item: item[1])
    avg_pu = float(np.mean([v for _, v in vals]))
    control_pu = float(min_pu if reference_mode == "minimum" else avg_pu)
    return control_pu, float(min_pu), min_node, avg_pu
# <<< USER REQUEST CHANGE 13 END


# ============================================================
# 6. Console output
# ============================================================

# >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 5 START
# The old "Batt kW" console column was ONLY Node 646, which made a feeder-wide
# discharge look like the whole battery fleet was idle.
_HDR = (f"{'Step':>5} {'Day':>3} {'k':>3} {'Load kW':>9} {'PV kW':>8} "
        f"{'Bat646':>9} {'BatTot':>9} {'646 action':>10} {'Grid kW':>10} "
        f"{'SoC% pred':>10} {'SoC% HIL(646)':>14} {'SoC% HW(646)':>13}")


def print_step(step, day, k, load, pv, batt646, batt_total, grid, soc_pred, soc_hil, soc_hardware):
    hil = f"{soc_hil:14.2f}" if soc_hil is not None else f"{'-':>14}"
    hw = f"{soc_hardware:13.2f}" if soc_hardware is not None else f"{'-':>13}"
    print(f"{step:5d} {day:3d} {k:3d} {load:9.1f} {pv:8.1f} "
          f"{batt646:9.2f} {batt_total:9.2f} {_action(batt646):>10} {grid:10.2f} "
          f"{soc_pred:10.2f} {hil} {hw}")
# <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 5 END


# ============================================================
# 7. Main -- feeder-wide receding-horizon MPC
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="ECE4191 Project -- joint nodal receding-horizon MPC with optional voltage constraints"
    )
    # >>> USER REQUEST CHANGE 8 START: remove aggregate battery args; expose per-customer battery parameters
    parser.add_argument("--actual", default="Code_and_data/agg_jan2013_students.csv",
                        help="Per-node actual load/PV CSV (fed to the feeder in real time).")
    parser.add_argument("--playback-days", type=int, default=DEFAULT_PLAYBACK_DAYS,
                        help=f"Number of days to play back (default {DEFAULT_PLAYBACK_DAYS}).")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS)
    parser.add_argument("--weight", type=float, default=DEFAULT_WEIGHT,
                        help=f"MPC/QP objective weight w (default {DEFAULT_WEIGHT}).")
    parser.add_argument("--battery-capacity-per-customer-kwh", type=float,
                        default=DEFAULT_BATTERY_CAPACITY_PER_CUSTOMER_KWH,
                        help=f"Battery energy capacity per customer in kWh (V18 default {DEFAULT_BATTERY_CAPACITY_PER_CUSTOMER_KWH:g}).")
    parser.add_argument("--battery-power-per-customer-kw", type=float,
                        default=DEFAULT_BATTERY_POWER_PER_CUSTOMER_KW,
                        help="Charge/discharge power limit per customer in kW (default 5).")
    parser.add_argument("--initial-soc-pct", type=float, default=DEFAULT_INITIAL_SOC_PCT,
                        help="Initial SoC for every nodal battery in percent (default 50).")
    # <<< USER REQUEST CHANGE 8 END
    parser.add_argument("--solver", default=PRIMARY_SOLVER_DEFAULT,
                        help="Primary CVXPY solver (V19 default CLARABEL).")
    # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 6 START
    parser.add_argument("--secondary-solver", default=SECONDARY_SOLVER_DEFAULT,
                        help="Backup CVXPY solver tried before voltage caps are discarded when the primary solver fails "
                             "(V19 default OSQP; use 'none' to disable).")
    parser.add_argument("--no-peak-guard-release-override", action="store_true",
                        help="Disable the default rule that clears a stale no-discharge guard at peak-reserve release "
                             "once voltage is safely below the high release threshold.")
    # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 6 END
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
    # >>> V19 BATTERY EMULATOR CHANGE 4 START: selectable Node-646 feedback implementation
    parser.add_argument("--battery-emulator", "--battery-emulator-mode",
                        choices=["hil", "hardware", "none"], default="hil",
                        help="Node-646 battery implementation/SoC feedback source: "
                             "hil = HIL internal battery (V18 behaviour), "
                             "hardware = laboratory serial battery emulator, "
                             "none = no measured SoC feedback; use MPC prediction (default: hil).")
    parser.add_argument("--no-soc-feedback", "--no-measurements", dest="no_soc_feedback", action="store_true",
                        help="Backwards-compatible override for --battery-emulator none. "
                             "No Node-646 measured SoC is used and both measurement CSV fields are '-'.")
    parser.add_argument("--hardware-emu-port", default=DEFAULT_EMULATOR_PORT,
                        help=f"Physical battery-emulator serial port (default: {DEFAULT_EMULATOR_PORT}).")
    parser.add_argument("--hardware-emu-wait", type=float, default=EMULATOR_READ_WAIT_S,
                        help=f"Maximum wait for a fresh hardware SoC packet (default {EMULATOR_READ_WAIT_S:g} s).")
    parser.add_argument("--hardware-emu-charge-rate", type=float, default=EMULATOR_CHARGE_MAX_RAW_PER_S,
                        help="Calibrated C255 SoC rate in raw counts/s (default 16).")
    parser.add_argument("--hardware-emu-discharge-rate", type=float, default=EMULATOR_DISCHARGE_MAX_RAW_PER_S,
                        help="Calibrated D255 SoC rate magnitude in raw counts/s (default 16).")
    parser.add_argument("--hardware-emu-stale-limit", type=float, default=DEFAULT_HARDWARE_STALE_LIMIT_S,
                        help="Abort HARDWARE feedback if the latest SoC sample is older than this many seconds.")
    parser.add_argument("--hardware-min-hold-seconds", type=float, default=DEFAULT_HARDWARE_MIN_HOLD_S,
                        help="Minimum real hold for a non-idle hardware-emulator MPC action (default 30 s).")
    parser.add_argument("--hardware-max-hold-seconds", type=float, default=DEFAULT_HARDWARE_MAX_HOLD_S,
                        help="Maximum real hold for a non-idle hardware-emulator MPC action (default 500 s).")
    parser.add_argument("--hardware-idle-hold-seconds", type=float, default=DEFAULT_HARDWARE_IDLE_HOLD_S,
                        help="Real hold for an idle/deadband hardware-emulator action (default 15 s).")
    parser.add_argument("--hardware-preferred-code", type=int, default=DEFAULT_HARDWARE_PREFERRED_CODE,
                        help="Preferred Cxxx/Dxxx magnitude used when choosing dynamic hold time (default 200).")
    parser.add_argument("--hardware-command-refresh-seconds", type=float,
                        default=DEFAULT_HARDWARE_COMMAND_REFRESH_S,
                        help="Re-send a nonzero hardware command during long holds at this interval; 0 disables refresh.")
    parser.add_argument("--hardware-hold-progress-seconds", type=float,
                        default=DEFAULT_HARDWARE_HOLD_PROGRESS_S,
                        help="Print hardware hold progress this often; 0 disables progress output (default 30 s).")
    # <<< V19 BATTERY EMULATOR CHANGE 4 END
    parser.add_argument("--measurement-delay", type=float, default=0.2,
                        help="Seconds to wait after a write before reading SoC.")
    parser.add_argument("--progress-every", type=int, default=1,
                        help="Print one row every N steps (0 = summary only).")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full dry-run Modbus payloads.")
    # >>> VOLTAGE CHANGE 2a START: command-line options <<<
    parser.add_argument("--no-voltage-constraint", action="store_true",
                        help="Switch all predictive voltage-to-power limits off. Hard measured-voltage guards/ramp limits remain available.")
    # >>> V5 NODAL VOLTAGE/RAMP CHANGE 5 START
    parser.add_argument("--voltage-cap-mode", choices=["nodal", "phase", "both"],
                        default=VOLTAGE_CAP_MODE_DEFAULT,
                        help="Predictive voltage model: phase (default) uses the empirically more stable phase-total model; "
                             "nodal uses each node's learned local V-P model; both applies both sets of soft caps.")
    parser.add_argument("--max-charge-ramp-per-customer-kw", type=float,
                        default=MAX_CHARGE_RAMP_PER_CUSTOMER_KW_DEFAULT,
                        help="Hard maximum increase in CHARGING magnitude per MPC step, in kW/customer. "
                             "Negative battery power is charging. 0 disables the ramp limit (default 0.5).")
    # >>> V10 HARD PHASE DISPATCH 3 START
    parser.add_argument("--no-hard-phase-first-action", action="store_true",
                        help="Disable V10 hard current-step phase voltage dispatch (not recommended for voltage-compliance tests).")
    parser.add_argument("--phase-support-discharge-buffer-kw", type=float,
                        default=PHASE_SUPPORT_DISCHARGE_BUFFER_KW_DEFAULT,
                        help="Extra aggregate discharge permitted above the minimum phase support requirement, in kW (default 0).")
    # >>> V11 VOLTAGE HOLD CHANGE 2 START
    parser.add_argument("--precharge-voltage-target-pu", type=float,
                        default=PRECHARGE_VOLTAGE_TARGET_PU_DEFAULT,
                        help="Weakest-phase voltage target followed continuously during security pre-charge (default 0.972 pu).")
    # >>> V13 CONTINUOUS PRECHARGE CHANGE 4 START
    parser.add_argument("--precharge-voltage-feedback-gain", type=float,
                        default=PRECHARGE_VOLTAGE_FEEDBACK_GAIN_DEFAULT,
                        help="Gain on measured-voltage correction of the pre-charge command (default 0.70).")
    parser.add_argument("--precharge-rho-min-mult", type=float,
                        default=PRECHARGE_RHO_MIN_MULT_DEFAULT,
                        help="Minimum RLS slope used by pre-charge feedback as a multiple of the initial phase slope (default 0.25).")
    parser.add_argument("--precharge-rho-max-mult", type=float,
                        default=PRECHARGE_RHO_MAX_MULT_DEFAULT,
                        help="Maximum RLS slope used by pre-charge feedback as a multiple of the initial phase slope (default 4.0).")
    # <<< V13 CONTINUOUS PRECHARGE CHANGE 4 END
    parser.add_argument("--phase-support-voltage-target-pu", type=float,
                        default=PHASE_SUPPORT_VOLTAGE_TARGET_PU_DEFAULT,
                        help="Weakest-phase target used by hard active-power ride-through (default 0.958 pu).")
    # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 6 START
    parser.add_argument("--support-voltage-feedback-gain", type=float,
                        default=SUPPORT_VOLTAGE_FEEDBACK_GAIN_DEFAULT,
                        help="Measured-voltage feedback gain used during ride-through (default 0.85).")
    parser.add_argument("--support-max-delta-per-customer-kw", type=float,
                        default=SUPPORT_MAX_DELTA_PER_CUSTOMER_KW_DEFAULT,
                        help="Maximum change in aggregate support discharge per step, scaled per customer (default 2.0 kW/customer).")
    parser.add_argument("--support-rho-min-mult", type=float,
                        default=SUPPORT_RHO_MIN_MULT_DEFAULT,
                        help="Minimum phase slope used by support feedback as a multiple of the initial slope (default 0.5).")
    parser.add_argument("--support-rho-max-mult", type=float,
                        default=SUPPORT_RHO_MAX_MULT_DEFAULT,
                        help="Maximum phase slope used by support feedback as a multiple of the initial slope (default 2.0).")
    parser.add_argument("--support-min-grid-import-per-customer-kw", type=float,
                        default=SUPPORT_MIN_GRID_IMPORT_PER_CUSTOMER_KW_DEFAULT,
                        help="Lower floor on learned safe phase import during support, in kW/customer (default 0.5).")
    parser.add_argument("--support-arm-hours", type=float, default=SUPPORT_ARM_HOURS_DEFAULT,
                        help="Arm near-limit voltage ride-through this many forecast hours before the outlier peak (default 6 h).")
    parser.add_argument("--support-arm-load-kw", type=float, default=SUPPORT_ARM_LOAD_KW_DEFAULT,
                        help="Legacy V14 ride-through arming threshold.")
    # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 6 END

    # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 2 START
    parser.add_argument("--security-event-enter-load-kw", type=float,
                        default=SECURITY_EVENT_ENTER_LOAD_KW_DEFAULT,
                        help="Actual feeder net-load threshold that permits a phase to latch into ride-through (default 1800 kW).")
    parser.add_argument("--security-event-enter-voltage-pu", type=float,
                        default=SECURITY_EVENT_ENTER_VOLTAGE_PU_DEFAULT,
                        help="Phase-voltage threshold for proactive ride-through entry when feeder load is above the event threshold. "
                             "Separate from the hard battery guard and support target (default 0.962 pu).")
    parser.add_argument("--security-event-exit-load-kw", type=float,
                        default=SECURITY_EVENT_EXIT_LOAD_KW_DEFAULT,
                        help="Actual feeder net-load threshold below which ride-through may exit (default 1400 kW).")
    parser.add_argument("--security-event-exit-steps", type=int,
                        default=SECURITY_EVENT_EXIT_STEPS_DEFAULT,
                        help="Recovered consecutive steps required before ending a latched ride-through (default 2).")
    parser.add_argument("--security-support-fixed-rho-mult", type=float,
                        default=SECURITY_SUPPORT_FIXED_RHO_MULT_DEFAULT,
                        help="Fixed ride-through phase sensitivity as a multiple of original rho (default 3.0).")
    parser.add_argument("--security-support-gain", type=float,
                        default=SECURITY_SUPPORT_GAIN_DEFAULT,
                        help="Measured-voltage droop gain during ride-through (default 0.70).")
    parser.add_argument("--security-precharge-fixed-rho-mult", type=float,
                        default=SECURITY_PRECHARGE_FIXED_RHO_MULT_DEFAULT,
                        help="Fixed pre-charge phase sensitivity as a multiple of original rho (default 3.0).")
    parser.add_argument("--security-precharge-gain", type=float,
                        default=SECURITY_PRECHARGE_GAIN_DEFAULT,
                        help="Measured-voltage gain used by security pre-charge (default 0.70).")
    # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 2 END
    parser.add_argument("--security-max-charge-per-customer-kw", type=float,
                        default=SECURITY_MAX_CHARGE_PER_CUSTOMER_KW_DEFAULT,
                        help="Maximum aggregate security/pre-charge rate expressed per customer (default 1.0 kW/customer). "
                             "The voltage-based import cap may reduce it further.")
    # <<< V11 VOLTAGE HOLD CHANGE 2 END
    # <<< V10 HARD PHASE DISPATCH 3 END
    # <<< V5 NODAL VOLTAGE/RAMP CHANGE 5 END
    # >>> CHATTER/STABILITY CHANGE 5 START: stateful hard directional guard + smoothing options
    parser.add_argument("--no-directional-voltage-guard", action="store_true",
                        help="Disable the default stateful hard first-action voltage guard.")
    parser.add_argument("--guard-v-min-pu", type=float, default=GUARD_V_MIN_PU_DEFAULT,
                        help="Hard battery-action lower threshold. At/below this voltage charging is forbidden (default 0.97 pu).")
    parser.add_argument("--guard-v-max-pu", type=float, default=GUARD_V_MAX_PU_DEFAULT,
                        help="Hard battery-action upper threshold. At/above this voltage discharging is forbidden (default 1.03 pu).")
    parser.add_argument("--directional-guard-engage-margin-pu", type=float,
                        default=DIRECTIONAL_GUARD_ENGAGE_MARGIN_PU_DEFAULT,
                        help="Optional pre-emptive margin inside the hard action band. Default 0 means engage exactly at 0.97/1.03.")
    parser.add_argument("--directional-guard-release-margin-pu", type=float,
                        default=DIRECTIONAL_GUARD_RELEASE_MARGIN_PU_DEFAULT,
                        help="Recovery hysteresis inside the hard action band. Default 0.008 gives 0.978/1.022 pu release thresholds.")
    parser.add_argument("--directional-guard-hold-steps", type=int,
                        default=DIRECTIONAL_GUARD_HOLD_STEPS_DEFAULT,
                        help="Minimum guard dwell time after an engage/re-engage event (default 2 MPC steps).")
    parser.add_argument("--battery-smoothing-weight", type=float, default=BATTERY_SMOOTHING_WEIGHT_DEFAULT,
                        help="Convex penalty on change in the first battery command from the previous applied command. "
                             "0 disables smoothing (default 0.25).")
    # <<< CHATTER/STABILITY CHANGE 5 END
    parser.add_argument("--v-min-pu", type=float, default=V_MIN_PU_DEFAULT,
                        help="Predictive MPC lower voltage requirement (default 0.95 pu). Separate from hard battery-action guard.")
    parser.add_argument("--v-max-pu", type=float, default=V_MAX_PU_DEFAULT,
                        help="Predictive MPC upper voltage requirement (default 1.05 pu). Separate from hard battery-action guard.")
    parser.add_argument("--v-margin-pu", type=float, default=V_MARGIN_PU_DEFAULT,
                        help="Safety margin inside the voltage limits (per unit).")
    parser.add_argument("--k-slack", type=float, default=K_SLACK_DEFAULT,
                        help="Penalty K per kW of voltage-limit violation (huge = acts like a hard limit when it can be met).")
    parser.add_argument("--rls-forget", type=float, default=RLS_FORGET_DEFAULT,
                        help="Forgetting factor of the recursive-least-squares slope estimator (1.0 = never forget).")
    parser.add_argument("--bias-decay", type=float, default=BIAS_DECAY_DEFAULT,
                        help="Per-step fade of the last forecast error when judging the voltage limit (0 = ignore).")
    parser.add_argument("--soc-min-pct", type=float, default=SOC_MIN_PCT_DEFAULT,
                        help="Lowest SoC the QP may plan to (hardware end-stop guard band).")
    parser.add_argument("--soc-max-pct", type=float, default=SOC_MAX_PCT_DEFAULT,
                        help="Highest SoC the QP may plan to (hardware end-stop guard band).")
    # >>> USER REQUEST CHANGE 10 START: stronger voltage diagnostics + optional convex support features
    parser.add_argument("--voltage-reference", choices=["minimum", "average"], default="minimum",
                        help="Measured phase voltage used to anchor the phase model. 'minimum' targets the weakest node.")
    parser.add_argument("--peak-reserve", action="store_true",
                        help="OFF by default. Softly reserve high SoC before an extreme forecast feeder peak.")
    parser.add_argument("--peak-reserve-threshold-kw", type=float, default=PEAK_RESERVE_THRESHOLD_KW_DEFAULT,
                        help="Activate reserve only when max forecast feeder net load exceeds this kW value.")
    parser.add_argument("--peak-reserve-target-pct", type=float, default=PEAK_RESERVE_TARGET_PCT_DEFAULT,
                        help="Target battery SoC during the reserve window before the extreme peak.")
    parser.add_argument("--peak-reserve-lead-hours", type=float, default=PEAK_RESERVE_LEAD_HOURS_DEFAULT,
                        help="How many hours before the forecast peak the reserve target should be reached in deadline mode.")
    # >>> V17 FORECAST RESERVE LOCK CHANGE 1 START
    parser.add_argument("--peak-reserve-fill-mode", choices=["deadline", "asap"],
                        default=PEAK_RESERVE_FILL_MODE_DEFAULT,
                        help="Reserve charging strategy. 'deadline' retains the V16 average-rate trajectory. "
                             "'asap' immediately charges toward the reserve target when a qualifying peak enters "
                             "the forecast horizon, subject to the existing voltage-safe charging controller, then "
                             "locks the stored reserve against economic discharge until it is actually needed.")
    # <<< V17 FORECAST RESERVE LOCK CHANGE 1 END
    parser.add_argument("--peak-reserve-penalty", type=float, default=PEAK_RESERVE_PENALTY_DEFAULT,
                        help="Soft-constraint penalty per kWh below the peak energy-management trajectory.")
    # >>> V8 ROBUST PRECHARGE CHANGE 4 START
    parser.add_argument("--peak-reserve-forecast-safety-factor", type=float,
                        default=PEAK_RESERVE_FORECAST_SAFETY_FACTOR_DEFAULT,
                        help="Multiply forecast peak magnitude only for reserve triggering (default 1.35). "
                             "This does NOT prescribe discharge power or energy during the event.")
    parser.add_argument("--reserve-release-v-pu", type=float,
                        default=PEAK_RESERVE_EVENT_RELEASE_PU_DEFAULT,
                        help="Measured weakest phase voltage that enters ride-through support (default 0.958 pu). "
                             "This is intentionally below the 0.97 no-charge guard so harmless pre-peak dips do not waste energy.")
    parser.add_argument("--reserve-recover-v-pu", type=float,
                        default=PEAK_RESERVE_EVENT_RECOVER_PU_DEFAULT,
                        help="Voltage required before a supported phase may leave ride-through mode after its hold time (default 0.985 pu).")
    parser.add_argument("--reserve-event-hold-steps", type=int,
                        default=PEAK_RESERVE_EVENT_HOLD_STEPS_DEFAULT,
                        help="Minimum number of MPC steps that ride-through remains latched after triggering (default 4).")
    # >>> V9 PHASE EVENT / PRECHARGE FIX 3 START
    parser.add_argument("--reserve-pause-hold-steps", type=int,
                        default=PEAK_RESERVE_PAUSE_HOLD_STEPS_DEFAULT,
                        help="Extra pre-charge pause dwell beyond the hard 0.97/0.978 guard hysteresis (default 0).")
    # <<< V9 PHASE EVENT / PRECHARGE FIX 3 END
    # Backward-compatible v7 options: accepted but intentionally ignored in v8.
    parser.add_argument("--peak-reserve-peak-floor-pct", type=float, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--peak-reserve-post-hours", type=float, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--peak-reserve-post-floor-pct", type=float, default=None, help=argparse.SUPPRESS)
    # <<< V8 ROBUST PRECHARGE CHANGE 4 END
    parser.add_argument("--local-voltage-support", action="store_true",
                        help="OFF by default. Bias the first MPC action toward discharge at locally low-voltage nodes.")
    parser.add_argument("--local-voltage-support-start-pu", type=float,
                        default=LOCAL_VOLTAGE_SUPPORT_START_PU_DEFAULT,
                        help="Local-voltage support starts below this per-unit voltage.")
    parser.add_argument("--local-voltage-support-penalty", type=float,
                        default=LOCAL_VOLTAGE_SUPPORT_PENALTY_DEFAULT,
                        help="Strength of the optional local first-action voltage support term.")
    # <<< USER REQUEST CHANGE 10 END
    # <<< VOLTAGE CHANGE 2a END
    # >>> USER REQUEST CHANGE 9 START: explicit forecast modes; live is default, perfect forecast is a one-flag override
    forecast_mode = parser.add_mutually_exclusive_group()
    forecast_mode.add_argument("--perfect-forecast", action="store_true",
                               help="Use each node's actual future load/PV as the 48-step MPC forecast (testing/reference mode).")
    forecast_mode.add_argument("--static-forecast", action="store_true",
                               help="Use the static average-household forecast CSV instead of live model forecasts.")
    parser.add_argument("--static-forecast-file", default="Code_and_Data/average_household_forecasts.csv",
                        help="Static per-customer forecast CSV used with --static-forecast.")
    parser.add_argument("--forecast-scale", type=float, default=2.0,
                        help="Multiplier on live/static per-household load and PV forecasts. Ignored by --perfect-forecast.")
    # <<< USER REQUEST CHANGE 9 END
    parser.add_argument("--forecast-refresh", type=int, default=1,
                        help="Re-run the load/PV models every N MPC steps (default 1 = every step).")
    parser.add_argument("--load-model", default="finalized_load_rf_model_v3.pkl")
    parser.add_argument("--pv-model", default="finalized_pv_rf_model_v3.pkl")
    parser.add_argument("--bom-max-temp", default="BOM_Data/IDCJAC0010_066137_1800_daily_max_temp/IDCJAC0010_066137_1800_Data.csv")
    parser.add_argument("--bom-min-temp", default="BOM_Data/IDCJAC0011_066137_1800_daily_min_temp/IDCJAC0011_066137_1800_Data.csv")
    parser.add_argument("--bom-solar", default="BOM_Data/IDCJAC0016_066137_1800_daily_solar_exposure/IDCJAC0016_066137_1800_Data.csv")
    # <<< LIVE FORECAST CHANGE 2 END
    # >>> VHIL CHANGE 2 START: choose how the controller talks to the HIL <<<
    parser.add_argument("--backend", choices=["modbus", "api"], default="modbus",
                        help="modbus = Modbus TCP (real HIL, default) | api = Typhoon Python API (Virtual HIL).")
    parser.add_argument("--api-control-signal", default="Local-Remote Control",
                        help="SCADA input that selects Modbus vs SCADA control in the model. In Monash_13NodeFeeder "
                             "0 = SCADA inputs (what the API writes), 1 = Modbus. Pass '' to leave it alone.")
    # >>> USER REQUEST CHANGE 11 START: API control value only applies when --backend api, so default to local/API control
    parser.add_argument("--api-control-value", type=float, default=0.0,
                        help="Value written to --api-control-signal when --backend api (default 0 = SCADA/API control).")
    # <<< USER REQUEST CHANGE 11 END
    parser.add_argument("--api-soc-signal", default=None,
                        help="Optional analog signal giving node-646 battery SoC in percent. If omitted, a Python "
                             "battery emulation provides the 'measured' SoC.")
    # <<< VHIL CHANGE 2 END
    args = parser.parse_args()

    # >>> V19 BATTERY EMULATOR CHANGE 5 START: resolve and validate selected implementation
    requested_battery_emulator = args.battery_emulator
    effective_battery_emulator = (
        "none" if (args.no_soc_feedback or args.dry_run) else requested_battery_emulator
    )
    if args.no_soc_feedback and requested_battery_emulator != "none":
        print(f"  NOTE: --no-soc-feedback overrides --battery-emulator {requested_battery_emulator}; using NONE mode.")

    if args.hardware_min_hold_seconds <= 0 or args.hardware_max_hold_seconds <= 0 \
            or args.hardware_idle_hold_seconds <= 0:
        raise ValueError("Hardware-emulator hold durations must all be > 0")
    if args.hardware_min_hold_seconds > args.hardware_max_hold_seconds:
        raise ValueError("--hardware-min-hold-seconds cannot exceed --hardware-max-hold-seconds")
    if not 1 <= args.hardware_preferred_code <= 255:
        raise ValueError("--hardware-preferred-code must be in 1..255")
    if args.hardware_command_refresh_seconds < 0 or args.hardware_hold_progress_seconds < 0:
        raise ValueError("Hardware refresh/progress intervals must be >= 0")
    if args.hardware_emu_wait < 0 or args.hardware_emu_stale_limit <= 0:
        raise ValueError("Hardware emulator wait must be >= 0 and stale limit must be > 0")
    if args.hardware_emu_charge_rate <= 0 or args.hardware_emu_discharge_rate <= 0:
        raise ValueError("Hardware emulator calibrated charge/discharge rates must be > 0")
    if effective_battery_emulator == "hardware" and args.backend != "modbus":
        raise ValueError("--battery-emulator hardware currently requires --backend modbus.")
    if effective_battery_emulator == "hardware" and args.no_wait:
        raise ValueError("--no-wait cannot be used with live HARDWARE emulator mode because the real hold time is part of the SoC scaling.")
    # <<< V19 BATTERY EMULATOR CHANGE 5 END

    # Connect
    conn = None
    # >>> VHIL CHANGE 3a START: API backend connection (the Modbus branch below is unchanged) <<<
    if args.backend == "api":
        conn = TyphoonApiConnection(args.dry_run, (args.api_control_signal or None), args.api_control_value,
                                    args.api_soc_signal, args.verbose)
        print("\nConnecting to the running Typhoon HIL model through the Python API ...")
        conn.connect()
        print("  Connected.")
    # <<< VHIL CHANGE 3a END
    elif not args.dry_run:
        conn = ModbusConnection(args.ip, args.port)
        print(f"\nConnecting to HIL Modbus server at {args.ip}:{args.port} ...")
        conn.connect()
        print("  Connected.")

    # >>> V19 BATTERY EMULATOR CHANGE 6 START: optional physical emulator connection
    hardware_emu = None
    if effective_battery_emulator == "hardware":
        print(f"Connecting to physical battery emulator at {args.hardware_emu_port} ...")
        try:
            hardware_emu = HardwareBatteryEmulator(args.hardware_emu_port)
        except Exception:
            if conn is not None:
                conn.close()
            raise
    # <<< V19 BATTERY EMULATOR CHANGE 6 END

    # >>> USER REQUEST CHANGE 12 START: clean forecast setup; live default, perfect/static optional
    act_path = Path(args.actual)
    if not act_path.exists():
        raise FileNotFoundError(f"Actual CSV not found: {act_path}")

    print(f"\nLoading actual CSV: {act_path.name}")
    node_data, total_load_act, total_pv_act, dates = load_actual_feeder_csv(act_path)
    n_days_act = len(dates)

    playback_days = min(args.playback_days, n_days_act)
    total_steps = playback_days * N_STEPS
    print(f"  Actual days available   : {n_days_act}")
    print(f"  Playback days used      : {playback_days}  ({total_steps} steps)")

    if args.battery_capacity_per_customer_kwh <= 0:
        raise ValueError("--battery-capacity-per-customer-kwh must be > 0")
    if args.battery_power_per_customer_kw < 0:
        raise ValueError("--battery-power-per-customer-kw must be >= 0")
    if not (0.0 <= args.initial_soc_pct <= 100.0):
        raise ValueError("--initial-soc-pct must lie in [0, 100]")
    if not (0.0 <= args.soc_min_pct < args.soc_max_pct <= 100.0):
        raise ValueError("Require 0 <= --soc-min-pct < --soc-max-pct <= 100")
    if not (0.0 < args.v_min_pu < args.v_max_pu):
        raise ValueError("Require 0 < --v-min-pu < --v-max-pu")
    if args.v_margin_pu < 0 or (args.v_min_pu + args.v_margin_pu) >= (args.v_max_pu - args.v_margin_pu):
        raise ValueError("--v-margin-pu leaves no usable voltage band")
    # >>> CHATTER/STABILITY CHANGE 6 START
    if not (0.0 < args.guard_v_min_pu < args.guard_v_max_pu):
        raise ValueError("Require 0 < --guard-v-min-pu < --guard-v-max-pu")
    if args.directional_guard_engage_margin_pu < 0 or args.directional_guard_release_margin_pu < 0:
        raise ValueError("directional-guard margins must be >= 0")
    if args.directional_guard_release_margin_pu <= args.directional_guard_engage_margin_pu:
        raise ValueError("--directional-guard-release-margin-pu must be greater than --directional-guard-engage-margin-pu")
    if args.directional_guard_hold_steps < 0:
        raise ValueError("--directional-guard-hold-steps must be >= 0")
    if args.battery_smoothing_weight < 0:
        raise ValueError("--battery-smoothing-weight must be >= 0")
    # >>> V5 NODAL VOLTAGE/RAMP CHANGE 6 START
    if args.max_charge_ramp_per_customer_kw < 0:
        raise ValueError("--max-charge-ramp-per-customer-kw must be >= 0")
    if args.phase_support_discharge_buffer_kw < 0:
        raise ValueError("--phase-support-discharge-buffer-kw must be >= 0")
    # >>> V11 VOLTAGE HOLD CHANGE 3 START
    if not (args.v_min_pu < args.phase_support_voltage_target_pu <= args.guard_v_min_pu):
        raise ValueError("--phase-support-voltage-target-pu must be > --v-min-pu and <= --guard-v-min-pu")
    # >>> V13 CONTINUOUS PRECHARGE CHANGE 5 START
    if not (args.guard_v_min_pu < args.precharge_voltage_target_pu < args.guard_v_max_pu):
        raise ValueError("--precharge-voltage-target-pu must be above --guard-v-min-pu and below --guard-v-max-pu")
    if not (0.0 < args.precharge_voltage_feedback_gain <= 2.0):
        raise ValueError("--precharge-voltage-feedback-gain must lie in (0, 2]")
    if not (0.0 < args.precharge_rho_min_mult <= args.precharge_rho_max_mult):
        raise ValueError("Require 0 < --precharge-rho-min-mult <= --precharge-rho-max-mult")
    # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 7 START
    if not (0.0 < args.support_voltage_feedback_gain <= 3.0):
        raise ValueError("--support-voltage-feedback-gain must lie in (0, 3]")
    if args.support_max_delta_per_customer_kw < 0:
        raise ValueError("--support-max-delta-per-customer-kw must be >= 0")
    if not (0.0 < args.support_rho_min_mult <= args.support_rho_max_mult):
        raise ValueError("Require 0 < --support-rho-min-mult <= --support-rho-max-mult")
    if args.support_min_grid_import_per_customer_kw < 0:
        raise ValueError("--support-min-grid-import-per-customer-kw must be >= 0")
    if args.support_arm_hours < 0 or args.support_arm_load_kw < 0:
        raise ValueError("support arm hours/load must be >= 0")
    # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 3 START
    if args.security_event_enter_load_kw < 0 or args.security_event_exit_load_kw < 0:
        raise ValueError("security event load thresholds must be >= 0")
    if not (args.v_min_pu < args.security_event_enter_voltage_pu < 1.0):
        raise ValueError("--security-event-enter-voltage-pu must be > --v-min-pu and < 1.0 pu")
    if args.security_event_enter_voltage_pu < args.guard_v_min_pu:
        raise ValueError("--security-event-enter-voltage-pu should be >= --guard-v-min-pu")
    if args.security_event_exit_load_kw >= args.security_event_enter_load_kw:
        raise ValueError("--security-event-exit-load-kw must be lower than --security-event-enter-load-kw")
    if args.security_event_exit_steps < 0:
        raise ValueError("--security-event-exit-steps must be >= 0")
    if args.security_support_fixed_rho_mult <= 0 or args.security_precharge_fixed_rho_mult <= 0:
        raise ValueError("security fixed-rho multipliers must be > 0")
    if not (0.0 < args.security_support_gain <= 2.0):
        raise ValueError("--security-support-gain must lie in (0, 2]")
    if not (0.0 < args.security_precharge_gain <= 2.0):
        raise ValueError("--security-precharge-gain must lie in (0, 2]")
    # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 3 END
    # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 7 END
    # <<< V13 CONTINUOUS PRECHARGE CHANGE 5 END
    if args.security_max_charge_per_customer_kw < 0:
        raise ValueError("--security-max-charge-per-customer-kw must be >= 0")
    # <<< V11 VOLTAGE HOLD CHANGE 3 END
    # <<< V5 NODAL VOLTAGE/RAMP CHANGE 6 END
    # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 7 START
    if str(args.secondary_solver).strip().lower() in ("", "none", "off", "false", "0"):
        args.secondary_solver = None
    # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 7 END

    guard_low_engage_pu = args.guard_v_min_pu + args.directional_guard_engage_margin_pu
    guard_low_release_pu = args.guard_v_min_pu + args.directional_guard_release_margin_pu
    guard_high_engage_pu = args.guard_v_max_pu - args.directional_guard_engage_margin_pu
    guard_high_release_pu = args.guard_v_max_pu - args.directional_guard_release_margin_pu
    if not (args.guard_v_min_pu <= guard_low_engage_pu < guard_low_release_pu <
            guard_high_release_pu < guard_high_engage_pu <= args.guard_v_max_pu):
        raise ValueError(
            "Directional-guard thresholds overlap or leave no neutral band. Reduce the guard margins or widen --guard-v-min-pu/--guard-v-max-pu."
        )
    # <<< CHATTER/STABILITY CHANGE 6 END
    if not (0.0 <= args.peak_reserve_target_pct <= 100.0):
        raise ValueError("--peak-reserve-target-pct must lie in [0, 100]")
    if args.peak_reserve_lead_hours < 0:
        raise ValueError("--peak-reserve-lead-hours must be >= 0")
    # >>> V8 ROBUST PRECHARGE CHANGE 5 START
    if args.peak_reserve_forecast_safety_factor < 1.0:
        raise ValueError("--peak-reserve-forecast-safety-factor must be >= 1")
    # >>> V12 SECURITY RIDE-THROUGH CHANGE 3 START
    if not (args.v_min_pu < args.reserve_release_v_pu < args.guard_v_min_pu):
        raise ValueError("Require --v-min-pu < --reserve-release-v-pu < --guard-v-min-pu")
    if not (args.guard_v_min_pu < args.reserve_recover_v_pu < args.guard_v_max_pu):
        raise ValueError("Require --guard-v-min-pu < --reserve-recover-v-pu < --guard-v-max-pu")
    # <<< V12 SECURITY RIDE-THROUGH CHANGE 3 END
    if args.reserve_event_hold_steps < 0:
        raise ValueError("--reserve-event-hold-steps must be >= 0")
    if args.reserve_pause_hold_steps < 0:
        raise ValueError("--reserve-pause-hold-steps must be >= 0")
    # <<< V8 ROBUST PRECHARGE CHANGE 5 END
    if args.peak_reserve_penalty < 0 or args.local_voltage_support_penalty < 0:
        raise ValueError("reserve/support penalties must be >= 0")

    eta_flat = make_eta_array(total_steps + N_STEPS)
    forecast_cache = None
    forecast_load_per_customer = None
    forecast_pv_per_customer = None

    if args.perfect_forecast:
        forecast_mode_name = "PERFECT (actual nodal future load/PV)"
        print("  Forecast mode           : PERFECT forecast")
    elif args.static_forecast:
        forecast_mode_name = f"STATIC ({args.static_forecast_file})"
        static_path = Path(args.static_forecast_file)
        if not static_path.exists():
            raise FileNotFoundError(f"Static forecast CSV not found: {static_path}")
        real_forecast_df = load_real_forecast_data(static_path)
        forecast_load_per_customer = pd.to_numeric(real_forecast_df["Predicted_Average_Load_kW"], errors="raise").to_numpy(dtype=float) * args.forecast_scale
        forecast_pv_per_customer = pd.to_numeric(real_forecast_df["Predicted_Average_PV_Gen_kW"], errors="raise").to_numpy(dtype=float) * args.forecast_scale
        forecast_load_per_customer = pad_to_length(forecast_load_per_customer, total_steps + N_STEPS)
        forecast_pv_per_customer = pad_to_length(forecast_pv_per_customer, total_steps + N_STEPS)
        print(f"  Forecast mode           : STATIC, scale x{args.forecast_scale:g}")
    else:
        forecast_mode_name = "LIVE ML"
        playback_time_cols = list(pd.read_csv(act_path, nrows=0).columns[5:53])
        weather = WeatherTable(args.bom_max_temp, args.bom_min_temp, args.bom_solar)
        forecaster = LiveForecaster(args.load_model, args.pv_model, weather,
                                    first_date=parse_date(dates[0]), time_col_labels=playback_time_cols)
        forecast_cache = WindowForecastCache(forecaster, n_steps=N_STEPS, refresh_every=args.forecast_refresh)
        print(f"  Forecast mode           : LIVE ML, scale x{args.forecast_scale:g}, refresh every {args.forecast_refresh} step(s)")
        print(f"  First playback date     : {parse_date(dates[0]).date()}, first slot {playback_time_cols[0]}")
        _days = pd.DatetimeIndex([parse_date(d) for d in dates[:playback_days]])
        _wx = weather.for_dates(_days).copy()
        _wx.insert(0, "Date", _days.strftime("%a %d-%b-%Y"))
        print("  Weather used by live forecast:")
        print("    " + _wx.round(1).to_string(index=False).replace("\n", "\n    "))
    # <<< USER REQUEST CHANGE 12 END

    # Banner
    print("=" * 78)
    print("ECE4191 Module 3  |  Project V19 Switchable Battery Emulator - Extension 1,3,5")
    print("=" * 78)
    # >>> VHIL CHANGE 3b START <<<
    print(f"  HIL target      : " + ("Typhoon Python API (SCADA inputs)" if args.backend == "api" else f"{args.ip}:{args.port}"))
    # <<< VHIL CHANGE 3b END
    print(f"  Forecast mode   : {forecast_mode_name}")
    print(f"  Actual CSV      : {act_path.name}  (per-node HIL playback)")
    print(f"  Battery/customer: {args.battery_capacity_per_customer_kwh:g} kWh, "
          f"+/-{args.battery_power_per_customer_kw:g} kW")
    print(f"  Initial SoC     : {args.initial_soc_pct:.1f}%")
    print(f"  Battery emulator: {effective_battery_emulator.upper()}" +
          (" (requested mode overridden by --no-soc-feedback/--dry-run)"
           if effective_battery_emulator != requested_battery_emulator else ""))
    if effective_battery_emulator == "hil":
        print("  SoC feedback    : HIL internal/API Node-646 battery measurement")
    elif effective_battery_emulator == "hardware":
        print(f"  SoC feedback    : physical serial emulator @ {args.hardware_emu_port}")
        print(f"  Hardware timing : active {args.hardware_min_hold_seconds:g}-{args.hardware_max_hold_seconds:g} s, "
              f"idle {args.hardware_idle_hold_seconds:g} s, preferred command {args.hardware_preferred_code}/255")
        print("  HIL SoC logging : ON for independent comparison; it does NOT seed the MPC in HARDWARE mode")
    else:
        print("  SoC feedback    : NONE; Node-646 MPC state is propagated from its own prediction")
    print(f"  Objective weight: w = {args.weight}")
    # >>> VOLTAGE CHANGE 2b START <<<
    if args.no_voltage_constraint:
        print("  Voltage limits  : predictive caps OFF")
    else:
        print(f"  Voltage limits  : {args.v_min_pu:.3f}-{args.v_max_pu:.3f} pu (margin {args.v_margin_pu:.3f}), "
              f"soft with K = {args.k_slack:g}, mode={args.voltage_cap_mode}, RLS forgetting {args.rls_forget}")
        if args.voltage_cap_mode in ("phase", "both"):
            print(f"  Phase V model   : reference={args.voltage_reference}")
    print(f"  SoC window      : {args.soc_min_pct:.1f}-{args.soc_max_pct:.1f} %")
    # >>> CHATTER/STABILITY CHANGE 7 START
    if args.no_directional_voltage_guard:
        print("  Direction guard : OFF")
    else:
        print(f"  Direction guard : ON, HARD action band {args.guard_v_min_pu:.3f}-{args.guard_v_max_pu:.3f} pu; "
              f"engage/release {guard_low_engage_pu:.3f}/{guard_low_release_pu:.3f} low, "
              f"{guard_high_engage_pu:.3f}/{guard_high_release_pu:.3f} high; hold {args.directional_guard_hold_steps} step(s)")
    print(f"  Batt smoothing  : K = {args.battery_smoothing_weight:g} "
          f"(first-action delta-P penalty; 0 = off)")
    # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 8 START
    print(f"  Solver path     : {args.solver}" + (f" -> {args.secondary_solver}" if args.secondary_solver else " (no backup)"))
    print("  Peak guard      : stale no-discharge release override ON"
          if not args.no_peak_guard_release_override else
          "  Peak guard      : stale no-discharge release override OFF")
    # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 8 END
    # >>> V5 NODAL VOLTAGE/RAMP CHANGE 7 START
    print(f"  Charge ramp     : {args.max_charge_ramp_per_customer_kw:g} kW/customer/step "
          f"max additional charging (0 = off; discharge remains unrestricted)")
    # <<< V5 NODAL VOLTAGE/RAMP CHANGE 7 END
    # <<< CHATTER/STABILITY CHANGE 7 END
    if args.peak_reserve:
        print(f"  Peak reserve    : ON, robust PRE-CHARGE -> {args.peak_reserve_target_pct:.1f}% by "
              f"-{args.peak_reserve_lead_hours:g} h; trigger uses forecast x{args.peak_reserve_forecast_safety_factor:g} "
              f">= {args.peak_reserve_threshold_kw:g} kW")
        # >>> V17 FORECAST RESERVE LOCK CHANGE 2 START
        if args.peak_reserve_fill_mode == "asap":
            print("  Reserve fill    : ASAP - fill immediately when the qualifying peak enters the horizon; "
                  "hold at target until ride-through or forecast clear")
        else:
            print("  Reserve fill    : DEADLINE - V16 average-rate reserve preparation")
        # <<< V17 FORECAST RESERVE LOCK CHANGE 2 END
        print(f"  Reserve V logic : hard no-charge at {args.guard_v_min_pu:.3f} pu; "
              f"ride-through starts <= {args.reserve_release_v_pu:.3f} pu; recover >= {args.reserve_recover_v_pu:.3f} pu")
    else:
        print("  Peak reserve    : OFF")
    # >>> V10 HARD PHASE DISPATCH 4 START
    print(f"  Hard phase step : {'OFF' if args.no_hard_phase_first_action else 'ON'}; "
          f"support overshoot allowance {args.phase_support_discharge_buffer_kw:g} kW/phase")
    # >>> V11 VOLTAGE HOLD CHANGE 4 START
    print(f"  Voltage hold    : continuous pre-charge target {args.precharge_voltage_target_pu:.3f} pu "
          f"(feedback gain {args.precharge_voltage_feedback_gain:g}); "
          f"support trigger/target {args.reserve_release_v_pu:.3f}/{args.phase_support_voltage_target_pu:.3f} pu; "
          f"security charge <= {args.security_max_charge_per_customer_kw:g} kW/customer")
    # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 8 START
    # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 4 START
    print(f"  V16 supervisor  : ride-through entry requires actual feeder >= {args.security_event_enter_load_kw:g} kW "
          f"and weak phase <= {args.security_event_enter_voltage_pu:.3f} pu, "
          f"or an actual V < {args.v_min_pu:.3f} pu emergency")
    print(f"  V15 ride exit   : feeder <= {args.security_event_exit_load_kw:g} kW and V >= {args.guard_v_min_pu:.3f} pu "
          f"for {args.security_event_exit_steps} consecutive step(s)")
    print(f"  V15 voltage loop: target {args.phase_support_voltage_target_pu:.3f} pu, fixed rho x"
          f"{args.security_support_fixed_rho_mult:g}, gain {args.security_support_gain:g}")
    # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 4 END
    # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 8 END
    print("  Charge sharing  : SoC-deficit balanced per node during security preparation")
    # <<< V11 VOLTAGE HOLD CHANGE 4 END
    # <<< V10 HARD PHASE DISPATCH 4 END
    print("  Local V support : " + ("ON" if args.local_voltage_support else "OFF"))
    # <<< VOLTAGE CHANGE 2b END
    print(f"  Playback period : {playback_days} day(s), {total_steps} steps")
    if args.dry_run:
        print("  *** DRY-RUN MODE -- no Modbus writes will occur ***")
    print("=" * 78)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        # >>> VHIL CHANGE 3c START: separate checklist for the API backend <<<
        if args.backend == "api":
            print("  1. Model loaded on the Virtual HIL device and the simulation is RUNNING.")
            print("  2. The model has the SCADA inputs / voltage probes listed in the setup notes.")
            print("  3. For Monash_13NodeFeeder the script sets 'Local-Remote Control' = 0 itself (SCADA inputs in control).")
        else:
        # <<< VHIL CHANGE 3c END
            print("  1. Model compiled and running in Typhoon HIL Control Center.")
            print("  2. SCADA open; Control Type = REMOTE CONTROL.")
            print("  3. BusSplitMap holding registers 2000-2063 enabled.")
            print("  4. Voltage/active-power Signal Analyzer export ready (see Appendix B).")
            if effective_battery_emulator == "hardware":
                print("  5. Physical battery emulator is powered/reset to the desired starting SoC.")
                print("  6. Emulator serial USB and analogue HIL connections are installed as for the E3 hardware test.")
        input("\nPress Enter to start playback ...\n")

    # Initial clear
    print("\nClearing all registers ...")
    clear_all_registers(conn, args.dry_run)

    settle = 12 #TODO: CHANGE BACK TO 12
    if args.no_wait or args.dry_run:
        print("Settle delay skipped.")
    else:
        print(f"Waiting {settle} s for model to settle ...")
        for i in range(settle, 0, -1):
            print(f"  Starting in {i}s ...", end="\r")
            time.sleep(1)
        print(" " * 30)
    print("Ready.\n")

    # >>> V19 BATTERY EMULATOR CHANGE 7 START: initialise selected Node-646 feedback source
    # HIL SoC is read in HIL mode and also in HARDWARE mode as an independent comparison.
    hil_log_enabled = effective_battery_emulator in ("hil", "hardware") and not args.dry_run
    cil_capacity_kwh = N_CUSTOMERS[CIL_NODE] * args.battery_capacity_per_customer_kwh

    if args.backend == "api":
        soc_logger = ApiSocLogger(conn, hil_log_enabled, init_soc_pct=args.initial_soc_pct,
                                  cil_capacity_kwh=cil_capacity_kwh)
    else:
        soc_logger = SocLogger(conn, hil_log_enabled)
    soc_logger.start()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False
    soc_pred = {nd: (args.initial_soc_pct / 100.0) * N_CUSTOMERS[nd] * args.battery_capacity_per_customer_kwh
                for nd in NODE_MAP}

    # This variable is the SELECTED feedback state used by the existing MPC/precharge logic.
    # It can come from the HIL, the physical emulator, or (NONE mode) the MPC prediction.
    soc_measured_646_CIL_kwh = soc_pred[CIL_NODE]
    cil_soc_feedback_active = False
    initial_soc_measured_pct = None       # HIL/API comparison measurement
    initial_soc_hardware_pct = None       # physical hardware-emulator measurement

    if hil_log_enabled:
        initial_soc_measured_pct = soc_logger.log_step()

    if effective_battery_emulator == "hardware":
        raw0, initial_soc_hardware_pct, age0, fresh0 = hardware_emu.read_latest(
            max(2.0, args.hardware_emu_wait)
        )
        if initial_soc_hardware_pct is None:
            raise RuntimeError("No physical battery-emulator SoC received; cannot start HARDWARE feedback mode.")
        if age0 is not None and age0 > args.hardware_emu_stale_limit:
            raise RuntimeError(f"Initial physical battery-emulator SoC is stale ({age0:.2f} s).")
        soc_measured_646_CIL_kwh = float(initial_soc_hardware_pct) / 100.0 * cil_capacity_kwh
        soc_pred[CIL_NODE] = soc_measured_646_CIL_kwh
        cil_soc_feedback_active = True
        print(f"  Initial Node 646 HARDWARE SoC used by MPC: {float(initial_soc_hardware_pct):.3f}% "
              f"(raw {raw0:05d})")
        if initial_soc_measured_pct is not None:
            print(f"  Initial Node 646 HIL SoC logged for comparison: {float(initial_soc_measured_pct):.3f}%")

    elif effective_battery_emulator == "hil":
        if initial_soc_measured_pct is not None:
            soc_measured_646_CIL_kwh = float(initial_soc_measured_pct) / 100.0 * cil_capacity_kwh
            soc_pred[CIL_NODE] = soc_measured_646_CIL_kwh
            cil_soc_feedback_active = True
            print(f"  Initial Node 646 HIL SoC used by MPC: {float(initial_soc_measured_pct):.3f}%")
        else:
            print("  WARNING: initial HIL Node-646 SoC unavailable; MPC prediction will be used until a valid read returns.")

    else:
        print("  Node 646 SoC feedback: NONE; MPC-predicted SoC will be used.")

    if effective_battery_emulator == "hil" and args.backend == "modbus":
        print(f"  HIL battery mode       : INTERNAL Node-646 SoC feedback; controller assumes "
              f"{args.battery_capacity_per_customer_kwh:g} kWh/customer. Ensure the HIL internal battery "
              "capacity is configured to the same value.")
    # <<< V19 BATTERY EMULATOR CHANGE 7 END

    pbat_nodes = {}
    batt_traj = {}
    grid_traj = {}
    soc_traj = {}
    status = {}
    obj_val = {}
    p_bat_node = {}
    soc_pred_next = {}
    grid_forecast_kw = {}
    soc_pred_pct = {}
    load_act_i = {}
    pv_act_i = {}
    grid_act_i = {}
    sched_rows_node = {}
    p_load_win = {}
    p_pv_win = {}
    sched_rows_all_nodes = {}
    node_voltage = {nd: nominal_voltage_for_node(nd) for nd in NODE_MAP}
    node_v_valid = {nd: False for nd in NODE_MAP}
    voltage_fallback_warned = False

    volt_on = not args.no_voltage_constraint
    hw = {nd: get_hardware_limits(nd, args.soc_min_pct, args.soc_max_pct,
                                  args.battery_capacity_per_customer_kwh,
                                  args.battery_power_per_customer_kw) for nd in NODE_MAP}

    print("Hard nodal battery limits used by the MPC:")
    for nd in NODE_MAP:
        h = hw[nd]
        req = h["requested_power_kw"]
        clipped = abs(h["p_hi_kw"] - req) > 1e-6 or abs(h["p_lo_kw"] + req) > 1e-6
        flag = "   <-- limited by HIL schematic range" if clipped else ""
        print(f"  {nd}: {h['p_lo_kw']:9.1f} .. {h['p_hi_kw']:8.1f} kW   cap {h['cap_kwh']:10.1f} kWh   "
              f"SoC {h['soc_lo_kwh']:10.1f} .. {h['soc_hi_kwh']:10.1f} kWh{flag}")

    estimators = {ph: PhaseVoltageEstimator(RHO0_V_PER_KW[ph], forget=args.rls_forget) for ph in PHASES}
    phase_bias_kw = {ph: 0.0 for ph in PHASES}

    # >>> V5 NODAL VOLTAGE/RAMP CHANGE 8 START
    node_estimators = {
        nd: NodeVoltageEstimator(node_rho0_v_per_kw(nd), forget=args.rls_forget, min_dp_kw=2.0)
        for nd in NODE_MAP
    }
    node_bias_kw = {nd: 0.0 for nd in NODE_MAP}
    node_caps = None
    node_slack_steps = {nd: 0 for nd in NODE_MAP}
    node_model_miss_steps = {nd: 0 for nd in NODE_MAP}
    charge_ramp_kw = {nd: args.max_charge_ramp_per_customer_kw * N_CUSTOMERS[nd] for nd in NODE_MAP}
    # <<< V5 NODAL VOLTAGE/RAMP CHANGE 8 END

    eta_win_nodes = {}
    volt_log_cols = {}
    phase_caps = None
    slack_steps = {ph: 0 for ph in PHASES}
    measured_violation_steps = {ph: 0 for ph in PHASES}
    model_miss_steps = {ph: 0 for ph in PHASES}
    phase_pu_range = {ph: [float("inf"), float("-inf")] for ph in PHASES}

    # >>> CHATTER/STABILITY CHANGE 8 START: persistent guard + previous applied command state
    directional_guard_state = {nd: {"mode": None, "hold": 0} for nd in NODE_MAP}
    last_applied_batt_kw = {nd: 0.0 for nd in NODE_MAP}
    # >>> V8 ROBUST PRECHARGE CHANGE 6 START
    # >>> V9 PHASE EVENT / PRECHARGE FIX 4 START
    # >>> V13 CONTINUOUS PRECHARGE CHANGE 6 START
    # Phase state is now intentionally simple: None=prepare/hold, support=real
    # ride-through. V13 no longer latches a phase-wide precharge pause; charging is
    # continuously trimmed from measured voltage instead.
    reserve_voltage_event_state = {ph: {"mode": None, "hold": 0} for ph in PHASES}
    # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 5 START
    security_ride_state = {ph: {"active": False, "recover_count": 0} for ph in PHASES}
    last_phase_baseline_kw = {ph: None for ph in PHASES}
    # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 5 END
    # <<< V13 CONTINUOUS PRECHARGE CHANGE 6 END
    # <<< V9 PHASE EVENT / PRECHARGE FIX 4 END
    # <<< V8 ROBUST PRECHARGE CHANGE 6 END
    # <<< CHATTER/STABILITY CHANGE 8 END

    voltage_fallback_warned = refresh_voltage_snapshot(soc_logger, args.dry_run, node_voltage, node_v_valid,
                                                       voltage_fallback_warned)
    if volt_on and not args.dry_run:
        if args.voltage_cap_mode in ("phase", "both"):
            for ph in PHASES:
                control_pu, min_pu, min_node, avg_pu = phase_voltage_measurement(
                    ph, node_voltage, node_v_valid, args.voltage_reference)
                if control_pu is not None:
                    estimators[ph].update(control_pu * NOMINAL_VOLTAGE, 0.0)
        # >>> V5 NODAL VOLTAGE/RAMP CHANGE 9 START
        if args.voltage_cap_mode in ("nodal", "both"):
            for nd in NODE_MAP:
                if node_v_valid.get(nd, False) and hw[nd]["cap_kwh"] > 0:
                    node_estimators[nd].update(node_voltage[nd], 0.0)
        # <<< V5 NODAL VOLTAGE/RAMP CHANGE 9 END
        print(f"  Voltage model initialised from the settled HIL voltages (mode={args.voltage_cap_mode}).")
    elif volt_on and args.dry_run:
        print("NOTE: --dry-run has no voltage measurements, so voltage caps stay inactive.")
    # <<< USER REQUEST CHANGE 14 END

    if args.verbose or args.progress_every > 0:
        print(_HDR)
        print("-" * len(_HDR))

    try:
        for i in range(total_steps):
            t0 = time.time()
            step = i + 1
            day_num = (i // N_STEPS) + 1
            k = (i % N_STEPS) + 1

            p_bat_total = 0.0

            # >>> USER REQUEST CHANGE 15 START: build exactly one 48-step nodal forecast window for each node
            fc_load_pc_win = None
            fc_pv_pc_win = None
            if forecast_cache is not None:
                fc_load_pc_win, fc_pv_pc_win = forecast_cache.window(i)
                fc_load_pc_win = np.asarray(fc_load_pc_win, dtype=float).reshape(-1) * args.forecast_scale
                fc_pv_pc_win = np.asarray(fc_pv_pc_win, dtype=float).reshape(-1) * args.forecast_scale
                if len(fc_load_pc_win) != N_STEPS or len(fc_pv_pc_win) != N_STEPS:
                    raise ValueError(f"Live forecast must return exactly {N_STEPS} steps; "
                                     f"got load={len(fc_load_pc_win)}, pv={len(fc_pv_pc_win)}")

            for node in NODE_MAP:
                if args.perfect_forecast:
                    p_load_win[node] = fixed_horizon_window(node_data[node]["load_kw"], i)
                    p_pv_win[node] = fixed_horizon_window(node_data[node]["pv_kw"], i)
                elif args.static_forecast:
                    p_load_win[node] = fixed_horizon_window(forecast_load_per_customer * N_CUSTOMERS[node], i)
                    p_pv_win[node] = fixed_horizon_window(forecast_pv_per_customer * N_CUSTOMERS[node], i)
                else:
                    p_load_win[node] = fc_load_pc_win * N_CUSTOMERS[node]
                    p_pv_win[node] = fc_pv_pc_win * N_CUSTOMERS[node]
                eta_win_nodes[node] = fixed_horizon_window(eta_flat, i)
            eta_win = eta_win_nodes[CIL_NODE]
            # <<< USER REQUEST CHANGE 15 END

            # >>> V5 NODAL VOLTAGE/RAMP CHANGE 10 START: predictive voltage caps
            # Default architecture is now NODE-level V->local-grid-power caps inside the same JOINT MPC.
            # The older phase-total caps are retained as an optional comparison mode.
            phase_caps = None
            node_caps = None
            if volt_on:
                if args.voltage_cap_mode in ("phase", "both"):
                    v_lo_equiv = (args.v_min_pu + args.v_margin_pu) * NOMINAL_VOLTAGE
                    v_hi_equiv = (args.v_max_pu - args.v_margin_pu) * NOMINAL_VOLTAGE
                    phase_caps = {}
                    for ph in PHASES:
                        c = estimators[ph].caps(N_STEPS, v_lo_equiv, v_hi_equiv,
                                                phase_bias_kw[ph], args.bias_decay)
                        if c is not None:
                            phase_caps[ph] = c

                if args.voltage_cap_mode in ("nodal", "both"):
                    node_caps = {}
                    for nd in NODE_MAP:
                        # A local cap is only useful where this script actually controls a battery.
                        if hw[nd]["cap_kwh"] <= 0:
                            continue
                        v_nom = nominal_voltage_for_node(nd)
                        v_lo = (args.v_min_pu + args.v_margin_pu) * v_nom
                        v_hi = (args.v_max_pu - args.v_margin_pu) * v_nom
                        c = node_estimators[nd].caps(
                            N_STEPS, v_lo, v_hi, node_bias_kw[nd], args.bias_decay)
                        if c is not None:
                            node_caps[nd] = c
            # <<< V5 NODAL VOLTAGE/RAMP CHANGE 10 END

            # >>> V11 VOLTAGE HOLD CHANGE 5 START
            # Separate current-step caps from the soft horizon cap.  The soft MPC still
            # plans around 0.955 pu.  For the applied action, charging is limited by a
            # 0.970-pu cap while load-event discharge targets 0.960 pu.
            phase_precharge_caps = {}
            phase_support_caps = {}
            if volt_on and not args.no_hard_phase_first_action:
                pre_v_lo = args.precharge_voltage_target_pu * NOMINAL_VOLTAGE
                sup_v_lo = args.phase_support_voltage_target_pu * NOMINAL_VOLTAGE
                hard_v_hi = args.guard_v_max_pu * NOMINAL_VOLTAGE
                for ph in PHASES:
                    c_pre = estimators[ph].caps(N_STEPS, pre_v_lo, hard_v_hi,
                                                phase_bias_kw[ph], args.bias_decay)
                    c_sup = estimators[ph].caps(N_STEPS, sup_v_lo, hard_v_hi,
                                                phase_bias_kw[ph], args.bias_decay)
                    if c_pre is not None:
                        phase_precharge_caps[ph] = c_pre
                    if c_sup is not None:
                        phase_support_caps[ph] = c_sup
            # <<< V11 VOLTAGE HOLD CHANGE 5 END

            # >>> V8 ROBUST PRECHARGE CHANGE 7 START
            # Robust PREPARATION, measurement-driven PROTECTION. The live forecast is
            # allowed to underestimate peak magnitude: we only use its timing plus a safety
            # factor to decide whether a high-SoC preparation should be active. Discharge
            # during the event is released by ACTUAL measured phase voltage, not by forecast.
            forecast_total_net_kw = np.zeros(N_STEPS, dtype=float)
            for nd in NODE_MAP:
                forecast_total_net_kw += p_load_win[nd] - p_pv_win[nd]
            forecast_peak_index = int(np.argmax(forecast_total_net_kw))
            forecast_peak_kw = float(forecast_total_net_kw[forecast_peak_index])
            robust_forecast_peak_kw = max(0.0, forecast_peak_kw) * args.peak_reserve_forecast_safety_factor
            peak_lead_steps = max(0, int(round(args.peak_reserve_lead_hours / DELTA_HOURS)))
            reserve_target_state = forecast_peak_index - peak_lead_steps

            reserve_active = bool(
                args.peak_reserve
                and robust_forecast_peak_kw >= args.peak_reserve_threshold_kw
            )

            # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 6 START
            # Forecast is preparation-only.  Actual load + measured voltage are
            # authoritative for voltage protection.
            #
            # The phase ride-through latch CANNOT turn off merely because the previous
            # battery command temporarily pushed voltage above target.  It only exits
            # after the feeder outlier itself has passed.
            reserve_release_phases = set()
            reserve_pause_phases = set()
            phase_event_voltage_pu = {}
            phase_baseline_now_kw = {}
            phase_previous_batt_kw = {}
            phase_safe_cap_now_kw = {}
            phase_support_safe_cap_now_kw = {}
            phase_precharge_safe_cap_now_kw = {}

            feeder_baseline_now_kw = float(sum(
                node_data[nd]["load_kw"][i] - node_data[nd]["pv_kw"][i]
                for nd in NODE_MAP
            ))
            hours_to_forecast_peak = max(0.0, float(forecast_peak_index) * DELTA_HOURS)

            for ph in PHASES:
                control_pu, _, _, _ = phase_voltage_measurement(
                    ph, node_voltage, node_v_valid, args.voltage_reference)
                phase_event_voltage_pu[ph] = control_pu

                members = [nd for nd in NODE_MAP if node_phase(nd) == ph]
                baseline_now = float(sum(
                    node_data[nd]["load_kw"][i] - node_data[nd]["pv_kw"][i]
                    for nd in members
                ))
                previous_batt = float(sum(last_applied_batt_kw.get(nd, 0.0) for nd in members))

                phase_baseline_now_kw[ph] = baseline_now
                phase_previous_batt_kw[ph] = previous_batt

                # Keep old learned caps only for soft-horizon MPC/logging.
                safe_cap_now = None
                support_cap_now = None
                precharge_cap_now = None
                if phase_caps and ph in phase_caps:
                    try:
                        safe_cap_now = float(np.asarray(phase_caps[ph][0], dtype=float).reshape(-1)[0])
                    except Exception:
                        pass
                if ph in phase_support_caps:
                    try:
                        support_cap_now = float(np.asarray(phase_support_caps[ph][0], dtype=float).reshape(-1)[0])
                    except Exception:
                        pass
                if ph in phase_precharge_caps:
                    try:
                        precharge_cap_now = float(np.asarray(phase_precharge_caps[ph][0], dtype=float).reshape(-1)[0])
                    except Exception:
                        pass

                phase_safe_cap_now_kw[ph] = safe_cap_now
                phase_support_safe_cap_now_kw[ph] = support_cap_now
                phase_precharge_safe_cap_now_kw[ph] = precharge_cap_now

                st = security_ride_state[ph]
                active = bool(st["active"])
                recover_count = int(st["recover_count"])

                if control_pu is not None:
                    emergency = control_pu < args.v_min_pu
                    high_load_low_headroom = (
                        feeder_baseline_now_kw >= args.security_event_enter_load_kw
                        and control_pu <= args.security_event_enter_voltage_pu
                    )

                    if not active and (emergency or high_load_low_headroom):
                        active = True
                        recover_count = 0

                    if active:
                        outlier_has_passed = (
                            feeder_baseline_now_kw <= args.security_event_exit_load_kw
                            and control_pu >= args.guard_v_min_pu
                        )
                        if outlier_has_passed:
                            recover_count += 1
                        else:
                            recover_count = 0

                        if recover_count >= args.security_event_exit_steps:
                            active = False
                            recover_count = 0

                st["active"] = active
                st["recover_count"] = recover_count

                reserve_voltage_event_state[ph]["mode"] = "support" if active else None
                reserve_voltage_event_state[ph]["hold"] = recover_count

                if active:
                    reserve_release_phases.add(ph)

            support_armed = bool(reserve_release_phases)
            reserve_released = bool(reserve_release_phases)

            if reserve_release_phases:
                reserve_stage = "v19_ride_through:" + ",".join(sorted(reserve_release_phases))
            elif reserve_active and args.peak_reserve_fill_mode == "asap":
                reserve_stage = "v19_asap_fill_or_lock"
            elif reserve_active and reserve_target_state > 0:
                reserve_stage = "v19_deadline_prepare"
            elif reserve_active:
                reserve_stage = "v19_charged_hold"
            else:
                reserve_stage = "normal_mpc"
            # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 6 END

            peak_reserve_cfg = {
                "active": reserve_active,
                "target_state": reserve_target_state,
                "target_pct": args.peak_reserve_target_pct,
                "penalty": args.peak_reserve_penalty,
                "release_phases": tuple(sorted(reserve_release_phases)),
            }

            # >>> V13 CONTINUOUS PRECHARGE CHANGE 8 START
            # Authoritative first-action security dispatch.
            #
            # PREPARE uses CLOSED-LOOP measured-voltage feedback instead of an RLS-derived
            # absolute import cap as the charging command. Let Pbat be positive for discharge
            # and negative for charge. The feedback proposal is
            #
            #   Pbat_next = Pbat_prev + K_v * (V_target - V_measured) / rho_pu_per_kw
            #
            # so low voltage makes Pbat less negative (less charging), and high voltage lets
            # charging grow smoothly. The deadline-derived charging request is then clipped by
            # that voltage-following proposal and by the security charge ceiling.
            #
            # SUPPORT uses the stable V15/V16 measured-voltage ride-through law.
            phase_first_action_bounds = {}
            node_first_action_bounds = {}
            phase_security_charge_command_kw = {}
            phase_security_energy_deficit_kwh = {}
            phase_security_soc_pct = {}
            phase_precharge_feedback_batt_kw = {}
            phase_precharge_rho_used_pu_per_kw = {}
            phase_precharge_required_average_kw = {}
            phase_precharge_allocated_charge_kw = {}
            # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 10 START
            phase_support_feedback_batt_kw = {}
            phase_support_feedforward_batt_kw = {}
            phase_support_rho_used_pu_per_kw = {}
            # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 10 END
            node_precharge_alloc_charge_kw = {nd: 0.0 for nd in NODE_MAP}
            node_precharge_deficit_kwh = {nd: 0.0 for nd in NODE_MAP}

            if not args.no_hard_phase_first_action:
                for ph in PHASES:
                    soft_safe_cap = phase_safe_cap_now_kw.get(ph)
                    support_safe_cap = phase_support_safe_cap_now_kw.get(ph)
                    control_pu = phase_event_voltage_pu.get(ph)
                    if support_safe_cap is None:
                        support_safe_cap = soft_safe_cap
                    if support_safe_cap is None or not np.isfinite(support_safe_cap):
                        continue

                    members = [nd for nd in NODE_MAP
                               if node_phase(nd) == ph and hw[nd]["cap_kwh"] > 0]
                    if not members:
                        continue

                    baseline_now = float(phase_baseline_now_kw[ph])
                    raw_support_batt = baseline_now - float(support_safe_cap)

                    phase_cap_kwh = float(sum(hw[nd]["cap_kwh"] for nd in members))
                    phase_soc_kwh = 0.0
                    discharge_available = 0.0
                    per_node_soc_now = {}
                    for nd in members:
                        soc_now = (soc_measured_646_CIL_kwh
                                   if (nd == CIL_NODE and cil_soc_feedback_active)
                                   else soc_pred[nd])
                        soc_now = float(soc_now)
                        per_node_soc_now[nd] = soc_now
                        phase_soc_kwh += soc_now
                        energy_power = max(0.0, (soc_now - hw[nd]["soc_lo_kwh"]) / DELTA_HOURS)
                        discharge_available += min(hw[nd]["p_hi_kw"], energy_power)

                    phase_security_soc_pct[ph] = (
                        100.0 * phase_soc_kwh / phase_cap_kwh if phase_cap_kwh > 0 else 0.0
                    )
                    target_kwh = phase_cap_kwh * args.peak_reserve_target_pct / 100.0
                    energy_deficit_kwh = max(0.0, target_kwh - phase_soc_kwh)
                    phase_security_energy_deficit_kwh[ph] = energy_deficit_kwh

                    for nd in members:
                        target_nd_kwh = hw[nd]["cap_kwh"] * args.peak_reserve_target_pct / 100.0
                        node_precharge_deficit_kwh[nd] = max(0.0, target_nd_kwh - per_node_soc_now[nd])

                    support_now = ph in reserve_release_phases

                    if support_now:
                        # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 7 START
                        # Persistent load-tracking voltage droop:
                        #
                        # grid = baseline - battery
                        #
                        # Pbat_new = Pbat_prev + ΔPbaseline
                        #            + K*(Vtarget - Vmeas)/rho_fixed
                        #
                        # This directly follows the measured outlier ramp.  Temporary
                        # over-correction smoothly reduces discharge; it never switches
                        # support off while the feeder is still in the high-load event.
                        prev_phase_batt = float(phase_previous_batt_kw.get(ph, 0.0))
                        prev_baseline = last_phase_baseline_kw.get(ph)
                        baseline_delta = 0.0 if prev_baseline is None else (
                            baseline_now - float(prev_baseline)
                        )

                        rho_fixed = max(
                            1e-9,
                            args.security_support_fixed_rho_mult
                            * RHO0_V_PER_KW[ph] / NOMINAL_VOLTAGE
                        )
                        phase_support_rho_used_pu_per_kw[ph] = rho_fixed

                        if control_pu is None:
                            voltage_term_kw = 0.0
                        else:
                            voltage_term_kw = (
                                args.security_support_gain
                                * (args.phase_support_voltage_target_pu - float(control_pu))
                                / rho_fixed
                            )

                        desired_support = (
                            max(0.0, prev_phase_batt)
                            + baseline_delta
                            + voltage_term_kw
                        )
                        desired_support = float(np.clip(
                            desired_support, 0.0, discharge_available
                        ))

                        phase_support_feedforward_batt_kw[ph] = max(
                            0.0, max(0.0, prev_phase_batt) + baseline_delta
                        )
                        phase_support_feedback_batt_kw[ph] = desired_support
                        phase_security_charge_command_kw[ph] = 0.0
                        phase_precharge_feedback_batt_kw[ph] = 0.0
                        phase_precharge_required_average_kw[ph] = 0.0

                        # The joint NODAL MPC remains the optimizer. V15 only fixes the
                        # aggregate phase first action needed for voltage security; the QP
                        # still allocates that action among individual nodal batteries subject
                        # to their own power, SoC and hard directional limits.
                        phase_first_action_bounds[ph] = (desired_support, desired_support)
                        # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 7 END

                    elif reserve_active:
                        phase_customers = sum(N_CUSTOMERS[nd] for nd in members)
                        security_charge_limit = max(
                            0.0, args.security_max_charge_per_customer_kw * phase_customers
                        )

                        # >>> V17 FORECAST RESERVE LOCK CHANGE 3 START
                        # In ASAP mode the forecast is a binary preparation signal: once the
                        # extreme event enters the horizon, request the maximum configured charge
                        # rate immediately. The measured-voltage precharge loop below remains the
                        # final authority and reduces/blocks charging whenever voltage headroom is
                        # insufficient. At the target SoC, required_average_kw becomes zero; the
                        # exact first-action bounds then lock the reserve against economic discharge.
                        if energy_deficit_kwh <= 1e-6:
                            required_average_kw = 0.0
                        elif args.peak_reserve_fill_mode == "asap":
                            required_average_kw = security_charge_limit
                        elif reserve_target_state > 0:
                            hours_to_target = max(DELTA_HOURS, reserve_target_state * DELTA_HOURS)
                            required_average_kw = min(security_charge_limit, energy_deficit_kwh / hours_to_target)
                        else:
                            required_average_kw = security_charge_limit
                        # <<< V17 FORECAST RESERVE LOCK CHANGE 3 END
                        phase_precharge_required_average_kw[ph] = float(required_average_kw)

                        # Continuous measured-voltage following. Use a bounded version of the
                        # learned phase slope only for the INCREMENTAL correction; this avoids
                        # the absolute-cap drift that previously produced negative import caps.
                        # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 8 START
                        # Preparation uses the same incremental physical structure and a
                        # FIXED calibrated sensitivity. No absolute learned import cap is
                        # used for the applied charging action.
                        prev_phase_batt = float(phase_previous_batt_kw.get(ph, 0.0))
                        prev_baseline = last_phase_baseline_kw.get(ph)
                        baseline_delta = 0.0 if prev_baseline is None else (
                            baseline_now - float(prev_baseline)
                        )
                        rho_eff = max(
                            1e-9,
                            args.security_precharge_fixed_rho_mult
                            * RHO0_V_PER_KW[ph] / NOMINAL_VOLTAGE
                        )
                        phase_precharge_rho_used_pu_per_kw[ph] = rho_eff

                        if control_pu is None:
                            voltage_follow_batt = -required_average_kw
                        else:
                            correction_kw = (
                                args.security_precharge_gain
                                * (args.precharge_voltage_target_pu - float(control_pu))
                                / rho_eff
                            )
                            voltage_follow_batt = prev_phase_batt + baseline_delta + correction_kw
                        # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 8 END

                        # Preparation may charge or idle, never discharge stored reserve.
                        voltage_follow_batt = float(np.clip(
                            voltage_follow_batt, -security_charge_limit, 0.0
                        ))
                        phase_precharge_feedback_batt_kw[ph] = voltage_follow_batt

                        # Deadline asks for -required_average_kw; feedback sets the maximum
                        # safe charging magnitude. max() chooses the LESS-negative of the two.
                        desired_phase_batt = max(-float(required_average_kw), voltage_follow_batt)

                        # The +/-3% hard-action rule remains absolute. If the phase already
                        # crossed 0.970 pu, do not charge this action. There is no multi-step
                        # phase-wide pause; as soon as measured voltage recovers, feedback
                        # resumes charging at an appropriately reduced level.
                        if control_pu is not None and control_pu <= args.guard_v_min_pu:
                            desired_phase_batt = 0.0

                        desired_charge_kw = max(0.0, -float(desired_phase_batt))
                        phase_security_charge_command_kw[ph] = desired_charge_kw

                        # Temporarily set the requested aggregate. After node guards are
                        # evaluated below, V13 allocates this charge by individual SoC deficit
                        # and replaces this bound with the actually feasible allocated sum.
                        phase_first_action_bounds[ph] = (-desired_charge_kw, -desired_charge_kw)

                    else:
                        # Ordinary day: retain cost-saving MPC.  Only an ACTUAL <0.95-pu
                        # emergency enters reserve_release_phases via the supervisor above;
                        # still-compliant 0.95-0.96 dips do not spend security energy.
                        phase_security_charge_command_kw[ph] = 0.0
                        phase_precharge_feedback_batt_kw[ph] = 0.0
                        phase_precharge_required_average_kw[ph] = 0.0
            # <<< V13 CONTINUOUS PRECHARGE CHANGE 8 END
            # <<< V8 ROBUST PRECHARGE CHANGE 7 END

            # >>> CHATTER/STABILITY CHANGE 9 START: hysteresis + minimum dwell-time directional guard
            # The old relay-style guard switched off immediately as soon as V crossed back inside its hard action band,
            # which caused charge/idle/charge chatter. This state machine engages at the configured hard-action limit,
            # stays active for at least N steps after the latest engage event, and only releases after a
            # healthier recovery threshold is reached. An opposite-side voltage emergency overrides immediately.
            directional_voltage_guard = {}
            if not args.no_directional_voltage_guard:
                for nd in NODE_MAP:
                    if hw[nd]["cap_kwh"] <= 0:
                        continue
                    st = directional_guard_state[nd]
                    mode = st["mode"]
                    hold = int(st["hold"])

                    if node_v_valid.get(nd, False):
                        vpu_now = node_voltage_pu(nd, node_voltage[nd])

                        # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 9 START
                        # Once the reserve target has released, do not let a stale historical
                        # over-voltage lockout strand stored energy through the main load peak.
                        # Only clear it after voltage is already safely below the high-side
                        # release threshold; a real/high voltage still retains no-discharge.
                        if (node_phase(nd) in reserve_release_phases
                                and not args.no_peak_guard_release_override
                                and mode == "no_discharge"
                                and vpu_now <= guard_high_release_pu):
                            mode = None
                            hold = 0
                        # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 9 END

                        if mode is None:
                            if vpu_now <= guard_low_engage_pu:
                                mode = "no_charge"
                                hold = args.directional_guard_hold_steps
                            elif vpu_now >= guard_high_engage_pu:
                                mode = "no_discharge"
                                hold = args.directional_guard_hold_steps

                        elif mode == "no_charge":
                            # Opposite emergency takes priority immediately.
                            if vpu_now >= guard_high_engage_pu:
                                mode = "no_discharge"
                                hold = args.directional_guard_hold_steps
                            elif vpu_now <= guard_low_engage_pu:
                                # Still near/in undervoltage: restart the dwell timer from this latest event.
                                hold = args.directional_guard_hold_steps
                            else:
                                # hold counts FOLLOWING MPC steps after the latest engage event.
                                # Do not release on the same step that the counter reaches zero.
                                if hold > 0:
                                    hold -= 1
                                elif vpu_now >= guard_low_release_pu:
                                    mode = None

                        elif mode == "no_discharge":
                            # Opposite emergency takes priority immediately.
                            if vpu_now <= guard_low_engage_pu:
                                mode = "no_charge"
                                hold = args.directional_guard_hold_steps
                            elif vpu_now >= guard_high_engage_pu:
                                # Still near/in overvoltage: restart the dwell timer from this latest event.
                                hold = args.directional_guard_hold_steps
                            else:
                                # hold counts FOLLOWING MPC steps after the latest engage event.
                                # Do not release on the same step that the counter reaches zero.
                                if hold > 0:
                                    hold -= 1
                                elif vpu_now <= guard_high_release_pu:
                                    mode = None

                    # If a voltage sample is missing, retain the previous safety mode/hold rather than
                    # silently releasing the guard on stale data.
                    st["mode"] = mode
                    st["hold"] = hold
                    if mode is not None:
                        directional_voltage_guard[nd] = mode

            # >>> V13 CONTINUOUS PRECHARGE CHANGE 9 START
            # Whole-phase protection is required only during genuine ride-through.
            # There is deliberately no phase-wide precharge pause in V13.
            for nd in NODE_MAP:
                ph = node_phase(nd)
                if hw[nd]["cap_kwh"] <= 0:
                    continue
                existing = directional_voltage_guard.get(nd)
                if ph in reserve_release_phases:
                    directional_voltage_guard[nd] = "idle" if existing == "no_discharge" else "no_charge"
            # <<< V13 CONTINUOUS PRECHARGE CHANGE 9 END
            # <<< CHATTER/STABILITY CHANGE 9 END

            # >>> V13 CONTINUOUS PRECHARGE CHANGE 10 START
            # SoC-balanced nodal allocation of the aggregate security charging request.
            # Allocation weights are ENERGY deficits (kWh), so equal percentage deficits
            # naturally give larger batteries proportionally more charging. Each node is
            # clipped by hardware power, remaining SoC room, the asymmetric charge ramp,
            # and its current hard directional guard. Any unavailable share is redistributed.
            if reserve_active and not args.no_hard_phase_first_action:
                for ph in PHASES:
                    if ph in reserve_release_phases:
                        continue
                    desired_total_charge = float(phase_security_charge_command_kw.get(ph, 0.0))
                    members = [nd for nd in NODE_MAP
                               if node_phase(nd) == ph and hw[nd]["cap_kwh"] > 0]
                    if not members:
                        continue

                    max_charge = {}
                    deficit = {}
                    for nd in members:
                        soc_now = (soc_measured_646_CIL_kwh
                                   if (nd == CIL_NODE and cil_soc_feedback_active)
                                   else soc_pred[nd])
                        soc_now = float(soc_now)
                        deficit[nd] = max(0.0, float(node_precharge_deficit_kwh.get(nd, 0.0)))

                        pmax_hw = max(0.0, -float(hw[nd]["p_lo_kw"]))
                        pmax_room = max(0.0, (float(hw[nd]["soc_hi_kwh"]) - soc_now) / DELTA_HOURS)

                        ramp = max(0.0, float(charge_ramp_kw.get(nd, 0.0)))
                        p_prev = float(last_applied_batt_kw.get(nd, 0.0))
                        ramp_floor = min(0.0, p_prev) - ramp
                        pmax_ramp = max(0.0, -ramp_floor)

                        guard_mode = directional_voltage_guard.get(nd)
                        if guard_mode in ("no_charge", "idle") or deficit[nd] <= 1e-9:
                            pmax = 0.0
                        else:
                            pmax = min(pmax_hw, pmax_room, pmax_ramp)
                        max_charge[nd] = max(0.0, float(pmax))

                    alloc = {nd: 0.0 for nd in members}
                    remaining = min(
                        max(0.0, desired_total_charge),
                        sum(max_charge.values()),
                    )
                    active = {nd for nd in members if max_charge[nd] > 1e-9 and deficit[nd] > 1e-9}

                    # Deficit-weighted water filling with redistribution after clipping.
                    for _ in range(len(members) + 2):
                        if remaining <= 1e-7 or not active:
                            break
                        wsum = sum(deficit[nd] for nd in active)
                        if wsum <= 1e-12:
                            break
                        used = 0.0
                        saturated = set()
                        for nd in list(active):
                            room = max_charge[nd] - alloc[nd]
                            share = remaining * deficit[nd] / wsum
                            add = min(room, share)
                            alloc[nd] += add
                            used += add
                            if room - add <= 1e-7:
                                saturated.add(nd)
                        remaining -= used
                        active -= saturated
                        if used <= 1e-9:
                            break

                    allocated_total = float(sum(alloc.values()))
                    phase_precharge_allocated_charge_kw[ph] = allocated_total
                    phase_security_charge_command_kw[ph] = allocated_total
                    phase_first_action_bounds[ph] = (-allocated_total, -allocated_total)

                    # Exact per-node commands stop the economic objective from circulating
                    # energy between batteries during the rare security preparation window.
                    for nd in members:
                        cmd = -float(alloc[nd])
                        node_precharge_alloc_charge_kw[nd] = float(alloc[nd])
                        node_first_action_bounds[nd] = (cmd, cmd)
            # <<< V13 CONTINUOUS PRECHARGE CHANGE 10 END

            # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 10 START
            # Last-resort rescue guard. It has no hysteresis memory: it only forbids
            # an action that would worsen a voltage that is ALREADY outside the +/-4% hard action band.
            instantaneous_voltage_guard = {}
            if not args.no_directional_voltage_guard:
                for nd in NODE_MAP:
                    if hw[nd]["cap_kwh"] <= 0 or not node_v_valid.get(nd, False):
                        continue
                    vpu_now = node_voltage_pu(nd, node_voltage[nd])
                    if vpu_now <= args.guard_v_min_pu:
                        instantaneous_voltage_guard[nd] = "no_charge"
                    elif vpu_now >= args.guard_v_max_pu:
                        instantaneous_voltage_guard[nd] = "no_discharge"
            # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 10 END

            # >>> USER REQUEST CHANGE 18 START: optional local weak-node first-action support (OFF by default)
            local_voltage_deficit = {}
            if args.local_voltage_support:
                for nd in NODE_MAP:
                    if node_v_valid.get(nd, False) and hw[nd]["cap_kwh"] > 0:
                        local_voltage_deficit[nd] = max(
                            0.0, args.local_voltage_support_start_pu - node_voltage_pu(nd, node_voltage[nd]))
                    else:
                        local_voltage_deficit[nd] = 0.0
            # <<< USER REQUEST CHANGE 18 END

            # >>> USER REQUEST CHANGE 19 START: this ONE joint QP IS the nodal MPC
            soc0_all = {nd: (soc_measured_646_CIL_kwh if (nd == CIL_NODE and cil_soc_feedback_active)
                             else soc_pred[nd]) for nd in NODE_MAP}
            # >>> V5 NODAL VOLTAGE/RAMP CHANGE 12 START
            previous_batt_for_step = dict(last_applied_batt_kw)
            # <<< V5 NODAL VOLTAGE/RAMP CHANGE 12 END
            fb_res = solve_joint_nodal_mpc_qp(
                p_load_win, p_pv_win, eta_win, args.weight, hw, soc0_all,
                phase_caps or None, node_caps or None, args.k_slack, args.solver,
                peak_reserve=peak_reserve_cfg,
                local_voltage_deficit=local_voltage_deficit,
                local_voltage_support_penalty=args.local_voltage_support_penalty,
                directional_voltage_guard=directional_voltage_guard,
                previous_batt_kw=previous_batt_for_step,
                battery_smoothing_weight=args.battery_smoothing_weight,
                charge_ramp_kw=charge_ramp_kw,
                secondary_solver=args.secondary_solver,
                rescue_directional_voltage_guard=instantaneous_voltage_guard,
                phase_first_action_bounds=phase_first_action_bounds,
                node_first_action_bounds=node_first_action_bounds)
            # <<< USER REQUEST CHANGE 19 END

            reserve_slack_total_kwh = 0.0
            if fb_res.get("reserve_slack"):
                reserve_slack_total_kwh = float(sum(np.sum(v) for v in fb_res["reserve_slack"].values()))

            for node in NODE_MAP:
                node_load_act = node_data[node]["load_kw"]
                node_pv_act = node_data[node]["pv_kw"]
                status[node] = fb_res["status"]
                obj_val[node] = fb_res["obj"]
                batt_traj[node] = None if fb_res["batt"] is None else fb_res["batt"][node]
                grid_traj[node] = None if fb_res["grid"] is None else fb_res["grid"][node]
                soc_traj[node] = None if fb_res["soc"] is None else fb_res["soc"][node]

                if status[node] not in ("optimal", "optimal_inaccurate"):
                    print(f"  WARNING: MPC status = {status[node]} at step {step}; applying zero battery command at {node}.")
                    p_bat_node[node] = 0.0
                    soc_pred_next[node] = soc_pred[node]
                    grid_forecast_kw[node] = float(p_load_win[node][0] - p_pv_win[node][0])
                else:
                    p_bat_node[node] = float(batt_traj[node][0])
                    soc_pred_next[node] = float(soc_traj[node][1])
                    grid_forecast_kw[node] = float(grid_traj[node][0])

                pbat_nodes[node] = p_bat_node[node]
                soc_pred[node] = soc_pred_next[node]
                cap_kwh = hw[node]["cap_kwh"]
                soc_pred_pct[node] = 100.0 * soc_pred[node] / cap_kwh if cap_kwh > 0 else np.nan
                load_act_i[node] = float(node_load_act[i])
                pv_act_i[node] = float(node_pv_act[i])
                grid_act_i[node] = load_act_i[node] - pv_act_i[node] - p_bat_node[node]

            # >>> CHATTER/STABILITY CHANGE 10 START
            # Store exactly the commands that are about to be applied. They become the smoothing reference
            # for the next receding-horizon solve.
            last_applied_batt_kw = dict(pbat_nodes)
            # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 9 START
            for ph in PHASES:
                if ph in phase_baseline_now_kw:
                    last_phase_baseline_kw[ph] = float(phase_baseline_now_kw[ph])
            # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 9 END
            # <<< CHATTER/STABILITY CHANGE 10 END


            # >>> V19 BATTERY EMULATOR CHANGE 8 START: apply selected battery implementation
            hardware_soc_646 = None
            hardware_soc_raw_646 = None
            hardware_soc_age_s = None
            hardware_soc_fresh = False
            hardware_refresh_count = 0
            hardware_emu_info = {
                "command": "-", "code": None, "saturated": False,
                "target_delta_raw": None, "target_delta_pct": None,
                "hold_seconds": 0.0, "unclamped_hold_seconds": None,
                "required_rate_raw_per_s": None, "max_rate_raw_per_s": None,
                "equivalent_power_kw": None,
            }

            if effective_battery_emulator == "hardware":
                # Capture the current sample, then issue the time-scaled physical command.
                hardware_emu.read_latest(min(0.25, args.hardware_emu_wait))
                hardware_emu_info = hardware_emu.send_dynamic_power_command(
                    p_bat_kw=p_bat_node[CIL_NODE],
                    capacity_kwh=cil_capacity_kwh,
                    min_hold_s=args.hardware_min_hold_seconds,
                    max_hold_s=args.hardware_max_hold_seconds,
                    idle_hold_s=args.hardware_idle_hold_seconds,
                    preferred_code=args.hardware_preferred_code,
                    charge_max_raw_per_s=args.hardware_emu_charge_rate,
                    discharge_max_raw_per_s=args.hardware_emu_discharge_rate,
                )
                if hardware_emu_info["saturated"]:
                    print(f"  WARNING: physical emulator command saturated at {hardware_emu_info['command']} "
                          f"for requested Pbat646={p_bat_node[CIL_NODE]:.2f} kW.")

            # Write feeder inputs through the selected HIL backend exactly as before.
            if args.backend == "api":
                conn.write_feeder(node_data, i, pbat_nodes)
            else:
                payload = build_feeder_payload(node_data, i, pbat_nodes)
                modbus_write_feeder(conn, payload, args.dry_run, args.verbose)

            if effective_battery_emulator == "hardware":
                hold_s = float(hardware_emu_info["hold_seconds"])
                refresh_cmd = (hardware_emu_info["command"]
                               if hardware_emu_info.get("code") not in (None, 0) else None)
                (hardware_soc_raw_646, hardware_soc_646, hardware_soc_age_s,
                 hardware_soc_fresh, hardware_refresh_count) = hardware_emu.hold_and_read(
                    duration_s=hold_s,
                    wait_s=args.hardware_emu_wait,
                    progress_every_s=args.hardware_hold_progress_seconds,
                    refresh_command=refresh_cmd,
                    refresh_every_s=args.hardware_command_refresh_seconds,
                )
                if hardware_soc_646 is None:
                    raise RuntimeError(f"No physical battery-emulator SoC available at step {step}.")
                if hardware_soc_age_s is not None and hardware_soc_age_s > args.hardware_emu_stale_limit:
                    raise RuntimeError(f"Physical battery-emulator SoC is stale ({hardware_soc_age_s:.2f}s) at step {step}.")
            elif not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                time.sleep(args.measurement_delay)

            # HIL/API SoC is sampled in HIL mode and ALSO in HARDWARE mode for comparison.
            measured_soc_646 = soc_logger.log_step() if hil_log_enabled else None

            # Select which state closes the Node-646 controller loop.
            if effective_battery_emulator == "hardware":
                soc_measured_646_CIL_kwh = float(hardware_soc_646) / 100.0 * cil_capacity_kwh
                cil_soc_feedback_active = True
            elif effective_battery_emulator == "hil" and measured_soc_646 is not None:
                soc_measured_646_CIL_kwh = float(measured_soc_646) / 100.0 * cil_capacity_kwh
                cil_soc_feedback_active = True
            else:
                soc_measured_646_CIL_kwh = soc_pred[CIL_NODE]
                cil_soc_feedback_active = False
            # <<< V19 BATTERY EMULATOR CHANGE 8 END

            # >>> USER REQUEST CHANGE 21 START: robust post-action voltage feedback
            voltage_fallback_warned = refresh_voltage_snapshot(
                soc_logger, args.dry_run, node_voltage, node_v_valid, voltage_fallback_warned)
            # <<< USER REQUEST CHANGE 21 END

            # >>> V5 NODAL VOLTAGE/RAMP CHANGE 11 START: update/log nodal + phase voltage models
            # First update the LOCAL node models from the action that was just applied and the resulting measured V.
            # Forecast bias is actual local net demand minus the step-0 forecast net demand; battery command cancels.
            node_log_cols = {}
            for nd in NODE_MAP:
                node_bias_kw[nd] = (
                    (load_act_i[nd] - pv_act_i[nd])
                    - (float(p_load_win[nd][0]) - float(p_pv_win[nd][0]))
                )
                if node_v_valid.get(nd, False) and hw[nd]["cap_kwh"] > 0:
                    node_estimators[nd].update(node_voltage[nd], grid_act_i[nd])

                nsl = fb_res.get("node_slack", {}).get(nd)
                node_slack0 = 0.0 if nsl is None else float(nsl[0][0] + nsl[1][0])
                if node_slack0 > 1e-3:
                    node_slack_steps[nd] += 1

                nd_vpu = node_voltage_pu(nd, node_voltage[nd]) if node_v_valid.get(nd, False) else None
                nd_violation = bool(nd_vpu is not None and (nd_vpu < args.v_min_pu or nd_vpu > args.v_max_pu))
                if nd_violation and node_slack0 <= 1e-3 and bool(fb_res.get("voltage_caps_used", False)) \
                        and args.voltage_cap_mode in ("nodal", "both") and node_caps and nd in node_caps:
                    node_model_miss_steps[nd] += 1

                cap_hi0 = node_caps[nd][0][0] if (node_caps and nd in node_caps) else ""
                cap_lo0 = node_caps[nd][1][0] if (node_caps and nd in node_caps) else ""
                node_log_cols |= {
                    f"{nd}_voltage_pu": "" if nd_vpu is None else round(float(nd_vpu), 5),
                    f"{nd}_voltage_rho_v_per_kw": round(node_estimators[nd].rho, 7),
                    f"{nd}_voltage_import_cap_hi_kw": "" if cap_hi0 == "" else round(float(cap_hi0), 4),
                    f"{nd}_voltage_import_cap_lo_kw": "" if cap_lo0 == "" else round(float(cap_lo0), 4),
                    f"{nd}_voltage_slack_kw": round(node_slack0, 4),
                    f"{nd}_voltage_model_miss": int(nd_violation and node_slack0 <= 1e-3
                                                     and bool(fb_res.get("voltage_caps_used", False))
                                                     and args.voltage_cap_mode in ("nodal", "both")
                                                     and bool(node_caps and nd in node_caps)),
                }

            # Keep phase-level diagnostics (and optionally the legacy phase estimator/caps) for comparison.
            volt_log_cols = {}
            for ph in PHASES:
                nodes_ph = [nd for nd in NODE_MAP if node_phase(nd) == ph]
                p_ph = sum(grid_act_i[nd] for nd in nodes_ph)
                phase_bias_kw[ph] = sum(
                    (load_act_i[nd] - pv_act_i[nd]) - (p_load_win[nd][0] - p_pv_win[nd][0])
                    for nd in nodes_ph)
                control_pu, min_pu, min_node, avg_pu = phase_voltage_measurement(
                    ph, node_voltage, node_v_valid, args.voltage_reference)

                if control_pu is not None:
                    if args.voltage_cap_mode in ("phase", "both"):
                        estimators[ph].update(control_pu * NOMINAL_VOLTAGE, p_ph)
                    phase_pu_range[ph][0] = min(phase_pu_range[ph][0], min_pu)
                    phase_pu_range[ph][1] = max(phase_pu_range[ph][1], min_pu)

                psl = fb_res.get("slack", {}).get(ph)
                phase_cap_slack0 = 0.0 if psl is None else float(psl[0][0] + psl[1][0])
                nodal_cap_slack0 = 0.0
                for nd in nodes_ph:
                    nsl = fb_res.get("node_slack", {}).get(nd)
                    if nsl is not None:
                        nodal_cap_slack0 += float(nsl[0][0] + nsl[1][0])
                slack0 = phase_cap_slack0 + nodal_cap_slack0
                if slack0 > 1e-3:
                    slack_steps[ph] += 1

                measured_violation = bool(min_pu is not None and
                                          (min_pu < args.v_min_pu or min_pu > args.v_max_pu))
                if measured_violation:
                    measured_violation_steps[ph] += 1
                    if slack0 <= 1e-3 and bool(fb_res.get("voltage_caps_used", False)):
                        model_miss_steps[ph] += 1

                cap0 = phase_caps[ph][0][0] if (phase_caps and ph in phase_caps) else ""
                volt_log_cols |= {
                    f"phase_{ph}_import_kw": round(p_ph, 4),
                    f"phase_{ph}_control_voltage_pu": "" if control_pu is None else round(control_pu, 5),
                    f"phase_{ph}_min_voltage_pu": "" if min_pu is None else round(min_pu, 5),
                    f"phase_{ph}_avg_voltage_pu": "" if avg_pu is None else round(avg_pu, 5),
                    f"phase_{ph}_weakest_node": "" if min_node is None else min_node,
                    f"phase_{ph}_rho_v_per_kw": round(estimators[ph].rho, 6),
                    f"phase_{ph}_import_cap_kw": "" if cap0 == "" else round(float(cap0), 3),
                    f"phase_{ph}_phase_cap_slack_kw": round(phase_cap_slack0, 4),
                    f"phase_{ph}_nodal_cap_slack_kw": round(nodal_cap_slack0, 4),
                    f"phase_{ph}_slack_kw": round(slack0, 4),
                    f"phase_{ph}_measured_violation": int(measured_violation),
                }
            # <<< V5 NODAL VOLTAGE/RAMP CHANGE 11 END

            total_load_i = float(total_load_act[i])
            total_pv_i   = float(total_pv_act[i])

            for node in NODE_MAP:
                p_bat_total += pbat_nodes[node]

            for node in NODE_MAP:
                if node != CIL_NODE:
                    sched_rows_node[node] = ({
                        f"{node}_p_load_fc_kw": round(float(p_load_win[node][0]), 4),
                        f"{node}_p_pv_fc_kw":   round(float(p_pv_win[node][0]), 4),
                        f"{node}_p_load_actual_kw": round(load_act_i[node], 4),
                        f"{node}_p_pv_actual_kw":   round(pv_act_i[node], 4),
                        f"{node}_baseline_grid_kw": round(load_act_i[node] - pv_act_i[node], 4),
                        f"{node}_battery_kw": round(p_bat_node[node], 4),
                        f"{node}_battery_action": _action(p_bat_node[node]),
                        f"{node}_grid_kw": round(grid_act_i[node], 4),
                        f"{node}_grid_forecast_kw": round(grid_forecast_kw[node], 4),
                        f"{node}_soc_predicted_pct": round(soc_pred_pct[node], 4),
                        f"{node}_mpc_status": status[node],
                        f"{node}_voltage": node_voltage[node],
                        f"{node}_directional_voltage_guard": directional_voltage_guard.get(node, ""),
                        f"{node}_directional_guard_hold_remaining": directional_guard_state[node]["hold"],
                        f"{node}_charge_ramp_kw_per_step": round(charge_ramp_kw[node], 4),
                        f"{node}_charge_ramp_floor_kw": round(min(0.0, previous_batt_for_step[node]) - charge_ramp_kw[node], 4)
                            if charge_ramp_kw[node] > 0 else "",
                        f"{node}_precharge_deficit_kwh": round(node_precharge_deficit_kwh.get(node, 0.0), 4),
                        f"{node}_precharge_alloc_charge_kw": round(node_precharge_alloc_charge_kw.get(node, 0.0), 4),
                    })


            sched_rows_node[CIL_NODE] = ({
                f"{CIL_NODE}_p_load_fc_kw": round(float(p_load_win[CIL_NODE][0]), 4),
                f"{CIL_NODE}_p_pv_fc_kw":   round(float(p_pv_win[CIL_NODE][0]), 4),
                f"{CIL_NODE}_p_load_actual_kw": round(load_act_i[CIL_NODE], 4),
                f"{CIL_NODE}_p_pv_actual_kw":   round(pv_act_i[CIL_NODE], 4),
                f"{CIL_NODE}_baseline_grid_kw": round(load_act_i[CIL_NODE] - pv_act_i[CIL_NODE], 4),
                f"{CIL_NODE}_battery_kw": round(p_bat_node[CIL_NODE], 4),
                f"{CIL_NODE}_battery_action": _action(p_bat_node[CIL_NODE]),
                f"{CIL_NODE}_grid_kw": round(grid_act_i[CIL_NODE], 4),
                f"{CIL_NODE}_grid_forecast_kw": round(grid_forecast_kw[CIL_NODE], 4),
                f"{CIL_NODE}_soc_predicted_pct": round(soc_pred_pct[CIL_NODE], 4),
                # HIL/internal/software measurement. Explicit '-' when feedback/logging is disabled or unavailable.
                f"{CIL_NODE}_soc_measured_pct": "-" if measured_soc_646 is None else round(float(measured_soc_646), 4),
                # NEW V19 physical-emulator measurement. It is populated only in HARDWARE mode.
                f"{CIL_NODE}_soc_hardware_pct": "-" if hardware_soc_646 is None else round(float(hardware_soc_646), 4),
                f"{CIL_NODE}_soc_feedback_source": effective_battery_emulator,
                f"{CIL_NODE}_hardware_emulator_command": hardware_emu_info["command"],
                f"{CIL_NODE}_hardware_emulator_hold_s": (
                    "-" if effective_battery_emulator != "hardware"
                    else round(float(hardware_emu_info["hold_seconds"]), 4)
                ),
                f"{CIL_NODE}_hardware_emulator_command_saturated": (
                    "-" if effective_battery_emulator != "hardware"
                    else int(bool(hardware_emu_info["saturated"]))
                ),
                f"{CIL_NODE}_hardware_emulator_raw_soc": (
                    "-" if hardware_soc_raw_646 is None else int(hardware_soc_raw_646)
                ),
                f"{CIL_NODE}_mpc_status": status[CIL_NODE],
                f"{CIL_NODE}_voltage": node_voltage[CIL_NODE],
                f"{CIL_NODE}_directional_voltage_guard": directional_voltage_guard.get(CIL_NODE, ""),
                f"{CIL_NODE}_directional_guard_hold_remaining": directional_guard_state[CIL_NODE]["hold"],
                f"{CIL_NODE}_charge_ramp_kw_per_step": round(charge_ramp_kw[CIL_NODE], 4),
                f"{CIL_NODE}_charge_ramp_floor_kw": round(min(0.0, previous_batt_for_step[CIL_NODE]) - charge_ramp_kw[CIL_NODE], 4)
                    if charge_ramp_kw[CIL_NODE] > 0 else "",
                f"{CIL_NODE}_precharge_deficit_kwh": round(node_precharge_deficit_kwh.get(CIL_NODE, 0.0), 4),
                f"{CIL_NODE}_precharge_alloc_charge_kw": round(node_precharge_alloc_charge_kw.get(CIL_NODE, 0.0), 4),
            })

            sched_rows_all_nodes = {}

            for node in NODE_MAP:
                sched_rows_all_nodes |= sched_rows_node[node]

            # >>> USER REQUEST CHANGE 23 START: log forecast/reserve/voltage-controller status explicitly
            sched_rows.append({
                "step": step,
                "day": day_num,
                "k": k,
                "forecast_mode": forecast_mode_name,
                "battery_emulator_mode": effective_battery_emulator,
                "battery_emulator_mode_requested": requested_battery_emulator,
                "feeder_baseline_grid_kw": round(total_load_i - total_pv_i, 4),
                "feeder_grid_with_batteries_kw": round(total_load_i - total_pv_i - p_bat_total, 4),
                "forecast_peak_net_kw": round(forecast_peak_kw, 4),
                "robust_forecast_peak_net_kw": round(robust_forecast_peak_kw, 4),
                "forecast_peak_safety_factor": args.peak_reserve_forecast_safety_factor,
                "forecast_peak_steps_ahead": forecast_peak_index,
                # >>> PEAK RESERVE RELEASE CHANGE 4 START
                "peak_reserve_active": int(peak_reserve_cfg["active"]),
                # >>> V17 FORECAST RESERVE LOCK CHANGE 4 START
                "peak_reserve_fill_mode": args.peak_reserve_fill_mode,
                "forecast_reserve_lock_active": int(bool(reserve_active and not reserve_release_phases)),
                # <<< V17 FORECAST RESERVE LOCK CHANGE 4 END
                "peak_reserve_released": int(reserve_released),
                # >>> V7 ENERGY MANAGEMENT CHANGE 8 START
                "peak_reserve_stage": reserve_stage,
                "peak_reserve_target_steps_ahead": reserve_target_state,
                "peak_reserve_target_pct": args.peak_reserve_target_pct if peak_reserve_cfg["active"] else "",
                "peak_reserve_release_phases": ";".join(sorted(reserve_release_phases)),
                "reserve_release_v_pu": args.reserve_release_v_pu,
                "reserve_recover_v_pu": args.reserve_recover_v_pu,
                "reserve_event_hold_steps": args.reserve_event_hold_steps,
                # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 12 START
                "support_armed": int(bool(support_armed)),
                "support_hours_to_forecast_peak": round(hours_to_forecast_peak, 4),
                "support_feeder_baseline_now_kw": round(feeder_baseline_now_kw, 4),
                # >>> V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 10 START
                "v15_phase_A_ride_active": int(bool(security_ride_state["A"]["active"])),
                "v15_phase_B_ride_active": int(bool(security_ride_state["B"]["active"])),
                "v15_phase_C_ride_active": int(bool(security_ride_state["C"]["active"])),
                "v15_phase_A_recover_count": int(security_ride_state["A"]["recover_count"]),
                "v15_phase_B_recover_count": int(security_ride_state["B"]["recover_count"]),
                "v15_phase_C_recover_count": int(security_ride_state["C"]["recover_count"]),
                "v15_security_event_enter_load_kw": args.security_event_enter_load_kw,
                "v16_security_event_enter_voltage_pu": args.security_event_enter_voltage_pu,
                "v15_security_event_exit_load_kw": args.security_event_exit_load_kw,
                "v15_support_fixed_rho_mult": args.security_support_fixed_rho_mult,
                "v15_support_gain": args.security_support_gain,
                # <<< V15 GROUND-UP VOLTAGE SUPERVISOR CHANGE 10 END
                # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 12 END
                # >>> V9 PHASE EVENT / PRECHARGE FIX 7 START
                "reserve_pause_hold_steps": args.reserve_pause_hold_steps,
                "reserve_event_phase_A": int(reserve_voltage_event_state["A"]["mode"] == "support"),
                "reserve_event_phase_B": int(reserve_voltage_event_state["B"]["mode"] == "support"),
                "reserve_event_phase_C": int(reserve_voltage_event_state["C"]["mode"] == "support"),
                "reserve_pause_phase_A": int(reserve_voltage_event_state["A"]["mode"] == "pause"),
                "reserve_pause_phase_B": int(reserve_voltage_event_state["B"]["mode"] == "pause"),
                "reserve_pause_phase_C": int(reserve_voltage_event_state["C"]["mode"] == "pause"),
                "reserve_phase_mode_A": reserve_voltage_event_state["A"]["mode"] or "",
                "reserve_phase_mode_B": reserve_voltage_event_state["B"]["mode"] or "",
                "reserve_phase_mode_C": reserve_voltage_event_state["C"]["mode"] or "",
                "reserve_phase_A_baseline_kw": round(phase_baseline_now_kw.get("A", float("nan")), 4),
                "reserve_phase_B_baseline_kw": round(phase_baseline_now_kw.get("B", float("nan")), 4),
                "reserve_phase_C_baseline_kw": round(phase_baseline_now_kw.get("C", float("nan")), 4),
                "reserve_phase_A_previous_batt_kw": round(phase_previous_batt_kw.get("A", float("nan")), 4),
                "reserve_phase_B_previous_batt_kw": round(phase_previous_batt_kw.get("B", float("nan")), 4),
                "reserve_phase_C_previous_batt_kw": round(phase_previous_batt_kw.get("C", float("nan")), 4),
                "reserve_phase_A_safe_cap_kw": "" if phase_safe_cap_now_kw.get("A") is None else round(phase_safe_cap_now_kw["A"], 4),
                "reserve_phase_B_safe_cap_kw": "" if phase_safe_cap_now_kw.get("B") is None else round(phase_safe_cap_now_kw["B"], 4),
                "reserve_phase_C_safe_cap_kw": "" if phase_safe_cap_now_kw.get("C") is None else round(phase_safe_cap_now_kw["C"], 4),
                # >>> V10 HARD PHASE DISPATCH 7 START
                "hard_phase_dispatch_enabled": int(not args.no_hard_phase_first_action),
                "hard_phase_A_batt_lo_kw": "" if "A" not in phase_first_action_bounds else round(phase_first_action_bounds["A"][0], 4),
                "hard_phase_A_batt_hi_kw": "" if "A" not in phase_first_action_bounds else round(phase_first_action_bounds["A"][1], 4),
                "hard_phase_B_batt_lo_kw": "" if "B" not in phase_first_action_bounds else round(phase_first_action_bounds["B"][0], 4),
                "hard_phase_B_batt_hi_kw": "" if "B" not in phase_first_action_bounds else round(phase_first_action_bounds["B"][1], 4),
                "hard_phase_C_batt_lo_kw": "" if "C" not in phase_first_action_bounds else round(phase_first_action_bounds["C"][0], 4),
                "hard_phase_C_batt_hi_kw": "" if "C" not in phase_first_action_bounds else round(phase_first_action_bounds["C"][1], 4),
                # >>> V11 VOLTAGE HOLD CHANGE 10 START
                "precharge_voltage_target_pu": args.precharge_voltage_target_pu,
                "phase_support_voltage_target_pu": args.phase_support_voltage_target_pu,
                "security_max_charge_per_customer_kw": args.security_max_charge_per_customer_kw,
                "phase_A_precharge_import_cap_kw": "" if phase_precharge_safe_cap_now_kw.get("A") is None else round(phase_precharge_safe_cap_now_kw["A"], 4),
                "phase_B_precharge_import_cap_kw": "" if phase_precharge_safe_cap_now_kw.get("B") is None else round(phase_precharge_safe_cap_now_kw["B"], 4),
                "phase_C_precharge_import_cap_kw": "" if phase_precharge_safe_cap_now_kw.get("C") is None else round(phase_precharge_safe_cap_now_kw["C"], 4),
                "phase_A_support_import_cap_kw": "" if phase_support_safe_cap_now_kw.get("A") is None else round(phase_support_safe_cap_now_kw["A"], 4),
                "phase_B_support_import_cap_kw": "" if phase_support_safe_cap_now_kw.get("B") is None else round(phase_support_safe_cap_now_kw["B"], 4),
                "phase_C_support_import_cap_kw": "" if phase_support_safe_cap_now_kw.get("C") is None else round(phase_support_safe_cap_now_kw["C"], 4),
                # >>> V12 SECURITY RIDE-THROUGH CHANGE 6 START
                "phase_A_security_soc_pct": round(phase_security_soc_pct.get("A", float("nan")), 4),
                "phase_B_security_soc_pct": round(phase_security_soc_pct.get("B", float("nan")), 4),
                "phase_C_security_soc_pct": round(phase_security_soc_pct.get("C", float("nan")), 4),
                "phase_A_security_energy_deficit_kwh": round(phase_security_energy_deficit_kwh.get("A", float("nan")), 4),
                "phase_B_security_energy_deficit_kwh": round(phase_security_energy_deficit_kwh.get("B", float("nan")), 4),
                "phase_C_security_energy_deficit_kwh": round(phase_security_energy_deficit_kwh.get("C", float("nan")), 4),
                "phase_A_security_charge_command_kw": round(phase_security_charge_command_kw.get("A", 0.0), 4),
                "phase_B_security_charge_command_kw": round(phase_security_charge_command_kw.get("B", 0.0), 4),
                "phase_C_security_charge_command_kw": round(phase_security_charge_command_kw.get("C", 0.0), 4),
                # >>> V13 CONTINUOUS PRECHARGE CHANGE 11 START
                "precharge_voltage_feedback_gain": args.precharge_voltage_feedback_gain,
                "phase_A_precharge_feedback_batt_kw": round(phase_precharge_feedback_batt_kw.get("A", 0.0), 4),
                "phase_B_precharge_feedback_batt_kw": round(phase_precharge_feedback_batt_kw.get("B", 0.0), 4),
                "phase_C_precharge_feedback_batt_kw": round(phase_precharge_feedback_batt_kw.get("C", 0.0), 4),
                "phase_A_precharge_required_average_kw": round(phase_precharge_required_average_kw.get("A", 0.0), 4),
                "phase_B_precharge_required_average_kw": round(phase_precharge_required_average_kw.get("B", 0.0), 4),
                "phase_C_precharge_required_average_kw": round(phase_precharge_required_average_kw.get("C", 0.0), 4),
                "phase_A_precharge_allocated_charge_kw": round(phase_precharge_allocated_charge_kw.get("A", 0.0), 4),
                "phase_B_precharge_allocated_charge_kw": round(phase_precharge_allocated_charge_kw.get("B", 0.0), 4),
                "phase_C_precharge_allocated_charge_kw": round(phase_precharge_allocated_charge_kw.get("C", 0.0), 4),
                "phase_A_precharge_rho_used_pu_per_kw": phase_precharge_rho_used_pu_per_kw.get("A", ""),
                "phase_B_precharge_rho_used_pu_per_kw": phase_precharge_rho_used_pu_per_kw.get("B", ""),
                "phase_C_precharge_rho_used_pu_per_kw": phase_precharge_rho_used_pu_per_kw.get("C", ""),
                # >>> V14 OUTLIER VOLTAGE HOLD CHANGE 13 START
                "support_voltage_feedback_gain": args.support_voltage_feedback_gain,
                "support_max_delta_per_customer_kw": args.support_max_delta_per_customer_kw,
                "phase_A_support_feedforward_batt_kw": round(phase_support_feedforward_batt_kw.get("A", 0.0), 4),
                "phase_B_support_feedforward_batt_kw": round(phase_support_feedforward_batt_kw.get("B", 0.0), 4),
                "phase_C_support_feedforward_batt_kw": round(phase_support_feedforward_batt_kw.get("C", 0.0), 4),
                "phase_A_support_feedback_batt_kw": round(phase_support_feedback_batt_kw.get("A", 0.0), 4),
                "phase_B_support_feedback_batt_kw": round(phase_support_feedback_batt_kw.get("B", 0.0), 4),
                "phase_C_support_feedback_batt_kw": round(phase_support_feedback_batt_kw.get("C", 0.0), 4),
                "phase_A_support_rho_used_pu_per_kw": phase_support_rho_used_pu_per_kw.get("A", ""),
                "phase_B_support_rho_used_pu_per_kw": phase_support_rho_used_pu_per_kw.get("B", ""),
                "phase_C_support_rho_used_pu_per_kw": phase_support_rho_used_pu_per_kw.get("C", ""),
                # <<< V14 OUTLIER VOLTAGE HOLD CHANGE 13 END
                # <<< V13 CONTINUOUS PRECHARGE CHANGE 11 END
                # <<< V12 SECURITY RIDE-THROUGH CHANGE 6 END
                # <<< V11 VOLTAGE HOLD CHANGE 10 END
                # <<< V10 HARD PHASE DISPATCH 7 END
                # <<< V9 PHASE EVENT / PRECHARGE FIX 7 END
                # <<< V7 ENERGY MANAGEMENT CHANGE 8 END
                "peak_reserve_total_slack_kwh": round(reserve_slack_total_kwh, 4),
                # <<< PEAK RESERVE RELEASE CHANGE 4 END
                "voltage_caps_used": int(bool(fb_res.get("voltage_caps_used", False))),
                "voltage_fallback": int(bool(fb_res.get("voltage_fallback", False))),
                # >>> V5 NODAL VOLTAGE/RAMP CHANGE 13 START
                "voltage_cap_mode": args.voltage_cap_mode if volt_on else "off",
                "max_charge_ramp_per_customer_kw": args.max_charge_ramp_per_customer_kw,
                # <<< V5 NODAL VOLTAGE/RAMP CHANGE 13 END
                # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 7 START
                "voltage_cap_failure_status": fb_res.get("voltage_cap_failure_status", ""),
                # >>> V6 PEAK SUPPORT/ROBUSTNESS CHANGE 11 START
                "solver_used": fb_res.get("solver_used", ""),
                "primary_solver_status": fb_res.get("primary_solver_status", ""),
                "secondary_solver_status": fb_res.get("secondary_solver_status", ""),
                "safety_rescue": int(bool(fb_res.get("safety_rescue", False))),
                # <<< V6 PEAK SUPPORT/ROBUSTNESS CHANGE 11 END
                "directional_guard_no_charge_count": sum(1 for v in directional_voltage_guard.values() if v == "no_charge"),
                "directional_guard_no_discharge_count": sum(1 for v in directional_voltage_guard.values() if v == "no_discharge"),
                "directional_guard_idle_count": sum(1 for v in directional_voltage_guard.values() if v == "idle"),
                "directional_guard_nodes": ";".join(f"{nd}:{mode}" for nd, mode in directional_voltage_guard.items()),
                # >>> CHATTER/STABILITY CHANGE 11 START
                "hard_action_guard_v_min_pu": args.guard_v_min_pu,
                "hard_action_guard_v_max_pu": args.guard_v_max_pu,
                "directional_guard_low_engage_pu": guard_low_engage_pu,
                "directional_guard_low_release_pu": guard_low_release_pu,
                "directional_guard_high_engage_pu": guard_high_engage_pu,
                "directional_guard_high_release_pu": guard_high_release_pu,
                "directional_guard_hold_steps": args.directional_guard_hold_steps,
                "battery_smoothing_weight": args.battery_smoothing_weight,
                # <<< CHATTER/STABILITY CHANGE 11 END
                # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 7 END
            } | sched_rows_all_nodes | node_log_cols | volt_log_cols)
            # <<< USER REQUEST CHANGE 23 END

            sched_rows_all_nodes = {}

            if args.verbose or (args.progress_every > 0 and
                                (step in (1, total_steps) or step % args.progress_every == 0)):
                print_step(step, day_num, k, sum(load_act_i.values()), sum(pv_act_i.values()),
                           p_bat_node[CIL_NODE], p_bat_total, sum(grid_act_i.values()),
                           soc_pred_pct[CIL_NODE], measured_soc_646, hardware_soc_646)

            # >>> USER REQUEST CHANGE 24 START: report timing overruns instead of silently falling behind
            if effective_battery_emulator != "hardware" and not args.no_wait and not args.dry_run:
                elapsed = time.time() - t0
                if elapsed > args.step_seconds:
                    print(f"  WARNING: step {step} computation/IO overrun: {elapsed:.3f}s > requested {args.step_seconds:.3f}s")
                else:
                    time.sleep(args.step_seconds - elapsed)
            # <<< USER REQUEST CHANGE 24 END



    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")
        aborted = True

    finally:
        if hardware_emu is not None:
            hardware_emu.stop()
            hardware_emu.close()
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

    # >>> V5 NODAL VOLTAGE/RAMP CHANGE 14 START: voltage diagnostics distinguish nodal/phase models
    if volt_on and not args.dry_run:
        print(f"\nVoltage model summary (predictive mode={args.voltage_cap_mode}):")
        for ph in PHASES:
            e = estimators[ph]
            lo_pu, hi_pu = phase_pu_range[ph]
            rng = f"{lo_pu:.3f}..{hi_pu:.3f} pu" if lo_pu <= hi_pu else "no valid measurements"
            phase_rho = f"rho {e.rho0:.4f}->{e.rho:.4f} V/kW ({e.n_updates} updates)" \
                if args.voltage_cap_mode in ("phase", "both") else "phase-rho inactive"
            print(f"  Phase {ph}: {phase_rho} | weakest measured range {rng} | predictive-slack steps {slack_steps[ph]} | "
                  f"measured violations {measured_violation_steps[ph]} | model-miss violations {model_miss_steps[ph]}")

        if args.voltage_cap_mode in ("nodal", "both"):
            print("  Nodal V-P estimators (only battery-controlled nodes):")
            for nd in NODE_MAP:
                if hw[nd]["cap_kwh"] <= 0:
                    continue
                e = node_estimators[nd]
                print(f"    {nd}: rho {e.rho0:.6f}->{e.rho:.6f} V/kW ({e.n_updates} updates) | "
                      f"slack steps {node_slack_steps[nd]} | model-miss violations {node_model_miss_steps[nd]}")
    # <<< V5 NODAL VOLTAGE/RAMP CHANGE 14 END

    if sched_rows:
        # >>> USER REQUEST CHANGE 26 START: ensure output directory exists
        output_dir = Path("Output")
        output_dir.mkdir(parents=True, exist_ok=True)
        sched_path = output_dir / f"mpc_feeder_schedule_{ts}.csv"
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        # <<< USER REQUEST CHANGE 26 END
        print(f"MPC schedule saved     : {sched_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()
