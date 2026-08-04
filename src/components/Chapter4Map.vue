<template>
  <section class="chapter chapter-4" :id="id" ref="sectionEl">
    <ChapterIntro
      ch-no="第 四 章"
      title="一叶行远"
      desc="自古港而向四海，沿茶马古道以入远方。拖动时间轴，航线与商道随年代而现隐，点击路线细览茶香万里的往事。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
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
  </section>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import ChapterIntro from './ChapterIntro.vue'
import { TEA_TRADE_DATA, HISTORICAL_EVENTS, getEventsByYear } from '../data/ch4/trade-data.js'

const props = defineProps({ id: { type: String, required: true } })

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

const sectionEl = ref(null)
const mapEl = ref(null)
const currentYear = ref(618)
const filter = ref('all')
const isPlaying = ref(false)
const selectedRoute = ref(null)
const showHint = ref(true)
const introDone = ref(false)

let map = null
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
  if (!selectedRoute.value) return ''
  const vp = visualPoints(selectedRoute.value)
  if (!vp || vp.length === 0) return ''
  return vp[0].name + ' → ' + vp[vp.length - 1].name
})
const routeHistoryEvents = computed(() => {
  if (!selectedRoute.value) return []
  return getEventsByYear(selectedRoute.value.startYear)
})

watch(filter, () => {
  render()
})

function onSliderInput(e) {
  const v = Number(e.target.value)
  currentYear.value = getClosestDataYear(v)
  render()
}
function onSliderChange(e) {
  const v = Number(e.target.value)
  currentYear.value = getClosestDataYear(v)
  render()
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    playTimer = setInterval(() => {
      const next = getNextDataYear(currentYear.value)
      if (next > currentYear.value) {
        currentYear.value = next
        render()
      } else {
        isPlaying.value = false
        clearInterval(playTimer)
        playTimer = null
      }
    }, 3000)
  } else {
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
  }
}

function resetView() {
  currentYear.value = 618
  filter.value = 'all'
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
  render()
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

  // 世界地图底图瓦片
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 19,
    attribution: ''
  }).addTo(map)

  routeLayer = L.layerGroup().addTo(map)
  nodeLayer = L.layerGroup().addTo(map)

  map.on('click', () => {
    if (selectedRoute.value) {
      selectedRoute.value = null
    }
  })
}

function loadChinaBoundary() {
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    .then(r => r.json())
    .then(geo => {
      if (!map) return
      L.geoJSON(geo, {
        interactive: false,
        style: () => ({
          color: '#B28F4C',
          weight: 2,
          opacity: 0.9,
          fillColor: '#F7F4EB',
          fillOpacity: 0.5,
        }),
      }).addTo(map)
    })
    .catch(err => console.warn('中国边界加载失败:', err))
}

function render() {
  if (!map || !routeLayer || !nodeLayer) return

  routeLayer.clearLayers()
  nodeLayer.clearLayers()

  const activeNodes = new Map()
  stats.activeCount = 0
  stats.endedCount = 0
  stats.routeCount = 0
  const nodeSet = new Set()

  for (const r of TEA_TRADE_DATA) {
    const k = kind(r)
    if (filter.value === 'sea' && k !== 'sea') continue
    if (filter.value === 'land' && k !== 'land') continue

    const state = getRouteState(r, currentYear.value)
    if (state === 'not_started') continue

    const vp = visualPoints(r)
    const c = coords(vp)
    if (c.length < 2) continue

    const isActive = state === 'active' || state === 'active_permanent'
    const isEnded = state === 'ended'
    const baseColor = k === 'sea' ? '#196c58' : '#d4933b'

    let line
    if (isEnded) {
      stats.endedCount++
      line = L.polyline(c, {
        smoothFactor: 0.5,
        interactive: true,
        color: '#8a8270',
        weight: 1.5,
        opacity: 0.45,
        dashArray: '6 4',
      })
    } else {
      stats.activeCount++
      stats.routeCount += vp.length - 1
      const totalLen = c.length * 20 // approximate pixel length
      line = L.polyline(c, {
        color: baseColor,
        weight: 2.7,
        opacity: 0.92,
        smoothFactor: 0.5,
        dashArray: totalLen,
        dashOffset: totalLen,
      })
      // 路线生长动画：dashOffset → 0
      setTimeout(() => {
        line.setStyle({ dashOffset: 0 })
      }, 30)
    }

    line.on('click', (e) => {
      L.DomEvent.stopPropagation(e)
      selectedRoute.value = r
      showHint.value = false
    })

    const fromName = vp.length ? vp[0].name : r.origin
    const toName = vp.length ? vp[vp.length - 1].name : r.destination
    const statusEmoji = isActive ? '🟢' : '⚪'
    line.bindTooltip(`${r.yearText}｜${fromName}→${toName} ${statusEmoji}`, {
      sticky: true,
      direction: 'top',
      offset: [0, -6],
      className: 'ch4-tip',
    })

    line.addTo(routeLayer)

    if (isActive && vp.length >= 2) {
      const originKey = `${vp[0].lon},${vp[0].lat}`
      if (!activeNodes.has(originKey)) {
        activeNodes.set(originKey, { ...vp[0], isOrigin: true, isCapital: false })
      }
      for (let i = 1; i < vp.length; i++) {
        const p = vp[i]
        const key = `${p.lon},${p.lat}`
        const isDest = i === vp.length - 1
        const isCapital = !inChina(p) || isDest
        if (!activeNodes.has(key)) {
          activeNodes.set(key, { ...p, isOrigin: false, isCapital })
        }
      }
    }
  }

  for (const [, p] of activeNodes) {
    nodeSet.add(`${p.lon},${p.lat}`)
    const isCapital = p.isCapital && !p.isOrigin
    const radius = isCapital ? 7 : 5
    const fillColor = p.isOrigin ? '#196c58' : (isCapital ? '#B28F4C' : '#5C7C3A')
    const idx = nodeSet.size

    const marker = L.circleMarker([p.lat, p.lon], {
      radius,
      fillColor,
      color: '#ffffff',
      weight: 2,
      fillOpacity: 0.95,
      className: 'ch4-wave-node',
    }).bindTooltip(p.name, {
      permanent: false,
      direction: 'top',
      offset: [0, -6],
      className: 'ch4-node-tip',
    }).addTo(nodeLayer)

    // 数据点波浪弹出
    setTimeout(() => {
      const el = marker.getElement()
      if (el) {
        el.style.animation = 'none'
        el.offsetHeight
        el.style.animation = ''
      }
    }, 600 + idx * 50)
  }

  stats.countryCount = nodeSet.size
}

function onKeydown(e) {
  if (e.code === 'ArrowRight') {
    const next = getNextDataYear(currentYear.value)
    if (next > currentYear.value) {
      currentYear.value = next
      render()
    }
  } else if (e.code === 'ArrowLeft') {
    const idx = allDataYears.indexOf(currentYear.value)
    if (idx > 0) {
      currentYear.value = allDataYears[idx - 1]
      render()
    }
  } else if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  }
}

function onIntroDone() {
  introDone.value = true
  setTimeout(() => {
    if (map) map.invalidateSize()
    render()
  }, 300)
}

onMounted(async () => {
  await nextTick()
  initMap()
  await nextTick()
  loadChinaBoundary()

  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
  if (map) {
    map.remove()
    map = null
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
.year-unit {
  font: 500 16px/1 var(--serif);
  color: var(--c-beige-dark);
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
}

.map {
  width: 100%;
  height: 100%;
  background: var(--c-paper);
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

.tick-year {
  font: 400 0.65rem/1 var(--sans);
  color: var(--muted);
  margin-top: 3px;
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
</style>
