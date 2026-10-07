#!/usr/bin/env python3
"""Align a USER-EXPORTED Signal Analyzer channel to controller write timestamps.

Requires explicit column names, units, and the first-write time on the Signal
Analyzer time axis. It does not invent a timing offset or infer signal identity.
Export voltages and feeder power BEFORE stopping HIL SCADA (Module 3, p.27).
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
from forecast_module import write_csv


def read_table(path:Path,skip:int=0,delimiter:str|None=None):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for _ in range(skip): next(f)
        sample=f.read(8192);f.seek(0)
        for _ in range(skip):next(f)
        delim=delimiter or csv.Sniffer().sniff(sample,delimiters=',;\t').delimiter
        r=csv.DictReader(f,delimiter=delim);headers=r.fieldnames
        if not headers:raise ValueError('No CSV header. Specify --skip-rows for preamble lines.')
        return headers,list(r)


def analyse(csv_path,log_path,time_column,value_column,unit,first_write_sa,out,settle=.25,skip=0,delimiter=None,kind='grid'):
    headers,raw=read_table(csv_path,skip,delimiter)
    if time_column not in headers or value_column not in headers:raise ValueError(f'Columns not found. Actual: {headers}')
    t=np.array([float(r[time_column]) for r in raw]);v=np.array([float(r[value_column]) for r in raw])
    if not np.isfinite(t).all() or not np.isfinite(v).all():raise ValueError('Nonfinite samples; review export rather than silently drop.')
    if (np.diff(t)<0).any():raise ValueError('Signal Analyzer times must be sorted.')
    if kind=='grid' and unit not in ('W','kW'):raise ValueError('Grid channel requires W or kW.')
    if kind=='voltage' and unit not in ('V','pu'):raise ValueError('Voltage channel requires V or pu.')
    if unit=='W':v=v/1000.
    _,logs=read_table(log_path)
    if not logs or any(r['run_type']!='HIL' for r in logs):raise ValueError('Use a HIL log, not an offline log.')
    origin=float(logs[0]['send_or_calculate_unix_s']);rel=t-first_write_sa;result=[]
    for i,r in enumerate(logs):
        start=float(r['send_or_calculate_unix_s'])-origin
        end=(float(logs[i+1]['send_or_calculate_unix_s']) if i+1<len(logs) else float(r['interval_end_unix_s']))-origin
        mask=(rel>=start+settle)&(rel<end)
        vals=v[mask];count=int(mask.sum());avg=float(vals.mean()) if count else None
        reference=float(r['grid_balance_CALCULATED_kw']) if kind=='grid' else None
        result.append([r['step'],r['dataset_step_start'],count,avg,
                       float(vals.min()) if count else None,float(vals.max()) if count else None,
                       reference,None if avg is None or reference is None else avg-reference])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'hil_channel_by_step.csv',
              ['step','dataset_step_start','samples_after_settle','measured_sample_mean','measured_min','measured_max','calculated_reference_kw','measured_minus_calculated_kw'],result)
    summary={'source_csv':str(csv_path),'controller_log':str(log_path),'channel':value_column,
             'output_unit':'kW' if kind=='grid' else unit,'kind':kind,'first_write_sa_seconds':first_write_sa,
             'settling_seconds_excluded_each_step':settle,'steps':len(result),'steps_without_samples':sum(r[2]==0 for r in result),
             'method':'mean/min/max of logged samples between consecutive writes after fixed settling exclusion; not a continuous-time guarantee',
             'energy_kwh_estimated_from_sample_means':sum(r[3]*.5 for r in result) if kind=='grid' and all(r[2]>0 for r in result) else None,
             'warning':'Check sign and location of the measured power channel. Feeder losses can make measured head power differ from load-PV-battery.'}
    (out/'hil_analysis.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--csv',type=Path,required=True)
    p.add_argument('--list-columns',action='store_true');p.add_argument('--skip-rows',type=int,default=0);p.add_argument('--delimiter')
    p.add_argument('--log',type=Path);p.add_argument('--time-column');p.add_argument('--value-column')
    p.add_argument('--unit',choices=['W','kW','V','pu']);p.add_argument('--kind',choices=['grid','voltage'],default='grid')
    p.add_argument('--first-write-sa-seconds',type=float);p.add_argument('--settle-seconds',type=float,default=.25)
    p.add_argument('--out',type=Path,default=Path('Output/Extension1/HIL_analysis'));a=p.parse_args(argv)
    try:
        if a.list_columns:
            print('\n'.join(read_table(a.csv,a.skip_rows,a.delimiter)[0]));return 0
        if any(x is None for x in (a.log,a.time_column,a.value_column,a.unit,a.first_write_sa_seconds)):
            raise ValueError('--log, --time-column, --value-column, --unit and --first-write-sa-seconds are required.')
        result=analyse(a.csv,a.log,a.time_column,a.value_column,a.unit,a.first_write_sa_seconds,a.out,
                       a.settle_seconds,a.skip_rows,a.delimiter,a.kind)
        print(json.dumps(result,indent=2));return 0
    except Exception as e:print(f'ERROR: {e}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
