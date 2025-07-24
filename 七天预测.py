# 七天预测.py
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# 1. 读数
file_path = r"C:\Users\ASUS\Desktop\beijing_metro\近十周地铁网络客流（北京）.xlsx"
df = pd.read_excel(file_path)
df.columns = ["date", "y"]
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").asfreq("D").sort_index()

# 2. 特征工程
def make_features(data):
    X = data.copy()
    X["dayofweek"] = X.index.dayofweek
    X["is_weekend"] = (X["dayofweek"] >= 5).astype(int)
    for l in [1, 2, 3, 7]:
        X[f"lag_{l}"] = X["y"].shift(l)
    for w in [3, 7]:
        X[f"roll_mean_{w}"] = X["y"].shift(1).rolling(w).mean()
        X[f"roll_std_{w}"] = X["y"].shift(1).rolling(w).std()
    return X.dropna()

feat_df = make_features(df)

# 3. 划分
X = feat_df.drop(columns=["y"])
y = feat_df["y"]
split_date = "2025-07-03"
train_mask = X.index <= split_date
X_train, y_train = X[train_mask], y[train_mask]
X_valid, y_valid = X[~train_mask], y[~train_mask]

# 4. 训练（XGBoost 3.0.2 写法）
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

model = xgb.XGBRegressor(
    n_estimators=3000,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
)

model.fit(
    X_train, y_train,
    eval_set=[(X_valid, y_valid)],
    verbose=False,
    callbacks=[xgb.callback.EarlyStopping(rounds=50, save_best=True, maximize=False)]
)

# 5. 验证
pred_valid = model.predict(X_valid)
print("验证 MAE =", mean_absolute_error(y_valid, pred_valid).round(2))

# 6. 未来 7 天
future_idx = pd.date_range("2025-07-10", periods=7, freq="D")
extended = pd.concat([df, pd.DataFrame(index=future_idx)])
for day in future_idx:
    tmp = make_features(extended.loc[:day])
    feat = tmp.loc[day:day, X.columns]
    extended.loc[day, "y"] = model.predict(feat)[0]

forecast = extended.loc[future_idx, "y"].rename("pred_xgb")
print("\n未来 7 天预测（万人次）：")
print(forecast.round(2))
