from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class MonitoringResult:
    t2: np.ndarray
    spe: np.ndarray
    t2_limit: float
    spe_limit: float
    alarm: np.ndarray


class PCAMonitor:
    def __init__(self, n_components=3, quantile=0.99):
        if n_components < 1:
            raise ValueError("n_components must be >= 1")
        if not 0.5 < quantile < 1:
            raise ValueError("quantile must be between 0.5 and 1")
        self.n_components = n_components
        self.quantile = quantile
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self._fitted = False

    def fit(self, x):
        array = np.asarray(x, dtype=float)
        if array.ndim != 2 or array.shape[0] <= self.n_components:
            raise ValueError("insufficient 2-D training data")
        if not np.all(np.isfinite(array)):
            raise ValueError("training data must be finite")
        standardized = self.scaler.fit_transform(array)
        scores = self.pca.fit_transform(standardized)
        reconstruction = self.pca.inverse_transform(scores)
        t2 = np.sum((scores**2) / self.pca.explained_variance_, axis=1)
        spe = np.sum((standardized - reconstruction) ** 2, axis=1)
        self.t2_limit_ = float(np.quantile(t2, self.quantile))
        self.spe_limit_ = float(np.quantile(spe, self.quantile))
        self._fitted = True
        return self

    def evaluate(self, x):
        if not self._fitted:
            raise RuntimeError("monitor must be fitted before evaluation")
        array = np.asarray(x, dtype=float)
        if not np.all(np.isfinite(array)):
            raise ValueError("evaluation data must be finite")
        standardized = self.scaler.transform(array)
        scores = self.pca.transform(standardized)
        reconstruction = self.pca.inverse_transform(scores)
        t2 = np.sum((scores**2) / self.pca.explained_variance_, axis=1)
        spe = np.sum((standardized - reconstruction) ** 2, axis=1)
        return MonitoringResult(
            t2,
            spe,
            self.t2_limit_,
            self.spe_limit_,
            (t2 > self.t2_limit_) | (spe > self.spe_limit_),
        )
