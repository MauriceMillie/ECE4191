"""Is the playback data on the same scale as the data the models were trained on?
Compares the creation script's exported test-week forecast (per household) with the playback actuals (per household).
Usage: python check_scale.py Code_and_Data/average_household_forecasts_v3.csv Code_and_Data/agg_jan2013_students.csv"""
import sys, numpy as np, pandas as pd
fc = pd.read_csv(sys.argv[1]); act = pd.read_csv(sys.argv[2])
L = pd.to_numeric(fc["Predicted_Average_Load_kW"]).to_numpy(); P = pd.to_numeric(fc["Predicted_Average_PV_Gen_kW"]).to_numpy()
tcols = list(act.columns[5:53]); N = act.drop_duplicates(["Node", "Phase"]).N_Customers.sum()
print(f"customers in playback file: {N}")
print(f"{'day':10s} {'load kWh/hh actual':>19s} {'forecast':>9s} {'ratio':>6s} | {'PV kWh/hh actual':>17s} {'forecast':>9s} {'ratio':>6s}")
for i, day in enumerate(dict.fromkeys(act["Date"])):
    a = act[act.Date == day]
    al = a[a.Profile == "GC_Load_kW"][tcols].sum().sum() / N * 0.5
    ap = a[a.Profile == "PV_Generation_kW"][tcols].sum().sum() / N * 0.5
    fl = L[i*48:(i+1)*48].sum() * 0.5 if len(L) >= (i+1)*48 else float("nan")
    fp = P[i*48:(i+1)*48].sum() * 0.5 if len(P) >= (i+1)*48 else float("nan")
    print(f"{day:10s} {al:19.2f} {fl:9.2f} {al/fl:6.2f} | {ap:17.2f} {fp:9.2f} {ap/fp:6.2f}")
print("\nA ratio that is ~2.0 for BOTH load and PV on days the model scored well (Mon/Thu) points to a units mismatch "
      "(kWh per 30 min vs kW). Ratios that differ between load and PV point to a different household population.")