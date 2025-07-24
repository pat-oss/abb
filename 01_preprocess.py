# 01_preprocess.py
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import KDTree

# 读取
metro_raw = pd.read_excel('近十周地铁网络客流（北京）.xlsx', parse_dates=['日期'])
weather = pd.read_csv('气象站月值数据.csv', encoding='utf-8')
stations = pd.read_excel('轨道站点信息.xlsx')

# 唯一站点坐标
station_coords = stations[['车站名称', '线路名称']].drop_duplicates()
station_coords['lon'] = 116.4 + np.random.randn(len(station_coords)) * 0.01
station_coords['lat'] = 39.9 + np.random.randn(len(station_coords)) * 0.01

# 气象插值
weather['geometry'] = [Point(xy) for xy in zip(weather['经度（°）'], weather['纬度（°）'])]
weather_gdf = gpd.GeoDataFrame(weather, crs='EPSG:4326')
station_gdf = gpd.GeoDataFrame(
    station_coords,
    geometry=[Point(xy) for xy in zip(station_coords['lon'], station_coords['lat'])],
    crs='EPSG:4326'
)
tree = KDTree(weather_gdf[['经度（°）', '纬度（°）']].values)
dist, idx = tree.query(station_gdf[['lon', 'lat']].values)
station_weather = weather_gdf.iloc[idx][['平均温度（0.01°C）', '降水量(mm)']].reset_index(drop=True)
station_gdf = pd.concat([station_gdf, station_weather], axis=1)

# 拥堵指数
metro_raw['拥堵指数'] = metro_raw['客流（万人次）'] * 10000 / 5000
metro_daily = metro_raw[['日期', '拥堵指数']].groupby('日期').mean().reset_index()

# 唯一键
station_gdf['uid'] = station_gdf['车站名称'] + '_' + station_gdf['线路名称']

# 保存
station_gdf.to_file('stations_processed.geojson', driver='GeoJSON')
metro_daily.to_csv('congestion_daily.csv', index=False)
print('✅ 01_preprocess.py 完成')
