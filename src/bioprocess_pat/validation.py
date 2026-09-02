from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from .soft_sensor import PLSSoftSensor


@dataclass(frozen=True)
class ValidationFold:
    held_out_batch: str
    calibration_batches: tuple[str, ...]
    n_calibration: int
    n_external: int
    rmse: float
    mae: float
    bias: float
    r2: float
    applicability_coverage: float
    model_fingerprint: str


@dataclass(frozen=True)
class SoftSensorValidationReport:
    strategy: str
    features: tuple[str, ...]
    target: str
    folds: tuple[ValidationFold, ...]
    macro_rmse: float
    macro_mae: float
    macro_bias: float
    macro_r2: float
    macro_applicability_coverage: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _validated_batch(
    batch_name: str, frame: pd.DataFrame, features: Sequence[str], target: str
) -> pd.DataFrame:
    required = [*features, target]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"batch {batch_name!r} is missing columns: {', '.join(missing)}")
    selected = frame.loc[:, required]
    if len(selected) < 3:
        raise ValueError(f"batch {batch_name!r} must contain at least 3 observations")
    if not np.isfinite(selected.to_numpy(dtype=float)).all():
        raise ValueError(f"batch {batch_name!r} contains non-finite values")
    return selected


def validate_soft_sensor_leave_one_batch_out(
    batches: Mapping[str, pd.DataFrame],
    *,
    features: Sequence[str],
    target: str,
    n_components: int = 2,
    applicability_quantile: float = 0.99,
) -> SoftSensorValidationReport:
    """Validate a PLS soft sensor using whole held-out batches.

    Each fold calibrates on complete batches and evaluates on a different,
    untouched batch. This avoids the optimistic leakage created by randomly
    splitting autocorrelated observations from one process run.
    """
    if len(batches) < 3:
        raise ValueError("at least three independent batches are required")
    if not features or len(set(features)) != len(features):
        raise ValueError("features must be a non-empty sequence of unique names")
    if target in features:
        raise ValueError("target must not also be used as a predictor")

    checked = {
        str(name): _validated_batch(str(name), frame, features, target)
        for name, frame in batches.items()
    }
    if len(checked) != len(batches):
        raise ValueError("batch names must be unique after string conversion")

    fold_results: list[ValidationFold] = []
    for held_out_name in sorted(checked):
        calibration_names = tuple(name for name in sorted(checked) if name != held_out_name)
        calibration = pd.concat(
            [checked[name] for name in calibration_names], ignore_index=True
        )
        external = checked[held_out_name]

        model = PLSSoftSensor(
            n_components=n_components,
            applicability_quantile=applicability_quantile,
        ).fit(calibration.loc[:, features], calibration.loc[:, target])
        prediction = model.predict_with_domain(external.loc[:, features])
        observed = external.loc[:, target].to_numpy(dtype=float)
        residual = prediction.values - observed

        fold_results.append(
            ValidationFold(
                held_out_batch=held_out_name,
                calibration_batches=calibration_names,
                n_calibration=len(calibration),
                n_external=len(external),
                rmse=float(np.sqrt(np.mean(residual**2))),
                mae=float(np.mean(np.abs(residual))),
                bias=float(np.mean(residual)),
                r2=float(r2_score(observed, prediction.values)),
                applicability_coverage=float(
                    np.mean(prediction.inside_applicability_domain)
                ),
                model_fingerprint=model.fingerprint(),
            )
        )

    def macro(metric: str) -> float:
        return float(np.mean([getattr(fold, metric) for fold in fold_results]))

    return SoftSensorValidationReport(
        strategy="leave-one-batch-out",
        features=tuple(features),
        target=target,
        folds=tuple(fold_results),
        macro_rmse=macro("rmse"),
        macro_mae=macro("mae"),
        macro_bias=macro("bias"),
        macro_r2=macro("r2"),
        macro_applicability_coverage=macro("applicability_coverage"),
    )
