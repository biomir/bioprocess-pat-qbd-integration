from dataclasses import dataclass

from .qbd import QbDModel


@dataclass(frozen=True)
class AdvisoryEvent:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ProcessAssessment:
    cpp_violations: tuple[str, ...]
    multivariate_alarm: bool
    soft_sensor_deviation: bool
    state: str
    advisories: tuple[AdvisoryEvent, ...]


def assess_process_state(
    latest,
    qbd: QbDModel,
    multivariate_alarm: bool,
    soft_sensor_value=None,
    soft_sensor_expected_min=None,
):
    violations = tuple(
        name
        for name in qbd.cpps
        if name in latest and qbd.cpp_out_of_range(name, latest[name])
    )
    soft_deviation = (
        soft_sensor_value is not None
        and soft_sensor_expected_min is not None
        and soft_sensor_value < soft_sensor_expected_min
    )
    advisories = []
    if violations:
        advisories.append(
            AdvisoryEvent(
                "CPP_RANGE", "high", f"Review CPP excursions: {', '.join(violations)}"
            )
        )
    if multivariate_alarm:
        advisories.append(
            AdvisoryEvent(
                "MVDA_ALARM",
                "medium",
                "Multivariate process state is outside the reference model envelope.",
            )
        )
    if soft_deviation:
        advisories.append(
            AdvisoryEvent(
                "SOFT_SENSOR",
                "medium",
                "Soft-sensor estimate is below the illustrative expected range.",
            )
        )
    state = "action" if violations else (
        "review" if multivariate_alarm or soft_deviation else "nominal"
    )
    return ProcessAssessment(
        violations,
        bool(multivariate_alarm),
        bool(soft_deviation),
        state,
        tuple(advisories),
    )
