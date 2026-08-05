<template>
  <section class="chapter chapter-4" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="第 四 章"
      title="一叶行远"
      desc="自古港而向四海，沿茶马古道以入远方；当代茶贸连接南北五洲，从产地直达餐桌。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
      <!-- Tab Navigation -->
      <nav class="ch4-tabs">
        <button
          v-for="t in ch4Tabs"
          :key="t.key"
          :class="['ch4-tab', { active: ch4Tab === t.key }]"
          @click="switchCh4Tab(t.key)"
        >
          <span class="tab-icon">{{ t.icon }}</span>
          <span class="tab-label">{{ t.label }}</span>
        </button>
      </nav>

      <!-- ============================== Tab: 古代贸易发展 ============================== -->
      <div v-show="ch4Tab === 'ancient'" class="ch4-view ch4-view-ancient">
        <div class="ch4-topbar">
          <div class="dynasty-indicator" :class="'dyn-' + dynastyClass">
            <span class="dyn-dot"></span>
            <span class="dyn-label">{{ dynastyName || '跨朝代' }}</span>
          </div>

          <div class="year-title">
            <span class="year-num">{{ dynastyName || '跨朝代' }}</span>
          </div>

          <div class="topbar-actions">
            <button class="action-btn" :class="{ playing: isPlaying }" @click="togglePlay">
              <span v-if="!isPlaying" class="btn-icon">▶</span>
              <span v-else class="btn-icon">❚❚</span>
              <span class="btn-text">{{ isPlaying ? '暂停' : '播放' }}</span>
            </button>
            <button class="action-btn secondary" @click="resetView">
              <span class="btn-icon">↺</span>
              <span class="btn-text">重置</span>
            </button>
          </div>
        </div>

        <div class="ch4-stage">
            <div ref="ancientMapEl" class="map"></div>

            <div v-if="showHint" class="map-hint">
              <span class="hint-icon">💡</span>
              <span>点击地图上的路线查看详情 · 拖动下方时间轴探索不同年代</span>
            </div>

            <div class="map-legend">
              <div class="legend-title">图例</div>
              <div class="legend-row">
                <span class="legend-line land"></span>
                <span>陆路·茶马古道</span>
              </div>
              <div class="legend-row">
                <span class="legend-line sea"></span>
                <span>海上·茶叶海运</span>
              </div>
              <div class="legend-row">
                <span class="legend-line ended"></span>
                <span>已结束路线</span>
              </div>
              <div class="legend-row nodes">
                <span class="legend-node origin"></span>
                <span>起点 / 中国港口</span>
              </div>
              <div class="legend-row nodes">
                <span class="legend-node dest"></span>
                <span>终点 / 海外都城</span>
              </div>
            </div>

            <transition name="panel-slide">
              <div v-if="selectedRoute" class="route-detail-panel">
                <div class="panel-header">
                  <div class="panel-title-wrap">
                    <span class="panel-type-tag">{{ selectedRoute.type }}</span>
                    <h3 class="panel-title">{{ routeFromTo }}</h3>
                  </div>
                  <button class="panel-close" @click="selectedRoute = null">×</button>
                </div>
                <div class="panel-scroll">
                  <div class="detail-year">
                    <span class="detail-year-label">年代</span>
                    <span class="detail-year-value">{{ selectedRoute.yearText }}</span>
                  </div>
                  <div class="detail-note">
                    <div class="detail-section-label">路线纪事</div>
                    <p>{{ selectedRoute.note }}</p>
                  </div>
                  <div class="detail-source">
                    <div class="detail-section-label">史料来源</div>
                    <p>{{ selectedRoute.source }}</p>
                  </div>
                  <div v-if="routeHistoryEvents.length" class="detail-history">
                    <div class="detail-section-label with-icon">
                      <span>📜</span>
                      <span>历史背景</span>
                    </div>
                    <ul>
                      <li v-for="(ev, i) in routeHistoryEvents" :key="i">{{ ev }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </transition>

            <transition name="panel-fade">
              <div v-if="currentEvents.length && !selectedRoute" class="history-panel">
                <div class="history-title">📜 {{ dynastyName }} · 此时</div>
                <ul>
                  <li v-for="(ev, i) in currentEvents.slice(0, 3)" :key="i">{{ ev }}</li>
                </ul>
              </div>
            </transition>
        </div>

        <div class="timeline-panel">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">活跃路线</div>
              <div class="stat-num">{{ stats.activeCount }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">已结束路线</div>
              <div class="stat-num">{{ stats.endedCount }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">可视流线</div>
              <div class="stat-num">{{ stats.routeCount }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">涉及节点</div>
              <div class="stat-num">{{ stats.countryCount }}</div>
            </div>
          </div>

          <div class="slider-wrap">
            <div class="dynasty-ticks">
              <div
                v-for="d in dynasties"
                :key="d.name"
                class="tick"
                :style="{ left: ((d.start - 618) / (1945 - 618) * 100) + '%' }"
              >
                <span class="tick-line"></span>
                <span class="tick-label">{{ d.name }}</span>
              </div>
            </div>

            <input
              type="range"
              :min="618"
              :max="1945"
              step="1"
              :value="currentYear"
              @input="onSliderInput"
              @change="onSliderChange"
              class="year-slider"
            />
          </div>

          <div class="filter-buttons">
            <button
              :class="['filter-btn', { active: filter === 'all' }]"
              @click="filter = 'all'"
            >全部</button>
            <button
              :class="['filter-btn', { active: filter === 'sea' }]"
              @click="filter = 'sea'"
            >海上</button>
            <button
              :class="['filter-btn', { active: filter === 'land' }]"
              @click="filter = 'land'"
            >陆路</button>
          </div>
        </div>
      </div>

      <!-- ============================== Tab: 当代贸易情况 ============================== -->
      <div v-show="ch4Tab === 'modern'" class="ch4-view ch4-view-modern">
        <div class="modern-topbar">
          <div class="modern-title">
            <span class="title-badge" :class="{ world: !isModernChinaMode }">
              {{ isModernChinaMode ? '🇨🇳 选择省份' : '🌍 ' + (selectedModernProvince || '中国') + ' → 世界' }}
            </span>
            <span class="title-sub" v-if="isModernChinaMode">点击任意省份，查看该省茶叶出口全球流向</span>
            <span class="title-sub" v-else>{{ modernYear }}年 出口总额 <b class="hl-num">{{ fmt(modernProvinceInfo.provinceValue / 1e8, 2) }}</b> 亿元，覆盖 <b class="hl-num">{{ modernProvinceInfo.flows.length }}</b> 个主要国家</span>
          </div>
          <div class="modern-controls">
            <div class="year-select">
              <span class="slider-label">出口年份</span>
              <select v-model.number="modernYear" @change="onModernYearChange" class="select-input">
                <option v-for="y in modernYears" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <button
              v-if="!isModernChinaMode"
              class="action-btn secondary"
              @click="backToChinaMap"
            >
              <span class="btn-icon">←</span>
              <span class="btn-text">返回省份选择</span>
            </button>
          </div>
        </div>

        <div class="ch4-stage modern-stage">
            <div ref="modernMapEl" class="map modern-map"></div>

            <!-- 中国模式图例 -->
            <div v-if="isModernChinaMode" class="map-legend modern-legend">
              <div class="legend-title">2024年各省出口额</div>
              <div class="legend-row">
                <span class="legend-bar" style="background: linear-gradient(90deg,#EFE9DA 0%, #B28F4C 50%, #516D33 100%)"></span>
              </div>
              <div class="legend-scale">
                <span>低</span><span>中</span><span>高</span>
              </div>
              <div class="legend-hint">鼠标悬浮查看数值；点击进入全球流向</div>
            </div>

            <!-- 世界模式图例 -->
            <div v-else class="map-legend modern-legend">
              <div class="legend-title">贸易流向（线条粗细=贸易量）</div>
              <div class="legend-row">
                <span class="legend-line" style="width:100%;max-width:260px;background:linear-gradient(90deg, rgba(178,143,76,0.2) 0%, #C8462E 100%);"></span>
              </div>
              <div class="legend-scale">
                <span>小</span><span>中</span><span>大</span>
              </div>
              <div class="legend-hint">
                <b>高亮</b>：{{ selectedModernProvince }}<br/>
                <span style="font-size:12px;opacity:.75">点击返回按钮可切换省份</span>
              </div>
            </div>

            <!-- 悬浮信息卡（中国模式：显示省份数值） -->
            <transition name="panel-fade">
              <div v-if="isModernChinaMode && hoveredProvince" class="hover-card">
                <div class="hc-title">{{ hoveredProvince.name }}</div>
                <div class="hc-row"><span>出口额</span><b>{{ fmt(hoveredProvince.value / 1e8, 2) }} 亿元</b></div>
                <div class="hc-row"><span>全国占比</span><b>{{ hoveredProvince.share }}%</b></div>
              </div>
            </transition>

            <!-- 世界模式：Top 进口国列表 -->
            <transition name="panel-slide">
              <div v-if="!isModernChinaMode && modernProvinceInfo.flows.length" class="modern-country-panel">
                <div class="panel-header">
                  <div class="panel-title-wrap">
                    <span class="panel-type-tag" style="background:var(--c-olive);">全球流向</span>
                    <h3 class="panel-title">{{ selectedModernProvince }} · Top 进口国</h3>
                  </div>
                </div>
                <div class="panel-scroll">
                  <div
                    v-for="(f, i) in modernProvinceInfo.flows.slice(0, 15)"
                    :key="f.country"
                    class="country-row"
                    :style="{ '--w': Math.max(8, Math.min(100, f.value / modernProvinceInfo.flows[0].value * 100)) + '%' }"
                    @mouseenter="highlightFlowCountry(f.country, true)"
                    @mouseleave="highlightFlowCountry(f.country, false)"
                  >
                    <div class="cr-rank">{{ i + 1 }}</div>
                    <div class="cr-name">{{ f.country }}</div>
                    <div class="cr-bar-wrap"><div class="cr-bar"></div></div>
                    <div class="cr-val">{{ fmt(f.value / 1e8, 2) }}<span class="unit">亿元</span></div>
                  </div>
                </div>
              </div>
            </transition>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import ChapterIntro from './ChapterIntro.vue'
import { TEA_TRADE_DATA, HISTORICAL_EVENTS, getEventsByYear } from '../data/ch4/trade-data.js'
import { fmt } from '../config/ch5.js'
import { assetUrl } from '../utils/base.js'
import {
  PROVINCE_CENTER,
  AVAILABLE_YEARS as MODERN_YEARS,
  getProvinceExports,
  estimateProvinceFlows,
} from '../config/ch4-modern.js'

// ============================= Tab System =============================
const ch4Tabs = [
  { key: 'ancient', label: '一叶行远·古代贸易发展', icon: '🏯' },
  { key: 'modern',  label: '一叶行远·当代贸易情况', icon: '🌐' },
]
const ch4Tab = ref('ancient')
function switchCh4Tab(k) {
  ch4Tab.value = k
  setTimeout(() => {
    if (k === 'ancient' && ancientMap) ancientMap.invalidateSize()
    if (k === 'modern' && modernMap) {
      modernMap.invalidateSize()
      if (isModernChinaMode.value) fitModernChinaBounds()
      else fitModernWorldBounds()
    }
  }, 60)
}

const props = defineProps({ id: { type: String, required: true } })
const sectionEl = ref(null)
const introDone = ref(false)
function onIntroDone() {
  introDone.value = true
  nextTick(() => {
    setTimeout(() => {
      if (!ancientMap) initAncientMap()
      if (ch4Tab.value === 'ancient' && ancientMap) ancientMap.invalidateSize()
    }, 200)
  })
}

// ==========================================================================
// Part 1: 古代贸易发展（保留原有全部逻辑）
// ==========================================================================
const dynasties = [
  { name: '唐代', start: 618, end: 907 },
  { name: '宋代', start: 960, end: 1279 },
  { name: '元代', start: 1271, end: 1368 },
  { name: '明代', start: 1368, end: 1644 },
  { name: '清代', start: 1644, end: 1911 },
  { name: '抗战时期', start: 1937, end: 1945 },
]

const kind = r => /海上|海运/.test(r.type) ? 'sea' : 'land'
function getRouteState(r, y) {
  y = Number(y)
  const s = Number(r.startYear)
  if (y < s) return 'not_started'
  if (r.endYear === undefined || r.endYear === null || r.endYear === '') return 'active_permanent'
  const e = Number(r.endYear)
  return y <= e ? 'active' : 'ended'
}
const inChina = p => p.lon >= 73 && p.lon <= 135 && p.lat >= 18 && p.lat <= 54
const capitals = [
  ['荷兰', '阿姆斯特丹', 4.9041, 52.3676],['英国', '伦敦', -0.1276, 51.5072],['美国', '华盛顿', -77.0369, 38.9072],
  ['法国', '巴黎', 2.3522, 48.8566],['德国', '柏林', 13.405, 52.52],['丹麦', '哥本哈根', 12.5683, 55.6761],
  ['瑞典', '斯德哥尔摩', 18.0686, 59.3293],['日本', '东京', 139.6917, 35.6895],['俄国', '莫斯科', 37.6173, 55.7558],
  ['俄罗斯', '莫斯科', 37.6173, 55.7558],['敖德萨', '莫斯科', 37.6173, 55.7558],['印度', '新德里', 77.209, 28.6139],
  ['尼泊尔', '加德满都', 85.324, 27.7172],['缅甸', '内比都', 96.0785, 19.7633],['欧洲', '布鲁塞尔', 4.3517, 50.8503]
]
function namedCapital(text) {
  const hit = capitals.find(([k]) => String(text).includes(k))
  return hit ? { name: hit[1], lon: hit[2], lat: hit[3] } : null
}
function visualPoints(r) {
  if (kind(r) !== 'sea') return r.points
  const chinese = r.points.find(inChina) || { name: '广州', lon: 113.2644, lat: 23.1291 }
  let dest = namedCapital(r.destination)
  if (!dest && inChina(r.points[r.points.length - 1])) dest = namedCapital(r.origin)
  if (!dest) {
    const foreign = r.points.filter(p => !inChina(p))
    dest = foreign.length ? foreign[foreign.length - 1] : null
  }
  return dest ? [chinese, dest] : r.points
}
function curved(a, b, steps = 28) {
  const dist = Math.hypot(b.lon - a.lon, b.lat - a.lat)
  const lift = Math.min(22, dist * 0.13)
  const out = []
  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    out.push([Math.max(-85, Math.min(85, a.lat + (b.lat - a.lat) * t + Math.sin(Math.PI * t) * lift)), a.lon + (b.lon - a.lon) * t])
  }
  return out
}
function coords(points) {
  const out = []
  for (let i = 1; i < points.length; i++) {
    const seg = curved(points[i - 1], points[i])
    if (i > 1) seg.shift()
    out.push(...seg)
  }
  return out
}
function getAllDataYears() {
  const years = new Set()
  for (const r of TEA_TRADE_DATA) {
    if (r.startYear != null) years.add(Number(r.startYear))
    if (r.endYear != null) years.add(Number(r.endYear))
  }
  years.add(618); years.add(1945)
  return Array.from(years).sort((a, b) => a - b)
}
const allDataYears = getAllDataYears()
function getClosestDataYear(y) {
  let closest = allDataYears[0], minDiff = Infinity
  for (const x of allDataYears) { const d = Math.abs(x - y); if (d < minDiff) { minDiff = d; closest = x } }
  return closest
}
function getNextDataYear(y) {
  for (const x of allDataYears) if (x > y) return x
  return allDataYears[allDataYears.length - 1]
}
function getDynastyName(y) {
  for (const d of dynasties) if (y >= d.start && y <= d.end) return d.name
  return ''
}

const ancientMapEl = ref(null)
const currentYear = ref(618)
const filter = ref('all')
const isPlaying = ref(false)
const selectedRoute = ref(null)
const showHint = ref(true)

let ancientMap = null
let routeLayer = null
let nodeLayer = null
let playTimer = null

const stats = reactive({
  activeCount: 0,
  endedCount: 0,
  routeCount: 0,
  countryCount: 0,
})

const dynastyName = computed(() => getDynastyName(currentYear.value))
const dynastyClass = computed(() => {
  const n = dynastyName.value
  if (n === '唐代') return 'tang'
  if (n === '宋代') return 'song'
  if (n === '元代') return 'yuan'
  if (n === '明代') return 'ming'
  if (n === '清代') return 'qing'
  if (n === '抗战时期') return 'kangzhan'
  return 'default'
})

const currentEvents = computed(() => getEventsByYear(currentYear.value))
const routeFromTo = computed(() => {
  const r = selectedRoute.value
  if (!r) return ''
  return `${r.origin} → ${r.destination}`
})
const routeHistoryEvents = computed(() => {
  const r = selectedRoute.value
  if (!r) return []
  const y = Number(r.startYear)
  return getEventsByYear(getClosestDataYear(y))
})

function renderRoutes() {
  if (!ancientMap) return
  if (routeLayer) { ancientMap.removeLayer(routeLayer); routeLayer = null }
  if (nodeLayer) { ancientMap.removeLayer(nodeLayer); nodeLayer = null }
  routeLayer = L.layerGroup().addTo(ancientMap)
  nodeLayer = L.layerGroup().addTo(ancientMap)

  const y = currentYear.value
  const activeSet = new Set()
  let endedCount = 0, activeCount = 0, visibleCount = 0

  TEA_TRADE_DATA.forEach(r => {
    const f = filter.value
    if (f !== 'all' && kind(r) !== f) return
    const st = getRouteState(r, y)
    if (st === 'not_started') return
    visibleCount++
    if (st === 'ended') endedCount++
    else activeCount++

    const k = kind(r)
    const baseColor = k === 'sea' ? '#0E4A54' : '#B28F4C'
    const color = st === 'ended' ? '#7a7a6e' : baseColor
    const dash = st === 'ended' ? '8 6' : null
    const weight = st === 'ended' ? 1.5 : 2.8

    const pts = visualPoints(r)
    if (pts.length < 2) return
    const line = L.polyline(coords(pts), {
      color, weight, opacity: st === 'ended' ? 0.5 : 0.88,
      lineCap: 'round', lineJoin: 'round', dashArray: dash, interactive: true,
    })
    line.on('click', () => { selectedRoute.value = r })
    line.on('mouseover', e => {
      line.setStyle({ weight: weight + 2, opacity: 1 })
      const latlng = e.latlng
      line.bindTooltip(`${r.yearText}  ${r.origin} → ${r.destination}`,
        { direction: 'top', offset: [0, -6], permanent: false, opacity: 0.95, className: 'route-tip' })
      line.openTooltip(latlng)
    })
    line.on('mouseout', () => {
      line.setStyle({ weight, opacity: st === 'ended' ? 0.5 : 0.88 })
      line.closeTooltip()
    })
    line.addTo(routeLayer)

    pts.forEach(p => {
      if (inChina(p)) activeSet.add('🇨🇳')
      activeSet.add((p.name || '').slice(0, 20))
    })
  })

  // 节点
  TEA_TRADE_DATA.forEach(r => {
    const f = filter.value
    if (f !== 'all' && kind(r) !== f) return
    const st = getRouteState(r, y)
    if (st === 'not_started') return
    const pts = visualPoints(r)
    if (!pts.length) return
    const origin = pts[0]
    const dest = pts[pts.length - 1]
    const oc = st === 'ended' ? '#7a7a6e' : '#0E6B5B'
    const dc = st === 'ended' ? '#9d9d8e' : '#B28F4C'
    const m1 = L.circleMarker([origin.lat, origin.lon],
      { radius: st === 'ended' ? 3 : 4.5, color: '#fff', weight: 1.2, fillColor: oc, fillOpacity: 1 })
    m1.bindTooltip(origin.name || '', { direction: 'top', offset: [0, -4] })
    m1.addTo(nodeLayer)
    if (dest !== origin) {
      const m2 = L.circleMarker([dest.lat, dest.lon],
        { radius: st === 'ended' ? 4 : 6, color: '#fff', weight: 1.2, fillColor: dc, fillOpacity: 1 })
      m2.bindTooltip(dest.name || '', { direction: 'top', offset: [0, -4] })
      m2.addTo(nodeLayer)
    }
  })

  stats.activeCount = activeCount
  stats.endedCount = endedCount
  stats.routeCount = visibleCount
  stats.countryCount = activeSet.size
}

function fitAncientWorldBounds() {
  if (!ancientMap) return
  ancientMap.setView([24, 60], 2)
  ancientMap.setMaxBounds([[-60, -180], [80, 180]])
}

function initAncientMap() {
  if (ancientMap) return
  ancientMap = L.map(ancientMapEl.value, {
    crs: L.CRS.EPSG4326,
    center: [24, 60],
    zoom: 2,
    minZoom: 2,
    maxZoom: 6,
    zoomControl: true,
    attributionControl: false,
    worldCopyJump: true,
  })
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 8, subdomains: 'abcd',
  }).addTo(ancientMap)

  ancientMap.createPane('routePane')
  ancientMap.getPane('routePane').style.zIndex = 395
  ancientMap.createPane('nodePane')
  ancientMap.getPane('nodePane').style.zIndex = 405
  setTimeout(() => { ancientMap && ancientMap.invalidateSize() }, 300)
  renderRoutes()
  fitAncientWorldBounds()
}

watch(currentYear, () => renderRoutes())
watch(filter, () => renderRoutes())
watch(selectedRoute, () => { showHint.value = !selectedRoute.value })

function onSliderInput(e) {
  currentYear.value = Number(e.target.value)
  if (isPlaying.value) isPlaying.value = false
  setTimeout(() => { if (ancientMap) ancientMap.invalidateSize() }, 0)
}
function onSliderChange(e) {
  currentYear.value = Number(e.target.value)
}
function togglePlay() {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    showHint.value = false
    playTimer = setInterval(() => {
      let next = currentYear.value + 2
      if (next > 1945) { next = 618; isPlaying.value = false; clearInterval(playTimer); return }
      currentYear.value = getClosestDataYear(next)
    }, 550)
  } else if (playTimer) {
    clearInterval(playTimer); playTimer = null
  }
}
function resetView() {
  currentYear.value = 618
  filter.value = 'all'
  isPlaying.value = false
  selectedRoute.value = null
  if (ancientMap) fitAncientWorldBounds()
}

// ==========================================================================
// Part 2: 当代贸易情况
// ==========================================================================
const modernMapEl = ref(null)
const modernYears = MODERN_YEARS.filter(y => y >= 2015 && y <= 2026)
const modernYear = ref(2024)
const isModernChinaMode = ref(true)
const selectedModernProvince = ref(null)
const hoveredProvince = ref(null)

let modernMap = null
let modernProvLayer = null     // 中国省份 geoJSON
let modernFlowLayer = null     // 世界模式：流线
let modernMarkersLayer = null  // 世界模式：节点
let modernHighlightedCountry = null  // 当前高亮国名

const modernProvinceInfo = reactive({
  provinceValue: 0,
  totalValue: 0,
  flows: [],
  year: 2024,
})

// ---- 中国模式：初始化省份底图 + 分级渲染 ----
function fitModernChinaBounds() {
  if (!modernMap) return
  modernMap.fitBounds([[18, 73], [54, 135]], { padding: [40, 40], maxZoom: 5 })
}
function fitModernWorldBounds() {
  if (!modernMap) return
  modernMap.fitBounds([[-55, -160], [75, 180]], { padding: [40, 40] })
}

function buildProvinceChoropleth() {
  const yearData = getProvinceExports(modernYear.value)
  const provinceMap = {}
  const total = yearData.reduce((s, p) => s + p.value, 0)
  yearData.forEach(p => { provinceMap[p.name] = { value: p.value, share: total ? (p.value / total * 100).toFixed(1) : 0 } })

  let maxV = Math.max(...yearData.map(p => p.value), 1)
  // 对数分段配色
  const colorFor = v => {
    if (!v || v <= 0) return '#F0EBD9'
    const t = Math.log10(Math.max(v, 1)) / Math.log10(maxV + 1)
    // 从米白(#F7F4EB) → 褐金(#B28F4C) → 深橄榄(#516D33)
    const lerp = (a, b, k) => a + (b - a) * k
    const stop1 = { r: 247, g: 244, b: 235 }
    const stop2 = { r: 178, g: 143, b: 76 }
    const stop3 = { r: 81, g: 109, b: 51 }
    const col = t < 0.5
      ? { r: lerp(stop1.r, stop2.r, t / 0.5), g: lerp(stop1.g, stop2.g, t / 0.5), b: lerp(stop1.b, stop2.b, t / 0.5) }
      : { r: lerp(stop2.r, stop3.r, (t - 0.5) / 0.5), g: lerp(stop2.g, stop3.g, (t - 0.5) / 0.5), b: lerp(stop2.b, stop3.b, (t - 0.5) / 0.5) }
    return `rgb(${Math.round(col.r)},${Math.round(col.g)},${Math.round(col.b)})`
  }

  const matchProvince = featureName => {
    // GeoJSON 中可能是「浙江」或「浙江省」，尝试匹配
    for (const p of yearData) {
      if (p.name === featureName) return p
      const clean = p.name.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政区/g, '')
      const fClean = featureName.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政区/g, '')
      if (clean && (clean === fClean || p.name.includes(featureName) || featureName.includes(clean))) return p
    }
    return null
  }

  return { provinceMap, colorFor, matchProvince }
}

function onModernYearChange() {
  if (isModernChinaMode.value) {
    renderModernChinaProvinces()
  } else if (selectedModernProvince.value) {
    enterWorldMode(selectedModernProvince.value)
  }
}

function renderModernChinaProvinces() {
  if (!modernMap) return
  if (modernProvLayer) { modernMap.removeLayer(modernProvLayer); modernProvLayer = null }
  const { provinceMap, colorFor, matchProvince } = buildProvinceChoropleth()

  fetch(assetUrl('data/2/china-provinces.geojson'))
    .then(r => r.json())
    .then(geo => {
      modernProvLayer = L.geoJSON(geo, {
        style: f => {
          const name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          const info = matchProvince(name)
          return {
            color: '#7e7866',
            weight: 0.6,
            fillColor: info ? colorFor(info.value) : '#F0EBD9',
            fillOpacity: 0.88,
          }
        },
        onEachFeature: (f, layer) => {
          const name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          const info = matchProvince(name)
          layer.on('mouseover', e => {
            hoveredProvince.value = info ? { name: info.name, value: info.value, share: provinceMap[info.name]?.share || 0 } : null
            layer.setStyle({ weight: 1.6, color: '#516D33' })
            layer.bringToFront()
          })
          layer.on('mouseout', () => {
            hoveredProvince.value = null
            modernProvLayer && modernProvLayer.resetStyle(layer)
          })
          layer.on('click', () => {
            if (!info) return
            enterWorldMode(info.name)
          })
        },
      }).addTo(modernMap)
      modernProvLayer.bringToFront()
    })
}

// ---- 世界模式：切换地图底图、渲染流线、中国高亮 ----
function enterWorldMode(provinceName) {
  selectedModernProvince.value = provinceName
  isModernChinaMode.value = false
  const info = estimateProvinceFlows(provinceName, modernYear.value, 20)
  Object.assign(modernProvinceInfo, info || { provinceValue: 0, totalValue: 0, flows: [], year: modernYear.value })
  modernProvinceInfo.year = modernYear.value

  nextTick(() => {
    if (!modernMap) return
    modernMap.invalidateSize()
    fitModernWorldBounds()
    renderModernFlows(provinceName, info)
  })
}

function backToChinaMap() {
  isModernChinaMode.value = true
  selectedModernProvince.value = null
  if (modernFlowLayer) { modernMap.removeLayer(modernFlowLayer); modernFlowLayer = null }
  if (modernMarkersLayer) { modernMap.removeLayer(modernMarkersLayer); modernMarkersLayer = null }
  modernHighlightedCountry = null
  nextTick(() => {
    if (!modernMap) return
    modernMap.invalidateSize()
    fitModernChinaBounds()
    renderModernChinaProvinces()
  })
}

function highlightFlowCountry(countryName, on) {
  if (!modernFlowLayer || !modernMarkersLayer) return
  modernHighlightedCountry = on ? countryName : null
  // 更新线和节点透明度
  modernFlowLayer.eachLayer(l => {
    const md = l._flowData
    if (!md) return
    const hl = (md.country === modernHighlightedCountry)
    const base = l._baseStyle || {}
    l.setStyle({
      opacity: hl ? 1 : (modernHighlightedCountry ? base.opacity * 0.18 : base.opacity),
      weight: hl ? (base.weight + 2) : base.weight,
    })
  })
  modernMarkersLayer.eachLayer(l => {
    const name = l._country
    if (!name) return
    const hl = (name === modernHighlightedCountry)
    const base = l._baseMarker || {}
    l.setStyle({
      radius: hl ? (base.radius + 4) : base.radius,
      opacity: hl ? 1 : (modernHighlightedCountry ? 0.35 : 0.95),
    })
  })
}

function renderModernFlows(provinceName, info) {
  if (!modernMap) return
  if (modernFlowLayer) { modernMap.removeLayer(modernFlowLayer); modernFlowLayer = null }
  if (modernMarkersLayer) { modernMap.removeLayer(modernMarkersLayer); modernMarkersLayer = null }

  // 省份起点坐标
  const center = PROVINCE_CENTER[provinceName] || PROVINCE_CENTER['浙江省']
  const fromLat = center[0], fromLon = center[1]

  // 重绘省份底图：高亮中国 + 突出选中省份
  if (modernProvLayer) { modernMap.removeLayer(modernProvLayer); modernProvLayer = null }
  fetch(assetUrl('data/2/china-provinces.geojson'))
    .then(r => r.json())
    .then(geo => {
      modernProvLayer = L.geoJSON(geo, {
        style: f => {
          const name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          const pClean = provinceName.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政区/g, '')
          const fClean = name.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政区/g, '')
          const isSelected = pClean === fClean
          return {
            color: isSelected ? '#C8462E' : '#516D33',
            weight: isSelected ? 2.6 : 0.8,
            fillColor: isSelected ? '#B28F4C' : '#93B55A',
            fillOpacity: isSelected ? 0.92 : 0.55,
          }
        }
      }).addTo(modernMap)
    })

  if (!info) return
  const flows = info.flows
  if (!flows.length) return

  const maxV = flows[0].value || 1
  modernFlowLayer = L.layerGroup().addTo(modernMap)
  modernMarkersLayer = L.layerGroup().addTo(modernMap)

  flows.forEach(f => {
    const [toLat, toLon] = f.to
    const norm = Math.max(0.05, Math.min(1, f.value / maxV))
    // 曲线生成：与 ancient 同算法
    const a = { lon: fromLon, lat: fromLat }, b = { lon: toLon, lat: toLat }
    const pts = coords([a, b])
    // 色从褐金→朱红渐变
    const t = norm
    const col = `rgb(${Math.round(178 + (200 - 178) * t)}, ${Math.round(143 - 143 * t * 0.6)}, ${Math.round(76 - 76 * t * 0.9)})`
    const w = 1.2 + norm * 8
    const line = L.polyline(pts, {
      color: col, weight: w, opacity: 0.45 + norm * 0.45,
      lineCap: 'round', lineJoin: 'round', interactive: true,
    })
    line._flowData = { country: f.country, value: f.value }
    line._baseStyle = { weight: w, opacity: 0.45 + norm * 0.45 }
    line.on('mouseover', () => {
      highlightFlowCountry(f.country, true)
      const latlng = pts[Math.floor(pts.length * 0.65)]
      line.bindTooltip(
        `<b>${provinceName} → ${f.country}</b><br/>出口额：${fmt(f.value / 1e8, 2)} 亿元`,
        { direction: 'top', offset: [0, -6], opacity: 0.96, className: 'route-tip modern-flow-tip' })
      line.openTooltip(latlng)
    })
    line.on('mouseout', () => { highlightFlowCountry(f.country, false); line.closeTooltip() })
    line.addTo(modernFlowLayer)

    // 终点国节点
    const isTop3 = norm >= 0.5
    const r = isTop3 ? 8 : 5
    const marker = L.circleMarker([toLat, toLon], {
      radius: r, color: '#fff', weight: 1.5,
      fillColor: isTop3 ? '#C8462E' : '#B28F4C', fillOpacity: 1,
    })
    marker._country = f.country
    marker._baseMarker = { radius: r }
    marker.bindTooltip(f.country, { direction: 'top', offset: [0, -6] })
    marker.on('mouseover', () => highlightFlowCountry(f.country, true))
    marker.on('mouseout', () => highlightFlowCountry(f.country, false))
    marker.addTo(modernMarkersLayer)
  })

  // 起点省份圆点（醒目）
  const originMarker = L.circleMarker([fromLat, fromLon], {
    radius: 12, color: '#fff', weight: 3,
    fillColor: '#516D33', fillOpacity: 1,
  })
  originMarker._baseMarker = { radius: 12 }
  originMarker.bindTooltip(`<b>${provinceName}</b><br/>出口总额 ${fmt(modernProvinceInfo.provinceValue / 1e8, 2)} 亿元`, { direction: 'top', offset: [0, -8] })
  originMarker.addTo(modernMarkersLayer)
}

function initModernMap() {
  if (modernMap) return
  modernMap = L.map(modernMapEl.value, {
    crs: L.CRS.EPSG4326,
    center: [32, 104],
    zoom: 4,
    minZoom: 2,
    maxZoom: 7,
    zoomControl: false,
    attributionControl: false,
  })
  L.control.zoom({ position: 'bottomright' }).addTo(modernMap)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 9, subdomains: 'abcd',
  }).addTo(modernMap)
  setTimeout(() => modernMap && modernMap.invalidateSize(), 300)
}

// ==========================================================================
// Lifecycle
// ==========================================================================
onMounted(async () => {
  await nextTick()
  // 初始化古代地图（默认 tab）；当代地图等切换时初始化
})

watch(ch4Tab, nv => {
  if (nv === 'modern' && !modernMap) {
    setTimeout(() => {
      initModernMap()
      renderModernChinaProvinces()
      fitModernChinaBounds()
    }, 250)
  }
})

onBeforeUnmount(() => {
  if (playTimer) { clearInterval(playTimer); playTimer = null }
  if (ancientMap) { ancientMap.remove(); ancientMap = null }
  if (modernMap) { modernMap.remove(); modernMap = null }
})
</script>

<style scoped>
/* ---- Tab Navigation ---- */
.ch4-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 14px 16px 0;
  flex-wrap: wrap;
}
.ch4-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 22px;
  border: 1.5px solid var(--c-beige);
  border-radius: 30px;
  background: rgba(247,244,235,0.7);
  color: var(--c-olive);
  font: 500 14px/1 var(--serif);
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.05em;
  backdrop-filter: blur(6px);
}
.ch4-tab:hover {
  border-color: var(--c-olive-mid);
  background: rgba(247, 244, 235, 0.95);
  transform: translateY(-1px);
}
.ch4-tab.active {
  background: var(--c-olive);
  border-color: var(--c-olive);
  color: var(--c-paper);
  box-shadow: 0 3px 14px rgba(81, 109, 51, 0.28);
}
.ch4-tab .tab-icon { font-size: 16px; }

.ch4-view {
  padding-top: 12px;
  min-height: 85vh;
  position: relative;
}

/* ---- Ancient view inherits original layout through nested classes ---- */
.ch4-view-ancient .ch4-topbar { top: 12px; }

/* ---- Modern view layout ---- */
.ch4-view-modern { padding-top: 10px; }
.modern-topbar {
  position: relative;
  z-index: 900;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  max-width: 1380px;
  margin: 0 auto 10px;
  padding: 10px 20px;
  background: rgba(247, 244, 235, 0.92);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(178, 143, 76, 0.18);
  box-shadow: 0 2px 10px rgba(81, 109, 51, 0.06);
  flex-wrap: wrap;
}
.modern-title { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 16px;
  background: var(--c-gold);
  color: #fff;
  border-radius: 20px;
  font: 700 14px/1 var(--serif);
  letter-spacing: 0.05em;
}
.title-badge.world { background: var(--c-olive-mid); }
.title-sub { color: var(--c-beige-dark); font-size: 13px; }
.title-sub .hl-num { color: var(--c-gold-deep); font-family: var(--serif); font-size: 16px; font-weight: 900; }
.modern-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.year-select { display: inline-flex; align-items: center; gap: 8px; }
.slider-label { color: var(--c-beige-dark); font-size: 13px; letter-spacing: 0.05em; }
.select-input {
  padding: 6px 12px;
  border: 1.5px solid var(--c-beige);
  border-radius: 8px;
  background: #fff;
  color: var(--c-olive);
  font: 500 13px/1 var(--serif);
  cursor: pointer;
  transition: all 0.2s ease;
}
.select-input:hover { border-color: var(--c-olive-mid); }
.select-input:focus { outline: none; border-color: var(--c-olive); box-shadow: 0 0 0 3px rgba(81,109,51,0.12); }

.modern-stage { position: relative; height: calc(100vh - 260px); min-height: 560px; max-width: 1380px; margin: 0 auto; border-radius: 14px; overflow: hidden; border: 1px solid var(--line); box-shadow: 0 4px 20px rgba(81,109,51,0.08); }
.modern-map { width: 100%; height: 100%; background: #F0EBD9; }

/* Hover card (China mode) */
.hover-card {
  position: absolute;
  top: 20px; right: 20px;
  z-index: 950;
  min-width: 220px;
  background: rgba(247, 244, 235, 0.98);
  border-radius: 10px;
  padding: 12px 16px;
  border: 1px solid rgba(178, 143, 76, 0.3);
  box-shadow: 0 4px 20px rgba(81,109,51,0.15);
  backdrop-filter: blur(8px);
}
.hc-title { font: 700 16px/1 var(--serif); color: var(--c-olive); margin-bottom: 8px; letter-spacing: 0.05em; }
.hc-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 13px; color: var(--c-beige-dark); }
.hc-row b { color: var(--c-gold-deep); font-family: var(--serif); font-weight: 900; }

/* Modern legend */
.modern-legend {
  position: absolute;
  left: 20px; bottom: 20px;
  z-index: 900;
  min-width: 230px;
  background: rgba(247, 244, 235, 0.94) !important;
}
.legend-bar { display: block; height: 12px; border-radius: 6px; margin: 4px 0 6px; }
.legend-scale { display: flex; justify-content: space-between; font-size: 11px; color: var(--c-beige-dark); letter-spacing: 0.08em; }
.legend-hint { margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(178,143,76,0.25); font-size: 12px; color: var(--c-beige-dark); }
.legend-hint b { color: var(--c-olive); font-weight: 700; }

/* Country ranking panel (world mode) */
.modern-country-panel {
  position: absolute;
  top: 16px; right: 16px;
  bottom: 16px;
  width: 340px;
  max-width: 42%;
  z-index: 920;
  background: rgba(247, 244, 235, 0.97);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(81, 109, 51, 0.18);
  border: 1px solid rgba(178, 143, 76, 0.15);
  display: flex;
  flex-direction: column;
}
.modern-country-panel .panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 10px 14px 18px;
}
.country-row {
  display: grid;
  grid-template-columns: 24px 96px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 8px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.country-row:hover { background: rgba(178, 143, 76, 0.1); }
.cr-rank {
  text-align: center;
  font: 900 12px/1 var(--serif);
  color: var(--c-beige-dark);
  width: 22px; height: 22px;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--c-paper-2); border-radius: 50%;
}
.country-row:nth-child(1) .cr-rank { background: #C8462E; color: #fff; }
.country-row:nth-child(2) .cr-rank { background: #B28F4C; color: #fff; }
.country-row:nth-child(3) .cr-rank { background: #5C7C3A; color: #fff; }
.cr-name {
  font: 600 13px/1 var(--serif);
  color: var(--c-olive);
  white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.cr-bar-wrap {
  height: 8px;
  background: rgba(178, 143, 76, 0.15);
  border-radius: 4px;
  overflow: hidden;
}
.cr-bar {
  height: 100%;
  width: var(--w);
  background: linear-gradient(90deg, #B28F4C, #C8462E);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.cr-val {
  font: 800 13px/1 var(--serif);
  color: var(--c-gold-deep);
  white-space: nowrap;
}
.cr-val .unit { font-weight: 500; color: var(--c-beige-dark); margin-left: 3px; font-size: 11px; }

/* Scrollbar for country panel */
.modern-country-panel .panel-scroll::-webkit-scrollbar { width: 5px; }
.modern-country-panel .panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(178, 143, 76, 0.3); border-radius: 3px;
}
.modern-country-panel .panel-scroll::-webkit-scrollbar-thumb:hover { background: rgba(178, 143, 76, 0.5); }

/* Tooltip for flows */
:deep(.modern-flow-tip) {
  background: var(--c-olive) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  border-radius: 6px;
  padding: 6px 10px !important;
  font: 500 12px/1.5 var(--serif);
}
:deep(.modern-flow-tip::before) { border-top-color: var(--c-olive) !important; }

/* ==========================================================
   Keep original Chapter 4 ancient layout styles below
   (from original file, prefixed to preserve)
   ========================================================== */
.ch4-topbar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1380px;
  margin: 0 auto 10px;
  padding: 10px 20px;
  background: rgba(247,244,235,0.92);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(178,143,76,0.18);
  box-shadow: 0 2px 10px rgba(81,109,51,0.06);
  z-index: 900;
}
.dynasty-indicator { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: rgba(178,143,76,0.12); border-radius: 24px; }
.dyn-dot { width: 10px; height: 10px; border-radius: 50%; background: #B28F4C; box-shadow: 0 0 0 3px rgba(178,143,76,0.2); animation: pulse 2.2s ease-in-out infinite; }
.dyn-label { font: 600 14px/1 var(--serif); color: var(--c-olive); letter-spacing: 0.08em; }
.dynasty-indicator.dyn-tang .dyn-dot { background: #C8462E; box-shadow: 0 0 0 3px rgba(200,70,46,0.2); }
.dynasty-indicator.dyn-song .dyn-dot { background: #5C9EAF; box-shadow: 0 0 0 3px rgba(92,158,175,0.2); }
.dynasty-indicator.dyn-yuan .dyn-dot { background: #5C7C3A; box-shadow: 0 0 0 3px rgba(92,124,58,0.2); }
.dynasty-indicator.dyn-ming .dyn-dot { background: #B28F4C; box-shadow: 0 0 0 3px rgba(178,143,76,0.2); }
.dynasty-indicator.dyn-qing .dyn-dot { background: #2F5D3A; box-shadow: 0 0 0 3px rgba(47,93,58,0.2); }
.dynasty-indicator.dyn-kangzhan .dyn-dot { background: #8a6f48; box-shadow: 0 0 0 3px rgba(138,111,72,0.2); }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.18); } }
.year-title { text-align: center; }
.year-num { font: 900 30px/1 var(--serif); color: var(--c-olive); letter-spacing: 0.08em; }
.topbar-actions { display: flex; gap: 10px; }
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  border: 1.5px solid var(--c-olive);
  border-radius: 24px;
  background: var(--c-olive);
  color: var(--c-paper);
  font: 600 13px/1 var(--serif);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(81,109,51,0.18);
}
.action-btn:hover { background: #3f5728; border-color: #3f5728; transform: translateY(-1px); }
.action-btn.secondary { background: transparent; color: var(--c-olive); }
.action-btn.secondary:hover { background: rgba(81,109,51,0.08); }
.action-btn .btn-icon { font-size: 11px; }
.action-btn.playing { background: var(--c-gold); border-color: var(--c-gold); }
.action-btn.playing:hover { background: #9a7a3d; border-color: #9a7a3d; }

.ch4-stage {
  position: relative;
  height: calc(100vh - 380px);
  min-height: 540px;
  max-width: 1380px;
  margin: 0 auto;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: 0 4px 20px rgba(81,109,51,0.08);
}
.ch4-view-ancient .map { width: 100%; height: 100%; background: #F0EBD9; }
.map-hint {
  position: absolute;
  top: 16px; left: 50%; transform: translateX(-50%);
  z-index: 900;
  background: rgba(81,109,51,0.9);
  color: var(--c-paper);
  padding: 8px 18px;
  border-radius: 24px;
  font: 500 13px/1 var(--serif);
  letter-spacing: 0.05em;
  backdrop-filter: blur(8px);
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.hint-icon { font-size: 15px; }

.map-legend {
  position: absolute;
  left: 16px; top: 16px;
  z-index: 900;
  background: rgba(247,244,235,0.92);
  backdrop-filter: blur(8px);
  border-radius: 10px;
  padding: 12px 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  font-size: 0.85rem;
}
.legend-title { font-weight: 700; color: var(--c-olive); margin-bottom: 8px; font-size: 0.82rem; letter-spacing: 0.12em; }
.legend-row { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; color: var(--c-beige-dark); font-size: 13px; }
.legend-line {
  display: inline-block;
  width: 32px; height: 4px;
  border-radius: 2px;
  background: #B28F4C;
}
.legend-line.sea { background: #0E4A54; }
.legend-line.ended { background: #8a8a7e; background-image: repeating-linear-gradient(90deg, #8a8a7e 0, #8a8a7e 4px, transparent 4px, transparent 8px); height: 4px; }
.legend-row.nodes { align-items: flex-start; }
.legend-node {
  display: inline-block;
  width: 10px; height: 10px;
  border-radius: 50%;
  border: 1.5px solid #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  margin-top: 2px;
}
.legend-node.origin { background: #0E6B5B; }
.legend-node.dest { background: #B28F4C; width: 12px; height: 12px; }

/* Route detail panel */
.route-detail-panel {
  position: absolute;
  right: 16px; top: 16px; bottom: 16px;
  width: 360px;
  max-width: 42%;
  z-index: 920;
  background: rgba(247,244,235,0.97);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(81, 109, 51, 0.18);
  border: 1px solid rgba(178, 143, 76, 0.15);
  display: flex;
  flex-direction: column;
}
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(178, 143, 76, 0.12);
  flex-shrink: 0;
}
.panel-title-wrap { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 0; }
.panel-type-tag {
  display: inline-block;
  background: var(--c-olive-mid);
  color: #fff;
  font-size: 0.72rem;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  width: fit-content;
}
.panel-title {
  font-size: 1.25rem; font-weight: 700;
  color: var(--c-olive);
  margin: 0;
  letter-spacing: 0.05em;
}
.panel-close {
  width: 28px; height: 28px;
  border: none;
  background: var(--c-paper-3);
  color: var(--c-beige-dark);
  font-size: 1.2rem;
  line-height: 1;
  border-radius: 50%;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.panel-close:hover { background: var(--c-gold); color: #fff; }
.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px 20px;
}
.panel-scroll::-webkit-scrollbar { width: 6px; }
.panel-scroll::-webkit-scrollbar-thumb { background: rgba(178,143,76,0.3); border-radius: 3px; }
.panel-scroll::-webkit-scrollbar-thumb:hover { background: rgba(178,143,76,0.5); }
.detail-year { margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px dashed rgba(178,143,76,0.25); }
.detail-year-label { font-size: 0.78rem; color: var(--c-beige); letter-spacing: 0.15em; display: block; margin-bottom: 4px; }
.detail-year-value { font: 900 22px/1 var(--serif); color: var(--c-gold-deep); }
.detail-section-label { font-size: 0.78rem; font-weight: 700; color: var(--c-gold); letter-spacing: 0.12em; margin-bottom: 6px; }
.detail-section-label.with-icon { display: inline-flex; align-items: center; gap: 6px; }
.detail-note { margin-bottom: 14px; }
.detail-note p, .detail-source p { font-size: 0.85rem; line-height: 1.7; color: #555; margin: 0; }
.detail-source { margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px dashed rgba(178,143,76,0.25); }
.detail-source p { color: var(--c-beige); font-size: 0.8rem; }
.detail-history ul { margin: 0; padding-left: 18px; }
.detail-history li { font-size: 0.83rem; line-height: 1.65; color: #555; margin-bottom: 5px; }

/* History panel */
.history-panel {
  position: absolute;
  right: 16px; top: 16px;
  width: 320px; max-width: 36%;
  z-index: 920;
  background: rgba(247, 244, 235, 0.96);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 14px 18px;
  box-shadow: 0 4px 20px rgba(81, 109, 51, 0.12);
  border: 1px solid rgba(178, 143, 76, 0.2);
}
.history-title { font: 700 14px/1 var(--serif); color: var(--c-olive); margin-bottom: 10px; letter-spacing: 0.08em; }
.history-panel ul { margin: 0; padding-left: 18px; }
.history-panel li { font-size: 0.83rem; line-height: 1.7; color: #555; margin-bottom: 5px; }

/* Panel animations */
.panel-slide-enter-active, .panel-slide-leave-active { transition: all 0.35s ease; }
.panel-slide-enter-from, .panel-slide-leave-to { opacity: 0; transform: translateX(24px); }
.panel-fade-enter-active, .panel-fade-leave-active { transition: all 0.3s ease; }
.panel-fade-enter-from, .panel-fade-leave-to { opacity: 0; transform: translateY(-6px); }

/* Timeline */
.timeline-panel {
  max-width: 1380px;
  margin: 14px auto 0;
  padding: 14px 20px 18px;
  background: rgba(247,244,235,0.92);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  border: 1px solid rgba(178,143,76,0.18);
  box-shadow: 0 4px 18px rgba(81,109,51,0.06);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
.stat-card {
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(255,255,255,0.7), rgba(239,233,218,0.5));
  border-radius: 10px;
  border: 1px solid rgba(178,143,76,0.15);
}
.stat-label { font-size: 0.75rem; color: var(--c-beige-dark); letter-spacing: 0.08em; margin-bottom: 4px; }
.stat-num { font: 900 24px/1 var(--serif); color: var(--c-olive); }

.slider-wrap { position: relative; padding: 18px 10px 14px; }
.dynasty-ticks {
  position: relative;
  height: 36px;
  margin-bottom: 8px;
}
.dynasty-ticks .tick {
  position: absolute;
  top: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateX(-50%);
}
.tick-line {
  width: 1px; height: 16px;
  background: rgba(178,143,76,0.4);
  margin-bottom: 4px;
}
.tick-label {
  font: 600 12px/1 var(--serif);
  color: var(--c-beige-dark);
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.year-slider {
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(90deg,
    #C8462E 0%, #C8462E 14%,
    #5C9EAF 14%, #5C9EAF 33%,
    #5C7C3A 33%, #5C7C3A 40%,
    #B28F4C 40%, #B28F4C 70%,
    #2F5D3A 70%, #2F5D3A 90%,
    #8a6f48 90%, #8a6f48 100%);
  outline: none;
  cursor: pointer;
}
.year-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid var(--c-olive);
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: transform 0.15s ease;
}
.year-slider::-webkit-slider-thumb:hover { transform: scale(1.12); }
.year-slider::-moz-range-thumb {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid var(--c-olive);
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  cursor: pointer;
}

.filter-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 12px;
}
.filter-btn {
  padding: 6px 18px;
  border: 1.5px solid var(--c-beige);
  border-radius: 20px;
  background: transparent;
  color: var(--c-beige-dark);
  font: 500 13px/1 var(--serif);
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-btn:hover { border-color: var(--c-olive-mid); color: var(--c-olive); }
.filter-btn.active {
  background: var(--c-gold);
  border-color: var(--c-gold);
  color: #fff;
  font-weight: 600;
}

:deep(.route-tip) {
  background: var(--c-olive) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  border-radius: 6px;
  padding: 6px 10px !important;
  font: 500 12px/1.5 var(--serif);
}
:deep(.route-tip::before) { border-top-color: var(--c-olive) !important; }

/* ---------- 全局适配 ---------- */
@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .ch4-stage { height: calc(100vh - 420px); min-height: 460px; }
  .modern-stage { height: calc(100vh - 300px); min-height: 460px; }
  .modern-country-panel {
    position: absolute;
    top: auto; bottom: 8px; right: 8px; left: 8px;
    width: auto; max-width: none; max-height: 45%;
  }
  .route-detail-panel {
    position: absolute;
    top: auto; bottom: 8px; right: 8px; left: 8px;
    width: auto; max-width: none; max-height: 50%;
  }
  .history-panel { width: calc(100% - 16px); max-width: none; top: auto; bottom: 16px; right: 8px; left: 8px; }
}
</style>
