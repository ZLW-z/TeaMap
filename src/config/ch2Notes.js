// 第二章 · "数据与分类依据"注解内容（只读配置）
// 原则：本文件只负责解释"数据从哪里来、当前图表示什么、分类依据来自哪里"。
//       不参与任何地图计算；"当前地图分级"一律从 ch2.js 的 FACTORS / COMPOSITE
//       levels 中实时读取，保证注解与图例阈值完全一致，不在此处另行维护数值。
import { FACTORS, COMPOSITE } from './ch2.js'

/* ---------------------------------------------------------
 * 各因子注解文案（字段：数据名称/数据来源/时间范围/空间分辨率/
 * 原始单位/处理方法/分类依据/补充说明/参考来源）
 * --------------------------------------------------------- */
const FACTOR_NOTES = {
  precip: {
    title: '降水适宜性',
    dataName: 'WorldClim 年降水量栅格（多年平均年降水）',
    dataSource: 'WorldClim Global Climate Data',
    timeRange: '多年气候平均态（年降水量）',
    resolution: '约 1 km',
    unit: 'mm',
    processing: '月/年降水栅格 → 多年平均年降水 → 中国范围裁剪 → 按项目分级阈值重分类',
    basis: 'FAO ECOCROP 对茶树（Camellia sinensis）给出的最适年降水为 1400–2000 mm，绝对生态范围约 1000–5000 mm。本图分级为项目当前采用的阈值，FAO 区间仅作生态需求参考。',
    note: '',
    sources: [
      { label: 'WorldClim Global Climate Data', url: 'https://www.worldclim.org/data/index.html' },
      { label: 'FAO ECOCROP – Camellia sinensis', url: 'https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=599' },
    ],
  },

  temp: {
    title: '多年平均气温',
    dataName: '中国逐日近地表气温数据集（日平均气温 Tavg）',
    dataSource: 'A Daily near-surface Air Temperature Dataset for China from 1979–2018',
    timeRange: '原始数据 1979–2018，取多年平均',
    resolution: '0.1°（逐日）',
    unit: '℃',
    processing: '逐日平均气温 → 多年平均 → 按项目阈值划分温度适宜带',
    basis: 'FAO ECOCROP 给出茶树最适温度 20–30 ℃、绝对范围 8–35 ℃。本图采用"核心—过渡—边缘"连续适宜性表达，分级阈值读取项目当前配置，与 FAO 最适范围区分表述。',
    note: '',
    sources: [
      { label: 'Zenodo 数据集（DOI 10.5281/zenodo.5502275）', url: 'https://doi.org/10.5281/zenodo.5502275' },
      { label: 'FAO ECOCROP – Camellia sinensis', url: 'https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=599' },
    ],
  },

  accum: {
    title: '≥10℃活动积温',
    dataName: '中国逐日近地表气温数据集（Tavg ≥10℃ 日期累计）',
    dataSource: 'A Daily near-surface Air Temperature Dataset for China from 1979–2018',
    timeRange: '项目处理时段 2000–2018，取多年平均',
    resolution: '0.1°（逐日）',
    unit: '℃·d',
    processing: '逐日筛选 Tavg≥10℃ → 年活动积温 → 2000–2018 多年平均 → 三级重分类',
    basis: '活动积温累计 Tavg≥10℃ 日期的日平均气温本身（非 Σ(T−10) 的有效积温概念）。茶树适宜性研究常将 ≥10℃ 活动积温作为关键热量指标，本图分为最优核心区、适宜过渡区、限制边缘区，阈值读取现有重分类结果。',
    note: '',
    sources: [
      { label: 'Zenodo 数据集（DOI 10.5281/zenodo.5502275）', url: 'https://doi.org/10.5281/zenodo.5502275' },
      { label: 'Li et al. 2012, Comprehensive Suitability Evaluation of Tea Crops Using GIS', url: 'https://doi.org/10.1016/S1002-0160(11)60198-7' },
      { label: '全国茶树种植适宜性区划研究（农业工程学报）', url: 'https://www.aeeisp.com/nygcxb/article/doi/10.11975/j.issn.1002-6819.202509121' },
    ],
  },

  rad: {
    title: '太阳辐射',
    dataName: 'CHELSA V2.1 地表向下短波辐射（rsds）',
    dataSource: 'CHELSA-climatologies V2.1',
    timeRange: '1981–2010 气候平均态（climatological means）',
    resolution: '约 1 km',
    unit: '原始单位 W·m⁻²；本图换算为年太阳总辐射 kcal·cm⁻²',
    processing: '1–12 月 rsds 多年平均栅格 → 中国范围裁剪 → 换算年太阳总辐射 → 按项目最终阈值重分类',
    basis: 'FAO ECOCROP 对茶树光照仅给出 very bright / light shade 的定性描述。图中数值区间为项目采用的文献/经验分级，并非 FAO 官方数值标准。',
    note: '',
    sources: [
      { label: 'CHELSA-climatologies V2.1', url: 'https://www.chelsa-climate.org/datasets/chelsa_climatologies' },
      { label: 'CHELSA 官网', url: 'https://www.chelsa-climate.org/' },
      { label: 'FAO ECOCROP – Camellia sinensis', url: 'https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=599' },
    ],
  },

  ph: {
    title: '土壤 pH',
    dataName: 'HWSD v2.0 土壤酸碱度栅格（中国范围裁剪）',
    dataSource: 'FAO & IIASA, Harmonized World Soil Database v2.0（HWSD v2.0）',
    timeRange: 'HWSD v2.0 历史土壤调查汇编',
    resolution: '约 1 km（30 arc-second）',
    unit: 'pH（无量纲）',
    processing: '异常/NoData 清理 → 中国范围裁剪 → 按 pH 区间重分类 → 适宜性地图',
    basis: '最适区依据 FAO ECOCROP（最适土壤 pH 4.5–5.5，绝对范围 4.0–6.0）；外围过渡/限制等级为项目扩展分级，并非 FAO 原始标准。',
    note: '',
    sources: [
      { label: 'FAO – Harmonized World Soil Database', url: 'https://www.fao.org/land-water/resources/tools/databases/hwsd/en' },
      { label: 'HWSD v2.0 技术报告', url: 'https://www.fao.org/3/cc3823en/cc3823en.pdf' },
      { label: 'FAO ECOCROP – Camellia sinensis', url: 'https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=599' },
    ],
  },

  composite: {
    title: '综合适宜性评价',
    dataName: '降水、多年均温、≥10℃活动积温、太阳辐射、土壤 pH 五因子重分类结果',
    dataSource: '各单因子数据源（详见对应因子注解）',
    timeRange: '各因子数据时段见对应因子注解',
    resolution: '各因子原始分辨率不一，叠置前统一重采样',
    unit: '适宜性等级（0–3）',
    processing: '各因子先转换为统一适宜性等级，再按项目综合评价方法（等权重空间叠置）得到综合结果',
    basis: '项目综合评价配置：五因子等权重叠加，综合评分 ≥2.5 为茶树生长最适宜区。',
    note: '综合结果反映自然环境条件的相对适宜程度，不等同于实际茶园分布，也不包含市场、交通、劳动力、政策等社会经济因素。',
    sources: [],
  },
}

/* ---------------------------------------------------------
 * "当前地图分级"：实时读取 ch2.js 现有 levels，
 * 与右侧图例完全同源，避免注解与地图阈值不一致。
 * --------------------------------------------------------- */
function getFactorLevels(factorId) {
  const cfg = factorId === 'composite' ? COMPOSITE : FACTORS[factorId]
  if (!cfg) return []
  return cfg.levels.map(lv => ({
    value: lv.value,
    label: lv.label,
    range: lv.range || '',
    color: lv.color,
  }))
}

// 分级下方的补充说明（仅综合评价有）
const CLASSIFICATION_EXTRA = {
  composite: '五因子等权重叠加，综合评分 ≥2.5 为最适宜区（读取自项目综合评价配置）。',
}

export { FACTOR_NOTES, getFactorLevels, CLASSIFICATION_EXTRA }
