# 03_forecast.py  (Python 3.13 兼容)
import pandas as pd
from utils import mlp_forecast

congestion = pd.read_csv('congestion_daily.csv')
congestion.columns = ['date', 'congestion']
congestion['date'] = pd.to_datetime(congestion['date'])

# 1. MLP 预测未来 7 天
pred = mlp_forecast(congestion.set_index('date')['congestion'])

# 2. 生成未来日期（兼容 3.13）
future_dates = pd.date_range(
    congestion['date'].max() + pd.Timedelta(days=1),
    periods=7,
    inclusive='both'
)
forecast_df = pd.DataFrame({'date': future_dates, 'mlp_pred': pred})

# 3. 保存
forecast_df.to_csv('mlp_pred.csv', index=False)
print('✅ 03_forecast.py 完成')
