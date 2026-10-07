#!/usr/bin/env python3
"""ECE4191 aggregate day-ahead forecasting, not a HIL controller.

Forecast each half-hour using the previous 30 completed days and, when supplied,
the same calendar date last year. Every MPC window is built from its own issue
information set; concatenated daily re-forecasts are NOT sliced across issues.
Raw files are never modified. No network access or hardware writes occur.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Sequence
import numpy as np

VERSION = '2.0.0'
DT_H = 0.5
SLOTS = [f'{k//2}:{30*(k%2):02d}' for k in range(1,48)] + ['0:00']
PROFILES = ('GC_Load_kW', 'PV_Generation_kW')
CATEGORIES = ('GC', 'GG', 'CL')
MONTHS = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')

def iso_date(s: str) -> date:
    return date.fromisoformat(s)

def raw_date(s: str) -> date:
    s=s.strip()
    if '/' in s:
        d,m,y=map(int,s.split('/')); return date(y,m,d)
    return date.fromisoformat(s)

def label(d: date) -> str:
    return f'{d.day}-{MONTHS[d.month-1]}-{d.year%100:02d}'

def last_year(d: date) -> date:
    # Explicit leap-day policy: use February 28, not an unexplained -365 shift.
    try: return d.replace(year=d.year-1)
    except ValueError: return date(d.year-1,2,28)

def write_csv(path: Path, headers: Sequence[str], rows) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(headers); w.writerows(rows)

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

@dataclass
class RawData:
    # (date, category, customer) -> (48 interval-energy values, quality string)
    records: dict
    dates: list[date]
    customers: list[int]
    sources: list[dict]
    rows: int


def read_raw(paths: Sequence[Path], raw_unit='kwh-per-interval') -> RawData:
    """Read Ausgrid's introductory line + header, preserving literal NA quality."""
    records={}; dates=set(); customers=set(); sources=[]; row_count=0
    seen_hash=set()
    for path in paths:
        path=Path(path).resolve()
        if not path.is_file(): raise FileNotFoundError(f'Raw CSV not found: {path}')
        sha=digest(path)
        if sha in seen_hash:
            raise ValueError('The same raw file was supplied twice (identical SHA256).')
        seen_hash.add(sha)
        sources.append({'file':path.name,'sha256':sha,'bytes':path.stat().st_size})
        with path.open('r',newline='',encoding='utf-8-sig') as f:
            reader=csv.reader(f); header=None
            for _ in range(8):
                row=next(reader,None)
                if row is None: break
                if row and row[0].strip()=='Customer':
                    header=[x.strip() for x in row]; break
            if header is None: raise ValueError(f'{path.name}: Customer header not found.')
            if len(set(header)) != len(header): raise ValueError('Duplicate raw column names.')
            required=['Customer','Consumption Category','date',*SLOTS]
            missing=set(required)-set(header)
            if missing: raise ValueError(f'Wrong CSV schema: missing {sorted(missing)}')
            ix={n:header.index(n) for n in required}
            qi=header.index('Row Quality') if 'Row Quality' in header else None
            idx=[ix[n] for n in SLOTS]
            for line_no,row in enumerate(reader, 3):
                if not row or not any(v.strip() for v in row): continue
                if len(row)!=len(header): raise ValueError(f'{path.name}:{line_no}: wrong number of fields.')
                cat=row[ix['Consumption Category']].strip()
                if cat not in CATEGORIES: raise ValueError(f'Unknown category: {cat}')
                customer=int(row[ix['Customer']]); d=raw_date(row[ix['date']])
                key=(d,cat,customer)
                if key in records: raise ValueError(f'Duplicate customer/date/category {key}.')
                vals=np.array([row[i].strip() or 'nan' for i in idx], dtype=float)
                if np.isinf(vals).any() or (vals[np.isfinite(vals)]<0).any():
                    raise ValueError(f'{key}: negative or infinite energy.')
                if raw_unit=='kw': vals=vals*DT_H
                elif raw_unit!='kwh-per-interval': raise ValueError('Unsupported raw unit.')
                quality=row[qi].strip() if qi is not None else ''
                records[key]=(vals, quality)
                dates.add(d); customers.add(customer); row_count+=1
    return RawData(records,sorted(dates),sorted(customers),sources,row_count)


def usable(record, quality='include-flagged') -> bool:
    return record is not None and np.isfinite(record[0]).all() and (quality=='include-flagged' or not record[1])


def select_cohort(data: RawData, first_issue: date, window: int,
                  quality: str, ids_path: Path|None=None) -> tuple[list[int],list[int]]:
    """Choose ONE fixed cohort from pre-test data only. Never select on test quality."""
    training=[first_issue-timedelta(days=k) for k in range(window,0,-1)]
    missing=[d for d in training if d not in data.dates]
    if missing: raise ValueError(f'Previous {window} full days not available; first missing date {missing[0]}.')
    candidates=sorted({c for (d,cat,c) in data.records if training[0]<=d<first_issue and cat in ('GC','GG')})
    if ids_path:
        text=Path(ids_path).read_text(encoding='utf-8-sig')
        chosen=sorted(set(int(x.strip()) for x in text.replace('\n',',').split(',') if x.strip()))
        if not chosen: raise ValueError('Empty customer ID file.')
        if not set(chosen)<=set(candidates): raise ValueError('Some requested IDs have no pre-test records.')
        bad=[c for c in chosen if not all(usable(data.records.get((d,cat,c)),quality) for d in training for cat in ('GC','GG'))]
        if bad: raise ValueError(f'Fixed requested IDs incomplete in initial history: {bad}')
    else:
        chosen=[c for c in candidates if all(usable(data.records.get((d,cat,c)),quality) for d in training for cat in ('GC','GG'))]
    if not chosen: raise ValueError('No complete fixed cohort in initial history.')
    return chosen, sorted(set(candidates)-set(chosen))


def aggregate_day(data: RawData, d: date, customers: Sequence[int], quality='include-flagged'):
    """Return (2,48) kW, availability and number of flagged source rows.
    Do not turn a missing household into a zero-demand household.
    """
    result=np.full((2,48),np.nan); flags=0; counts=[]
    for pi,cat in enumerate(('GC','GG')):
        rows=[data.records.get((d,cat,c)) for c in customers]
        good=[usable(r,quality) for r in rows]
        counts.append(sum(good))
        flags+=sum(bool(r and r[1]) for r in rows)
        if all(good): result[pi]=np.sum([r[0] for r in rows],axis=0)/DT_H
    return result, bool(np.isfinite(result).all()), flags, counts


def daily_report(data: RawData):
    """Descriptive raw totals only: all available rows, with coverage/quality flags."""
    totals={(d,c):[0.0,0,0,0] for d in data.dates for c in CATEGORIES}
    for (d,cat,c),(v,q) in data.records.items():
        item=totals[(d,cat)]; item[0]+=float(np.nansum(v)); item[1]+=1
        item[2]+=int(bool(q)); item[3]+=int((~np.isfinite(v)).sum())
    for d in data.dates:
        gc,gg,cl=(totals[(d,c)] for c in CATEGORIES)
        yield [d.isoformat(),gc[0],cl[0],gc[0]+cl[0],gg[0],gc[0]-gg[0],
               gc[1],gg[1],cl[1],gc[2]+gg[2]+cl[2],gc[3]+gg[3]+cl[3]]


def predict_issue(data: RawData, issue: date, customers: Sequence[int], *,
                  window=30, alpha=0.5, method='hybrid', missing_year='error', quality='include-flagged'):
    """Issue 2 days at 00:00 using history ending strictly before issue.
    Second day is provisional, generated NOW, not tomorrow's re-issued forecast.
    """
    hist_dates=[issue-timedelta(days=k) for k in range(window,0,-1)]
    hist=[]; flagged=0
    for d in hist_dates:
        v,ok,q,_=aggregate_day(data,d,customers,quality)
        if not ok: raise ValueError(f'{issue}: history incomplete on {d} for the FIXED cohort. No test-dependent re-selection.')
        hist.append(v); flagged+=q
    hist=np.stack(hist); recent=hist.mean(axis=0)
    out=[]; audit=[]
    for lead in range(2):
        target=issue+timedelta(days=lead); ydate=last_year(target)
        y,ok,q,_=aggregate_day(data,ydate,customers,quality)
        if method=='persistence':
            pred=hist[-1].copy(); eff_alpha=None; used='persistence'; prior_used=False
        elif method=='recent30' or alpha==1:
            pred=recent.copy(); eff_alpha=1.; used='recent30'; prior_used=False
        elif method=='hybrid' and ok:
            pred=alpha*recent+(1-alpha)*y; eff_alpha=alpha; used='hybrid'; prior_used=True
        elif method=='hybrid' and missing_year=='recent':
            pred=recent.copy(); eff_alpha=1.; used='recent30_missing_prior_year'; prior_used=False
        else:
            raise ValueError(f'{target}: missing last-year reference {ydate} for fixed cohort. '
                             'Supply 2011-2012 raw CSV too, or explicitly choose --missing-year recent. '
                             'The two-year blend is NOT available for this date.')
        assert hist_dates[-1]<issue and ydate<issue
        out.append(pred)
        audit.append({'issue_time':datetime.combine(issue,time()).isoformat(),
                      'target_date':target.isoformat(),'lead_days':lead+1,
                      'history_start':hist_dates[0].isoformat(),'history_end':hist_dates[-1].isoformat(),
                      'history_days':window,'prior_year_date':ydate.isoformat(),
                      'prior_year_available':ok,'prior_year_used':prior_used,
                      'method_used':used,'effective_recent_weight':eff_alpha,
                      'history_flagged_rows':flagged,'prior_year_flagged_rows':q if prior_used else 0})
    return np.concatenate(out,axis=1), audit # (2,96)


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    a=np.asarray(actual,float); p=np.asarray(predicted,float)
    mask=np.isfinite(a)&np.isfinite(p)
    if not mask.any(): return {'n':0,'mae_kw':None,'rmse_kw':None,'bias_kw':None,'wape_percent':None}
    e=p[mask]-a[mask]; denom=np.abs(a[mask]).sum()
    return {'n':int(mask.sum()),'mae_kw':float(np.abs(e).mean()),'rmse_kw':float(np.sqrt(np.mean(e*e))),
            'bias_kw':float(e.mean()),'wape_percent':float(100*np.abs(e).sum()/denom) if denom>0 else None}


def write_central(path:Path, dates:Sequence[date], arrays:np.ndarray, n_customers:int):
    # arrays: (days,2,48); explicit customer count, no implicit 1330 scaling.
    write_csv(path,['Date','N_Customers','Profile',*SLOTS],
              ([label(d),n_customers,p,*arrays[i,pi].tolist()] for i,d in enumerate(dates) for pi,p in enumerate(PROFILES)))


def plot_results(bundle:Path) -> None:
    """Separate Matplotlib figures, library default colours; never requires GUI."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    with np.load(Path(bundle)/'forecast_bundle.npz',allow_pickle=False) as z:
        dates=[date.fromisoformat(d) for d in z['dates'].tolist()]
        actual=z['actual_kw']; pred=z['forecast_kw']; base=z['persistence_kw']
    folder=Path(bundle)/'plots'; folder.mkdir(exist_ok=True)
    x=[datetime.combine(d,time())+timedelta(minutes=30*k) for d in dates for k in range(1,49)]
    for pi,p in enumerate(PROFILES):
        fig,ax=plt.subplots(figsize=(12,4.5))
        ax.plot(x,actual[:,pi].reshape(-1),label='Actual (fixed source cohort)')
        ax.plot(x,pred[:,pi].reshape(-1),'--',label='Selected forecast; see issue_log.csv')
        ax.plot(x,base[:,pi].reshape(-1),':',label='Persistence baseline',alpha=.7)
        ax.set(title=f'Aggregate {p} | day-ahead backtest',ylabel='Average power (kW)',xlabel='Interval-ending time (dataset clock)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M'))
        ax.legend(); ax.grid(alpha=.25); fig.tight_layout(); fig.savefig(folder/f'{p}.png',dpi=150); plt.close(fig)


def build(raw:RawData, out:Path, start:date, days:int, *, window=30,alpha=.5,method='hybrid',
          missing_year='error',quality='include-flagged',ids_path:Path|None=None,overwrite=False):
    if days<1 or window<1 or not 0<=alpha<=1: raise ValueError('days/window must be positive; alpha in [0,1].')
    out=Path(out).resolve()
    # Prevent output being a raw-input directory containing arbitrary user data.
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise FileExistsError(f'Output is not empty: {out}. Use another folder or --overwrite.')
    cohort,excluded=select_cohort(raw,start,window,quality,ids_path)
    dates=[start+timedelta(days=d) for d in range(days)]
    pred=[]; actual=[]; persistence=[]; issues=[]; status=[]; win_l=[];win_p=[];step_starts=[];issue_times=[]
    for d in dates:
        p,audit=predict_issue(raw,d,cohort,window=window,alpha=alpha,method=method,missing_year=missing_year,quality=quality)
        b,_=predict_issue(raw,d,cohort,window=window,alpha=alpha,method='persistence',missing_year=missing_year,quality=quality)
        a,ok,flags,counts=aggregate_day(raw,d,cohort,quality)
        pred.append(p[:,:48]); actual.append(a); persistence.append(b[:,:48]); issues.extend(audit)
        status.append({'date':d.isoformat(),'actual_complete':ok,'gc_customer_rows':counts[0],
                       'gg_customer_rows':counts[1],'actual_flagged_rows':flags})
        for k in range(48):
            win_l.append(p[0,k:k+48]);win_p.append(p[1,k:k+48])
            step_starts.append((datetime.combine(d,time())+timedelta(minutes=30*k)).isoformat())
            issue_times.append(datetime.combine(d,time()).isoformat())
    pred=np.stack(pred); actual=np.stack(actual); persistence=np.stack(persistence)
    out.mkdir(parents=True,exist_ok=True)
    n=len(cohort)
    np.savez_compressed(out/'forecast_bundle.npz',dates=np.array([d.isoformat() for d in dates]),
                        actual_kw=actual,forecast_kw=pred,persistence_kw=persistence,customers=np.array(cohort),
                        mpc_load_kw=np.array(win_l),mpc_pv_kw=np.array(win_p),
                        step_start=np.array(step_starts),issue_time=np.array(issue_times),dt_hours=np.array(DT_H))
    write_central(out/'forecast_5day_central.csv',dates,pred,n)
    write_central(out/'actual_5day_central.csv',dates,actual,n)
    (out/'customer_ids.txt').write_text('\n'.join(map(str,cohort))+'\n',encoding='utf-8')
    write_csv(out/'issue_log.csv',list(issues[0]),([row[k] for k in issues[0]] for row in issues))
    write_csv(out/'actual_coverage.csv',list(status[0]),([row[k] for k in status[0]] for row in status))
    write_csv(out/'daily_totals_raw_reported.csv',
              ['date','gc_kwh','cl_kwh','gc_plus_cl_kwh','gg_kwh','gc_minus_gg_kwh','gc_rows','gg_rows','cl_rows','flagged_rows','missing_halfhours'],daily_report(raw))
    comparison=[]; daily=[]; scores=[]
    for i,d in enumerate(dates):
        for pi,profile in enumerate(PROFILES):
            for k in range(48):
                end=datetime.combine(d,time())+timedelta(minutes=30*(k+1))
                comparison.append([d.isoformat(),k+1,end.isoformat(),profile,float(actual[i,pi,k]),float(pred[i,pi,k]),float(persistence[i,pi,k])])
            ae=float(actual[i,pi].sum()*DT_H) if np.isfinite(actual[i,pi]).all() else None
            fe=float(pred[i,pi].sum()*DT_H)
            daily.append([d.isoformat(),profile,ae,fe,float(persistence[i,pi].sum()*DT_H),None if ae is None else fe-ae])
            for name,pvals in [('selected',pred),('persistence',persistence)]:
                m=metrics(actual[i,pi],pvals[i,pi]);scores.append([d.isoformat(),profile,name,*m.values()])
    for pi,profile in enumerate(PROFILES):
        for name,pvals in [('selected',pred),('persistence',persistence)]:
            m=metrics(actual[:,pi],pvals[:,pi]);scores.append(['ALL',profile,name,*m.values()])
    write_csv(out/'forecast_vs_actual.csv',['date','step_in_day','interval_end','profile','actual_kw','forecast_kw','persistence_kw'],comparison)
    write_csv(out/'daily_energy_forecast.csv',['date','profile','actual_kwh','forecast_kwh','persistence_kwh','error_kwh'],daily)
    write_csv(out/'forecast_metrics.csv',['date','profile','method','n','mae_kw','rmse_kw','bias_kw','wape_percent'],scores)
    manifest={'version':VERSION,'start':start.isoformat(),'days':days,'steps':days*48,'sample_customers':n,
              'customers':cohort,'excluded_pretest_incomplete_ids':excluded,'cohort_selected_using':f'{start-timedelta(days=window)}..{start-timedelta(days=1)} ONLY',
              'raw_sources':raw.sources,'raw_days':len(raw.dates),'raw_rows':raw.rows,
              'raw_start':raw.dates[0].isoformat(),'raw_end':raw.dates[-1].isoformat(),'quality_policy':quality,
              'load_definition':'GC only; CL reported separately, NOT added to control load',
              'output_units':'kW half-hour averages; daily energy = sum(kW)*0.5h',
              'raw_input_units_normalised_to':'kWh/half-hour; converted once to kW',
              'method_requested':method,'recent_days':window,'requested_recent_weight':alpha,'missing_year_policy':missing_year,
              'methods_used':sorted(set(x['method_used'] for x in issues)),
              'initial_daily_issue_time':'00:00 dataset clock; preceding full day assumed available',
              'mpc_policy':'48-step windows from latest midnight issue; second-day forecast formed at SAME issue; no intraday forecast corrections',
              'prior_year_rule':'same calendar date, February 29 -> February 28; no automatic weekday adjustment',
              'actual_complete':all(s['actual_complete'] for s in status),'actual_flagged_rows':sum(s['actual_flagged_rows'] for s in status),
              'not_done':['HIL experiment','customer-to-course-node reconstruction','trained AI model','tuned blend weights'],
              'warnings':['Not the original course node scene. Do not pair these forecasts with agg_jan2013_students.csv actuals.',
                          'HIL input export requires explicit new-scenario acceptance.',
                          'Raw totals may have changing record counts. Forecast uses a fixed PRE-TEST-selected cohort.',
                          'Two-year Customer ID continuity is an assumption to verify against the source notes.']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    return manifest


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw',type=Path,nargs='+',required=True,help='One or more annual CSVs; quote paths with spaces.')
    p.add_argument('--start',type=iso_date,default=date(2013,1,7));p.add_argument('--days',type=int,default=5)
    p.add_argument('--window',type=int,default=30);p.add_argument('--alpha',type=float,default=.5)
    p.add_argument('--method',choices=['hybrid','recent30','persistence'],default='hybrid')
    p.add_argument('--missing-year',choices=['error','recent'],default='error',help='No silent fallback: default error.')
    p.add_argument('--quality',choices=['include-flagged','exclude-flagged'],default='include-flagged')
    p.add_argument('--raw-unit',choices=['kwh-per-interval','kw'],default='kwh-per-interval')
    p.add_argument('--customer-ids',type=Path,help='Optional PRE-SPECIFIED fixed household set.')
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results'/'annual_forecast')
    p.add_argument('--plots',action='store_true');p.add_argument('--overwrite',action='store_true')
    a=p.parse_args(argv)
    try:
        data=read_raw(a.raw,a.raw_unit)
        result=build(data,a.out,a.start,a.days,window=a.window,alpha=a.alpha,method=a.method,
                     missing_year=a.missing_year,quality=a.quality,ids_path=a.customer_ids,overwrite=a.overwrite)
        if a.plots: plot_results(a.out)
        print(f"Saved: {a.out.resolve()}\nFixed cohort: {result['sample_customers']} households; {result['steps']} half-hour steps")
        print(f"Actually used: {', '.join(result['methods_used'])}")
        print('No HIL writes. Source GC only; CL is a separate descriptive total.')
        if 'recent30_missing_prior_year' in result['methods_used']:
            print('WARNING: prior-year data missing. This run is NOT a two-year hybrid result.')
        return 0
    except (ValueError,FileNotFoundError,FileExistsError,csv.Error) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':
    raise SystemExit(main())
