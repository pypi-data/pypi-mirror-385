import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.decomposition import NMF


class Preprocessing(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):  # noqa: N803
        return self

    def transform(self, X):  # noqa: N803
        min_val = np.min(X, axis=0, keepdims=True)
        max_val = np.max(X, axis=0, keepdims=True)
        return np.where((max_val - min_val) != 0, (X - min_val) / (max_val - min_val + 1e-8), 0)


class NMFRegressor(RegressorMixin, BaseEstimator):
    def __init__(self, **kwargs):
        self.nmf = NMF(**kwargs)

    def fit(self, X, y=None):  # noqa: N803
        self.nmf.fit(X)
        self.H = self.nmf.components_
        self.is_fitted_ = True
        return self

    def predict(self, X):  # noqa: N803
        W = self.nmf.transform(X)  # noqa: N806
        rec = np.dot(W, self.H)
        mse = np.mean((X - rec) ** 2, axis=1)
        return rec, mse

    def score(self, X, y, sample_weight=None):  # noqa: N803
        preds, _ = self.predict(X)
        return np.mean((y - preds) ** 2, axis=1)
