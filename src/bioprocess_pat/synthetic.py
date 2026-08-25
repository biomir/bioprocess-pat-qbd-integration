import numpy as np
import pandas as pd

def generate_fed_batch(n_hours: int = 168, seed: int = 42, deviation_start: int | None = None) -> pd.DataFrame:
    if n_hours < 24: raise ValueError('n_hours must be >= 24')
    rng = np.random.default_rng(seed)
    t = np.arange(n_hours, dtype=float)
    growth = 1/(1+np.exp(-(t-60)/18))
    late = 1/(1+np.exp(-(t-125)/10))
    temperature = 37.0 + rng.normal(0,0.06,n_hours)
    ph = 7.05 - 0.08*growth + 0.04*late + rng.normal(0,0.015,n_hours)
    do = 55 - 25*growth + 18*late + rng.normal(0,1.2,n_hours)
    agitation = 250 + 180*growth - 80*late + rng.normal(0,5,n_hours)
    gas_flow = 0.4 + 0.8*growth - 0.25*late + rng.normal(0,0.025,n_hours)
    feed_rate = np.clip((t-24)/80,0,1.2)*(1-0.25*late) + rng.normal(0,0.015,n_hours)
    feed_rate = np.clip(feed_rate,0,None)
    biomass = 1 + 14*growth - 2*late + rng.normal(0,0.2,n_hours)
    glucose = 5.5 - 2.6*growth + 0.9*late + rng.normal(0,0.12,n_hours)
    lactate = 0.6 + 2.4*growth - 1.5*late + rng.normal(0,0.08,n_hours)
    raman1 = 0.6*biomass - 0.8*glucose + rng.normal(0,0.3,n_hours)
    raman2 = 0.7*lactate + 0.2*feed_rate + rng.normal(0,0.08,n_hours)
    raman3 = -0.4*do + 0.05*agitation + rng.normal(0,0.5,n_hours)
    if deviation_start is not None:
        if not 0 <= deviation_start < n_hours: raise ValueError('deviation_start must be within run')
        idx = np.arange(n_hours) >= deviation_start
        ph[idx] -= np.linspace(0,0.18,idx.sum())
        do[idx] -= np.linspace(0,15,idx.sum())
        lactate[idx] += np.linspace(0,1.5,idx.sum())
        raman2[idx] += np.linspace(0,0.8,idx.sum())
    productivity = 0.45*biomass + 0.6*feed_rate - 0.25*lactate + rng.normal(0,0.15,n_hours)
    quality = 1 - 1.6*np.abs(ph-7.0) - 0.8*np.abs(temperature-37.0) - 0.12*lactate + rng.normal(0,0.03,n_hours)
    return pd.DataFrame({
        'hour': t.astype(int),'temperature_c':temperature,'ph':ph,'do_percent':do,
        'agitation_rpm':agitation,'gas_flow':gas_flow,'feed_rate':feed_rate,
        'biomass_proxy':biomass,'glucose':glucose,'lactate':lactate,
        'raman_lv1':raman1,'raman_lv2':raman2,'raman_lv3':raman3,
        'productivity_proxy':productivity,'quality_proxy':quality,
    })
