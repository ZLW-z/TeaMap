// 第一章 · 图层路径与地理范围
export const DEM_IMG = '/data/1/dem_relief.png'
export const DEM_BOUNDS_URL = '/data/1/dem_bounds.json'

// 省份底图 + 市级茶区 + 古茶树
export const PROV_BG_URL = '/data/1/china_provinces_background.geojson'
export const TANG_AREAS_URL = '/data/1/tang_areas.geojson'
export const TEA_TREES_URL = '/data/1/tea_trees.geojson'

// 默认 DEM bounds（若 dem_bounds.json 加载失败则回退到此）
export const DEM_BOUNDS_FALLBACK = [
  [3.8291666666666515, 73.49583333333331],
  [53.562499999999986, 135.08749999999998]
]

export async function loadDemBounds() {
  try {
    const res = await fetch(DEM_BOUNDS_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const b = await res.json()
    return [[b.south, b.west], [b.north, b.east]]
  } catch (e) {
    console.warn('[ch1] dem_bounds.json 加载失败', e)
    return DEM_BOUNDS_FALLBACK
  }
}

export const MAP_INIT = {
  center: [30, 108],
  zoom: 4,
  minZoom: 3,
  maxZoom: 7,
  fitBounds: [[18, 95], [41, 125]]
}

// 古茶树类型配色：强对比三色 —— 暖红 / 中金 / 冷深绿
export const TREE_TYPE_STYLE = {
  1: { color: '#C8462E', fill: '#C8462E', label: '野生型' },
  2: { color: '#B28F4C', fill: '#B28F4C', label: '过渡/其他' },
  3: { color: '#2F5D3A', fill: '#2F5D3A', label: '栽培型' }
}

// 省份底图样式：极浅米灰，不抢视觉
export const PROV_STYLE = {
  color: '#A8A28D', weight: 0.8, fillColor: '#E8E2D0', fillOpacity: 0.35
}

// 市级茶区样式：参考早期人工茶区.png 中黄色产茶区
export const TANG_STYLE = {
  color: '#8E6F38', weight: 1.5, fillColor: '#D4B44C', fillOpacity: 0.55
}
