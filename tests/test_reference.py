from pathlib import Path

from bioprocess_pat import (
    PCAMonitor,
    assess_process_state,
    default_qbd_model,
    generate_fed_batch,
    validate_traceability,
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


def test_qbd_range():
    model = default_qbd_model()
    assert not model.cpp_out_of_range("ph", 7.0)
    assert model.cpp_out_of_range("ph", 6.5)


def test_synthetic_reproducible():
    assert generate_fed_batch(48, 1).equals(generate_fed_batch(48, 1))


def test_monitor_detects_late_shift():
    reference = generate_fed_batch(168, 3)
    shifted = generate_fed_batch(168, 4, 125)
    monitor = PCAMonitor(4, 0.99).fit(reference[FEATURES].iloc[:120])
    result = monitor.evaluate(shifted[FEATURES])
    assert result.alarm[-20:].mean() > result.alarm[:80].mean()


def test_cpp_excursion_drives_action():
    assessment = assess_process_state(
        {"ph": 6.4, "temperature_c": 37, "do_percent": 50, "feed_rate": 1},
        default_qbd_model(),
        False,
    )
    assert assessment.state == "action"
    assert "ph" in assessment.cpp_violations


def test_traceability_example():
    path = Path(__file__).parents[1] / "examples" / "traceability.csv"
    assert validate_traceability(path) == []
