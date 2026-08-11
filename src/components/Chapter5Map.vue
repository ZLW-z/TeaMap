<template>
  <section class="chapter chapter-5" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="伍"
      title="今日茶境"
      desc="千年茶脉绵延至今，国内茶园规模稳步扩张，茶叶外销步履不停，现代产业续写着茶业蓬勃发展的新篇章。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen ch5-redesign" :class="{ show: introDone }">

      <!-- =============== LEFT: Tea tree with 3 clickable zones =============== -->
      <div class="ch5-left">
        <div class="ch5-tree-scene single-tree">
          <svg viewBox="0 0 600 820" class="tree-svg" preserveAspectRatio="xMidYMid meet">
            <defs>
              <!-- 扩散圆动画 -->
              <radialGradient id="rippleGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(255,255,255,0.85)" />
                <stop offset="60%" stop-color="rgba(255,255,255,0.28)" />
                <stop offset="100%" stop-color="rgba(255,255,255,0)" />
              </radialGradient>
              <linearGradient id="skyGrad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#F0EBDC" />
                <stop offset="50%" stop-color="#E0DECC" />
                <stop offset="100%" stop-color="#D8DCC0" />
              </linearGradient>
              <linearGradient id="groundGrad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#B8B484" />
                <stop offset="30%" stop-color="#9A9567" />
                <stop offset="100%" stop-color="#6B5D3A" />
              </linearGradient>
            </defs>

            <!-- 背景 -->
            <rect x="0" y="0" width="600" height="630" fill="url(#skyGrad2)" rx="18" />
            <rect x="0" y="630" width="600" height="190" fill="url(#groundGrad2)" rx="18" />

            <!-- 单棵大茶树（放大1.5倍居中，底部与土面对齐并略下移） -->
            <g class="tea-tree single-big-tree" style="transform-origin: 300px 630px;">
              <image :href="TREE_IMG_URL" x="-90" y="-120" width="780" height="1050" preserveAspectRatio="xMidYEnd meet" />
            </g>

            <!-- ============ 区域1: 叶片（对应茶树右上叶片团） ============ -->
            <g class="click-zone zone-leaves"
               :class="{ active: activePhonePanel === 'leaves', hover: hoveredZone === 'leaves' }"
               @mouseenter="hoveredZone = 'leaves'"
               @mouseleave="hoveredZone = null"
               @click="activePhonePanel = 'leaves'"
            >
              <!-- 点击热区（覆盖右上叶片团） -->
              <circle cx="390" cy="220" r="108" fill="rgba(255,255,255,0.001)" stroke="none" style="cursor:pointer" />
              <!-- 扩散圆动效（圆心即热区中心） -->
              <circle class="ripple ripple-1" cx="390" cy="220" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-2" cx="390" cy="220" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-3" cx="390" cy="220" r="18" fill="url(#rippleGrad)" />
              <!-- 标注框（左上） -->
              <g class="zone-tag" transform="translate(24, 76)">
                <rect x="0" y="0" width="152" height="64" rx="12"
                      :fill="activePhonePanel === 'leaves' ? 'rgba(92,124,58,0.95)' : 'rgba(247,244,235,0.92)'" />
                <text x="14" y="26"
                      :fill="activePhonePanel === 'leaves' ? '#FFF8E8' : '#5C7C3A'"
                      style="font-size:13px;font-weight:700;letter-spacing:0.05em">叶片 · 茶种</text>
                <text x="14" y="52"
                      :fill="activePhonePanel === 'leaves' ? '#EFE9DA' : '#4A4A40'"
                      style="font-size:22px;font-weight:900;font-family:var(--font-huiwen)">{{ fmt(output, 2) }}万吨</text>
              </g>
              <!-- 引线：标签右下 → 热区中心左下 -->
              <line x1="176" y1="106" x2="320" y2="232" stroke="#5C7C3A" stroke-width="2" stroke-dasharray="4 4" fill="none" opacity="0.75" />
            </g>

            <!-- ============ 区域2: 枝条（对应主干中部） ============ -->
            <g class="click-zone zone-branches"
               :class="{ active: activePhonePanel === 'branches', hover: hoveredZone === 'branches' }"
               @mouseenter="hoveredZone = 'branches'"
               @mouseleave="hoveredZone = null"
               @click="activePhonePanel = 'branches'"
            >
              <circle cx="285" cy="520" r="108" fill="rgba(255,255,255,0.001)" stroke="none" style="cursor:pointer" />
              <circle class="ripple ripple-1" cx="285" cy="520" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-2" cx="285" cy="520" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-3" cx="285" cy="520" r="18" fill="url(#rippleGrad)" />
              <g class="zone-tag" transform="translate(24, 484)">
                <rect x="0" y="0" width="164" height="64" rx="12"
                      :fill="activePhonePanel === 'branches' ? 'rgba(107,68,35,0.95)' : 'rgba(247,244,235,0.92)'" />
                <text x="14" y="26"
                      :fill="activePhonePanel === 'branches' ? '#FFF8E8' : '#6B4423'"
                      style="font-size:13px;font-weight:700;letter-spacing:0.05em">枝条 · 出口</text>
                <text x="14" y="52"
                      :fill="activePhonePanel === 'branches' ? '#EFE9DA' : '#4A4A40'"
                      style="font-size:22px;font-weight:900;font-family:var(--font-huiwen)">{{ fmt(exportTotal / 1e8, 2) }}亿元</text>
              </g>
              <line x1="188" y1="516" x2="218" y2="520" stroke="#6B4423" stroke-width="2" stroke-dasharray="4 4" fill="none" opacity="0.75" />
            </g>

            <!-- ============ 区域3: 根系（对应泥土层根部中心） ============ -->
            <g class="click-zone zone-roots"
               :class="{ active: activePhonePanel === 'roots', hover: hoveredZone === 'roots' }"
               @mouseenter="hoveredZone = 'roots'"
               @mouseleave="hoveredZone = null"
               @click="activePhonePanel = 'roots'"
            >
              <circle cx="295" cy="750" r="112" fill="rgba(255,255,255,0.001)" stroke="none" style="cursor:pointer" />
              <circle class="ripple ripple-1" cx="295" cy="750" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-2" cx="295" cy="750" r="18" fill="url(#rippleGrad)" />
              <circle class="ripple ripple-3" cx="295" cy="750" r="18" fill="url(#rippleGrad)" />
              <g class="zone-tag" transform="translate(24, 738)">
                <rect x="0" y="0" width="180" height="64" rx="12"
                      :fill="activePhonePanel === 'roots' ? 'rgba(178,143,76,0.95)' : 'rgba(247,244,235,0.92)'" />
                <text x="14" y="26"
                      :fill="activePhonePanel === 'roots' ? '#FFF8E8' : '#B28F4C'"
                      style="font-size:13px;font-weight:700;letter-spacing:0.05em">根系 · 生产</text>
                <text x="14" y="52"
                      :fill="activePhonePanel === 'roots' ? '#EFE9DA' : '#4A4A40'"
                      style="font-size:22px;font-weight:900;font-family:var(--font-huiwen)">{{ fmt(gardenArea, 2) }}千公顷</text>
              </g>
              <line x1="204" y1="770" x2="240" y2="752" stroke="#B28F4C" stroke-width="2" stroke-dasharray="4 4" fill="none" opacity="0.75" />
            </g>
          </svg>
        </div>
      </div>

      <!-- =============== RIGHT: Phone/Tablet screen waterfall =============== -->
      <div class="ch5-right">
        <div class="phone-frame" :class="'panel-' + activePhonePanel">
          <!-- 手机顶部状态栏 -->
          <div class="phone-notch">
            <div class="notch-speaker"></div>
            <div class="notch-cam"></div>
          </div>
          <div class="phone-statusbar">
            <span class="sb-time">9:41</span>
            <span class="sb-title">{{ activePhonePanel === 'roots' ? '生产根基' : activePhonePanel === 'leaves' ? '茶种结构' : '出口流向' }}</span>
            <span class="sb-signal">●●●</span>
          </div>

          <!-- 手机小程序内容区（瀑布流） -->
          <div class="phone-screen" :key="activePhonePanel">

            <!-- ========== 根系：生产根基（瀑布流） ========== -->
            <div v-if="activePhonePanel === 'roots'" class="waterfall-panel panel-roots">

              <!-- 顶部小工具条 -->
              <div class="wf-controls wf-ctrl-inline">
                <div class="ch5-metric-toggle small">
                  <button
                    v-for="m in metricOptions"
                    :key="m.key"
                    :class="['toggle-btn', { active: metric === m.key }]"
                    :style="metric === m.key ? { background: m.color, borderColor: m.color } : {}"
                    @click="setMetric(m.key)"
                  >{{ m.label }}</button>
                </div>
                <div class="ch5-year-slider small">
                  <input type="range" :min="allProvinceYears[0]" :max="allProvinceYears[allProvinceYears.length - 1]" step="1" v-model.number="rootsYear" class="slider-input" />
                  <span class="slider-value">{{ rootsYear }}</span>
                </div>
              </div>

              <!-- 概览 2x2 -->
              <div class="wf-overview-grid">
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">茶园面积</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ fmt(rootsOverview.gardenArea, 2) }}</span><span class="ov-unit">千公顷</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">茶叶产量</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ fmt(rootsOverview.totalOutput, 2) }}</span><span class="ov-unit">万吨</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">产量同比</div>
                  <div class="ov-value">
                    <span class="ch5-stat-num" :style="{ color: rootsOverview.yoy >= 0 ? '#5C7C3A' : '#A8453A' }">
                      {{ rootsOverview.yoy !== null ? (rootsOverview.yoy >= 0 ? '+' : '') + rootsOverview.yoy.toFixed(2) + '%' : '—' }}
                    </span>
                  </div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">统计省份</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ rootsOverview.provinceCount }}</span><span class="ov-unit">个</span></div>
                </div>
              </div>

              <!-- 地图 -->
              <div class="ch5-card small-card wf-map-card">
                <div class="card-title-sm">{{ metricLabel }}分布</div>
                <div class="chart-container chart-map">
                  <div v-if="!mapReady" class="ch5-map-loading">加载中…</div>
                  <EChart v-else :option="rootsMapOption" @ready="onRootsMapReady" @click="onMapClick" style="height:280px" />
                </div>
              </div>

              <!-- 省份详情 -->
              <div class="ch5-card small-card wf-prov-card">
                <div class="card-title-sm">{{ selectedProvince }} · 详情</div>
                <div v-if="rootsProvinceDetail" class="province-detail-body small">
                  <div class="chart-container chart-province-trend small">
                    <EChart :option="rootsProvinceTrendOption" style="height:200px" />
                  </div>
                </div>
                <div v-else class="empty-hint small">点击地图选择省份</div>
              </div>

              <!-- TOP10 排名 -->
              <div class="ch5-card small-card wf-rank-card">
                <div class="card-title-sm">{{ metricLabel }} TOP 10</div>
                <div class="chart-container chart-ranking small">
                  <EChart :option="rootsRankingOption" style="height:260px" />
                </div>
              </div>
            </div>

            <!-- ========== 叶片：茶种结构（瀑布流） ========== -->
            <div v-if="activePhonePanel === 'leaves'" class="waterfall-panel panel-leaves">

              <div class="wf-controls wf-ctrl-inline">
                <div class="ch5-year-select small">
                  <select v-model.number="leavesYear" class="select-input">
                    <option v-for="y in leavesYears" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>
              </div>

              <div class="wf-overview-grid">
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">出口总额</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ fmt(leavesOverview.totalExport / 1e8, 2) }}</span><span class="ov-unit">亿</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">首类茶种</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ leavesOverview.topType || '—' }}</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">茶种类</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ leavesOverview.typeCount }}</span><span class="ov-unit">类</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">总产量</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ fmt(leavesOverview.latestOutput, 2) }}</span><span class="ov-unit">万吨</span></div>
                </div>
              </div>

              <!-- 饼图（茶种出口结构） -->
              <div class="ch5-card small-card">
                <div class="card-title-sm">茶种出口结构</div>
                <div class="chart-container chart-pie small">
                  <EChart :option="leavesPieOption" style="height:260px" />
                </div>
              </div>

              <!-- 茶种产量趋势 -->
              <div class="ch5-card small-card">
                <div class="card-title-sm">茶种产量趋势</div>
                <div class="chart-container chart-trend small">
                  <EChart :option="leavesTrendOption" style="height:240px" />
                </div>
              </div>

              <!-- 堆叠面积图（茶种出口演变） -->
              <div class="ch5-card small-card">
                <div class="card-title-sm">茶种出口演变 15—24</div>
                <div class="chart-container chart-stacked small">
                  <EChart :option="leavesStackedOption" style="height:260px" />
                </div>
              </div>
            </div>

            <!-- ========== 枝条：出口流向（瀑布流） ========== -->
            <div v-if="activePhonePanel === 'branches'" class="waterfall-panel panel-branches">

              <div class="wf-controls wf-ctrl-inline">
                <div class="ch5-year-select small">
                  <select v-model.number="branchesYear" class="select-input">
                    <option v-for="y in branchesYears" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>
              </div>

              <div class="wf-overview-grid">
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">出口总额</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ fmt(branchesOverview.totalExport / 1e8, 2) }}</span><span class="ov-unit">亿</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">首位目的</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ branchesOverview.topCountry || '—' }}</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">目的数</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ branchesOverview.countryCount }}</span><span class="ov-unit">国</span></div>
                </div>
                <div class="ch5-overview-card small-card">
                  <div class="ov-label">出口省份</div>
                  <div class="ov-value"><span class="ch5-stat-num">{{ branchesOverview.provinceCount }}</span><span class="ov-unit">省</span></div>
                </div>
              </div>

              <!-- 桑基图 -->
              <div class="ch5-card small-card wf-sankey-card">
                <div class="card-title-sm">省→目的地 桑基图</div>
                <div class="chart-container chart-sankey small">
                  <EChart :option="branchesSankeyOption" style="height:320px" />
                </div>
              </div>

              <!-- TOP 10 目的地 -->
              <div class="ch5-card small-card">
                <div class="card-title-sm">TOP 10 目的地</div>
                <div class="chart-container chart-country-rank small">
                  <EChart :option="branchesCountryRankOption" style="height:260px" />
                </div>
              </div>

              <!-- 出口趋势 -->
              <div class="ch5-card small-card">
                <div class="card-title-sm">出口趋势</div>
                <div class="chart-container chart-branch-trend small">
                  <EChart :option="branchesTrendOption" style="height:240px" />
                </div>
              </div>
            </div>

          </div>
          <!-- 手机底部 Home indicator -->
          <div class="phone-homebar"></div>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from './EChart.vue'
import ChapterIntro from './ChapterIntro.vue'
import * as echarts from 'echarts'
import { assetUrl } from '../utils/base.js'
import {
  nationalData,
  provinceData,
  teaTypeData,
  countryData,
  provinceExportData,
  sankeyData,
  TEA_COLORS,
  TEA_INFO,
  TEA_ORDER,
  fmt,
  latestFullYear,
  latestProvinceYear,
  getNational,
  getProvince,
  LATEST_EXPORT_YEAR,
} from '../config/ch5.js'

const props = defineProps({ id: { type: String, required: true } })

// 茶树图资源路径
const TREE_IMG_URL = assetUrl('data/5/茶树.png')

// ---- 数据辅助：判断值是否为 "空/0/不存在"，为 true 则从可视化中剔除（折线转 null、饼/排名/Sankey过滤）
function isMissingVal(v) {
  if (v === null || v === undefined || v === '') return true
  if (typeof v === 'number') {
    return Number.isNaN(v) || v === 0
  }
  // 字符串：形如 "—" / "-" / "--" / 0 字符串等 → 空
  if (typeof v === 'string') {
    const s = v.trim()
    if (!s) return true
    if (/^[—\-–~_·]*$/.test(s)) return true
    const num = Number(s)
    if (!Number.isNaN(num)) return num === 0
    return false
  }
  return false
}
// 折线/堆叠用：缺失返回 null（ECharts 自动断线不绘制），非缺失原样
function numOrNull(v) {
  return isMissingVal(v) ? null : (typeof v === 'number' ? v : Number(v))
}
function arrHasAnyValue(arr) {
  return arr.some(v => v !== null && v !== undefined)
}

// ---- Tab system (兼容原逻辑) ----
const tabs = [
  { key: 'home', label: '茶树全景', icon: '🌳' },
  { key: 'roots', label: '根系·生产', icon: '🌱' },
  { key: 'leaves', label: '叶片·茶种', icon: '🍃' },
  { key: 'branches', label: '枝条·出口', icon: '🌐' },
]
// 手机屏幕当前显示的面板: roots/leaves/branches
const activePhonePanel = ref('roots')
// 保持 activeTab 为一个常量，用于原 roots/leaves/branches 选项内 v-show 始终显示（因为在手机里，不是整屏切换了）
const activeTab = computed({
  get() { return activePhonePanel.value },
  set(v) { if (['roots','leaves','branches'].includes(v)) activePhonePanel.value = v }
})

// ---- Shared refs ----
const sectionEl = ref(null)
const hoveredZone = ref(null)
const mapReady = ref(false)
const introDone = ref(false)

// ---- 地图缩放联动：geo zoom 与 bubble symbolSize 同步 ----
const DEFAULT_GEO_ZOOM = 1.15
const currentGeoZoom = ref(DEFAULT_GEO_ZOOM)
let _rootsChartInstance = null

function onRootsMapReady(chart) {
  _rootsChartInstance = chart
  // 监听缩放/平移事件，同步 zoom
  chart.on('georoam', () => {
    try {
      const opt = chart.getOption()
      // 茶园面积 tab: opt.geo[0].zoom；产量 tab: opt.series[0].zoom
      const bubbleZoom = opt.geo?.[0]?.zoom
      const mapZoom = opt.series?.[0]?.zoom
      const z = bubbleZoom ?? mapZoom ?? DEFAULT_GEO_ZOOM
      if (typeof z === 'number' && z > 0) {
        currentGeoZoom.value = z
      }
    } catch (_) { /* ignore */ }
  })
}

// ---- Metric config ----
const metricOptions = [
  { key: 'gardenArea', label: '茶园面积', unit: '千公顷', color: '#B28F4C' },
  { key: 'totalOutput', label: '茶叶产量', unit: '万吨', color: '#5C7C3A' },
]
const metric = ref('gardenArea')
const metricLabel = computed(() => metricOptions.find(m => m.key === metric.value)?.label || '')
const metricUnit = computed(() => metricOptions.find(m => m.key === metric.value)?.unit || '')
const metricColor = computed(() => metricOptions.find(m => m.key === metric.value)?.color || '')

// ---- Roots state ----
const allProvinceYears = computed(() => {
  const years = new Set()
  provinceData.forEach(p => p.years.forEach(y => years.add(y.year)))
  return Array.from(years).sort((a, b) => a - b)
})
const rootsYear = ref(latestProvinceYear('gardenArea'))

function setMetric(key) {
  metric.value = key
  const y = latestProvinceYear(key)
  if (y) rootsYear.value = y
}

// ---- Leaves state ----
const leavesYears = teaTypeData.map(d => d.year)
const leavesYear = ref(LATEST_EXPORT_YEAR)

// ---- Branches state ----
const branchesYears = countryData.map(d => d.year)
const branchesYear = ref(LATEST_EXPORT_YEAR)

// ---- Roots selected province ----
const selectedProvince = ref('云南省')

// ============================================================
//  Home view computeds
// ============================================================
const homeYear = latestFullYear()
const homeNat = getNational(homeYear)
const gardenArea = homeNat?.gardenArea ?? 0
const output = homeNat?.totalOutput ?? 0
const homeExportYearData = countryData.find(y => y.year === LATEST_EXPORT_YEAR)
const exportTotal = homeExportYearData
  ? homeExportYearData.countries.reduce((s, c) => s + c.value, 0)
  : 0

// ============================================================
//  中国各省面积常量表（单位：km²）
//  数据来源：中华人民共和国国家统计局《中国统计年鉴》公开行政区划面积数据
//  参考链接：https://www.stats.gov.cn/sj/tjnj/ （各省份土地面积/行政区划面积）
// ============================================================
const PROVINCE_AREAS = {
  '北京市': 16410,
  '天津市': 11966,
  '河北省': 188800,
  '山西省': 156700,
  '内蒙古自治区': 1183000,
  '辽宁省': 148000,
  '吉林省': 187400,
  '黑龙江省': 473000,
  '上海市': 6340,
  '江苏省': 107200,
  '浙江省': 105500,
  '安徽省': 140100,
  '福建省': 124000,
  '江西省': 166900,
  '山东省': 157900,
  '河南省': 167000,
  '湖北省': 185900,
  '湖南省': 211800,
  '广东省': 179800,
  '广西壮族自治区': 237600,
  '海南省': 35400,
  '重庆市': 82400,
  '四川省': 486000,
  '贵州省': 176200,
  '云南省': 394100,
  '西藏自治区': 1228400,
  '陕西省': 205600,
  '甘肃省': 425900,
  '青海省': 722300,
  '宁夏回族自治区': 66400,
  '新疆维吾尔自治区': 1664900,
  '台湾省': 36013,
  '香港特别行政区': 1114,
  '澳门特别行政区': 33,
}

// ============================================================
//  中国各省会/首府中心经纬度（用于气泡散点定位）
//  数据来源：公开地理坐标数据（WGS84 近似值，ECharts 坐标系适用）
// ============================================================
const PROVINCE_COORDS = {
  '北京市': [116.405285, 39.904989],
  '天津市': [117.200983, 39.084158],
  '河北省': [114.502461, 38.045474],
  '山西省': [112.549248, 37.857014],
  '内蒙古自治区': [111.75199, 40.841439],
  '辽宁省': [123.429096, 41.796767],
  '吉林省': [125.3245, 43.886841],
  '黑龙江省': [126.642464, 45.756967],
  '上海市': [121.472644, 31.231706],
  '江苏省': [118.767413, 32.041544],
  '浙江省': [120.153576, 30.287459],
  '安徽省': [117.283042, 31.86119],
  '福建省': [119.306239, 26.075302],
  '江西省': [115.892151, 28.676493],
  '山东省': [117.000923, 36.675807],
  '河南省': [113.665412, 34.757975],
  '湖北省': [114.298572, 30.584355],
  '湖南省': [112.982279, 28.19409],
  '广东省': [113.280637, 23.125178],
  '广西壮族自治区': [108.320004, 22.82402],
  '海南省': [110.330802, 20.031971],
  '重庆市': [106.504962, 29.533155],
  '四川省': [104.065735, 30.659462],
  '贵州省': [106.713478, 26.578343],
  '云南省': [102.712251, 25.040609],
  '西藏自治区': [91.132212, 29.660361],
  '陕西省': [108.948024, 34.263161],
  '甘肃省': [103.823557, 36.058039],
  '青海省': [101.778916, 36.623178],
  '宁夏回族自治区': [106.230909, 38.487222],
  '新疆维吾尔自治区': [87.617733, 43.792818],
  '台湾省': [121.509062, 25.044332],
  '香港特别行政区': [114.173355, 22.320048],
  '澳门特别行政区': [113.549132, 22.198951],
}

// ============================================================
//  Shared ECharts style fragments
// ============================================================
const tooltipBase = {
  backgroundColor: 'rgba(250,247,239,0.96)',
  borderColor: '#A8C18A',
  borderWidth: 1,
  textStyle: { color: '#3A4D38', fontSize: 12 },
  extraCssText: 'box-shadow: 0 2px 12px rgba(81,109,51,0.15); border-radius: 6px;',
}
const axisLineStyle = { lineStyle: { color: '#A8C18A' } }
const axisLabelStyle = { color: '#5A6655', fontSize: 11 }
const splitLineStyle = { lineStyle: { color: 'rgba(168,193,138,0.2)', type: 'dashed' } }

// ============================================================
//  Roots view computeds
// ============================================================
const rootsOverview = computed(() => {
  const nat = getNational(rootsYear.value)
  const prevNat = getNational(rootsYear.value - 1)
  const provinceCount = provinceData.filter(p => {
    const yd = p.years.find(y => y.year === rootsYear.value)
    return yd && yd[metric.value] > 0
  }).length
  const yoy = nat && prevNat && prevNat.totalOutput > 0
    ? ((nat.totalOutput - prevNat.totalOutput) / prevNat.totalOutput) * 100
    : null
  return {
    gardenArea: nat?.gardenArea ?? 0,
    totalOutput: nat?.totalOutput ?? 0,
    yoy,
    provinceCount,
  }
})

const rootsMapData = computed(() => {
  return provinceData
    .map(p => {
      const yd = p.years.find(y => y.year === rootsYear.value)
      const v = yd ? yd[metric.value] : null
      if (isMissingVal(v)) return { name: p.province, value: 0 }
      return { name: p.province, value: typeof v === 'number' ? v : Number(v) }
    })
    .filter(d => !isMissingVal(d.value) && d.value > 0)
})

const rootsMapOption = computed(() => {
  const data = rootsMapData.value

  // =================== 茶园面积 Tab：气泡图方案（geo 米色底图 + 散点） ===================
  if (metric.value === 'gardenArea') {
    // 计算覆盖率 & 组装散点数据（1千公顷 = 10 km²）
    const scatterList = []
    const coverageList = []
    let areaMax = 0
    data.forEach(d => {
      const areaKm2 = PROVINCE_AREAS[d.name]
      if (!areaKm2 || areaKm2 <= 0) return
      const coord = PROVINCE_COORDS[d.name]
      if (!coord) return
      const gardenKm2 = d.value * 10 // 千公顷 → km²
      const coverage = (gardenKm2 / areaKm2) * 100 // 覆盖率 %
      scatterList.push({
        name: d.name,
        // value 标准 3 元素：[lng, lat, coverage]；第2索引即 dimension=2 供 visualMap 染色
        value: [coord[0], coord[1], coverage],
        // 保留自定义属性供 tooltip / symbolSize 使用
        coverage,
        gardenArea: d.value,
      })
      coverageList.push(coverage)
      if (d.value > areaMax) areaMax = d.value
    })

    // 覆盖率最大值向上取整
    const coverageMaxRaw = coverageList.length ? Math.max(...coverageList) : 1
    const coverageMax = Math.max(1, Math.ceil(coverageMaxRaw))

    // 气泡大小映射（基于茶园面积绝对值，开方缩放使视觉更合理）
    const areaMaxRef = Math.max(areaMax, 1)
    const sizeMax = 24 // 最大气泡像素（整体调小，原 36）
    const sizeMin = 4  // 最小气泡像素（整体调小，原 6）

    return {
      tooltip: {
        ...tooltipBase,
        trigger: 'item',
        formatter: p => {
          if (p.componentType === 'geo') return `${p.name}<br/>（点击气泡查看省份详情）`
          const d = p.data
          if (!d || !d.gardenArea) return `${p.name}<br/>暂无数据`
          return `<b>${d.name}</b><br/>茶园面积：${fmt(d.gardenArea, 2)} 千公顷<br/>覆盖率：${fmt(d.coverage, 3)} %`
        },
      },
      geo: {
        map: 'china',
        roam: true,
        zoom: currentGeoZoom.value,
        label: { show: false },
        itemStyle: {
          areaColor: '#F7F4EB', // 统一米色底图
          borderColor: 'rgba(178,143,76,0.45)',
          borderWidth: 0.8,
        },
        emphasis: {
          label: { show: true, color: '#3A4D38', fontWeight: 700 },
          itemStyle: { areaColor: '#EFE9DA', borderColor: '#B28F4C', borderWidth: 1.2 },
        },
      },
      visualMap: {
        min: 0,
        max: coverageMax,
        left: 16,
        bottom: 24,
        text: [`${coverageMax}%`, '0%'],
        textStyle: { color: '#5A6655', fontSize: 10 },
        inRange: { color: ['#F0F4E6', '#C5D6AC', '#8BA667', '#5C7C3A', '#3A4D38'] },
        calculable: true,
        formatter: v => `${v.toFixed(1)}%`,
        show: true,
        dimension: 2, // ★ 核心修复：绑定 value[2]=coverage，避免误取经度导致全白
        seriesIndex: 0, // 只作用于散点系列，不影响 geo
      },
      series: [{
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        symbol: 'circle',
        // symbolSize 随地图缩放联动：zoom 越大气泡越大；除以 DEFAULT_GEO_ZOOM 保证初始视觉与以前一致
        symbolSize: (value, params) => {
          const area = params.data?.gardenArea || 0
          const ratio = Math.sqrt(area / areaMaxRef)
          const base = Math.max(sizeMin, sizeMin + (sizeMax - sizeMin) * ratio)
          const zoomFactor = currentGeoZoom.value / DEFAULT_GEO_ZOOM
          return base * zoomFactor
        },
        itemStyle: {
          borderColor: 'rgba(255,255,255,0.92)',
          borderWidth: 1,
          opacity: 0.9,
        },
        emphasis: {
          itemStyle: {
            borderColor: '#B28F4C',
            borderWidth: 2,
            opacity: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(92,124,58,0.35)',
          },
        },
        data: scatterList,
      }],
    }
  }

  // =================== 茶叶产量 Tab：保持原分级设色 choropleth ===================
  const values = data.map(d => d.value)
  const maxVal = values.length ? Math.max(...values) : 0
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'item',
      formatter: p => {
        if (p.value == null || isNaN(p.value)) return `${p.name}<br/>暂无数据`
        return `<b>${p.name}</b><br/>${metricLabel.value}：${fmt(p.value, 2)} ${metricUnit.value}`
      },
    },
    visualMap: {
      min: 0,
      max: maxVal || 1,
      left: 20,
      bottom: 30,
      text: ['高', '低'],
      textStyle: { color: '#5A6655', fontSize: 11 },
      inRange: { color: ['#F0F4E6', '#C5D6AC', '#8BA667', '#5C7C3A', '#3A4D38'] },
      calculable: true,
    },
    series: [{
      type: 'map',
      map: 'china',
      roam: true,
      zoom: currentGeoZoom.value,
      label: { show: false },
      emphasis: {
        label: { show: true, color: '#3A4D38', fontWeight: 700 },
        itemStyle: { areaColor: '#C8A155', borderColor: '#fff', borderWidth: 1.5 },
      },
      itemStyle: { areaColor: '#EDE6D3', borderColor: 'rgba(255,255,255,0.6)', borderWidth: 0.8 },
      data,
    }],
  }
})

const rootsProvinceDetail = computed(() => {
  const prov = getProvince(selectedProvince.value)
  if (!prov) return null
  const yd = prov.years.find(y => y.year === rootsYear.value)
  // 只保留有该指标值的年份（去除 0/null/NaN 的年份点）
  const filteredYears = []
  const filteredValues = []
  prov.years.forEach(y => {
    const v = y[metric.value]
    if (!isMissingVal(v)) {
      filteredYears.push(y.year)
      filteredValues.push(typeof v === 'number' ? v : Number(v))
    }
  })
  return {
    name: prov.province,
    gardenArea: yd?.gardenArea || 0,
    totalOutput: yd?.totalOutput || 0,
    metricValue: yd ? (isMissingVal(yd[metric.value]) ? 0 : (yd[metric.value] || 0)) : 0,
    years: filteredYears,
    values: filteredValues,
  }
})

const rootsProvinceTrendOption = computed(() => {
  const detail = rootsProvinceDetail.value
  if (!detail || !detail.years.length) return {}
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => {
        const v = ps[0]?.value
        return `${v.axisValue ?? ps[0]?.axisValue}年<br/>${metricLabel.value}：${fmt(v.value ?? v.data, 2)} ${metricUnit.value}`
      },
    },
    grid: { left: 48, right: 16, top: 16, bottom: 28 },
    xAxis: { type: 'category', data: detail.years, axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: { type: 'value', axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    series: [{
      type: 'line',
      data: detail.values,
      connectNulls: false,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: metricColor.value, width: 2.5 },
      itemStyle: { color: metricColor.value },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: metricColor.value + '55' },
          { offset: 1, color: metricColor.value + '08' },
        ]),
      },
    }],
  }
})

const rootsRankingOption = computed(() => {
  const data = rootsMapData.value
    .slice()
    .sort((a, b) => b.value - a.value)
    .slice(0, 10)
    .reverse()
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => `<b>${ps[0].name}</b><br/>${metricLabel.value}：${fmt(ps[0].value, 2)} ${metricUnit.value}`,
    },
    grid: { left: 90, right: 40, top: 10, bottom: 24 },
    xAxis: { type: 'value', axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    yAxis: { type: 'category', data: data.map(d => d.name), axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: metricColor.value + '88' },
            { offset: 1, color: metricColor.value },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barWidth: '60%',
      label: { show: true, position: 'right', color: '#5A6655', fontSize: 11, formatter: p => fmt(p.value, 1) },
    }],
  }
})

function onMapClick(params) {
  if (params.name && getProvince(params.name)) {
    selectedProvince.value = params.name
  }
}

// ============================================================
//  Leaves view computeds
// ============================================================
const leavesOverview = computed(() => {
  const yd = teaTypeData.find(d => d.year === leavesYear.value)
  const validTypes = yd ? yd.types.filter(t => !isMissingVal(t.value)) : []
  const totalExport = validTypes.reduce((s, t) => s + (Number(t.value) || 0), 0)
  const sorted = validTypes.slice().sort((a, b) => Number(b.value) - Number(a.value))
  const topType = sorted.length ? sorted[0].type : ''
  const typeCount = validTypes.length
  const latestNat = getNational(latestFullYear())
  return {
    totalExport,
    topType,
    typeCount,
    latestOutput: latestNat?.totalOutput ?? 0,
  }
})

const leavesPieOption = computed(() => {
  const yd = teaTypeData.find(d => d.year === leavesYear.value)
  if (!yd) return {}
  const data = yd.types
    .filter(t => !isMissingVal(t.value))
    .map(t => ({
      name: t.type,
      value: Number(t.value) || 0,
      itemStyle: { color: TEA_COLORS[t.type] || '#8A8270' },
    }))
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'item',
      formatter: p => `<b>${p.name}</b><br/>出口额：${fmt(p.value / 1e8, 2)} 亿元<br/>占比：${p.percent}%`,
    },
    legend: {
      bottom: 5,
      left: 'center',
      textStyle: { color: '#5A6655', fontSize: 11 },
      itemWidth: 12,
      itemHeight: 12,
    },
    series: [{
      type: 'pie',
      radius: ['42%', '72%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#FAF7EF', borderWidth: 2, borderRadius: 4 },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 11,
        color: '#3A4D38',
      },
      emphasis: {
        label: { fontSize: 13, fontWeight: 700 },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' },
      },
      data,
    }],
  }
})

const leavesTrendOption = computed(() => {
  const years = nationalData.map(d => d.year)
  const totalSeries = {
    name: '茶叶总产量',
    color: '#5C7C3A',
    data: nationalData.map(d => numOrNull(d.totalOutput)),
  }
  const greenSeries = {
    name: '绿茶',
    color: '#6F9150',
    data: nationalData.map(d => numOrNull(d.greenTea)),
  }
  const blackSeries = {
    name: '红茶',
    color: '#A8453A',
    data: nationalData.map(d => numOrNull(d.blackTea)),
  }
  const allSeries = [totalSeries, greenSeries, blackSeries].filter(s => arrHasAnyValue(s.data))
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => {
        let html = `<b>${ps[0]?.axisValue ?? ''}年</b>`
        ps.forEach(p => {
          if (p.value == null) return
          html += `<br/>${p.marker}${p.seriesName}：${fmt(p.value, 2)} 万吨`
        })
        return html
      },
    },
    legend: {
      top: 5,
      textStyle: { color: '#5A6655', fontSize: 11 },
      data: allSeries.map(s => s.name),
    },
    grid: { left: 48, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: years, axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: { type: 'value', name: '万吨', nameTextStyle: { color: '#5A6655', fontSize: 11 }, axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    series: allSeries.map(s => ({
      name: s.name,
      type: 'line',
      data: s.data,
      connectNulls: false,
      smooth: true,
      lineStyle: {
        color: s.color,
        width: s.name === '茶叶总产量' ? 2.5 : 2,
      },
      itemStyle: { color: s.color },
      areaStyle: s.name === '茶叶总产量' ? { color: 'rgba(92,124,58,0.12)' } : undefined,
    })),
  }
})

const leavesStackedOption = computed(() => {
  const yearRange = teaTypeData.filter(d => d.year >= 2015 && d.year <= 2024)
  const years = yearRange.map(d => d.year)
  const allTypes = TEA_ORDER.filter(t => t !== '其他')
  // 生成每个茶种的年度数据（0/空 → null，不参与堆叠绘制）
  const typedSeriesData = allTypes.map(type => {
    const data = yearRange.map(d => {
      const t = d.types.find(x => x.type === type)
      return t ? numOrNull(t.value) : null
    })
    return { type, data }
  }).filter(ts => arrHasAnyValue(ts.data))

  const types = typedSeriesData.map(s => s.type)

  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => {
        let html = `<b>${ps[0].axisValue}年</b>`
        ps.forEach(p => {
          if (p.value == null) return
          html += `<br/>${p.marker}${p.seriesName}：${fmt(p.value / 1e8, 2)} 亿元`
        })
        return html
      },
    },
    legend: {
      top: 5,
      textStyle: { color: '#5A6655', fontSize: 11 },
      data: types,
    },
    grid: { left: 56, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', boundaryGap: false, data: years, axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: {
      type: 'value',
      name: '亿元',
      nameTextStyle: { color: '#5A6655', fontSize: 11 },
      axisLine: axisLineStyle,
      axisLabel: { ...axisLabelStyle, formatter: v => (v / 1e8).toFixed(1) },
      splitLine: splitLineStyle,
    },
    series: typedSeriesData.map(ts => ({
      name: ts.type,
      type: 'line',
      stack: 'total',
      areaStyle: { opacity: 0.55, color: TEA_COLORS[ts.type] || '#8A8270' },
      lineStyle: { color: TEA_COLORS[ts.type] || '#8A8270', width: 1.5 },
      itemStyle: { color: TEA_COLORS[ts.type] || '#8A8270' },
      connectNulls: false,
      smooth: true,
      data: ts.data,
    })),
  }
})

const leavesTeaCards = computed(() => {
  const yd = teaTypeData.find(d => d.year === leavesYear.value)
  const valueMap = {}
  if (yd) yd.types.forEach(t => {
    if (!isMissingVal(t.value)) valueMap[t.type] = Number(t.value) || 0
  })
  // 只返回当前年份有非0/非空数据的茶种，其余从卡片中隐藏
  return TEA_ORDER
    .filter(t => t !== '其他')
    .filter(type => !isMissingVal(valueMap[type]))
    .map(type => ({
      type,
      ...TEA_INFO[type],
      color: TEA_COLORS[type] || '#8A8270',
      value: valueMap[type] || 0,
    }))
})

// ============================================================
//  Branches view computeds
// ============================================================
const branchesOverview = computed(() => {
  const yd = countryData.find(d => d.year === branchesYear.value)
  const pd = provinceExportData.find(d => d.year === branchesYear.value)
  const validCountries = yd ? yd.countries.filter(c => !isMissingVal(c.value)) : []
  const validProvinces = pd ? pd.provinces.filter(p => !isMissingVal(p.value)) : []
  const totalExport = validCountries.reduce((s, c) => s + (Number(c.value) || 0), 0)
  const sorted = validCountries.slice().sort((a, b) => Number(b.value) - Number(a.value))
  return {
    totalExport,
    topCountry: sorted.length ? sorted[0].name : '',
    countryCount: validCountries.length,
    provinceCount: validProvinces.length,
  }
})

const branchesSankeyOption = computed(() => {
  const yd = sankeyData.find(d => d.year === branchesYear.value)
  if (!yd) return {}
  // 只保留 value 有效（非 0/空）的连线
  const validLinks = yd.links
    .filter(l => !isMissingVal(l.value))
    .map(l => ({
      source: l.source,
      target: l.target,
      value: Number(l.value) || 0,
      lineStyle: { color: 'gradient', opacity: 0.35, curveness: 0.5 },
    }))
  // 只保留出现在有效 links 中的节点（避免孤立节点）
  const usedNames = new Set()
  validLinks.forEach(l => { usedNames.add(l.source); usedNames.add(l.target) })
  const validNodes = yd.nodes.filter(n => usedNames.has(n.name))
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'item',
      formatter: p => {
        if (p.dataType === 'edge') {
          return `${p.data.source} → ${p.data.target}<br/>出口额：${fmt(p.data.value / 1e8, 2)} 亿元`
        }
        return `<b>${p.name}</b>`
      },
    },
    series: [{
      type: 'sankey',
      left: 20,
      right: 120,
      top: 20,
      bottom: 20,
      nodeWidth: 16,
      nodeGap: 8,
      layoutIterations: 64,
      emphasis: { focus: 'adjacency' },
      data: validNodes.map(n => ({
        name: n.name,
        itemStyle: { color: n.category === 'province' ? '#5C7C3A' : '#C8A155' },
        label: { color: '#3A4D38', fontSize: 11 },
      })),
      links: validLinks,
      lineStyle: { curveness: 0.5 },
    }],
  }
})

const branchesCountryRankOption = computed(() => {
  const yd = countryData.find(d => d.year === branchesYear.value)
  if (!yd) return {}
  const sorted = yd.countries
    .filter(c => !isMissingVal(c.value))
    .map(c => ({ ...c, value: Number(c.value) || 0 }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10)
    .reverse()
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => `<b>${ps[0].name}</b><br/>出口额：${fmt(ps[0].value, 2)} 亿元`,
    },
    grid: { left: 100, right: 50, top: 10, bottom: 24 },
    xAxis: { type: 'value', axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    yAxis: { type: 'category', data: sorted.map(c => c.name), axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    series: [{
      type: 'bar',
      data: sorted.map(c => ({
        value: c.value / 1e8,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#C8A15588' },
            { offset: 1, color: '#C8A155' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barWidth: '60%',
      label: { show: true, position: 'right', color: '#5A6655', fontSize: 11, formatter: p => p.value.toFixed(2) },
    }],
  }
})

const branchesTrendOption = computed(() => {
  // 2026年未结束、数据不完整，从趋势图中剔除（不进x轴也不绘制该年点）
  const trend = countryData
    .filter(d => d.year < 2026)
    .map(d => {
      const total = d.countries.reduce((s, c) => {
        if (isMissingVal(c.value)) return s
        return s + (Number(c.value) || 0)
      }, 0)
      // 当年没有任何有效数据 → 返回 null，折线断档
      const noValid = d.countries.length === 0 || d.countries.every(c => isMissingVal(c.value))
      return {
        year: d.year,
        total: noValid ? null : total,
      }
    })
  const validItems = trend.filter(d => d.total !== null)
  const maxItem = validItems.length
    ? validItems.reduce((m, d) => (d.total > m.total ? d : m), validItems[0])
    : null
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => {
        const v = ps[0]?.value
        if (v == null) return `${ps[0]?.axisValue ?? ''}年<br/>暂无出口数据`
        return `<b>${ps[0]?.axisValue ?? ''}年</b><br/>出口总额：${fmt(v, 2)} 亿元`
      },
    },
    grid: { left: 52, right: 30, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: trend.map(d => d.year), axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: {
      type: 'value',
      name: '亿元',
      nameTextStyle: { color: '#5A6655', fontSize: 11 },
      axisLine: axisLineStyle,
      axisLabel: axisLabelStyle,
      splitLine: splitLineStyle,
    },
    series: [{
      type: 'line',
      data: trend.map(d => d.total == null ? null : d.total / 1e8),
      connectNulls: false,
      smooth: true,
      symbol: 'circle',
      symbolSize: 7,
      lineStyle: { color: '#6B4423', width: 2.5 },
      itemStyle: { color: '#6B4423' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(107,68,35,0.25)' },
          { offset: 1, color: 'rgba(107,68,35,0.03)' },
        ]),
      },
      markPoint: maxItem ? {
        symbol: 'pin',
        symbolSize: 48,
        data: [{ name: '最大值', value: maxItem.total / 1e8, xAxis: maxItem.year, yAxis: maxItem.total / 1e8 }],
        itemStyle: { color: '#B28F4C' },
        label: { color: '#fff', fontSize: 10, formatter: p => p.value.toFixed(1) },
      } : undefined,
    }],
  }
})

const branchesProvinceShares = computed(() => {
  const yd = provinceExportData.find(d => d.year === branchesYear.value)
  if (!yd) return []
  const validProvinces = yd.provinces
    .filter(p => !isMissingVal(p.value))
    .map(p => ({ ...p, value: Number(p.value) || 0 }))
  const total = validProvinces.reduce((s, p) => s + p.value, 0)
  return validProvinces
    .slice()
    .sort((a, b) => b.value - a.value)
    .slice(0, 8)
    .map(p => ({
      name: p.name,
      value: p.value,
      valueYi: p.value / 1e8,
      pct: total > 0 ? (p.value / total) * 100 : 0,
    }))
})

// ============================================================
//  Lifecycle: load China GeoJSON and register map
// ============================================================
function onIntroDone() {
  introDone.value = true
}

onMounted(async () => {
  try {
    const res = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const geo = await res.json()
    echarts.registerMap('china', geo)
    mapReady.value = true
  } catch (e) {
    console.warn('China GeoJSON 加载失败:', e)
    mapReady.value = true
  }
})
</script>

<style scoped>
/* ============================================================
   Chapter 5 · 今日茶境  (Redesign: Tree + Phone waterfall)
   ============================================================ */
.chapter-5 {
  position: relative;
  background: var(--c-paper-2);
}

.map-fullscreen.ch5-redesign {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
  overflow: hidden;
  padding: 0;
  display: grid;
  grid-template-columns: minmax(580px, 1.1fr) minmax(360px, 440px);
  gap: 16px;
  padding: 1.6rem 3rem 1.6rem 1rem;
}
.map-fullscreen.ch5-redesign.show {
  opacity: 1;
}

/* ============ LEFT · Tea tree ============ */
.ch5-left {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.ch5-tree-scene.single-tree {
  background: linear-gradient(160deg, rgba(245,240,228,0.6) 0%, rgba(220,228,200,0.55) 100%);
  border-radius: 24px;
  border: 1px solid rgba(165,163,122,0.35);
  overflow: hidden;
  box-shadow:
    0 10px 36px rgba(81, 109, 51, 0.14),
    inset 0 0 120px rgba(255,255,255,0.35);
  width: 100%;
  max-width: 640px;
  aspect-ratio: 600 / 820;
  max-height: calc(100vh - 60px - 3.2rem);
}

.tree-svg {
  display: block;
  width: 100%;
  height: 100%;
}

.tea-tree.single-big-tree {
  animation: tree-sway-single 6s ease-in-out infinite;
  transform-origin: 300px 630px;
  transform-box: view-box;
  filter: drop-shadow(0 12px 20px rgba(70, 90, 40, 0.22));
}

@keyframes tree-sway-single {
  0%, 100% { transform: rotate(0deg); }
  30% { transform: rotate(0.3deg); }
  70% { transform: rotate(-0.3deg); }
}

/* ---------- Click zones ---------- */
.click-zone {
  transition: filter 0.25s ease;
}
.click-zone.hover {
  filter: drop-shadow(0 0 10px rgba(255,255,255,0.7));
}
.click-zone.active {
  filter: drop-shadow(0 0 14px rgba(255,255,255,0.95));
}

/* 扩散圆动效 */
.ripple {
  transform-box: fill-box;
  transform-origin: center;
  opacity: 0;
}
.ripple-1 { animation: ripple-expand 2.4s ease-out 0s infinite; }
.ripple-2 { animation: ripple-expand 2.4s ease-out 0.8s infinite; }
.ripple-3 { animation: ripple-expand 2.4s ease-out 1.6s infinite; }

@keyframes ripple-expand {
  0% {
    opacity: 0.9;
    transform: scale(0.6);
  }
  70% {
    opacity: 0.35;
  }
  100% {
    opacity: 0;
    transform: scale(3.8);
  }
}

/* active时加速 + 更亮 */
.click-zone.active .ripple-1 { animation-duration: 1.6s; }
.click-zone.active .ripple-2 { animation-duration: 1.6s; }
.click-zone.active .ripple-3 { animation-duration: 1.6s; }

.zone-tag text {
  font-family: var(--font-huiwen);
  pointer-events: none;
}

/* ============ RIGHT · Phone / Tablet frame ============ */
.ch5-right {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.phone-frame {
  width: 100%;
  max-width: 440px;
  height: calc(100vh - 60px - 3.2rem);
  max-height: 880px;
  background: #1a1a1a;
  border-radius: 44px;
  padding: 12px;
  box-shadow:
    0 30px 60px rgba(0, 0, 0, 0.35),
    0 0 0 2px #2a2a2a,
    inset 0 0 0 1px #000;
  position: relative;
  display: flex;
  flex-direction: column;
  transition: all 0.5s ease;
}

/* 不同面板对应颜色边框发光 */
.phone-frame.panel-roots   { box-shadow: 0 30px 60px rgba(0,0,0,0.35), 0 0 0 2px #2a2a2a, 0 0 28px rgba(178,143,76,0.35), inset 0 0 0 1px #000; }
.phone-frame.panel-leaves  { box-shadow: 0 30px 60px rgba(0,0,0,0.35), 0 0 0 2px #2a2a2a, 0 0 28px rgba(92,124,58,0.35),  inset 0 0 0 1px #000; }
.phone-frame.panel-branches{ box-shadow: 0 30px 60px rgba(0,0,0,0.35), 0 0 0 2px #2a2a2a, 0 0 28px rgba(107,68,35,0.35), inset 0 0 0 1px #000; }

/* 顶部刘海 */
.phone-notch {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 28px;
  background: #0a0a0a;
  border-radius: 18px;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.notch-speaker {
  width: 40px; height: 6px;
  background: #222;
  border-radius: 4px;
}
.notch-cam {
  width: 12px; height: 12px;
  background: radial-gradient(circle at 35% 35%, #4a5a6a 0%, #0a0a0a 70%);
  border-radius: 50%;
}

/* 状态栏 */
.phone-statusbar {
  height: 44px;
  padding: 0 22px 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  background: transparent;
  border-top-left-radius: 32px;
  border-top-right-radius: 32px;
  flex-shrink: 0;
  z-index: 10;
  position: relative;
}
.sb-time { min-width: 40px; }
.sb-title {
  font: 600 14px/1 var(--font-huiwen);
  letter-spacing: 0.08em;
  color: rgba(255,255,255,0.92);
  text-shadow: 0 0 6px rgba(0,0,0,0.4);
}
.sb-signal { font-size: 10px; opacity: 0.75; }

/* 屏幕内部 */
.phone-screen {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: linear-gradient(180deg, #F4F0E3 0%, #EDE8D4 100%);
  border-radius: 32px;
  padding: 10px 14px 18px;
  position: relative;
  scrollbar-width: thin;
  scrollbar-color: #B8B484 transparent;
  --serif: var(--font-huiwen);
  --sans: var(--font-huiwen);
}

.phone-screen::-webkit-scrollbar { width: 4px; }
.phone-screen::-webkit-scrollbar-thumb { background: #B8B484; border-radius: 2px; }

/* 底部 home indicator */
.phone-homebar {
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.phone-homebar::after {
  content: "";
  width: 120px;
  height: 5px;
  background: #555;
  border-radius: 3px;
}

/* ============================================================
   Waterfall panels · 瀑布流排布
   ============================================================ */
.waterfall-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: fadeSlideUp 0.45s ease;
}

@keyframes fadeSlideUp {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Controls 小控件 */
.wf-controls.wf-ctrl-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 6px 2px 4px;
}

/* 小版 Controls */
.ch5-metric-toggle.small {
  display: flex;
  gap: 0;
  border: 1px solid rgba(165,163,122,0.55);
  border-radius: 7px;
  overflow: hidden;
  background: rgba(255,255,255,0.7);
}
.ch5-metric-toggle.small .toggle-btn {
  padding: 4px 8px;
  font-size: 11px;
  letter-spacing: 0;
  border: none;
}
.ch5-metric-toggle.small .toggle-btn:not(:last-child) {
  border-right: 1px solid rgba(165,163,122,0.4);
}

.ch5-year-slider.small {
  display: flex;
  align-items: center;
  gap: 6px;
}
.ch5-year-slider.small .slider-input {
  width: 120px;
  height: 4px;
}
.ch5-year-slider.small .slider-input::-webkit-slider-thumb {
  width: 14px; height: 14px;
}
.ch5-year-slider.small .slider-value {
  font-size: 13px;
  min-width: 36px;
}

.ch5-year-select.small .select-input {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 6px;
}
.ch5-year-select.small .slider-label { display: none; }

/* ============ 概览 grid 手机版 ============ */
.wf-overview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.ch5-overview-card.small-card {
  background: linear-gradient(135deg, rgba(250,247,239,0.92) 0%, rgba(245,241,232,0.92) 100%);
  border: 1px solid rgba(165,163,122,0.35);
  border-radius: 12px;
  padding: 10px 12px;
  box-shadow: 0 2px 8px rgba(81,109,51,0.06);
}
.ch5-overview-card.small-card .ov-label {
  font-size: 11px;
  margin-bottom: 4px;
  letter-spacing: 0.03em;
}
.ch5-overview-card.small-card .ov-unit { font-size: 10px; }
.ch5-overview-card.small-card .ch5-stat-num {
  font-size: 1.25rem;
}

/* ============ 通用 card 手机版 ============ */
.ch5-card.small-card {
  background: linear-gradient(135deg, rgba(250,247,239,0.95) 0%, rgba(245,241,232,0.95) 100%);
  border: 1px solid rgba(165,163,122,0.35);
  border-radius: 14px;
  padding: 10px 12px 12px;
  box-shadow: 0 2px 10px rgba(81,109,51,0.06);
}

.card-title-sm {
  font: 600 13px/1 var(--font-huiwen);
  color: var(--c-olive);
  letter-spacing: 0.04em;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(165,163,122,0.4);
}

.chart-container { width: 100%; }

.ch5-map-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  font: 400 12px/1 var(--sans);
  color: var(--muted);
}

.empty-hint.small {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
  font-size: 12px;
  color: var(--muted);
}

/* province detail 小版 */
.province-detail-body.small {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.province-mini-stats.small {
  display: flex;
  gap: 6px;
}
.province-mini-stats.small .mini-stat {
  padding: 6px 4px;
  border-radius: 6px;
  border: 1px solid rgba(165,163,122,0.3);
}
.province-mini-stats.small .mini-label { font-size: 10px; margin-bottom: 2px; }
.province-mini-stats.small .mini-val { font-size: 12px; }
.province-mini-stats.small .mini-val small { font-size: 9px; }

/* 图表行 */
.wf-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

/* ============ 叶片茶种卡片 小版 ============ */
.ch5-tea-cards.small-wrap {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.ch5-tea-card.small {
  --tea-color: var(--c-olive);
  background: linear-gradient(135deg, rgba(250,247,239,0.95) 0%, rgba(245,241,232,0.95) 100%);
  border: 1px solid rgba(165,163,122,0.3);
  border-top: 3px solid var(--tea-color);
  border-radius: 10px;
  padding: 8px 10px;
}
.ch5-tea-card.small .tea-card-icon { font-size: 16px; }
.ch5-tea-card.small .tea-card-name { font-size: 13px; }
.ch5-tea-card.small .tea-card-en { font-size: 10px; }
.ch5-tea-card.small .tea-card-desc { font-size: 11px; line-height: 1.5; margin: 0 0 4px; }
.ch5-tea-card.small .tea-card-val { padding-top: 4px; }
.ch5-tea-card.small .val-num { font-size: 14px; }
.ch5-tea-card.small .val-unit { font-size: 10px; }

/* ============ 枝条 省份占比 小版 ============ */
.ch5-province-shares.small-wrap { margin-top: 2px; }
.ch5-province-shares.small-wrap .shares-title {
  font-size: 13px;
  margin-bottom: 8px;
}
.shares-grid.small {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ch5-share-card.small {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, rgba(250,247,239,0.95) 0%, rgba(245,241,232,0.95) 100%);
  border: 1px solid rgba(165,163,122,0.3);
  border-radius: 8px;
  padding: 6px 8px;
}
.ch5-share-card.small .share-rank {
  width: 22px; height: 22px;
  font-size: 11px;
}
.ch5-share-card.small .share-name { font-size: 12px; }
.ch5-share-card.small .share-val { font-size: 10px; margin-bottom: 2px; }
.ch5-share-card.small .share-bar-wrap { height: 4px; }

/* ============================================================
   响应式：窄屏时上下堆叠
   ============================================================ */
@media (max-width: 1100px) {
  .map-fullscreen.ch5-redesign {
    grid-template-columns: 1fr;
    overflow-y: auto;
    gap: 16px;
    padding: 1rem 1.2rem 2rem;
  }
  .ch5-tree-scene.single-tree {
    max-height: 560px;
    margin: 0 auto;
  }
  .phone-frame {
    max-height: 760px;
    margin: 0 auto;
  }
}
</style>
