from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory

app = Flask(__name__)

# 静态文件快捷路由
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# API：返回折线图数据
@app.route('/api/trend')
def api_trend():
    import pandas as pd
    hist = pd.read_csv('static/csv/congestion_daily.csv')
    pred = pd.read_csv('static/csv/mlp_pred.csv')
    return jsonify({
        'hist': hist.to_dict(orient='records'),
        'pred': pred.to_dict(orient='records')
    })

# API：返回分级柱状图数据
@app.route('/api/levels')
def api_levels():
    import geopandas as gpd
    gdf = gpd.read_file('static/geojson/topsis_result.geojson')
    vc = gdf['level'].value_counts().to_dict()
    return jsonify(vc)

# API：返回地图点位数据
@app.route('/api/stations')
def api_stations():
    import geopandas as gpd
    gdf = gpd.read_file('static/geojson/topsis_result.geojson')
    # 生成 geojson 字典
    return jsonify(gdf.to_crs(4326).__geo_interface__)
# 在 app.py 末尾追加
@app.route('/trend')
def trend():
    return render_template('trend.html')

@app.route('/congestion')
def congestion():
    return render_template('congestion.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')
@app.route('/team')
def team():
    people = [
        {'name': '彭世腾', 'img': 'peng.jpg'},
        {'name': '陈宇扬', 'img': 'chen.jpg'},
        {'name': '冯孟尧', 'img': 'fengmy.jpg'},
        {'name': '冯康',   'img': 'fengk.jpg'},
        {'name': '赵俊全', 'img': 'zhao.jpg'}
    ]
    return render_template('team.html', people=people)
app = Flask(__name__)
from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

# 根目录静态文件
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

# 静态资源统一路由：/static/...
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 示例 API：返回 GeoJSON（按你实际路径改）
@app.route('/api/stations')
def api_stations():
    path = os.path.join('static', 'data', 'stations.geojson')
    with open(path, encoding='utf-8') as f:
        return jsonify(f.read())

# 让 Flask 在 Render 的 10000 端口上监听
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)