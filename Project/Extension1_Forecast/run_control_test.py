#!/usr/bin/env python3
"""Separate Extension 1 test harness; default OFFLINE, never overwrites repo code.

QP objective, signs, tariffs, battery sizing and import/export bounds follow the
inspected Project/experiment1_applied.py. SciPy solves the convex QP. This is NOT
an unmodified execution of experiment2_submission.py. Both modes enforce the
same energy target at the next dataset midnight (a documented comparison choice).

Optional live mode REUSES the repository QP module's Modbus transport/mapping
only, and needs explicit operator confirmations. Hardware testing is not implied
by the supplied offline results. Scalar grid balance is NOT measured HIL power.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,Bounds,LinearConstraint
from export_hil_scenario import COUNTS,REPO_COMMIT

DT=.5
EXPECTED_QP_BLOB='61c120663eb21cdc291e4e4663e855f0bffc9a1a'


def tariff(indices):
    k=np.asarray(indices)%48
    return np.where((k<14)|(k>=44),.03,np.where((k<28)|(k>=40),.06,.30))


def solve_schedule(load,pv,prices,energy0,capacity,power,weight=1.,remaining=48,
                   target=None,energy_bounds=None,initial=None):
    """Same engineering objective, rescaled by power**2 for numerical stability.
    b>0 discharges; e(k+1)=e(k)-0.5*b(k). Includes e(0).
    """
    load=np.asarray(load,float);pv=np.asarray(pv,float);prices=np.asarray(prices,float)
    n=len(load);net=load-pv
    if n!=48 or pv.shape!=(n,) or prices.shape!=(n,): raise ValueError('Exactly 48 aligned samples required.')
    if not np.isfinite(np.r_[load,pv,prices,energy0,capacity,power,weight]).all(): raise ValueError('Non-finite controller input.')
    if min(capacity,power,weight)<=0 or not 0<=energy0<=capacity: raise ValueError('Invalid battery parameters/state.')
    if (prices<=0).any():raise ValueError('This test objective expects positive prices.')
    if target is None:target=capacity/2
    if not 1<=remaining<=48:raise ValueError('remaining must be 1..48')
    elow,ehigh=(0.,capacity) if energy_bounds is None else energy_bounds
    if elow>ehigh or not elow-1e-5<=energy0<=ehigh+1e-5:raise ValueError('Node energy states are inconsistent.')
    # x = battery kW / power kW. Box constraints also enforce forecast grid limits.
    lower=np.maximum(-1.,(net-3000.)/power);upper=np.minimum(1.,(net+1500.)/power)
    if np.any(lower>upper): raise RuntimeError('Power/grid limits cannot both be satisfied.')
    tri=np.tril(np.ones((n,n)))
    lower_c=np.full(n,(energy0-ehigh)/(DT*power));upper_c=np.full(n,(energy0-elow)/(DT*power))
    # Remove the terminal row from the inequalities, then add it as equality.
    mask=np.arange(n)!=remaining-1
    constraints=[LinearConstraint(tri[mask],lower_c[mask],upper_c[mask]),
                 LinearConstraint(tri[remaining-1:remaining],(energy0-target)/(DT*power),(energy0-target)/(DT*power))]
    def fun(x):return float(np.sum(weight*prices*(net/power-x)**2-DT*prices*x/power))
    def jac(x):return 2*weight*prices*(x-net/power)-DT*prices/power
    x0=np.zeros(n) if initial is None else np.asarray(initial,float)/power
    x0=np.minimum(np.maximum(x0,lower),upper)
    sol=minimize(fun,x0,jac=jac,bounds=Bounds(lower,upper),constraints=constraints,
                 method='SLSQP',options={'ftol':1e-11,'maxiter':500})
    batt=np.asarray(sol.x)*power;grid=net-batt;energy=np.r_[energy0,energy0-DT*np.cumsum(batt)]
    viol=max(0.,float(np.max(np.abs(batt)-power)),float(np.max(grid-3000)),float(np.max(-1500-grid)),
             float(np.max(elow-energy)),float(np.max(energy-ehigh)),float(abs(energy[remaining]-target)))
    if not sol.success or viol>1e-3:
        raise RuntimeError(f'QP failed: {sol.message}; max constraint residual {viol:.6g}. No command should be applied.')
    return batt,grid,energy,{'iterations':int(sol.nit),'max_residual':viol,'solver':'SciPy SLSQP (convex QP)','objective':fun(sol.x)*power*power}


def load_repo_transport(project:Path):
    """Only import user-selected inspected source; hash check is a version check."""
    path=Path(project)/'experiment1_applied.py'
    raw=path.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    # Git working trees may have CRLF conversion. Check canonical LF as well.
    canonical=raw.replace(b'\r\n',b'\n')
    norm=hashlib.sha1(b'blob '+str(len(canonical)).encode()+b'\0'+canonical).hexdigest()
    if EXPECTED_QP_BLOB not in (blob,norm):
        raise ValueError(f'Repository QP file differs from inspected version {REPO_COMMIT}. '
                         'Do not bypass this check; review its register mapping and transport first.')
    spec=importlib.util.spec_from_file_location('ext1_repo_transport',path);mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    if mod.N_CUSTOMERS!=COUNTS:raise ValueError('Repo customer map differs.')
    return mod


def check_bundle(scene:Path):
    scene=Path(scene)
    config=json.loads((scene/'scenario.json').read_text(encoding='utf-8'))
    if config.get('scenario_type')!='NEW_proportional_annual_data_scene':raise ValueError('Unexpected scenario.')
    with np.load(scene/'controller_inputs.npz',allow_pickle=False) as f:z={k:f[k].copy() for k in f.files}
    n=len(z['step_start']);n_days=len(z['dates'])
    if n!=48*n_days or z['forecast_kw'].shape!=(n_days,2,48) or z['actual_kw'].shape!=(n_days,2,48):
        raise ValueError('Incorrect daily/step shapes.')
    for k in ('actual_kw','forecast_kw','mpc_load_kw','mpc_pv_kw'):
        if not np.isfinite(z[k]).all():raise ValueError('Incomplete actual/forecast; no playback permitted.')
    if z['mpc_load_kw'].shape!=(n,48) or z['mpc_pv_kw'].shape!=(n,48):raise ValueError('Incorrect MPC windows.')
    if np.any(z['issue_time']>z['step_start']):raise ValueError('MPC has a future-issued forecast.')
    if dict(zip(z['group_names'].tolist(),z['counts'].tolist()))!=COUNTS:raise ValueError('Scenario node counts changed.')
    return z,config


def run(args):
    z,config=check_bundle(args.scene); live=bool(args.live)
    total=int(z['counts'].sum());capacity=args.capacity;power=args.power;target=args.initial_soc
    shares=z['group_shares'];group_names=z['group_names'].tolist();gi646=group_names.index('646_B')
    cap_nodes=capacity*shares;energy_nodes=target*shares
    n_all=len(z['step_start']);steps=n_all if args.steps is None else args.steps
    if not 1<=steps<=n_all:raise ValueError(f'--steps must be 1..{n_all}.')
    if not 0<=target<=capacity:raise ValueError('Initial state not within capacity.')
    if args.step_seconds<=0:raise ValueError('Positive playback step time required.')
    if live:
        if not(args.approve_new_scenario and args.confirm_soc_source and args.repo_project and args.ip):
            raise ValueError('Live needs --approve-new-scenario --confirm-soc-source --repo-project PATH --ip ADDRESS.')
        if args.dry_run:raise ValueError('Choose either --live or --dry-run.')
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');path=out/f'{args.mode}_{"HIL" if live else "OFFLINE"}_{stamp}.csv'
    # QP pre-solves five separate daily problems. MPC solves only at each current step.
    daily=[]; solve_times=[]
    if args.mode=='qp':
        for d in range((steps+47)//48):
            t=time.perf_counter()
            b,g,e,info=solve_schedule(z['forecast_kw'][d,0],z['forecast_kw'][d,1],tariff(np.arange(48)),
                                     target,capacity,power,args.weight,target=target)
            solve_times.append(time.perf_counter()-t);daily.append((b,g,e,info))
    mod=None;conn=None;completed=False;errors=[];rows=[];last_payload=None
    node_data={g:{'load_kw':z['actual_kw'][:,0].reshape(-1)*s,'pv_kw':z['actual_kw'][:,1].reshape(-1)*s}
               for g,s in zip(group_names,shares)}
    headers=['step','dataset_step_start','forecast_issue','wall_time_utc','mode','run_type',
             'p_load_fc_kw','p_pv_fc_kw','p_load_actual_input_kw','p_pv_actual_input_kw',
             'battery_command_kw','grid_forecast_kw','grid_balance_CALCULATED_kw',
             'soc_model_before_kwh','soc_model_after_kwh','soc_646_measured_before_pct',
             'solve_seconds','send_or_calculate_unix_s','interval_end_unix_s','tariff_per_kwh','constraint_max_residual']
    try:
        if live:
            mod=load_repo_transport(args.repo_project)
            print('LIVE: verify REMOTE CONTROL, holding 2000-2063, Node646 HIL-model SoC input 3000 /100 = percent.')
            print('This uses a NEW proportional source scene. It does NOT read node voltages or feeder power over Modbus.')
            print('The wall-clock step period MUST match the model playback/SOC time scaling. Default: 2s = 30min.')
            if input('Type START to confirm lab reset, capture ready and limits approved: ').strip()!='START':
                raise ValueError('Live run not confirmed.')
            conn=mod.ModbusConnection(args.ip,args.port);conn.connect()
            mod.clear_all_registers(conn,False)
            time.sleep(args.settle_seconds)
        with path.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader();f.flush()
            warm=None
            for i in range(steps):
                tick=time.perf_counter();measured=None
                if live:
                    rr=conn.client.read_input_registers(address=mod.SOC_INPUT_REGISTER,count=1)
                    if rr is None or rr.isError():raise IOError('SoC read failed. Stop, do not substitute zero.')
                    measured=float(rr.registers[0])/100.
                    if not np.isfinite(measured) or not 0<=measured<=100:raise ValueError('Invalid SoC percent.')
                    if i==0 and abs(measured-100*target/capacity)>2:
                        raise ValueError('Initial measured Node646 SOC differs from requested initial condition by >2 percentage points.')
                    if args.mode=='mpc':energy_nodes[gi646]=cap_nodes[gi646]*measured/100.
                before=float(energy_nodes.sum());day,k=divmod(i,48)
                prices=tariff(np.arange(i,i+48));t=time.perf_counter()
                if args.mode=='qp':
                    b,g,e,info=daily[day];command=float(b[k]);grid_fc=float(g[k]);solve_s=0.
                    load_fc=float(z['forecast_kw'][day,0,k]);pv_fc=float(z['forecast_kw'][day,1,k])
                else:
                    nz=shares>0
                    # Keep every node's modelled energy feasible under proportional commands.
                    elow=before-float(np.min(energy_nodes[nz]/shares[nz]))
                    ehigh=before-float(np.max((energy_nodes[nz]-cap_nodes[nz])/shares[nz]))
                    b,g,e,info=solve_schedule(z['mpc_load_kw'][i],z['mpc_pv_kw'][i],prices,
                        before,capacity,power,args.weight,remaining=48-k,target=target,
                        energy_bounds=(max(0.,elow),min(capacity,ehigh)),initial=warm)
                    warm=np.r_[b[1:],b[-1]];command=float(b[0]);grid_fc=float(g[0]);solve_s=time.perf_counter()-t
                    solve_times.append(solve_s);load_fc=float(z['mpc_load_kw'][i,0]);pv_fc=float(z['mpc_pv_kw'][i,0])
                commands={g:command*s for g,s in zip(group_names,shares)}
                actual_l=float(z['actual_kw'][day,0,k]);actual_pv=float(z['actual_kw'][day,1,k])
                if live:
                    if time.perf_counter()-tick>args.step_seconds*.8:
                        raise RuntimeError('Solver/measurement exceeded 80% of cycle. Stop and review model/control time scaling.')
                    # Use the verified repo encoder/order. No automatic retry with stale data.
                    payload=mod.build_feeder_payload(node_data,i,commands)
                    reply=conn.client.write_registers(address=mod.HOLDING_START,values=payload)
                    if reply is None or reply.isError():raise IOError('Command write failed; stopping playback.')
                    last_payload=payload
                    # Engineering-integer quantisation is the repo's wire format.
                    node_b=np.array([round(commands[g]) for g in group_names],float)
                    actual_l=sum(round(node_data[g]['load_kw'][i]) for g in group_names)
                    actual_pv=sum(round(node_data[g]['pv_kw'][i]) for g in group_names)
                else:node_b=command*shares
                sent=time.time();energy_nodes=energy_nodes-DT*node_b
                # Tiny engineering-integer endpoint deviations are LOGGED, not silently clamped.
                if np.min(energy_nodes)<-5 or np.max(energy_nodes-cap_nodes)>5:
                    raise RuntimeError('Modelled node energy violates bounds beyond quantisation tolerance.')
                row=dict(zip(headers,[i+1,str(z['step_start'][i]),str(z['issue_time'][i]),datetime.now(timezone.utc).isoformat(),
                        args.mode,'HIL' if live else 'OFFLINE_IDEAL_BATTERY',load_fc,pv_fc,actual_l,actual_pv,
                        float(node_b.sum()),grid_fc,actual_l-actual_pv-float(node_b.sum()),before,float(energy_nodes.sum()),
                        '' if measured is None else measured,solve_s,sent,'',float(prices[0]),info['max_residual']]))
                if live:time.sleep(max(0.,args.step_seconds-(time.perf_counter()-tick)))
                row['interval_end_unix_s']=time.time();writer.writerow(row);f.flush();rows.append(row)
                if args.progress_every and (i%args.progress_every==0 or i==steps-1):
                    print(f'{args.mode.upper()} {i+1:3d}/{steps} | battery {command:9.2f} kW | SOC model {energy_nodes.sum():9.2f} kWh')
            completed=True
    except (Exception,KeyboardInterrupt) as exc:
        errors.append(f'{type(exc).__name__}: {exc}')
    finally:
        if conn is not None:
            try:mod.clear_all_registers(conn,False)
            except Exception as exc:
                errors.append(f'FAILED SAFE CLEAR: {exc}. Operator must use HIL SCADA Stop / lab safe-stop procedure.')
                print(errors[-1],file=sys.stderr)
            conn.close()
    # This is a course tariff balance calculation, not a retail bill / measured grid bill.
    cost=sum(DT*r['tariff_per_kwh']*r['grid_balance_CALCULATED_kw'] for r in rows)
    base=sum(DT*r['tariff_per_kwh']*(r['p_load_actual_input_kw']-r['p_pv_actual_input_kw']) for r in rows)
    meta={'mode':args.mode,'run_type':'HIL' if live else 'OFFLINE_IDEAL_BATTERY',
          'scenario':str(args.scene),'scenario_type':config['scenario_type'],'completed':completed,'rows':len(rows),'requested_steps':steps,
          'errors':errors,'log_csv':path.name,'capacity_kwh':capacity,'battery_power_kw':power,'weight':args.weight,
          'initial_soc_kwh':target,'final_soc_model_kwh':float(energy_nodes.sum()),
          'max_solve_seconds':max(solve_times,default=0.),'solver':'SciPy SLSQP with analytic gradient and residual checks',
          'grid_net_cost_calculated':cost,'no_battery_net_cost_calculated':base,
          'cost_assumption':'same TOU price for signed import/export; calculated from input power balance, NOT actual SCADA power',
          'calculated_grid_peak_import_kw':max((r['grid_balance_CALCULATED_kw'] for r in rows),default=None),
          'calculated_grid_min_kw':min((r['grid_balance_CALCULATED_kw'] for r in rows),default=None),
          'actual_balance_steps_outside_forecast_grid_limits':sum(not -1500.001<=r['grid_balance_CALCULATED_kw']<=3000.001 for r in rows),
          'grid_limits_are_forecast_constraints_not_actual_guarantees':True,
          'terminal_policy':'both modes: aggregate energy returns to initial target at each DATASET midnight',
          'forecast_updates':'latest midnight-issued 48-step window; no intraday error correction',
          'feedback': 'Node646 measured energy replaces its modelled state; other nodes estimated' if live and args.mode=='mpc' else 'model only / QP ignores SoC for re-planning',
          'not_measured_by_this_script':['feeder head power','node voltages','actual delivered battery power'],
          'source_repo_commit':REPO_COMMIT,'not_original_mpc_main':True}
    path.with_suffix('.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Log: {path}\nMetadata: {path.with_suffix(".json")}')
    if errors:raise RuntimeError('; '.join(errors))
    return meta,path


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene',type=Path,required=True);p.add_argument('--mode',choices=['qp','mpc'],required=True)
    p.add_argument('--out',type=Path,default=Path('Output/Extension1'))
    p.add_argument('--capacity',type=float,default=13300.);p.add_argument('--power',type=float,default=6650.)
    p.add_argument('--initial-soc',type=float,default=6650.);p.add_argument('--weight',type=float,default=1.)
    p.add_argument('--steps',type=int);p.add_argument('--progress-every',type=int,default=48)
    p.add_argument('--dry-run',action='store_true');p.add_argument('--live',action='store_true')
    p.add_argument('--repo-project',type=Path);p.add_argument('--ip');p.add_argument('--port',type=int,default=502)
    p.add_argument('--approve-new-scenario',action='store_true');p.add_argument('--confirm-soc-source',action='store_true')
    p.add_argument('--step-seconds',type=float,default=2.);p.add_argument('--settle-seconds',type=float,default=12.)
    a=p.parse_args(argv)
    print(vars(a))
    try:run(a);return 0
    except (Exception,KeyboardInterrupt) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
