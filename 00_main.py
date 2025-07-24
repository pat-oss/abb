# 00_main.py  (Python 3.13 兼容 & 丰富可视化)
import subprocess, os, sys
import pandas as pd
import geopandas as gpd
import folium
from branca.colormap import linear
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont('C:\\Windows\\Fonts\\simhei.ttf')
plt.rcParams['font.family'] = 'SimHei'
# ---------- 1. 运行子脚本 ----------
scripts = ['01_preprocess.py', '02_topsis.py', '03_forecast.py']
for s in scripts:
    print(f"🔄 Running {s} ...")
    subprocess.run([sys.executable, s], check=True)
    print(f"✅ {s} finished\n")

# ---------- 2. 读取关键结果 ----------
stations = gpd.read_file('topsis_result.geojson')
congestion = pd.read_csv('congestion_daily.csv')
mlp_pred   = pd.read_csv('mlp_pred.csv')

print("\n📊 样本数据预览：")
print("站点评价（前 5 行）：")
print(stations[['车站名称', 'TOPSIS_score', 'level']].head())
print("\n客流时间序列（前 5 行）：")
print(congestion.head())
print("\n未来 7 天 MLP 预测：")
print(mlp_pred)

# ---------- 3. 生成 PNG 折线 ----------
plt.figure(figsize=(8,4))
plt.plot(congestion['日期'], congestion['拥堵指数'], label='历史')
plt.plot(mlp_pred['date'], mlp_pred['mlp_pred'], label='MLP 预测', linestyle='--')
plt.title('北京地铁全网拥堵指数')
plt.xlabel('日期')
plt.ylabel('拥堵指数')
plt.legend()
plt.tight_layout()
plt.savefig('congestion_trend.png')
plt.close()
print("📈 折线图已保存：congestion_trend.png")

# ---------- 4. 生成 PNG 分级柱状 ----------
level_counts = stations['level'].value_counts()
plt.figure(figsize=(5,3))
level_counts.plot(kind='bar', color=['green','yellow','orange','red'])
plt.title('站点拥堵等级分布')
plt.xlabel('等级')
plt.ylabel('站点数')
plt.tight_layout()
plt.savefig('station_levels.png')
plt.close()
print("📊 柱状图已保存：station_levels.png")

# ---------- 5. Folium 交互地图 ----------
colormap = linear.Set1_04.scale(0, 1)
m = folium.Map(location=[39.9, 116.4], zoom_start=10)
for _, row in stations.iterrows():
    # 新增两行：跳过空 geometry
    if row.geometry is None:
        continue
    # 下面保持不变
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color={
            '畅通': 'green',
            '轻度': 'lightgreen',
            '中度': 'orange',
            '严重': 'red'
        }[row['level']],
        fill=True,
        fill_opacity=0.8,
        popup=f"{row['车站名称']} - {row['level']}"
    ).add_to(m)
m.save('congestion_map.html')
print("🗺️ 交互地图已保存：congestion_map.html")

print("\n🎉 全部可视化完成！")
