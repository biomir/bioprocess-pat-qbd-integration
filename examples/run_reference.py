from bioprocess_pat import PCAMonitor, PLSSoftSensor, assess_process_state, default_qbd_model, generate_fed_batch
FEATURES=['temperature_c','ph','do_percent','agitation_rpm','gas_flow','feed_rate','biomass_proxy','glucose','lactate','raman_lv1','raman_lv2','raman_lv3']
ref=generate_fed_batch(168,seed=10); ev=generate_fed_batch(168,seed=11,deviation_start=130)
mon=PCAMonitor(n_components=4,quantile=0.99).fit(ref[FEATURES].iloc[:120]); mv=mon.evaluate(ev[FEATURES])
soft=PLSSoftSensor(n_components=3).fit(ref[FEATURES].iloc[:120],ref['productivity_proxy'].iloc[:120]); pred=soft.predict(ev[FEATURES])
a=assess_process_state(ev.iloc[-1].to_dict(),default_qbd_model(),bool(mv.alarm[-1]),float(pred[-1]),float(ref['productivity_proxy'].quantile(.10)))
print('Final T2:',round(float(mv.t2[-1]),3),'limit:',round(mv.t2_limit,3))
print('Final SPE:',round(float(mv.spe[-1]),3),'limit:',round(mv.spe_limit,3))
print('Process state:',a.state)
for e in a.advisories: print('-',e.code+':',e.message)
