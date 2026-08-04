# -*- coding: utf-8 -*-
"""
进一步诊断：
 1) 核对唐代茶区的现代位置——山南茶区/淮南茶区/剑南茶区应该在哪？
    比如：
     - 山南茶区：湖北西北部+陕西南部 (鄂西+陕南) ≈ lat 31-33, lon 108-112
     - 淮南茶区：河南南部+安徽北部+湖北北部 ≈ lat 31-34, lon 114-118
     - 剑南茶区：四川 ≈ lat 27-32, lon 101-108
     - 浙西茶区：浙江北部+江苏南部+安徽南部 ≈ lat 29-32, lon 118-121
     - 浙东茶区：浙江 ≈ lat 27-30.5, lon 119-122
     - 岭南茶区：广东广西福建 ≈ lat 20-26, lon 104-119
     - 黔中茶区：贵州 ≈ lat 24-29, lon 103-109
     - 江西茶区：江西 ≈ lat 24.5-30, lon 113.5-118.5

 2) 古茶树点中明显不合理的分布（如 x≈116.4 y≈39.9 北京位置却标注"云南"）→ 坐标和属性错位。

我们先在前端控制台看：
    - DEM imageOverlay 的 bounds 是多少
    - 唐代茶区 8 大茶区的面，经 GeoJSON 加载后的 bounds 是多少
    - 古茶树点 bounds
    - 北京附近古茶树点真实坐标
"""
import os
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json
import geopandas as gpd
import numpy as np

BASE = r'd:\Desktop\teamap\data\1'

tang = gpd.read_file(BASE + r'\唐代产茶区.shp')
print('=== 唐代产茶区：按所属茶区的坐标范围 ===')
# 归一化
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
        '山南茶区':'山南茶区','淮南茶区':'淮南茶区','浙西茶区':'浙西茶区','浙东茶区':'浙东茶区',
        '剑南茶区':'剑南茶区','岭南茶区':'岭南茶区','江西茶区':'江西茶区','黔中茶区':'黔中茶区',
    }
    return mapping.get(s_base, s if s else None)
tang['_area'] = tang['所属茶'].apply(norm_name)

expected = {
    '山南茶区': (31,33,108,112),
    '淮南茶区': (31,34,114,118),
    '剑南茶区': (27,32,101,108),
    '浙西茶区': (29,32,118,121),
    '浙东茶区': (27,30.5,119,122),
    '岭南茶区': (20,26,104,119),
    '黔中茶区': (24,29,103,109),
    '江西茶区': (24.5,30,113.5,118.5),
}
print(f"{'茶区':<8} {'点数':>3}  {'lat 范围':<12} {'lon 范围':<14} {'期望 lat':<12} {'期望 lon':<14} 匹配")
print('-'*110)
for area, sub in tang.groupby('_area'):
    if area is None: continue
    lats = sub.geometry.y.values
    lons = sub.geometry.x.values
    lat_rng = (round(lats.min(),1), round(lats.max(),1))
    lon_rng = (round(lons.min(),1), round(lons.max(),1))
    exp = expected.get(area)
    ok = '?'
    if exp:
        elat0,elat1,elon0,elon1 = exp
        overlap_lat = max(0, min(lats.max(),elat1)-max(lats.min(),elat0)) / max(1e-6, elat1-elat0)
        overlap_lon = max(0, min(lons.max(),elon1)-max(lons.min(),elon0)) / max(1e-6, elon1-elon0)
        ok = f'lat✓{overlap_lat:.0%} lon✓{overlap_lon:.0%}'
    print(f"{area:<8} {len(sub):>3}  {str(lat_rng):<12} {str(lon_rng):<14} {str(exp[0:2]):<12} {str(exp[2:4]):<14}  {ok}")

print('\n=== 古茶树异常点：属性 vs 坐标位置 ===')
trees = gpd.read_file(BASE + r'\Export_Output.shp')

# 定义省份中心经纬度，判断坐标是否和 province 大致吻合
# 粗略值（省会/区域中心）
province_ref = {
    '云南': (24.5, 102.5),
    '贵州': (26.6, 106.7),
    '四川': (30.7, 104.1),
    '重庆': (29.5, 106.5),
    '湖北': (30.6, 114.3),
    '湖南': (28.2, 112.9),
    '广西': (22.8, 108.4),
    '广东': (23.1, 113.3),
    '福建': (26.1, 119.3),
    '浙江': (30.3, 120.2),
    '安徽': (31.8, 117.3),
    '海南': (19.9, 110.3),
    '台湾': (25.0, 121.5),
}
print('超出其省份+/-8度之外的点（疑似坐标错误）：')
print(f"{'茶树名':<24} {'省份':<5} {'x(lon)':>8} {'y(lat)':>8}  {'应在~':<12}  偏差度")
n_bad = 0
for _, r in trees.iterrows():
    p = str(r['省份']).strip()
    ref = province_ref.get(p)
    if not ref: continue
    rlat, rlon = ref
    dlat = abs(r.y - rlat)
    dlon = abs(r.x - rlon)
    if dlat > 8 or dlon > 8:
        n_bad += 1
        print(f"{str(r['茶树名']):<24} {p:<5} {r.x:>8.2f} {r.y:>8.2f}  ({rlat:.1f},{rlon:.1f})  lat+{dlat:.1f} lon+{dlon:.1f}")

print(f'\n共 {n_bad}/{len(trees)} 个疑似坐标错位')
print('\n疑似坐标=北京的点(lon~116.4,lat~39.9)统计：')
beijing = trees[(trees.x.between(115.6,117.0)) & (trees.y.between(39.3,40.8))]
print(beijing[['茶树名','省份','x','y','种类']].to_string())
