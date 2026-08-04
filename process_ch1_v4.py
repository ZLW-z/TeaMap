# -*- coding: utf-8 -*-
import os; os.environ['SHAPE_RESTORE_SHX'] = 'YES'
import json, numpy as np, geopandas as gpd
from shapely.geometry import Point, shape
from collections import Counter
import rasterio
from matplotlib.colors import LightSource, Normalize, LinearSegmentedColormap

TEA_COLORS = [
    (0.00,'#3D5428'),(0.20,'#46612C'),(0.38,'#516D33'),(0.45,'#C3C19A'),
    (0.52,'#F7F4EB'),(0.62,'#EFE9DA'),(0.72,'#C3C19A'),(0.82,'#B28F4C'),
    (0.92,'#8E6F38'),(1.00,'#F7F4EB'),
]
cmap_tea = LinearSegmentedColormap.from_list('tea', list(zip([c[0] for c in TEA_COLORS],[c[1] for c in TEA_COLORS])))

B = r'd:\Desktop\teamap\data\1'
BG = np.array([0xDD/255,0xD5/255,0xC0/255],dtype=np.float32)

# 1) DEM
print('[1/3] DEM ...')
with rasterio.open(B+r'\高程.tif') as dem:
    l,b,r,t = dem.bounds.left,dem.bounds.bottom,dem.bounds.right,dem.bounds.top
    oH,oW = dem.height//6, dem.width//6
    arr = dem.read(1,out_shape=(oH,oW),resampling=rasterio.enums.Resampling.bilinear)
    vm = arr > -1000
    ma = np.ma.masked_array(arr.astype(np.float32), mask=~vm)
    elev = np.ma.masked_array(ma, fill_value=np.nan)
    ls = LightSource(azdeg=315, altdeg=40)
    v = elev[~elev.mask].compressed()
    vmin,vmax = np.percentile(v,[1,99]) if v.size else (0,3000)
    norm = Normalize(vmin=vmin, vmax=vmax)
    rgb_s = ls.shade(elev.filled(np.nan),cmap=cmap_tea,norm=norm,blend_mode='soft',vert_exag=15)
    rgb = rgb_s[:,:,0:3].copy()
    mask3d = np.stack([elev.mask]*3, axis=-1)
    for c in range(3):
        ch = rgb[:,:,c]
        ch = np.where(np.isnan(ch), 0, ch)
        rgb[:,:,c] = np.where(mask3d[:,:,c], BG[c], ch)
    from PIL import Image
    Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8),mode='RGB').save(B+r'\dem_relief.png',optimize=True)
    json.dump({'south':b,'west':l,'north':t,'east':r,'southWest':[b,l],'northEast':[t,r],
               'center':[(t+b)/2,(l+r)/2],'imageSize':[oW,oH],'crs':str(dem.crs)},
              open(B+r'\dem_bounds.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(f'  DEM: {oW}x{oH}, nodata={np.sum(~vm)}')

# 2) Tea areas -> city polygons
print('[2/3] Tea areas -> cities ...')
city_feats = []
for ft in json.load(open(B+r'\china_tea_provinces_cities.json','r',encoding='utf-8'))['features']:
    city_feats.append({'adcode':ft['properties']['adcode'],'name':ft['properties']['name'],
                       'geom':shape(ft['geometry'])})

tang = gpd.read_file(B+r'\唐代产茶区.shp')
if tang.crs is None: tang = tang.to_crs(epsg=4326)

def nm(x):
    if not x: return None
    s=str(x).strip()
    if s=='——': return None
    if '/' in s: s=s.split('/')[0]
    if s.endswith('茶区') and len(s)>2: s=s[:-2]
    return {'山南':'山南茶区','淮南':'淮南茶区','浙西':'浙西茶区','浙东':'浙东茶区',
            '剑南':'剑南茶区','岭南':'岭南茶区','江西':'江西茶区','黔中':'黔中茶区'}.get(s,s or None)

tang['_a'] = tang['所属茶'].apply(nm)
matched = {}
for _,row in tang.iterrows():
    if row['_a'] is None or row.geometry is None: continue
    pt = Point(row.geometry.x, row.geometry.y)
    for cf in city_feats:
        if cf['geom'].contains(pt):
            ac=cf['adcode']
            if ac not in matched: matched[ac]={'name':cf['name'],'adcode':ac,'areas':set(),'count':0,'geom':cf['geom']}
            matched[ac]['areas'].add(row['_a'])
            matched[ac]['count']+=1
            break

tfeats = []
for ac,info in matched.items():
    tfeats.append({'type':'Feature','geometry':json.loads(json.dumps(info['geom'].__geo_interface__)),
        'properties':{'adcode':ac,'name':info['name'],'areas':sorted(list(info['areas'])),
        'areaLabel':'、'.join(sorted(list(info['areas']))),'pointCount':info['count'],'layer':'tea_city'}})
json.dump({'type':'FeatureCollection','features':tfeats},open(B+r'\tang_areas.geojson','w',encoding='utf-8'),ensure_ascii=False)
print(f'  Tea cities: {len(tfeats)}')

# Province bg
pd = json.load(open(B+r'\china_provinces_full.json','r',encoding='utf-8'))
pf = [f for f in pd['features'] if f['properties'].get('level')=='province' and f['properties'].get('adcode',0)<900000]
json.dump({'type':'FeatureCollection','features':pf},open(B+r'\china_provinces_background.geojson','w',encoding='utf-8'),ensure_ascii=False)
print(f'  Provinces: {len(pf)}')

# 3) Tea trees
print('[3/3] Tea trees ...')
trees = gpd.read_file(B+r'\Export_Output.shp')
if trees.crs is None: trees = trees.to_crs(epsg=4326)

REP=[('勐库','云南',23.45,99.85),('大雪山','云南',24.02,100.06),('冰岛','云南',23.62,99.91),
     ('昔归','云南',23.73,100.45),('那焦','云南',23.42,99.78),('坝糯','云南',23.38,99.86),
     ('巴达','云南',21.96,100.11),('南糯山','云南',21.92,100.61),('布朗山','云南',21.78,100.38),
     ('帕沙','云南',22.05,100.78),('班章','云南',21.84,100.62),('易武','云南',22.07,101.40),
     ('曼糯','云南',22.28,100.82),('景迈','云南',22.18,100.00),('邦崴','云南',22.56,99.93),
     ('千家寨','云南',23.94,101.06),('景谷','云南',23.45,100.70),('宁洱','云南',23.06,101.04),
     ('镇沅','云南',23.89,100.73),('无量山','云南',24.50,100.67),('哀牢山','云南',24.20,101.50),
     ('古永','云南',25.15,98.30),('芒洪','云南',23.42,99.72),('源头茶','云南',24.68,98.85),
     ('芹菜塘','云南',25.32,98.86),('标水崖','云南',24.38,98.78),('沿江村','云南',24.65,98.55),
     ('石佛','云南',24.98,98.76),('新房子','云南',22.56,100.53),('玉溪元江','云南',23.56,101.95),
     ('元江','云南',23.56,101.95),('曲靖师宗','云南',24.83,103.98),('师宗','云南',24.83,103.98),
     ('文山麻栗坡','云南',23.12,104.71),('麻栗坡','云南',23.12,104.71),('斯须乐','云南',22.20,101.12),
     ('大箐','云南',24.20,100.30),('肉桂','福建',27.76,118.03),('大红袍','福建',27.64,118.03),
     ('黄山','安徽',30.13,118.17),('雷波大茶树','四川',28.26,103.57),('大木茶','四川',27.90,103.80)]

PC={'云南':(24.5,102.5),'贵州':(26.6,106.7),'四川':(30.7,104.1),'重庆':(29.5,106.5),
    '湖北':(30.6,114.3),'湖南':(28.2,112.9),'广西':(22.8,108.4),'广东':(23.1,113.3),
    '福建':(26.1,119.3),'浙江':(30.3,120.2),'安徽':(31.8,117.3),'海南':(19.9,110.3),
    '台湾':(25.0,121.5),'陕西':(34.3,108.9),'河南':(34.6,113.6),'江西':(28.7,115.9),
    '江苏':(32.0,118.8),'山东':(36.7,117.0),'甘肃':(36.1,103.8),'西藏':(29.6,91.1)}

tm={'野生型':1,'其他':2,'栽培型':3}
tnm={'野生型':'野生型','其他':'过渡/其他','栽培型':'栽培型'}
cm={1:'#C8462E',2:'#B28F4C',3:'#2F5D3A'}

feats=[]
for i,row in trees.iterrows():
    g=row.geometry
    if g is None: continue
    lon,lat=float(g.x),float(g.y)
    name=str(row['茶树名']) if row['茶树名'] else f'古茶树#{i+1}'
    prov=str(row['省份']) if row['省份'] else ''
    kind=str(row['种类']) if row['种类'] else '其他'
    mk=False
    for kw,kwp,kl,kln in REP:
        if kw in name: lat,lon=kl,kln; mk=True; break
    if lon<70 or lon>136 or lat<14 or lat>46: continue
    pc=PC.get(prov)
    if pc:
        pl,plon=pc
        if abs(lat-pl)>10 or abs(lon-plon)>10:
            if mk:
                for kw,kwp2,*_ in REP:
                    if kw in name: prov=kwp2; break
            else: continue
    t=tm.get(kind,2)
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},
        'properties':{'name':name,'province':prov,'species':str(row['学名']) if row['学名'] else '',
        'kind':kind,'type':t,'typeName':tnm.get(kind,kind),'color':cm[t],'repaired':mk}})

cnt=Counter(f['properties']['typeName'] for f in feats)
print(f'  Types: {dict(cnt)}, Total: {len(feats)}')
json.dump({'type':'FeatureCollection','features':feats},open(B+r'\tea_trees.geojson','w',encoding='utf-8'),ensure_ascii=False)
print('All done!')
