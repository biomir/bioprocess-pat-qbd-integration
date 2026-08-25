from pathlib import Path
import numpy as np
from sklearn.metrics import r2_score
from bioprocess_pat import PCAMonitor, PLSSoftSensor, assess_process_state, default_qbd_model, generate_fed_batch, validate_traceability
FEATURES=['temperature_c','ph','do_percent','agitation_rpm','gas_flow','feed_rate','biomass_proxy','glucose','lactate','raman_lv1','raman_lv2','raman_lv3']

def test_qbd_range():
    q=default_qbd_model(); assert not q.cpp_out_of_range('ph',7.0); assert q.cpp_out_of_range('ph',6.5)

def test_synthetic_reproducible():
    assert generate_fed_batch(48,1).equals(generate_fed_batch(48,1))

def test_monitor_detects_late_shift():
    ref=generate_fed_batch(168,3); shifted=generate_fed_batch(168,4,125)
    m=PCAMonitor(4,.99).fit(ref[FEATURES].iloc[:120]); r=m.evaluate(shifted[FEATURES])
    assert r.alarm[-20:].mean() > r.alarm[:80].mean()

def test_soft_sensor_has_predictive_signal():
    d=generate_fed_batch(168,5)
    train=d.sample(frac=0.75, random_state=7); test=d.drop(train.index)
    m=PLSSoftSensor(3).fit(train[FEATURES],train['productivity_proxy']); p=m.predict(test[FEATURES])
    assert np.isfinite(p).all(); assert r2_score(test['productivity_proxy'],p) > 0.75

def test_cpp_excursion_drives_action():
    q=default_qbd_model(); a=assess_process_state({'ph':6.4,'temperature_c':37,'do_percent':50,'feed_rate':1},q,False)
    assert a.state=='action' and 'ph' in a.cpp_violations

def test_traceability_example():
    p=Path(__file__).parents[1]/'examples'/'traceability.csv'; assert validate_traceability(p)==[]
