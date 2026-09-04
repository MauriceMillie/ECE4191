#!/usr/bin/env python3
"""
ECE4191 Module 3 - Experiment 1
Feeder-wide day-ahead QP battery scheduling over Modbus TCP/IP.

What this script does
---------------------
1. Reads the central feeder day-ahead load/PV forecast.
2. Solves one 48-step (24 h) QP for each day.
3. Disaggregates the aggregate battery command across the 16 node-phase
   battery groups in proportion to customer count.
4. Reads the actual per-node load/PV playback data used in Module 1.
5. Writes all 64 Modbus holding registers (2000-2063) to the HIL at every
   playback step.
6. Optionally reads Node 646 battery SoC from input register 3000 for
   logging only. Experiment 1 remains open-loop: measured SoC is NOT fed
   back into the QP.
7. Saves a timestamped experiment1_qp_schedule_*.csv log.

Sign convention
---------------
Pbat > 0  -> battery discharging / injecting power
Pbat < 0  -> battery charging / absorbing power
Grid power = Pload - PPV - Pbat

Important
---------
The default objective weight below is 1e-3 only as a documented working
reference value from the team's Module 2 studies. If your group selected a
different final w, run this script with --weight <value>.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

try:
    import cvxpy as cp
except ImportError:
    print("ERROR: cvxpy not found. Install it with:")
    print("  pip install cvxpy --break-system-packages")
    sys.exit(1)

# Permit forecast/QP dry testing on a machine without pymodbus installed.
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    ModbusTcpClient = None


# =============================================================================
# 1. Experiment settings
# =============================================================================

N_STEPS = 48
DELTA_HOURS = 0.5
STEP_SECONDS = 2.0

# Provisional/reference value. Override with --weight if your team chose another w.
DEFAULT_WEIGHT = 1e-3

# Aggregate feeder battery: 10 kWh/customer and 5 kW/customer.
BATTERY_KWH_PER_CUSTOMER = 10.0
BATTERY_KW_PER_CUSTOMER = 5.0

# Modbus server on the HIL model.
DEFAULT_HIL_IP = "192.168.1.210"
DEFAULT_HIL_PORT = 502

HOLDING_START = 2000
HOLDING_COUNT = 64
SOC_INPUT_REGISTER = 3000

SIGNED_16BIT_MIN = -32768
SIGNED_16BIT_MAX = 32767

RECONNECT_RETRIES = 5
RECONNECT_DELAY_S = 2.0
INITIAL_SETTLE_SECONDS = 12

TIME_COL_RE = re.compile(r"^\d{1,2}:\d{2}$")

# Holding-register layout from the Module 3 register map.
# "normal"   = [Pload, Qload, PPV, Pbat]
# "reversed" = [Pbat, PPV, Qload, Pload]
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

# Customer counts used for battery disaggregation.
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

TOTAL_CUSTOMERS = sum(N_CUSTOMERS.values())

BATTERY_CAPACITY_KWH = BATTERY_KWH_PER_CUSTOMER * TOTAL_CUSTOMERS
BATTERY_POWER_KW = BATTERY_KW_PER_CUSTOMER * TOTAL_CUSTOMERS
INITIAL_SOC_KWH = 0.5 * BATTERY_CAPACITY_KWH

# Module 1 feeder playback used Qref = 0 for the time-varying loads.
QREF_MAP = {node: 0.0 for node in NODE_MAP}

PHASE_MAP = {
    "A": "A", "B": "B", "C": "C",
    "Ph1": "A", "Ph2": "B", "Ph3": "C",
    "1": "A", "2": "B", "3": "C",
}


# =============================================================================
# 2. CSV helpers
# =============================================================================

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


def find_time_columns(df: pd.DataFrame) -> list[str]:
    cols = [str(c) for c in df.columns if TIME_COL_RE.match(str(c).strip())]
    if len(cols) != N_STEPS:
        raise ValueError(
            f"Expected {N_STEPS} half-hour time columns, found {len(cols)}: {cols}"
        )
    return cols


def normalise_node(value) -> str:
    """Convert values such as 646, 646.0, or '646' to '646'."""
    text = str(value).strip()
    try:
        number = float(text)
        if number.is_integer():
            return str(int(number))
    except ValueError:
        pass
    return text


def normalise_phase(value) -> str:
    text = str(value).strip()
    if text not in PHASE_MAP:
        raise ValueError(f"Unknown phase label: {value!r}")
    return PHASE_MAP[text]


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
    """
    Read agg_jan2013_students.csv and assemble per-node actual playback arrays.

    Missing PV rows are allowed and treated as zero, matching the Module 1
    playback behaviour. Every expected node-phase must have a GC_Load_kW row.
    """
    df = pd.read_csv(path)

    required = {"Date", "Node", "Phase", "Profile"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Actual feeder CSV missing columns: {sorted(missing)}")

    time_cols = find_time_columns(df)
    dates = sorted_date_labels(df)
    total_steps = len(dates) * N_STEPS

    node_data = {
        node: {
            "load_kw": np.zeros(total_steps, dtype=float),
            "pv_kw": np.zeros(total_steps, dtype=float),
        }
        for node in NODE_MAP
    }

    seen_load: set[tuple[str, str]] = set()
    seen_pv: set[tuple[str, str]] = set()

    for day_i, date in enumerate(dates):
        day_rows = df[df["Date"].astype(str).str.strip() == date]

        for _, row in day_rows.iterrows():
            node = normalise_node(row["Node"])
            phase = normalise_phase(row["Phase"])
            node_key = f"{node}_{phase}"

            # Ignore rows that are not one of the 16 controlled node-phases.
            if node_key not in NODE_MAP:
                continue

            profile = str(row["Profile"]).strip()
            if profile not in ("GC_Load_kW", "PV_Generation_kW"):
                continue

            values = pd.to_numeric(row[time_cols], errors="raise").to_numpy(float)
            start = day_i * N_STEPS
            end = start + N_STEPS
            seen_key = (date, node_key)

            if profile == "GC_Load_kW":
                if seen_key in seen_load:
                    raise ValueError(f"Duplicate load row for {date}, {node_key}")
                node_data[node_key]["load_kw"][start:end] = values
                seen_load.add(seen_key)
            else:
                if seen_key in seen_pv:
                    raise ValueError(f"Duplicate PV row for {date}, {node_key}")
                node_data[node_key]["pv_kw"][start:end] = values
                seen_pv.add(seen_key)

    missing_load = [
        f"{date}/{node}"
        for date in dates
        for node in NODE_MAP
        if (date, node) not in seen_load
    ]
    if missing_load:
        raise ValueError(
            "Actual feeder CSV is missing GC_Load_kW rows for expected node-phases: "
            + ", ".join(missing_load[:20])
            + (" ..." if len(missing_load) > 20 else "")
        )

    missing_pv = [
        f"{date}/{node}"
        for date in dates
        for node in NODE_MAP
        if (date, node) not in seen_pv
    ]
    if missing_pv:
        print(
            f"NOTE: {len(missing_pv)} node/day PV row(s) are absent in the actual CSV; "
            "those PV inputs will be sent as 0 kW."
        )

    total_load = np.zeros(total_steps, dtype=float)
    total_pv = np.zeros(total_steps, dtype=float)

    for node in NODE_MAP:
        total_load += node_data[node]["load_kw"]
        total_pv += node_data[node]["pv_kw"]

    return node_data, total_load, total_pv, dates, time_cols


# =============================================================================
# 3. QP controller
# =============================================================================

def make_tariff() -> np.ndarray:
    """48-step TOU tariff used in the team's Module 2 code."""
    eta = np.zeros(N_STEPS, dtype=float)
    eta[np.r_[0:14, 44:48]] = 0.03
    eta[np.r_[14:28, 40:44]] = 0.06
    eta[28:40] = 0.30
    return eta


def solve_daily_qp(
    p_load: np.ndarray,
    p_pv: np.ndarray,
    eta: np.ndarray,
    weight: float,
    batt_power_kw: float,
    capacity_kwh: float,
    soc0_kwh: float,
    solver: str,
):
    """
    Solve the Module 2 day-ahead QP:

        min sum_k[-Delta*eta(k)*Pbat(k)
                  + w*eta(k)*Pgrid(k)^2]

        Pgrid = Pload_hat - PPV_hat - Pbat
        SoC(k+1) = SoC(k) - Delta*Pbat(k)
        -Bch <= Pbat <= Bdis
        0 <= SoC <= C
        SoC(end) = SoC(start)
    """
    p_load = np.asarray(p_load, dtype=float)
    p_pv = np.asarray(p_pv, dtype=float)
    eta = np.asarray(eta, dtype=float)

    if not (len(p_load) == len(p_pv) == len(eta) == N_STEPS):
        raise ValueError("Daily QP requires 48 load, PV, and tariff samples.")
    if weight <= 0:
        raise ValueError("QP weight w must be > 0.")
    if not (0.0 <= soc0_kwh <= capacity_kwh):
        raise ValueError("Initial SoC must lie within [0, capacity].")

    n = len(p_load)
    batt = cp.Variable(n, name="Pbat")
    grid = cp.Variable(n, name="Pgrid")
    soc = cp.Variable(n + 1, name="SoC")

    objective = cp.Minimize(
        cp.sum(
            -DELTA_HOURS * cp.multiply(eta, batt)
            + weight * cp.multiply(eta, cp.square(grid))
        )
    )

    constraints = [
        grid == p_load - p_pv - batt,
        batt >= -batt_power_kw,
        batt <= batt_power_kw,
        soc[0] == soc0_kwh,
        soc[1:] == soc[:-1] - DELTA_HOURS * batt,
        soc >= 0.0,
        soc <= capacity_kwh,
        soc[-1] == soc0_kwh,
    ]

    problem = cp.Problem(objective, constraints)

    installed = set(cp.installed_solvers())
    if solver not in installed:
        raise RuntimeError(
            f"Requested solver {solver!r} is not installed. "
            f"Available solvers: {sorted(installed)}"
        )

    problem.solve(solver=solver, verbose=False)

    if problem.status not in ("optimal", "optimal_inaccurate") or batt.value is None:
        raise RuntimeError(f"QP failed with status: {problem.status}")

    batt_v = np.asarray(batt.value, dtype=float).reshape(-1)
    grid_v = np.asarray(grid.value, dtype=float).reshape(-1)
    soc_v = np.asarray(soc.value, dtype=float).reshape(-1)

    return batt_v, grid_v, soc_v, str(problem.status), float(problem.value)


def battery_action(value_kw: float) -> str:
    if value_kw > 0.5:
        return "Discharge"
    if value_kw < -0.5:
        return "Charge"
    return "Idle"


def disaggregate_battery(pbat_aggregate_kw: float) -> Dict[str, float]:
    commands = {
        node: float(pbat_aggregate_kw) * N_CUSTOMERS[node] / TOTAL_CUSTOMERS
        for node in N_CUSTOMERS
    }

    if not np.isclose(sum(commands.values()), pbat_aggregate_kw, atol=1e-8):
        raise RuntimeError("Battery disaggregation does not sum to the aggregate command.")

    return commands


# =============================================================================
# 4. Modbus helpers
# =============================================================================

class ModbusConnection:
    def __init__(
        self,
        ip: str,
        port: int,
        retries: int = RECONNECT_RETRIES,
        delay: float = RECONNECT_DELAY_S,
    ):
        self.ip = ip
        self.port = port
        self.retries = retries
        self.delay = delay
        self.client = None

    def connect(self) -> None:
        if ModbusTcpClient is None:
            raise RuntimeError(
                "pymodbus is not installed. Install it with:\n"
                "  pip install pymodbus --break-system-packages"
            )

        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                client = ModbusTcpClient(self.ip, port=self.port)
                if client.connect():
                    self.client = client
                    return
            except Exception as exc:
                last_exc = exc

            print(
                f"  Connection attempt {attempt}/{self.retries} failed"
                f"{f' ({last_exc})' if last_exc else ''}; "
                f"retrying in {self.delay}s ..."
            )
            time.sleep(self.delay)

        raise ConnectionError(
            f"Cannot connect to HIL Modbus server at {self.ip}:{self.port} "
            f"after {self.retries} attempts."
        )

    def reconnect(self) -> None:
        self.close()
        print("  Attempting Modbus reconnection ...")
        self.connect()

    def close(self) -> None:
        try:
            if self.client is not None:
                self.client.close()
        except Exception:
            pass
        self.client = None


def signed_to_register(value: float) -> int:
    """Convert signed engineering integer to unsigned 16-bit register encoding."""
    integer = int(round(float(value)))

    if integer < SIGNED_16BIT_MIN or integer > SIGNED_16BIT_MAX:
        raise ValueError(
            f"Modbus value {integer} is outside signed 16-bit range "
            f"[{SIGNED_16BIT_MIN}, {SIGNED_16BIT_MAX}]."
        )

    return integer & 0xFFFF


def build_feeder_payload(
    node_data: dict,
    step_index: int,
    pbat_nodes: Dict[str, float],
) -> list[int]:
    """Build holding-register payload 2000-2063 for one playback step."""
    payload = [0] * HOLDING_COUNT

    for node, config in NODE_MAP.items():
        p_load = float(node_data[node]["load_kw"][step_index])
        q_load = float(QREF_MAP[node])
        p_pv = float(node_data[node]["pv_kw"][step_index])
        p_bat = float(pbat_nodes[node])

        values = [p_load, q_load, p_pv, p_bat]

        if config["order"] == "reversed":
            values = list(reversed(values))

        offset = config["start"] - HOLDING_START
        payload[offset:offset + 4] = [signed_to_register(v) for v in values]

    if len(payload) != HOLDING_COUNT:
        raise RuntimeError("Internal error: feeder payload is not 64 registers.")

    return payload


def modbus_write_feeder(
    conn: Optional[ModbusConnection],
    payload: list[int],
    dry_run: bool,
    verbose: bool = False,
) -> None:
    if len(payload) != HOLDING_COUNT:
        raise ValueError(
            f"Expected {HOLDING_COUNT} Modbus registers, got {len(payload)}."
        )

    if dry_run:
        if verbose:
            print(f"    [DRY-RUN] holding[2000:2064] = {payload}")
        return

    if conn is None or conn.client is None:
        raise RuntimeError("Modbus client is not connected.")

    try:
        result = conn.client.write_registers(
            address=HOLDING_START,
            values=payload,
        )
        if result is None or result.isError():
            raise IOError("write_registers returned an error result")
        return
    except Exception as exc:
        print(f"  WARNING: Modbus write failed ({exc}).")

    conn.reconnect()
    result = conn.client.write_registers(
        address=HOLDING_START,
        values=payload,
    )
    if result is None or result.isError():
        raise IOError("Modbus write failed again after reconnection.")


def clear_all_registers(
    conn: Optional[ModbusConnection],
    dry_run: bool,
) -> None:
    payload = [0] * HOLDING_COUNT

    if dry_run:
        print(
            f"    [DRY-RUN] clear holding[{HOLDING_START}:"
            f"{HOLDING_START + HOLDING_COUNT}]"
        )
        return

    if conn is None or conn.client is None:
        raise RuntimeError("Modbus client is not connected.")

    result = conn.client.write_registers(
        address=HOLDING_START,
        values=payload,
    )

    if result is None or result.isError():
        raise IOError(
            f"Failed to clear registers {HOLDING_START}-"
            f"{HOLDING_START + HOLDING_COUNT - 1}."
        )

    print(
        f"  Registers {HOLDING_START}-"
        f"{HOLDING_START + HOLDING_COUNT - 1} cleared."
    )


class SocLogger:
    """Read Node 646 SoC for logging only; never feed it back in Experiment 1."""

    def __init__(self, conn: Optional[ModbusConnection], enabled: bool):
        self.conn = conn
        self.enabled = enabled

    def _read_soc_pct(self) -> float:
        if self.conn is None or self.conn.client is None:
            raise RuntimeError("Modbus client unavailable.")

        rr = self.conn.client.read_input_registers(
            address=SOC_INPUT_REGISTER,
            count=1,
        )
        if rr is None or rr.isError():
            raise IOError(
                f"Failed to read SoC input register {SOC_INPUT_REGISTER}."
            )
        return float(rr.registers[0]) / 100.0

    def start(self) -> None:
        if not self.enabled:
            return

        try:
            value = self._read_soc_pct()
            print(
                f"  Node 646 SoC register {SOC_INPUT_REGISTER} readable "
                f"({value:.2f}%). It will be logged only."
            )
        except Exception as exc:
            print(
                f"  WARNING: Node 646 SoC could not be read ({exc}). "
                "Measured SoC will be left blank."
            )

    def read_pct(self) -> Optional[float]:
        if not self.enabled:
            return None
        try:
            return self._read_soc_pct()
        except Exception:
            return None


# =============================================================================
# 5. Console/log helpers
# =============================================================================

def timestamped_output_path(path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = path.suffix or ".csv"
    stem = path.stem if path.suffix else path.name
    output = path.with_name(f"{stem}_{ts}{suffix}")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def print_day_summary(
    day_num: int,
    date_label: str,
    batt_kw: np.ndarray,
    grid_kw: np.ndarray,
    soc_kw_h: np.ndarray,
    p_load: np.ndarray,
    p_pv: np.ndarray,
    status: str,
    obj_val: float,
    capacity_kwh: float,
) -> None:
    base_grid = p_load - p_pv
    print("=" * 78)
    print(f"Experiment 1 feeder-wide QP | Day {day_num} | {date_label}")
    print("=" * 78)
    print(f"  Solver status          : {status}")
    print(f"  QP objective value     : {obj_val:,.3f}")
    print(f"  Forecast net range     : {base_grid.min():,.1f} to {base_grid.max():,.1f} kW")
    print(f"  Forecast QP grid range : {grid_kw.min():,.1f} to {grid_kw.max():,.1f} kW")
    print(f"  Aggregate battery      : {batt_kw.min():,.1f} to {batt_kw.max():,.1f} kW")
    print(
        f"  Predicted SoC range    : "
        f"{100*soc_kw_h.min()/capacity_kwh:.1f}% to "
        f"{100*soc_kw_h.max()/capacity_kwh:.1f}%"
    )
    print(
        f"  Terminal SoC           : {soc_kw_h[-1]:,.2f} kWh "
        f"({100*soc_kw_h[-1]/capacity_kwh:.2f}%)"
    )
    print("=" * 78)


def print_step(
    step: int,
    total_steps: int,
    date_label: str,
    time_label: str,
    load_actual: float,
    pv_actual: float,
    batt: float,
    grid_actual: float,
    soc_pred_pct: float,
    soc_meas_pct: Optional[float],
) -> None:
    measured = "-" if soc_meas_pct is None else f"{soc_meas_pct:.2f}%"
    print(
        f"Step {step:03d}/{total_steps} | {date_label:>9} {time_label:>5} | "
        f"Load {load_actual:8.1f} | PV {pv_actual:8.1f} | "
        f"Batt {batt:8.1f} ({battery_action(batt):>9}) | "
        f"Grid(calc) {grid_actual:8.1f} kW | "
        f"SoC pred {soc_pred_pct:6.2f}% | SoC646 meas {measured}"
    )


def make_log_header() -> list[str]:
    base = [
        "step",
        "day",
        "date_label",
        "profile_time",
        "eta_per_kwh",
        "p_load_forecast_total_kw",
        "p_pv_forecast_total_kw",
        "p_load_actual_total_kw",
        "p_pv_actual_total_kw",
        "baseline_grid_actual_kw",
        "pbat_aggregate_kw",
        "battery_action",
        "grid_forecast_qp_kw",
        "grid_actual_calculated_kw",
        "soc_predicted_pct",
        "soc646_measured_pct",
        "qp_status",
        "qp_objective_day",
    ]
    base += [f"pbat_{node}_kw" for node in NODE_MAP]
    return base


# =============================================================================
# 6. Main
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "ECE4191 Module 3 Experiment 1 - feeder-wide day-ahead QP "
            "battery playback over Modbus TCP."
        )
    )

    parser.add_argument(
        "--input",
        default="Code_and_data/central_agg_forecast_data_students.csv",
        help="Central feeder forecast CSV used by the QP.",
    )
    parser.add_argument(
        "--actual",
        default="Code_and_data/agg_jan2013_students.csv",
        help="Actual per-node Module 1 load/PV CSV played into Typhoon.",
    )
    parser.add_argument(
        "--output",
        default="experiment1_qp_schedule.csv",
        help="Base output CSV name; a timestamp is appended automatically.",
    )

    parser.add_argument(
        "--weight",
        type=float,
        default=DEFAULT_WEIGHT,
        help=(
            f"QP objective weight w (default {DEFAULT_WEIGHT:g}; "
            "override with your team's chosen Module 2 value)."
        ),
    )
    parser.add_argument(
        "--batt-power",
        type=float,
        default=BATTERY_POWER_KW,
        help=f"Aggregate battery charge/discharge limit in kW (default {BATTERY_POWER_KW:.0f}).",
    )
    parser.add_argument(
        "--capacity",
        type=float,
        default=BATTERY_CAPACITY_KWH,
        help=f"Aggregate battery capacity in kWh (default {BATTERY_CAPACITY_KWH:.0f}).",
    )
    parser.add_argument(
        "--initial-soc",
        type=float,
        default=INITIAL_SOC_KWH,
        help=f"Initial aggregate battery energy in kWh (default {INITIAL_SOC_KWH:.0f}, 50%).",
    )
    parser.add_argument("--solver", default="OSQP")

    parser.add_argument("--step-seconds", type=float, default=STEP_SECONDS)
    parser.add_argument(
        "--measurement-delay",
        type=float,
        default=0.2,
        help="Delay after Modbus write before reading Node 646 SoC.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1,
        help="Print one playback row every N steps; 0 = summaries only.",
    )

    parser.add_argument("--ip", default=DEFAULT_HIL_IP)
    parser.add_argument("--port", type=int, default=DEFAULT_HIL_PORT)

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solve and build payloads without connecting/writing to the HIL.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Skip the 12 s initial settle and per-step timing delays.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip the live-run pre-start confirmation.",
    )
    parser.add_argument(
        "--no-measurements",
        action="store_true",
        help="Do not read Node 646 SoC register 3000.",
    )
    parser.add_argument(
        "--keep-final",
        action="store_true",
        help="Leave final holding-register values applied after playback.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full 64-register payloads in dry-run mode.",
    )

    args = parser.parse_args()

    if args.capacity <= 0:
        raise ValueError("--capacity must be > 0.")
    if args.batt_power <= 0:
        raise ValueError("--batt-power must be > 0.")
    if not 0 <= args.initial_soc <= args.capacity:
        raise ValueError("--initial-soc must lie within [0, capacity].")
    if args.weight <= 0:
        raise ValueError("--weight must be > 0.")
    if args.step_seconds < 0 or args.measurement_delay < 0:
        raise ValueError("Timing values cannot be negative.")
    if args.progress_every < 0:
        raise ValueError("--progress-every cannot be negative.")

    forecast_path = Path(args.input)
    actual_path = Path(args.actual)

    if not forecast_path.exists():
        raise FileNotFoundError(f"Forecast CSV not found: {forecast_path}")
    if not actual_path.exists():
        raise FileNotFoundError(f"Actual feeder CSV not found: {actual_path}")

    print("\nLoading forecast data ...")
    pv_days, load_days, forecast_dates, forecast_time_cols = load_forecast_csv(
        forecast_path
    )

    print("Loading actual feeder playback data ...")
    (
        node_data,
        total_load_actual,
        total_pv_actual,
        actual_dates,
        actual_time_cols,
    ) = load_actual_feeder_csv(actual_path)

    if forecast_dates != actual_dates:
        raise ValueError(
            "Forecast and actual CSV dates do not match.\n"
            f"Forecast: {forecast_dates}\n"
            f"Actual:   {actual_dates}"
        )

    if forecast_time_cols != actual_time_cols:
        raise ValueError(
            "Forecast and actual CSV half-hour columns do not match."
        )

    n_days = len(forecast_dates)
    total_steps = n_days * N_STEPS

    if n_days != 5:
        print(
            f"WARNING: Experiment 1 specifies a 5-day playback, "
            f"but the supplied files contain {n_days} day(s)."
        )

    eta = make_tariff()

    # Solve all daily QPs before touching the HIL. This catches data/solver
    # problems before the live experiment starts.
    print("\nPre-solving feeder-wide day-ahead QP schedules ...")
    daily_results = []

    soc0_day = float(args.initial_soc)
    for day_i in range(n_days):
        batt_kw, grid_kw, soc_kwh, status, obj_val = solve_daily_qp(
            p_load=load_days[day_i],
            p_pv=pv_days[day_i],
            eta=eta,
            weight=args.weight,
            batt_power_kw=args.batt_power,
            capacity_kwh=args.capacity,
            soc0_kwh=soc0_day,
            solver=args.solver,
        )

        daily_results.append({
            "batt_kw": batt_kw,
            "grid_kw": grid_kw,
            "soc_kwh": soc_kwh,
            "status": status,
            "objective": obj_val,
        })

        print_day_summary(
            day_num=day_i + 1,
            date_label=forecast_dates[day_i],
            batt_kw=batt_kw,
            grid_kw=grid_kw,
            soc_kw_h=soc_kwh,
            p_load=load_days[day_i],
            p_pv=pv_days[day_i],
            status=status,
            obj_val=obj_val,
            capacity_kwh=args.capacity,
        )

        # State inheritance from Module 2 daily-batch framework.
        # With the terminal equality, this should equal soc0_day (apart from
        # numerical tolerance), but carrying it explicitly is clearer.
        soc0_day = float(soc_kwh[-1])

    print("\n" + "=" * 78)
    print("ECE4191 Module 3 | Experiment 1 - Feeder-wide QP Playback")
    print("=" * 78)
    print(f"  HIL target         : {args.ip}:{args.port}")
    print(f"  Forecast CSV       : {forecast_path}")
    print(f"  Actual feeder CSV  : {actual_path}")
    print(f"  Dates              : {', '.join(forecast_dates)}")
    print(f"  Playback           : {n_days} day(s), {total_steps} steps")
    print(f"  Step mapping       : {args.step_seconds:g} s real = 30 min simulated")
    print(f"  Customers          : {TOTAL_CUSTOMERS}")
    print(f"  Capacity           : {args.capacity:,.0f} kWh")
    print(f"  Battery limit      : +/-{args.batt_power:,.0f} kW")
    print(f"  Initial SoC        : {args.initial_soc:,.0f} kWh "
          f"({100*args.initial_soc/args.capacity:.1f}%)")
    print(f"  QP weight w        : {args.weight:g}")
    print(f"  Qref feeder inputs : 0 kVAr")
    print(f"  Holding registers  : 2000-2063 (64 values written each step)")
    print(f"  SoC measurement    : register 3000, logging only (no QP feedback)")
    if np.isclose(args.weight, DEFAULT_WEIGHT):
        print(
            "  NOTE               : w=1e-3 is the script's reference default; "
            "change it with --weight if your team selected another value."
        )
    if args.dry_run:
        print("  *** DRY-RUN MODE - NO MODBUS CONNECTION OR WRITES ***")
    print("=" * 78)

    if not args.no_prompt and not args.dry_run:
        print("\nPre-run checklist:")
        print("  1. HIL model is compiled and running.")
        print("  2. SCADA Control Type is set to REMOTE CONTROL.")
        print("  3. Module 1 Windows auto-launch playback is disabled/stopped.")
        print("  4. BusSplitMap holding registers 2000-2063 are enabled.")
        print("  5. Battery initial SoC is consistent with the optimisation setting.")
        input("\nPress Enter to start Experiment 1 playback ...\n")

    conn = None
    if not args.dry_run:
        conn = ModbusConnection(args.ip, args.port)
        print("\nConnecting to Modbus server ...")
        conn.connect()
        print("Connected.")

    output_path = timestamped_output_path(Path(args.output))
    soc_logger = SocLogger(
        conn,
        enabled=(not args.dry_run and not args.no_measurements),
    )

    aborted = False

    try:
        print("\nClearing all 64 holding registers ...")
        clear_all_registers(conn, args.dry_run)

        if args.no_wait or args.dry_run:
            print("Initial settle delay skipped.")
        else:
            print(f"Waiting {INITIAL_SETTLE_SECONDS} s for model to settle ...")
            for remaining in range(INITIAL_SETTLE_SECONDS, 0, -1):
                print(f"  Starting in {remaining}s ...", end="\r")
                time.sleep(1)
            print(" " * 40)

        soc_logger.start()

        header = make_log_header()
        step = 0

        print(f"\nLogging schedule/playback to: {output_path}")

        with output_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=header)
            writer.writeheader()
            fh.flush()

            for day_i, date_label in enumerate(forecast_dates):
                result = daily_results[day_i]
                batt_day = result["batt_kw"]
                grid_fc_day = result["grid_kw"]
                soc_day = result["soc_kwh"]

                for k, time_label in enumerate(forecast_time_cols):
                    t0 = time.time()
                    step += 1
                    step_index = day_i * N_STEPS + k

                    pbat_aggregate = float(batt_day[k])
                    pbat_nodes = disaggregate_battery(pbat_aggregate)

                    payload = build_feeder_payload(
                        node_data=node_data,
                        step_index=step_index,
                        pbat_nodes=pbat_nodes,
                    )

                    modbus_write_feeder(
                        conn=conn,
                        payload=payload,
                        dry_run=args.dry_run,
                        verbose=args.verbose,
                    )

                    # Let the plant update before sampling SoC; the total
                    # step duration remains approximately --step-seconds.
                    if (
                        not args.no_wait
                        and not args.dry_run
                        and args.measurement_delay > 0
                    ):
                        time.sleep(args.measurement_delay)

                    soc_measured_pct = soc_logger.read_pct()

                    load_actual = float(total_load_actual[step_index])
                    pv_actual = float(total_pv_actual[step_index])
                    baseline_actual = load_actual - pv_actual
                    grid_actual = baseline_actual - pbat_aggregate
                    soc_predicted_pct = (
                        100.0 * float(soc_day[k + 1]) / args.capacity
                    )

                    # Time columns are interval-ending labels. The last
                    # "0:00" belongs to the start of the next calendar day.
                    log_date = (
                        next_day_label(date_label)
                        if time_label == "0:00"
                        else date_label
                    )

                    row = {
                        "step": step,
                        "day": day_i + 1,
                        "date_label": log_date,
                        "profile_time": time_label,
                        "eta_per_kwh": round(float(eta[k]), 6),
                        "p_load_forecast_total_kw": round(float(load_days[day_i][k]), 6),
                        "p_pv_forecast_total_kw": round(float(pv_days[day_i][k]), 6),
                        "p_load_actual_total_kw": round(load_actual, 6),
                        "p_pv_actual_total_kw": round(pv_actual, 6),
                        "baseline_grid_actual_kw": round(baseline_actual, 6),
                        "pbat_aggregate_kw": round(pbat_aggregate, 6),
                        "battery_action": battery_action(pbat_aggregate),
                        "grid_forecast_qp_kw": round(float(grid_fc_day[k]), 6),
                        "grid_actual_calculated_kw": round(grid_actual, 6),
                        "soc_predicted_pct": round(soc_predicted_pct, 6),
                        "soc646_measured_pct": (
                            ""
                            if soc_measured_pct is None
                            else round(float(soc_measured_pct), 6)
                        ),
                        "qp_status": result["status"],
                        "qp_objective_day": round(float(result["objective"]), 6),
                    }

                    for node in NODE_MAP:
                        row[f"pbat_{node}_kw"] = round(float(pbat_nodes[node]), 6)

                    writer.writerow(row)
                    fh.flush()

                    if (
                        args.progress_every > 0
                        and (
                            step == 1
                            or step == total_steps
                            or step % args.progress_every == 0
                        )
                    ):
                        print_step(
                            step=step,
                            total_steps=total_steps,
                            date_label=log_date,
                            time_label=time_label,
                            load_actual=load_actual,
                            pv_actual=pv_actual,
                            batt=pbat_aggregate,
                            grid_actual=grid_actual,
                            soc_pred_pct=soc_predicted_pct,
                            soc_meas_pct=soc_measured_pct,
                        )

                    if not args.no_wait and not args.dry_run and step < total_steps:
                        elapsed = time.time() - t0
                        time.sleep(max(0.0, args.step_seconds - elapsed))

    except KeyboardInterrupt:
        print("\nPlayback stopped by user.")
        aborted = True

    finally:
        if args.keep_final:
            print("\nFinal HIL register values kept (--keep-final).")
        else:
            print("\nClearing all 64 holding registers ...")
            try:
                clear_all_registers(conn, args.dry_run)
            except Exception as exc:
                print(f"WARNING: final register clear failed: {exc}")

        if conn is not None:
            conn.close()

    print("\nExperiment 1 playback complete." + (" (aborted)" if aborted else ""))
    print(f"Schedule/playback log: {output_path}")


if __name__ == "__main__":
    main()
