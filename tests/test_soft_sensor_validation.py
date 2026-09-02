import json

import numpy as np
import pytest

from bioprocess_pat import (
    PLSSoftSensor,
    generate_fed_batch,
    validate_soft_sensor_leave_one_batch_out,
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


def synthetic_batches(count: int = 5):
    return {
        f"batch-{number:02d}": generate_fed_batch(168, seed=100 + number)
        for number in range(count)
    }


def test_leave_one_batch_out_uses_independent_runs():
    report = validate_soft_sensor_leave_one_batch_out(
        synthetic_batches(),
        features=FEATURES,
        target="productivity_proxy",
        n_components=3,
    )

    assert report.strategy == "leave-one-batch-out"
    assert len(report.folds) == 5
    assert report.macro_r2 > 0.80
    assert report.macro_rmse < 0.30
    for fold in report.folds:
        assert fold.held_out_batch not in fold.calibration_batches
        assert fold.n_calibration == 4 * 168
        assert fold.n_external == 168
        assert len(fold.model_fingerprint) == 64
    json.dumps(report.to_dict())


def test_applicability_domain_flags_extreme_predictor_shift():
    calibration = generate_fed_batch(168, seed=7)
    external = generate_fed_batch(168, seed=8)
    model = PLSSoftSensor(n_components=3, applicability_quantile=0.99).fit(
        calibration[FEATURES], calibration["productivity_proxy"]
    )
    nominal = model.predict_with_domain(external[FEATURES])
    extreme = external[FEATURES].copy()
    extreme["temperature_c"] += 10.0
    shifted = model.predict_with_domain(extreme)

    assert nominal.inside_applicability_domain.mean() > 0.50
    assert not shifted.inside_applicability_domain.any()
    assert shifted.squared_distance.min() > model.applicability_limit_


def test_model_fingerprint_is_deterministic_and_configuration_sensitive():
    batch = generate_fed_batch(96, seed=21)
    first = PLSSoftSensor(2).fit(batch[FEATURES], batch["productivity_proxy"])
    second = PLSSoftSensor(2).fit(batch[FEATURES], batch["productivity_proxy"])
    third = PLSSoftSensor(3).fit(batch[FEATURES], batch["productivity_proxy"])

    assert first.fingerprint() == second.fingerprint()
    assert first.fingerprint() != third.fingerprint()


@pytest.mark.parametrize(
    ("batches", "message"),
    [
        ({"a": generate_fed_batch(), "b": generate_fed_batch(seed=2)}, "three"),
        (
            {
                "a": generate_fed_batch(),
                "b": generate_fed_batch(seed=2),
                "c": generate_fed_batch(seed=3).drop(columns=["ph"]),
            },
            "missing columns",
        ),
    ],
)
def test_validation_rejects_invalid_batch_evidence(batches, message):
    with pytest.raises(ValueError, match=message):
        validate_soft_sensor_leave_one_batch_out(
            batches, features=FEATURES, target="productivity_proxy"
        )


def test_soft_sensor_rejects_nonfinite_and_feature_mismatch():
    batch = generate_fed_batch(48, seed=8)
    invalid = batch[FEATURES].copy()
    invalid.iloc[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        PLSSoftSensor(2).fit(invalid, batch["productivity_proxy"])

    model = PLSSoftSensor(2).fit(batch[FEATURES], batch["productivity_proxy"])
    with pytest.raises(ValueError, match="predictor columns"):
        model.predict(batch[FEATURES[:-1]])
