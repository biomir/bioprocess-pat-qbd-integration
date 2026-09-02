from bioprocess_pat import (
    PCAMonitor,
    PLSSoftSensor,
    assess_process_state,
    default_qbd_model,
    generate_fed_batch,
)

FEATURES = [
    "temperature_c",
    "ph",
    "do_percent",
    "agitation_rpm",
    "gas_flow",
    "feed_rate",
    "biomass_proxy",
    "glucose",
    "lactate",
    "raman_lv1",
    "raman_lv2",
    "raman_lv3",
]

reference = generate_fed_batch(168, seed=10)
evaluation = generate_fed_batch(168, seed=11, deviation_start=130)
monitor = PCAMonitor(n_components=4, quantile=0.99).fit(reference[FEATURES].iloc[:120])
multivariate = monitor.evaluate(evaluation[FEATURES])
soft_sensor = PLSSoftSensor(n_components=3).fit(
    reference[FEATURES].iloc[:120], reference["productivity_proxy"].iloc[:120]
)
prediction = soft_sensor.predict(evaluation[FEATURES])
assessment = assess_process_state(
    evaluation.iloc[-1].to_dict(),
    default_qbd_model(),
    bool(multivariate.alarm[-1]),
    float(prediction[-1]),
    float(reference["productivity_proxy"].quantile(0.10)),
)

print(
    "Final T2:",
    round(float(multivariate.t2[-1]), 3),
    "limit:",
    round(multivariate.t2_limit, 3),
)
print(
    "Final SPE:",
    round(float(multivariate.spe[-1]), 3),
    "limit:",
    round(multivariate.spe_limit, 3),
)
print("Process state:", assessment.state)
for event in assessment.advisories:
    print("-", event.code + ":", event.message)
