<template>
  <section class="chapter chapter-4" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="肆"
      title="一叶行远"
      desc="小小一叶茶叶踏出深山，顺着古道、江河辗转流通，从地方风物变成流通四方的货品，开启漫长的远行之路。"
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
          <div ref="mapEl" class="map"></div>

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

          <!-- 信息卡 - 渐入渐出 -->
          <transition name="card-fade" mode="out-in">
            <div v-if="selectedRoute" class="route-detail-panel" :key="selectedRoute.id || selectedRoute.origin + selectedRoute.startYear">
              <div class="panel-header">
                <div class="panel-title-wrap">
                  <span class="panel-type-tag">{{ selectedRoute.type || '贸易路线' }}</span>
                  <h3 class="panel-title">{{ routeFromTo }}</h3>
                </div>
                <button class="panel-close" @click="selectedRoute = null">×</button>
              </div>
              <div class="panel-scroll">
                <div class="detail-year">
                  <span class="detail-year-label">年代</span>
                  <span class="detail-year-value">{{ selectedRoute.yearText || selectedRoute.startYear + '年' }}</span>
                </div>
                <div class="detail-note">
                  <div class="detail-section-label">路线纪事</div>
                  <p>{{ selectedRoute.note || '暂无详细记录' }}</p>
                </div>
                <div class="detail-source">
                  <div class="detail-section-label">史料来源</div>
                  <p>{{ selectedRoute.source || '待考证' }}</p>
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
              ref="sliderInput"
            />
          </div>

          <!-- 播放控制区 - 在时间轴下方 -->
          <div class="timeline-controls">
            <button class="action-btn" :class="{ playing: isPlaying }" @click="togglePlay">
              <span v-if="!isPlaying" class="btn-icon">▶</span>
              <span v-else class="btn-icon">❚❚</span>
              <span class="btn-text">{{ isPlaying ? '暂停' : '播放' }}</span>
            </button>
            <button class="action-btn secondary" @click="resetView">
              <span class="btn-icon">↺</span>
              <span class="btn-text">重置</span>
            </button>
            <span class="step-indicator" v-if="totalSteps > 0">
              {{ currentStep + 1 }} / {{ totalSteps }}
            </span>
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
      </div><!-- end ch4-view-ancient -->

      <!-- ============================== Tab: 当代贸易情况 ============================== -->
      <div v-show="ch4Tab === 'modern'" class="ch4-view ch4-view-modern">
        <div class="modern-topbar">
          <div class="modern-title">
            <span class="title-badge" :class="{ world: !isModernChinaMode }">
              {{ isModernChinaMode ? '🇨🇳 选择省份' : ' ' + (selectedModernProvince || '中国') + ' → 世界' }}
            </span>
            <span class="title-sub" v-if="isModernChinaMode">点击任意省份，查看该省茶叶出口全球流向</span>
            <span class="title-sub" v-if="!isModernChinaMode && modernProvinceInfo.flows.length">{{ modernYear }}年 出口总额 <b class="hl-num">{{ fmtNum(modernProvinceInfo.provinceValue / 1e8) }}</b> 亿元，覆盖 <b class="hl-num">{{ modernProvinceInfo.flows.length }}</b> 个主要国家</span>
            <span class="title-sub" v-else-if="!isModernChinaMode">{{ modernYear }}年 出口总额 <b class="hl-num">{{ fmtNum(modernProvinceInfo.provinceValue / 1e8) }}</b> 亿元，暂无主要出口目的地数据</span>
          </div>
          <div class="modern-controls">
            <div class="year-select">
              <span class="slider-label">出口年份</span>
              <select v-model.number="modernYear" @change="onModernYearChange" class="select-input">
                <option v-for="y in modernYears" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="ch4-stage modern-stage">
          <div ref="modernMapEl" class="map modern-map"></div>

          <!-- 悬浮信息卡 -->
          <transition name="panel-fade">
            <div v-if="isModernChinaMode && hoveredProvince" class="hover-card">
              <div class="hc-title">{{ hoveredProvince.name }}</div>
              <div class="hc-row"><span>出口额</span><b>{{ fmtNum(hoveredProvince.value / 1e8) }} 亿元</b></div>
              <div class="hc-row"><span>全国占比</span><b>{{ hoveredProvince.share }}%</b></div>
            </div>
          </transition>

          <!-- 世界模式：主要出口目的地 Top10 -->
          <transition name="panel-slide">
            <div v-if="!isModernChinaMode && modernProvinceInfo.flows.length" class="modern-country-panel">
              <div class="panel-header">
                <div class="panel-title-wrap">
                  <span class="panel-type-tag modern-tag">全球流向</span>
                  <h3 class="panel-title">{{ selectedModernProvince }} · 主要出口目的地</h3>
                </div>
              </div>
              <div class="panel-scroll">
                <div
                  v-for="(f, i) in modernProvinceInfo.flows.slice(0, 10)"
                  :key="f.country"
                  class="country-row"
                  :style="{ '--w': Math.max(8, Math.min(100, f.value / modernProvinceInfo.flows[0].value * 100)) + '%' }"
                  @mouseenter="highlightFlowCountry(f.country, true)"
                  @mouseleave="highlightFlowCountry(f.country, false)"
                >
                  <div class="cr-rank">{{ i + 1 }}</div>
                  <div class="cr-name">{{ f.country }}</div>
                  <div class="cr-bar-wrap"><div class="cr-bar"></div></div>
                  <div class="cr-val">{{ fmtNum(f.value / 1e8) }}<span class="unit">亿元</span></div>
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
import { assetUrl } from '../utils/base.js'
import {
  PROVINCE_CENTER,
  AVAILABLE_YEARS as MODERN_YEARS,
  getProvinceExports,
  estimateProvinceFlows,
} from '../config/ch4-modern.js'

const props = defineProps({ id: { type: String, required: true } })

// ============================= Tab System =============================
const ch4Tabs = [
  { key: 'ancient', label: '一叶行远·古代贸易发展', icon: '' },
  { key: 'modern', label: '一叶行远·当代贸易情况', icon: '' },
]
const ch4Tab = ref('ancient')
function switchCh4Tab(k) {
  ch4Tab.value = k
  setTimeout(() => {
    if (k === 'ancient' && map) map.invalidateSize()
    if (k === 'modern' && modernMap) {
      modernMap.invalidateSize()
      if (isModernChinaMode.value) fitModernChinaBounds()
      else fitModernWorldBounds()
    }
  }, 60)
}

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
  ['荷兰', '阿姆斯特丹', 4.9041, 52.3676], ['英国', '伦敦', -0.1276, 51.5072], ['美国', '华盛顿', -77.0369, 38.9072],
  ['法国', '巴黎', 2.3522, 48.8566], ['德国', '柏林', 13.405, 52.52], ['丹麦', '哥本哈根', 12.5683, 55.6761],
  ['瑞典', '斯德哥尔摩', 18.0686, 59.3293], ['日本', '东京', 139.6917, 35.6895], ['俄国', '莫斯科', 37.6173, 55.7558],
  ['俄罗斯', '莫斯科', 37.6173, 55.7558], ['敖德萨', '莫斯科', 37.6173, 55.7558], ['印度', '新德里', 77.209, 28.6139],
  ['尼泊尔', '加德满都', 85.324, 27.7172], ['缅甸', '内比都', 96.0785, 19.7633], ['欧洲', '布鲁塞尔', 4.3517, 50.8503]
]
function namedCapital(text) {
  const hit = capitals.find(function(item) {
    return String(text).includes(item[0])
  })
  return hit ? { name: hit[1], lon: hit[2], lat: hit[3] } : null
}
function visualPoints(r) {
  try {
    if (kind(r) !== 'sea') return r.points || []
    var chinese = (r.points || []).find(inChina) || { name: '广州', lon: 113.2644, lat: 23.1291 }
    var dest = namedCapital(r.destination)
    if (!dest && r.points && r.points.length && inChina(r.points[r.points.length - 1])) {
      dest = namedCapital(r.origin)
    }
    if (!dest && r.points) {
      var foreign = r.points.filter(function(p) { return !inChina(p) })
      dest = foreign.length ? foreign[foreign.length - 1] : null
    }
    return dest ? [chinese, dest] : (r.points || [])
  } catch (e) {
    return r.points || []
  }
}
function curved(a, b, steps) {
  if (steps === undefined) steps = 28
  var dist = Math.hypot(b.lon - a.lon, b.lat - a.lat)
  var lift = Math.min(22, dist * 0.13)
  var out = []
  for (var i = 0; i <= steps; i++) {
    var t = i / steps
    out.push([Math.max(-85, Math.min(85, a.lat + (b.lat - a.lat) * t + Math.sin(Math.PI * t) * lift)), a.lon + (b.lon - a.lon) * t])
  }
  return out
}
function coords(points) {
  if (!points || points.length < 2) return []
  var out = []
  for (var i = 1; i < points.length; i++) {
    var seg = curved(points[i - 1], points[i])
    if (i > 1) seg.shift()
    out.push.apply(out, seg)
  }
  return out
}
function getAllDataYears() {
  var years = new Set()
  for (var i = 0; i < TEA_TRADE_DATA.length; i++) {
    var r = TEA_TRADE_DATA[i]
    if (r.startYear != null) years.add(Number(r.startYear))
    if (r.endYear != null) years.add(Number(r.endYear))
  }
  years.add(618); years.add(1945)
  return Array.from(years).sort(function(a, b) { return a - b })
}
var allDataYears = getAllDataYears()
function getClosestDataYear(y) {
  var closest = allDataYears[0], minDiff = Infinity
  for (var i = 0; i < allDataYears.length; i++) {
    var x = allDataYears[i]
    var d = Math.abs(x - y)
    if (d < minDiff) { minDiff = d; closest = x }
  }
  return closest
}
function getNextDataYear(y) {
  for (var i = 0; i < allDataYears.length; i++) {
    var x = allDataYears[i]
    if (x > y) return x
  }
  return allDataYears[allDataYears.length - 1]
}
function getDynastyName(y) {
  for (var i = 0; i < dynasties.length; i++) {
    var d = dynasties[i]
    if (y >= d.start && y <= d.end) return d.name
  }
  return ''
}

var sectionEl = ref(null)
var mapEl = ref(null)
var sliderInput = ref(null)
var currentYear = ref(618)
var filter = ref('all')
var isPlaying = ref(false)
var selectedRoute = ref(null)
var showHint = ref(true)
var introDone = ref(false)

var currentStep = ref(0)
var totalSteps = ref(0)
var stepRoutes = ref([])

var eraMode = ref('all')

var map = null
var routeLayer = null
var nodeLayer = null
var playTimer = null

var stats = reactive({
  activeCount: 0,
  endedCount: 0,
  routeCount: 0,
  countryCount: 0,
})

var dynastyName = computed(function() { return getDynastyName(currentYear.value) })
var dynastyClass = computed(function() {
  var n = dynastyName.value
  if (n === '唐代') return 'tang'
  if (n === '宋代') return 'song'
  if (n === '元代') return 'yuan'
  if (n === '明代') return 'ming'
  if (n === '清代') return 'qing'
  if (n === '抗战时期') return 'kangzhan'
  return 'default'
})
var currentEvents = computed(function() { return getEventsByYear(currentYear.value) })
var routeFromTo = computed(function() {
  if (!selectedRoute.value) return ''
  var vp = visualPoints(selectedRoute.value)
  if (!vp || vp.length === 0) return ''
  var fromName = vp[0] && vp[0].name ? vp[0].name : (selectedRoute.value.origin || '起点')
  var toName = vp[vp.length - 1] && vp[vp.length - 1].name ? vp[vp.length - 1].name : (selectedRoute.value.destination || '终点')
  return fromName + ' → ' + toName
})
var routeHistoryEvents = computed(function() {
  if (!selectedRoute.value) return []
  return getEventsByYear(selectedRoute.value.startYear)
})

watch(filter, function() {
  render()
})

function onSliderInput(e) {
  var v = Number(e.target.value)
  currentYear.value = getClosestDataYear(v)
  eraMode.value = 'era'
  renderByEra(currentYear.value)
}

function onSliderChange(e) {
  var v = Number(e.target.value)
  currentYear.value = getClosestDataYear(v)
  eraMode.value = 'era'
  renderByEra(currentYear.value)
}

function renderByEra(year) {
  if (!map || !routeLayer || !nodeLayer) return
  
  var routes = []
  for (var i = 0; i < TEA_TRADE_DATA.length; i++) {
    var r = TEA_TRADE_DATA[i]
    try {
      var k = kind(r)
      if (filter.value === 'sea' && k !== 'sea') continue
      if (filter.value === 'land' && k !== 'land') continue
      
      if (r.startYear === undefined || r.startYear === null) continue
      
      var state = getRouteState(r, year)
      if (state === 'not_started') continue
      
      routes.push(r)
    } catch (e) {
      console.warn('处理路线时出错，已跳过:', r, e)
    }
  }
  
  var sortedRoutes = routes.sort(function(a, b) {
    var aYear = Number(a.startYear) || 0
    var bYear = Number(b.startYear) || 0
    return aYear - bYear
  })
  
  stepRoutes.value = sortedRoutes
  totalSteps.value = sortedRoutes.length
  
  if (totalSteps.value === 0) {
    if (routeLayer) routeLayer.clearLayers()
    if (nodeLayer) nodeLayer.clearLayers()
    stats.activeCount = 0
    stats.endedCount = 0
    stats.routeCount = 0
    stats.countryCount = 0
    return
  }
  
  renderAllRoutes(sortedRoutes, year)
}

function renderAllRoutes(routes, year) {
  if (!map || !routeLayer || !nodeLayer) return
  
  routeLayer.clearLayers()
  nodeLayer.clearLayers()
  
  var activeNodes = new Map()
  var activeCount = 0
  var endedCount = 0
  var routeCount = 0
  
  routes.forEach(function(r, idx) {
    try {
      var k = kind(r)
      var state = getRouteState(r, year)
      
      var isActive = state === 'active' || state === 'active_permanent'
      var isEnded = state === 'ended'
      
      var vp = visualPoints(r)
      if (!vp || vp.length < 2) return
      
      var c = coords(vp)
      if (!c || c.length < 2) return
      
      var baseColor = k === 'sea' ? '#196c58' : '#d4933b'
      
      if (isActive) activeCount++
      if (isEnded) endedCount++
      routeCount += Math.max(0, (vp.length || 0) - 1)
      
      var line = L.polyline(c, {
        color: isActive ? baseColor : '#8a8270',
        weight: isActive ? 2.7 : 1.5,
        opacity: isActive ? 0.92 : 0.45,
        smoothFactor: 0.5,
        dashArray: isEnded ? '6 4' : null,
        interactive: true,
      })
      
      if (isActive) {
        var totalLen = Math.max(1, c.length * 20)
        line.setStyle({ dashArray: totalLen, dashOffset: totalLen })
        setTimeout(function() {
          try { line.setStyle({ dashOffset: 0 }) } catch (e) {}
        }, 100 + idx * 60)
      }
      
      line.on('click', function(e) {
        L.DomEvent.stopPropagation(e)
        selectedRoute.value = r
        showHint.value = false
      })
      
      var fromName = (vp.length && vp[0] && vp[0].name) ? vp[0].name : (r.origin || '起点')
      var toName = (vp.length && vp[vp.length - 1] && vp[vp.length - 1].name) ? vp[vp.length - 1].name : (r.destination || '终点')
      
      line.bindTooltip((r.yearText || '') + '｜' + fromName + '→' + toName, {
        sticky: true,
        direction: 'top',
        offset: [0, -6],
        className: 'ch4-tip',
      })
      
      line.addTo(routeLayer)
      
      if (isActive && vp && vp.length >= 2) {
        vp.forEach(function(p, pIdx) {
          if (!p || p.lon === undefined || p.lat === undefined) return
          var key = p.lon + ',' + p.lat
          if (!activeNodes.has(key)) {
            var isOrigin = pIdx === 0
            var isDest = pIdx === vp.length - 1
            activeNodes.set(key, { lon: p.lon, lat: p.lat, name: p.name, isOrigin: isOrigin, isCapital: isDest && !inChina(p) })
          }
        })
      }
    } catch (e) {
      console.warn('渲染单条路线时出错:', r, e)
    }
  })
  
  var nodeIdx = 0
  var nodeIterator = activeNodes.values()
  var nodeResult = nodeIterator.next()
  while (!nodeResult.done) {
    var p = nodeResult.value
    try {
      var isCapital = p.isCapital && !p.isOrigin
      var radius = isCapital ? 7 : 5
      var fillColor = p.isOrigin ? '#196c58' : (isCapital ? '#B28F4C' : '#5C7C3A')
      
      var marker = L.circleMarker([p.lat || 0, p.lon || 0], {
        radius: 0,
        fillColor: fillColor,
        color: '#ffffff',
        weight: 2,
        fillOpacity: 0.95,
      }).bindTooltip(p.name || '节点', {
        permanent: false,
        direction: 'top',
        offset: [0, -6],
        className: 'ch4-node-tip',
      }).addTo(nodeLayer)
      
      setTimeout(function(marker, radius) {
        return function() {
          try { marker.setStyle({ radius: radius }) } catch (e) {}
        }
      }(marker, radius), 200 + nodeIdx * 60)
      nodeIdx++
    } catch (e) {
      console.warn('渲染节点时出错:', p, e)
    }
    nodeResult = nodeIterator.next()
  }
  
  stats.activeCount = activeCount
  stats.endedCount = endedCount
  stats.routeCount = routeCount
  stats.countryCount = activeNodes.size
}

function updateDynastyInfo() {}

function togglePlay() {
  if (totalSteps.value === 0) {
    console.warn('没有可播放的路线')
    return
  }
  
  eraMode.value = 'all'
  
  if (currentStep.value >= totalSteps.value - 1 && !isPlaying.value) {
    currentStep.value = 0
    renderStep(0)
    syncSliderToStep(0)
  }
  
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    if (currentStep.value >= totalSteps.value - 1) {
      currentStep.value = 0
      renderStep(0)
      syncSliderToStep(0)
    }
    
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
    
    playTimer = setInterval(function() {
      var next = currentStep.value + 1
      if (next < totalSteps.value) {
        currentStep.value = next
        renderStep(next)
        syncSliderToStep(next)
      } else {
        isPlaying.value = false
        if (playTimer) {
          clearInterval(playTimer)
          playTimer = null
        }
      }
    }, 4000)
  } else {
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
  }
}

function syncSliderToStep(stepIndex) {
  if (stepIndex >= stepRoutes.value.length) return
  var route = stepRoutes.value[stepIndex]
  if (!route) return
  
  var year = Number(route.startYear) || 618
  currentYear.value = year
  
  if (sliderInput.value) {
    sliderInput.value.value = year
  }
}

function renderStep(stepIndex) {
  if (!map || !routeLayer || !nodeLayer) return
  
  if (stepIndex >= stepRoutes.value.length) {
    console.warn('步骤索引超出范围:', stepIndex, stepRoutes.value.length)
    return
  }
  
  eraMode.value = 'all'
  
  routeLayer.clearLayers()
  nodeLayer.clearLayers()
  
  var routesToShow = stepRoutes.value.slice(0, stepIndex + 1)
  var activeNodes = new Map()
  var activeCount = 0
  var endedCount = 0
  var routeCount = 0
  
  routesToShow.forEach(function(r, idx) {
    try {
      var k = kind(r)
      if (filter.value === 'sea' && k !== 'sea') return
      if (filter.value === 'land' && k !== 'land') return
      
      var displayYear = Number(r.startYear) + 50
      var state = getRouteState(r, displayYear)
      
      var isActive = state === 'active' || state === 'active_permanent'
      var isEnded = state === 'ended'
      
      var vp = visualPoints(r)
      if (!vp || vp.length < 2) return
      
      var c = coords(vp)
      if (!c || c.length < 2) return
      
      var baseColor = k === 'sea' ? '#196c58' : '#d4933b'
      
      if (isActive) activeCount++
      if (isEnded) endedCount++
      routeCount += Math.max(0, (vp.length || 0) - 1)
      
      var line = L.polyline(c, {
        color: isActive ? baseColor : '#8a8270',
        weight: isActive ? 2.7 : 1.5,
        opacity: isActive ? 0.92 : 0.45,
        smoothFactor: 0.5,
        dashArray: isEnded ? '6 4' : null,
        interactive: true,
      })
      
      if (isActive) {
        var totalLen = Math.max(1, c.length * 20)
        line.setStyle({ dashArray: totalLen, dashOffset: totalLen })
        setTimeout(function() {
          try { line.setStyle({ dashOffset: 0 }) } catch (e) {}
        }, 300 + idx * 150)
      }
      
      line.on('click', function(e) {
        L.DomEvent.stopPropagation(e)
        selectedRoute.value = r
        showHint.value = false
      })
      
      var fromName = (vp.length && vp[0] && vp[0].name) ? vp[0].name : (r.origin || '起点')
      var toName = (vp.length && vp[vp.length - 1] && vp[vp.length - 1].name) ? vp[vp.length - 1].name : (r.destination || '终点')
      
      line.bindTooltip((r.yearText || '') + '｜' + fromName + '→' + toName, {
        sticky: true,
        direction: 'top',
        offset: [0, -6],
        className: 'ch4-tip',
      })
      
      line.addTo(routeLayer)
      
      if (isActive && vp && vp.length >= 2) {
        vp.forEach(function(p, pIdx) {
          if (!p || p.lon === undefined || p.lat === undefined) return
          var key = p.lon + ',' + p.lat
          if (!activeNodes.has(key)) {
            var isOrigin = pIdx === 0
            var isDest = pIdx === vp.length - 1
            activeNodes.set(key, { lon: p.lon, lat: p.lat, name: p.name, isOrigin: isOrigin, isCapital: isDest && !inChina(p) })
          }
        })
      }
    } catch (e) {
      console.warn('渲染单条路线时出错:', r, e)
    }
  })
  
  var nodeIdx = 0
  var nodeIterator = activeNodes.values()
  var nodeResult = nodeIterator.next()
  while (!nodeResult.done) {
    var p = nodeResult.value
    try {
      var isCapital = p.isCapital && !p.isOrigin
      var radius = isCapital ? 7 : 5
      var fillColor = p.isOrigin ? '#196c58' : (isCapital ? '#B28F4C' : '#5C7C3A')
      
      var marker = L.circleMarker([p.lat || 0, p.lon || 0], {
        radius: 0,
        fillColor: fillColor,
        color: '#ffffff',
        weight: 2,
        fillOpacity: 0.95,
      }).bindTooltip(p.name || '节点', {
        permanent: false,
        direction: 'top',
        offset: [0, -6],
        className: 'ch4-node-tip',
      }).addTo(nodeLayer)
      
      setTimeout(function(marker, radius) {
        return function() {
          try { marker.setStyle({ radius: radius }) } catch (e) {}
        }
      }(marker, radius), 300 + nodeIdx * 80)
      nodeIdx++
    } catch (e) {
      console.warn('渲染节点时出错:', p, e)
    }
    nodeResult = nodeIterator.next()
  }
  
  stats.activeCount = activeCount
  stats.endedCount = endedCount
  stats.routeCount = routeCount
  stats.countryCount = activeNodes.size
  
  if (stepIndex < stepRoutes.value.length) {
    var currentRoute = stepRoutes.value[stepIndex]
    if (currentRoute) {
      selectedRoute.value = currentRoute
      showHint.value = false
    }
  }
}

function render() {
  if (!map || !routeLayer || !nodeLayer) return
  
  var routes = []
  for (var i = 0; i < TEA_TRADE_DATA.length; i++) {
    var r = TEA_TRADE_DATA[i]
    try {
      var k = kind(r)
      if (filter.value === 'sea' && k !== 'sea') continue
      if (filter.value === 'land' && k !== 'land') continue
      
      if (r.startYear === undefined || r.startYear === null) {
        console.warn('路线缺少 startYear，已跳过:', r)
        continue
      }
      
      routes.push(r)
    } catch (e) {
      console.warn('处理路线时出错，已跳过:', r, e)
    }
  }
  
  stepRoutes.value = routes.sort(function(a, b) {
    var aYear = Number(a.startYear) || 0
    var bYear = Number(b.startYear) || 0
    return aYear - bYear
  })
  
  totalSteps.value = stepRoutes.value.length
  
  if (totalSteps.value === 0) {
    console.warn('没有可显示的路线数据')
    if (routeLayer) routeLayer.clearLayers()
    if (nodeLayer) nodeLayer.clearLayers()
    stats.activeCount = 0
    stats.endedCount = 0
    stats.routeCount = 0
    stats.countryCount = 0
    return
  }
  
  if (eraMode.value === 'era') {
    renderByEra(currentYear.value)
    return
  }
  
  if (!isPlaying.value) {
    currentStep.value = 0
    renderStep(0)
    setTimeout(function() { syncSliderToStep(0) }, 100)
  }
}

function resetView() {
  currentYear.value = 618
  filter.value = 'all'
  eraMode.value = 'all'
  if (map) map.flyTo([30, 90], 3, { duration: 1 })
  if (isPlaying.value) {
    isPlaying.value = false
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
  }
  showHint.value = true
  selectedRoute.value = null
  currentStep.value = 0
  render()
  setTimeout(function() {
    if (sliderInput.value) {
      sliderInput.value.value = 618
    }
  }, 100)
}

function initMap() {
  map = L.map(mapEl.value, {
    center: [30, 90],
    zoom: 3,
    minZoom: 2,
    maxZoom: 7,
    worldCopyJump: true,
    zoomControl: false,
    attributionControl: false,
  })

  L.control.zoom({ position: 'bottomright' }).addTo(map)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19,
    attribution: ''
  }).addTo(map)

  routeLayer = L.layerGroup().addTo(map)
  nodeLayer = L.layerGroup().addTo(map)

  map.on('click', function() {
    if (selectedRoute.value) {
      selectedRoute.value = null
    }
  })
}

function loadChinaBoundary() {
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    .then(function(r) { return r.json() })
    .then(function(geo) {
      if (!map) return
      L.geoJSON(geo, {
        interactive: false,
        style: function() {
          return {
            color: '#B28F4C',
            weight: 2,
            opacity: 0.9,
            fillColor: '#F7F4EB',
            fillOpacity: 0.5,
          }
        },
      }).addTo(map)
    })
    .catch(function(err) { console.warn('中国边界加载失败:', err) })
}

function onKeydown(e) {
  if (e.code === 'ArrowRight') {
    var next = getNextDataYear(currentYear.value)
    if (next > currentYear.value) {
      currentYear.value = next
      renderByEra(currentYear.value)
    }
  } else if (e.code === 'ArrowLeft') {
    var idx = allDataYears.indexOf(currentYear.value)
    if (idx > 0) {
      currentYear.value = allDataYears[idx - 1]
      renderByEra(currentYear.value)
    }
  } else if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  }
}

function onIntroDone() {
  introDone.value = true
  setTimeout(function() {
    if (map) map.invalidateSize()
    render()
  }, 300)
}

// ==========================================================================
// Part 2: 当代贸易情况
// ==========================================================================
var modernMapEl = ref(null)
var modernYears = MODERN_YEARS.filter(function(y) { return y >= 2015 && y <= 2026 })
var modernYear = ref(2024)
var isModernChinaMode = ref(true)
var selectedModernProvince = ref(null)
var hoveredProvince = ref(null)

var modernMap = null
var modernProvLayer = null
var modernFlowLayer = null
var modernMarkersLayer = null
var modernHighlightedCountry = null

var modernProvinceInfo = reactive({
  provinceValue: 0,
  totalValue: 0,
  flows: [],
  year: 2024,
})

function fmtNum(n) {
  if (n == null || isNaN(n)) return '0.00'
  return Number(n).toFixed(2)
}

function fitModernChinaBounds() {
  if (!modernMap) return
  modernMap.fitBounds([[18, 73], [54, 135]], { padding: [40, 40], maxZoom: 5, animate: true })
}
function fitModernWorldBounds() {
  if (!modernMap) return
  // 右侧留出面板宽度（320px + 16px外边距 + 24px间距 = 360px）
  // 左侧留 24px，上下各 40px
  modernMap.fitBounds([[-45, -40], [55, 150]], { paddingTopLeft: [40, 24], paddingBottomRight: [40, 360], animate: true })
}

// 窗口大小变化时重新调整地图
function onWindowResize() {
  if (!modernMap) return
  modernMap.invalidateSize()
  if (isModernChinaMode.value) {
    fitModernChinaBounds()
  } else {
    fitModernWorldBounds()
  }
}

function buildProvinceChoropleth() {
  var yearData = getProvinceExports(modernYear.value)
  var provinceMap = {}
  var total = yearData.reduce(function(s, p) { return s + p.value }, 0)
  yearData.forEach(function(p) { provinceMap[p.name] = { value: p.value, share: total ? (p.value / total * 100).toFixed(1) : 0 } })

  // 判断是否为"无数据"省份：出口额为0 或 全国占比为0.00%
  var isZeroProvince = function(info) {
    if (!info) return true
    if (!info.value || info.value <= 0) return true
    var sh = provinceMap[info.name] ? parseFloat(provinceMap[info.name].share) : 0
    if (sh <= 0) return true
    return false
  }

  var positiveYearData = yearData.filter(function(p) { return p.value > 0 })
  var maxV = Math.max.apply(null, positiveYearData.map(function(p) { return p.value }).concat([1]))
  var colorFor = function(v) {
    if (!v || v <= 0) return '#F7F4EB'  // 0 出口省份使用最浅纸色
    var t = Math.log10(Math.max(v, 1)) / Math.log10(maxV + 1)
    var lerp = function(a, b, k) { return a + (b - a) * k }
    var stop1 = { r: 247, g: 244, b: 235 }
    var stop2 = { r: 178, g: 143, b: 76 }
    var stop3 = { r: 81, g: 109, b: 51 }
    var col = t < 0.5
      ? { r: lerp(stop1.r, stop2.r, t / 0.5), g: lerp(stop1.g, stop2.g, t / 0.5), b: lerp(stop1.b, stop2.b, t / 0.5) }
      : { r: lerp(stop2.r, stop3.r, (t - 0.5) / 0.5), g: lerp(stop2.g, stop3.g, (t - 0.5) / 0.5), b: lerp(stop2.b, stop3.b, (t - 0.5) / 0.5) }
    return 'rgb(' + Math.round(col.r) + ',' + Math.round(col.g) + ',' + Math.round(col.b) + ')'
  }

  var matchProvince = function(featureName) {
    for (var i = 0; i < yearData.length; i++) {
      var p = yearData[i]
      if (p.name === featureName) return p
      var clean = p.name.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政/g, '')
      var fClean = featureName.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政/g, '')
      if (clean && (clean === fClean || p.name.includes(featureName) || featureName.includes(clean))) return p
    }
    return null
  }

  // 判断省份是否可点击：非零出口 且 非零占比 且 不是台湾省
  var isClickable = function(info, featureName) {
    if (isZeroProvince(info)) return false
    var nm = (info && info.name) || featureName || ''
    if (/台湾/.test(nm)) return false
    return true
  }

  return { provinceMap: provinceMap, colorFor: colorFor, matchProvince: matchProvince, isClickable: isClickable, isZeroProvince: isZeroProvince }
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
  var _build = buildProvinceChoropleth()
  var provinceMap = _build.provinceMap
  var colorFor = _build.colorFor
  var matchProvince = _build.matchProvince
  var isClickable = _build.isClickable
  var isZeroProvince = _build.isZeroProvince

  fetch(assetUrl('data/2/china-provinces.geojson'))
    .then(function(r) { return r.json() })
    .then(function(geo) {
      modernProvLayer = L.geoJSON(geo, {
        style: function(f) {
          var name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          var info = matchProvince(name)
          var zero = isZeroProvince(info)
          return {
            color: zero ? '#B28F4C' : '#7e7866',
            weight: zero ? 0.4 : 0.6,
            fillColor: zero ? '#F7F4EB' : colorFor(info.value),
            fillOpacity: zero ? 1.0 : 0.88,
            dashArray: zero ? '4 4' : null,
          }
        },
        onEachFeature: function(f, layer) {
          var name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          var info = matchProvince(name)
          var clickable = isClickable(info, name)
          if (clickable) {
            layer.on('mouseover', function() {
              hoveredProvince.value = info ? { name: info.name, value: info.value, share: provinceMap[info.name] ? provinceMap[info.name].share : 0 } : null
              layer.setStyle({ weight: 1.6, color: '#516D33' })
              layer.bringToFront()
            })
            layer.on('mouseout', function() {
              hoveredProvince.value = null
              modernProvLayer && modernProvLayer.resetStyle(layer)
            })
            layer.on('click', function() {
              if (!info) return
              enterWorldMode(info.name)
            })
            layer._path && (layer._path.style.cursor = 'pointer')
          } else {
            // 0出口/0占比/台湾省：仅悬浮提示数值，无法点击
            var displayInfo = info || { name: name.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政/g, '') + '省', value: 0 }
            layer.on('mouseover', function() {
              var sh = provinceMap[displayInfo.name] ? provinceMap[displayInfo.name].share : 0
              hoveredProvince.value = { name: displayInfo.name, value: displayInfo.value || 0, share: sh }
              layer.setStyle({ weight: 1.2, color: '#B28F4C' })
              layer.bringToFront()
            })
            layer.on('mouseout', function() {
              hoveredProvince.value = null
              modernProvLayer && modernProvLayer.resetStyle(layer)
            })
          }
        },
      }).addTo(modernMap)
      modernProvLayer.bringToFront()
    })
}

function enterWorldMode(provinceName) {
  selectedModernProvince.value = provinceName
  isModernChinaMode.value = false
  var info = estimateProvinceFlows(provinceName, modernYear.value, 20)
  Object.assign(modernProvinceInfo, info || { provinceValue: 0, totalValue: 0, flows: [], year: modernYear.value })
  modernProvinceInfo.year = modernYear.value

  nextTick(function() {
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
  nextTick(function() {
    if (!modernMap) return
    modernMap.invalidateSize()
    fitModernChinaBounds()
    renderModernChinaProvinces()
  })
}

function highlightFlowCountry(countryName, on) {
  if (!modernFlowLayer || !modernMarkersLayer) return
  modernHighlightedCountry = on ? countryName : null
  modernFlowLayer.eachLayer(function(l) {
    var md = l._flowData
    if (!md) return
    // 跳过命中辅助线
    if (l._isHitHelper) return
    var hl = (md.country === modernHighlightedCountry)
    var base = l._baseStyle || {}
    l.setStyle({
      opacity: hl ? 1 : (modernHighlightedCountry ? base.opacity * 0.18 : base.opacity),
      weight: hl ? (base.weight + 2) : base.weight,
    })
  })
  modernMarkersLayer.eachLayer(function(l) {
    var name = l._country
    if (!name) return
    var hl = (name === modernHighlightedCountry)
    var base = l._baseMarker || {}
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

  var center = PROVINCE_CENTER[provinceName] || PROVINCE_CENTER['浙江省']
  var fromLat = center[0], fromLon = center[1]

  // 阻止事件冒泡到地图 click 空白区返回逻辑
  var stopClick = function(ev) { L.DomEvent.stopPropagation(ev) }

  if (modernProvLayer) { modernMap.removeLayer(modernProvLayer); modernProvLayer = null }
  var _build2 = buildProvinceChoropleth()
  var colorFor2 = _build2.colorFor
  var matchProvince2 = _build2.matchProvince
  var isZeroProvince2 = _build2.isZeroProvince

  fetch(assetUrl('data/2/china-provinces.geojson'))
    .then(function(r) { return r.json() })
    .then(function(geo) {
      modernProvLayer = L.geoJSON(geo, {
        style: function(f) {
          var name = f.properties.name || f.properties.NAME || f.properties.NL_NAME_1 || ''
          var info = matchProvince2(name)
          var zero = isZeroProvince2(info)
          var pClean = provinceName.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政/g, '')
          var fClean = name.replace(/省|市|自治区|壮族|回族|维吾尔|特别行政/g, '')
          var isSelected = pClean === fClean
          if (isSelected) {
            // 选中省份：红色边框 + 金棕色填充，突出显示
            return {
              color: '#C8462E',
              weight: 2.6,
              fillColor: zero ? '#B28F4C' : colorFor2(info.value),
              fillOpacity: 0.92,
              dashArray: zero ? '4 4' : null,
            }
          } else {
            // 其他省份：保留分级设色 (choropleth) 风格
            return {
              color: zero ? '#B28F4C' : '#7e7866',
              weight: zero ? 0.4 : 0.6,
              fillColor: zero ? '#F7F4EB' : colorFor2(info.value),
              fillOpacity: zero ? 1.0 : 0.88,
              dashArray: zero ? '4 4' : null,
            }
          }
        },
        onEachFeature: function(f, layer) {
          layer.on('click', stopClick)
        }
      }).addTo(modernMap)
    })

  if (!info) return
  var flows = info.flows
  if (!flows.length) return

  var maxV = flows[0].value || 1
  modernFlowLayer = L.layerGroup().addTo(modernMap)
  modernMarkersLayer = L.layerGroup().addTo(modernMap)

  // 停止之前可能存在的动画
  if (window._ch4FlowAnimTimers) {
    window._ch4FlowAnimTimers.forEach(function(t) { try { cancelAnimationFrame(t) } catch(e) {} })
    window._ch4FlowAnimTimers = []
  } else {
    window._ch4FlowAnimTimers = []
  }

  // 动画参数
  var FLOW_ANIM_DURATION = 900   // 每条线路从起点到终点的伸展时长 (ms)
  var START_DELAY_STEP = 60      // 每条线路的起始延迟步长 (ms)，按 norm 递减排序

  // 按贸易额从大到小排序，大额先绘制（更强烈的发散感）
  var flowIndexList = flows.map(function(f, i) { return { idx: i, f: f, norm: Math.max(0.05, Math.min(1, f.value / maxV)) } })
  flowIndexList.sort(function(a, b) { return b.norm - a.norm })

  flowIndexList.forEach(function(item, sortIdx) {
    var i = item.idx
    var f = item.f
    var itemNorm = item.norm
    var toLat = f.to[0], toLon = f.to[1]
    var a = { lon: fromLon, lat: fromLat }, b = { lon: toLon, lat: toLat }
    var pts = coords([a, b])
    var totalPts = pts.length
    var t = itemNorm
    var col = 'rgb(' + Math.round(178 + (200 - 178) * t) + ', ' + Math.round(143 - 143 * t * 0.6) + ', ' + Math.round(76 - 76 * t * 0.9) + ')'
    var w = 1.2 + itemNorm * 8
    var tipHtml = '<b>' + provinceName + ' → ' + f.country + '</b><br/>出口额：' + fmtNum(f.value / 1e8) + ' 亿元'

    // ========== 1. 创建线路（初始只含起点，动画中逐点追加）==========
    var startPts = [pts[0]]
    var line = L.polyline(startPts, {
      color: col, weight: w, opacity: 0.45 + itemNorm * 0.45,
      lineCap: 'round', lineJoin: 'round', interactive: false,
      bubblingMouseEvents: true,
    })
    line._flowData = { country: f.country, value: f.value }
    line._baseStyle = { weight: w, opacity: 0.45 + itemNorm * 0.45 }
    line.bindTooltip(tipHtml, { direction: 'top', offset: [0, -6], opacity: 0.96, sticky: true, className: 'route-tip modern-flow-tip' })
    line.on('mouseover', function() {
      highlightFlowCountry(f.country, true)
      var ll = line.getLatLngs()
      if (ll && ll.length) line.openTooltip(ll[ll.length - 1])
    })
    line.on('mouseout', function() { highlightFlowCountry(f.country, false); line.closeTooltip() })
    line.on('click', stopClick)
    line.addTo(modernFlowLayer)

    // ========== 2. 创建 marker（初始 opacity=0, radius=0，动画结尾渐显）==========
    var isTop3 = itemNorm >= 0.5
    var r = isTop3 ? 8 : 5
    var marker = L.circleMarker([toLat, toLon], {
      radius: 0, color: '#fff', weight: 1.5,
      fillColor: isTop3 ? '#C8462E' : '#B28F4C', fillOpacity: 0, opacity: 0,
      interactive: false,
    })
    marker._country = f.country
    marker._baseMarker = { radius: r }
    marker.bindTooltip(tipHtml, { direction: 'top', offset: [0, -6], opacity: 0.96, className: 'route-tip modern-flow-tip' })
    marker.on('mouseover', function() { highlightFlowCountry(f.country, true); marker.openTooltip() })
    marker.on('mouseout', function() { highlightFlowCountry(f.country, false); marker.closeTooltip() })
    marker.on('click', stopClick)
    marker.addTo(modernMarkersLayer)

    // ========== 3. 动画：循序渐进生成线路 ==========
    var startTime = null
    var startDelay = START_DELAY_STEP * sortIdx  // 大额先绘制

    function animateFlow(timestamp) {
      if (!startTime) startTime = timestamp
      var elapsed = timestamp - startTime
      if (elapsed < startDelay) {
        window._ch4FlowAnimTimers.push(requestAnimationFrame(animateFlow))
        return
      }
      var localElapsed = elapsed - startDelay
      var progress = Math.min(1, localElapsed / FLOW_ANIM_DURATION)
      // easeOutCubic: 开头快结尾慢
      var eased = 1 - Math.pow(1 - progress, 3)
      var targetIndex = Math.floor(eased * (totalPts - 1)) + 1
      if (targetIndex < totalPts) {
        var subPts = pts.slice(0, targetIndex)
        line.setLatLngs(subPts)
      } else {
        line.setLatLngs(pts)
      }

      // marker 动画：最后 35% 进度时显示
      if (progress > 0.65) {
        var markerProgress = Math.min(1, (progress - 0.65) / 0.35)
        var markerEased = 1 - Math.pow(1 - markerProgress, 2)
        marker.setStyle({
          radius: markerEased * r,
          fillOpacity: markerEased * 1,
          opacity: markerEased * 0.95,
        })
      }

      if (progress < 1) {
        window._ch4FlowAnimTimers.push(requestAnimationFrame(animateFlow))
      } else {
        // 动画结束：启用交互、添加命中辅助线
        line.setStyle({ interactive: true })
        marker.setStyle({ interactive: true, radius: r, fillOpacity: 1, opacity: 0.95 })

        // 命中辅助线
        var hitLine = L.polyline(pts, {
          color: '#000', weight: Math.max(12, w + 10), opacity: 0.01,
          lineCap: 'round', lineJoin: 'round', interactive: true,
        })
        hitLine._isHitHelper = true
        hitLine._flowData = line._flowData
        hitLine._baseStyle = line._baseStyle
        hitLine.on('mouseover', function() {
          highlightFlowCountry(f.country, true)
          var latlng = pts[Math.floor(pts.length * 0.65)]
          line.openTooltip(latlng)
        })
        hitLine.on('mouseout', function() { highlightFlowCountry(f.country, false); line.closeTooltip() })
        hitLine.on('click', stopClick)
        hitLine.addTo(modernFlowLayer)
        hitLine.bringToFront()
        line.bringToFront()
      }
    }
    window._ch4FlowAnimTimers.push(requestAnimationFrame(animateFlow))
  })

  // 起点 marker（即时显示，带脉冲效果）
  var originMarker = L.circleMarker([fromLat, fromLon], {
    radius: 0, color: '#fff', weight: 3,
    fillColor: '#516D33', fillOpacity: 0,
  })
  originMarker._baseMarker = { radius: 12 }
  originMarker.bindTooltip('<b>' + provinceName + '</b><br/>出口总额 ' + fmtNum(modernProvinceInfo.provinceValue / 1e8) + ' 亿元', { direction: 'top', offset: [0, -8] })
  originMarker.on('click', stopClick)
  originMarker.addTo(modernMarkersLayer)
  // 起点 marker 即时弹出
  var originAnimStart = null
  function animateOrigin(t) {
    if (!originAnimStart) originAnimStart = t
    var p = Math.min(1, (t - originAnimStart) / 400)
    var e = 1 - Math.pow(1 - p, 2)
    originMarker.setStyle({ radius: 12 * e, fillOpacity: e, opacity: e })
    if (p < 1) requestAnimationFrame(animateOrigin)
  }
  requestAnimationFrame(animateOrigin)

  // 确保路线层和标记层在省份层之上
  if (modernFlowLayer) modernFlowLayer.bringToFront()
  if (modernMarkersLayer) modernMarkersLayer.bringToFront()
  if (modernProvLayer) modernProvLayer.bringToBack()
}

function initModernMap() {
  if (modernMap) return
  modernMap = L.map(modernMapEl.value, {
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

  // 区分点击 vs 拖动：只在纯点击（非拖动）空白区域返回
  var dragState = { startX: 0, startY: 0, moved: false }
  var mapContainer = modernMap.getContainer()
  var DRAG_THRESHOLD = 5

  mapContainer.addEventListener('mousedown', function(e) {
    if (isModernChinaMode.value) return
    dragState.startX = e.clientX
    dragState.startY = e.clientY
    dragState.moved = false
  }, true)

  mapContainer.addEventListener('mousemove', function(e) {
    if (isModernChinaMode.value || dragState.moved) return
    var dx = e.clientX - dragState.startX
    var dy = e.clientY - dragState.startY
    if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
      dragState.moved = true
    }
  }, true)

  mapContainer.addEventListener('click', function(e) {
    if (isModernChinaMode.value) return
    // 拖动过就当是正常浏览地图，不返回
    if (dragState.moved) return
    // 检查是否点击在 Leaflet 交互元素上（省份多边形、贸易线路、marker）
    var target = e.target
    if (!target || !target.closest) { backToChinaMap(); return }
    // 点击在地图容器本身（非任何子元素）上
    if (target === mapContainer) { backToChinaMap(); return }
    // 检查是否是 Leaflet overlay 图层上的元素
    var leafletPane = target.closest('.leaflet-overlay-pane, .leaflet-marker-pane')
    if (leafletPane) {
      // 在 overlay/marker pane 上，检查是否是省份 polygon 或贸易线路
      var interactive = target.closest('svg, path, polygon, polyline, circle, .leaflet-interactive')
      if (!interactive) backToChinaMap()
    }
    // 如果是 tile pane 或其他 pane，也返回（空白区域）
  }, true)
  setTimeout(function() { modernMap && modernMap.invalidateSize() }, 300)
}

watch(ch4Tab, function(nv) {
  if (nv === 'modern' && !modernMap) {
    setTimeout(function() {
      initModernMap()
      renderModernChinaProvinces()
      fitModernChinaBounds()
    }, 250)
  }
})

onMounted(async function() {
  await nextTick()
  initMap()
  await nextTick()
  loadChinaBoundary()

  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', onWindowResize)
})

onBeforeUnmount(function() {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onWindowResize)
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
  if (map) {
    map.remove()
    map = null
  }
  if (modernMap) {
    modernMap.remove()
    modernMap = null
  }
})
</script>

<style scoped>
.chapter-4 {
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
  display: flex;
  flex-direction: column;
}
.map-fullscreen.show {
  opacity: 1;
}

.ch4-topbar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 22px;
  margin: 12px 16px 0;
  box-shadow: 0 2px 12px rgba(81, 109, 51, 0.06);
  z-index: 800;
}

.dynasty-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 16px;
  background: rgba(92, 124, 58, 0.08);
  border-radius: 20px;
  border: 1px solid rgba(92, 124, 58, 0.2);
}
.dyn-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--c-olive-mid);
  box-shadow: 0 0 0 3px rgba(92, 124, 58, 0.2);
}
.dyn-tang .dyn-dot { background: #C8763E; box-shadow: 0 0 0 3px rgba(200, 118, 62, 0.2); }
.dyn-song .dyn-dot { background: #5A7A9A; box-shadow: 0 0 0 3px rgba(90, 122, 154, 0.2); }
.dyn-yuan .dyn-dot { background: #6B8E6B; box-shadow: 0 0 0 3px rgba(107, 142, 107, 0.2); }
.dyn-ming .dyn-dot { background: #B28F4C; box-shadow: 0 0 0 3px rgba(178, 143, 76, 0.2); }
.dyn-qing .dyn-dot { background: #8A6A9A; box-shadow: 0 0 0 3px rgba(138, 106, 154, 0.2); }
.dyn-kangzhan .dyn-dot { background: #A8453A; box-shadow: 0 0 0 3px rgba(168, 69, 58, 0.2); }

.dyn-label {
  font: 600 14px/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.1em;
}

.year-title {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.year-num {
  font: 900 28px/1 var(--serif);
  color: var(--c-olive-deep2);
  letter-spacing: 0.08em;
}

.topbar-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: 1.5px solid var(--c-olive-mid);
  border-radius: 8px;
  background: var(--c-olive);
  color: var(--c-paper);
  font: 600 13px/1 var(--sans);
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.05em;
}
.action-btn:hover {
  background: var(--c-olive-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(81, 109, 51, 0.25);
}
.action-btn.playing {
  background: var(--c-gold);
  border-color: var(--c-gold-deep);
}
.action-btn.secondary {
  background: var(--c-paper);
  color: var(--c-olive);
  border-color: var(--c-beige);
}
.action-btn.secondary:hover {
  background: var(--c-paper-3);
  box-shadow: 0 4px 12px rgba(178, 143, 76, 0.15);
}
.btn-icon {
  font-size: 10px;
}

.ch4-stage {
  position: relative;
  flex: 1;
  min-height: 0;
  margin: 12px 16px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(81, 109, 51, 0.12);
  border: 1px solid var(--line);
  z-index: 1;
}

.map {
  width: 100%;
  height: 100%;
  background: var(--c-paper);
  position: relative;
  z-index: 1;
}
.map :deep(.leaflet-container) {
  background: var(--c-paper) !important;
}

.map-hint {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(8px);
  border: 1px solid var(--line);
  border-radius: 20px;
  font: 400 12px/1 var(--sans);
  color: var(--ink-soft);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}
.hint-icon {
  font-size: 14px;
}

.map-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  z-index: 800;
  background: rgba(247, 244, 235, 0.94);
  backdrop-filter: blur(8px);
  border-radius: 10px;
  padding: 12px 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  font-size: 0.82rem;
  border: 1px solid var(--line);
}

.legend-title {
  font-weight: 700;
  color: var(--c-olive);
  margin-bottom: 10px;
  font-size: 0.78rem;
  letter-spacing: 0.1em;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  color: var(--ink-soft);
}
.legend-row.nodes {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(81, 109, 51, 0.15);
}

.legend-line {
  display: inline-block;
  width: 28px;
  height: 0;
  border-top: 3px solid;
  border-radius: 2px;
}
.legend-line.land {
  border-color: #d4933b;
}
.legend-line.sea {
  border-color: #196c58;
}
.legend-line.ended {
  border-color: #8a8270;
  border-top-style: dashed;
  border-top-width: 2px;
}

.legend-node {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}
.legend-node.origin {
  background: #196c58;
}
.legend-node.dest {
  background: #B28F4C;
  width: 14px;
  height: 14px;
}

/* ===== 信息卡 - 渐入渐出 ===== */
.route-detail-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  bottom: 16px;
  width: 380px;
  max-width: 42%;
  z-index: 900;
  background: rgba(247, 244, 235, 0.98);
  backdrop-filter: blur(14px);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(81, 109, 51, 0.2);
  border: 1px solid rgba(178, 143, 76, 0.2);
  display: flex;
  flex-direction: column;
}

.card-fade-enter-active,
.card-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.card-fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
}
.card-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.96);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
  background: linear-gradient(135deg, rgba(92, 124, 58, 0.08) 0%, rgba(178, 143, 76, 0.06) 100%);
}

.panel-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.panel-type-tag {
  display: inline-block;
  padding: 3px 12px;
  background: var(--c-gold);
  color: #fff;
  font: 600 0.72rem/1 var(--sans);
  border-radius: 12px;
  letter-spacing: 0.08em;
  width: fit-content;
}

.panel-title {
  font: 700 1.25rem/1.3 var(--serif);
  color: var(--c-olive-deep2);
  margin: 0;
  letter-spacing: 0.03em;
}

.panel-close {
  width: 30px;
  height: 30px;
  border: none;
  background: var(--c-paper-3);
  color: var(--c-beige-dark);
  font-size: 1.3rem;
  line-height: 1;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.panel-close:hover {
  background: var(--c-gold);
  color: #fff;
}

.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px 20px;
}
.panel-scroll::-webkit-scrollbar {
  width: 5px;
}
.panel-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(178, 143, 76, 0.3);
  border-radius: 3px;
}
.panel-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(178, 143, 76, 0.5);
}

.detail-year {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 10px 14px;
  background: var(--c-paper);
  border-radius: 8px;
  border-left: 3px solid var(--c-gold);
  margin-bottom: 14px;
}
.detail-year-label {
  font: 500 0.75rem/1 var(--sans);
  color: var(--muted);
  letter-spacing: 0.1em;
}
.detail-year-value {
  font: 700 1.1rem/1 var(--serif);
  color: var(--c-gold-deep);
}

.detail-section-label {
  font: 700 0.75rem/1 var(--sans);
  color: var(--c-olive);
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}
.detail-section-label.with-icon {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-note,
.detail-source,
.detail-history {
  margin-bottom: 16px;
}

.detail-note p,
.detail-source p {
  font: 400 0.87rem/1.7 var(--serif);
  color: var(--ink);
  margin: 0;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  border: 1px solid var(--line);
}
.detail-source p {
  font-size: 0.8rem;
  color: var(--muted);
  font-style: italic;
}

.detail-history ul {
  margin: 0;
  padding: 0;
  list-style: none;
}
.detail-history li {
  font: 400 0.85rem/1.7 var(--serif);
  color: var(--ink-soft);
  padding: 8px 12px;
  padding-left: 22px;
  position: relative;
  border-bottom: 1px dashed var(--line);
}
.detail-history li:last-child {
  border-bottom: none;
}
.detail-history li::before {
  content: '▸';
  position: absolute;
  left: 8px;
  color: var(--c-gold);
}

.history-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 320px;
  max-width: 38%;
  z-index: 850;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 4px 20px rgba(81, 109, 51, 0.12);
  border: 1px solid var(--line);
}

.history-title {
  font: 700 0.85rem/1 var(--serif);
  color: var(--c-olive);
  margin-bottom: 10px;
  letter-spacing: 0.05em;
}

.history-panel ul {
  margin: 0;
  padding: 0;
  list-style: none;
}
.history-panel li {
  font: 400 0.8rem/1.6 var(--serif);
  color: var(--ink-soft);
  padding: 6px 0;
  padding-left: 16px;
  position: relative;
  border-bottom: 1px dashed var(--line);
}
.history-panel li:last-child {
  border-bottom: none;
}
.history-panel li::before {
  content: '◆';
  position: absolute;
  left: 0;
  color: var(--c-gold);
  font-size: 0.6rem;
  top: 10px;
}

.timeline-panel {
  flex-shrink: 0;
  margin: 0 16px 12px;
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 2px 14px rgba(81, 109, 51, 0.06);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.6rem;
}

.stat-card {
  background: var(--c-paper);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
  transition: all 0.25s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(178, 143, 76, 0.12);
  border-color: rgba(178, 143, 76, 0.3);
}

.stat-label {
  font: 400 0.78rem/1 var(--sans);
  color: var(--muted);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.stat-num {
  font: 900 1.8rem/1 var(--serif);
  color: var(--c-olive);
  letter-spacing: 0.02em;
}

.slider-wrap {
  position: relative;
  padding: 50px 8px 20px;
  margin-bottom: 1rem;
}

.dynasty-ticks {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  pointer-events: none;
}

.tick {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translateX(-50%);
}

.tick-line {
  width: 1px;
  height: 14px;
  background: var(--c-beige);
}

.tick-label {
  font: 600 0.78rem/1 var(--serif);
  color: var(--c-olive);
  margin-top: 4px;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  background: var(--c-paper);
  border: 1px solid var(--line);
  border-radius: 4px;
  white-space: nowrap;
}

.year-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg,
    #C8763E 0%, #C8763E 20%,
    #5A7A9A 22%, #5A7A9A 32%,
    #6B8E6B 33%, #6B8E6B 38%,
    #B28F4C 39%, #B28F4C 58%,
    #8A6A9A 59%, #8A6A9A 78%,
    #C3C19A 79%, #C3C19A 95%,
    #A8453A 96%, #A8453A 100%
  );
  outline: none;
  cursor: pointer;
}

.year-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--c-paper);
  border: 3px solid var(--c-olive);
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(81, 109, 51, 0.3);
  transition: all 0.2s ease;
}
.year-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  border-color: var(--c-gold);
  box-shadow: 0 3px 14px rgba(178, 143, 76, 0.4);
}

.year-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--c-paper);
  border: 3px solid var(--c-olive);
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(81, 109, 51, 0.3);
}

/* ===== 时间轴控制区 ===== */
.timeline-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 6px 0 12px;
  padding: 8px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.step-indicator {
  font: 500 13px/1 var(--sans);
  color: var(--c-olive);
  padding: 6px 16px;
  background: var(--c-paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  min-width: 60px;
  text-align: center;
}

.filter-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.filter-btn {
  padding: 8px 28px;
  border: 1.5px solid var(--c-beige);
  border-radius: 22px;
  background: var(--c-paper);
  color: var(--ink-soft);
  font: 500 0.88rem/1 var(--sans);
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.1em;
}
.filter-btn:hover {
  border-color: var(--c-olive-mid);
  color: var(--c-olive);
  transform: translateY(-1px);
}
.filter-btn.active {
  background: var(--c-olive);
  border-color: var(--c-olive);
  color: var(--c-paper);
  box-shadow: 0 3px 12px rgba(81, 109, 51, 0.25);
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: all 0.3s ease;
}
.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

:deep(.ch4-tip) {
  background: rgba(247, 244, 235, 0.98) !important;
  border: 1px solid var(--c-gold-light) !important;
  color: var(--c-olive-deep2) !important;
  font: 500 12px/1.4 var(--sans) !important;
  padding: 6px 12px !important;
  border-radius: 6px !important;
  box-shadow: 0 3px 12px rgba(81, 109, 51, 0.15) !important;
}
:deep(.ch4-tip::before) {
  border-top-color: var(--c-gold-light) !important;
}

:deep(.ch4-node-tip) {
  background: var(--c-olive) !important;
  border: none !important;
  color: var(--c-paper) !important;
  font: 500 11px/1 var(--sans) !important;
  padding: 3px 9px !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}
:deep(.ch4-node-tip::before) {
  border-top-color: var(--c-olive) !important;
}

@media (max-width: 960px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .route-detail-panel {
    width: auto;
    max-width: none;
    left: 8px;
    right: 8px;
    top: auto;
    bottom: 8px;
    max-height: 55%;
  }
  .history-panel {
    width: auto;
    max-width: none;
    left: 8px;
    right: 8px;
    top: 56px;
  }
  .ch4-topbar {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .ch4-stage {
    margin: 8px 8px;
  }
  .ch4-topbar {
    margin: 8px 8px 0;
  }
  .timeline-panel {
    margin: 0 8px 8px;
  }
  .dynasty-ticks .tick-label {
    font-size: 0.65rem;
    padding: 2px 5px;
  }
  .year-num {
    font-size: 22px;
  }
  .filter-btn {
    padding: 7px 18px;
    font-size: 0.8rem;
  }
}

/* ---------- 路线生长动画 ---------- */
.world-map :deep(svg path.leaflet-interactive),
.world-map :deep(svg polyline.leaflet-interactive) {
  transition: stroke-dashoffset 1.6s cubic-bezier(.4,0,.2,1);
}

/* ---------- 数据点波浪弹出 ---------- */
.world-map :deep(.ch4-wave-node) {
  animation: ch4WavePop .5s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes ch4WavePop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

/* ---------- 信息卡滑入 ---------- */
.world-map ~ .detail-panel,
.detail-panel {
  animation: panelSlide .5s cubic-bezier(.4,0,.2,1);
}
@keyframes panelSlide {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ---------- 历史事件交错淡入 ---------- */
.history-panel .event-item {
  animation: eventFadeIn .4s cubic-bezier(.4,0,.2,1) both;
}
@keyframes eventFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ================================================================
   Tab Navigation
   ================================================================ */
.ch4-tabs {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 10px 16px 0;
  flex-shrink: 0;
}
.ch4-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border: 1.5px solid var(--line);
  border-radius: 30px;
  background: rgba(247,244,235,0.7);
  color: var(--c-olive-mid);
  font: 500 13px/1 var(--font-dzji, var(--serif));
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.05em;
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
.ch4-tab .tab-icon { font-size: 15px; }

.ch4-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.ch4-view-ancient,
.ch4-view-modern {
  --serif: var(--font-body);
}

.ch4-view-ancient .timeline-panel {
  flex-shrink: 1;
  overflow-y: auto;
  min-height: 180px;
}
.ch4-view-ancient .ch4-stage {
  min-height: 320px;
}

/* ================================================================
   当代贸易情况
   ================================================================ */
.ch4-view-modern { padding-top: 8px; }

.modern-topbar {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #FAF7EF 0%, #F5F1E8 100%);
  border: 1px solid var(--line);
  border-radius: 12px;
  margin: 8px 16px 0;
  box-shadow: 0 2px 12px rgba(81, 109, 51, 0.06);
  z-index: 800;
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
  font: 700 13px/1 var(--serif);
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.title-badge.world { background: var(--c-olive-mid); }
.title-sub { color: var(--c-beige-dark); font-size: 13px; }
.title-sub .hl-num { color: var(--c-gold-deep, #8a6f3d); font-family: var(--serif); font-size: 16px; font-weight: 900; }
.modern-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.year-select { display: inline-flex; align-items: center; gap: 8px; }
.slider-label { color: var(--c-beige-dark); font-size: 13px; letter-spacing: 0.05em; }
.select-input {
  padding: 6px 12px;
  border: 1.5px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: var(--c-olive);
  font: 500 13px/1 var(--serif);
  cursor: pointer;
}
.select-input:hover { border-color: var(--c-olive-mid); }
.select-input:focus { outline: none; border-color: var(--c-olive); }

.modern-stage {
  flex: 1;
  min-height: 400px;
  margin-top: 8px;
}
.modern-map { width: 100%; height: 100%; background: #F0EBD9; }

.hover-card {
  position: absolute;
  top: 16px; right: 16px;
  z-index: 950;
  min-width: 200px;
  background: rgba(247, 244, 235, 0.98);
  border-radius: 10px;
  padding: 10px 14px;
  border: 1px solid rgba(178, 143, 76, 0.3);
  box-shadow: 0 4px 20px rgba(81,109,51,0.15);
}
.hc-title { font: 700 15px/1 var(--serif); color: var(--c-olive); margin-bottom: 6px; }
.hc-row { display: flex; justify-content: space-between; align-items: center; padding: 3px 0; font-size: 12px; color: var(--c-beige-dark); }
.hc-row b { color: var(--c-gold-deep, #8a6f3d); font-family: var(--serif); font-weight: 900; }

.modern-legend {
  left: 16px !important;
  top: 16px !important;
  min-width: 200px;
}
.legend-bar { display: block; width: 140px; height: 12px; border-radius: 6px; margin: 4px 0 6px; background: linear-gradient(90deg,#EFE9DA 0%, #B28F4C 50%, #516D33 100%); }
.modern-flow-legend { width: 140px !important; max-width: 260px; background: linear-gradient(90deg, rgba(178,143,76,0.2) 0%, #C8462E 100%) !important; }
.legend-scale { display: flex; justify-content: space-between; font-size: 11px; color: var(--c-beige-dark); letter-spacing: 0.08em; }
.legend-hint { margin-top: 6px; padding-top: 6px; border-top: 1px dashed rgba(178,143,76,0.25); font-size: 11px; color: var(--c-beige-dark); }
.legend-hint b { color: var(--c-olive); font-weight: 700; }

.modern-country-panel {
  position: absolute;
  top: 16px; right: 16px;
  bottom: 16px;
  width: 320px;
  max-width: 42%;
  z-index: 1000;
  background: rgba(247, 244, 235, 0.97);
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
  padding: 8px 12px 16px;
}
.country-row {
  display: grid;
  grid-template-columns: 22px 80px 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 6px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.country-row:hover { background: rgba(178, 143, 76, 0.1); }
.cr-rank {
  text-align: center;
  font: 900 11px/1 var(--serif);
  color: var(--c-beige-dark);
  width: 20px; height: 20px;
  display: inline-flex; align-items: center; justify-content: center;
  background: rgba(239,233,218,0.8); border-radius: 50%;
}
.country-row:nth-child(1) .cr-rank { background: #C8462E; color: #fff; }
.country-row:nth-child(2) .cr-rank { background: #B28F4C; color: #fff; }
.country-row:nth-child(3) .cr-rank { background: #5C7C3A; color: #fff; }
.cr-name { font: 600 12px/1 var(--serif); color: var(--c-olive); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cr-bar-wrap { height: 7px; background: rgba(178,143,76,0.15); border-radius: 4px; overflow: hidden; }
.cr-bar { height: 100%; width: var(--w); background: linear-gradient(90deg, #B28F4C, #C8462E); border-radius: 4px; }
.cr-val { font: 800 12px/1 var(--serif); color: var(--c-gold-deep, #8a6f3d); white-space: nowrap; }
.cr-val .unit { font-weight: 500; color: var(--c-beige-dark); margin-left: 2px; font-size: 10px; }

.modern-country-panel .panel-scroll::-webkit-scrollbar { width: 5px; }
.modern-country-panel .panel-scroll::-webkit-scrollbar-thumb { background: rgba(178,143,76,0.3); border-radius: 3px; }

.modern-tag { background: var(--c-olive) !important; }

:deep(.modern-flow-tip) {
  background: var(--c-olive) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  border-radius: 6px;
  padding: 6px 10px !important;
  font: 500 12px/1.5 var(--serif);
}

@media (max-width: 900px) {
  .modern-country-panel {
    top: auto; bottom: 8px; right: 8px; left: 8px;
    width: auto; max-width: none; max-height: 45%;
  }
}
</style>