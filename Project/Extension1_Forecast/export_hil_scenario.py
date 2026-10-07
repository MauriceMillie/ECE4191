#!/usr/bin/env python3
"""Opt-in NEW proportional HIL scenario. Does not reconstruct the course mapping.
Copies no original actual values. Forecast AND actual use identical fixed weights.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
from datetime import date
import numpy as np
from forecast_module import write_csv,write_central,label,SLOTS,PROFILES

# Repository Project/experiment1_applied.py at commit 3bc07f6...
COUNTS={'646_B':102,'645_B':63,'611_C':68,'652_A':46,
        '671_A':159,'671_B':155,'671_C':159,'692_A':0,'692_B':0,'692_C':66,
        '675_A':191,'675_B':36,'675_C':119,'634_A':69,'634_B':45,'634_C':52}
REPO_COMMIT='3bc07f6f346789d763a6b326dead10a12d0e5272'


def export(bundle:Path,out:Path,accepted=False,overwrite=False):
    if not accepted: raise ValueError('Required: --accept-new-scenario. This is NOT the original course actual scene.')
    bundle=Path(bundle);out=Path(out)
    if out.exists() and any(out.iterdir()) and not overwrite: raise FileExistsError('Output exists; choose a new folder or --overwrite.')
    manifest=json.loads((bundle/'manifest.json').read_text(encoding='utf-8'))
    with np.load(bundle/'forecast_bundle.npz',allow_pickle=False) as f: z={k:f[k].copy() for k in f.files}
    if not np.isfinite(z['actual_kw']).all():
        raise ValueError('Test actuals are incomplete. Forecast-only outputs cannot be played as measured ground truth.')
    n=len(z['customers']);total=sum(COUNTS.values());scale=total/n
    out.mkdir(parents=True,exist_ok=True)
    dates=[date.fromisoformat(x) for x in z['dates'].tolist()]
    actual=z['actual_kw']*scale;forecast=z['forecast_kw']*scale
    write_central(out/'forecast_5day_central.csv',dates,forecast,total)
    write_central(out/'actual_5day_central.csv',dates,actual,total)
    write_central(out/'perfect_5day_central_reference.csv',dates,actual,total)
    for fname,data in [('actual_5day_nodes.csv',actual),('forecast_5day_nodes.csv',forecast)]:
        rows=[]
        for di,d in enumerate(dates):
            for group,count in COUNTS.items():
                node,phase=group.split('_')
                for pi,profile in enumerate(PROFILES):
                    values=data[di,pi]*count/total
                    if np.max(np.abs(values))>32767: raise ValueError('Node input would exceed signed 16-bit engineering units.')
                    rows.append([label(d),int(node),phase,count,profile,*values.tolist()])
        write_csv(out/fname,['Date','Node','Phase','N_Customers','Profile',*SLOTS],rows)
    groups=list(COUNTS);shares=np.array(list(COUNTS.values()),float)/total
    np.savez_compressed(out/'controller_inputs.npz',
        dates=z['dates'],step_start=z['step_start'],issue_time=z['issue_time'],
        forecast_kw=forecast,actual_kw=actual,persistence_kw=z['persistence_kw']*scale,
        mpc_load_kw=z['mpc_load_kw']*scale,mpc_pv_kw=z['mpc_pv_kw']*scale,
        group_names=np.array(groups),group_shares=shares,counts=np.array(list(COUNTS.values())))
    write_csv(out/'scenario_weights.csv',['group','virtual_customers','weight_of_SOURCE_cohort','share_of_virtual_total'],
              ([g,c,c/n,c/total] for g,c in COUNTS.items()))
    report={'scenario_type':'NEW_proportional_annual_data_scene','source_cohort_size':n,
            'virtual_customers':total,'scale_of_total':scale,'forecast_manifest':manifest,
            'course_mapping_reconstructed':False,'scaling_rule':'Each node = SOURCE cohort total * node_customer_count / source_cohort_size.',
            'counts_basis':f'GitHub {REPO_COMMIT}: Project/experiment1_applied.py N_CUSTOMERS',
            'same_scaling_for_forecast_and_actual':True,
            'battery_parameters_from_repo':{'capacity_kwh':13300.,'power_kw':6650.,'initial_soc_kwh':6650.},
            'operator_approval_still_required':True,'hardware_tested':False,
            'warnings':['All nonzero nodes share the same normalised curve. Not independent node-level prediction evidence.',
                        '1330 VIRTUAL customers, NOT 1330 independent measured households.',
                        'This retains the source load/PV per-customer ratio but does not reproduce course voltages.',
                        'Do NOT pair these forecasts with original agg_jan2013_students.csv.',
                        'Verify topology, Qref, SoC scaling and sample period with TA before live use.']}
    (out/'scenario.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--accept-new-scenario',action='store_true')
    p.add_argument('--overwrite',action='store_true');a=p.parse_args(argv)
    try:
        r=export(a.bundle,a.out,a.accept_new_scenario,a.overwrite)
        print(f"Exported NEW scene: {a.out.resolve()}\n{r['source_cohort_size']} source households -> {r['virtual_customers']} virtual customers.")
        print('Not the original course scene. No hardware was contacted.')
        return 0
    except (ValueError,FileNotFoundError,FileExistsError) as e:
        print(f'ERROR: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
