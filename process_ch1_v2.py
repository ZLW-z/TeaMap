# -*- coding: utf-8 -*-
"""
第一章 · 真实数据处理（V2）
 1) 唐代产茶区（点+所属茶字段）→ 按所属茶聚合为面状 GeoJSON（8 大茶区）
    - 每个茶区内的点做 buffer → union → simplify → 面状
    - 为保留"水墨晕染"感，外层追加模糊描边层（可选单独渲染）
 2) 古茶树（Export_Output）→ 按 种类（野生型/其他/栽培型）三色 GeoJSON
输出：
  data/1/tang_areas.geojson   （面状，8 大茶区 + 外层模糊扩展层）
  data/1/tea_trees.geojson    （点，三型真实种类）
"""
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json
import numpy as np
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import shape

BASE = r'd:\Desktop\teamap\data\1'

# ------------------------------------------------------------------
# 1) 唐代产茶区 → 面状（按所属茶聚合）
# ------------------------------------------------------------------
print('[1/2] 唐代产茶区：按所属茶聚合为面...')
tang = gpd.read_file(BASE + r'\唐代产茶区.shp')  # 新带属性版本
tang = tang.to_crs(epsg=4326) if tang.crs is None else tang

# 清洗：所属茶列有些是"山南"有些是"山南茶区"；统一
def norm_name(x):
    if not x: return None
    s = str(x).strip()
    if s == '——': return None
    # 把 "XX/YY" 拆成两条，按 XX 和 YY 各记一次？不，为简单起见，斜杠的归第一个
    if '/' in s:
        s = s.split('/')[0]
    # 去掉"茶区"结尾后缀以合并"山南/山南茶区"
    if s.endswith('茶区') and len(s) > 2:
        s_base = s[:-2]
    else:
        s_base = s
    # 归并到标准名称
    mapping = {
        '山南':'山南茶区','淮南':'淮南茶区','浙西':'浙西茶区','浙东':'浙东茶区',
        '剑南':'剑南茶区','岭南':'岭南茶区','江西':'江西茶区','黔中':'黔中茶区',
        '山南茶区':'山南茶区','淮南茶区':'淮南茶区','浙西茶区':'浙西茶区','浙东茶区':'浙东茶区',
        '剑南茶区':'剑南茶区','岭南茶区':'岭南茶区','江西茶区':'江西茶区','黔中茶区':'黔中茶区',
    }
    return mapping.get(s_base, s if s else None)

tang['_area'] = tang['所属茶'].apply(norm_name)
print('  归一化后茶区分布：')
print(tang['_area'].value_counts().to_string())

# 以度为单位 buffer（≈ 1度 ~ 111km，用 0.7 度约 80km 半径匹配"茶区"大小的模糊面）
# 外层"水墨晕染"再追加一层更淡、更大的扩展
BUFFER_CORE = 1.15   # 核心区（约 130km）—— 对应点+缓冲合并成面
BUFFER_SOFT = 2.2    # 软边界（约 250km）—— 用于半透明晕染层

tang_4326 = tang.copy()
# 投影到等距近似（米制）做 buffer 会更精确，但这里度制 + 后期再做简化也可以
# 为精确 buffer，转到 EPSG:3857（Web墨卡托，米制），buffer，再转回 4326
tang_proj = tang_4326.to_crs(epsg=3857)
AREA_BUFFERS = {
    'core': 115_000,   # 115km
    'soft': 260_000    # 260km
}

features_core = []
features_soft = []
for area_name, sub in tang_proj.groupby('_area'):
    if area_name is None: continue
    # 点 buffer
    cores = sub.geometry.buffer(AREA_BUFFERS['core'])
    softs = sub.geometry.buffer(AREA_BUFFERS['soft'])
    u_core = unary_union(list(cores)).simplify(20_000, preserve_topology=True)
    u_soft = unary_union(list(softs)).simplify(40_000, preserve_topology=True)
    # 转回 4326
    gc_c = gpd.GeoSeries([u_core], crs=3857).to_crs(4326).iloc[0]
    gc_s = gpd.GeoSeries([u_soft], crs=3857).to_crs(4326).iloc[0]
    features_core.append({
        "type":"Feature","geometry":json.loads(gpd.GeoSeries([gc_c]).to_json())['features'][0]['geometry'],
        "properties":{"name": area_name, "layer":"core"}
    })
    features_soft.append({
        "type":"Feature","geometry":json.loads(gpd.GeoSeries([gc_s]).to_json())['features'][0]['geometry'],
        "properties":{"name": area_name, "layer":"soft"}
    })
    print(f'  ✓ {area_name}')

out_tang = {"type":"FeatureCollection","features": features_soft + features_core}
with open(BASE + r'\tang_areas.geojson','w',encoding='utf-8') as f:
    json.dump(out_tang, f, ensure_ascii=False)
print(f'  saved tang_areas.geojson  ({len(features_core)} core + {len(features_soft)} soft)')

# ------------------------------------------------------------------
# 2) 古茶树 → 按真实种类字段导出 GeoJSON
# ------------------------------------------------------------------
print('\n[2/2] 古茶树点：按 种类 字段（野生型/其他/栽培型）导出...')
trees = gpd.read_file(BASE + r'\Export_Output.shp')  # 带属性版本
trees = trees.to_crs(epsg=4326) if trees.crs is None else trees

# 类型映射：
# 种类 3 值：野生型 / 其他 / 栽培型 → 对应 类型 1/2/3（保持之前配色）
type_map = {'野生型': 1, '其他': 2, '栽培型': 3}
type_name_map = {'野生型': '野生型', '其他': '过渡/其他', '栽培型': '栽培型'}
color_map = {1: '#b5394a', 2: '#d98a2b', 3: '#2f8f6b'}

features = []
n_outlier = 0
for i, row in trees.iterrows():
    g = row.geometry
    if g is None: continue
    lon, lat = float(g.x), float(g.y)
    if lon < 70 or lon > 135 or lat < 15 or lat > 45:
        n_outlier += 1
        continue
    kind = str(row['种类']) if row['种类'] else '其他'
    t = type_map.get(kind, 2)
    features.append({
        "type":"Feature",
        "geometry":{"type":"Point","coordinates":[lon, lat]},
        "properties":{
            "name": str(row['茶树名']) if row['茶树名'] else f'古茶树#{i+1}',
            "province": str(row['省份']) if row['省份'] else '',
            "species": str(row['学名']) if row['学名'] else '',
            "kind": kind,
            "type": t,
            "typeName": type_name_map.get(kind, kind),
            "color": color_map[t]
        }
    })

print(f'  类型分布：')
from collections import Counter
print('  ' + str(Counter(f['properties']['typeName'] for f in features)))
print(f'  保留 {len(features)} 个点，异常 {n_outlier} 个')

fc = {"type":"FeatureCollection","features": features}
with open(BASE + r'\tea_trees.geojson','w',encoding='utf-8') as f:
    json.dump(fc, f, ensure_ascii=False)
print('  saved tea_trees.geojson')

print('\n全部完成。')
