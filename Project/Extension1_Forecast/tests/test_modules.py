import csv,sys,tempfile,unittest
from pathlib import Path
from datetime import date,timedelta
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forecast_module import RawData,last_year,select_cohort,predict_issue,metrics,write_central,read_raw,SLOTS,build
from export_hil_scenario import export,COUNTS
from run_control_test import solve_schedule,tariff,check_bundle
from analyse_hil_export import analyse

D=date(2013,1,7)
def fixture(include_prior=True):
    records={}
    dates=[D-timedelta(days=k) for k in range(30,0,-1)]+[D,D+timedelta(days=1)]
    if include_prior:dates +=[last_year(D+timedelta(days=j)) for j in range(3)]
    for d in dates:
        for c in [1,2]:
            for cat in ['GC','GG']:
                v=(1.0 if cat=='GC' else .5)*(2 if d.year==2012 and d.month==1 else 1)
                records[(d,cat,c)]=(np.full(48,v),'')
    return RawData(records,sorted(dates),[1,2],[],len(records))

class ForecastTests(unittest.TestCase):
    def test_slots_midnight_last(self):
        self.assertEqual((len(SLOTS),SLOTS[0],SLOTS[-1]),(48,'0:30','0:00'))
    def test_calendar_year(self):
        self.assertEqual(last_year(date(2013,3,1)),date(2012,3,1))
        self.assertEqual(last_year(date(2012,2,29)),date(2011,2,28))
    def test_raw_intro_quality_and_conversion(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'raw.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['Read notes'])
                w.writerow(['Customer','Consumption Category','date',*SLOTS,'Row Quality'])
                w.writerow([1,'GC','1/07/2012',*([.8]*48),'NA'])
            r=read_raw([p]);self.assertEqual(r.records[(date(2012,7,1),'GC',1)][1],'NA')
            self.assertAlmostEqual(r.records[(date(2012,7,1),'GC',1)][0][0],.8)
    def test_duplicate_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'raw.csv';p.write_text('Customer,Consumption Category,date,'+','.join(SLOTS)+'\n')
            with self.assertRaises(ValueError):read_raw([p,p])
    def test_hybrid_weights(self):
        p,a=predict_issue(fixture(),D,[1,2],alpha=.25)
        np.testing.assert_allclose(p[0],7.);np.testing.assert_allclose(p[1],3.5)
        self.assertEqual(a[0]['method_used'],'hybrid')
    def test_missing_year_is_error(self):
        with self.assertRaises(ValueError):predict_issue(fixture(False),D,[1,2])
    def test_fallback_explicit(self):
        p,a=predict_issue(fixture(False),D,[1,2],missing_year='recent')
        self.assertEqual(a[0]['method_used'],'recent30_missing_prior_year');np.testing.assert_allclose(p[0],4.)
    def test_no_future_leakage(self):
        r=fixture();p,_=predict_issue(r,D,[1,2]);r.records[(D,'GC',1)]=(np.full(48,999),'')
        q,_=predict_issue(r,D,[1,2]);np.testing.assert_array_equal(p,q)
    def test_new_issue_may_use_yesterday(self):
        r=fixture();p,_=predict_issue(r,D+timedelta(days=1),[1,2],method='persistence')
        r.records[(D,'GC',1)]=(np.full(48,20),'')
        q,_=predict_issue(r,D+timedelta(days=1),[1,2],method='persistence');self.assertGreater(q[0,0],p[0,0])
    def test_cohort_not_selected_on_test(self):
        r=fixture();r.records.pop((D,'GC',2));ids,ex=select_cohort(r,D,30,'include-flagged')
        self.assertEqual(ids,[1,2]);self.assertEqual(ex,[])
    def test_missing_history_excluded_once(self):
        r=fixture();r.records.pop((D-timedelta(days=5),'GC',2));ids,ex=select_cohort(r,D,30,'include-flagged')
        self.assertEqual(ids,[1]);self.assertEqual(ex,[2])
    def test_quality_exclusion_is_explicit(self):
        r=fixture();r.records[(D-timedelta(days=5),'GC',2)]=(np.ones(48),'NA')
        self.assertEqual(select_cohort(r,D,30,'exclude-flagged')[0],[1])
        self.assertEqual(select_cohort(r,D,30,'include-flagged')[0],[1,2])
    def test_metrics_zero_pv(self):
        m=metrics(np.zeros(48),np.zeros(48));self.assertEqual(m['rmse_kw'],0);self.assertIsNone(m['wape_percent'])
    def test_bundle_windows_energy_and_export(self):
        with tempfile.TemporaryDirectory() as td:
            b=Path(td)/'bundle';s=Path(td)/'scene';r=fixture()
            build(r,b,D,2)
            with np.load(b/'forecast_bundle.npz') as z:
                self.assertEqual(z['mpc_load_kw'].shape,(96,48))
                self.assertTrue(np.all(z['issue_time']<=z['step_start']))
                np.testing.assert_allclose(z['forecast_kw'][:,0].sum(axis=1)*.5,144.)
            with self.assertRaises(ValueError):export(b,s)
            out=export(b,s,True);z,conf=check_bundle(s)
            self.assertEqual(z['counts'].sum(),1330);self.assertEqual(z['group_shares'].sum(),1.)
            np.testing.assert_allclose(z['forecast_kw'][0,0],6.*1330/2)
            with (s/'actual_5day_nodes.csv').open(encoding='utf-8-sig') as f:
                rows=list(csv.DictReader(f));self.assertEqual(len(rows),64)
                zero=[row for row in rows if row['Node']=='692' and row['Phase'] in ('A','B')]
                self.assertTrue(all(float(row[t])==0 for row in zero for t in SLOTS))
    def test_unseen_actual_cannot_export(self):
        with tempfile.TemporaryDirectory() as td:
            r=fixture();r.records.pop((D,'GC',2));b=Path(td)/'bundle';build(r,b,D,1)
            with self.assertRaises(ValueError):export(b,Path(td)/'s',True)

class ControlTests(unittest.TestCase):
    def test_sign_balance_terminal(self):
        load=np.r_[np.full(24,700),np.full(24,1300)];pv=np.zeros(48)
        b,g,e,info=solve_schedule(load,pv,tariff(np.arange(48)),6650,13300,6650)
        np.testing.assert_allclose(g,load-pv-b,atol=1e-7)
        self.assertEqual(len(e),49);self.assertAlmostEqual(e[-1],6650,places=4)
        self.assertTrue(np.allclose(np.diff(e),-.5*b))
    def test_mpc_midnight_target(self):
        b,g,e,info=solve_schedule(np.full(48,1000.),np.zeros(48),tariff(np.arange(3,51)),6000.,13300.,6650.,remaining=45,target=6650.)
        self.assertAlmostEqual(e[45],6650,places=4)
    def test_infeasible_is_rejected(self):
        with self.assertRaises(RuntimeError):solve_schedule(np.full(48,20000.),np.zeros(48),np.ones(48),6650,13300,6650)
    def test_invalid_shapes(self):
        with self.assertRaises(ValueError):solve_schedule(np.ones(47),np.ones(47),np.ones(47),1,2,1)

class MeasurementTests(unittest.TestCase):
    def test_explicit_alignment_units(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);sig=td/'sig.csv';log=td/'log.csv'
            sig.write_text('t,p\n10.5,100000\n11.5,100000\n12.5,200000\n13.5,200000\n')
            log.write_text('step,dataset_step_start,run_type,send_or_calculate_unix_s,interval_end_unix_s,grid_balance_CALCULATED_kw\n1,2013-01-07T00:00:00,HIL,1000,1002,95\n2,2013-01-07T00:30:00,HIL,1002,1004,195\n')
            r=analyse(sig,log,'t','p','W',10,td/'out')
            self.assertEqual(r['steps_without_samples'],0);self.assertEqual(r['energy_kwh_estimated_from_sample_means'],150.)

if __name__=='__main__':unittest.main(verbosity=2)
