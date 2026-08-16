"""
将 teas.json 中的经纬度 (lng, lat) 转换为 Albers 米坐标
输出: teas-albers.json - 保留所有字段, 附加 { x_m, y_m }
"""
import json, os
from pyproj import CRS, Transformer

ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

SRC = os.path.join(os.path.dirname(__file__), '..', 'data', '3', 'teas.json')
DST = os.path.join(os.path.dirname(__file__), '..', 'data', '3', 'teas-albers.json')

crs_wgs = CRS.from_epsg(4326)
crs_albers = CRS.from_proj4(ALBERS_PROJ4)
t = Transformer.from_crs(crs_wgs, crs_albers, always_xy=True)

with open(SRC, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item.get('lng') is None or item.get('lat') is None:
        continue
    x_m, y_m = t.transform(item['lng'], item['lat'])
    item['x_m'] = round(x_m, 2)
    item['y_m'] = round(y_m, 2)

with open(DST, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'done: {len(data)} items -> {DST}')
