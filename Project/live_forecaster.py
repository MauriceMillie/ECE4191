"""
live_forecaster.py
------------------
Builds a per-customer load + PV forecast for any window of the MPC, using the saved
joblib models and daily BOM weather data (BOM data = stand-in for a perfect weather forecast).

Nothing here is trained: it only loads the .pkl files and calls .predict().
To swap "perfect BOM" for a real/noisy forecast later, only WeatherTable needs to change.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MAX_COL = "Maximum temperature (Degree C)"
MIN_COL = "Minimum temperature (Degree C)"
SOL_COL = "Daily global solar exposure (MJ/m*m)"

N_STEPS_PER_DAY = 48

# Same Month -> Season mapping as the training script
SEASON_MAP = {12: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4}


def _read_bom(path, col):
    """Reads a BOM daily CSV into a date-indexed Series (gaps filled like the training script)."""
    df = pd.read_csv(path)
    dates = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=df["Day"]))
    s = pd.Series(df[col].to_numpy(dtype=float), index=dates).sort_index()
    s = s[~s.index.duplicated()]
    full = pd.date_range(s.index.min(), s.index.max(), freq="D")
    return s.reindex(full).ffill().bfill()


class WeatherTable:
    """Daily weather lookup: max temp, min temp, solar exposure, plus the temperature
    history features (Prev_Day_Max, Max_3d_Mean) built the same way as in training."""

    def __init__(self, max_path, min_path=None, sol_path=None):
        mx = _read_bom(max_path, MAX_COL)
        tbl = pd.DataFrame({MAX_COL: mx})
        tbl["Prev_Day_Max"] = mx.shift(1).fillna(mx)
        tbl["Max_3d_Mean"] = mx.rolling("3D").mean()          # today + previous 2 days
        if min_path:
            tbl[MIN_COL] = _read_bom(min_path, MIN_COL).reindex(tbl.index).ffill().bfill()
        if sol_path:
            tbl[SOL_COL] = _read_bom(sol_path, SOL_COL).reindex(tbl.index).ffill().bfill()
        self.table = tbl

    def for_dates(self, dates):
        """Rows for each date in `dates`. A date outside the BOM file reuses the nearest day."""
        idx = self.table.index
        pos = idx.get_indexer(pd.DatetimeIndex(dates), method="nearest")
        return self.table.iloc[pos].reset_index(drop=True)


class LiveForecaster:
    def __init__(self, load_model_path, pv_model_path, weather: WeatherTable,
                 first_date, time_col_labels, holidays=None):
        """
        first_date       : calendar date of MPC step 0 (day 1 of the playback)
        time_col_labels  : the 48 time-column headers of the playback CSV, in order.
                           Used to work out whether a slot label is interval-START (0:00 ... 23:30)
                           or interval-END (0:30 ... 24:00); the training data uses the latter,
                           with "24:00" stored as Hour 0.0 on the SAME date.
        """
        self.load_model = joblib.load(load_model_path)
        self.pv_model = joblib.load(pv_model_path)
        self.weather = weather
        self.first_date = pd.Timestamp(first_date).normalize()
        self.holidays = pd.DatetimeIndex(holidays) if holidays is not None else None

        first = str(time_col_labels[0]).strip()
        h, m = (int(x) for x in first.split(":"))
        start_minutes = h * 60 + m
        if start_minutes == 0:            # 0:00, 0:30 ... 23:30   (interval start)
            self.slot_hours = np.arange(N_STEPS_PER_DAY) * 0.5
        elif start_minutes == 30:         # 0:30 ... 24:00         (interval end, as in training data)
            hrs = (np.arange(N_STEPS_PER_DAY) + 1) * 0.5
            hrs[-1] = 0.0                 # 24:00 -> 00:00, same date (matches training)
            self.slot_hours = hrs
        else:
            raise ValueError(f"Unexpected first time column '{first}' (expected 0:00 or 0:30)")

        for name, mdl in (("load", self.load_model), ("pv", self.pv_model)):
            if not hasattr(mdl, "feature_names_in_"):
                raise ValueError(f"The saved {name} model has no feature_names_in_ "
                                 "(it must be fitted on a DataFrame).")
        self.load_cols = list(self.load_model.feature_names_in_)
        self.pv_cols = list(self.pv_model.feature_names_in_)
        if "Load_Prev_Day" in self.load_cols:
            raise ValueError("This load model uses Load_Prev_Day (yesterday's actual load), which the "
                             "live forecaster does not supply. Retrain with DROP_LOAD_LAG = True.")

    # ------------------------------------------------------------------
    def _feature_frame(self, start_step, n_rows):
        steps = np.arange(start_step, start_step + n_rows)
        day_idx = steps // N_STEPS_PER_DAY
        slot = steps % N_STEPS_PER_DAY
        dates = self.first_date + pd.to_timedelta(day_idx, unit="D")   # per-slot date (handles midnight)

        df = pd.DataFrame({
            "Hour": self.slot_hours[slot],
            "Month": dates.month,
            "Day_of_Week": dates.dayofweek,
        })
        df["Season"] = df["Month"].map(SEASON_MAP)
        wx = self.weather.for_dates(dates)
        for c in wx.columns:
            df[c] = wx[c].to_numpy()
        if self.holidays is not None:
            df["Is_Holiday"] = dates.isin(self.holidays).astype(int)
        return df

    def predict(self, start_step, n_rows):
        """Per-customer (average household) kW for n_rows slots starting at MPC step start_step."""
        df = self._feature_frame(start_step, n_rows)
        for cols, name in ((self.load_cols, "load"), (self.pv_cols, "pv")):
            miss = [c for c in cols if c not in df.columns]
            if miss:
                raise ValueError(f"The {name} model needs features not available live: {miss}")
        load = np.asarray(self.load_model.predict(df[self.load_cols]), dtype=float)
        pv = np.asarray(self.pv_model.predict(df[self.pv_cols]), dtype=float)
        return np.clip(load, 0.0, None), np.clip(pv, 0.0, None)


class WindowForecastCache:
    """Re-forecasts only every `refresh_every` MPC steps; in between it serves slices of the
    last forecast. It predicts (48 + refresh_every - 1) slots at each refresh so a full 48-slot
    window is always available."""

    def __init__(self, forecaster: LiveForecaster, n_steps=48, refresh_every=1):
        self.f = forecaster
        self.n = n_steps
        self.every = max(1, int(refresh_every))
        self._start = None
        self._load = None
        self._pv = None
        self.n_refreshes = 0

    def window(self, step):
        if self._start is None or not (0 <= step - self._start < self.every):
            self._start = step
            self._load, self._pv = self.f.predict(step, self.n + self.every - 1)
            self.n_refreshes += 1
        off = step - self._start
        return self._load[off:off + self.n], self._pv[off:off + self.n]
