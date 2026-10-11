"""Plot + score the controller's live forecast against the actuals it played back.
Usage: python plot_fc_vs_actual.py Output/mpc_feeder_schedule_XXXX.csv   (defaults to the newest file in Output/)"""
import sys, glob, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob("Output/mpc_feeder_schedule_*.csv"), key=os.path.getmtime)
d = pd.read_csv(path)
nodes = sorted({c.split("_p_load_fc_kw")[0] for c in d.columns if c.endswith("_p_load_fc_kw")})

def tot(suffix): return d[[f"{n}_{suffix}" for n in nodes]].sum(axis=1).to_numpy()
series = {
    "Feeder total load": (tot("p_load_fc_kw"), tot("p_load_actual_kw")),
    "Feeder total PV":   (tot("p_pv_fc_kw"),   tot("p_pv_actual_kw")),
    "646_B load":        (d["646_B_p_load_fc_kw"].to_numpy(), d["646_B_p_load_actual_kw"].to_numpy()),
}
fig, axs = plt.subplots(len(series), 1, figsize=(14, 9), sharex=True)
print(f"file: {path}   steps: {len(d)}")
for ax, (name, (fc, ac)) in zip(axs, series.items()):
    ax.plot(ac, label="actual", lw=1.2); ax.plot(fc, label="live forecast", lw=1.2); ax.set_title(name); ax.legend(loc="upper right")
    wape = np.abs(fc - ac).sum() / max(ac.sum(), 1e-9) * 100
    print(f"{name:20s} WAPE {wape:5.1f}%  | std actual {ac.std():8.1f}  std forecast {fc.std():8.1f}  "
          f"| per-day peak actual/forecast: " +
          "  ".join(f"{ac[i:i+48].max():.0f}/{fc[i:i+48].max():.0f}" for i in range(0, len(ac), 48)))
axs[-1].set_xlabel("MPC step (48 per day)")
plt.tight_layout(); out = os.path.splitext(path)[0] + "_fc_vs_actual.png"; plt.savefig(out, dpi=110); print("saved", out)