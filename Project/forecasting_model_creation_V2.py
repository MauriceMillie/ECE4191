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

from sklearn.base import clone


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

# Typed in by hand i mighta done it wrong ;-; (hopefully correct tho)
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
    temp_df = temp_df.sort_values("date").reset_index(drop=True)
    s = temp_df.set_index("date")[data_col]
    temp_df["Prev_Day_Max"] = s.reindex(s.index - pd.Timedelta(days=1)).to_numpy()
    temp_df["Prev_Day_Max"] = temp_df["Prev_Day_Max"].fillna(temp_df[data_col])
    temp_df["Max_3d_Mean"] = s.rolling("3D").mean().to_numpy()   # today + previous 2 days
    return temp_df


def add_min_temp(temp_df, min_temp_data_path):
    min_df = format_bom_data(min_temp_data_path, MIN_TEMP_COL)
    min_df["date"] = pd.to_datetime(min_df["date"], format="%d/%m/%Y")
    temp_df = temp_df.merge(min_df, on="date", how="left")
    temp_df[MIN_TEMP_COL] = temp_df[MIN_TEMP_COL].ffill().bfill()
    return temp_df


def add_prev_day_load(df, source_df, value_col="Load_kW"):
    lag = source_df[["date", "Hour", value_col]].copy()
    lag["date"] = lag["date"] + pd.Timedelta(days=1)
    lag = lag.rename(columns={value_col: "Load_Prev_Day"})
    return df.merge(lag, on=["date", "Hour"], how="left")


def wape(y_true, y_pred):
    # Weighted absolute percentage error: total error / total actual.
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    return float(np.abs(y_true - y_pred).sum() / np.abs(y_true).sum())


def masked_mape(y_true, y_pred, min_actual=0.01):
    # MAPE over daylight slots only (actual above a small threshold) # the normal mape didnt work because solar has lots of 0s
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    m = y_true > min_actual
    if not m.any():
        return float("nan")
    return float(np.mean(np.abs(y_true[m] - y_pred[m]) / y_true[m]))


def report_metrics(label, y_true, y_pred, dates, exclude_date=None, min_actual=0.01):
    # prints metrics. can exclude the outlier day if we need to make the argument that our model would perform better than it seems due to test week outlier
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


def compare_feature_sets(model, x_train, y_train, train_dates, feature_sets, weeks):
    # makes model/data validation weeks that at different periods. to compare v1 feature set to v2 across different test weeks
    # running this takes way longer soooooo maybe turn this off unless you are trying to get data for something.
    train_dates = pd.Series(pd.to_datetime(train_dates)).reset_index(drop=True)
    for start, end in weeks:
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        in_val = train_dates.between(start, end)
        leave_out = train_dates.between(start, end + pd.Timedelta(days=1))
        print(f"\n  Validation week {start:%d %b %Y} - {end:%d %b %Y}")
        for name, cols in feature_sets.items():
            m = clone(model).fit(x_train.loc[~leave_out, cols], y_train[~leave_out])
            pred = m.predict(x_train.loc[in_val, cols])
            y = y_train[in_val]
            print(
                f"    {name:<16} MAE {mean_absolute_error(y, pred):.3f} | WAPE {wape(y, pred):.1%} | "
                f"MAPE {masked_mape(y, pred):.1%} | R2 {r2_score(y, pred):.3f}"
            )


def p_initialize_model(p_data_path1, p_data_path2, temp_data_path, min_temp_data_path=None):

    df_p_2011_2012 = format_provided_p_data(p_data_path1, "load")
    df_p_2012_2013 = format_provided_p_data(p_data_path2, "load")

    data_col = "Maximum temperature (Degree C)"
    temp_df = format_bom_data(temp_data_path, data_col)

    full_power_df = pd.concat([df_p_2011_2012, df_p_2012_2013], ignore_index=True)

    start_test_date = pd.to_datetime("07/01/2013", format="%d/%m/%Y") # I SHOULD PROBS CHANGE THIS TO THE 5TH or something
    end_test_date = pd.to_datetime("13/01/2013", format="%d/%m/%Y")

    full_power_df["date"] = pd.to_datetime(full_power_df["date"], format="%d/%m/%Y")
    temp_df["date"] = pd.to_datetime(temp_df["date"], format="%d/%m/%Y")


    temp_df = add_temp_history_features(temp_df, data_col)
    extra_temp_cols = ["Prev_Day_Max", "Max_3d_Mean"]
    if min_temp_data_path:
        temp_df = add_min_temp(temp_df, min_temp_data_path)
        extra_temp_cols.append(MIN_TEMP_COL)

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


    for _df in (final_train_dataset, final_test_dataset):
        _df["Is_Holiday"] = _df["date"].isin(NSW_PUBLIC_HOLIDAYS).astype(int)

    _train_only = final_train_dataset[['date', 'Hour', 'Load_kW']]
    _train_plus_test = pd.concat([_train_only, final_test_dataset[['date', 'Hour', 'Load_kW']]])
    final_train_dataset = add_prev_day_load(final_train_dataset, _train_only)
    final_test_dataset = add_prev_day_load(final_test_dataset, _train_plus_test)
    final_train_dataset = final_train_dataset.dropna(subset=["Load_Prev_Day"]).reset_index(drop=True)
    if final_test_dataset["Load_Prev_Day"].isna().any():
        print("WARNING: some test rows have no previous-day load (missing day in the data).")


    features = [
        "Hour",
        "Month",
        "Day_of_Week",
        "Season",
        data_col,
    ]


    features = features + extra_temp_cols + ["Is_Holiday", "Load_Prev_Day"]

    p_x_train = final_train_dataset[features]
    p_y_train = final_train_dataset["Load_kW"]

    p_x_final_test = final_test_dataset[features]
    p_y_final_test = final_test_dataset["Load_kW"]


    date_info = {"train": final_train_dataset["date"].reset_index(drop=True),
                 "test": final_test_dataset["date"].reset_index(drop=True)}
    return p_x_train, p_y_train, p_x_final_test, p_y_final_test, date_info


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


    date_info = {"train": final_train_dataset["date"].reset_index(drop=True),
                 "test": final_test_dataset["date"].reset_index(drop=True)}
    return p_x_train, p_y_train, p_x_final_test, p_y_final_test, date_info



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

    MIN_TEMP_PATH = "BOM_Data/IDCJAC0011_066137_1800_daily_min_temp/IDCJAC0011_066137_1800_Data.csv"
    if not Path(MIN_TEMP_PATH).exists():
        print(f"  (min temp file not found at {MIN_TEMP_PATH} - continuing without it)")
        MIN_TEMP_PATH = None

    p_x_train, p_y_train, p_x_test, p_y_test, p_dates = p_initialize_model(
        "Provided_Data/2011-2012Solarhomeelectricitydatav2.csv",
        "Provided_Data/2012-2013 Solar home electricity data v2.csv",
        "BOM_Data/IDCJAC0010_066137_1800_daily_max_temp/IDCJAC0010_066137_1800_Data.csv",
        min_temp_data_path=MIN_TEMP_PATH,
    )

    pv_x_train, pv_y_train, pv_x_test, pv_y_test, pv_dates = pv_initialize_model(
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


    RUN_VALIDATION = True   # set False to skip. when true it can make the code take kinda ages on certain machines
    VALIDATION_WEEKS = [("2012-01-09", "2012-01-15"), ("2012-02-06", "2012-02-12")]
    if RUN_VALIDATION:
        print("\nComparing feature sets on validation weeks (training data only)...")
        base_cols = ["Hour", "Month", "Day_of_Week", "Season", "Maximum temperature (Degree C)"]
        compare_feature_sets(
            load_model, p_x_train, p_y_train, p_dates["train"],
            {"baseline (5)": base_cols, f"new ({p_x_train.shape[1]})": list(p_x_train.columns)},
            VALIDATION_WEEKS,
        )

    print("Training Random Forest Regressors (using all CPU cores)...")
    load_model.fit(p_x_train, p_y_train)
    print("  Load Model training completed successfully.")

    pv_model.fit(pv_x_train, pv_y_train)
    print("  PV Model training completed successfully.")

    print("Executing forecasts across the evaluation timeline...")
    pred_single_L = load_model.predict(p_x_test)
    pred_single_P = pv_model.predict(pv_x_test)

    print("Freezing models and writing compressed .pkl binaries...")
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

    # more metrics data added for V2/V3
    report_metrics(
        "LOAD", y_test_agg_L, scaled_pred_load, p_dates["test"],
        exclude_date="2013-01-08",   # DAY 2, THE OUTLIER 42DEGC DAY
        min_actual=0.01,
    )
    report_metrics(
        "PV", y_test_agg_P, scaled_pred_pv, pv_dates["test"],
        min_actual=0.05,   # MAPE only counted when PV output > 0.05 kW (skips night and dawn/dusk)
    )

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
            "Date": p_dates["test"].to_numpy(),
            "Hour": p_x_test["Hour"],
            "Predicted_Average_Load_kW": scaled_pred_load,
            "Predicted_Average_PV_Gen_kW": scaled_pred_pv,
        }
    )

    export_filename = "./Code_and_Data/average_household_forecasts_v3.csv"
    export_df.to_csv(export_filename, index=False)
    print(f"  Saved successfully as '{export_filename}'.")


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



if __name__ == "__main__":
    main()