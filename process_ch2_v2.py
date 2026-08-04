# -*- coding: utf-8 -*-
"""
第二章数据处理脚本：5大茶树生态适宜性因子
1. 降水适宜性  — 从2020-2024年均降水量重分类为3级
2. 气温适宜性  — 现有均温栅格(3级)
3. 积温适宜性  — 现有活动积温栅格(3级)
4. 光照适宜性  — 现有太阳辐射栅格(3级)
5. 土壤酸碱度  — 已有pH适宜性(4级)

输出：统一分辨率/投影的PNG + bounds.json + config.json + 综合分析图
"""
import os, json, shutil
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import reproject, Resampling
from PIL import Image
import geopandas as gpd
from shapely.geometry import shape
import scipy.ndimage as nd
from collections import Counter

SRC_PREC = r'D:\Desktop\星湖杯\茶叶\prec'
SRC_TEMP = r'D:\Desktop\星湖杯\茶叶\temp'
SRC_RAD  = r'D:\Desktop\星湖杯\茶叶\光照'
DST      = r'D:\Desktop\teamap\data\2'

# 统一目标分辨率（对齐 DEM 原始分辨率 ~1km）
DS = 8  # 降采样因子
REF_BOUNDS = (73.49, 3.82, 135.10, 53.57)  # 统一边界 (left,bottom,right,top)
REF_CRS = 'EPSG:4326'

# 颜色方案（统一色系）
FACTOR_CONFIG = {
    'precip': {
        'name': '降水适宜性', 'unit': '',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#A8C5A0'},
            {'value': 2, 'label': '较适宜',   'color': '#6BA368'},
            {'value': 3, 'label': '最适宜',   'color': '#2F6B2F'},
        ]
    },
    'temp': {
        'name': '气温适宜性', 'unit': '',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '低温适宜', 'color': '#9AC4D6'},
            {'value': 2, 'label': '中温适宜', 'color': '#5C9EAF'},
            {'value': 3, 'label': '高温适宜', 'color': '#C8462E'},
        ]
    },
    'accum': {
        'name': '积温适宜性', 'unit': '',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#D4B44C'},
            {'value': 2, 'label': '较适宜',   'color': '#93B55A'},
            {'value': 3, 'label': '最适宜',   'color': '#516D33'},
        ]
    },
    'rad': {
        'name': '光照适宜性', 'unit': '',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '最适宜',   'color': '#2F6B2F'},
            {'value': 2, 'label': '较适宜',   'color': '#5C9EAF'},
            {'value': 3, 'label': '限制适宜', 'color': '#C3C19A'},
        ]
    },
    'ph': {
        'name': '土壤酸碱度适宜性', 'unit': '',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#D4B44C'},
            {'value': 2, 'label': '较适宜',   'color': '#5C7C3A'},
            {'value': 3, 'label': '最适宜',   'color': '#516D33'},
        ]
    },
}

# 初始化输出目录
os.makedirs(DST, exist_ok=True)

# ============================================================
# 加载省份边界 + 统一裁剪
# ============================================================
print('加载省份边界...')
prov_path = os.path.join(DST, 'china-provinces.geojson')
if not os.path.exists(prov_path):
    shutil.copy(r'D:\Desktop\teamap\data\1\china_provinces_background.geojson', prov_path)
china = gpd.read_file(prov_path)
if china.crs is None:
    china = china.set_crs(REF_CRS)
china_geom = [shape(g) for g in china.geometry]

# 计算统一目标网格
ref_left, ref_bottom, ref_right, ref_top = REF_BOUNDS
ref_width = 7392   # 对齐原始 DEM 宽度
ref_height = 5969  # 对齐原始 DEM 高度
pixel_size_x = (ref_right - ref_left) / ref_width
pixel_size_y = (ref_top - ref_bottom) / ref_height

# ============================================================
# 1. 降水适宜性 — 从原始年降水量数据重分类
# ============================================================
print('\n[1/5] 降水适宜性 ...')
precip_years = ['_2020', '_2021', '_2022', '_2023', '_2024']
precip_sum = None
precip_count = 0

for yr in precip_years:
    path = os.path.join(SRC_PREC, yr, 'w001001.adf')
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        if precip_sum is None:
            precip_sum = np.zeros(arr.shape, dtype=np.float64)
        valid = arr != src.nodata
        precip_sum[valid] += arr[valid]
        precip_count += valid.astype(np.int16)

# 年均降水量
with np.errstate(divide='ignore', invalid='ignore'):
    precip_avg = np.where(precip_count > 0, precip_sum / np.maximum(precip_count, 1), np.nan)

print(f'  年均降水: {np.nanmin(precip_avg):.1f} ~ {np.nanmax(precip_avg):.1f} mm, 均值 {np.nanmean(precip_avg):.1f} mm')

# 重分类为3级（基于茶树适宜性）
# 最适宜: 1200-2500mm, 较适宜: 800-1200mm 或 2500-3500mm, 限制适宜: 500-800mm 或 3500-4500mm
# 0=nodata/不适宜
precip_class = np.zeros(precip_avg.shape, dtype=np.uint8)
valid_mask = np.isfinite(precip_avg)

# 最适宜 (3): 1200-2500
precip_class[valid_mask & (precip_avg >= 1200) & (precip_avg <= 2500)] = 3
# 较适宜 (2): 800-1200 或 2500-3500
precip_class[valid_mask & ((precip_avg >= 800) & (precip_avg < 1200))] = 2
precip_class[valid_mask & ((precip_avg > 2500) & (precip_avg <= 3500))] = 2
# 限制适宜 (1): 500-800 或 3500-4500
precip_class[valid_mask & ((precip_avg >= 500) & (precip_avg < 800))] = 1
precip_class[valid_mask & ((precip_avg > 3500) & (precip_avg <= 4500))] = 1
# 其他 valid = 0 (不适宜)
precip_class[valid_mask & (precip_class == 0)] = 0

# nodata 标记
nodata_mask = ~valid_mask | (precip_avg < 400) | (precip_avg > 5000)
precip_class[nodata_mask] = 255

# 裁剪到中国范围
with rasterio.open(os.path.join(SRC_PREC, '_2020', 'w001001.adf')) as src_ref:
    # 创建临时 rasterio 源用于裁剪
    from rasterio.transform import from_bounds
    transform_orig = src_ref.transform
    orig_width, orig_height = src_ref.width, src_ref.height

# 裁剪到中国
with rasterio.open(os.path.join(SRC_PREC, '_2020', 'w001001.adf')) as src_ref:
    profile = src_ref.profile.copy()
    profile.update(count=1, dtype='uint8', nodata=255)

import tempfile, uuid
tmp_precip = os.path.join(DST, 'tmp_precip.tif')
with rasterio.open(tmp_precip, 'w', **profile) as dst:
    dst.write(precip_class, 1)

with rasterio.open(tmp_precip) as src_p:
    precip_cropped, precip_transform = rio_mask(src_p, china_geom, crop=True, nodata=255)
    precip_data = precip_cropped[0]

os.remove(tmp_precip)

# 统计
v, c = np.unique(precip_data, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  降水 {lb}({val}): {cnt} px ({100*cnt/precip_data.size:.1f}%)')

# 保存为统一分辨率
precip_final, precip_transform_final = _reproject_to_grid(
    precip_data, precip_transform, REF_BOUNDS, ref_width, ref_height, src_p.crs
)

# ============================================================
# 2. 气温适宜性
# ============================================================
print('\n[2/5] 气温适宜性 ...')
temp_file = os.path.join(DST, '多年均温.tif')
with rasterio.open(temp_file) as src:
    temp_arr = src.read(1).astype(np.uint8)
    # 值0=低温适宜? 1=中温? 2=高温? 3=最适?
    # 根据原数据分布调整: 0占97.4% 应该是nodata
    temp_valid = temp_arr != 0
    # 转换: 0->255(nodata), 1->1, 2->2, 3->3
    temp_class = np.where(temp_valid, temp_arr, 255)
    
    v, c = np.unique(temp_class, return_counts=True)
    for val, cnt in zip(v, c):
        lb = {0:'?',1:'低温适宜',2:'中温适宜',3:'高温适宜',255:'nodata'}.get(val,'?')
        print(f'  气温 {lb}({val}): {cnt} px ({100*cnt/temp_class.size:.1f}%)')

# 裁剪到中国范围
profile = src.profile.copy()
profile.update(count=1, dtype='uint8', nodata=255)
tmp_temp = os.path.join(DST, 'tmp_temp.tif')
with rasterio.open(tmp_temp, 'w', **profile) as dst:
    dst.write(temp_class, 1)

with rasterio.open(tmp_temp) as src_t:
    temp_cropped, temp_transform_c = rio_mask(src_t, china_geom, crop=True, nodata=255)
    temp_data = temp_cropped[0]
    temp_crs = src_t.crs

os.remove(tmp_temp)

# ============================================================
# 3. 积温适宜性
# ============================================================
print('\n[3/5] 积温适宜性 ...')
accum_file = os.path.join(DST, '多年平均活动积温.tif')
with rasterio.open(accum_file) as src:
    accum_arr = src.read(1).astype(np.int16)
    # -9999=nodata, 1/2/3 = 限制/较/最适宜
    accum_class = np.where(accum_arr == -9999, 255, accum_arr).astype(np.uint8)
    
    v, c = np.unique(accum_class, return_counts=True)
    for val, cnt in zip(v, c):
        lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
        print(f'  积温 {lb}({val}): {cnt} px ({100*cnt/accum_class.size:.1f}%)')

# 裁剪
profile = src.profile.copy()
profile.update(count=1, dtype='uint8', nodata=255)
tmp_accum = os.path.join(DST, 'tmp_accum.tif')
with rasterio.open(tmp_accum, 'w', **profile) as dst:
    dst.write(accum_class, 1)

with rasterio.open(tmp_accum) as src_a:
    accum_cropped, accum_transform_c = rio_mask(src_a, china_geom, crop=True, nodata=255)
    accum_data = accum_cropped[0]
    accum_crs = src_a.crs

os.remove(tmp_accum)

# ============================================================
# 4. 光照适宜性
# ============================================================
print('\n[4/5] 光照适宜性 ...')
rad_file = os.path.join(DST, 'radiation_suitability_reclass.tif')
with rasterio.open(rad_file) as src:
    rad_arr = src.read(1).astype(np.int16)
    # -9999=nodata, 1=最适宜, 2=较适宜, 3=限制适宜
    rad_class = np.where(rad_arr == -9999, 255, rad_arr).astype(np.uint8)
    
    v, c = np.unique(rad_class, return_counts=True)
    for val, cnt in zip(v, c):
        lb = {0:'不适宜',1:'最适宜',2:'较适宜',3:'限制适宜',255:'nodata'}.get(val,'?')
        print(f'  光照 {lb}({val}): {cnt} px ({100*cnt/rad_class.size:.1f}%)')

# 裁剪
profile = src.profile.copy()
profile.update(count=1, dtype='uint8', nodata=255)
tmp_rad = os.path.join(DST, 'tmp_rad.tif')
with rasterio.open(tmp_rad, 'w', **profile) as dst:
    dst.write(rad_class, 1)

with rasterio.open(tmp_rad) as src_r:
    rad_cropped, rad_transform_c = rio_mask(src_r, china_geom, crop=True, nodata=255)
    rad_data = rad_cropped[0]
    rad_crs = src_r.crs

os.remove(tmp_rad)

# ============================================================
# 5. 土壤酸碱度 (已处理，直接加载)
# ============================================================
print('\n[5/5] 土壤酸碱度适宜性 (已处理)')
ph_file = os.path.join(DST, 'soil_ph_suitability.tif')
with rasterio.open(ph_file) as src:
    ph_data = src.read(1)
    ph_transform_c = src.transform
    ph_crs = src.crs
    print(f'  pH data: {ph_data.shape}')

# ============================================================
# 统一分辨率：全部重投影到参考网格
# ============================================================
print('\n统一分辨率/投影 ...')

def reproject_to_grid(src_data, src_transform, src_crs_str,
                      dst_bounds, dst_width, dst_height, dst_crs_str='EPSG:4326'):
    """将任意分辨率的栅格重投影到统一网格"""
    # 创建源数据临时文件
    profile = {
        'driver': 'GTiff',
        'height': src_data.shape[0],
        'width': src_data.shape[1],
        'count': 1,
        'dtype': 'uint8',
        'nodata': 255,
        'crs': src_crs_str,
        'transform': src_transform,
    }
    tmp_src = os.path.join(DST, f'_tmp_src_{uuid.uuid4().hex[:8]}.tif')
    with rasterio.open(tmp_src, 'w', **profile) as dst:
        dst.write(src_data, 1)
    
    # 目标网格
    dst_transform = rasterio.transform.from_bounds(
        west=dst_bounds[0], south=dst_bounds[1],
        east=dst_bounds[2], north=dst_bounds[3],
        width=dst_width, height=dst_height
    )
    tmp_dst = os.path.join(DST, f'_tmp_dst_{uuid.uuid4().hex[:8]}.tif')
    
    with rasterio.open(tmp_src) as src_r:
        profile_dst = src_r.profile.copy()
        profile_dst.update(
            height=dst_height, width=dst_width,
            transform=dst_transform, crs=dst_crs_str
        )
        with rasterio.open(tmp_dst, 'w', **profile_dst) as dst_r:
            reproject(
                source=rasterio.band(src_r, 1),
                destination=rasterio.band(dst_r, 1),
                src_transform=src_r.transform,
                src_crs=src_r.crs,
                dst_transform=dst_transform,
                dst_crs=dst_crs_str,
                resampling=Resampling.nearest,
                dst_nodata=255,
            )
    
    with rasterio.open(tmp_dst) as final:
        result = final.read(1).copy()
        final_transform = final.transform
    
    os.remove(tmp_src)
    os.remove(tmp_dst)
    return result, final_transform

factor_data = {}
factor_transforms = {}

factors = [
    ('precip', precip_data, precip_transform, 'EPSG:4326'),
    ('temp', temp_data, temp_transform_c, str(temp_crs)),
    ('accum', accum_data, accum_transform_c, str(accum_crs)),
    ('rad', rad_data, rad_transform_c, str(rad_crs)),
    ('ph', ph_data, ph_transform_c, str(ph_crs)),
]

for name, data, trans, crs in factors:
    print(f'  处理 {name}: {data.shape} -> {ref_width}x{ref_height}')
    resampled, transform = reproject_to_grid(data, trans, crs, REF_BOUNDS, ref_width, ref_height)
    factor_data[name] = resampled
    factor_transforms[name] = transform
    v, c = np.unique(resampled, return_counts=True)
    print(f'    结果: {dict(zip(v.tolist(), [f"{x}px" for x in c.tolist()]))}')

# ============================================================
# 渲染 PNG（带中国边界 alpha mask）
# ============================================================
print('\n渲染 PNG ...')

def render_png(data, transform, bounds, config, out_path, downsample=DS):
    """将分类栅格渲染为带 alpha 的 PNG"""
    h, w = data.shape
    # 降采样
    if downsample > 1:
        h2, w2 = h // downsample, w // downsample
        from PIL import Image as Pim
        img = Pim.fromarray(data, mode='L')
        img = img.resize((w2, h2), resample=Pim.NEAREST)
        data_ds = np.array(img)
    else:
        data_ds = data
        h2, w2 = h, w
    
    colors = {}
    for level in config['levels']:
        colors[level['value']] = np.array([int(level['color'][1:3],16),
                                            int(level['color'][3:5],16),
                                            int(level['color'][5:7],16)], dtype=np.uint8)
    
    rgb = np.zeros((h2, w2, 3), dtype=np.uint8)
    alpha = np.zeros((h2, w2), dtype=np.uint8)
    
    for val, color in colors.items():
        mask_val = data_ds == val
        rgb[mask_val] = color
        alpha[mask_val] = 255
    
    # nodata(255) -> transparent
    nodata_mask = data_ds == 255
    rgb[nodata_mask] = [0xDD, 0xD5, 0xC0]  # 背景米色
    alpha[nodata_mask] = 0
    
    # 边缘羽化
    alpha_f = nd.uniform_filter(alpha.astype(np.float32), size=3)
    alpha = np.clip(alpha_f, 0, 255).astype(np.uint8)
    
    rgba = np.dstack([rgb, alpha])
    Pim.fromarray(rgba, mode='RGBA').save(out_path, optimize=True)
    print(f'  Saved: {out_path} ({w2}x{h2})')
    return (w2, h2)

factor_bounds_info = {}
for name in factor_data:
    config = FACTOR_CONFIG[name]
    png_path = os.path.join(DST, f'{name}_suitability.png')
    img_size = render_png(factor_data[name], factor_transforms[name], REF_BOUNDS, config, png_path)
    
    bounds_info = {
        'south': REF_BOUNDS[1], 'west': REF_BOUNDS[0],
        'north': REF_BOUNDS[3], 'east': REF_BOUNDS[2],
        'southWest': [REF_BOUNDS[1], REF_BOUNDS[0]],
        'northEast': [REF_BOUNDS[3], REF_BOUNDS[2]],
        'center': [(REF_BOUNDS[1]+REF_BOUNDS[3])/2, (REF_BOUNDS[0]+REF_BOUNDS[2])/2],
        'imageSize': list(img_size),
        'crs': 'EPSG:4326',
        'factor': name,
        'factorName': config['name'],
        'levels': config['levels'],
    }
    factor_bounds_info[name] = bounds_info
    
    with open(os.path.join(DST, f'{name}_bounds.json'), 'w', encoding='utf-8') as f:
        json.dump(bounds_info, f, ensure_ascii=False, indent=2)

# ============================================================
# 综合分析：5因子叠加，计算综合适宜性
# ============================================================
print('\n生成综合适宜性分析 ...')
# 每个因子的值映射为适宜性得分
# 0=最适宜(3分), 1=较适宜(2分), 2=限制适宜(1分), 3=不适宜(0分)
# 但各因子编码不同，需要统一映射

# 统一得分：3=最适宜(3分), 2=较适宜(2分), 1=限制适宜(1分), 0=不适宜(0分)
# 各因子编码 -> 得分映射
score_maps = {
    'precip': {0: 0, 1: 1, 2: 2, 3: 3},  # 已经是0-3, 直接映射
    'temp':   {0: 0, 1: 1, 2: 2, 3: 3},  # 气温分级
    'accum':  {0: 0, 1: 1, 2: 2, 3: 3},  # 积温分级
    'rad':    {0: 0, 1: 3, 2: 2, 3: 1},  # 光照: 1=最适宜->3分, 2=较适宜->2分, 3=限制->1分
    'ph':     {0: 0, 1: 1, 2: 2, 3: 3},  # pH分级
}

def get_score(data, score_map):
    """将分类数据转为得分栅格"""
    score = np.zeros(data.shape, dtype=np.float32)
    nodata_mask = data == 255
    for val, sc in score_map.items():
        score[data == val] = sc
    score[nodata_mask] = np.nan
    return score

scores = {}
for name in factor_data:
    scores[name] = get_score(factor_data[name], score_maps[name])

# 加权平均（等权重 0.2 每个）
weighted_sum = np.zeros_like(scores['precip'])
weight_count = np.zeros_like(scores['precip'])
for name in scores:
    valid = ~np.isnan(scores[name])
    weighted_sum[valid] += scores[name][valid]
    weight_count[valid] += 1

with np.errstate(divide='ignore', invalid='ignore'):
    composite = np.where(weight_count > 0, weighted_sum / np.maximum(weight_count, 0), np.nan)

# 综合分级: 0-1=限制适宜, 1-2=较适宜, 2-2.5=次适宜, 2.5-3=最适宜
# 四档: 不适宜(0-1), 限制适宜(1-1.8), 较适宜(1.8-2.5), 最适宜(2.5-3)
composite_class = np.full(composite.shape, 255, dtype=np.uint8)
composite_valid = ~np.isnan(composite)
composite_class[composite_valid & (composite < 1.0)] = 0
composite_class[composite_valid & (composite >= 1.0) & (composite < 1.8)] = 1
composite_class[composite_valid & (composite >= 1.8) & (composite < 2.5)] = 2
composite_class[composite_valid & (composite >= 2.5)] = 3

# 统计
v, c = np.unique(composite_class, return_counts=True)
total = composite_class.size
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  综合 {lb}({val}): {cnt} px ({100*cnt/total:.1f}%)')

# 渲染综合图
composite_config = {
    'name': '茶树生态适宜性综合评价',
    'levels': [
        {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
        {'value': 1, 'label': '限制适宜', 'color': '#C3C19A'},
        {'value': 2, 'label': '较适宜',   'color': '#93B55A'},
        {'value': 3, 'label': '最适宜',   'color': '#516D33'},
    ]
}

composite_png = os.path.join(DST, 'composite_suitability.png')
img_size = render_png(composite_class, None, REF_BOUNDS, composite_config, composite_png)

# 保存综合图 bounds
composite_bounds = {
    'south': REF_BOUNDS[1], 'west': REF_BOUNDS[0],
    'north': REF_BOUNDS[3], 'east': REF_BOUNDS[2],
    'southWest': [REF_BOUNDS[1], REF_BOUNDS[0]],
    'northEast': [REF_BOUNDS[3], REF_BOUNDS[2]],
    'center': [(REF_BOUNDS[1]+REF_BOUNDS[3])/2, (REF_BOUNDS[0]+REF_BOUNDS[2])/2],
    'imageSize': list(img_size),
    'crs': 'EPSG:4326',
    'factor': 'composite',
    'factorName': composite_config['name'],
    'levels': composite_config['levels'],
}
with open(os.path.join(DST, 'composite_bounds.json'), 'w', encoding='utf-8') as f:
    json.dump(composite_bounds, f, ensure_ascii=False, indent=2)

# ============================================================
# 生成主配置文件
# ============================================================
print('\n生成配置文件 ...')

# 因子配置
factors_list = []
for name in FACTOR_CONFIG:
    cfg = FACTOR_CONFIG[name]
    factors_list.append({
        'id': name,
        'name': cfg['name'],
        'png': f'{name}_suitability.png',
        'bounds': f'{name}_bounds.json',
        'levels': cfg['levels'],
    })

main_config = {
    'title': '中国茶树栽培生态适宜性分析',
    'subtitle': '基于降水、气温、积温、光照、土壤酸碱度五因子叠加评价',
    'factors': factors_list,
    'composite': {
        'name': composite_config['name'],
        'png': 'composite_suitability.png',
        'bounds': 'composite_bounds.json',
        'levels': composite_config['levels'],
    },
    'method': {
        'description': '5因子等权重叠加评价',
        'weights': {'precip': 0.2, 'temp': 0.2, 'accum': 0.2, 'rad': 0.2, 'ph': 0.2},
        'scoreRange': '0-3 (0=不适宜, 3=最适宜)',
    },
    'projection': 'EPSG:4326',
    'bounds': {
        'west': REF_BOUNDS[0], 'south': REF_BOUNDS[1],
        'east': REF_BOUNDS[2], 'north': REF_BOUNDS[3],
    }
}

with open(os.path.join(DST, 'config.json'), 'w', encoding='utf-8') as f:
    json.dump(main_config, f, ensure_ascii=False, indent=2)
print('  Saved config.json')

# ============================================================
# 复制省界底图
# ============================================================
print('\n复制省界底图 ...')
shutil.copy(prov_path, os.path.join(DST, 'china_provinces.geojson'))

# ============================================================
# 最终文件列表
# ============================================================
print('\n' + '='*60)
print('data/2 目录最终内容:')
print('='*60)
for f in sorted(os.listdir(DST)):
    fpath = os.path.join(DST, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        if size > 1024*1024:
            print(f'  {f:50s} {size/1024/1024:.1f} MB')
        elif size > 1024:
            print(f'  {f:50s} {size/1024:.0f} KB')
        else:
            print(f'  {f:50s} {size} B')
print('='*60)
print('DONE!')
