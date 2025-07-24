# utils.py  (策略 A：无 TensorFlow)
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

def entropy_weight(matrix: pd.DataFrame) -> np.ndarray:
    matrix = matrix.apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    k = 1 / np.log(matrix.shape[0])
    p = matrix / matrix.sum()
    e = -k * (p * np.log(p + 1e-12)).sum()
    d = 1 - e
    w = d / d.sum()
    return w.values

def topsis_score(data: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    norm = data / np.sqrt((data**2).sum())
    weighted = norm * weights
    ideal_best = weighted.max()
    ideal_worst = weighted.min()
    d_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
    score = d_worst / (d_best + d_worst)
    return pd.Series(score, index=data.index)

def mlp_forecast(series: pd.Series, look_back=7, steps=7):
    """基于 MLPRegressor 的简易时间序列预测"""
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1)).flatten()
    X, y = [], []
    for i in range(len(scaled) - look_back):
        X.append(scaled[i:i+look_back])
        y.append(scaled[i+look_back])
    X, y = np.array(X), np.array(y)

    mlp = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
    mlp.fit(X, y)

    last = scaled[-look_back:]
    preds = []
    for _ in range(steps):
        pred = mlp.predict(last.reshape(1, -1))[0]
        preds.append(pred)
        last = np.append(last[1:], pred)
    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    return preds
