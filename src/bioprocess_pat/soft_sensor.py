from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class SoftSensorPrediction:
    values: np.ndarray
    squared_distance: np.ndarray
    inside_applicability_domain: np.ndarray


class PLSSoftSensor:
    """PLS soft sensor with an explicit calibration-domain boundary.

    The applicability-domain statistic is squared Mahalanobis distance in the
    standardized predictor space. It is a screening control, not proof that a
    prediction is fit for release or process control.
    """

    def __init__(self, n_components: int = 2, applicability_quantile: float = 0.99):
        if n_components < 1:
            raise ValueError("n_components must be >= 1")
        if not 0.5 < applicability_quantile < 1.0:
            raise ValueError("applicability_quantile must be between 0.5 and 1")
        self.n_components = n_components
        self.applicability_quantile = applicability_quantile
        self.scaler = StandardScaler()
        self.model = PLSRegression(n_components=n_components, scale=False)
        self._fitted = False

    @staticmethod
    def _matrix(values: object, *, label: str) -> np.ndarray:
        array = np.asarray(values, dtype=float)
        if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
            raise ValueError(f"{label} must be a non-empty 2-D matrix")
        if not np.all(np.isfinite(array)):
            raise ValueError(f"{label} must contain only finite values")
        return array

    def fit(self, x: object, y: object) -> PLSSoftSensor:
        predictors = self._matrix(x, label="x")
        target = np.asarray(y, dtype=float).reshape(-1)
        if target.shape[0] != predictors.shape[0]:
            raise ValueError("x and y must contain matching observations")
        if not np.all(np.isfinite(target)):
            raise ValueError("y must contain only finite values")
        maximum_components = min(predictors.shape[1], predictors.shape[0] - 1)
        if self.n_components > maximum_components:
            raise ValueError(
                f"n_components cannot exceed {maximum_components} for these calibration data"
            )

        standardized = self.scaler.fit_transform(predictors)
        self.model.fit(standardized, target.reshape(-1, 1))

        covariance = np.atleast_2d(np.cov(standardized, rowvar=False))
        self._inverse_covariance = np.linalg.pinv(covariance, hermitian=True)
        calibration_distance = self._squared_distance(standardized)
        self.applicability_limit_ = float(
            np.quantile(calibration_distance, self.applicability_quantile)
        )
        self.n_features_in_ = predictors.shape[1]
        self._fitted = True
        return self

    def _require_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("soft sensor must be fitted before prediction")

    def _squared_distance(self, standardized: np.ndarray) -> np.ndarray:
        return np.einsum(
            "ij,jk,ik->i", standardized, self._inverse_covariance, standardized
        )

    def predict(self, x: object) -> np.ndarray:
        return self.predict_with_domain(x).values

    def predict_with_domain(self, x: object) -> SoftSensorPrediction:
        self._require_fitted()
        predictors = self._matrix(x, label="x")
        if predictors.shape[1] != self.n_features_in_:
            raise ValueError(f"x must contain {self.n_features_in_} predictor columns")
        standardized = self.scaler.transform(predictors)
        values = self.model.predict(standardized).reshape(-1)
        distance = self._squared_distance(standardized)
        return SoftSensorPrediction(
            values=values,
            squared_distance=distance,
            inside_applicability_domain=distance <= self.applicability_limit_,
        )

    def fingerprint(self) -> str:
        """Return a deterministic digest of fitted preprocessing and PLS parameters."""
        self._require_fitted()
        payload = {
            "schema_version": 1,
            "n_components": self.n_components,
            "applicability_quantile": self.applicability_quantile,
            "applicability_limit": self.applicability_limit_,
            "scaler_mean": self.scaler.mean_.tolist(),
            "scaler_scale": self.scaler.scale_.tolist(),
            "x_weights": self.model.x_weights_.tolist(),
            "x_loadings": self.model.x_loadings_.tolist(),
            "y_loadings": self.model.y_loadings_.tolist(),
            "coef": self.model.coef_.tolist(),
            "intercept": self.model.intercept_.tolist(),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
