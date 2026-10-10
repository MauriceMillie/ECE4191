from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# =====================================================================
# >>> CHANGE 1 START: extra import (used by the validation check in CHANGE 6) <<<
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingRegressor
# <<< CHANGE 1 END
# =====================================================================

from simple_pid import PID

import joblib
import matplotlib.pyplot as plt

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



# note to self: bom station for data was 066137

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

def format_provided_p_data(p_data_path1, mode):
    # read csvs
    p_df = pd.read_csv(p_data_path1, header=1)

    # format data slightly (combine GC and CL to get total load)
    if mode == "load":
        filtered_p_df = p_df[p_df["Consumption Category"].isin(["GC", "CL"])]
        value_name_col = "Load_kW"
    elif mode == "pv":
        filtered_p_df = p_df[p_df["Consumption Category"] == "GG"]
        value_name_col = "PV_Gen_kW"
    else:
        raise ValueError("Mode must be 'load' or 'pv'")

    group_columns = ["Customer", "Generator Capacity", "Postcode", "date"]
    final_df = filtered_p_df.groupby(group_columns).sum().reset_index() 

    time_columns = [col for col in final_df.columns if ":" in col]
    long_df = final_df.melt(
        id_vars=group_columns,
        value_vars=time_columns,
        var_name="Time_of_Day",
        value_name=value_name_col,
    ) 

    long_df["Time_of_Day"] = long_df["Time_of_Day"].replace("24:00", "00:00") # just in case (i know the power data uses 00:00)

    long_df['datetime'] = pd.to_datetime(long_df['date'] + ' ' + long_df['Time_of_Day'], format='%d/%m/%Y %H:%M')

    long_df['Hour'] = long_df['datetime'].dt.hour + long_df['datetime'].dt.minute / 60.0
    long_df['Month'] = long_df['datetime'].dt.month
    long_df['Day_of_Week'] = long_df['datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
    long_df['Is_Weekend'] = long_df['Day_of_Week'].isin([5, 6]).astype(int)
    long_df["Season"] = long_df["Month"].map(
        {12: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4}
    )

    long_df[value_name_col] = long_df.groupby(['Customer', 'date'])[value_name_col].transform(lambda x: x.ffill().bfill())

    return long_df

def format_bom_data(bom_data_path, data_col):
    bom_df = pd.read_csv(bom_data_path)
    bom_df['date'] = (
        bom_df['Day'].astype(str).str.zfill(2) + '/' +
        bom_df['Month'].astype(str).str.zfill(2) + '/' +
        bom_df['Year'].astype(str)
    )

    bom_df[data_col] = bom_df[data_col].ffill().bfill()

    clean_bom_df = bom_df[['date', data_col]]

    return clean_bom_df

# =====================================================================
# >>> CHANGE 2 START: NEW HELPER FUNCTIONS (used by CHANGES 3, 6 and 8) <<<
# =====================================================================

# NSW public holidays across the dataset period (Jul 2011 - Jun 2013).
# Typed in by hand: please double-check against the NSW Government list.
NSW_PUBLIC_HOLIDAYS = pd.to_datetime([
    "2011-10-03", "2011-12-25", "2011-12-26", "2011-12-27",
    "2012-01-01", "2012-01-02", "2012-01-26",
    "2012-04-06", "2012-04-07", "2012-04-08", "2012-04-09", "2012-04-25",
    "2012-06-11", "2012-10-01", "2012-12-25", "2012-12-26",
    "2013-01-01", "2013-01-26", "2013-01-28",
    "2013-03-29", "2013-03-30", "2013-03-31", "2013-04-01", "2013-04-25",
    "2013-06-10",
])

MIN_TEMP_COL = "Minimum temperature (Degree C)"


def add_temp_history_features(temp_df, data_col):
    """Adds Prev_Day_Max and Max_3d_Mean (heat build-up) to the daily max-temp table.
    Built on the full continuous BOM series, so the test week's first day still sees its
    real previous day. Date-based (not row-based), so missing days can't shift values."""
    temp_df = temp_df.sort_values("date").reset_index(drop=True)
    s = temp_df.set_index("date")[data_col]
    temp_df["Prev_Day_Max"] = s.reindex(s.index - pd.Timedelta(days=1)).to_numpy()
    temp_df["Prev_Day_Max"] = temp_df["Prev_Day_Max"].fillna(temp_df[data_col])
    temp_df["Max_3d_Mean"] = s.rolling("3D").mean().to_numpy()   # today + previous 2 days
    return temp_df


def add_min_temp(temp_df, min_temp_data_path):
    """Merges the BOM daily minimum temperature onto the daily table (by date)."""
    min_df = format_bom_data(min_temp_data_path, MIN_TEMP_COL)
    min_df["date"] = pd.to_datetime(min_df["date"], format="%d/%m/%Y")
    temp_df = temp_df.merge(min_df, on="date", how="left")
    temp_df[MIN_TEMP_COL] = temp_df[MIN_TEMP_COL].ffill().bfill()
    return temp_df


def add_prev_day_load(df, source_df, value_col="Load_kW"):
    """Adds Load_Prev_Day = load at the same half-hour on the previous calendar day,
    looked up by date from source_df (so the removed test week can't misalign it)."""
    lag = source_df[["date", "Hour", value_col]].copy()
    lag["date"] = lag["date"] + pd.Timedelta(days=1)
    lag = lag.rename(columns={value_col: "Load_Prev_Day"})
    return df.merge(lag, on=["date", "Hour"], how="left")


def wape(y_true, y_pred):
    """Weighted absolute percentage error = total |error| / total actual. Safe with zeros."""
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    return float(np.abs(y_true - y_pred).sum() / np.abs(y_true).sum())


def masked_mape(y_true, y_pred, min_actual=0.01):
    """MAPE over only the slots where actual > min_actual (skips night-time PV zeros)."""
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    m = y_true > min_actual
    if not m.any():
        return float("nan")
    return float(np.mean(np.abs(y_true[m] - y_pred[m]) / y_true[m]))


def report_metrics(label, y_true, y_pred, dates, exclude_date=None, min_actual=0.01):
    """Prints whole-week metrics, optionally the week without one day, and a per-day table."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    dates = pd.Series(pd.to_datetime(dates)).reset_index(drop=True)

    def summary(mask):
        yt, yp = y_true[mask], y_pred[mask]
        return (
            f"MAE {mean_absolute_error(yt, yp):.3f} kW | RMSE {np.sqrt(mean_squared_error(yt, yp)):.3f} | "
            f"WAPE {wape(yt, yp):.1%} | MAPE(actual>{min_actual}) {masked_mape(yt, yp, min_actual):.1%} | "
            f"R2 {r2_score(yt, yp):.3f}"
        )

    print(f"\n--- {label}: detailed metrics ---")
    print(f"  Whole week        : {summary(np.ones(len(dates), dtype=bool))}")
    if exclude_date is not None:
        ex = pd.Timestamp(exclude_date)
        print(f"  Excluding {ex:%a %d %b}: {summary((dates != ex).to_numpy())}")
    print("  Per day:")
    for d in sorted(dates.unique()):
        m = (dates == d).to_numpy()
        yt, yp = y_true[m], y_pred[m]
        print(
            f"    {pd.Timestamp(d):%a %d %b}: MAE {mean_absolute_error(yt, yp):.3f} kW | "
            f"WAPE {wape(yt, yp):.1%} | MAPE {masked_mape(yt, yp, min_actual):.1%}"
        )


TEMP_COL = "Maximum temperature (Degree C)"
HOT_WEIGHT_START_C = 25.0    # hot-day weighting starts above this temperature... (default 30)
HOT_WEIGHT_PER_DEG = 2    # ...and adds this much weight per degree (30C=1x, 38C=3x, 46C=5x) (default 0.25)

HOT_WEIGHT_START_C2 = 35.0    # hot-day weighting starts above this temperature... (default 30)
HOT_WEIGHT_PER_DEG2 = 7

HOT_WEIGHT_START_C3 = 15.0    # hot-day weighting starts above this temperature... (default 30)
HOT_WEIGHT_PER_DEG3 = 1

def hot_day_weights(x, temp_col=TEMP_COL):
    """Sample weights that make hotter days count more during training."""
    over = np.clip(x[temp_col].to_numpy(dtype=float) - HOT_WEIGHT_START_C, 0, None)
    over2 = np.clip(x[temp_col].to_numpy(dtype=float) - HOT_WEIGHT_START_C2, 0, None)
    over3 = np.clip(x[temp_col].to_numpy(dtype=float) - HOT_WEIGHT_START_C3, 0, None)
    return 1.0 + (HOT_WEIGHT_PER_DEG * over)+(HOT_WEIGHT_PER_DEG2*over2)+(HOT_WEIGHT_PER_DEG3*over3)


def make_hgb():
    """Gradient boosting alternative to the random forest. early_stopping=False so it uses ALL the training rows."""
    return HistGradientBoostingRegressor(
        max_iter=400, learning_rate=0.05, min_samples_leaf=40, early_stopping=False, random_state=42
    )


def find_hot_windows(dates, temps, threshold=38.0, max_windows=2):
    """Finds clusters of hot days (> threshold) in the training data and returns one 7+ day window around each."""
    daily = pd.DataFrame({"date": pd.to_datetime(pd.Series(dates)).to_numpy(), "t": np.asarray(temps, dtype=float)})
    daily = daily.groupby("date")["t"].max()
    hot = list(daily[daily > threshold].index)
    clusters = []
    for d in hot:
        if clusters and (d - clusters[-1][-1]).days <= 6:
            clusters[-1].append(d)
        else:
            clusters.append([d])
    windows = []
    for c in clusters[:max_windows]:
        start = c[0] - pd.Timedelta(days=2)
        end = max(c[-1] + pd.Timedelta(days=2), start + pd.Timedelta(days=6))
        windows.append((start, end))
    return windows


def run_recipe_comparison(base_model, x_train, y_train, train_dates, recipes, windows, label,
                          hot_threshold=38.0, n_trees=100):
    """For each held-out window: fit every recipe on the REST of the training data, score it on the window.
    A recipe is {"cols": [...features...], "model": "rf"|"hgb", "hot_weights": True|False}.
    The real test week is never touched. The day after each window is also left out of fitting,
    because its Load_Prev_Day feature would contain the window's actual load.
    peak bias = average (predicted - actual) over the window's top-10% load slots (negative = peaks under-predicted)."""
    train_dates = pd.Series(pd.to_datetime(train_dates)).reset_index(drop=True)
    daily_t = pd.DataFrame({"date": train_dates, "t": x_train[TEMP_COL].to_numpy()}).groupby("date")["t"].max()
    hot_days = list(daily_t[daily_t > hot_threshold].index)
    scores = {name: [] for name in recipes}
    for start, end in windows:
        in_val = train_dates.between(start, end)
        leave_out = train_dates.between(start, end + pd.Timedelta(days=1))
        if in_val.sum() == 0:
            print(f"\n  [{label}] {start:%d %b %Y} - {end:%d %b %Y}: no data in this window, skipped")
            continue
        n_out = sum(start <= d <= end for d in hot_days)
        n_left = sum(not (start <= d <= end + pd.Timedelta(days=1)) for d in hot_days)
        print(f"\n  [{label}] {start:%d %b %Y} - {end:%d %b %Y}   (days > {hot_threshold:.0f}C held out: {n_out}, left in training: {n_left})")
        y = np.asarray(y_train[in_val], dtype=float)
        peak = y >= np.quantile(y, 0.9)
        fit_rows = ~leave_out
        for name, spec in recipes.items():
            cols = spec["cols"]
            if spec.get("model") == "hgb":
                model = make_hgb()
            else:
                model = clone(base_model).set_params(n_estimators=n_trees)
            kw = {"sample_weight": hot_day_weights(x_train.loc[fit_rows])} if spec.get("hot_weights") else {}
            model.fit(x_train.loc[fit_rows, cols], y_train[fit_rows], **kw)
            pred = np.asarray(model.predict(x_train.loc[in_val, cols]), dtype=float)
            w = wape(y, pred)
            scores[name].append(w)
            print(
                f"    {name:<36} WAPE {w:6.1%} | MAE {mean_absolute_error(y, pred):.3f} | "
                f"R2 {r2_score(y, pred):6.3f} | peak bias {np.mean(pred[peak] - y[peak]):+.3f} kW"
            )
    if any(scores.values()):
        print(f"\n  Average WAPE over the {label} windows (lower is better):")
        for name, v in sorted(scores.items(), key=lambda kv: np.mean(kv[1]) if kv[1] else 9.0):
            if v:
                print(f"    {name:<36} {np.mean(v):6.1%}")
    return scores

# <<< CHANGE 2 END
# =====================================================================

def p_initialize_model(p_data_path1, p_data_path2, temp_data_path, min_temp_data_path=None):  # CHANGE 3 (new optional arg)

    df_p_2011_2012 = format_provided_p_data(p_data_path1, "load")
    df_p_2012_2013 = format_provided_p_data(p_data_path2, "load")

    data_col = "Maximum temperature (Degree C)"
    temp_df = format_bom_data(temp_data_path, data_col)

    full_power_df = pd.concat([df_p_2011_2012, df_p_2012_2013], ignore_index=True)

    start_test_date = pd.to_datetime("07/01/2013", format="%d/%m/%Y") # I SHOULD PROBS CHANGE THIS TO THE 5TH or something
    end_test_date = pd.to_datetime("13/01/2013", format="%d/%m/%Y")

    full_power_df["date"] = pd.to_datetime(full_power_df["date"], format="%d/%m/%Y")
    temp_df["date"] = pd.to_datetime(temp_df["date"], format="%d/%m/%Y")

    # >>> CHANGE 3a START: temperature history features (+ optional min temp) <<<
    temp_df = add_temp_history_features(temp_df, data_col)
    extra_temp_cols = ["Prev_Day_Max", "Max_3d_Mean"]
    if min_temp_data_path:
        temp_df = add_min_temp(temp_df, min_temp_data_path)
        extra_temp_cols.append(MIN_TEMP_COL)
    # <<< CHANGE 3a END

    final_test_power_df = full_power_df[
        (full_power_df["date"] >= start_test_date)
        & (full_power_df["date"] <= end_test_date)
    ]


    training_power_df = full_power_df[
        ~(
            (full_power_df["date"] >= start_test_date)
            & (full_power_df["date"] <= end_test_date)
        )
    ]

    training_power_df['date'] = pd.to_datetime(training_power_df['date'], format='%d/%m/%Y')
    temp_df['date'] = pd.to_datetime(temp_df['date'], format='%d/%m/%Y')


    valid_training_dates = training_power_df["date"].unique()

    training_temp_df = temp_df[temp_df["date"].isin(valid_training_dates)]

    valid_test_dates = final_test_power_df["date"].unique()
    test_bom_df = temp_df[temp_df["date"].isin(valid_test_dates)]


    final_train_dataset = pd.merge(training_power_df, training_temp_df, on="date", how="left")
    final_test_dataset = pd.merge(final_test_power_df, test_bom_df, on="date", how="left")

    time_group_cols = ["date", "Hour", "Month", "Day_of_Week", "Season", data_col] + extra_temp_cols  # CHANGE 3b (+ extra_temp_cols)
    
    final_train_dataset = final_train_dataset.groupby(time_group_cols)[["Load_kW"]].mean().reset_index()
    final_test_dataset  = final_test_dataset.groupby(time_group_cols)[["Load_kW"]].mean().reset_index()

    # >>> CHANGE 3c START: holiday flag + previous-day load <<<
    for _df in (final_train_dataset, final_test_dataset):
        _df["Is_Holiday"] = _df["date"].isin(NSW_PUBLIC_HOLIDAYS).astype(int)
    # Training lags come from TRAINING data only (so Jan 14 never sees real test-week load).
    # Test lags come from train + test: forecast day D using the actual load of day D-1.
    _train_only = final_train_dataset[['date', 'Hour', 'Load_kW']]
    _train_plus_test = pd.concat([_train_only, final_test_dataset[['date', 'Hour', 'Load_kW']]])
    final_train_dataset = add_prev_day_load(final_train_dataset, _train_only)
    final_test_dataset = add_prev_day_load(final_test_dataset, _train_plus_test)
    final_train_dataset = final_train_dataset.dropna(subset=["Load_Prev_Day"]).reset_index(drop=True)
    if final_test_dataset["Load_Prev_Day"].isna().any():
        print("WARNING: some test rows have no previous-day load (missing day in the data).")
    # <<< CHANGE 3c END

    features = [
        "Hour",
        "Month",
        "Day_of_Week",
        "Season",
        data_col,
    ]

    # >>> CHANGE 3d START: add the new columns to the model's feature list <<<
    features = features + extra_temp_cols + ["Is_Holiday", "Load_Prev_Day"]
    # <<< CHANGE 3d END

    p_x_train = final_train_dataset[features]
    p_y_train = final_train_dataset["Load_kW"]

    p_x_final_test = final_test_dataset[features]
    p_y_final_test = final_test_dataset["Load_kW"]


    # >>> CHANGE 3e START: also return the dates (needed for per-day metrics / export) <<<
    date_info = {"train": final_train_dataset["date"].reset_index(drop=True),
                 "test": final_test_dataset["date"].reset_index(drop=True)}
    return p_x_train, p_y_train, p_x_final_test, p_y_final_test, date_info
    # <<< CHANGE 3e END


def pv_initialize_model(pv_data_path1, pv_data_path2, sol_exp_data_path):

    # I COULDNT BE BOTHERED TO CHANGE THE VARIABLE NAMES IN HERE REALLY SO I ONLY CHANGED THOSE THAT ARE NECESSARY
    # READABILITY IS WORSE BUT IT WAS ALREADY P BAD LMAO

    df_p_2011_2012 = format_provided_p_data(pv_data_path1, "pv")
    df_p_2012_2013 = format_provided_p_data(pv_data_path2, "pv")

    data_col = "Daily global solar exposure (MJ/m*m)"
    temp_df = format_bom_data(sol_exp_data_path, data_col)

    full_power_df = pd.concat([df_p_2011_2012, df_p_2012_2013], ignore_index=True)

    start_test_date = pd.to_datetime("07/01/2013", format="%d/%m/%Y")
    end_test_date = pd.to_datetime("13/01/2013", format="%d/%m/%Y")

    full_power_df["date"] = pd.to_datetime(full_power_df["date"], format="%d/%m/%Y")
    temp_df["date"] = pd.to_datetime(temp_df["date"], format="%d/%m/%Y")

    final_test_power_df = full_power_df[
        (full_power_df["date"] >= start_test_date)
        & (full_power_df["date"] <= end_test_date)
    ]


    training_power_df = full_power_df[
        ~(
            (full_power_df["date"] >= start_test_date)
            & (full_power_df["date"] <= end_test_date)
        )
    ]

    training_power_df['date'] = pd.to_datetime(training_power_df['date'], format='%d/%m/%Y')
    temp_df['date'] = pd.to_datetime(temp_df['date'], format='%d/%m/%Y')


    valid_training_dates = training_power_df["date"].unique()

    training_temp_df = temp_df[temp_df["date"].isin(valid_training_dates)]

    valid_test_dates = final_test_power_df["date"].unique()
    test_bom_df = temp_df[temp_df["date"].isin(valid_test_dates)]


    final_train_dataset = pd.merge(training_power_df, training_temp_df, on="date", how="left")
    final_test_dataset = pd.merge(final_test_power_df, test_bom_df, on="date", how="left")

    time_group_cols = ["date", "Hour", "Month", "Day_of_Week", "Season", data_col]
    
    final_train_dataset = final_train_dataset.groupby(time_group_cols)[["PV_Gen_kW"]].mean().reset_index()
    final_test_dataset  = final_test_dataset.groupby(time_group_cols)[["PV_Gen_kW"]].mean().reset_index()

    features = [
        "Hour",
        "Month",
        "Day_of_Week",
        "Season",
        data_col,
    ]

    p_x_train = final_train_dataset[features]
    p_y_train = final_train_dataset["PV_Gen_kW"]

    p_x_final_test = final_test_dataset[features]
    p_y_final_test = final_test_dataset["PV_Gen_kW"]


    # >>> CHANGE 4 START: also return the dates (PV features themselves are unchanged) <<<
    date_info = {"train": final_train_dataset["date"].reset_index(drop=True),
                 "test": final_test_dataset["date"].reset_index(drop=True)}
    return p_x_train, p_y_train, p_x_final_test, p_y_final_test, date_info
    # <<< CHANGE 4 END



# =====================================================================
# >>> CHANGE 10a START: two-graph plotting helper (replaces the old twin-axis plot) <<<
# =====================================================================
def plot_predicted_vs_actual(dates, actual, predicted, title, ylabel, actual_color, pred_color):
    """One figure: actual vs predicted over the continuous half-hourly test week.
    Day boundaries and their date labels come from the real `dates` column."""
    x = np.arange(len(actual))
    dates = pd.Series(pd.to_datetime(dates)).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(x, actual, color=actual_color, linewidth=2, label="Actual")
    ax.plot(x, predicted, color=pred_color, linewidth=2, linestyle="--", label="Predicted")

    day_starts = np.where(dates.ne(dates.shift()).to_numpy())[0]   # first slot of each new date
    ax.set_xticks(day_starts)
    ax.set_xticklabels([f"{dates[i]:%a %d %b}" for i in day_starts])
    for d in day_starts[1:]:
        ax.axvline(d, color="gray", linewidth=0.8, alpha=0.4)

    ax.set_xlabel("Half-hourly intervals (day boundaries marked)", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", fontsize=11)
    fig.tight_layout()
    return fig

# <<< CHANGE 10a END
# =====================================================================

def main():
    '''
    p_x_train, p_y_train, p_x_test, p_y_test = p_initialize_model(
        "Provided_Data/2011-2012Solarhomeelectricitydatav2.csv", 
        "Provided_Data/2012-2013 Solar home electricity data v2.csv", 
        "BOM_Data/IDCJAC0010_066137_1800_daily_max_temp/IDCJAC0010_066137_1800_Data.csv"
    )

    pv_x_train, pv_y_train, pv_x_test, pv_y_test = pv_initialize_model(
        "Provided_Data/2011-2012Solarhomeelectricitydatav2.csv", 
        "Provided_Data/2012-2013 Solar home electricity data v2.csv", 
        "BOM_Data/IDCJAC0016_066137_1800_daily_solar_exposure/IDCJAC0016_066137_1800_Data.csv"
    )

    load_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    pv_model   = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)

    load_model.fit(p_x_train, p_y_train)
    pv_model.fit(pv_x_train, pv_y_train)

    pred_single_L = load_model.predict(p_x_test)
    pred_single_P = pv_model.predict(pv_x_test)

    joblib.dump(load_model, "finalized_load_rf_model.pkl", compress=3)
    joblib.dump(pv_model, "finalized_pv_rf_model.pkl", compress=3)

    house_multiplier = 1

    scaled_pred_load = pred_single_L * house_multiplier
    scaled_pred_pv   = pred_single_P * house_multiplier

    y_test_agg_L = p_y_test * house_multiplier
    y_test_agg_P = pv_y_test * house_multiplier


    mae_L = mean_absolute_error(y_test_agg_L, scaled_pred_load)
    r2_L  = r2_score(y_test_agg_L, scaled_pred_load)

    mae_P = mean_absolute_error(y_test_agg_P, scaled_pred_pv)
    r2_P  = r2_score(y_test_agg_P, scaled_pred_pv)

    print("\n=================== FINAL EVALUATION RESULTS ===================")
    print(f"Target Holdout Week: Jan 7 - Jan 13, 2013")
    print(f"Aggregate Pool Scaling Factor: {house_multiplier:,} houses\n")
    print(f"[LOAD MODEL] MAE: {mae_L:,.2f} kW | R² Score: {r2_L:.3f}")
    print(f"[PV MODEL]   MAE: {mae_P:,.2f} kW | R² Score: {r2_P:.3f}")
    print("=================================================================")
    '''

    print("\nFetching and formatting data arrays...")

    # >>> CHANGE 5a START: optional minimum-temperature file (skipped if not found) <<<
    MIN_TEMP_PATH = "BOM_Data/IDCJAC0011_066137_1800_daily_min_temp/IDCJAC0011_066137_1800_Data.csv"  # <- adjust to your file
    if not Path(MIN_TEMP_PATH).exists():
        print(f"  (min temp file not found at {MIN_TEMP_PATH} - continuing without it)")
        MIN_TEMP_PATH = None
    # <<< CHANGE 5a END

    p_x_train, p_y_train, p_x_test, p_y_test, p_dates = p_initialize_model(  # CHANGE 5b (+ p_dates)
        "Provided_Data/2011-2012Solarhomeelectricitydatav2.csv",
        "Provided_Data/2012-2013 Solar home electricity data v2.csv",
        "BOM_Data/IDCJAC0010_066137_1800_daily_max_temp/IDCJAC0010_066137_1800_Data.csv",
        min_temp_data_path=MIN_TEMP_PATH,  # CHANGE 5b
    )

    pv_x_train, pv_y_train, pv_x_test, pv_y_test, pv_dates = pv_initialize_model(  # CHANGE 5c (+ pv_dates)
        "Provided_Data/2011-2012Solarhomeelectricitydatav2.csv",
        "Provided_Data/2012-2013 Solar home electricity data v2.csv",
        "BOM_Data/IDCJAC0016_066137_1800_daily_solar_exposure/IDCJAC0016_066137_1800_Data.csv",
    )
    ''' # original load model settings (V1)
    load_model = RandomForestRegressor(
        n_estimators=100, max_depth=15, random_state=42, n_jobs=-1
    )
    '''
    # current load model settings (V2)
    load_model = RandomForestRegressor(
        n_estimators=250, max_depth=22, min_samples_split=5, random_state=42, n_jobs=-1
    )

    pv_model = RandomForestRegressor(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    )

    # =====================================================================
    # >>> CHANGE 6 START: validation experiments (TRAINING data only - the test week is never used) <<<
    # Compares feature sets / model types / hot-day weighting on held-out weeks, so you can choose the
    # final recipe WITHOUT looking at Jan 7-13. It fits many temporary models and takes a few minutes.
    # =====================================================================
    RUN_VALIDATION = True       # False = skip this whole block
    FULL_ABLATION = True        # False = only baseline / all features / all minus lag (much faster)
    VALIDATION_WEEKS = [("2012-01-09", "2012-01-15"), ("2012-02-06", "2012-02-12")]   # ordinary weeks inside training data
    HOT_VALIDATION = True       # also test on windows around the hottest training days
    HOT_THRESHOLD_C = 38.0
    if RUN_VALIDATION:
        all_cols = list(p_x_train.columns)
        base_cols = ["Hour", "Month", "Day_of_Week", "Season", TEMP_COL]
        temp_hist = [c for c in ("Prev_Day_Max", "Max_3d_Mean") if c in all_cols]
        min_cols = [c for c in all_cols if c.startswith("Minimum temperature")]
        no_lag = [c for c in all_cols if c != "Load_Prev_Day"]

        recipes = {"baseline (5 features)": {"cols": base_cols}}
        if FULL_ABLATION:
            recipes["+ temp history"] = {"cols": base_cols + temp_hist}
            if min_cols:
                recipes["+ min temp"] = {"cols": base_cols + min_cols}
            recipes["+ holiday flag"] = {"cols": base_cols + ["Is_Holiday"]}
            recipes["+ previous-day load"] = {"cols": base_cols + ["Load_Prev_Day"]}
        recipes[f"all ({len(all_cols)} features)"] = {"cols": all_cols}
        recipes["all minus previous-day load"] = {"cols": no_lag}
        if FULL_ABLATION:
            recipes["all + hot-day weights"] = {"cols": all_cols, "hot_weights": True}
            recipes["all minus lag + hot-day weights"] = {"cols": no_lag, "hot_weights": True}
            recipes["all + boosting"] = {"cols": all_cols, "model": "hgb"}
            recipes["all minus lag + boosting"] = {"cols": no_lag, "model": "hgb"}
            recipes["all minus lag + boosting + weights"] = {"cols": no_lag, "model": "hgb", "hot_weights": True}

        print("\nValidation experiments on ordinary weeks (training data only)...")
        windows = [(pd.Timestamp(a_), pd.Timestamp(b_)) for a_, b_ in VALIDATION_WEEKS]
        run_recipe_comparison(load_model, p_x_train, p_y_train, p_dates["train"], recipes, windows,
                              "ordinary", HOT_THRESHOLD_C)

        if HOT_VALIDATION:
            hot_windows = find_hot_windows(p_dates["train"], p_x_train[TEMP_COL], HOT_THRESHOLD_C)
            if hot_windows:
                print("\nValidation experiments on HOT windows (training data only)...")
                run_recipe_comparison(load_model, p_x_train, p_y_train, p_dates["train"], recipes, hot_windows,
                                      "hot", HOT_THRESHOLD_C)
            else:
                print(f"\n(no training days above {HOT_THRESHOLD_C:.0f}C - hot-window validation skipped)")
        print("\nPick the recipe that does well on BOTH groups, then set the switches in CHANGE 12 below.")
    # <<< CHANGE 6 END
    # =====================================================================

    # =====================================================================
    # >>> CHANGE 12 START: FINAL load-model switches (set these after reading the CHANGE 6 results) <<<
    # =====================================================================
    DROP_LOAD_LAG = True       # True = train without the Load_Prev_Day feature
    LOAD_MODEL_TYPE = "hgb"      # "rf" = random forest (settings above) | "hgb" = gradient boosting
    HOT_DAY_WEIGHTING = False   # True = hotter days count more in training (see hot_day_weights)
    DROP_HOLIDAY_LIST = True
    #DROP_HOLIDAY_LIST "Max_3d_Mean" "Prev_Day_Max"
    DROP_3D_MEAN = False
    DROP_PREV_DAY_MAX_TEMP = False
    if DROP_LOAD_LAG:
        p_x_train = p_x_train.drop(columns=["Load_Prev_Day"])
        p_x_test = p_x_test.drop(columns=["Load_Prev_Day"])
    if DROP_HOLIDAY_LIST:
        p_x_train = p_x_train.drop(columns=["Is_Holiday"])
        p_x_test = p_x_test.drop(columns=["Is_Holiday"])

    if DROP_3D_MEAN:
        p_x_train = p_x_train.drop(columns=["Max_3d_Mean"])
        p_x_test = p_x_test.drop(columns=["Max_3d_Mean"])

    if DROP_PREV_DAY_MAX_TEMP:
        p_x_train = p_x_train.drop(columns=["Prev_Day_Max"])
        p_x_test = p_x_test.drop(columns=["Prev_Day_Max"])


    if LOAD_MODEL_TYPE == "hgb":
        load_model = make_hgb()
    load_fit_kwargs = {"sample_weight": hot_day_weights(p_x_train)} if HOT_DAY_WEIGHTING else {}
    print(f"\nFinal load model: {LOAD_MODEL_TYPE} | {p_x_train.shape[1]} features | hot-day weighting: {HOT_DAY_WEIGHTING} | Drop holiday dates: {DROP_HOLIDAY_LIST} | Drop load lag: {DROP_LOAD_LAG} | Drop 3d mean: {DROP_3D_MEAN} | Drop prev day max temp: {DROP_PREV_DAY_MAX_TEMP}")
    # <<< CHANGE 12 END
    # =====================================================================

    print("Training Random Forest Regressors (using all CPU cores)...")
    load_model.fit(p_x_train, p_y_train, **load_fit_kwargs)  # CHANGE 12 (+ load_fit_kwargs)
    print("  Load Model training completed successfully.")

    pv_model.fit(pv_x_train, pv_y_train)
    print("  PV Model training completed successfully.")

    print("Executing forecasts across the evaluation timeline...")
    pred_single_L = load_model.predict(p_x_test)
    pred_single_P = pv_model.predict(pv_x_test)

    print("Freezing models and writing compressed .pkl binaries...")
    # >>> CHANGE 7: load model saved under a NEW name so your existing 5-feature model isn't overwritten <<<
    joblib.dump(load_model, "finalized_load_rf_model_v3.pkl", compress=3)
    joblib.dump(pv_model, "finalized_pv_rf_model_v3.pkl", compress=3)


    house_multiplier = 1
    scaled_pred_load = pred_single_L * house_multiplier
    scaled_pred_pv = pred_single_P * house_multiplier

    y_test_agg_L = p_y_test * house_multiplier
    y_test_agg_P = pv_y_test * house_multiplier

    mae_L = mean_absolute_error(y_test_agg_L, scaled_pred_load)
    r2_L = r2_score(y_test_agg_L, scaled_pred_load)

    mae_P = mean_absolute_error(y_test_agg_P, scaled_pred_pv)
    r2_P = r2_score(y_test_agg_P, scaled_pred_pv)

    print(
        "\n=================== FINAL EVALUATION RESULTS ==================="
    )
    print("Target Holdout Week: Jan 7 - Jan 13, 2013")
    print(f"Aggregate Pool Scaling Factor: {house_multiplier:,} houses\n")
    print(f"[LOAD MODEL] MAE: {mae_L:,.2f} kW | R2 Score: {r2_L:.3f}")
    print(f"[PV MODEL]   MAE: {mae_P:,.2f} kW | R2 Score: {r2_P:.3f}")
    print(
        "=================================================================\n"
    )

    # =====================================================================
    # >>> CHANGE 8 START: extra metrics (WAPE, masked MAPE, per-day, week without the outlier day) <<<
    # =====================================================================
    report_metrics(
        "LOAD", y_test_agg_L, scaled_pred_load, p_dates["test"],
        exclude_date="2013-01-08",   # the 42C day; clearly labelled in the output
        min_actual=0.01,
    )
    report_metrics(
        "PV", y_test_agg_P, scaled_pred_pv, pv_dates["test"],
        min_actual=0.05,   # MAPE only counted when PV output > 0.05 kW (skips night and dawn/dusk)
    )
    # <<< CHANGE 8 END
    # =====================================================================

    # --- EXPORTING RESULTS TO CSV ---
    print("Exporting baseline forecasts to CSV archive...")


    ''' 
    # TODO: WE SHOULD PROBS ADD THIS KINDA AND APPLY IT TO PXTEST STUFF SO THAT THE DATES ARE CORRECT
    # CURRENTLY THERE IS NO DATE COLUMN I THINK AND SO IT JUST MAKES EVERY DAY DEFAULT TO 7-13-13!!!

    bom_df['date'] = (
        bom_df['Day'].astype(str).str.zfill(2) + '/' +
        bom_df['Month'].astype(str).str.zfill(2) + '/' +
        bom_df['Year'].astype(str)
    )
    '''

    export_df = pd.DataFrame(
        {
            "Date": p_dates["test"].to_numpy(),  # CHANGE 9: real dates (replaces the fixed "Jan 7-13 2013" label)
            "Hour": p_x_test["Hour"],
            "Predicted_Average_Load_kW": scaled_pred_load,
            "Predicted_Average_PV_Gen_kW": scaled_pred_pv,
        }
    )

    export_filename = "./Code_and_Data/average_household_forecasts_v3.csv"
    export_df.to_csv(export_filename, index=False)
    print(f"  Saved successfully as '{export_filename}'.")

    # =====================================================================
    # >>> CHANGE 10b START: two separate predicted-vs-actual graphs (load, then PV) <<<
    # =====================================================================
    print("Plotting predicted vs actual (load and PV)...")

    plot_predicted_vs_actual(
        dates=p_dates["test"],
        actual=np.asarray(y_test_agg_L),
        predicted=np.asarray(scaled_pred_load),
        title="Predicted vs Actual Household Load: Jan 7 - Jan 13, 2013",
        ylabel="Load Power Demand (kW)",
        actual_color="tab:blue",
        pred_color="tab:red",
    )

    plot_predicted_vs_actual(
        dates=pv_dates["test"],
        actual=np.asarray(y_test_agg_P),
        predicted=np.asarray(scaled_pred_pv),
        title="Predicted vs Actual PV Generation: Jan 7 - Jan 13, 2013",
        ylabel="PV Solar Generation (kW)",
        actual_color="tab:orange",
        pred_color="tab:green",
    )

    print("  Rendering plot windows, close them to end code execution :)")
    plt.show()
    # <<< CHANGE 10b END
    # =====================================================================



if __name__ == "__main__":
    main()