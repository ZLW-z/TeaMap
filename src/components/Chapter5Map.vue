<template>
  <section class="chapter chapter-5" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="第 五 章"
      title="今日茶境"
      desc="以茶树喻产业：根系深扎产区沃土，叶片舒展茶种格局，枝条伸向海外流向。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
    <!-- Tab navigation -->
    <nav class="ch5-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['ch5-tab', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </nav>

    <!-- ============================== Home view ============================== -->
    <div v-show="activeTab === 'home'" class="ch5-view ch5-view-home">
      <div class="ch5-tree-scene">
        <svg viewBox="0 0 1200 760" class="tree-svg" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#F7F4EB" />
              <stop offset="40%" stop-color="#E8E4D0" />
              <stop offset="75%" stop-color="#D8DCC0" />
              <stop offset="100%" stop-color="#C5D6AC" />
            </linearGradient>
            <linearGradient id="groundGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#C3C19A" />
              <stop offset="30%" stop-color="#A5A37A" />
              <stop offset="100%" stop-color="#6B5D3A" />
            </linearGradient>
            <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="rgba(255,240,200,0.6)" />
              <stop offset="100%" stop-color="rgba(255,240,200,0)" />
            </radialGradient>
          </defs>

          <!-- Sky -->
          <rect x="0" y="0" width="1200" height="490" fill="url(#skyGrad)" />
          <!-- Sun glow -->
          <circle cx="950" cy="120" r="100" fill="url(#sunGlow)" />
          <circle cx="950" cy="120" r="35" fill="rgba(255,235,180,0.5)" />
          <!-- Ground -->
          <rect x="0" y="485" width="1200" height="275" fill="url(#groundGrad)" />
          <!-- Ground line -->
          <path d="M0,488 Q300,475 600,488 T1200,488" stroke="#8a8478" stroke-width="1" fill="none" opacity="0.4" />

          <!-- ===== Tree 1 (left, smaller) ===== -->
          <g class="tea-tree tree-1" style="transform-origin: 250px 490px;">
            <image :href="TREE_IMG_URL" x="150" y="220" width="220" height="280" preserveAspectRatio="xMidYEnd meet" />
          </g>

          <!-- ===== Tree 2 (center, largest) ===== -->
          <g class="tea-tree tree-2" style="transform-origin: 600px 490px;">
            <image :href="TREE_IMG_URL" x="430" y="150" width="340" height="360" preserveAspectRatio="xMidYEnd meet" />
          </g>

          <!-- ===== Tree 3 (right, medium) ===== -->
          <g class="tea-tree tree-3" style="transform-origin: 950px 490px;">
            <image :href="TREE_IMG_URL" x="830" y="180" width="260" height="330" preserveAspectRatio="xMidYEnd meet" />
          </g>

          <!-- Floating leaves decoration -->
          <g class="floating-leaves">
            <ellipse cx="400" cy="100" rx="8" ry="5" fill="#7A9A55" opacity="0.5" class="float-leaf fl-1" />
            <ellipse cx="800" cy="80" rx="7" ry="4" fill="#6F9150" opacity="0.5" class="float-leaf fl-2" />
            <ellipse cx="500" cy="60" rx="6" ry="4" fill="#7A9A55" opacity="0.4" class="float-leaf fl-3" />
            <ellipse cx="700" cy="120" rx="7" ry="5" fill="#6F9150" opacity="0.4" class="float-leaf fl-4" />
          </g>

          <!-- ===== Interactive zone: Leaves (top) ===== -->
          <g class="zone-group" @mouseenter="hoveredZone = 'leaves'" @mouseleave="hoveredZone = null" @click="activeTab = 'leaves'">
            <rect x="0" y="20" width="1200" height="270" :class="['zone-rect', { 'zone-active': hoveredZone === 'leaves' }]" rx="8" />
            <g class="zone-label" transform="translate(60, 55)">
              <rect x="0" y="0" width="210" height="56" rx="10" :style="{ fill: hoveredZone === 'leaves' ? 'rgba(92,124,58,0.92)' : 'rgba(247,244,235,0.88)' }" />
              <text x="16" y="24" :style="{ fill: hoveredZone === 'leaves' ? '#F7F4EB' : '#5C7C3A', 'font-size': '14px', 'font-weight': 700 }">叶片 · 茶种结构</text>
              <text x="16" y="46" :style="{ fill: hoveredZone === 'leaves' ? '#EFE9DA' : '#4a4a40', 'font-size': '20px', 'font-weight': 900, 'font-family': 'serif' }">{{ fmt(output, 2) }} 万吨</text>
            </g>
            <text x="1170" y="50" text-anchor="end" :style="{ fill: '#A5A37A', 'font-size': '12px', 'letter-spacing': '0.15em' }">点击进入 →</text>
          </g>

          <!-- ===== Interactive zone: Branches (middle) ===== -->
          <g class="zone-group" @mouseenter="hoveredZone = 'branches'" @mouseleave="hoveredZone = null" @click="activeTab = 'branches'">
            <rect x="0" y="290" width="1200" height="210" :class="['zone-rect', { 'zone-active': hoveredZone === 'branches' }]" rx="8" />
            <g class="zone-label" transform="translate(60, 440)">
              <rect x="0" y="0" width="210" height="56" rx="10" :style="{ fill: hoveredZone === 'branches' ? 'rgba(107,68,35,0.92)' : 'rgba(247,244,235,0.88)' }" />
              <text x="16" y="24" :style="{ fill: hoveredZone === 'branches' ? '#F7F4EB' : '#6B4423', 'font-size': '14px', 'font-weight': 700 }">枝条 · 出口流向</text>
              <text x="16" y="46" :style="{ fill: hoveredZone === 'branches' ? '#EFE9DA' : '#4a4a40', 'font-size': '20px', 'font-weight': 900, 'font-family': 'serif' }">{{ fmt(exportTotal / 1e8, 2) }} 亿元</text>
            </g>
          </g>

          <!-- ===== Interactive zone: Roots (bottom) ===== -->
          <g class="zone-group" @mouseenter="hoveredZone = 'roots'" @mouseleave="hoveredZone = null" @click="activeTab = 'roots'">
            <rect x="0" y="500" width="1200" height="240" :class="['zone-rect', { 'zone-active': hoveredZone === 'roots' }]" rx="8" />
            <g class="zone-label" transform="translate(60, 680)">
              <rect x="0" y="0" width="210" height="56" rx="10" :style="{ fill: hoveredZone === 'roots' ? 'rgba(178,143,76,0.92)' : 'rgba(247,244,235,0.88)' }" />
              <text x="16" y="24" :style="{ fill: hoveredZone === 'roots' ? '#F7F4EB' : '#B28F4C', 'font-size': '14px', 'font-weight': 700 }">根系 · 生产根基</text>
              <text x="16" y="46" :style="{ fill: hoveredZone === 'roots' ? '#EFE9DA' : '#4a4a40', 'font-size': '20px', 'font-weight': 900, 'font-family': 'serif' }">{{ fmt(gardenArea, 2) }} 千公顷</text>
            </g>
          </g>
        </svg>
      </div>

      <!-- Zone cards -->
      <div class="ch5-zone-cards">
        <div class="ch5-zone-card" :style="{ '--zone-color': '#B28F4C' }" @click="activeTab = 'roots'">
          <div class="zone-card-top">
            <span class="zone-card-icon">🌱</span>
            <span class="zone-card-title">根系 / 生产根基</span>
          </div>
          <div class="zone-card-stat">
            <span class="ch5-stat-num">{{ fmt(gardenArea, 2) }}</span>
            <span class="zone-card-unit">千公顷 · 茶园面积</span>
          </div>
        </div>
        <div class="ch5-zone-card" :style="{ '--zone-color': '#5C7C3A' }" @click="activeTab = 'leaves'">
          <div class="zone-card-top">
            <span class="zone-card-icon">🍃</span>
            <span class="zone-card-title">叶片 / 茶种结构</span>
          </div>
          <div class="zone-card-stat">
            <span class="ch5-stat-num">{{ fmt(output, 2) }}</span>
            <span class="zone-card-unit">万吨 · 茶叶产量</span>
          </div>
        </div>
        <div class="ch5-zone-card" :style="{ '--zone-color': '#6B4423' }" @click="activeTab = 'branches'">
          <div class="zone-card-top">
            <span class="zone-card-icon">🌐</span>
            <span class="zone-card-title">枝条 / 出口流向</span>
          </div>
          <div class="zone-card-stat">
            <span class="ch5-stat-num">{{ fmt(exportTotal / 1e8, 2) }}</span>
            <span class="zone-card-unit">亿元 · 出口总额</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================== Roots view ============================== -->
    <div v-show="activeTab === 'roots'" class="ch5-view ch5-view-roots">
      <div class="ch5-controls">
        <div class="ch5-metric-toggle">
          <button
            v-for="m in metricOptions"
            :key="m.key"
            :class="['toggle-btn', { active: metric === m.key }]"
            :style="metric === m.key ? { background: m.color, borderColor: m.color } : {}"
            @click="setMetric(m.key)"
          >{{ m.label }}</button>
        </div>
        <div class="ch5-year-slider">
          <span class="slider-label">年份</span>
          <input type="range" :min="allProvinceYears[0]" :max="allProvinceYears[allProvinceYears.length - 1]" step="1" v-model.number="rootsYear" class="slider-input" />
          <span class="slider-value">{{ rootsYear }}</span>
        </div>
      </div>

      <div class="ch5-overview-grid">
        <div class="ch5-overview-card">
          <div class="ov-label">全国茶园面积</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ fmt(rootsOverview.gardenArea, 2) }}</span><span class="ov-unit">千公顷</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">全国茶叶产量</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ fmt(rootsOverview.totalOutput, 2) }}</span><span class="ov-unit">万吨</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">产量同比</div>
          <div class="ov-value">
            <span class="ch5-stat-num" :style="{ color: rootsOverview.yoy >= 0 ? '#5C7C3A' : '#A8453A' }">
              {{ rootsOverview.yoy !== null ? (rootsOverview.yoy >= 0 ? '+' : '') + rootsOverview.yoy.toFixed(2) + '%' : '—' }}
            </span>
          </div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">统计省份数</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ rootsOverview.provinceCount }}</span><span class="ov-unit">个</span></div>
        </div>
      </div>

      <div class="ch5-roots-main">
        <div class="ch5-card ch5-map-panel">
          <div class="card-title">{{ metricLabel }}分布 · {{ rootsYear }}年</div>
          <div class="chart-container chart-map">
            <div v-if="!mapReady" class="ch5-map-loading">地图加载中…</div>
            <EChart v-else :option="rootsMapOption" @click="onMapClick" />
          </div>
        </div>
        <div class="ch5-card ch5-province-detail">
          <div class="card-title">{{ selectedProvince }} · 详情</div>
          <div v-if="rootsProvinceDetail" class="province-detail-body">
            <div class="province-mini-stats">
              <div class="mini-stat">
                <span class="mini-label">茶园面积</span>
                <span class="mini-val">{{ fmt(rootsProvinceDetail.gardenArea, 2) }} <small>千公顷</small></span>
              </div>
              <div class="mini-stat">
                <span class="mini-label">茶叶产量</span>
                <span class="mini-val">{{ fmt(rootsProvinceDetail.totalOutput, 2) }} <small>万吨</small></span>
              </div>
              <div class="mini-stat">
                <span class="mini-label">{{ metricLabel }}</span>
                <span class="mini-val" :style="{ color: metricColor }">{{ fmt(rootsProvinceDetail.metricValue, 2) }} <small>{{ metricUnit }}</small></span>
              </div>
            </div>
            <div class="chart-container chart-province-trend">
              <EChart :option="rootsProvinceTrendOption" />
            </div>
          </div>
          <div v-else class="empty-hint">点击地图选择省份</div>
        </div>
      </div>

      <div class="ch5-card ch5-ranking-panel">
        <div class="card-title">{{ metricLabel }} TOP 15 · {{ rootsYear }}年</div>
        <div class="chart-container chart-ranking">
          <EChart :option="rootsRankingOption" />
        </div>
      </div>
    </div>

    <!-- ============================== Leaves view ============================== -->
    <div v-show="activeTab === 'leaves'" class="ch5-view ch5-view-leaves">
      <div class="ch5-controls">
        <div class="ch5-year-select">
          <span class="slider-label">出口年份</span>
          <select v-model.number="leavesYear" class="select-input">
            <option v-for="y in leavesYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>

      <div class="ch5-overview-grid">
        <div class="ch5-overview-card">
          <div class="ov-label">出口总额</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ fmt(leavesOverview.totalExport / 1e8, 2) }}</span><span class="ov-unit">亿元</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">第一大出口茶种</div>
          <div class="ov-value"><span class="ch5-stat-num" :style="{ fontSize: '1.3rem' }">{{ leavesOverview.topType || '—' }}</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">茶种类别数</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ leavesOverview.typeCount }}</span><span class="ov-unit">类</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">最新茶叶总产量</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ fmt(leavesOverview.latestOutput, 2) }}</span><span class="ov-unit">万吨</span></div>
        </div>
      </div>

      <div class="ch5-charts-row">
        <div class="ch5-card">
          <div class="card-title">茶种出口结构 · {{ leavesYear }}年</div>
          <div class="chart-container chart-pie">
            <EChart :option="leavesPieOption" />
          </div>
        </div>
        <div class="ch5-card">
          <div class="card-title">全国茶叶产量趋势</div>
          <div class="chart-container chart-trend">
            <EChart :option="leavesTrendOption" />
          </div>
        </div>
      </div>

      <div class="ch5-card">
        <div class="card-title">茶种出口演变 2015—2024</div>
        <div class="chart-container chart-stacked">
          <EChart :option="leavesStackedOption" />
        </div>
      </div>

      <div class="ch5-tea-cards">
        <div
          v-for="card in leavesTeaCards"
          :key="card.type"
          class="ch5-tea-card"
          :style="{ '--tea-color': card.color }"
        >
          <div class="tea-card-header">
            <span class="tea-card-icon">{{ card.icon }}</span>
            <div class="tea-card-titles">
              <span class="tea-card-name">{{ card.type }}</span>
              <span class="tea-card-en">{{ card.en }}</span>
            </div>
          </div>
          <p class="tea-card-desc">{{ card.desc }}</p>
          <div class="tea-card-val" v-if="card.value > 0">
            <span class="val-num">{{ fmt(card.value / 1e8, 2) }}</span>
            <span class="val-unit">亿元</span>
          </div>
          <div class="tea-card-val" v-else>
            <span class="val-num muted">—</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================== Branches view ============================== -->
    <div v-show="activeTab === 'branches'" class="ch5-view ch5-view-branches">
      <div class="ch5-controls">
        <div class="ch5-year-select">
          <span class="slider-label">出口年份</span>
          <select v-model.number="branchesYear" class="select-input">
            <option v-for="y in branchesYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>

      <div class="ch5-overview-grid">
        <div class="ch5-overview-card">
          <div class="ov-label">出口总额</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ fmt(branchesOverview.totalExport / 1e8, 2) }}</span><span class="ov-unit">亿元</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">第一大目的地</div>
          <div class="ov-value"><span class="ch5-stat-num" :style="{ fontSize: '1.3rem' }">{{ branchesOverview.topCountry || '—' }}</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">出口目的地数</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ branchesOverview.countryCount }}</span><span class="ov-unit">个</span></div>
        </div>
        <div class="ch5-overview-card">
          <div class="ov-label">出口注册省份数</div>
          <div class="ov-value"><span class="ch5-stat-num">{{ branchesOverview.provinceCount }}</span><span class="ov-unit">个</span></div>
        </div>
      </div>

      <div class="ch5-card">
        <div class="card-title">省份 → 目的地 桑基图 · {{ branchesYear }}年</div>
        <div class="chart-container chart-sankey">
          <EChart :option="branchesSankeyOption" />
        </div>
      </div>

      <div class="ch5-charts-row">
        <div class="ch5-card">
          <div class="card-title">TOP 15 目的地 · {{ branchesYear }}年</div>
          <div class="chart-container chart-country-rank">
            <EChart :option="branchesCountryRankOption" />
          </div>
        </div>
        <div class="ch5-card">
          <div class="card-title">出口总额趋势</div>
          <div class="chart-container chart-branch-trend">
            <EChart :option="branchesTrendOption" />
          </div>
        </div>
      </div>

      <div class="ch5-province-shares">
        <div class="shares-title">出口省份占比 TOP 8 · {{ branchesYear }}年</div>
        <div class="shares-grid">
          <div
            v-for="(s, i) in branchesProvinceShares"
            :key="s.name"
            class="ch5-share-card"
          >
            <div class="share-rank" :style="{ background: i < 3 ? 'var(--c-gold)' : 'var(--c-beige)' }">{{ i + 1 }}</div>
            <div class="share-info">
              <div class="share-name">{{ s.name }}</div>
              <div class="share-val">{{ fmt(s.valueYi, 2) }} 亿元 · {{ s.pct.toFixed(1) }}%</div>
              <div class="share-bar-wrap">
                <div class="share-bar" :style="{ width: s.pct + '%', background: 'var(--c-olive-mid)' }"></div>
              </div>
            </div>
          </div>
        </div>
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

// ---- Tab system ----
const tabs = [
  { key: 'home', label: '茶树全景', icon: '🌳' },
  { key: 'roots', label: '根系·生产', icon: '🌱' },
  { key: 'leaves', label: '叶片·茶种', icon: '🍃' },
  { key: 'branches', label: '枝条·出口', icon: '🌐' },
]
const activeTab = ref('home')

// ---- Shared refs ----
const sectionEl = ref(null)
const hoveredZone = ref(null)
const mapReady = ref(false)
const introDone = ref(false)

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
      return { name: p.province, value: yd ? (yd[metric.value] || 0) : 0 }
    })
    .filter(d => d.value > 0)
})

const rootsMapOption = computed(() => {
  const data = rootsMapData.value
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
      zoom: 1.15,
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
  return {
    name: prov.province,
    gardenArea: yd?.gardenArea || 0,
    totalOutput: yd?.totalOutput || 0,
    metricValue: yd ? (yd[metric.value] || 0) : 0,
    years: prov.years.map(y => y.year),
    values: prov.years.map(y => y[metric.value] || 0),
  }
})

const rootsProvinceTrendOption = computed(() => {
  const detail = rootsProvinceDetail.value
  if (!detail) return {}
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => `${ps[0].axisValue}年<br/>${metricLabel.value}：${fmt(ps[0].value, 2)} ${metricUnit.value}`,
    },
    grid: { left: 48, right: 16, top: 16, bottom: 28 },
    xAxis: { type: 'category', data: detail.years, axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: { type: 'value', axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    series: [{
      type: 'line',
      data: detail.values,
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
    .slice(0, 15)
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
  const totalExport = yd ? yd.types.reduce((s, t) => s + t.value, 0) : 0
  const sorted = yd ? [...yd.types].sort((a, b) => b.value - a.value) : []
  const topType = sorted.length ? sorted[0].type : ''
  const typeCount = yd ? yd.types.length : 0
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
      data: yd.types.map(t => ({
        name: t.type,
        value: t.value,
        itemStyle: { color: TEA_COLORS[t.type] || '#8A8270' },
      })),
    }],
  }
})

const leavesTrendOption = computed(() => {
  const years = nationalData.map(d => d.year)
  return {
    tooltip: { ...tooltipBase, trigger: 'axis' },
    legend: {
      top: 5,
      textStyle: { color: '#5A6655', fontSize: 11 },
      data: ['茶叶总产量', '绿茶', '红茶'],
    },
    grid: { left: 48, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: years, axisLine: axisLineStyle, axisLabel: axisLabelStyle },
    yAxis: { type: 'value', name: '万吨', nameTextStyle: { color: '#5A6655', fontSize: 11 }, axisLine: axisLineStyle, axisLabel: axisLabelStyle, splitLine: splitLineStyle },
    series: [
      {
        name: '茶叶总产量',
        type: 'line',
        data: nationalData.map(d => d.totalOutput),
        smooth: true,
        lineStyle: { color: '#5C7C3A', width: 2.5 },
        itemStyle: { color: '#5C7C3A' },
        areaStyle: { color: 'rgba(92,124,58,0.12)' },
      },
      {
        name: '绿茶',
        type: 'line',
        data: nationalData.map(d => d.greenTea),
        smooth: true,
        lineStyle: { color: '#6F9150', width: 2 },
        itemStyle: { color: '#6F9150' },
      },
      {
        name: '红茶',
        type: 'line',
        data: nationalData.map(d => d.blackTea),
        smooth: true,
        lineStyle: { color: '#A8453A', width: 2 },
        itemStyle: { color: '#A8453A' },
      },
    ],
  }
})

const leavesStackedOption = computed(() => {
  const yearRange = teaTypeData.filter(d => d.year >= 2015 && d.year <= 2024)
  const years = yearRange.map(d => d.year)
  const types = TEA_ORDER.filter(t => t !== '其他')
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => {
        let html = `<b>${ps[0].axisValue}年</b>`
        ps.forEach(p => {
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
    series: types.map(type => ({
      name: type,
      type: 'line',
      stack: 'total',
      areaStyle: { opacity: 0.55, color: TEA_COLORS[type] || '#8A8270' },
      lineStyle: { color: TEA_COLORS[type] || '#8A8270', width: 1.5 },
      itemStyle: { color: TEA_COLORS[type] || '#8A8270' },
      smooth: true,
      data: yearRange.map(d => {
        const t = d.types.find(x => x.type === type)
        return t ? t.value : 0
      }),
    })),
  }
})

const leavesTeaCards = computed(() => {
  const yd = teaTypeData.find(d => d.year === leavesYear.value)
  const valueMap = {}
  if (yd) yd.types.forEach(t => { valueMap[t.type] = t.value })
  return TEA_ORDER
    .filter(t => t !== '其他')
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
  if (!yd) return { totalExport: 0, topCountry: '', countryCount: 0, provinceCount: 0 }
  const totalExport = yd.countries.reduce((s, c) => s + c.value, 0)
  const sorted = [...yd.countries].sort((a, b) => b.value - a.value)
  return {
    totalExport,
    topCountry: sorted.length ? sorted[0].name : '',
    countryCount: yd.countries.length,
    provinceCount: pd ? pd.provinces.length : 0,
  }
})

const branchesSankeyOption = computed(() => {
  const yd = sankeyData.find(d => d.year === branchesYear.value)
  if (!yd) return {}
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
      data: yd.nodes.map(n => ({
        name: n.name,
        itemStyle: { color: n.category === 'province' ? '#5C7C3A' : '#C8A155' },
        label: { color: '#3A4D38', fontSize: 11 },
      })),
      links: yd.links.map(l => ({
        source: l.source,
        target: l.target,
        value: l.value,
        lineStyle: { color: 'gradient', opacity: 0.35, curveness: 0.5 },
      })),
      lineStyle: { curveness: 0.5 },
    }],
  }
})

const branchesCountryRankOption = computed(() => {
  const yd = countryData.find(d => d.year === branchesYear.value)
  if (!yd) return {}
  const sorted = [...yd.countries].sort((a, b) => b.value - a.value).slice(0, 15).reverse()
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
  const trend = countryData.map(d => ({
    year: d.year,
    total: d.countries.reduce((s, c) => s + c.value, 0),
  }))
  const maxItem = trend.reduce((m, d) => (d.total > m.total ? d : m), trend[0] || { year: 0, total: 0 })
  return {
    tooltip: {
      ...tooltipBase,
      trigger: 'axis',
      formatter: ps => `<b>${ps[0].axisValue}年</b><br/>出口总额：${fmt(ps[0].value, 2)} 亿元`,
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
      data: trend.map(d => d.total / 1e8),
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
      markPoint: {
        symbol: 'pin',
        symbolSize: 48,
        data: [{ name: '最大值', value: maxItem.total / 1e8, xAxis: maxItem.year, yAxis: maxItem.total / 1e8 }],
        itemStyle: { color: '#B28F4C' },
        label: { color: '#fff', fontSize: 10, formatter: p => p.value.toFixed(1) },
      },
    }],
  }
})

const branchesProvinceShares = computed(() => {
  const yd = provinceExportData.find(d => d.year === branchesYear.value)
  if (!yd) return []
  const total = yd.provinces.reduce((s, p) => s + p.value, 0)
  return yd.provinces
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
   Chapter 5 · 今日茶境
   ============================================================ */
.chapter-5 {
  position: relative;
  background: var(--c-paper-2);
}

.map-fullscreen {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
  overflow-y: auto;
  padding: 1rem 2rem 5rem;
}
.map-fullscreen.show {
  opacity: 1;
}

/* ---- Tab navigation ---- */
.ch5-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  max-width: 900px;
  margin: 0 auto 2rem;
  flex-wrap: wrap;
}

.ch5-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 22px;
  border: 1.5px solid var(--c-beige);
  border-radius: 30px;
  background: var(--c-paper);
  color: var(--c-olive);
  font: 500 14px/1 var(--serif);
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.05em;
}

.ch5-tab:hover {
  border-color: var(--c-olive-mid);
  background: rgba(247, 244, 235, 0.9);
  transform: translateY(-1px);
}

.ch5-tab.active {
  background: var(--c-olive);
  border-color: var(--c-olive);
  color: var(--c-paper);
  box-shadow: 0 3px 14px rgba(81, 109, 51, 0.28);
}

.ch5-tab .tab-icon {
  font-size: 16px;
}

/* ---- View container ---- */
.ch5-view {
  max-width: 1280px;
  margin: 0 auto;
}

/* ============================================================
   Home view · Tea tree SVG scene
   ============================================================ */
.ch5-view-home {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.ch5-tree-scene {
  background: linear-gradient(160deg, var(--c-paper) 0%, var(--c-paper-2) 100%);
  border-radius: 14px;
  border: 1px solid var(--line);
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(81, 109, 51, 0.08);
}

.tree-svg {
  display: block;
  width: 100%;
  height: auto;
  max-height: 640px;
}

/* Sway animation for trees */
.tea-tree {
  animation: tree-sway 5s ease-in-out infinite;
  transform-box: fill-box;
}

.tree-1 { animation-delay: 0s; animation-duration: 5.5s; }
.tree-2 { animation-delay: -1.2s; animation-duration: 6s; }
.tree-3 { animation-delay: -2.5s; animation-duration: 5s; }

@keyframes tree-sway {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(0.4deg); }
  75% { transform: rotate(-0.4deg); }
}

/* Floating leaves */
.float-leaf {
  transform-box: fill-box;
  transform-origin: center;
}

.fl-1 { animation: float-down 8s ease-in 1s infinite; }
.fl-2 { animation: float-down 10s ease-in 3s infinite; }
.fl-3 { animation: float-down 9s ease-in 5s infinite; }
.fl-4 { animation: float-down 11s ease-in 0.5s infinite; }

@keyframes float-down {
  0% { transform: translate(0, 0) rotate(0deg); opacity: 0.5; }
  50% { opacity: 0.3; }
  100% { transform: translate(30px, 380px) rotate(360deg); opacity: 0; }
}

/* Interactive zones */
.zone-group {
  cursor: pointer;
}

.zone-rect {
  fill: transparent;
  transition: fill 0.3s ease;
}

.zone-rect.zone-active {
  fill: rgba(81, 109, 51, 0.06);
}

.zone-label text {
  font-family: var(--serif);
  pointer-events: none;
  transition: all 0.3s ease;
}

/* Zone cards */
.ch5-zone-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
}

.ch5-zone-card {
  --zone-color: var(--c-olive);
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-left: 4px solid var(--zone-color);
  border-radius: 12px;
  padding: 1.2rem 1.4rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(81, 109, 51, 0.06);
}

.ch5-zone-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 24px rgba(81, 109, 51, 0.14);
  border-left-width: 6px;
}

.zone-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.8rem;
}

.zone-card-icon {
  font-size: 24px;
}

.zone-card-title {
  font: 600 15px/1 var(--serif);
  color: var(--zone-color);
  letter-spacing: 0.05em;
}

.zone-card-stat {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.zone-card-unit {
  font: 400 12px/1 var(--sans);
  color: var(--muted);
}

/* ============================================================
   Controls (metric toggle, year slider, year select)
   ============================================================ */
.ch5-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.2rem;
  padding: 0.8rem 1.2rem;
  background: var(--c-paper);
  border: 1px solid var(--line);
  border-radius: 10px;
}

.ch5-metric-toggle {
  display: flex;
  gap: 0;
  border: 1.5px solid var(--c-beige);
  border-radius: 8px;
  overflow: hidden;
}

.toggle-btn {
  padding: 7px 20px;
  border: none;
  background: var(--c-paper);
  color: var(--ink-soft);
  font: 500 13px/1 var(--sans);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:not(:last-child) {
  border-right: 1px solid var(--c-beige);
}

.toggle-btn:hover {
  background: var(--c-paper-2);
}

.toggle-btn.active {
  color: #fff;
}

.ch5-year-slider {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-label {
  font: 500 13px/1 var(--sans);
  color: var(--c-olive);
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.slider-input {
  -webkit-appearance: none;
  appearance: none;
  width: 200px;
  height: 6px;
  border-radius: 3px;
  background: var(--c-beige);
  outline: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--c-olive);
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.slider-input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--c-olive);
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.slider-value {
  font: 700 16px/1 var(--serif);
  color: var(--c-olive);
  min-width: 48px;
  text-align: center;
}

.ch5-year-select {
  display: flex;
  align-items: center;
  gap: 10px;
}

.select-input {
  padding: 6px 16px;
  border: 1.5px solid var(--c-beige);
  border-radius: 8px;
  background: var(--c-paper);
  color: var(--c-olive);
  font: 500 14px/1 var(--sans);
  cursor: pointer;
  outline: none;
}

.select-input:focus {
  border-color: var(--c-olive-mid);
}

/* ============================================================
   Overview cards grid
   ============================================================ */
.ch5-overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.ch5-overview-card {
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 1rem 1.2rem;
  box-shadow: 0 2px 10px rgba(81, 109, 51, 0.05);
}

.ov-label {
  font: 400 12px/1.4 var(--sans);
  color: var(--muted);
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.ov-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.ov-unit {
  font: 400 12px/1 var(--sans);
  color: var(--beige-dark, #A5A37A);
}

.ch5-stat-num {
  font: 900 1.7rem/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.02em;
}

/* ============================================================
   Card container
   ============================================================ */
.ch5-card {
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 1rem 1.2rem 1.2rem;
  box-shadow: 0 2px 14px rgba(81, 109, 51, 0.06);
}

.card-title {
  font: 600 15px/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.05em;
  margin-bottom: 0.8rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--line);
}

.chart-container {
  width: 100%;
}

.chart-map { height: 460px; }
.chart-province-trend { height: 200px; }
.chart-ranking { height: 380px; }
.chart-pie { height: 340px; }
.chart-trend { height: 340px; }
.chart-stacked { height: 360px; }
.chart-sankey { height: 420px; }
.chart-country-rank { height: 360px; }
.chart-branch-trend { height: 340px; }

.ch5-map-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font: 400 14px/1 var(--sans);
  color: var(--muted);
}

.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  font: 400 14px/1 var(--sans);
  color: var(--muted);
}

/* ============================================================
   Roots view layout
   ============================================================ */
.ch5-roots-main {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.2rem;
  margin-bottom: 1.2rem;
}

.province-detail-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.province-mini-stats {
  display: flex;
  gap: 0.6rem;
}

.mini-stat {
  flex: 1;
  background: var(--c-paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  text-align: center;
}

.mini-label {
  display: block;
  font: 400 11px/1.4 var(--sans);
  color: var(--muted);
  margin-bottom: 4px;
}

.mini-val {
  display: block;
  font: 700 16px/1 var(--serif);
  color: var(--c-olive);
}

.mini-val small {
  font: 400 11px/1 var(--sans);
  color: var(--muted);
}

/* ============================================================
   Leaves view layout
   ============================================================ */
.ch5-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
  margin-bottom: 1.2rem;
}

.ch5-tea-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.ch5-tea-card {
  --tea-color: var(--c-olive);
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-top: 3px solid var(--tea-color);
  border-radius: 10px;
  padding: 1rem 1.1rem;
  transition: all 0.25s ease;
}

.ch5-tea-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(81, 109, 51, 0.12);
}

.tea-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.6rem;
}

.tea-card-icon {
  font-size: 22px;
}

.tea-card-titles {
  display: flex;
  flex-direction: column;
}

.tea-card-name {
  font: 700 15px/1.2 var(--serif);
  color: var(--tea-color);
}

.tea-card-en {
  font: 400 11px/1 var(--sans);
  color: var(--muted);
  letter-spacing: 0.05em;
}

.tea-card-desc {
  font: 400 12.5px/1.6 var(--serif);
  color: var(--ink-soft);
  margin: 0 0 0.6rem;
}

.tea-card-val {
  display: flex;
  align-items: baseline;
  gap: 4px;
  border-top: 1px dashed var(--line);
  padding-top: 0.5rem;
}

.val-num {
  font: 700 18px/1 var(--serif);
  color: var(--tea-color);
}

.val-num.muted {
  color: var(--muted);
}

.val-unit {
  font: 400 12px/1 var(--sans);
  color: var(--muted);
}

/* ============================================================
   Branches view layout
   ============================================================ */
.ch5-province-shares {
  margin-top: 1.5rem;
}

.shares-title {
  font: 600 15px/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.shares-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.8rem;
}

.ch5-share-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.7rem 1rem;
}

.share-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font: 700 14px/1 var(--serif);
  color: #fff;
  flex-shrink: 0;
}

.share-info {
  flex: 1;
  min-width: 0;
}

.share-name {
  font: 600 14px/1.3 var(--serif);
  color: var(--c-olive);
  margin-bottom: 2px;
}

.share-val {
  font: 400 12px/1.4 var(--sans);
  color: var(--ink-soft);
  margin-bottom: 4px;
}

.share-bar-wrap {
  height: 5px;
  background: var(--c-paper-3);
  border-radius: 3px;
  overflow: hidden;
}

.share-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

/* ============================================================
   Responsive
   ============================================================ */
@media (max-width: 960px) {
  .ch5-overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .ch5-roots-main,
  .ch5-charts-row {
    grid-template-columns: 1fr;
  }
  .ch5-zone-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .map-fullscreen {
    padding: 0.5rem 1rem 3rem;
  }
  .ch5-overview-grid {
    grid-template-columns: 1fr;
  }
  .ch5-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .ch5-metric-toggle {
    justify-content: center;
  }
  .ch5-year-slider {
    justify-content: center;
  }
  .slider-input {
    width: 100%;
  }
  .ch5-stat-num {
    font-size: 1.4rem;
  }
}
</style>
