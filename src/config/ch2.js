import { assetUrl } from '../utils/base.js'

// 第二章 · 五因子适宜性配置
const FACTORS = {
  precip: {
    id: 'precip',
    name: '降水',
    short: '降水',
    icon: '',
    png: assetUrl('data/2/precip_suitability.png'),
    boundsUrl: assetUrl('data/2/precip_bounds.json'),
    desc: '茶树喜湿润，年降水量 1200–1800 mm 为最适宜区',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#A8C5A0' },
      { value: 2, label: '较适宜', color: '#6BA368' },
      { value: 3, label: '最适宜', color: '#2F6B2F' },
    ],
  },
  temp: {
    id: 'temp',
    name: '气温',
    short: '气温',
    icon: '',
    png: assetUrl('data/2/temp_suitability.png'),
    boundsUrl: assetUrl('data/2/temp_bounds.json'),
    desc: '茶树喜温暖，中温区最宜生长，低温与高温区为次适宜',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '低温适宜', color: '#9AC4D6' },
      { value: 2, label: '中温适宜', color: '#5C9EAF' },
      { value: 3, label: '高温适宜', color: '#C8462E' },
    ],
  },
  accum: {
    id: 'accum',
    name: '积温',
    short: '积温',
    icon: '',
    png: assetUrl('data/2/accum_suitability.png'),
    boundsUrl: assetUrl('data/2/accum_bounds.json'),
    desc: '≥10℃ 年活动积温 4000℃·d 以上方可满足茶树生长需求',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#D4B44C' },
      { value: 2, label: '较适宜', color: '#93B55A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
  rad: {
    id: 'rad',
    name: '光照',
    short: '光照',
    icon: '',
    png: assetUrl('data/2/rad_suitability.png'),
    boundsUrl: assetUrl('data/2/rad_bounds.json'),
    desc: '茶树喜光耐阴，年太阳辐射总量适中为最适宜',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#C3C19A' },
      { value: 2, label: '较适宜', color: '#93B55A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
  ph: {
    id: 'ph',
    name: '酸碱度',
    short: 'pH',
    icon: '',
    png: assetUrl('data/2/ph_suitability.png'),
    boundsUrl: assetUrl('data/2/ph_bounds.json'),
    desc: '茶树喜酸性土壤，pH 4.5–5.5 为最适宜区',
    levels: [
      { value: 0, label: '不适宜', color: '#E8E2D0' },
      { value: 1, label: '限制适宜', color: '#D4B44C' },
      { value: 2, label: '较适宜', color: '#5C7C3A' },
      { value: 3, label: '最适宜', color: '#516D33' },
    ],
  },
}

const COMPOSITE = {
  id: 'composite',
  name: '综合',
  short: '综合',
  icon: '🍃',
  png: assetUrl('data/2/composite_suitability.png'),
  boundsUrl: assetUrl('data/2/composite_bounds.json'),
  desc: '五因子等权重叠加，综合评分 ≥2.5 为茶树生长最适宜区',
  levels: [
    { value: 0, label: '不适宜', color: '#E8E2D0' },
    { value: 1, label: '限制适宜', color: '#C3C19A' },
    { value: 2, label: '较适宜', color: '#93B55A' },
    { value: 3, label: '最适宜', color: '#516D33' },
  ],
}

const FACTOR_ORDER = ['precip', 'temp', 'accum', 'rad', 'ph']

const MAP_BOUNDS = [
  [-2521178, -15157622], // [southY, westX] Albers
  [16124181,  15157622], // [northY, eastX] Albers
]

const PROV_BG_URL = assetUrl('data/2/china-provinces-albers.geojson')

const PROV_STYLE = {
  color: '#A8A28D',
  weight: 0.6,
  fillColor: '#F0EBD9',
  fillOpacity: 0.5,
}

const WHEEL_COLORS = [
  '#2F6B2F', // precip - deep green-blue
  '#5C9EAF', // temp - medium teal
  '#D4B44C', // accum - gold
  '#C3C19A', // rad - beige
  '#516D33', // ph - deep olive
]

export {
  FACTORS,
  COMPOSITE,
  FACTOR_ORDER,
  MAP_BOUNDS,
  PROV_BG_URL,
  PROV_STYLE,
  WHEEL_COLORS,
}

export async function loadFactorBounds(factorId) {
  const cfg = factorId === 'composite'
    ? COMPOSITE
    : FACTORS[factorId]
  try {
    const res = await fetch(cfg.boundsUrl)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const b = await res.json()
    // Albers 米制坐标: [[southY, westX], [northY, eastX]]
    return [[b.south, b.west], [b.north, b.east]]
  } catch (e) {
    console.warn('[ch2] bounds load failed:', factorId, e)
    return MAP_BOUNDS
  }
}
