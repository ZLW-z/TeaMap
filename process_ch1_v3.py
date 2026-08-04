# -*- coding: utf-8 -*-
"""
第一章 · 真实数据处理（V3 - 图层对齐修复版）
改动点：
 1) DEM PNG 重渲染：使用 rasterio 读取(downsample)+matplotlib.imsave 保存，
    输出 PNG 的 extent 与 tif bounds 完全一致，且 origin='upper' 与 Leaflet imageOverlay 契约一致。
    同时输出 bounds.json，前端直接读（无需手填）。
 2) 唐代茶区面：针对 8 大茶区的真实历史地理范围，使用"自适应 buffer"，
    避免岭南/江西/黔中因为样本点稀疏或集中而明显偏小偏北。
 3) 古茶树点：两层过滤 + 修正
     a) 简单范围裁剪（lon 70-135, lat 14-45）
     b) 省份-坐标 一致性检测：按"茶树名+省份关键字"做修正（如"巴达""南糯山""勐库"都在云南版纳/普洱一带，
        但它们的坐标恰好是北京，显然是 x/y 填错 → 回退到"茶树名"对应的已知真实产地坐标；
        lon=10.44 的非洲点 直接删除）
"""
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json
import numpy as np
import geopandas as gpd
from shapely.ops import unary_union
from collections import Counter

# -------- 依赖：DEM 渲染需要 rasterio + matplotlib + PIL --------
import rasterio
from matplotlib.colors import LightSource, Normalize, LinearSegmentedColormap

# ------------------------------------------------------------------
# 自定义：茶主题六色系 DEM 渲染
# 固定六色 #EFE9DA #F7F4EB #516D33 #B28F4C #C3C19A #5C7C3A + 色带相近衍生
# 海→陆渐变：深橄榄绿(海) → 米灰(岸) → 米白(低地) → 褐金(中山) → 深褐金(高原)
# ------------------------------------------------------------------
TEA_EARTH_COLORS = [
    (0.00, '#3D5428'),   # 深海：更深橄榄绿
    (0.20, '#46612C'),   # 浅海：深橄榄绿二档
    (0.38, '#516D33'),   # 近海：深橄榄绿（主色）
    (0.45, '#C3C19A'),   # 海岸线：米灰
    (0.52, '#F7F4EB'),   # 低地：最浅米白
    (0.62, '#EFE9DA'),   # 平原：浅米色
    (0.72, '#C3C19A'),   # 丘陵：米灰
    (0.82, '#B28F4C'),   # 中山：褐金
    (0.92, '#8E6F38'),   # 高原：深褐金
    (1.00, '#F7F4EB'),   # 雪山：最浅米白
]
pos = [c[0] for c in TEA_EARTH_COLORS]
colors = [c[1] for c in TEA_EARTH_COLORS]
cmap_tea = LinearSegmentedColormap.from_list('tea_earth', list(zip(pos, colors)))


BASE = r'd:\Desktop\teamap\data\1'
DEM_SRC = BASE + r'\高程.tif'
DEM_OUT_PNG = BASE + r'\dem_relief.png'
DEM_OUT_BOUNDS = BASE + r'\dem_bounds.json'
TANG_OUT = BASE + r'\tang_areas.geojson'
TREE_OUT = BASE + r'\tea_trees.geojson'

# ===================== 1) DEM PNG（bounds 完全对齐 tif） =====================
print('[1/3] DEM 重渲染：严格对齐 GeoTiff bounds ...')
DOWNSAMPLE = 6  # 14782/6≈2464, 11936/6≈1989，保持比例
with rasterio.open(DEM_SRC) as dem:
    # 真正的 bounds（rasterio 直接读 tif tag，不受 transform 解包顺序影响）
    # rasterio 的 BoundingBox 是 (left, bottom, right, top) （lon/lat）
    left, bottom, right, top = dem.bounds.left, dem.bounds.bottom, dem.bounds.right, dem.bounds.top
    crs = dem.crs

    # 按 DOWNSAMPLE 读取（省内存 + 前端 PNG 尺寸合理）
    outH = dem.height // DOWNSAMPLE
    outW = dem.width  // DOWNSAMPLE
    # 使用 read 加 out_shape 做降采样（rasterio 会自动 average-like 重采样）
    arr = dem.read(1, out_shape=(outH, outW), resampling=rasterio.enums.Resampling.bilinear, masked=True)

    # 用 LightSource 做山体阴影渲染（和之前版本风格一致）
    elev = np.ma.masked_array(arr, mask=arr.mask, fill_value=-9999)
    ls = LightSource(azdeg=315, altdeg=40)
    # 归一化：去除负异常（海/掩码）
    valid = elev[~elev.mask]
    vmin, vmax = np.percentile(valid.compressed(), [1, 99]) if valid.size else (0, 3000)
    norm = Normalize(vmin=vmin, vmax=vmax)

    # 生成带阴影的 RGB（使用自定义茶文化配色）
    rgb_shaded = ls.shade(elev.filled(np.nan), cmap=cmap_tea, norm=norm, blend_mode='soft', vert_exag=15)

    # 填充底色：浅米灰 #DDD5C0（与地图容器背景同色），让 DEM 无边框融入容器
    # 所有 mask 区域（海洋/无数据）都填充为浅米灰，消除"矩形背景框"
    BG_COLOR = np.array([0xDD/255, 0xD5/255, 0xC0/255], dtype=np.float32)
    rgb = rgb_shaded[:, :, 0:3].copy()
    for c in range(3):
        rgb[c] = np.where(elev.mask, BG_COLOR[c], rgb[c])

    # 保存为 RGB（不使用 alpha，整张图铺满）
    from PIL import Image
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), mode='RGB')
    img.save(DEM_OUT_PNG, optimize=True)
    print(f'  saved: {DEM_OUT_PNG}  ({outW}x{outH})')
    print(f'  bounds (lon lat): left={left:.6f} bottom={bottom:.6f} right={right:.6f} top={top:.6f}')

    # 写 bounds.json（前端直接读）
    bounds = {
        "south": bottom,   # lat min
        "west":  left,     # lon min
        "north": top,      # lat max
        "east":  right,    # lon max
        "southWest": [bottom, left],  # Leaflet [[s,w],[n,e]]
        "northEast": [top, right],
        "center": [(top+bottom)/2, (left+right)/2],
        "imageSize": [outW, outH],
        "crs": str(crs),
    }
    with open(DEM_OUT_BOUNDS, 'w', encoding='utf-8') as f:
        json.dump(bounds, f, ensure_ascii=False, indent=2)
    print(f'  saved: {DEM_OUT_BOUNDS}')

# ===================== 2) 唐代茶区：自适应 buffer =====================
print('\n[2/3] 唐代产茶区：按所属茶聚合为面 + 自适应 buffer ...')
tang = gpd.read_file(BASE + r'\唐代产茶区.shp')
tang = tang.to_crs(epsg=4326) if tang.crs is None else tang

def norm_name(x):
    if not x: return None
    s = str(x).strip()
    if s == '——': return None
    if '/' in s: s = s.split('/')[0]
    if s.endswith('茶区') and len(s) > 2:
        s_base = s[:-2]
    else:
        s_base = s
    mapping = {
        '山南':'山南茶区','淮南':'淮南茶区','浙西':'浙西茶区','浙东':'浙东茶区',
        '剑南':'剑南茶区','岭南':'岭南茶区','江西':'江西茶区','黔中':'黔中茶区',
    }
    return mapping.get(s_base, s if s else None)

tang['_area'] = tang['所属茶'].apply(norm_name)
print('  茶区点数分布：')
print(tang['_area'].value_counts().to_string())

# 每个茶区的"目标范围"——按真实历史茶区地理范围（以 lat0,lat1,lon0,lon1 给出）
# 用于"自适应 buffer"：如果原始点位聚合得到的面小于这个目标范围的 1/3，就增大 buffer 让它大致匹配
TARGET_AREA_BOUNDS = {
    '山南茶区': (31.0, 33.5, 106.5, 113.5),   # 鄂西+陕南+川东
    '淮南茶区': (31.0, 35.0, 113.0, 119.5),   # 河南南部+皖中北+鄂北
    '剑南茶区': (26.0, 33.5,  99.0, 109.0),   # 四川（含川西高原边缘）
    '浙西茶区': (28.5, 32.5, 117.0, 122.0),   # 浙北+苏南+皖南
    '浙东茶区': (26.5, 31.0, 118.5, 123.0),   # 浙江+闽东北+东海沿海
    '岭南茶区': (18.0, 26.5, 104.0, 120.0),   # 粤桂闽琼
    '黔中茶区': (23.5, 30.0, 103.0, 110.0),   # 贵州
    '江西茶区': (24.0, 31.0, 113.0, 119.0),   # 江西
}

tang_proj = tang.to_crs(epsg=3857)  # 米制 buffer

features_core = []

for area_name, sub in tang_proj.groupby('_area'):
    if area_name is None: continue
    # 先算这个茶区真实点的 bounding box，再计算自适应 buffer
    sub_4326 = sub.to_crs(4326)
    p_lats = sub_4326.geometry.y.values
    p_lons = sub_4326.geometry.x.values
    cur_lat_span = max(1.0, p_lats.max() - p_lats.min())
    cur_lon_span = max(1.0, p_lons.max() - p_lons.min())

    # 目标跨度
    target = TARGET_AREA_BOUNDS.get(area_name)
    if target:
        lat0, lat1, lon0, lon1 = target
        tgt_lat_span = lat1 - lat0
        tgt_lon_span = lon1 - lon0
        # 当前面的理想 buffer 半径：(目标跨度 - 当前跨度) / 2
        mid_lat = np.mean(p_lats)
        lat_m = (tgt_lat_span - cur_lat_span) / 2 * 111_000
        lon_m = (tgt_lon_span - cur_lon_span) / 2 * 111_000 * np.cos(np.deg2rad(mid_lat))
        buf_core_m = min(350_000, max(70_000, (lat_m + lon_m) / 2))
    else:
        buf_core_m = 150_000

    cores = sub.geometry.buffer(buf_core_m)
    u_core = unary_union(list(cores)).simplify(20_000, preserve_topology=True)

    gc_c = gpd.GeoSeries([u_core], crs=3857).to_crs(4326).iloc[0]
    features_core.append({
        "type":"Feature",
        "geometry": json.loads(gpd.GeoSeries([gc_c]).to_json())['features'][0]['geometry'],
        "properties": {"name": area_name, "layer": "core", "buffer_m": int(buf_core_m)}
    })
    print(f'  ✓ {area_name:<8} core={int(buf_core_m)/1000:>4.0f}km  点数={len(sub)}')

out_tang = {"type":"FeatureCollection","features": features_core}
with open(TANG_OUT, 'w', encoding='utf-8') as f:
    json.dump(out_tang, f, ensure_ascii=False)
print(f'  saved: {TANG_OUT}  ({len(features_core)} core)')

# ===================== 3) 古茶树：坐标清洗 & 异常修正 =====================
print('\n[3/3] 古茶树点：按真实种类 + 坐标清洗导出 ...')
trees = gpd.read_file(BASE + r'\Export_Output.shp')
trees = trees.to_crs(epsg=4326) if trees.crs is None else trees

# ---------- 坐标修正：茶树名关键字 → 真实地理坐标 ----------
# 这批数据里有 20 条的坐标恰好是北京天安门附近（39.95,116.4），但省份写云南/福建。
# 这类属于 x/y 录入错误——根据茶树名或其知名产地，赋值一个相对正确的坐标。
REPAIR_BY_KEYWORD = [
    # (关键字, 省份, 建议 lat, lon, 说明)
    ('勐库',       '云南', 23.45,  99.85, '云南临沧双江县勐库镇'),
    ('大雪山',     '云南', 24.02, 100.06, '云南临沧永德/双江大雪山'),
    ('冰岛',       '云南', 23.62,  99.91, '临沧双江冰岛村'),
    ('昔归',       '云南', 23.73, 100.45, '临沧临翔区邦东乡昔归'),
    ('那焦',       '云南', 23.42,  99.78, '临沧双江那焦村'),
    ('坝糯',       '云南', 23.38,  99.86, '临沧双江坝糯'),
    ('巴达',       '云南', 21.96, 100.11, '西双版纳勐海巴达'),
    ('南糯山',     '云南', 21.92, 100.61, '西双版纳勐海南糯山'),
    ('布朗山',     '云南', 21.78, 100.38, '西双版纳勐海布朗山'),
    ('帕沙',       '云南', 22.05, 100.78, '西双版纳勐海帕沙'),
    ('班章',       '云南', 21.84, 100.62, '西双版纳勐海老班章'),
    ('易武',       '云南', 22.07, 101.40, '西双版纳勐腊易武'),
    ('曼糯',       '云南', 22.28, 100.82, '西双版纳勐往曼糯'),
    ('景迈',       '云南', 22.18, 100.00, '普洱澜沧景迈山'),
    ('邦崴',       '云南', 22.56,  99.93, '普洱澜沧邦崴'),
    ('千家寨',     '云南', 23.94, 101.06, '普洱镇沅千家寨'),
    ('景谷',       '云南', 23.45, 100.70, '普洱景谷'),
    ('宁洱',       '云南', 23.06, 101.04, '普洱宁洱'),
    ('镇沅',       '云南', 23.89, 100.73, '普洱镇沅'),
    ('无量山',     '云南', 24.50, 100.67, '大理-普洱无量山'),
    ('哀牢山',     '云南', 24.20, 101.50, '楚雄-玉溪哀牢山'),
    ('古永',       '云南', 25.15,  98.30, '保山腾冲古永（猴桥）'),
    ('芒洪',       '云南', 23.42,  99.72, '临沧沧源芒洪'),
    ('源头茶',     '云南', 24.68,  98.85, '保山腾冲源头/云华'),
    ('芹菜塘',     '云南', 25.32,  98.86, '保山腾冲芹菜塘'),
    ('标水崖',     '云南', 24.38,  98.78, '保山龙陵标水崖'),
    ('沿江村',     '云南', 24.65,  98.55, '保山腾冲沿江村'),
    ('石佛',       '云南', 24.98,  98.76, '保山隆阳石佛山/杨柳一带'),
    ('新房子',     '云南', 22.56, 100.53, '普洱澜沧新房子'),
    ('玉溪元江',   '云南', 23.56, 101.95, '玉溪元江'),
    ('元江',       '云南', 23.56, 101.95, '玉溪元江'),
    ('曲靖师宗',   '云南', 24.83, 103.98, '曲靖师宗'),
    ('师宗',       '云南', 24.83, 103.98, '曲靖师宗'),
    ('文山麻栗坡', '云南', 23.12, 104.71, '文山麻栗坡'),
    ('麻栗坡',     '云南', 23.12, 104.71, '文山麻栗坡'),
    ('斯须乐',     '云南', 22.20, 101.12, '西双版纳勐腊/江城一带'),
    ('大箐',       '云南', 24.20, 100.30, '普洱景东/镇沅大箐'),
    # 福建肉桂：福建武夷山市（肉桂发源地）
    ('肉桂',       '福建', 27.76, 118.03, '福建南平武夷山肉桂'),
    ('大红袍',     '福建', 27.64, 118.03, '福建南平武夷山九龙窠大红袍'),
    # 四川 / 黄山大茶树 —— 黄山属安徽，但名字叫黄山，坐标应在安徽黄山
    ('黄山',       '安徽', 30.13, 118.17, '安徽黄山市黄山'),
    ('雷波大茶树', '四川', 28.26, 103.57, '四川凉山雷波县'),
    ('大木茶',     '四川', 27.90, 103.80, '四川宜宾/川南大木茶'),
]

# ---------- 省份中心 ----------
PROVINCE_CENTER = {
    '云南':(24.5,102.5), '贵州':(26.6,106.7), '四川':(30.7,104.1), '重庆':(29.5,106.5),
    '湖北':(30.6,114.3), '湖南':(28.2,112.9), '广西':(22.8,108.4), '广东':(23.1,113.3),
    '福建':(26.1,119.3), '浙江':(30.3,120.2), '安徽':(31.8,117.3), '海南':(19.9,110.3),
    '台湾':(25.0,121.5), '陕西':(34.3,108.9), '河南':(34.6,113.6), '江西':(28.7,115.9),
    '江苏':(32.0,118.8), '山东':(36.7,117.0), '甘肃':(36.1,103.8), '西藏':(29.6,91.1),
    '湖南':(28.2,112.9),
}

type_map = {'野生型': 1, '其他': 2, '栽培型': 3}
type_name_map = {'野生型': '野生型', '其他': '过渡/其他', '栽培型': '栽培型'}
color_map = {1: '#C8462E', 2: '#B28F4C', 3: '#2F5D3A'}

features = []
stats = {'raw': len(trees), 'keyword_repaired':0, 'outlier_drop':0, 'province_mismatch_drop':0, 'keep':0}

for i, row in trees.iterrows():
    g = row.geometry
    if g is None: continue
    lon, lat = float(g.x), float(g.y)
    name = str(row['茶树名']) if row['茶树名'] else f'古茶树#{i+1}'
    prov = str(row['省份']) if row['省份'] else ''
    kind = str(row['种类']) if row['种类'] else '其他'

    # ---- 1) 关键字修正（北京坐标的云南茶点们）
    matched_key = False
    for kw, kwp, k_lat, k_lon, _ in REPAIR_BY_KEYWORD:
        if kw in name or (kw in prov and kw in REPAIR_BY_KEYWORD[0]):
            if kw in name:
                # 只在关键字匹配茶树名时覆盖（避免'云南'作为省份误触发）
                lat, lon = k_lat, k_lon
                matched_key = True
                break
    if matched_key:
        stats['keyword_repaired'] += 1

    # ---- 2) 硬异常裁剪（非洲/欧洲/太平洋上的点）
    if lon < 70 or lon > 136 or lat < 14 or lat > 46:
        stats['outlier_drop'] += 1
        continue

    # ---- 3) 省份-坐标一致性（允许 10° 容差）
    pc = PROVINCE_CENTER.get(prov)
    if pc:
        p_lat, p_lon = pc
        if abs(lat - p_lat) > 10 or abs(lon - p_lon) > 10:
            # 如果已经被关键字修正过，可能省份写的还是错的（如"黄山"省份写四川），
            # 但它实际应该在安徽——这种保留，因为关键字 > 省份。
            if matched_key:
                # 把省份也改成更合理的
                for kw, kwp, *_ in REPAIR_BY_KEYWORD:
                    if kw in name:
                        prov = kwp
                        break
            else:
                stats['province_mismatch_drop'] += 1
                continue

    t = type_map.get(kind, 2)
    features.append({
        "type":"Feature",
        "geometry":{"type":"Point","coordinates":[lon, lat]},
        "properties":{
            "name": name,
            "province": prov,
            "species": str(row['学名']) if row['学名'] else '',
            "kind": kind,
            "type": t,
            "typeName": type_name_map.get(kind, kind),
            "color": color_map[t],
            "repaired": matched_key
        }
    })
    stats['keep'] += 1

print(f'  统计：')
for k,v in stats.items(): print(f'    {k}: {v}')
cnt = Counter(f['properties']['typeName'] for f in features)
print(f'  类型分布：{dict(cnt)}')

# 省份分布
prov_cnt = Counter(f['properties']['province'] for f in features)
print(f'  省份分布：{dict(prov_cnt)}')

fc = {"type":"FeatureCollection","features": features}
with open(TREE_OUT, 'w', encoding='utf-8') as f:
    json.dump(fc, f, ensure_ascii=False)
print(f'  saved: {TREE_OUT}')

print('\n全部完成。')
