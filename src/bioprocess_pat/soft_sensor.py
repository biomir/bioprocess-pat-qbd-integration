import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler

class PLSSoftSensor:
    def __init__(self,n_components=2):
        if n_components < 1: raise ValueError('n_components must be >= 1')
        self.n_components=n_components; self.scaler=StandardScaler(); self.model=PLSRegression(n_components=n_components,scale=False); self._fitted=False
    def fit(self,x,y):
        xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float).reshape(-1,1)
        if xa.ndim != 2 or len(xa) != len(ya): raise ValueError('x and y must contain matching observations')
        z=self.scaler.fit_transform(xa); self.model.fit(z,ya); self._fitted=True; return self
    def predict(self,x):
        if not self._fitted: raise RuntimeError('soft sensor must be fitted before prediction')
        return self.model.predict(self.scaler.transform(np.asarray(x,dtype=float))).ravel()
