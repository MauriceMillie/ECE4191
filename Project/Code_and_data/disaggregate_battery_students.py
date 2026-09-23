#!/usr/bin/env python3
"""
disaggregate_battery_toy.py  --  ECE4191 Module 3 (toy example, 1 day)

Input : # 1. Read the single battery row. The 48 time labels become the columns.
Output: per-node battery values -- one row per node, same 48 time columns.

Split rule:  P_bat_node = battery * (customers_node / total_customers)
"""

import pandas as pd

# --- Customers per node --------------------------------------------------
# Hard-coded from the "N_Customers" column of agg_jan2013_students.csv
# (one entry per Node+Phase group; total = 1330 customers).
N_CUSTOMERS = {
    "646_B": 102, "645_B":  63, "611_C":  68, "652_A":  46,
    "671_A": 159, "671_B": 155, "671_C": 159,
    "692_A":   0, "692_B":   0, "692_C":  66,
    "675_A": 191, "675_B":  36, "675_C": 119,
    "634_A":  69, "634_B":  45, "634_C":  52,
}
TOTAL = sum(N_CUSTOMERS.values())   # 1330

INPUT_CSV  = "central_battery_input_1_day_students.csv"
OUTPUT_CSV = "Battery_Power_per_node_1_day.csv"

# 1. Read the battery row. index_col=0 drops the "Time"/"Battery_Power_kW"
#    label column, leaving the 48 time labels as the columns.
df = pd.read_csv(INPUT_CSV)
time_cols = list(df.columns)          # 48 time labels: 0:30 ... 0:00
battery = df.iloc[0]                   # the single day's battery array

# 2. Split per node by customer share; one output row per node.
rows = []
for node, n in N_CUSTOMERS.items():
    row = {"Node": node}
    row.update((t, battery[t] * (n / TOTAL)) for t in time_cols)
    rows.append(row)

# 3. Write per-node battery values.
out = pd.DataFrame(rows, columns=["Node"] + time_cols)
out.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote {OUTPUT_CSV}: {out.shape[0]} nodes x {len(time_cols)} steps")