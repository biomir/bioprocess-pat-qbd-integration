import json
from pathlib import Path

from bioprocess_pat import generate_fed_batch, validate_soft_sensor_leave_one_batch_out

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

batches = {
    f"synthetic-batch-{number:02d}": generate_fed_batch(168, seed=500 + number)
    for number in range(1, 6)
}
report = validate_soft_sensor_leave_one_batch_out(
    batches,
    features=FEATURES,
    target="productivity_proxy",
    n_components=3,
)

output = Path("artifacts/soft_sensor_validation.json")
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output}")
print(f"Macro R2: {report.macro_r2:.3f}")
print(f"Macro RMSE: {report.macro_rmse:.3f}")
print(f"Applicability coverage: {report.macro_applicability_coverage:.1%}")
