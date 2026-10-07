# Source review / integration changes

Inspected main commit: `3bc07f6f346789d763a6b326dead10a12d0e5272` (GitHub connector read during this request).

## Source-supported interfaces

- `experiment1_applied.py`, blob `61c120663eb21cdc291e4e4663e855f0bffc9a1a`: forecast columns `Date,N_Customers,Profile,48 time columns`; actual columns `Date,Node,Phase,N_Customers,Profile,48 time columns`. Uses `--input` and `--actual`; output name set by `--output` with timestamp. Modbus TCP 502, holding 2000–2063 with mixed normal/reverse order; SoC input 3000, divided by 100 gives percent.
- `experiment2_submission.py`, blob `7e366d8e1eac43a19dd0fde35710fe8ee232940f`: reads `--forecast`, flattens forecast days, takes future slices, calls QP each step and executes first action.

## Problems to avoid when using the original MPC main for these new forecasts

1. `soc_measured_646_CIL_kwh = (measured_soc_646/100)*args.capacity` scales a Node646 percentage by the WHOLE feeder capacity. The solver treats that variable as Node646 energy. In the new harness only Node646 capacity is used.
2. In dry-run/no-measurements the logger can return `None`; the above division would fail. The new harness has a separate ideal-state offline path.
3. Concatenating daily re-issued forecasts and slicing across midnight can consume a forecast not yet available at the simulated time. The module exports separately issued windows; the new harness uses them.
4. The MPC terminal SOC equality is commented out while the QP daily net-energy constraint is active. A direct cost comparison can therefore use different terminal resources. The new harness uses a common next-midnight energy target; this changes the experiment and is documented, not silently described as original MPC.
5. Original `grid_kw` is calculated from actual inputs and battery commands, not a measured feeder power sensor. The new harness explicitly labels it `grid_balance_CALCULATED_kw`.

## Limits of this audit

The source was read, not physically executed against HIL. No original repository file was overwritten or committed. No compiled model was modified. The independent offline harness was executed with a mathematical ideal battery; that does not certify hardware timing, mapping, metering, stability, or safety.

The live branch reuses the QP source's transport/encoding, after a blob-hash and customer-map check. It still requires the user to verify actual lab mapping, time scaling and the physical source of input register 3000. This is especially important if the team redirected it to an external emulator.
