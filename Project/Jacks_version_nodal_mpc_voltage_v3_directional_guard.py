"""
ECE4191 Module 3 - Experiment 2
Feeder-wide MPC battery scheduling over Modbus TCP/IP.

Voltage-aware version: hard battery-hardware limits + soft (slack) voltage limits with an online-learned
voltage-vs-import slope per phase.

>>> USER REQUEST CHANGE SUMMARY (12-Oct-2026)
- Nodal battery size/power are configured per customer (defaults 10 kWh, 5 kW).
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
DEFAULT_BATTERY_CAPACITY_PER_CUSTOMER_KWH = 10.0
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

SOC_INPUT_REGISTER = 3000 # MAKE SURE WE DOUBLE CHECK THIS TO ENSURE ITS SET TO WHATEVER THE REGISTER FOR THE EXTERNAL BATTERY EMULATOR SOC IS. we might want to see if the other register works at the same time because then we could compare all 3 models!!!!
EXT_SOC_INPUT_REGISTER = 3001 # UNFINISHED

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0

DEFAULT_PLAYBACK_DAYS = 4   # Experiment 2 has a 4-day playback period


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

# Voltage limits (per unit). These are controller planning limits; the assessed hard band may be configured separately.
V_MIN_PU_DEFAULT    = 0.97 # default 0.95 # v2 val 0.97
V_MAX_PU_DEFAULT    = 1.03 # defualt 1.05 # v2 val 1.03
V_MARGIN_PU_DEFAULT = 0.005  # plan inside the requested band to leave room for model/forecast error
K_SLACK_DEFAULT     = 1.0e5     # penalty per kW of voltage-cap violation (see explanation below)
RLS_FORGET_DEFAULT  = 0.98      # forgetting factor, ~50 steps (about one day) of memory
BIAS_DECAY_DEFAULT  = 0.8       # how fast the last forecast error is assumed to fade over the horizon (0 = ignore it)

# >>> USER REQUEST CHANGE 6 START: optional reserve/support features (OFF by default)
PEAK_RESERVE_THRESHOLD_KW_DEFAULT = 1800.0
PEAK_RESERVE_TARGET_PCT_DEFAULT = 95.0
PEAK_RESERVE_LEAD_HOURS_DEFAULT = 2.0
PEAK_RESERVE_PENALTY_DEFAULT = 1.0e5      # objective penalty per kWh below reserve target

LOCAL_VOLTAGE_SUPPORT_START_PU_DEFAULT = 0.97
LOCAL_VOLTAGE_SUPPORT_PENALTY_DEFAULT = 2.0e4
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
    k_slack,
    solver,
    peak_reserve=None,
    local_voltage_deficit=None,
    local_voltage_support_penalty=0.0,
    directional_voltage_guard=None,
):
    """Solve ONE receding-horizon QP containing a separate battery, grid and SoC trajectory for every node.

    This is still nodal battery control. The nodes are solved together only because feeder-voltage constraints
    couple their decisions. With phase_caps=None and the optional features disabled, the objective/constraints
    separate mathematically into the old independent nodal MPC problems.

    peak_reserve (optional dict):
        {"active": bool, "target_state": int,
         "target_pct": float, "penalty": float}
    When active, the battery is softly required to REACH the target SoC at one forecast state
    (normally the requested lead time before an extreme predicted peak). The reserve condition is
    removed once that target time is reached/passed, so the normal MPC/voltage objective can freely
    discharge the battery afterwards. A nonnegative slack keeps this convex and prevents this optional
    reserve target from making the QP infeasible by itself.

    local_voltage_deficit (optional dict node -> positive pu deficit):
    Adds a first-action linear incentive to discharge at locally weak-voltage nodes. This is OFF unless requested.

    # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 1 START
    directional_voltage_guard (optional dict node -> mode):
        "no_charge"    -> hard first-action constraint batt[node][0] >= 0
        "no_discharge" -> hard first-action constraint batt[node][0] <= 0
    Positive battery power means discharge. Therefore, if the latest measured node voltage is below
    --v-min-pu, charging is forbidden for the next applied action; if it is above --v-max-pu,
    discharging is forbidden. These are hard affine constraints, so they preserve convexity and remain
    active even if the predictive phase-voltage caps later fall back.
    # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 1 END
    """
    nodes = list(p_load)
    n = len(p_load[nodes[0]])
    eta = np.asarray(eta, dtype=float).reshape(-1)
    if len(eta) != n:
        raise ValueError(f"MPC input length mismatch: load={n}, eta={len(eta)}")

    for nd in nodes:
        if len(np.asarray(p_load[nd]).reshape(-1)) != n or len(np.asarray(p_pv[nd]).reshape(-1)) != n:
            raise ValueError(f"MPC horizon mismatch at {nd}: expected {n} samples.")

    def build_and_solve(caps):
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

            # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 2 START
            # HARD first-action "do not worsen an existing voltage violation" guard.
            # Sign convention: batt > 0 = discharge/injection (tends to raise V),
            #                  batt < 0 = charge/extra demand (tends to lower V).
            guard_mode = None if not directional_voltage_guard else directional_voltage_guard.get(nd)
            if guard_mode == "no_charge":
                cons += [batt[nd][0] >= 0.0]
            elif guard_mode == "no_discharge":
                cons += [batt[nd][0] <= 0.0]
            # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 2 END

            if local_voltage_deficit and h["cap_kwh"] > 0:
                deficit = max(0.0, float(local_voltage_deficit.get(nd, 0.0)))
                if deficit > 0.0:
                    cost += -float(local_voltage_support_penalty) * deficit * batt[nd][0]

            # >>> PEAK RESERVE RELEASE CHANGE 1 START
            # Softly require the battery to REACH the reserve target at ONE state only.
            # Do not hold it above the target all the way to the peak. Once this target state
            # has passed, peak_reserve["active"] becomes False in the main loop and the
            # battery is fully released back to the normal MPC/voltage objective.
            if peak_reserve and peak_reserve.get("active") and h["cap_kwh"] > 0:
                target_state = int(np.clip(peak_reserve["target_state"], 1, n))
                target_kwh = h["cap_kwh"] * float(peak_reserve["target_pct"]) / 100.0
                s = cp.Variable(nonneg=True)
                cons += [soc[nd][target_state] + s >= target_kwh]
                cost += float(peak_reserve["penalty"]) * s
                reserve_slack[nd] = s
            # <<< PEAK RESERVE RELEASE CHANGE 1 END

        slack = {}
        if caps:
            for ph, (c_hi, c_lo) in caps.items():
                members = [nd for nd in nodes if node_phase(nd) == ph]
                p_phase = sum(grid[nd] for nd in members)
                s_hi = cp.Variable(n, nonneg=True)
                s_lo = cp.Variable(n, nonneg=True)
                cons += [p_phase <= c_hi + s_hi,
                         p_phase >= c_lo - s_lo]
                cost += k_slack * (cp.sum(s_hi) + cp.sum(s_lo))
                slack[ph] = (s_hi, s_lo)

        problem = cp.Problem(cp.Minimize(cost), cons)
        kwargs = {"max_iter": 50000} if str(solver).upper() == "OSQP" else {}
        try:
            problem.solve(solver=getattr(cp, solver), verbose=False, **kwargs)
        except Exception as e:
            return {"status": f"solver_error: {e}"}, None

        ok = problem.status in ("optimal", "optimal_inaccurate") and all(
            batt[nd].value is not None for nd in nodes
        )
        if not ok:
            return {"status": str(problem.status)}, None

        res = {
            "status": str(problem.status),
            "obj": float(problem.value),
            "batt": {nd: np.asarray(batt[nd].value).flatten() for nd in nodes},
            "grid": {nd: np.asarray(grid[nd].value).flatten() for nd in nodes},
            "soc": {nd: np.asarray(soc[nd].value).flatten() for nd in nodes},
            "slack": {ph: (np.maximum(np.asarray(s[0].value).flatten(), 0.0),
                            np.maximum(np.asarray(s[1].value).flatten(), 0.0)) for ph, s in slack.items()},
            "reserve_slack": {nd: np.maximum(np.asarray(s.value).flatten(), 0.0)
                              for nd, s in reserve_slack.items()},
        }
        return res, True

    res, ok = build_and_solve(phase_caps)
    voltage_fallback = False
    voltage_cap_failure_status = ""
    if ok is None and phase_caps:
        # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 3 START
        # The phase-voltage caps use nonnegative slack, so they should not by themselves make an
        # otherwise-feasible MPC mathematically infeasible. With very large --k-slack values, OSQP can
        # instead become poorly conditioned / fail to converge. Preserve the failed status for the CSV
        # and retry without ONLY the predictive phase caps. The hard directional guard is part of the
        # nodal constraints above and therefore remains active in this retry.
        voltage_cap_failure_status = str(res.get("status", "unknown"))
        print(f"  WARNING: predictive voltage-cap solve failed ({voltage_cap_failure_status}); "
              "re-solving without the predictive phase caps for this step. "
              "Hard directional voltage guards remain active.")
        voltage_fallback = True
        res, ok = build_and_solve(None)
        # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 3 END

    if ok is None:
        return {"status": res["status"], "obj": float("nan"), "batt": None, "grid": None,
                "soc": None, "slack": {}, "reserve_slack": {}, "voltage_caps_used": False,
                "voltage_fallback": voltage_fallback,
                "voltage_cap_failure_status": voltage_cap_failure_status}

    res["voltage_caps_used"] = bool(phase_caps) and not voltage_fallback
    res["voltage_fallback"] = voltage_fallback
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
                        help="Battery energy capacity per customer in kWh (default 10).")
    parser.add_argument("--battery-power-per-customer-kw", type=float,
                        default=DEFAULT_BATTERY_POWER_PER_CUSTOMER_KW,
                        help="Charge/discharge power limit per customer in kW (default 5).")
    parser.add_argument("--initial-soc-pct", type=float, default=DEFAULT_INITIAL_SOC_PCT,
                        help="Initial SoC for every nodal battery in percent (default 50).")
    # <<< USER REQUEST CHANGE 8 END
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
    # >>> USER REQUEST CHANGE 27 START: clarify that this switch disables only the Node-646 SoC feedback
    parser.add_argument("--no-soc-feedback", "--no-measurements", dest="no_soc_feedback", action="store_true",
                        help="Do not use HIL Node-646 SoC feedback; propagate Node-646 SoC with the MPC model instead. "
                             "Useful for hypothetical battery-capacity tests unless the HIL battery capacity is changed too.")
    # <<< USER REQUEST CHANGE 27 END
    parser.add_argument("--measurement-delay", type=float, default=0.2,
                        help="Seconds to wait after a write before reading SoC.")
    parser.add_argument("--progress-every", type=int, default=1,
                        help="Print one row every N steps (0 = summary only).")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full dry-run Modbus payloads.")
    # >>> VOLTAGE CHANGE 2a START: command-line options <<<
    parser.add_argument("--no-voltage-constraint", action="store_true",
                        help="Switch the predictive phase-voltage limits off (QP then behaves like uncoupled nodal MPC unless other guards are enabled).")
    # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 4 START
    parser.add_argument("--no-directional-voltage-guard", action="store_true",
                        help="Disable the default hard first-action guard: below --v-min-pu a battery may not charge; "
                             "above --v-max-pu it may not discharge. The guard is ON by default.")
    # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 4 END
    parser.add_argument("--v-min-pu", type=float, default=V_MIN_PU_DEFAULT, help="Lower voltage limit (per unit).")
    parser.add_argument("--v-max-pu", type=float, default=V_MAX_PU_DEFAULT, help="Upper voltage limit (per unit).")
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
                        help="How many hours before the forecast peak the reserve target should start.")
    parser.add_argument("--peak-reserve-penalty", type=float, default=PEAK_RESERVE_PENALTY_DEFAULT,
                        help="Soft-constraint penalty per kWh below the peak-reserve target.")
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
    if not (0.0 <= args.peak_reserve_target_pct <= 100.0):
        raise ValueError("--peak-reserve-target-pct must lie in [0, 100]")
    if args.peak_reserve_lead_hours < 0:
        raise ValueError("--peak-reserve-lead-hours must be >= 0")
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
    print("ECE4191 Module 3  |  Project - Extension 1,3,5")
    print("=" * 78)
    # >>> VHIL CHANGE 3b START <<<
    print(f"  HIL target      : " + ("Typhoon Python API (SCADA inputs)" if args.backend == "api" else f"{args.ip}:{args.port}"))
    # <<< VHIL CHANGE 3b END
    print(f"  Forecast mode   : {forecast_mode_name}")
    print(f"  Actual CSV      : {act_path.name}  (per-node HIL playback)")
    print(f"  Battery/customer: {args.battery_capacity_per_customer_kwh:g} kWh, "
          f"+/-{args.battery_power_per_customer_kw:g} kW")
    print(f"  Initial SoC     : {args.initial_soc_pct:.1f}%")
    print(f"  Objective weight: w = {args.weight}")
    # >>> VOLTAGE CHANGE 2b START <<<
    if args.no_voltage_constraint:
        print("  Voltage limits  : OFF")
    else:
        print(f"  Voltage limits  : {args.v_min_pu:.3f}-{args.v_max_pu:.3f} pu (margin {args.v_margin_pu:.3f}), "
              f"soft with K = {args.k_slack:g}, RLS forgetting {args.rls_forget}, reference={args.voltage_reference}")
    print(f"  SoC window      : {args.soc_min_pct:.1f}-{args.soc_max_pct:.1f} %")
    # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 5 START
    if args.no_directional_voltage_guard:
        print("  Direction guard : OFF")
    else:
        print(f"  Direction guard : ON (hard first action: V<{args.v_min_pu:.3f} => no charge; "
              f"V>{args.v_max_pu:.3f} => no discharge)")
    # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 5 END
    if args.peak_reserve:
        # >>> PEAK RESERVE RELEASE CHANGE 2 START
        print(f"  Peak reserve    : ON, target >= {args.peak_reserve_target_pct:.1f}% at "
              f"{args.peak_reserve_lead_hours:g} h before forecast net-load peak; released afterwards "
              f"when peak >= {args.peak_reserve_threshold_kw:g} kW")
        # <<< PEAK RESERVE RELEASE CHANGE 2 END
    else:
        print("  Peak reserve    : OFF")
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

    # >>> USER REQUEST CHANGE 14 START: consistent nodal SoC initialisation + initial feedback/voltage snapshot
    log_enabled = not args.no_soc_feedback and not args.dry_run
    cil_capacity_kwh = N_CUSTOMERS[CIL_NODE] * args.battery_capacity_per_customer_kwh

    if args.backend == "api":
        soc_logger = ApiSocLogger(conn, log_enabled, init_soc_pct=args.initial_soc_pct,
                                  cil_capacity_kwh=cil_capacity_kwh)
    else:
        soc_logger = SocLogger(conn, log_enabled)
    soc_logger.start()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    aborted = False
    soc_pred = {nd: (args.initial_soc_pct / 100.0) * N_CUSTOMERS[nd] * args.battery_capacity_per_customer_kwh
                for nd in NODE_MAP}
    soc_measured_646_CIL_kwh = soc_pred[CIL_NODE]

    initial_soc_measured_pct = None
    cil_soc_feedback_active = False
    if log_enabled:
        initial_soc_measured_pct = soc_logger.log_step()
        if initial_soc_measured_pct is not None:
            soc_measured_646_CIL_kwh = float(initial_soc_measured_pct) / 100.0 * cil_capacity_kwh
            soc_pred[CIL_NODE] = soc_measured_646_CIL_kwh
            cil_soc_feedback_active = True
            print(f"  Initial Node 646 measured SoC used by MPC: {float(initial_soc_measured_pct):.3f}%")
    if args.no_soc_feedback:
        print("  Node 646 SoC feedback: OFF; MPC-predicted SoC will be used.")
    elif abs(args.battery_capacity_per_customer_kwh - 10.0) > 1e-9 and args.backend == "modbus":
        print("  WARNING: battery capacity per customer differs from the original 10 kWh HIL model. "
              "Unless you also changed the HIL battery capacity, its measured SoC is not physically consistent "
              "with this controller capacity. Use --no-soc-feedback for a controller-only hypothetical capacity test.")

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
    eta_win_nodes = {}
    volt_log_cols = {}
    phase_caps = None
    slack_steps = {ph: 0 for ph in PHASES}
    measured_violation_steps = {ph: 0 for ph in PHASES}
    model_miss_steps = {ph: 0 for ph in PHASES}
    phase_pu_range = {ph: [float("inf"), float("-inf")] for ph in PHASES}

    voltage_fallback_warned = refresh_voltage_snapshot(soc_logger, args.dry_run, node_voltage, node_v_valid,
                                                       voltage_fallback_warned)
    if volt_on and not args.dry_run:
        for ph in PHASES:
            control_pu, min_pu, min_node, avg_pu = phase_voltage_measurement(
                ph, node_voltage, node_v_valid, args.voltage_reference)
            if control_pu is not None:
                estimators[ph].update(control_pu * NOMINAL_VOLTAGE, 0.0)
        print(f"  Voltage model initialised from the settled HIL voltages (reference={args.voltage_reference}).")
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

            # >>> USER REQUEST CHANGE 16 START: phase voltage caps use the latest weakest/selected phase measurement
            phase_caps = None
            if volt_on:
                v_lo_equiv = (args.v_min_pu + args.v_margin_pu) * NOMINAL_VOLTAGE
                v_hi_equiv = (args.v_max_pu - args.v_margin_pu) * NOMINAL_VOLTAGE
                phase_caps = {}
                for ph in PHASES:
                    c = estimators[ph].caps(N_STEPS, v_lo_equiv, v_hi_equiv,
                                            phase_bias_kw[ph], args.bias_decay)
                    if c is not None:
                        phase_caps[ph] = c
            # <<< USER REQUEST CHANGE 16 END

            # >>> USER REQUEST CHANGE 17 START: optional soft pre-peak SoC reserve (convex)
            forecast_total_net_kw = np.zeros(N_STEPS, dtype=float)
            for nd in NODE_MAP:
                forecast_total_net_kw += p_load_win[nd] - p_pv_win[nd]
            forecast_peak_index = int(np.argmax(forecast_total_net_kw))
            forecast_peak_kw = float(forecast_total_net_kw[forecast_peak_index])
            peak_lead_steps = max(0, int(round(args.peak_reserve_lead_hours / DELTA_HOURS)))

            # >>> PEAK RESERVE RELEASE CHANGE 3 START
            # Power forecast index p refers to interval p. soc[j] is the state at the
            # boundary before interval j. Therefore p - lead_steps is the SoC state at
            # the requested lead time before the predicted peak interval.
            #
            # IMPORTANT: do NOT clamp this to 1. If it is <= 0, the requested reserve
            # target time has already been reached/passed. In that case reserve_active
            # becomes False and the battery is released for normal MPC/voltage support.
            reserve_target_state = forecast_peak_index - peak_lead_steps
            reserve_active = bool(
                args.peak_reserve
                and forecast_peak_kw >= args.peak_reserve_threshold_kw
                and reserve_target_state >= 1
            )
            reserve_released = bool(
                args.peak_reserve
                and forecast_peak_kw >= args.peak_reserve_threshold_kw
                and reserve_target_state <= 0
            )

            peak_reserve_cfg = {
                "active": reserve_active,
                "target_state": reserve_target_state,
                "target_pct": args.peak_reserve_target_pct,
                "penalty": args.peak_reserve_penalty,
            }
            # <<< PEAK RESERVE RELEASE CHANGE 3 END
            # <<< USER REQUEST CHANGE 17 END

            # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 6 START
            # Use the latest REAL measured nodal voltages (the snapshot from the end of the previous
            # control interval; before step 1 it is the settled pre-run snapshot). This guard is deliberately
            # independent of the learned phase model. It does not try to predict the next voltage; it simply
            # prevents the next battery action from pushing an already-violating node in the wrong direction.
            directional_voltage_guard = {}
            if not args.no_directional_voltage_guard:
                for nd in NODE_MAP:
                    if node_v_valid.get(nd, False) and hw[nd]["cap_kwh"] > 0:
                        vpu_now = node_voltage_pu(nd, node_voltage[nd])
                        if vpu_now < args.v_min_pu:
                            directional_voltage_guard[nd] = "no_charge"
                        elif vpu_now > args.v_max_pu:
                            directional_voltage_guard[nd] = "no_discharge"
            # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 6 END

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
            fb_res = solve_joint_nodal_mpc_qp(
                p_load_win, p_pv_win, eta_win, args.weight, hw, soc0_all,
                phase_caps or None, args.k_slack, args.solver,
                peak_reserve=peak_reserve_cfg,
                local_voltage_deficit=local_voltage_deficit,
                local_voltage_support_penalty=args.local_voltage_support_penalty,
                directional_voltage_guard=directional_voltage_guard)
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


            # >>> VHIL CHANGE 6 START: write through the API (SCADA inputs) or Modbus, as chosen <<<
            if args.backend == "api":
                conn.write_feeder(node_data, i, pbat_nodes)
            else:
                payload = build_feeder_payload(node_data, i, pbat_nodes)
                modbus_write_feeder(conn, payload, args.dry_run, args.verbose)
            # <<< VHIL CHANGE 6 END


            if not args.no_wait and args.measurement_delay > 0 and not args.dry_run:
                time.sleep(args.measurement_delay)

            if not args.dry_run:
                measured_soc_646 = soc_logger.log_step()
            else:
                measured_soc_646 = None

            # >>> USER REQUEST CHANGE 20 START: measured SoC uses the SAME per-customer capacity as the MPC
            if measured_soc_646 is not None and not args.no_soc_feedback and not args.dry_run:
                soc_measured_646_CIL_kwh = float(measured_soc_646) / 100.0 * cil_capacity_kwh
                cil_soc_feedback_active = True
            else:
                soc_measured_646_CIL_kwh = soc_pred[CIL_NODE]
                cil_soc_feedback_active = False
            # <<< USER REQUEST CHANGE 20 END

            # >>> USER REQUEST CHANGE 21 START: robust post-action voltage feedback
            voltage_fallback_warned = refresh_voltage_snapshot(
                soc_logger, args.dry_run, node_voltage, node_v_valid, voltage_fallback_warned)
            # <<< USER REQUEST CHANGE 21 END

            # >>> USER REQUEST CHANGE 22 START: control/log the weakest measured voltage, not only the phase average
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
                    estimators[ph].update(control_pu * NOMINAL_VOLTAGE, p_ph)
                    phase_pu_range[ph][0] = min(phase_pu_range[ph][0], min_pu)
                    phase_pu_range[ph][1] = max(phase_pu_range[ph][1], min_pu)

                sl = fb_res["slack"].get(ph) if fb_res.get("slack") else None
                slack0 = 0.0 if sl is None else float(sl[0][0] + sl[1][0])
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
                    f"phase_{ph}_slack_kw": round(slack0, 4),
                    f"phase_{ph}_measured_violation": int(measured_violation),
                }
            # <<< USER REQUEST CHANGE 22 END

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
                f"{CIL_NODE}_soc_measured_pct": "" if measured_soc_646 is None else round(float(measured_soc_646), 4),
                f"{CIL_NODE}_mpc_status": status[CIL_NODE],
                f"{CIL_NODE}_voltage": node_voltage[CIL_NODE],
                f"{CIL_NODE}_directional_voltage_guard": directional_voltage_guard.get(CIL_NODE, ""),
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
                "feeder_baseline_grid_kw": round(total_load_i - total_pv_i, 4),
                "feeder_grid_with_batteries_kw": round(total_load_i - total_pv_i - p_bat_total, 4),
                "forecast_peak_net_kw": round(forecast_peak_kw, 4),
                "forecast_peak_steps_ahead": forecast_peak_index,
                # >>> PEAK RESERVE RELEASE CHANGE 4 START
                "peak_reserve_active": int(peak_reserve_cfg["active"]),
                "peak_reserve_released": int(reserve_released),
                "peak_reserve_target_steps_ahead": reserve_target_state,
                "peak_reserve_target_pct": args.peak_reserve_target_pct if peak_reserve_cfg["active"] else "",
                "peak_reserve_total_slack_kwh": round(reserve_slack_total_kwh, 4),
                # <<< PEAK RESERVE RELEASE CHANGE 4 END
                "voltage_caps_used": int(bool(fb_res.get("voltage_caps_used", False))),
                "voltage_fallback": int(bool(fb_res.get("voltage_fallback", False))),
                # >>> DIRECTIONAL VOLTAGE GUARD CHANGE 7 START
                "voltage_cap_failure_status": fb_res.get("voltage_cap_failure_status", ""),
                "directional_guard_no_charge_count": sum(1 for v in directional_voltage_guard.values() if v == "no_charge"),
                "directional_guard_no_discharge_count": sum(1 for v in directional_voltage_guard.values() if v == "no_discharge"),
                "directional_guard_nodes": ";".join(f"{nd}:{mode}" for nd, mode in directional_voltage_guard.items()),
                # <<< DIRECTIONAL VOLTAGE GUARD CHANGE 7 END
            } | sched_rows_all_nodes | volt_log_cols)
            # <<< USER REQUEST CHANGE 23 END

            sched_rows_all_nodes = {}

            if args.verbose or (args.progress_every > 0 and
                                (step in (1, total_steps) or step % args.progress_every == 0)):
                print_step(step, day_num, k, sum(load_act_i.values()), sum(pv_act_i.values()), p_bat_node[CIL_NODE],
                           sum(grid_act_i.values()), soc_pred_pct[CIL_NODE], measured_soc_646)

            # >>> USER REQUEST CHANGE 24 START: report timing overruns instead of silently falling behind
            if not args.no_wait and not args.dry_run:
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

    # >>> USER REQUEST CHANGE 25 START: voltage diagnostics distinguish slack from model miss
    if volt_on and not args.dry_run:
        print("\nVoltage model summary (rho = equivalent V drop per kW of extra phase net import):")
        for ph in PHASES:
            e = estimators[ph]
            lo_pu, hi_pu = phase_pu_range[ph]
            rng = f"{lo_pu:.3f}..{hi_pu:.3f} pu" if lo_pu <= hi_pu else "no valid measurements"
            print(f"  Phase {ph}: rho {e.rho0:.4f} -> {e.rho:.4f} V/kW ({e.n_updates} updates) | "
                  f"weakest measured range {rng} | QP-slack steps {slack_steps[ph]} | "
                  f"measured violations {measured_violation_steps[ph]} | model-miss violations {model_miss_steps[ph]}")
    # <<< USER REQUEST CHANGE 25 END

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