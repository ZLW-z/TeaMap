# -*- coding: utf-8 -*-
"""
第二章数据处理：土壤酸碱度适宜性重分类
- 读取原始 pH 栅格，按茶叶种植适宜性重分类
- 渲染为带中国边界 alpha mask 的 PNG（供 Leaflet imageOverlay 使用）
- 输出 bounds.json + 分类配置 JSON
- 同时复制原始栅格数据到 data/2
"""
import os, json, shutil
import numpy as np
import rasterio
from rasterio.mask import mask
from PIL import Image
from shapely.geometry import Point, shape
import geopandas as gpd
import scipy.ndimage as nd

SRC = r'D:\Desktop\星湖杯\茶叶\ppho2'
DST = r'D:\Desktop\teamap\data\2'

# ========= 1. 复制原始数据 =========
print('[1/4] 复制原始栅格数据 ...')
shutil.copy(os.path.join(SRC, 'soil_ph.tif'), os.path.join(DST, 'soil_ph.tif'))
shutil.copy(os.path.join(SRC, 'soil_ph.tfw'), os.path.join(DST, 'soil_ph.tfw'))
shutil.copy(os.path.join(SRC, 'soil_ph.tif.aux.xml'), os.path.join(DST, 'soil_ph.tif.aux.xml'))
print('  soil_ph.tif copied')

# 复制原始 pH 分层栅格
ph_dir = os.path.join(SRC, 'soil_ph')
if os.path.isdir(ph_dir):
    for f in os.listdir(ph_dir):
        shutil.copy(os.path.join(ph_dir, f), os.path.join(DST, f))
    print('  soil_ph/*.tif copied (3 depth layers)')

# 复制省份边界 geojson
prov_src = os.path.join(SRC, 'china-provinces.geojson')
if os.path.exists(prov_src):
    shutil.copy(prov_src, os.path.join(DST, 'china-provinces.geojson'))
    print('  china-provinces.geojson copied')

# ========= 2. 重分类 + 渲染 PNG =========
print('\n[2/4] 重分类 + 渲染 PNG ...')

ph_file = os.path.join(DST, 'soil_ph.tif')
prov_file = os.path.join(DST, 'china-provinces.geojson')

# 读取省份边界用于裁剪
china = gpd.read_file(prov_file)

with rasterio.open(ph_file) as src:
    # 确保 CRS 对齐
    if china.crs != src.crs:
        china = china.to_crs(src.crs)

    # 用中国边界裁剪
    data, transform = mask(src, china.geometry, crop=True)
    ph = data[0].astype(np.float32)

    # 处理 nodata
    nodata = src.nodata
    if nodata is not None:
        ph = np.where(ph == nodata, np.nan, ph)

    # 原始 bounds（未裁剪前的完整栅格范围）
    left = src.bounds.left
    bottom = src.bounds.bottom
    right = src.bounds.right
    top = src.bounds.top
    crs = str(src.crs)

    # 裁剪后的 bounds（mask 后 transform 变了）
    # 实际上 mask crop 后 transform 已经更新，我们用裁剪后的
    crop_left = transform[2]
    crop_top = transform[5]
    crop_right = crop_left + transform[0] * ph.shape[1]
    crop_bottom = crop_top + transform[4] * ph.shape[0]

    print(f'  裁剪后范围: lon {crop_left:.4f}~{crop_right:.4f}, lat {crop_bottom:.4f}~{crop_top:.4f}')
    print(f'  栅格尺寸: {ph.shape[1]} x {ph.shape[0]}')

    # ========= 重分类 =========
    # 0=不适宜 (pH<4 或 pH>7.5)
    # 1=限制适宜 (pH 4~4.5 或 6.5~7.5)
    # 2=较适宜 (pH 5.5~6.5)
    # 3=最适宜 (pH 4.5~5.5)
    # 255=nodata
    suitability = np.full(ph.shape, 255, dtype=np.uint8)
    valid = ~np.isnan(ph)

    suitability[valid & ((ph < 4) | (ph > 7.5))] = 0
    suitability[valid & (((ph >= 4) & (ph < 4.5)) | ((ph > 6.5) & (ph <= 7.5)))] = 1
    suitability[valid & ((ph >= 5.5) & (ph <= 6.5))] = 2
    suitability[valid & ((ph >= 4.5) & (ph < 5.5))] = 3

    vals, counts = np.unique(suitability, return_counts=True)
    print('  重分类结果:')
    labels = {0: '不适宜', 1: '限制适宜', 2: '较适宜', 3: '最适宜', 255: 'nodata'}
    for v, c in zip(vals, counts):
        print(f'    {v} ({labels.get(v, "?")}): {c} px ({100*c/suitability.size:.1f}%)')

    # ========= 保存重分类栅格 =========
    suit_out = os.path.join(DST, 'soil_ph_suitability.tif')
    profile = src.profile.copy()
    profile.update({
        'height': ph.shape[0],
        'width': ph.shape[1],
        'transform': transform,
        'dtype': 'uint8',
        'nodata': 255,
        'count': 1
    })
    with rasterio.open(suit_out, 'w', **profile) as dst:
        dst.write(suitability, 1)
    print(f'  Saved: {suit_out}')

    # ========= 渲染 PNG =========
    # 配色方案（与原始脚本一致，但适配六色系）
    # 0=不适宜 -> #C3C19A (米灰)
    # 1=限制适宜 -> #D4B44C (浅金)
    # 2=较适宜 -> #5C7C3A (中橄榄绿)
    # 3=最适宜 -> #516D33 (深橄榄绿)
    SUIT_COLORS = {
        0: np.array([0xC3, 0xC1, 0x9A], dtype=np.uint8),  # 米灰
        1: np.array([0xD4, 0xB4, 0x4C], dtype=np.uint8),  # 浅金
        2: np.array([0x5C, 0x7C, 0x3A], dtype=np.uint8),  # 中橄榄绿
        3: np.array([0x51, 0x6D, 0x33], dtype=np.uint8),  # 深橄榄绿
    }

    h, w = ph.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    alpha = np.zeros((h, w), dtype=np.uint8)

    for val, color in SUIT_COLORS.items():
        mask_val = suitability == val
        rgb[mask_val] = color
        alpha[mask_val] = 255

    # 边缘羽化
    alpha_f = nd.uniform_filter(alpha.astype(np.float32), size=3)
    alpha = np.clip(alpha_f, 0, 255).astype(np.uint8)

    # 降采样（减小 PNG 体积）
    DS = 2
    if DS > 1:
        h2, w2 = h // DS, w // DS
        rgb_img = Image.fromarray(rgb, mode='RGB')
        alpha_img = Image.fromarray(alpha, mode='L')
        rgb_img = rgb_img.resize((w2, h2), resample=Image.LANCZOS)
        alpha_img = alpha_img.resize((w2, h2), resample=Image.LANCZOS)
        rgb = np.array(rgb_img)
        alpha = np.array(alpha_img)
        # 降采样后 bounds 不变，但 imageSize 变了
        out_w, out_h = w2, h2
    else:
        out_w, out_h = w, h

    rgba = np.dstack([rgb, alpha])
    png_out = os.path.join(DST, 'soil_suitability.png')
    Image.fromarray(rgba, mode='RGBA').save(png_out, optimize=True)
    print(f'  Saved PNG: {png_out} ({out_w}x{out_h})')

    # ========= bounds.json =========
    bounds = {
        'south': crop_bottom,
        'west': crop_left,
        'north': crop_top,
        'east': crop_right,
        'southWest': [crop_bottom, crop_left],
        'northEast': [crop_top, crop_right],
        'center': [(crop_top + crop_bottom) / 2, (crop_left + crop_right) / 2],
        'imageSize': [out_w, out_h],
        'crs': crs,
    }
    bounds_out = os.path.join(DST, 'soil_suitability_bounds.json')
    with open(bounds_out, 'w', encoding='utf-8') as f:
        json.dump(bounds, f, ensure_ascii=False, indent=2)
    print(f'  Saved bounds: {bounds_out}')

# ========= 3. 分类配置 JSON =========
print('\n[3/4] 生成分类配置 JSON ...')
config = {
    'title': '中国茶叶种植土壤酸碱度适宜性',
    'source': 'SoilGrids 250m pH数据 + 中国省界裁剪',
    'classification': [
        {'value': 0, 'label': '不适宜', 'pH_range': 'pH<4 或 pH>7.5', 'color': '#C3C19A'},
        {'value': 1, 'label': '限制适宜', 'pH_range': '4≤pH<4.5 或 6.5<pH≤7.5', 'color': '#D4B44C'},
        {'value': 2, 'label': '较适宜', 'pH_range': '5.5≤pH≤6.5', 'color': '#5C7C3A'},
        {'value': 3, 'label': '最适宜', 'pH_range': '4.5≤pH<5.5', 'color': '#516D33'},
    ],
    'nodata_value': 255,
    'files': {
        'raster': 'soil_ph_suitability.tif',
        'png': 'soil_suitability.png',
        'bounds': 'soil_suitability_bounds.json',
        'original_ph': 'soil_ph.tif',
    }
}
config_out = os.path.join(DST, 'soil_suitability_config.json')
with open(config_out, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f'  Saved: {config_out}')

# ========= 4. 复制适宜性脚本 =========
print('\n[4/4] 复制适宜性分析脚本 ...')
shutil.copy(os.path.join(SRC, 'ph_suitability.py'), os.path.join(DST, 'ph_suitability.py'))
print('  ph_suitability.py copied')

print('\n全部完成！data/2 目录内容：')
for f in sorted(os.listdir(DST)):
    fpath = os.path.join(DST, f)
    size = os.path.getsize(fpath)
    if size > 1024 * 1024:
        print(f'  {f:40s} {size/1024/1024:.1f} MB')
    else:
        print(f'  {f:40s} {size/1024:.0f} KB')
