# -*- coding: utf-8 -*-
"""
将中国省份 GeoJSON (EPSG4326 WGS84 lon/lat) 重投影为 Albers 等积圆锥 (米)
输出: china-provinces-albers.geojson (与 createAlbersCRS 画布同一坐标系)
"""
import os, json
from pyproj import CRS, Transformer

IN_DIR  = r'd:\Desktop\teamap\public\data\2'
SRC     = os.path.join(IN_DIR, 'china-provinces.geojson')
DST     = os.path.join(IN_DIR, 'china-provinces-albers.geojson')

EPSG4326 = CRS.from_epsg(4326)
ALBERS_PROJ4 = '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
ALBERS_CRS = CRS.from_string(ALBERS_PROJ4)
ll_to_albers = Transformer.from_crs(EPSG4326, ALBERS_CRS, always_xy=True)

with open(SRC, 'r', encoding='utf-8') as f:
    gj = json.load(f)

def proj_ring(ring):
    # ring: [[lon,lat], ...]  →  [[x_albers, y_albers], ...]
    # 为了与 Leaflet L.GeoJSON 在 CRS.Simple 下解析一致, 我们存 [x, y] (即 [easting, northing]),
    # 但 Leaflet 要求坐标是 [lat, lng] 风格, 实际上当使用 CRS.Simple 时它直接接受 [y, x] 作为 coords.
    # 更安全: 我们输出一个单独的 .json (不是 geojson) 给 L.polygon 直接用, 或者构造 GeoJSON 时让 coords = [y, x].
    # Leaflet L.GeoJSON 对每个 coord 取 (coord[1], coord[0]) 作为 latlng → 传给 CRS.latLngToPoint(latlng):
    #   latlng.lat = coord[1], latlng.lng = coord[0]
    # 而 CRS.Simple 的 project(LatLng(lat, lng)) = Point(lng, lat)
    # 所以如果我们让 coord[0]=x, coord[1]=y, 那么 project 得到 Point(x, y) 正是我们想要的米坐标.
    out = []
    for c in ring:
        x, y = ll_to_albers.transform(c[0], c[1])
        out.append([x, y])   # [easting, northing]
    return out

def proj_poly(poly):
    # poly: [ring, hole1, hole2, ...]
    return [proj_ring(r) for r in poly]

new_feats = []
for f in gj['features']:
    g = f.get('geometry')
    if not g: continue
    t = g['type']
    if t == 'Polygon':
        new_coords = proj_poly(g['coordinates'])
        new_geom = {'type': 'Polygon', 'coordinates': new_coords}
    elif t == 'MultiPolygon':
        new_coords = [proj_poly(p) for p in g['coordinates']]
        new_geom = {'type': 'MultiPolygon', 'coordinates': new_coords}
    else:
        # 点 / 线: 不处理, 跳过
        continue
    new_feats.append({'type': 'Feature', 'properties': f.get('properties', {}), 'geometry': new_geom})

out = {'type': 'FeatureCollection',
       'name': 'china-provinces-albers',
       'crs': {'type':'name','properties':{'name': ALBERS_PROJ4}},
       'features': new_feats}
with open(DST, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)

print('Done:', DST, 'features=', len(new_feats), 'size=', os.path.getsize(DST))
