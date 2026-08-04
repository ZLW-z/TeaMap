// 第五章数据与配置
import nationalYearly from '../data/ch5/national_yearly.json'
import provinceYearly from '../data/ch5/province_yearly.json'
import teaTypeExport from '../data/ch5/tea_type_export.json'
import exportByCountry from '../data/ch5/export_by_country.json'
import exportByProvince from '../data/ch5/export_by_province.json'
import sankeyFlow from '../data/ch5/sankey_flow.json'

export const nationalData = nationalYearly
export const provinceData = provinceYearly
export const teaTypeData = teaTypeExport
export const countryData = exportByCountry
export const provinceExportData = exportByProvince
export const sankeyData = sankeyFlow

// 茶种类别 -> 颜色
export const TEA_COLORS = {
  '绿茶': '#6F9150',
  '红茶': '#A8453A',
  '白茶': '#B8AE93',
  '乌龙茶': '#C8A155',
  '普洱茶': '#6B4423',
  '黑茶': '#3A2D24',
  '花茶': '#D89BAA',
  '其他': '#8A8270',
}

// 六大茶类解说
export const TEA_INFO = {
  '绿茶': { en: 'Green', desc: '不发酵茶，清汤绿叶，保留鲜叶天然物质。中国产量第一，西湖龙井、碧螺春为代表。', icon: '🌿' },
  '红茶': { en: 'Black', desc: '全发酵茶，红汤红叶，茶性温和。祁门红茶、正山小种享誉海外，出口主力之一。', icon: '🍂' },
  '白茶': { en: 'White', desc: '微发酵茶，满披白毫，工艺最简。福鼎白茶为代表，近年市场热度持续走高。', icon: '🤍' },
  '乌龙茶': { en: 'Oolong', desc: '半发酵茶，绿叶红镶边，香气馥郁。铁观音、大红袍、单丛皆属此类。', icon: '🍃' },
  '普洱茶': { en: "Pu'er", desc: '后发酵茶，越陈越香。云南特产，分生茶熟茶，具收藏与文化价值。', icon: '🫖' },
  '黑茶': { en: 'Dark', desc: '后发酵茶，汤色橙黄至暗褐。安化黑茶、六堡茶为代表，边疆民族日常饮品。', icon: '🟤' },
  '花茶': { en: 'Scented', desc: '再加工茶，以绿茶为茶坯窨制香花。茉莉花茶为代表，北方消费广泛。', icon: '🌸' },
}

export const TEA_ORDER = ['绿茶', '红茶', '乌龙茶', '花茶', '普洱茶', '白茶', '黑茶', '其他']

// 数字格式化
export function fmt(n, digits = 0) {
  if (!n || Number.isNaN(n)) return '—'
  return n.toLocaleString('zh-CN', { maximumFractionDigits: digits, minimumFractionDigits: digits })
}

// 取最新有完整数据的年份
export function latestFullYear() {
  const valid = nationalData.filter(d => d.gardenArea > 0)
  return valid.length ? valid[valid.length - 1].year : 2024
}

// 取分省数据中某指标最新有非零数据的年份
export function latestProvinceYear(metric) {
  const yearSet = new Set()
  provinceData.forEach(p => p.years.forEach(y => yearSet.add(y.year)))
  const years = Array.from(yearSet).sort((a, b) => b - a)
  for (const yr of years) {
    const count = provinceData.filter(p => {
      const pt = p.years.find(y => y.year === yr)
      return pt && pt[metric] > 0
    }).length
    if (count >= 3) return yr
  }
  return 2023
}

export function getNational(year) {
  return nationalData.find(d => d.year === year)
}

export function getProvince(name) {
  return provinceData.find(p => p.province === name)
}

export const LATEST_EXPORT_YEAR = 2024
