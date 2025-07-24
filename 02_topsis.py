# 02_topsis.py  (兼容 3.13，无 Categorical 问题)
import pandas as pd
import numpy as np
import geopandas as gpd
from utils import entropy_weight, topsis_score

stations = gpd.read_file('stations_processed.geojson')

# 评价矩阵
criteria = pd.DataFrame({
    '客流强度': np.random.uniform(0.5, 1.5, len(stations)),
    '人口密度': np.random.uniform(0.3, 2.0, len(stations)),
    '道路拥堵': np.random.uniform(0.2, 0.8, len(stations)),
    '地形坡度': np.random.uniform(0.0, 0.3, len(stations)),
    'POI混合度': np.random.uniform(0.4, 0.9, len(stations))
}, index=stations['uid'])

weights = entropy_weight(criteria)
stations['TOPSIS_score'] = topsis_score(criteria, weights).values

# 分级 + 转字符串解决 Categorical 无法写入问题
stations['level'] = pd.qcut(stations['TOPSIS_score'], 4, labels=['畅通','轻度','中度','严重'])
stations['level'] = stations['level'].astype(str)

stations.to_file('topsis_result.geojson', driver='GeoJSON')
print('✅ 02_topsis.py 完成')
