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

// 取分省数据中某指标最新有非零数据的年份（2025 年数据不完整，统一不超过 2024 年）
export function latestProvinceYear(metric) {
  const yearSet = new Set()
  provinceData.forEach(p => p.years.forEach(y => yearSet.add(y.year)))
  const years = Array.from(yearSet)
    .filter(y => y <= 2024)
    .sort((a, b) => b - a)
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

/* =======================================================================
 * 叶片·新生 —— 2010—2024 中国茶消费的长期变化与新表达（仅用于 ch5 叶片面板）
 * 数据来源: public/data/5/茶文化网页_叶片现代产品与消费趋势数据.xlsx
 *   sheets: 03_产品应用 / 04_内销趋势 / 05_线上趋势 / 06_阶段分析
 * qualifier 规则: 精确->直显; 约数->"约"/"≈"; 推算->"推算"; 下限->">"; 缺失->null
 * ======================================================================= */

// ---- 先看结论：3张分析卡 ----
export const LEAVES_CONCLUSIONS = [
  {
    id: 'scale',
    title: '十五年规模扩张',
    from: '2010',
    to: '2024',
    startVal: 110.00,
    endVal: 241.27,
    unit: '万吨',
    growthPct: 119.3,
    desc: '2010—2024年内销量由约110.00万吨增至241.27万吨，累计增长约119.3%。',
  },
  {
    id: 'shift',
    title: '增长速度换挡',
    phases: [
      { period: '2010—2014', cagr: 8.1 },
      { period: '2015—2019', cagr: 4.8 },
      { period: '2020—2024', cagr: 2.3 },
    ],
    desc: '三阶段复合增速由8.1%降至2.3%，增长逐步放缓。',
  },
  {
    id: 'recent',
    title: '近两年量稳价变',
    compareYear: 2022,
    currentYear: 2024,
    metrics: [
      { label: '内销量', change: '+0.6%' },
      { label: '内销额', change: '-4.1%' },
      { label: '均价', change: '-4.7%' },
    ],
    desc: '量稳价变，市场从规模扩张转向结构竞争。',
  },
]

// ---- 04_内销趋势：2010—2024 全15年 ----
// volume=内销量(万吨) value=内销总额(亿元) avgPrice=均价(元/千克)
// qualifier: 精确/约数/推算/约数·图表数字化
// value=null 表示该年无纳入口径可比的总额数据（2010—2012）
export const LEAVES_DOMESTIC_TREND = [
  { year: 2010, volume: 110.00, volumeQualifier: '约数', value: null, avgPrice: null, fig1Label: '2010｜110.00万吨（约数）', sourceNote: '2010年国内茶叶消费量约110万吨；未采用不可比零售额', sourceUrl: 'https://www.chinadaily.com.cn/dfpd/2011-09/22/content_13774068.htm' },
  { year: 2011, volume: 118.00, volumeQualifier: '约数', value: null, avgPrice: null, fig1Label: '2011｜118.00万吨（约数）', sourceNote: '公开报道为接近118万吨；未采用不可比零售额', sourceUrl: 'https://www.aticoc.com/cqdt/info.aspx?itemid=3154' },
  { year: 2012, volume: 130.00, volumeQualifier: '精确', value: null, avgPrice: null, fig1Label: '2012｜130.00万吨', sourceNote: '全国茶叶消费量130万吨；未采用不可比零售额', sourceUrl: 'https://www.hunan.gov.cn/szf/hnzb_18/2014_18/2014nd4q_18/szfbgtwj_98278_18/201403/t20140311_4700858.html' },
  { year: 2013, volume: 133.83, volumeQualifier: '推算', value: 1380, valueQualifier: '约数', avgPrice: 103.12, fig1Label: '2013｜133.83万吨（推算）', fig2ValueLabel: '1380.00亿元（约）', fig2PriceLabel: '103.12元/千克', sourceNote: '内销量由2013—2023增量与增幅反推；销售额依据协会公开图表数字化', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/72433.html' },
  { year: 2014, volume: 150.25, volumeQualifier: '精确', value: 1660, valueQualifier: '约数', avgPrice: 110.48, fig1Label: '2014｜150.25万吨', fig2ValueLabel: '1660.00亿元（约）', fig2PriceLabel: '110.48元/千克', sourceNote: '内销量为公开统计；销售额依据协会公开图表数字化', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/72433.html' },
  { year: 2015, volume: 168.00, volumeQualifier: '约数·图表数字化', value: 1870, valueQualifier: '约数', avgPrice: 111.31, fig1Label: '2015｜168.00万吨（约数/图表数字化）', fig2ValueLabel: '1870.00亿元（约）', fig2PriceLabel: '111.31元/千克', sourceNote: '内销量和销售额依据协会公开图表数字化，仅用于趋势展示', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/72433.html' },
  { year: 2016, volume: 171.06, volumeQualifier: '精确', value: 2148, valueQualifier: '精确', avgPrice: 125.57, fig1Label: '2016｜171.06万吨', fig2ValueLabel: '2148.00亿元', fig2PriceLabel: '125.57元/千克', sourceNote: '中国茶叶产销形势分析公开数据', sourceUrl: 'https://www.sciopen.com/local/article_pdf/10.15905/j.cnki.33-1157/ts.2022.02.004.pdf' },
  { year: 2017, volume: 181.70, volumeQualifier: '精确', value: 2353, valueQualifier: '精确', avgPrice: 129.50, fig1Label: '2017｜181.70万吨', fig2ValueLabel: '2353.00亿元', fig2PriceLabel: '129.50元/千克', sourceNote: '商务部对外投资合作国别（地区）指南相关统计', sourceUrl: 'https://www.mofcom.gov.cn/cms_files/filemanager/ckzn/upload/2018ckcy.pdf' },
  { year: 2018, volume: 191.05, volumeQualifier: '精确', value: 2661, valueQualifier: '精确', avgPrice: 139.28, fig1Label: '2018｜191.05万吨', fig2ValueLabel: '2661.00亿元', fig2PriceLabel: '139.28元/千克', sourceNote: '中国茶叶流通协会年度数据', sourceUrl: 'https://www.cnwinenews.com/html/2019/huaxiachashi_0605/117443.html' },
  { year: 2019, volume: 202.56, volumeQualifier: '精确', value: 2739.50, valueQualifier: '精确', avgPrice: 135.24, fig1Label: '2019｜202.56万吨', fig2ValueLabel: '2739.50亿元', fig2PriceLabel: '135.24元/千克', sourceNote: '中国茶叶流通协会2019年度数据', sourceUrl: 'https://www.ctma.com.cn/hangyeyaowen/65252.html' },
  { year: 2020, volume: 220.16, volumeQualifier: '精确', value: 2888.84, valueQualifier: '精确', avgPrice: 131.22, fig1Label: '2020｜220.16万吨', fig2ValueLabel: '2888.84亿元', fig2PriceLabel: '131.22元/千克', sourceNote: '中国茶叶流通协会2021年报告披露的2020年度数据', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/72433.html' },
  { year: 2021, volume: 230.19, volumeQualifier: '精确', value: 3120, valueQualifier: '精确', avgPrice: 135.54, fig1Label: '2021｜230.19万吨', fig2ValueLabel: '3120.00亿元', fig2PriceLabel: '135.54元/千克', sourceNote: '年度茶叶内销数据', sourceUrl: 'https://m.ipucha.com/show-11-7757.html' },
  { year: 2022, volume: 239.75, volumeQualifier: '精确', value: 3395.27, valueQualifier: '精确', avgPrice: 141.62, fig1Label: '2022｜239.75万吨', fig2ValueLabel: '3395.27亿元', fig2PriceLabel: '141.62元/千克', sourceNote: '2022年度茶叶内销数据', sourceUrl: 'https://bj.news.cn/20230602/a84263c1fc4641fbbbd03581ecfa0300/c.html' },
  { year: 2023, volume: 240.40, volumeQualifier: '精确', value: 3346.70, valueQualifier: '精确', avgPrice: 139.21, fig1Label: '2023｜240.40万吨', fig2ValueLabel: '3346.70亿元', fig2PriceLabel: '139.21元/千克', sourceNote: '中国茶叶流通协会年度调查数据', sourceUrl: 'https://www.ctma.com.cn/xxfb.html' },
  { year: 2024, volume: 241.27, volumeQualifier: '精确', value: 3257.55, valueQualifier: '精确', avgPrice: 135.02, fig1Label: '2024｜241.27万吨', fig2ValueLabel: '3257.55亿元', fig2PriceLabel: '135.02元/千克', sourceNote: '中国茶叶流通协会2024年度数据', sourceUrl: 'https://www.news.cn/food/20250403/762ed35936a64a34b43c08b0c836da2a/c.html' },
]

// ---- 05_线上趋势：2016—2024（2021缺失，不插值）----
export const LEAVES_ONLINE_TREND = [
  { year: 2016, value: 148, qualifier: '精确', displayValue: '148亿元', sourceNote: '第三方行业图表汇总', sourceUrl: 'https://www.woshipm.com/it/5174895.html' },
  { year: 2017, value: 175, qualifier: '精确', displayValue: '175亿元', sourceNote: '第三方行业图表汇总', sourceUrl: 'https://www.woshipm.com/it/5174895.html' },
  { year: 2018, value: 205, qualifier: '精确', displayValue: '205亿元', sourceNote: '第三方行业图表汇总', sourceUrl: 'https://www.woshipm.com/it/5174895.html' },
  { year: 2019, value: 243, qualifier: '精确', displayValue: '243亿元', sourceNote: '第三方行业图表汇总', sourceUrl: 'https://www.woshipm.com/it/5174895.html' },
  { year: 2020, value: 280, qualifier: '约数', displayValue: '≈280亿元', sourceNote: '协会报告与行业图表均显示约280亿元', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/72433.html' },
  { year: 2021, value: null, qualifier: '缺失', displayValue: '—', sourceNote: '未找到与前后口径一致的公开值，必须保留断点', sourceUrl: null },
  { year: 2022, value: 330, qualifier: '下限', displayValue: '>330亿元', sourceNote: '协会表述为超过330亿元', sourceUrl: 'https://www.ctma.com.cn/hangyeyaowen/77981.html' },
  { year: 2023, value: 350, qualifier: '下限', displayValue: '>350亿元', sourceNote: '协会表述为超过350亿元', sourceUrl: 'https://www.ctma.com.cn/hangyeyaowen/77981.html' },
  { year: 2024, value: 370, qualifier: '约数', displayValue: '≈370亿元', sourceNote: '协会表述为约370亿元', sourceUrl: 'https://www.ctma.com.cn/xiehuidongtai/80691.html' },
]

// ---- 06_阶段分析：三阶段 ----
export const LEAVES_STAGES = [
  {
    id: 'P1',
    period: '2010—2014',
    name: '规模扩张',
    startVolume: 110.00,
    endVolume: 150.25,
    cagr: 8.1,
    startValue: null,
    endValue: 1660,
    conclusion: '内销量由约110增至150.25万吨，规模快速扩张；早期总额口径不完整，因此不做量价强比较。',
  },
  {
    id: 'P2',
    period: '2015—2019',
    name: '价值提升与电商萌芽',
    startVolume: 168.00,
    endVolume: 202.56,
    cagr: 4.8,
    startValue: 1870,
    endValue: 2739.50,
    conclusion: '内销量继续上行，内销额约由1870增至2739.5亿元；电商开始成为可见渠道。',
  },
  {
    id: 'P3',
    period: '2020—2024',
    name: '场景分化与理性调整',
    startVolume: 220.16,
    endVolume: 241.27,
    cagr: 2.3,
    startValue: 2888.84,
    endValue: 3257.55,
    conclusion: '内销量仍增但复合增速降至约2.3%；总额2022年见顶后回落，市场转向场景与产品结构竞争。',
  },
]

// ---- 03_产品应用：六种新表达（入口卡 + 详情卡，数据独立不做横向比较）----
export const LEAVES_PRODUCT_APPS = [
  {
    order: 1,
    type: '原叶冲泡',
    subtitle: '原叶传统冲泡',
    image: '/data/5/images/01-loose-leaf-tea-wide.png',
    imageAlt: '完整呈现的紫砂壶、原叶茶与茶汤',
    imagePosition: 'center 55%',
    imageCredit: 'Markus Kniebes · Wikimedia Commons（CC0）',
    imageSourceUrl: 'https://commons.wikimedia.org/wiki/File:Yixing_ware_teapot_and_Lapsang_tea.jpg',
    summary: '2024年，全国原叶茶内销量为241.27万吨，内销总额达到3257.55亿元。',
    // 入口卡默认显示 2 个代表产品示例
    entryProducts: ['散茶', '冷泡'],
    // 详情卡：全部代表产品
    products: ['散茶', '冷泡', '小规格', '拼配风味'],
    coreNum: '241.27',
    coreUnit: '万吨',
    indexName: '2024年原叶茶内销量',
    year: '2024',
    range: '全国',
    aux: '内销总额3257.55亿元',
    explain: '原叶茶仍是中国茶消费的主体，也是其他现代茶产品的原料基础。',
    source: '中国茶叶流通协会、新华网',
    sourceUrl: 'https://www.news.cn/food/20250403/762ed35936a64a34b43c08b0c836da2a/c.html',
    trendExplain: '保留茶叶本体与冲泡仪式，同时降低知识和时间门槛',
    observeDims: '产品形态/冲泡方式/包装规格',
  },
  {
    order: 2,
    type: '便捷茶饮',
    subtitle: '冲泡变得更便捷',
    image: '/data/5/images/02-convenient-tea-wide.png',
    imageAlt: '完整呈现的袋泡茶杯、茶包与茶汤',
    imagePosition: 'center 48%',
    imageCredit: 'HisSpaceResearch · Wikimedia Commons（公共领域）',
    imageSourceUrl: 'https://commons.wikimedia.org/wiki/File:Tea_bag.JPG',
    summary: '2022年，全国袋泡茶线上市场规模为180.3亿元；截至2023年6月，袋泡茶存续企业达1939家。',
    entryProducts: ['袋泡茶', '茶粉'],
    products: ['袋泡茶', '茶粉', '浓缩茶液', '冻干茶块'],
    coreNum: '180.3',
    coreUnit: '亿元',
    indexName: '袋泡茶线上市场规模',
    year: '2022',
    range: '全国线上市场',
    aux: '截至2023年6月，袋泡茶存续企业1939家',
    explain: '袋泡茶以冲泡简单和便携为核心特征，是便捷茶饮中公开数据较完整的代表品类。',
    source: '艾媒咨询（新浪财经转载）',
    sourceUrl: 'https://finance.sina.cn/2023-07-06/detail-imyztazu9095747.d.html?vt=4',
    trendExplain: '强调即溶、定量、便携，连接办公与出行场景',
    observeDims: '形态数量/冲泡时长/便携场景',
  },
  {
    order: 3,
    type: '现制新茶饮',
    subtitle: '融入现代调饮',
    image: '/data/5/images/03-modern-tea-drink-wide.png',
    imageAlt: '三杯中国现制奶茶产品',
    imageCredit: 'CHENG SHIYI · Wikimedia Commons（CC BY-SA 4.0）',
    imageSourceUrl: 'https://commons.wikimedia.org/wiki/File:%E8%8C%B6%E9%A2%9C%E6%82%A6%E8%89%B2%E5%A5%B6%E8%8C%B6%E5%AE%9E%E6%8B%8D%E5%9B%BE.jpg',
    summary: '2024年，全国新茶饮行业耗茶量约30万吨，约占当年原叶茶内销量的12.4%。',
    entryProducts: ['原叶鲜奶茶', '果茶'],
    products: ['原叶鲜奶茶', '果茶', '纯茶', '轻乳茶'],
    coreNum: '约30',
    coreUnit: '万吨',
    indexName: '新茶饮行业耗茶量',
    year: '2024',
    range: '全国',
    aux: '约占当年原叶茶内销量12.4%',
    explain: '现制新茶饮已成为连接传统茶产区与年轻消费场景的重要原料渠道。',
    source: '中国茶叶流通协会、新华网',
    sourceUrl: 'https://www.news.cn/food/20250403/762ed35936a64a34b43c08b0c836da2a/c.html',
    trendExplain: '从单一饮品转向口味、社交和门店体验',
    observeDims: '菜单结构/基底茶种/门店场景',
  },
  {
    order: 4,
    type: '即饮及无糖茶',
    subtitle: '免冲泡即开即饮',
    image: '/data/5/images/04-ready-to-drink-tea-wide.png',
    imageAlt: '中国市场销售的瓶装柠檬茶饮料',
    imageCredit: 'Dinkun Chen · Wikimedia Commons（CC BY-SA 4.0）',
    imageSourceUrl: 'https://commons.wikimedia.org/wiki/File:VITA_LEMON_TEA_CHINA_VERSION.jpg',
    summary: '2024年，全国无糖茶饮市场规模约600亿元，总产量突破2000万吨。',
    entryProducts: ['瓶装原叶茶', '无糖茶'],
    products: ['瓶装原叶茶', '无糖茶', '低糖茶', '气泡茶'],
    coreNum: '约600',
    coreUnit: '亿元',
    indexName: '无糖茶饮市场规模',
    year: '2024',
    range: '全国',
    aux: '总产量突破2000万吨',
    explain: '无糖茶将茶叶风味、标准化生产和即开即饮结合，成为包装茶饮的重要增长方向。',
    source: '中国茶叶流通协会、新华网',
    sourceUrl: 'https://www.news.cn/food/20250403/762ed35936a64a34b43c08b0c836da2a/c.html',
    trendExplain: '以健康感、便利性和稳定口味进入高频消费',
    observeDims: '糖度/容量/饮用频次/渠道',
  },
  {
    order: 5,
    type: '茶食品',
    subtitle: '从饮茶到食茶',
    image: '/data/5/images/05-tea-food-wide.png',
    imageAlt: '抹茶蛋糕卷与茶饮',
    imagePosition: 'center 72%',
    imageCredit: 'Andy Li · Wikimedia Commons（CC0）',
    imageSourceUrl: 'https://commons.wikimedia.org/wiki/File:Matcha_rollcake_and_iced_lemon_tea_-_Rawlab_Juice_%26_Tea.jpg',
    summary: '2023年，浙江省作为代表性案例，抹茶产量超过4200吨，产值突破6亿元。',
    entryProducts: ['抹茶烘焙', '茶点'],
    products: ['抹茶烘焙', '茶点', '糖果', '冰淇淋', '复合调味'],
    coreNum: '4200吨以上',
    coreUnit: '',
    indexName: '浙江抹茶产量（区域案例）',
    year: '2023',
    range: '浙江省代表性案例',
    aux: '产值突破6亿元',
    explain: '抹茶能够直接进入烘焙、甜品和复合食品，是茶食品应用较具代表性的原料。',
    source: '福建日报',
    sourceUrl: 'https://www.fjdaily.com/app/content/2025-01/21/content_3060209.html',
    isRegional: true,
    trendExplain: '将茶香、茶色与茶文化转化为可食用体验',
    observeDims: '品类/风味/联名/节令',
  },
  {
    order: 6,
    type: '精深应用',
    subtitle: '拓展为功能性原料',
    image: '/data/5/images/06-tea-extract-wide.png',
    imageAlt: '茶提取物粉末、功能性胶囊与茶叶',
    imageCredit: 'aixklusiv · Pixabay Content License',
    imageSourceUrl: 'https://pixabay.com/photos/capsules-matcha-tea-3285279/',
    summary: '2017年，全国茶叶提取物产量超过2.5万吨，累计消耗茶叶原料约15万吨。',
    entryProducts: ['茶多酚', '茶氨酸'],
    products: ['茶多酚', '茶氨酸', '茶色素', '日化及保健应用'],
    coreNum: '2.5万吨以上',
    coreUnit: '',
    indexName: '全国茶叶提取物产量',
    year: '2017',
    range: '全国',
    aux: '累计消耗茶叶原料约15万吨',
    explain: '茶叶提取物进入功能饮料、食品、日化和健康产品，延伸了茶叶的产业链。',
    source: '人民周刊',
    sourceUrl: 'https://paper.people.com.cn/rmzk/html/2019-08/05/content_1939659.htm',
    trendExplain: '延伸产业链，突出功能成分和跨行业使用',
    observeDims: '成分/技术/应用行业/专利',
  },
]

// 数据来源统一说明
export const LEAVES_DATA_SOURCE = '数据来源：中国茶叶流通协会、新华社、商务部及公开行业资料；约数、推算值与缺失值已单独标注，详见数据表。'
