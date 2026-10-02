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


HARDWARE-SYNCHRONISED EXTENSION MODE (this file):
    * Runs only a selected interval of the E3 dataset (default 38.0 h to 47.0 h).
    * Holds each 30-minute data step for 500 real seconds by default.
    * Uses the measured battery-emulator SoC as the MPC feedback state.
    * Converts the MPC kW request to Cxxx/Dxxx using the measured emulator rate
      (~16 raw SoC counts/s at command 255), rather than simply mapping 510 kW to 255.
    * Continuously records the emulator's ~1 Hz raw 00000..65500 SoC stream while
      each step is held. The HIL SoC is still read and logged for comparison.

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

import re

try:
    import serial
except ImportError:
    print("ERROR: pyserial not found. Install it with:")
    print("  sudo apt install python3-serial")
    print("or:")
    print("  pip install pyserial --break-system-packages")
    sys.exit(1)

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
STEP_SECONDS = 500.0

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

# QREF_646_KVAR = 132
# QREF_MAP = {node: 0.0 for node in NODE_MAP}
# QREF_MAP[CIL_NODE] = QREF_646_KVAR

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

# Node-646-specific battery parameters (from Section 7's guided toy walkthrough).
# NOTE: these are independent of the aggregate 1330-customer feeder battery used
# in Experiments 1 and 2.
NODE646_CAPACITY_KWH  = 1020.0
NODE646_BATT_POWER_KW = 510.0
NODE646_INITIAL_SOC_KWH = 510.0   # 50%

DEFAULT_WEIGHT = 1

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

# --- Physical battery emulator serial interface ------------------------------
DEFAULT_EMULATOR_PORT = "/dev/serial/by-id/usb-FTDI_TTL232R_FTEAE3LA-if00-port0"
EMULATOR_BAUD = 9600
EMULATOR_SOC_MAX_RAW = 65500
EMULATOR_READ_WAIT_S = 1.2   # emulator broadcasts approximately once per second
EMULATOR_COMMAND_DEADBAND_KW = 0.5

# Hardware calibration measured on the laboratory battery emulator.
# D255 ~= -16 raw SoC counts/s, C255 ~= +16 raw SoC counts/s.
EMULATOR_DISCHARGE_MAX_RAW_PER_S = 16.0
EMULATOR_CHARGE_MAX_RAW_PER_S = 16.0

# Selected E3 validation window.  Dataset time is still 0.5 h per data step.
DEFAULT_SYNC_START_HOUR = 38.0
DEFAULT_SYNC_END_HOUR = 47.0
DEFAULT_EMULATOR_SAMPLE_PERIOD_S = 1.0
DEFAULT_HOLD_PROGRESS_S = 30.0
DEFAULT_EMULATOR_STALE_LIMIT_S = 3.0


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
        #soc[-1] == soc0_kwh,   # terminal SoC(t+n|t) = SoC(t|t), Eq. (12)
        grid <=3000, 
        grid >=-1500,

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


class BatteryEmulatorReader:
    """Read the physical battery emulator's unsolicited ASCII SoC stream.

    The emulator broadcasts a raw SoC value from 00000 to 65500 at about 1 Hz
    over 9600-8N1 serial. This reader is deliberately DIAGNOSTIC ONLY: it does
    not alter the MPC state or battery command.

    The parser accepts both delimited packets (for example ``32768\r\n``) and
    back-to-back fixed-width five-digit packets.
    """

    def __init__(self, port: str):
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
        self.latest_raw: int | None = None
        self.latest_rx_monotonic: float | None = None
        self.ser.reset_input_buffer()
        print(f"  Battery emulator serial connected: {port}")

    def _consume_available(self) -> bool:
        """Drain available bytes. Return True if at least one NEW valid SoC arrived."""
        got_new = False

        waiting = self.ser.in_waiting
        if waiting > 0:
            data = self.ser.read(waiting)
        else:
            # Short blocking read helps catch a packet that is just about to arrive.
            data = self.ser.read(1)

        if data:
            self.buffer += data.decode("ascii", errors="ignore")

        # Five ASCII digits encode one raw SoC sample.  Values >65500 are rejected.
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

            # Remove complete parsed groups but retain any partial trailing digits.
            self.buffer = self.buffer[last_end:]

        # Prevent unexpected serial noise from growing the buffer forever.
        if len(self.buffer) > 100:
            self.buffer = self.buffer[-20:]

        return got_new

    def read_latest(self, max_wait_s: float = EMULATOR_READ_WAIT_S):
        """Return (raw, pct, age_s, fresh).

        Wait up to max_wait_s for a fresh broadcast. If no new packet arrives,
        return the most recently received value and mark fresh=False.
        """
        deadline = time.monotonic() + max(0.0, max_wait_s)
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

    def power_to_sync_command(self, p_bat_kw: float, capacity_kwh: float,
                              step_seconds: float, charge_max_raw_per_s: float,
                              discharge_max_raw_per_s: float) -> dict:
        """Convert one MPC kW request into a time-scaled Cxxx/Dxxx command.

        The MPC energy equation represents a 30-minute interval:
            delta_soc_kWh = -Pbat * DELTA_HOURS

        The hardware emulator changes raw SoC at a measured rate proportional
        to command code.  Therefore the code is chosen so that, over the real
        wall-clock hold time ``step_seconds``, the emulator should undergo the
        same SoC change as the ideal 1020 kWh model does over 0.5 simulated h.

        +Pbat = discharge -> Dxxx -> raw SoC decreases
        -Pbat = charge    -> Cxxx -> raw SoC increases
        """
        if capacity_kwh <= 0:
            raise ValueError("capacity_kwh must be > 0")
        if step_seconds <= 0:
            raise ValueError("step_seconds must be > 0")

        p = float(p_bat_kw)
        if abs(p) <= EMULATOR_COMMAND_DEADBAND_KW:
            return {
                "command": "D000", "code": 0, "saturated": False,
                "target_delta_raw": 0.0, "required_rate_raw_per_s": 0.0,
                "max_rate_raw_per_s": (discharge_max_raw_per_s if p >= 0
                                        else charge_max_raw_per_s),
                "equivalent_power_kw": 0.0,
            }

        discharge = p > 0
        max_rate = (discharge_max_raw_per_s if discharge
                    else charge_max_raw_per_s)
        if max_rate <= 0:
            raise ValueError("Emulator calibrated max rate must be > 0")

        target_delta_raw = (
            abs(p) * DELTA_HOURS / capacity_kwh * EMULATOR_SOC_MAX_RAW
        )
        required_rate = target_delta_raw / step_seconds
        code_float = 255.0 * required_rate / max_rate
        saturated = code_float > 255.0
        code = int(round(min(255.0, max(0.0, code_float))))

        prefix = "D" if discharge else "C"
        command = f"{prefix}{code:03d}"

        # The ideal battery power represented by the rounded hardware command
        # over this wall-clock step. Useful for quantifying mapping error.
        achieved_raw_delta = max_rate * (code / 255.0) * step_seconds
        equiv_mag_kw = (
            achieved_raw_delta / EMULATOR_SOC_MAX_RAW
            * capacity_kwh / DELTA_HOURS
        )
        equivalent_power_kw = equiv_mag_kw if discharge else -equiv_mag_kw

        return {
            "command": command,
            "code": code,
            "saturated": saturated,
            "target_delta_raw": target_delta_raw,
            "required_rate_raw_per_s": required_rate,
            "max_rate_raw_per_s": max_rate,
            "equivalent_power_kw": equivalent_power_kw,
        }

    def send_sync_power_command(self, p_bat_kw: float, capacity_kwh: float,
                                step_seconds: float, charge_max_raw_per_s: float,
                                discharge_max_raw_per_s: float) -> dict:
        """Send a time-scaled Cxxx/Dxxx command and return mapping metadata."""
        info = self.power_to_sync_command(
            p_bat_kw=p_bat_kw,
            capacity_kwh=capacity_kwh,
            step_seconds=step_seconds,
            charge_max_raw_per_s=charge_max_raw_per_s,
            discharge_max_raw_per_s=discharge_max_raw_per_s,
        )
        self.ser.write(info["command"].encode("ascii"))
        self.ser.flush()
        return info

    def stop(self) -> None:
        """Command zero battery power. Safe to call during cleanup."""
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


# ============================================================
# 5. Hardware-sync helpers + console output
# ============================================================

def _hour_to_step_index(hour: float) -> int:
    """Convert a simulation-hour boundary to the corresponding 0-based row index."""
    idx = int(round(hour / DELTA_HOURS))
    if abs(idx * DELTA_HOURS - hour) > 1e-9:
        raise ValueError(
            f"Simulation hour {hour} is not aligned to the {DELTA_HOURS:.1f} h data grid."
        )
    return idx


def emulator_representable_power_kw(capacity_kwh: float, step_seconds: float,
                                     max_rate_raw_per_s: float) -> float:
    """Maximum ideal-model kW that command 255 can reproduce in one held step."""
    return (
        max_rate_raw_per_s * step_seconds / EMULATOR_SOC_MAX_RAW
        * capacity_kwh / DELTA_HOURS
    )


def hold_step_and_log_emulator(emu, duration_s: float, emu_wait_s: float,
                               sample_rows: list[dict], step_context: dict,
                               progress_every_s: float):
    """Hold one operating point while recording fresh emulator SoC packets.

    Returns the most recent (raw, pct, age_s, fresh_seen_during_hold).
    The emulator broadcasts roughly once per second; every fresh packet is saved
    to the high-rate sample CSV so the physical trajectory is not lost during a
    long 500 s controller step.
    """
    start = time.monotonic()
    next_progress = progress_every_s if progress_every_s > 0 else float("inf")
    latest_raw = latest_pct = latest_age = None
    any_fresh = False

    while True:
        elapsed = time.monotonic() - start
        remaining = duration_s - elapsed
        if remaining <= 0:
            break

        if emu is not None:
            wait_now = min(max(0.05, emu_wait_s), max(0.05, remaining))
            raw, pct, age_s, fresh = emu.read_latest(wait_now)
            if raw is not None:
                latest_raw, latest_pct, latest_age = raw, pct, age_s
            if fresh and raw is not None:
                any_fresh = True
                sample_rows.append({
                    **step_context,
                    "wall_elapsed_in_step_s": round(time.monotonic() - start, 4),
                    "emulator_soc_raw": int(raw),
                    "emulator_soc_pct": round(float(pct), 6),
                })
        else:
            time.sleep(min(1.0, remaining))

        elapsed = time.monotonic() - start
        if elapsed >= next_progress:
            if latest_raw is None:
                emu_text = "EMU no sample"
            else:
                emu_text = f"EMU {latest_raw:05d} ({latest_pct:.3f}%)"
            print(f"    hold {min(elapsed, duration_s):6.1f}/{duration_s:.1f} s  |  {emu_text}")
            next_progress += progress_every_s

    # One short final drain catches a packet arriving right at the boundary.
    if emu is not None:
        raw, pct, age_s, fresh = emu.read_latest(min(0.25, emu_wait_s))
        if raw is not None:
            latest_raw, latest_pct, latest_age = raw, pct, age_s
        if fresh and raw is not None:
            any_fresh = True
            sample_rows.append({
                **step_context,
                "wall_elapsed_in_step_s": round(time.monotonic() - start, 4),
                "emulator_soc_raw": int(raw),
                "emulator_soc_pct": round(float(pct), 6),
            })

    return latest_raw, latest_pct, latest_age, any_fresh


_HDR = (f"{'Run':>3} {'GStep':>5} {'SimHr':>6} {'Day':>3} {'k':>3} "
        f"{'BattkW':>8} {'Action':>10} {'EMUcmd':>6} {'EMUraw':>7} "
        f"{'EMU%':>7} {'HIL%':>7} {'Pred%':>7} {'Errpp':>7} {'Sat':>3}")


def print_step(run_step, global_step, sim_hour, day, k, batt, emu_cmd,
               emu_raw, emu_pct, hil_pct, pred_pct, err_pp, saturated):
    emu_raw_s = f"{emu_raw:7d}" if emu_raw is not None else f"{'-':>7}"
    emu_pct_s = f"{emu_pct:7.2f}" if emu_pct is not None else f"{'-':>7}"
    hil_s = f"{hil_pct:7.2f}" if hil_pct is not None else f"{'-':>7}"
    err_s = f"{err_pp:7.3f}" if err_pp is not None else f"{'-':>7}"
    print(f"{run_step:3d} {global_step:5d} {sim_hour:6.1f} {day:3d} {k:3d} "
          f"{batt:8.2f} {_action(batt):>10} {emu_cmd:>6} {emu_raw_s} "
          f"{emu_pct_s} {hil_s} {pred_pct:7.2f} {err_s} "
          f"{'YES' if saturated else 'no ':>3}")


# ============================================================
# 6. Main -- hardware-synchronised Node 646 MPC
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "ECE4191 E3 hardware-synchronised Node 646 MPC: selected-window "
            "playback with physical battery-emulator SoC feedback"
        )
    )
    parser.add_argument("--forecast", default=None,
                        help="Node-646-specific day-ahead forecast CSV. If omitted, "
                             "forecast = actual Node 646 data.")
    parser.add_argument("--actual", default="Code_and_data/agg_jan2013_students.csv",
                        help="Per-node actual load/PV CSV (fed to the whole feeder).")
    parser.add_argument("--start-hour", type=float, default=DEFAULT_SYNC_START_HOUR,
                        help=f"First simulated hour to execute (default {DEFAULT_SYNC_START_HOUR}).")
    parser.add_argument("--end-hour", type=float, default=DEFAULT_SYNC_END_HOUR,
                        help=f"End simulated hour, exclusive (default {DEFAULT_SYNC_END_HOUR}).")
    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS,
                        help=f"Real seconds used for each 30-min data step (default {STEP_SECONDS:.0f}).")
    parser.add_argument("--feedback-source", choices=("emulator", "hil"), default="emulator",
                        help="SoC used to seed each new MPC solve (default: emulator).")
    parser.add_argument("--weight", type=float, default=DEFAULT_WEIGHT)
    parser.add_argument("--node646-capacity", type=float, default=NODE646_CAPACITY_KWH)
    parser.add_argument("--node646-batt-power", type=float, default=NODE646_BATT_POWER_KW)
    parser.add_argument("--node646-initial-soc", type=float, default=NODE646_INITIAL_SOC_KWH,
                        help="Fallback model/HIL initial SoC in kWh.")
    parser.add_argument("--solver", default="OSQP")
    parser.add_argument("--ip", default=DEFAULT_HIL_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_HIL_PORT)
    parser.add_argument("--emu-port", default=DEFAULT_EMULATOR_PORT)
    parser.add_argument("--emu-wait", type=float, default=EMULATOR_READ_WAIT_S)
    parser.add_argument("--emu-charge-rate", type=float,
                        default=EMULATOR_CHARGE_MAX_RAW_PER_S,
                        help="Measured C255 raw SoC rate in counts/s.")
    parser.add_argument("--emu-discharge-rate", type=float,
                        default=EMULATOR_DISCHARGE_MAX_RAW_PER_S,
                        help="Measured D255 raw SoC rate magnitude in counts/s.")
    parser.add_argument("--emu-stale-limit", type=float,
                        default=DEFAULT_EMULATOR_STALE_LIMIT_S,
                        help="Abort emulator-feedback mode if latest SoC sample is older than this.")
    parser.add_argument("--hold-progress-seconds", type=float,
                        default=DEFAULT_HOLD_PROGRESS_S,
                        help="Print a hold-progress line this often; 0 disables it.")
    parser.add_argument("--target-start-soc-pct", type=float, default=None,
                        help="Optional expected physical-emulator SoC at the selected window start.")
    parser.add_argument("--start-soc-tolerance-pct", type=float, default=1.0,
                        help="Allowed error around --target-start-soc-pct (percentage points).")
    parser.add_argument("--command-emulator", action="store_true",
                        help="Required for hardware-sync mode: send time-scaled Cxxx/Dxxx commands.")
    parser.add_argument("--no-emulator", action="store_true",
                        help="Disable the physical emulator (diagnostic/HIL-only use).")
    parser.add_argument("--no-wait", action="store_true",
                        help="Skip wall-clock holds. For dry/logic testing only; not a sync experiment.")
    parser.add_argument("--no-prompt", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-final", action="store_true")
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.step_seconds <= 0:
        raise ValueError("--step-seconds must be > 0")
    if args.end_hour <= args.start_hour:
        raise ValueError("--end-hour must be greater than --start-hour")
    if args.feedback_source == "emulator" and args.no_emulator:
        raise ValueError("--feedback-source emulator cannot be used with --no-emulator")
    if (not args.dry_run and args.feedback_source == "emulator"
            and not args.command_emulator):
        raise ValueError(
            "Hardware-sync mode uses the emulator as the MPC state. "
            "Run with --command-emulator, or explicitly use --feedback-source hil."
        )

    start_idx = _hour_to_step_index(args.start_hour)
    end_idx = _hour_to_step_index(args.end_hour)
    selected_steps = end_idx - start_idx
    effective_feedback = "model" if args.dry_run else args.feedback_source

    # ── Connections ──────────────────────────────────────────────────────────
    conn = None
    if not args.dry_run:
        conn = ModbusConnection(args.ip, args.port)
        print(f"\nConnecting to HIL Modbus server at {args.ip}:{args.port} ...")
        conn.connect()
        print("  Connected.")

    emu = None
    if not args.dry_run and not args.no_emulator:
        print(f"Connecting to physical battery emulator at {args.emu_port} ...")
        try:
            emu = BatteryEmulatorReader(args.emu_port)
        except (serial.SerialException, OSError) as e:
            if conn is not None:
                conn.close()
            raise RuntimeError(
                f"Could not open battery emulator serial port {args.emu_port}: {e}"
            ) from e

    # ── Dataset ──────────────────────────────────────────────────────────────
    act_path = Path(args.actual)
    if not act_path.exists():
        raise FileNotFoundError(f"Actual CSV not found: {act_path}")

    print(f"\nLoading actual CSV: {act_path.name}")
    node_data, total_load_act, total_pv_act, dates = load_actual_feeder_csv(act_path)
    available_steps = len(total_load_act)
    if start_idx < 0 or end_idx > available_steps:
        raise ValueError(
            f"Requested window {args.start_hour:.1f}-{args.end_hour:.1f} h "
            f"needs rows {start_idx}:{end_idx}, but actual data has only "
            f"{available_steps} steps ({available_steps * DELTA_HOURS:.1f} h)."
        )

    load646_act = node_data[CIL_NODE]["load_kw"]
    pv646_act = node_data[CIL_NODE]["pv_kw"]

    if args.forecast is not None:
        fc_path = Path(args.forecast)
        if not fc_path.exists():
            raise FileNotFoundError(f"Node-646 forecast CSV not found: {fc_path}")
        print(f"Loading forecast CSV: {fc_path.name}")
        pv_days, load_days, _ = load_forecast_csv(fc_path)
        load646_fc = load_days.flatten()
        pv646_fc = pv_days.flatten()
    else:
        print("No --forecast supplied: using perfect Node-646 forecast from actual data.")
        load646_fc = load646_act.copy()
        pv646_fc = pv646_act.copy()

    # Keep the FULL future horizon even though only a selected interval is executed.
    needed_len = end_idx + N_STEPS
    if len(load646_fc) < needed_len:
        load646_fc = pad_to_length(load646_fc, needed_len)
        pv646_fc = pad_to_length(pv646_fc, needed_len)
    eta_flat = make_eta_array(needed_len)

    pmax_discharge_hw = emulator_representable_power_kw(
        args.node646_capacity, args.step_seconds, args.emu_discharge_rate
    )
    pmax_charge_hw = emulator_representable_power_kw(
        args.node646_capacity, args.step_seconds, args.emu_charge_rate
    )
    wall_runtime_s = selected_steps * args.step_seconds

    # ── Banner ───────────────────────────────────────────────────────────────
    print("=" * 86)
    print("ECE4191 Experiment 3 | Physical Battery Emulator Hardware-Synchronised MPC")
    print("=" * 86)
    print(f"  Selected window    : {args.start_hour:.1f} h <= t < {args.end_hour:.1f} h")
    print(f"  Dataset steps      : {selected_steps} x {DELTA_HOURS:.1f} simulated h")
    print(f"  Wall step          : {args.step_seconds:.1f} s per data step")
    print(f"  Expected wall time : {wall_runtime_s/3600:.2f} h")
    print(f"  MPC feedback       : {effective_feedback.upper()} SoC")
    print(f"  HIL target         : {args.ip}:{args.port}")
    print(f"  Emulator rate      : C255={args.emu_charge_rate:.2f}, "
          f"D255={args.emu_discharge_rate:.2f} raw counts/s")
    print(f"  Physical range     : approx -{pmax_charge_hw:.1f} to +{pmax_discharge_hw:.1f} kW "
          f"at {args.step_seconds:.0f} s/step")
    print(f"  Ideal battery      : +/-{args.node646_batt_power:.0f} kW, "
          f"{args.node646_capacity:.0f} kWh")
    if args.step_seconds < 100:
        print("  WARNING            : very short wall step; this is not the calibrated sync run.")
    if args.no_wait:
        print("  WARNING            : --no-wait skips hardware time scaling; diagnostic only.")
    if args.dry_run:
        print("  *** DRY-RUN MODE ***")
    print("=" * 86)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. HIL model is compiled, running, and in REMOTE CONTROL.")
        print("  2. Modbus holding registers 2000-2063 are enabled.")
        print("  3. Emulator Auto Batt V and Auto Chg/Dischg are connected to the intended HIL inputs.")
        print("  4. Emulator startup SoC has been set/reset to the desired SoC for the selected E3 window.")
        print("  5. Signal Analyzer / SCADA logging is ready before starting the long hold sequence.")
        input("\nPress Enter to initialise the selected-window run ...\n")

    # ── Initial state ────────────────────────────────────────────────────────
    print("\nClearing all Modbus holding registers ...")
    clear_all_registers(conn, args.dry_run)

    settle = 12
    if not args.no_wait and not args.dry_run:
        print(f"Waiting {settle} s for HIL to settle ...")
        time.sleep(settle)

    hil_initial_pct = None if args.dry_run else read_node646_soc_pct(conn)
    emu_initial_raw = emu_initial_pct = emu_initial_age = None
    if emu is not None:
        emu_initial_raw, emu_initial_pct, emu_initial_age, _ = emu.read_latest(
            max(2.0, args.emu_wait)
        )

    if emu_initial_pct is not None:
        print(f"  Initial emulator SoC : {emu_initial_raw:05d} = {emu_initial_pct:.3f}%")
    else:
        print("  Initial emulator SoC : unavailable")
    if hil_initial_pct is not None:
        print(f"  Initial HIL SoC      : {hil_initial_pct:.3f}%")

    if args.target_start_soc_pct is not None:
        if emu_initial_pct is None:
            raise RuntimeError("Cannot verify --target-start-soc-pct: no emulator SoC received.")
        err = emu_initial_pct - args.target_start_soc_pct
        if abs(err) > args.start_soc_tolerance_pct:
            raise RuntimeError(
                f"Physical emulator starts at {emu_initial_pct:.2f}% but target is "
                f"{args.target_start_soc_pct:.2f}% (error {err:+.2f} pp). "
                "Adjust the startup SoC knob/reset the emulator before running."
            )

    if effective_feedback == "emulator":
        if emu_initial_pct is None:
            raise RuntimeError("No emulator SoC received; cannot start emulator-feedback MPC.")
        if emu_initial_age is not None and emu_initial_age > args.emu_stale_limit:
            raise RuntimeError("Initial emulator SoC sample is stale.")
        soc0_kwh = emu_initial_pct / 100.0 * args.node646_capacity
    elif effective_feedback == "hil" and hil_initial_pct is not None:
        soc0_kwh = hil_initial_pct / 100.0 * args.node646_capacity
    else:
        soc0_kwh = args.node646_initial_soc
        if not args.dry_run:
            print(f"  WARNING: feedback SoC unavailable; using fallback {soc0_kwh:.1f} kWh.")

    if not args.no_prompt and not args.dry_run:
        print(f"\nMPC will start at {100.0*soc0_kwh/args.node646_capacity:.3f}% SoC "
              f"from {effective_feedback.upper()} feedback.")
        input("Press Enter to begin the timed hardware playback ...\n")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sched_rows = []
    emu_sample_rows = []
    aborted = False

    print(_HDR)
    print("-" * len(_HDR))

    try:
        for run_i, global_i in enumerate(range(start_idx, end_idx), start=1):
            step_wall_start = time.monotonic()
            global_step = global_i + 1
            sim_hour = global_i * DELTA_HOURS
            day_num = (global_i // N_STEPS) + 1
            k = (global_i % N_STEPS) + 1

            soc_start_pct = 100.0 * soc0_kwh / args.node646_capacity

            # Full 24 h MPC horizon beginning at the selected global dataset row.
            window_end = global_i + N_STEPS
            p_load_win = load646_fc[global_i:window_end]
            p_pv_win = pv646_fc[global_i:window_end]
            eta_win = eta_flat[global_i:window_end]

            batt_traj, grid_traj, soc_traj, status, obj_val = solve_daily_qp(
                p_load_win, p_pv_win, eta_win,
                weight=args.weight,
                batt_power_kw=args.node646_batt_power,
                capacity_kwh=args.node646_capacity,
                soc0_kwh=soc0_kwh,
                solver=args.solver,
            )

            if status not in ("optimal", "optimal_inaccurate"):
                print(f"  WARNING: MPC status={status} at global step {global_step}; using 0 kW.")
                p_bat_646 = 0.0
                soc_pred_next_kwh = soc0_kwh
                grid_forecast_kw = float(p_load_win[0] - p_pv_win[0])
            else:
                p_bat_646 = float(batt_traj[0])
                soc_pred_next_kwh = float(soc_traj[1])
                grid_forecast_kw = float(grid_traj[0])

            # Capture the physical SoC immediately BEFORE issuing the new command.
            # This gives a clean per-step raw-delta measurement.
            emu_start_raw = emu_start_pct = None
            if emu is not None:
                emu_start_raw, emu_start_pct, _, _ = emu.read_latest(0.25)

            # Send the physical emulator a time-scaled command based on the measured
            # 16 counts/s calibration and the actual wall-clock hold duration.
            emu_info = {
                "command": "-", "code": None, "saturated": False,
                "target_delta_raw": None, "required_rate_raw_per_s": None,
                "max_rate_raw_per_s": None, "equivalent_power_kw": None,
            }
            if emu is not None and args.command_emulator:
                emu_info = emu.send_sync_power_command(
                    p_bat_kw=p_bat_646,
                    capacity_kwh=args.node646_capacity,
                    step_seconds=args.step_seconds,
                    charge_max_raw_per_s=args.emu_charge_rate,
                    discharge_max_raw_per_s=args.emu_discharge_rate,
                )
                if emu_info["saturated"]:
                    print(
                        f"  WARNING: emulator command saturated at {emu_info['command']} "
                        f"for requested Pbat={p_bat_646:.2f} kW."
                    )

            # HIL still receives the same E3 feeder inputs and requested Node-646 Pbat
            # through Modbus. The physical emulator is the SoC feedback state in the
            # default hardware-sync mode; HIL SoC is retained as a comparison signal.
            pbat_nodes = {node: 0.0 for node in NODE_MAP}
            pbat_nodes[CIL_NODE] = p_bat_646
            payload = build_feeder_payload(node_data, global_i, pbat_nodes)
            modbus_write_feeder(conn, payload, args.dry_run, args.verbose)

            load_act_i = float(load646_act[global_i])
            pv_act_i = float(pv646_act[global_i])
            total_load_i = float(total_load_act[global_i])
            total_pv_i = float(total_pv_act[global_i])
            grid_646_actual_kw = load_act_i - pv_act_i - p_bat_646

            context = {
                "run_step": run_i,
                "global_step": global_step,
                "sim_hour_start": sim_hour,
                "day": day_num,
                "k": k,
                "battery_646_kw": round(p_bat_646, 6),
                "emulator_command": emu_info["command"],
            }

            if args.no_wait or args.dry_run:
                emu_end_raw, emu_end_pct, emu_age_s, emu_fresh = (
                    (emu_start_raw, emu_start_pct, None, False)
                    if emu is not None else (None, None, None, False)
                )
            else:
                emu_end_raw, emu_end_pct, emu_age_s, emu_fresh = hold_step_and_log_emulator(
                    emu=emu,
                    duration_s=args.step_seconds,
                    emu_wait_s=args.emu_wait,
                    sample_rows=emu_sample_rows,
                    step_context=context,
                    progress_every_s=args.hold_progress_seconds,
                )

            hil_end_pct = None if args.dry_run else read_node646_soc_pct(conn)

            # Fail closed if physical feedback disappears during a long hardware run.
            if effective_feedback == "emulator":
                if emu_end_pct is None:
                    raise RuntimeError(
                        f"No emulator SoC available at end of run step {run_i}."
                    )
                if emu_age_s is not None and emu_age_s > args.emu_stale_limit:
                    raise RuntimeError(
                        f"Emulator SoC is stale ({emu_age_s:.2f}s) at run step {run_i}."
                    )
                soc0_kwh = emu_end_pct / 100.0 * args.node646_capacity
            elif effective_feedback == "hil" and hil_end_pct is not None:
                soc0_kwh = hil_end_pct / 100.0 * args.node646_capacity
            else:
                soc0_kwh = soc_pred_next_kwh

            pred_end_pct = 100.0 * soc_pred_next_kwh / args.node646_capacity
            emu_pred_err_pp = (
                None if emu_end_pct is None else float(emu_end_pct - pred_end_pct)
            )
            emu_delta_raw = (
                None if emu_start_raw is None or emu_end_raw is None
                else int(emu_end_raw - emu_start_raw)
            )
            target_signed_raw = None
            if emu_info["target_delta_raw"] is not None:
                target_signed_raw = (
                    -emu_info["target_delta_raw"] if p_bat_646 > 0
                    else emu_info["target_delta_raw"] if p_bat_646 < 0
                    else 0.0
                )

            sched_rows.append({
                "run_step": run_i,
                "global_step": global_step,
                "sim_hour_start": sim_hour,
                "sim_hour_end": sim_hour + DELTA_HOURS,
                "day": day_num,
                "k": k,
                "soc_feedback_source": effective_feedback,
                "soc_start_feedback_pct": round(soc_start_pct, 6),
                "p_load_fc_646_kw": round(float(p_load_win[0]), 6),
                "p_pv_fc_646_kw": round(float(p_pv_win[0]), 6),
                "p_load_646_kw": round(load_act_i, 6),
                "p_pv_646_kw": round(pv_act_i, 6),
                "baseline_grid_646_kw": round(load_act_i - pv_act_i, 6),
                "battery_646_kw": round(p_bat_646, 6),
                "battery_action": _action(p_bat_646),
                "grid_646_kw": round(grid_646_actual_kw, 6),
                "grid_646_forecast_kw": round(grid_forecast_kw, 6),
                "soc_predicted_end_pct": round(pred_end_pct, 6),
                "soc_hil_end_pct": "" if hil_end_pct is None else round(float(hil_end_pct), 6),
                "emulator_command": emu_info["command"],
                "emulator_command_code": "" if emu_info["code"] is None else int(emu_info["code"]),
                "emulator_command_saturated": bool(emu_info["saturated"]),
                "emulator_equivalent_power_kw": (
                    "" if emu_info["equivalent_power_kw"] is None
                    else round(float(emu_info["equivalent_power_kw"]), 6)
                ),
                "emulator_target_delta_raw": (
                    "" if target_signed_raw is None else round(float(target_signed_raw), 6)
                ),
                "emulator_actual_delta_raw": "" if emu_delta_raw is None else int(emu_delta_raw),
                "emulator_soc_start_raw": "" if emu_start_raw is None else int(emu_start_raw),
                "emulator_soc_end_raw": "" if emu_end_raw is None else int(emu_end_raw),
                "emulator_soc_start_pct": "" if emu_start_pct is None else round(float(emu_start_pct), 6),
                "emulator_soc_end_pct": "" if emu_end_pct is None else round(float(emu_end_pct), 6),
                "emulator_minus_predicted_pp": (
                    "" if emu_pred_err_pp is None else round(emu_pred_err_pp, 6)
                ),
                "emulator_sample_age_s": "" if emu_age_s is None else round(float(emu_age_s), 6),
                "emulator_fresh_during_hold": bool(emu_fresh),
                "feeder_baseline_grid_kw": round(total_load_i - total_pv_i, 6),
                "feeder_grid_with_cil_kw": round(total_load_i - total_pv_i - p_bat_646, 6),
                "mpc_status": status,
                "mpc_objective": obj_val,
                "wall_step_actual_s": round(time.monotonic() - step_wall_start, 4),
            })

            if args.verbose or (args.progress_every > 0 and
                                (run_i in (1, selected_steps)
                                 or run_i % args.progress_every == 0)):
                print_step(
                    run_step=run_i,
                    global_step=global_step,
                    sim_hour=sim_hour,
                    day=day_num,
                    k=k,
                    batt=p_bat_646,
                    emu_cmd=emu_info["command"],
                    emu_raw=emu_end_raw,
                    emu_pct=emu_end_pct,
                    hil_pct=hil_end_pct,
                    pred_pct=pred_end_pct,
                    err_pp=emu_pred_err_pp,
                    saturated=bool(emu_info["saturated"]),
                )

    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")
        aborted = True

    finally:
        if emu is not None:
            if args.command_emulator:
                emu.stop()
            emu.close()
        if args.keep_final:
            print("\nFinal HIL Modbus state kept (--keep-final).")
        else:
            print("\nClearing all HIL holding registers ...")
            try:
                clear_all_registers(conn, args.dry_run)
            except Exception as e:
                print(f"  WARNING: final HIL clear failed: {e}")
        if conn is not None:
            conn.close()
        print("Done.")

    print("-" * len(_HDR))

    output_dir = Path("Output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if sched_rows:
        sched_path = output_dir / f"mpc_cil_node646_hw_sync_{ts}.csv"
        pd.DataFrame(sched_rows).to_csv(sched_path, index=False)
        print(f"Hardware-sync step log : {sched_path}")

    if emu_sample_rows:
        sample_path = output_dir / f"mpc_cil_node646_emulator_1Hz_{ts}.csv"
        pd.DataFrame(emu_sample_rows).to_csv(sample_path, index=False)
        print(f"Emulator ~1 Hz log     : {sample_path}")

    print("\nPlayback complete." + ("  (aborted)" if aborted else ""))


if __name__ == "__main__":
    main()
