# -*- coding: utf-8 -*-
"""
第二章数据处理 v3：5大茶树生态适宜性因子
- 统一分辨率/投影/边界
- 生成5张单因子PNG + 1张综合分析PNG
"""
import os, json, shutil, uuid
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from PIL import Image as Pim
import geopandas as gpd
from shapely.geometry import shape
import scipy.ndimage as nd

SRC_PREC = r'D:\Desktop\星湖杯\茶叶\prec'
SRC_TEMP = r'D:\Desktop\星湖杯\茶叶\temp'
DST      = r'D:\Desktop\teamap\data\2'

# 统一参数
DS = 8
REF_BOUNDS = (73.49, 3.82, 135.10, 53.57)
REF_CRS = 'EPSG:4326'
REF_W = 7392
REF_H = 5969

FACTOR_CONFIG = {
    'precip': {'name': '降水适宜性',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#A8C5A0'},
            {'value': 2, 'label': '较适宜',   'color': '#6BA368'},
            {'value': 3, 'label': '最适宜',   'color': '#2F6B2F'},
        ]},
    'temp': {'name': '气温适宜性',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '低温适宜', 'color': '#9AC4D6'},
            {'value': 2, 'label': '中温适宜', 'color': '#5C9EAF'},
            {'value': 3, 'label': '高温适宜', 'color': '#C8462E'},
        ]},
    'accum': {'name': '积温适宜性',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#D4B44C'},
            {'value': 2, 'label': '较适宜',   'color': '#93B55A'},
            {'value': 3, 'label': '最适宜',   'color': '#516D33'},
        ]},
    'rad': {'name': '光照适宜性',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '最适宜',   'color': '#2F6B2F'},
            {'value': 2, 'label': '较适宜',   'color': '#5C9EAF'},
            {'value': 3, 'label': '限制适宜', 'color': '#C3C19A'},
        ]},
    'ph': {'name': '土壤酸碱度适宜性',
        'levels': [
            {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
            {'value': 1, 'label': '限制适宜', 'color': '#D4B44C'},
            {'value': 2, 'label': '较适宜',   'color': '#5C7C3A'},
            {'value': 3, 'label': '最适宜',   'color': '#516D33'},
        ]},
}

os.makedirs(DST, exist_ok=True)

# 加载省份边界
print('加载省份边界...')
prov_path = os.path.join(DST, 'china-provinces.geojson')
if not os.path.exists(prov_path):
    shutil.copy(r'D:\Desktop\teamap\data\1\china_provinces_background.geojson', prov_path)
china = gpd.read_file(prov_path)
if china.crs is None:
    china = china.set_crs(REF_CRS)
china_geom = [shape(g) for g in china.geometry]

def save_geotiff(data, transform, crs, path):
    profile = {
        'driver': 'GTiff', 'height': data.shape[0], 'width': data.shape[1],
        'count': 1, 'dtype': 'uint8', 'nodata': 255,
        'crs': crs, 'transform': transform,
    }
    with rasterio.open(path, 'w', **profile) as dst:
        dst.write(data, 1)

def crop_to_china(src_path):
    with rasterio.open(src_path) as src:
        data = src.read(1)
        crs = src.crs
        cropped, transform = rio_mask(src, china_geom, crop=True, nodata=255)
        return cropped[0], transform, crs

def reproject_to_grid(src_path, dst_bounds, dst_w, dst_h):
    with rasterio.open(src_path) as src:
        dst_transform = from_bounds(
            west=dst_bounds[0], south=dst_bounds[1],
            east=dst_bounds[2], north=dst_bounds[3],
            width=dst_w, height=dst_h
        )
        dst_path = src_path + '.reproj.tif'
        profile = src.profile.copy()
        profile.update(
            driver='GTiff', height=dst_h, width=dst_w,
            transform=dst_transform, crs=REF_CRS, nodata=255,
        )
        with rasterio.open(dst_path, 'w', **profile) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform, src_crs=src.crs,
                dst_transform=dst_transform, dst_crs=REF_CRS,
                resampling=Resampling.nearest, dst_nodata=255,
            )
        with rasterio.open(dst_path) as final:
            result = final.read(1).copy()
        os.remove(dst_path)
        return result

def render_png(data, config, out_path, downsample=DS):
    h, w = data.shape
    if downsample > 1:
        h2, w2 = h // downsample, w // downsample
        img = Pim.fromarray(data, mode='L')
        img = img.resize((w2, h2), resample=Pim.NEAREST)
        data_ds = np.array(img)
    else:
        data_ds = data.copy()
        h2, w2 = h, w

    colors = {}
    for lv in config['levels']:
        colors[lv['value']] = np.array(
            [int(lv['color'][1:3],16), int(lv['color'][3:5],16), int(lv['color'][5:7],16)],
            dtype=np.uint8)

    rgb = np.zeros((h2, w2, 3), dtype=np.uint8)
    alpha = np.zeros((h2, w2), dtype=np.uint8)

    for val, color in colors.items():
        m = data_ds == val
        rgb[m] = color
        alpha[m] = 255

    nm = data_ds == 255
    rgb[nm] = [0xDD, 0xD5, 0xC0]
    alpha[nm] = 0

    alpha_f = nd.uniform_filter(alpha.astype(np.float32), size=3)
    alpha = np.clip(alpha_f, 0, 255).astype(np.uint8)

    rgba = np.dstack([rgb, alpha])
    Pim.fromarray(rgba, mode='RGBA').save(out_path, optimize=True)
    return (w2, h2)

# ============================================================
# 1. 降水：从原始年数据重分类
# ============================================================
print('\n[1/5] 降水适宜性 ...')
precip_sum = None
precip_count = 0
for yr in ['_2020','_2021','_2022','_2023','_2024']:
    path = os.path.join(SRC_PREC, yr, 'w001001.adf')
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        if precip_sum is None:
            precip_sum = np.zeros(arr.shape, dtype=np.float64)
            valid_mask = np.zeros(arr.shape, dtype=bool)
        v = arr != src.nodata
        precip_sum[v] += arr[v]
        valid_mask |= v
        precip_count += v.astype(np.int16)

precip_avg = np.where(precip_count > 0, precip_sum / np.maximum(precip_count, 1), np.nan)
print(f'  年均降水: {np.nanmin(precip_avg):.1f}~{np.nanmax(precip_avg):.1f}mm')

precip_class = np.zeros(precip_avg.shape, dtype=np.uint8)
vm = np.isfinite(precip_avg)
# 最适宜: 1200-2500
precip_class[vm & (precip_avg>=1200) & (precip_avg<=2500)] = 3
# 较适宜: 800-1200 或 2500-3500
precip_class[vm & (precip_avg>=800) & (precip_avg<1200)] = 2
precip_class[vm & (precip_avg>2500) & (precip_avg<=3500)] = 2
# 限制适宜: 500-800 或 3500-4500
precip_class[vm & (precip_avg>=500) & (precip_avg<800)] = 1
precip_class[vm & (precip_avg>3500) & (precip_avg<=4500)] = 1
# nodata
precip_class[~vm | (precip_avg<400) | (precip_avg>5000)] = 255

# 保存为 GTiff
tmp_precip = os.path.join(DST, 'tmp_precip_raw.tif')
with rasterio.open(os.path.join(SRC_PREC, '_2020', 'w001001.adf')) as src_ref:
    profile = src_ref.profile.copy()
    profile.update(driver='GTiff', count=1, dtype='uint8', nodata=255)
    with rasterio.open(tmp_precip, 'w', **profile) as dst:
        dst.write(precip_class, 1)

# 裁剪 + 重投影
tmp_precip_crop = os.path.join(DST, 'tmp_precip_crop.tif')
with rasterio.open(tmp_precip) as src:
    cropped, transform = rio_mask(src, china_geom, crop=True, nodata=255)
    save_geotiff(cropped[0], transform, src.crs, tmp_precip_crop)
    orig_crs = src.crs

precip_final = reproject_to_grid(tmp_precip_crop, REF_BOUNDS, REF_W, REF_H)

for f in [tmp_precip, tmp_precip_crop]:
    if os.path.exists(f): os.remove(f)

v, c = np.unique(precip_final, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  降水 {lb}: {cnt}px ({100*cnt/precip_final.size:.1f}%)')

# ============================================================
# 2. 气温
# ============================================================
print('\n[2/5] 气温适宜性 ...')
temp_file = os.path.join(DST, '多年均温.tif')
tmp_temp = os.path.join(DST, 'tmp_temp_crop.tif')

with rasterio.open(temp_file) as src:
    temp_arr = src.read(1).astype(np.uint8)
    # 0->255(nodata), 保持1/2/3
    temp_class = np.where(temp_arr == 0, 255, temp_arr)
    save_geotiff(temp_class, src.transform, src.crs, tmp_temp)

temp_final = reproject_to_grid(tmp_temp, REF_BOUNDS, REF_W, REF_H)
if os.path.exists(tmp_temp): os.remove(tmp_temp)

v, c = np.unique(temp_final, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'?',1:'低温适宜',2:'中温适宜',3:'高温适宜',255:'nodata'}.get(val,'?')
    print(f'  气温 {lb}: {cnt}px ({100*cnt/temp_final.size:.1f}%)')

# ============================================================
# 3. 积温
# ============================================================
print('\n[3/5] 积温适宜性 ...')
accum_file = os.path.join(DST, '多年平均活动积温.tif')
tmp_accum = os.path.join(DST, 'tmp_accum_crop.tif')

with rasterio.open(accum_file) as src:
    accum_arr = src.read(1).astype(np.int16)
    accum_class = np.where(accum_arr == -9999, 255, accum_arr).astype(np.uint8)
    save_geotiff(accum_class, src.transform, src.crs, tmp_accum)

accum_final = reproject_to_grid(tmp_accum, REF_BOUNDS, REF_W, REF_H)
if os.path.exists(tmp_accum): os.remove(tmp_accum)

v, c = np.unique(accum_final, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  积温 {lb}: {cnt}px ({100*cnt/accum_final.size:.1f}%)')

# ============================================================
# 4. 光照
# ============================================================
print('\n[4/5] 光照适宜性 ...')
rad_file = os.path.join(DST, 'radiation_suitability_reclass.tif')
tmp_rad = os.path.join(DST, 'tmp_rad_crop.tif')

with rasterio.open(rad_file) as src:
    rad_arr = src.read(1).astype(np.int16)
    rad_class = np.where(rad_arr == -9999, 255, rad_arr).astype(np.uint8)
    save_geotiff(rad_class, src.transform, src.crs, tmp_rad)

rad_final = reproject_to_grid(tmp_rad, REF_BOUNDS, REF_W, REF_H)
if os.path.exists(tmp_rad): os.remove(tmp_rad)

v, c = np.unique(rad_final, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'最适宜',2:'较适宜',3:'限制适宜',255:'nodata'}.get(val,'?')
    print(f'  光照 {lb}: {cnt}px ({100*cnt/rad_final.size:.1f}%)')

# ============================================================
# 5. 土壤pH
# ============================================================
print('\n[5/5] 土壤酸碱度适宜性 ...')
ph_file = os.path.join(DST, 'soil_ph_suitability.tif')
tmp_ph = os.path.join(DST, 'tmp_ph_crop.tif')

with rasterio.open(ph_file) as src:
    ph_arr = src.read(1)
    save_geotiff(ph_arr, src.transform, src.crs, tmp_ph)

ph_final = reproject_to_grid(tmp_ph, REF_BOUNDS, REF_W, REF_H)
if os.path.exists(tmp_ph): os.remove(tmp_ph)

v, c = np.unique(ph_final, return_counts=True)
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  pH {lb}: {cnt}px ({100*cnt/ph_final.size:.1f}%)')

# ============================================================
# 渲染单因子PNG
# ============================================================
print('\n渲染PNG ...')
factor_data = {
    'precip': precip_final, 'temp': temp_final,
    'accum': accum_final, 'rad': rad_final, 'ph': ph_final,
}

for name, data in factor_data.items():
    cfg = FACTOR_CONFIG[name]
    img_size = render_png(data, cfg, os.path.join(DST, f'{name}_suitability.png'))
    bounds_info = {
        'south': REF_BOUNDS[1], 'west': REF_BOUNDS[0],
        'north': REF_BOUNDS[3], 'east': REF_BOUNDS[2],
        'southWest': [REF_BOUNDS[1], REF_BOUNDS[0]],
        'northEast': [REF_BOUNDS[3], REF_BOUNDS[2]],
        'center': [(REF_BOUNDS[1]+REF_BOUNDS[3])/2, (REF_BOUNDS[0]+REF_BOUNDS[2])/2],
        'imageSize': list(img_size), 'crs': REF_CRS,
        'factor': name, 'factorName': cfg['name'], 'levels': cfg['levels'],
    }
    with open(os.path.join(DST, f'{name}_bounds.json'), 'w', encoding='utf-8') as f:
        json.dump(bounds_info, f, ensure_ascii=False, indent=2)

# ============================================================
# 综合分析
# ============================================================
print('\n生成综合分析 ...')
score_maps = {
    'precip': {0:0,1:1,2:2,3:3},
    'temp':   {0:0,1:1,2:2,3:3},
    'accum':  {0:0,1:1,2:2,3:3},
    'rad':    {0:0,1:3,2:2,3:1},  # 光照编码不同
    'ph':     {0:0,1:1,2:2,3:3},
}

def to_score(data, smap):
    sc = np.zeros(data.shape, dtype=np.float32)
    nm = data == 255
    for v, s in smap.items():
        sc[data == v] = s
    sc[nm] = np.nan
    return sc

scores = {n: to_score(d, score_maps[n]) for n, d in factor_data.items()}

ws = np.zeros_like(scores['precip'])
wc = np.zeros_like(scores['precip'])
for n in scores:
    valid = ~np.isnan(scores[n])
    ws[valid] += scores[n][valid]
    wc[valid] += 1

with np.errstate(divide='ignore', invalid='ignore'):
    comp = np.where(wc > 0, ws / np.maximum(wc, 0), np.nan)

comp_cls = np.full(comp.shape, 255, dtype=np.uint8)
cv = ~np.isnan(comp)
comp_cls[cv & (comp < 1.0)] = 0
comp_cls[cv & (comp >= 1.0) & (comp < 1.8)] = 1
comp_cls[cv & (comp >= 1.8) & (comp < 2.5)] = 2
comp_cls[cv & (comp >= 2.5)] = 3

v, c = np.unique(comp_cls, return_counts=True)
total = comp_cls.size
for val, cnt in zip(v, c):
    lb = {0:'不适宜',1:'限制适宜',2:'较适宜',3:'最适宜',255:'nodata'}.get(val,'?')
    print(f'  综合 {lb}: {cnt}px ({100*cnt/total:.1f}%)')

comp_cfg = {
    'name': '茶树生态适宜性综合评价',
    'levels': [
        {'value': 0, 'label': '不适宜',   'color': '#E8E2D0'},
        {'value': 1, 'label': '限制适宜', 'color': '#C3C19A'},
        {'value': 2, 'label': '较适宜',   'color': '#93B55A'},
        {'value': 3, 'label': '最适宜',   'color': '#516D33'},
    ]
}
img_size = render_png(comp_cls, comp_cfg, os.path.join(DST, 'composite_suitability.png'))
comp_bounds = {
    'south': REF_BOUNDS[1], 'west': REF_BOUNDS[0],
    'north': REF_BOUNDS[3], 'east': REF_BOUNDS[2],
    'southWest': [REF_BOUNDS[1], REF_BOUNDS[0]],
    'northEast': [REF_BOUNDS[3], REF_BOUNDS[2]],
    'center': [(REF_BOUNDS[1]+REF_BOUNDS[3])/2, (REF_BOUNDS[0]+REF_BOUNDS[2])/2],
    'imageSize': list(img_size), 'crs': REF_CRS,
    'factor': 'composite', 'factorName': comp_cfg['name'], 'levels': comp_cfg['levels'],
}
with open(os.path.join(DST, 'composite_bounds.json'), 'w', encoding='utf-8') as f:
    json.dump(comp_bounds, f, ensure_ascii=False, indent=2)

# ============================================================
# 主配置
# ============================================================
print('\n生成主配置 ...')
factors_list = []
for name in FACTOR_CONFIG:
    cfg = FACTOR_CONFIG[name]
    factors_list.append({
        'id': name, 'name': cfg['name'],
        'png': f'{name}_suitability.png',
        'bounds': f'{name}_bounds.json',
        'levels': cfg['levels'],
    })

main_cfg = {
    'title': '中国茶树栽培生态适宜性分析',
    'subtitle': '基于降水·气温·积温·光照·土壤酸碱度五因子叠加评价',
    'factors': factors_list,
    'composite': {
        'name': comp_cfg['name'],
        'png': 'composite_suitability.png',
        'bounds': 'composite_bounds.json',
        'levels': comp_cfg['levels'],
    },
    'method': {
        'description': '5因子等权重叠加评价',
        'weights': {'precip':0.2,'temp':0.2,'accum':0.2,'rad':0.2,'ph':0.2},
        'scoreRange': '0-3',
        'breakpoints': [1.0, 1.8, 2.5],
    },
    'bounds': {'west': REF_BOUNDS[0], 'south': REF_BOUNDS[1],
               'east': REF_BOUNDS[2], 'north': REF_BOUNDS[3]},
}
with open(os.path.join(DST, 'config.json'), 'w', encoding='utf-8') as f:
    json.dump(main_cfg, f, ensure_ascii=False, indent=2)

print('\n' + '='*60)
print('data/2 最终文件:')
print('='*60)
for f in sorted(os.listdir(DST)):
    fp = os.path.join(DST, f)
    if os.path.isfile(fp):
        sz = os.path.getsize(fp)
        tag = 'MB' if sz > 1024*1024 else 'KB'
        val = sz/1024/1024 if sz > 1024*1024 else sz/1024
        print(f'  {f:50s} {val:.1f} {tag}')
print('DONE!')
