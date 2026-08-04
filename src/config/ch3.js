// 第三章 · 十大名茶配置
import { assetUrl } from '../utils/base.js'
import teasData from '../../data/3/teas.json'

export const TEAS = teasData.map(t => ({
  ...t,
  image: assetUrl(t.image),
}))

// 茶类颜色映射
export const TEA_TYPE_COLORS = {
  '绿茶': '#5C7C3A',
  '乌龙茶（青茶）': '#B28F4C',
  '白茶（微发酵茶）': '#C3C19A',
  '黑茶（后发酵茶）': '#516D33',
  '黄茶': '#D4B44C',
  '红茶': '#92402E',
}

// 十大名茶点样式（醒目）
export const TOP10_STYLE = {
  radius: 9,
  fillColor: '#B28F4C',
  color: '#FFFFFF',
  weight: 2.5,
  opacity: 1,
  fillOpacity: 0.9,
}

// 其他名茶点样式（较小）
export const OTHER_STYLE = {
  radius: 6,
  fillColor: '#5C7C3A',
  color: '#FFFFFF',
  weight: 1.5,
  opacity: 1,
  fillOpacity: 0.8,
}

// 省份底图样式
export const PROV_BG_URL = assetUrl('data/2/china-provinces.geojson')

export const PROV_STYLE = {
  color: '#A8A28D',
  weight: 0.6,
  fillColor: '#F0EBD9',
  fillOpacity: 0.5,
}

// 地图初始视图
export const MAP_INIT = {
  center: [32, 108],
  zoom: 4,
  minZoom: 3,
  maxZoom: 8,
  maxBounds: [[15, 70], [55, 140]],
}
