<template>
  <section class="chapter chapter-4" :id="id" ref="sectionEl">
    <ChapterIntro
      :ch-no="chapter.number"
      :title="chapter.title"
      :desc="chapter.description"
      :duration="7"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{ show: introDone }">
      <ChapterCornerIntro chapter-key="ch4" :visible="introDone" />
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
        <div class="ch4-ancient-container">
          <!-- Loading State -->
          <div v-if="ancientLoading" class="map-loading">
            <div class="loading-spinner"></div>
            <div class="loading-text">地图载入中...</div>
          </div>
          <div v-else-if="ancientError" class="map-error">
            <div class="error-icon">⚠️</div>
            <div class="error-text">地图加载失败</div>
            <div class="error-hint">{{ ancientError }}</div>
            <button class="reload-btn" @click="reloadMap">重新加载</button>
          </div>

          <!-- Main Map Stage -->
          <div class="ch4-stage">
            <div ref="mapEl" class="map"></div>

            <!-- Legend -->
            <div class="map-legend">
              <div class="legend-title">图例</div>
              <div class="legend-row">
                <span class="legend-line land"></span>
                <span>陆路</span>
              </div>
              <div class="legend-row">
                <span class="legend-line sea"></span>
                <span>海路</span>
              </div>
              <div class="legend-row">
                <span class="legend-line digitized"></span>
                <span>实线：当前路线</span>
              </div>
              <div class="legend-row">
                <span class="legend-line inferred"></span>
                <span>虚线：已消失的历史路线</span>
              </div>
              <div class="legend-row nodes">
                <span class="legend-node origin"></span>
                <span>起点</span>
              </div>
              <div class="legend-row nodes">
                <span class="legend-node destination"></span>
                <span>终点</span>
              </div>
            </div>

            <!-- 播放时显示朝代背景；仅在用户点击路线或节点后显示路线详情 -->
            <transition name="ancient-panel-fade" mode="out-in">
              <div class="route-detail-panel" :key="panelKey">
                <template v-if="panelMode === 'dynasty'">
                  <div class="panel-header">
                    <div class="panel-badges">
                      <span class="panel-type-tag dynasty">朝代背景</span>
                      <span class="panel-dynasty-tag">{{ dynastyName }}</span>
                    </div>
                  </div>
                  <div class="panel-title-row">
                    <h3 class="panel-title">{{ currentDynastyInfo.title }}</h3>
                  </div>
                  <div class="panel-scroll">
                    <div class="panel-section">
                      <div class="section-label">阶段特征</div>
                      <p class="section-text">{{ currentDynastyInfo.feature }}</p>
                    </div>
                    <div class="panel-section">
                      <div class="section-label">主要通道</div>
                      <p class="section-text">{{ currentDynastyInfo.channels }}</p>
                    </div>
                    <div class="panel-section">
                      <div class="section-label">贸易影响</div>
                      <p class="section-text">{{ currentDynastyInfo.impact }}</p>
                    </div>
                  </div>
                </template>

                <template v-else-if="nodeRouteOptions.length && !selectedRoute">
                  <div class="panel-header">
                    <div class="panel-badges">
                      <span class="panel-type-tag dynasty">路线节点</span>
                      <span class="panel-dynasty-tag">{{ dynastyName }}</span>
                    </div>
                    <button class="panel-back" @click="showDynastyPanel">返回朝代背景</button>
                  </div>
                  <div class="panel-title-row">
                    <h3 class="panel-title">{{ selectedNodeName }}</h3>
                    <p class="panel-subtitle">该节点关联 {{ nodeRouteOptions.length }} 条路线，请选择查看详情。</p>
                  </div>
                  <div class="panel-scroll node-route-list">
                    <button
                      v-for="route in nodeRouteOptions"
                      :key="route.id"
                      class="node-route-option"
                      @click="selectRoute(route)"
                    >
                      <span class="node-route-kind">{{ route.routeType }} · {{ route.dynasty }}</span>
                      <strong>{{ route.origin }} → {{ route.destination }}</strong>
                    </button>
                  </div>
                </template>

                <template v-else-if="selectedRoute">
                  <div class="panel-header">
                    <div class="panel-badges">
                      <span class="panel-type-tag" :class="kind(selectedRoute)">{{ selectedRoute.routeType }}</span>
                      <span class="panel-dynasty-tag">{{ selectedRoute.dynasty }}</span>
                      <span class="panel-dynasty-tag">{{ routeModeLabel }}</span>
                    </div>
                    <button class="panel-back" @click="showDynastyPanel">返回朝代背景</button>
                  </div>
                  <div class="panel-title-row">
                    <h3 class="panel-title">{{ routeFromTo }}</h3>
                  </div>
                  <div class="panel-scroll">
                    <div class="panel-info-grid">
                      <div class="info-item">
                        <span class="info-label">时间</span>
                        <span class="info-value">{{ routeDisplayTime }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">流向</span>
                        <span class="info-value">{{ selectedRoute.routeType === '海路' ? '海上航线' : selectedRoute.routeType === '水陆联运' ? '水陆联运' : '陆路商道' }}</span>
                      </div>
                      <div class="info-item info-item-wide">
                        <span class="info-label">途经节点</span>
                        <span class="info-value">{{ routeViaText }}</span>
                      </div>
                    </div>
                    <div class="panel-section">
                      <div class="section-label">历史背景</div>
                      <p class="section-text">{{ selectedRoute.historicalBackground }}</p>
                    </div>
                    <div class="panel-section">
                      <div class="section-label">路线故事</div>
                      <p class="section-text">{{ selectedRoute.routeStory }}</p>
                    </div>
                    <div class="panel-section">
                      <div class="section-label">贸易影响</div>
                      <p class="section-text">{{ selectedRoute.tradeSignificance }}</p>
                    </div>
                  </div>
                </template>
              </div>
            </transition>

            <!-- Floating Timeline (在地图容器内部，半悬浮) -->
            <div class="timeline-floating">
              <div class="timeline-header">
                <span class="current-dynasty-label">{{ dynastyName }}</span>
                <div class="timeline-controls">
                  <button class="play-btn" :class="{ playing: isPlaying }" @click="togglePlay">{{ isPlaying ? '暂停' : '播放' }}</button>
                  <button class="reset-btn" @click="resetView">重置</button>
                </div>
              </div>
              <div class="timeline-body">
                <div class="timeline-axis">
                  <div class="slider-track" ref="sliderTrack" @mousedown="onSliderMouseDown">
                    <div class="slider-fill" :style="{ width: progress * 100 + '%' }"></div>
                    <div class="slider-thumb" :style="{ left: progress * 100 + '%' }"></div>
                  </div>
                  <button
                    v-for="tick in dynastyTicks"
                    :key="tick.name"
                    type="button"
                    class="dynasty-tick"
                    :class="{ active: dynastyName === tick.name, alternate: tick.index % 2 === 1 }"
                    :style="{ left: (tick.progress * 100) + '%' }"
                    @mousedown.stop
                    @click="jumpToDynasty(tick)"
                  >
                    <span class="tick-label">{{ tick.name }}</span>
                    <span class="tick-mark"></span>
                  </button>
                </div>
              </div>
              <div class="route-filter-control" aria-label="路线类型筛选">
                <button
                  v-for="option in routeFilterOptions"
                  :key="option.value"
                  :class="['route-filter-btn', { active: routeFilter === option.value }]"
                  :aria-pressed="routeFilter === option.value"
                  @click.stop="setRouteFilter(option.value)"
                >{{ option.label }}</button>
              </div>
            </div>
          </div>
        </div>
      </div><!-- end ch4-view-ancient -->

      <!-- ============================== Tab: 当代贸易情况 ============================== -->
      <div v-show="ch4Tab === 'modern'" class="ch4-view ch4-view-modern">
        <div class="modern-topbar">
          <div class="modern-title">
            <span v-if="!isModernChinaMode" class="title-badge world">
              {{ selectedModernProvince || '中国' }}
            </span>
            <span class="title-sub" v-if="!isModernChinaMode && modernProvinceInfo.hasData && modernProvinceInfo.flows.length">{{ modernYear }}年 出口总额 <b class="hl-num">{{ fmtNum(modernProvinceInfo.provinceValue / 1e8) }}</b> 亿元，覆盖 <b class="hl-num">{{ modernProvinceInfo.flows.length }}</b> 个主要国家</span>
            <span class="title-sub" v-else-if="!isModernChinaMode && modernProvinceInfo.hasData">{{ modernYear }}年 出口总额 <b class="hl-num">{{ fmtNum(modernProvinceInfo.provinceValue / 1e8) }}</b> 亿元，暂无主要出口目的地数据</span>
            <span class="title-sub" v-else-if="!isModernChinaMode">{{ modernYear }}年该省暂无茶叶出口数据</span>
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

          <!-- 茶叶形比例符号图例：概览与世界详情共用同一固定尺度 -->
          <div class="map-legend modern-legend">
            <div class="modern-legend-section">
              <div class="modern-legend-title" style="font-family:var(--font-body),KaiTi,STKaiti,serif !important;font-style:normal !important">茶叶符号大小：出口额（亿元）</div>
              <div class="leaf-size-legend">
                <div v-for="item in leafSizeLegendItems" :key="item.ratio" class="leaf-size-item">
                  <span
                    class="legend-leaf size-leaf"
                    :style="{ width: item.displaySize + 'px', height: item.displaySize + 'px' }"
                    v-html="createLeafSvg('#7F985D', false, 1)"
                  ></span>
                  <span>{{ fmtNum(item.valueYi) }}</span>
                </div>
              </div>
            </div>
            <div class="modern-legend-section color-section">
              <div class="modern-legend-title" style="font-family:var(--font-body),KaiTi,STKaiti,serif !important;font-style:normal !important">茶叶颜色：出口额同比增速</div>
              <div class="leaf-color-legend">
                <div v-for="item in leafColorLegendItems" :key="item.label" class="leaf-color-item">
                  <span class="legend-leaf color-leaf" v-html="createLeafSvg(item.color, false, 1)"></span>
                  <span>{{ item.label }}</span>
                </div>
              </div>
            </div>
            <div v-if="isModernChinaMode" class="modern-legend-guide">
              点击任意省份，查看该省茶叶出口全球流向
            </div>
          </div>

          <!-- 悬浮信息卡 -->
          <transition name="panel-fade">
            <div v-if="isModernChinaMode && hoveredProvince" class="hover-card">
              <div class="hc-title">{{ hoveredProvince.name }}</div>
              <template v-if="hoveredProvince.hasData">
                <div class="hc-row"><span>出口额</span><b>{{ fmtNum(hoveredProvince.valueYi) }} 亿元</b></div>
                <div class="hc-row"><span>全国占比</span><b>{{ fmtNum(hoveredProvince.share) }}%</b></div>
                <div class="hc-row"><span>同比增速</span><b>{{ formatYoY(hoveredProvince.yoy) }}</b></div>
                <div class="hc-row market-row"><span>主要出口市场</span><b>{{ hoveredProvince.markets }}</b></div>
              </template>
              <div v-else class="hc-empty">该年份暂无数据</div>
            </div>
          </transition>

          <!-- 世界模式：主要出口目的地 Top10 -->
          <transition name="panel-slide">
            <div v-if="!isModernChinaMode" class="modern-country-panel">
              <div class="panel-header">
                <div class="panel-title-wrap">
                  <span class="panel-type-tag modern-tag">全球流向</span>
                  <h3 class="panel-title">{{ selectedModernProvince }} · 主要出口目的地</h3>
                </div>
              </div>
              <div v-if="modernProvinceInfo.hasData" class="province-trade-summary">
                <div><span>出口额</span><b>{{ fmtNum(modernProvinceInfo.provinceValue / 1e8) }}亿元</b></div>
                <div><span>全国占比</span><b>{{ fmtNum(modernProvinceInfo.share) }}%</b></div>
                <div><span>同比增速</span><b>{{ formatYoY(modernProvinceInfo.yoy) }}</b></div>
              </div>
              <div v-if="modernProvinceInfo.flows.length" class="panel-scroll">
                <div
                  v-for="(f, i) in modernProvinceInfo.flows.slice(0, 10)"
                  :key="f.country"
                  class="country-row"
                  :style="getCountryBarStyle(f.value)"
                  @mouseenter="highlightFlowCountry(f.country, true)"
                  @mouseleave="highlightFlowCountry(f.country, false)"
                >
                  <div class="cr-rank">{{ i + 1 }}</div>
                  <div class="cr-name">{{ f.country }}</div>
                  <div class="cr-bar-wrap"><div class="cr-bar"></div></div>
                  <div class="cr-val">{{ fmtNum(f.value / 1e8) }}<span class="unit">亿元</span></div>
                </div>
              </div>
              <div v-else class="modern-empty-state">
                {{ modernProvinceInfo.hasData ? '该年份暂无主要出口目的地数据' : '该年份暂无数据' }}
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
import ChapterCornerIntro from './ChapterCornerIntro.vue'
import { CHAPTER_META } from '../data/chapterMeta.js'
import { TEA_TRADE_DATA, DYNASTY_INFO } from '../data/ch4/trade-data.js'
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

const MIN_YEAR = 618
const MAX_YEAR = 1945
const dynasties = [
  { name: '唐代', start: 618, end: 959 },
  { name: '宋代', start: 960, end: 1270 },
  { name: '元代', start: 1271, end: 1367 },
  { name: '明代', start: 1368, end: 1643 },
  { name: '清代', start: 1644, end: 1936 },
  { name: '抗战时期', start: 1937, end: 1945 },
]
function yearToProgress(year) {
  return Math.max(0, Math.min(1, (Number(year) - MIN_YEAR) / (MAX_YEAR - MIN_YEAR)))
}
const dynastyTicks = dynasties.map(function(dynasty, index) {
  return { ...dynasty, index, progress: yearToProgress(dynasty.start) }
})

function getDynastyByProgress(currentProgress) {
  var active = dynastyTicks[0]
  for (var i = 0; i < dynastyTicks.length; i++) {
    if (currentProgress + 1e-8 >= dynastyTicks[i].progress) active = dynastyTicks[i]
    else break
  }
  return active
}

const ANCIENT_ROUTE_URL = `${import.meta.env.BASE_URL || '/'}data/4/ancient_tea_routes.geojson`
const ANCIENT_NODE_URL = `${import.meta.env.BASE_URL || '/'}data/4/ancient_tea_nodes.geojson`
const WORLD_COUNTRIES_URL = `${import.meta.env.BASE_URL || '/'}data/4/world_countries_50m.geojson`
const DYNASTY_ORDER = dynasties.map(function(item) { return item.name })
const LEGACY_ROUTE_MATCH = {
  R01: 135, R02: 135, R03: 134, R04: 134, R05: 133, R06: 136,
  R07: 91, R08: 52, R09: 1, R10: 10, R11: 23, R12: 39,
  R13: 45, R14: 50, R15: 95, R16: 108, R17: 142, R18: 139,
}

var ancientRouteFeatureIndex = new Map()
var ancientNodeFeatureIndex = new Map()
var ancientTradeRoutes = []

function routeTypeCode(route) {
  if (route && route.routeTypeCode) return route.routeTypeCode
  if (route && route.route_type) return String(route.route_type).toLowerCase()
  return /海上|海运|海路/.test(route && (route.type || route.routeType)) ? 'sea' : 'land'
}
const kind = r => routeTypeCode(r) === 'sea' ? 'sea' : 'land'
function routePassesFilter(route) {
  var type = routeTypeCode(route)
  return routeFilter.value === 'all' || type === routeFilter.value || type === 'mixed'
}
function setRouteFilter(value) {
  routeFilter.value = value
  if ((selectedRoute.value && !routePassesFilter(selectedRoute.value)) || nodeRouteOptions.value.length) {
    showDynastyPanel()
  }
  renderCurrentProgress()
}
function visualPoints(r) {
  return (r && r.points) || []
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
function arcSegmentsFromNodes(points) {
  if (!points || points.length < 2) return []
  var out = []
  for (var i = 1; i < points.length; i++) {
    var seg = curved(points[i - 1], points[i])
    if (i > 1) seg.shift()
    out.push.apply(out, seg)
  }
  return out.length ? [out] : []
}

// 保留给当代贸易流向线使用；古代路线只通过 routePathSegments 决定是否调用弧线。
function coords(points) {
  return arcSegmentsFromNodes(points)[0] || []
}

function routePathSegments(route) {
  if (route && route.routeMode === 'digitized' && Array.isArray(route.geometrySegments)) {
    return route.geometrySegments
  }
  return arcSegmentsFromNodes(visualPoints(route))
}

function sameCoordinate(a, b) {
  return a && b && Math.abs(Number(a[0]) - Number(b[0])) < 1e-8 && Math.abs(Number(a[1]) - Number(b[1])) < 1e-8
}

function extractGeometrySegments(geometry) {
  if (!geometry) return []
  if (geometry.type === 'LineString') return [geometry.coordinates]
  if (geometry.type === 'MultiLineString') return geometry.coordinates
  return []
}

function mergeOrderedSegments(features) {
  var merged = []
  ;(features || []).forEach(function(feature) {
    extractGeometrySegments(feature.geometry).forEach(function(rawSegment) {
      var segment = (rawSegment || []).map(function(coordinate) {
        return [Number(coordinate[1]), Number(coordinate[0])]
      }).filter(function(coordinate) {
        return Number.isFinite(coordinate[0]) && Number.isFinite(coordinate[1])
      })
      if (segment.length < 2) return
      var previous = merged[merged.length - 1]
      if (previous && sameCoordinate(previous[previous.length - 1], segment[0])) {
        previous.push.apply(previous, segment.slice(1))
      } else {
        merged.push(segment)
      }
    })
  })
  return merged
}

function parseDynasties(value) {
  var tokens = String(value || '').split(/[|｜、,，/]+/).map(function(item) { return item.trim() }).filter(Boolean)
  var normalized = tokens.filter(function(item) { return DYNASTY_ORDER.includes(item) })
  return normalized.length ? Array.from(new Set(normalized)) : ['唐代']
}

function nodeFromFeature(feature) {
  var properties = (feature && feature.properties) || {}
  var coordinate = feature && feature.geometry && feature.geometry.coordinates
  var lon = Array.isArray(coordinate) ? Number(coordinate[0]) : Number(properties['经度_lon'])
  var lat = Array.isArray(coordinate) ? Number(coordinate[1]) : Number(properties['纬度_lat'])
  return {
    id: properties.OBJECTID != null ? String(properties.OBJECTID) : undefined,
    routeId: String(properties.route_id || ''),
    seq: Number(properties.seq),
    name: properties['节点名称'] || properties.node_name || properties.name || '路线节点',
    role: properties['节点角色'] || properties.node_role || '',
    dynasty: properties['展示朝代'] || properties.dynasty || '',
    routeName: properties['路线名称'] || properties.route_name || '',
    lon,
    lat,
    properties,
  }
}

function groupRouteFeatures(features) {
  var index = new Map()
  ;(features || []).forEach(function(feature) {
    var routeId = String(feature && feature.properties && feature.properties.route_id || '')
    if (!routeId) return
    if (!index.has(routeId)) index.set(routeId, [])
    index.get(routeId).push(feature)
  })
  return index
}

function groupNodeFeatures(features) {
  var index = new Map()
  ;(features || []).forEach(function(feature) {
    var node = nodeFromFeature(feature)
    if (!node.routeId || !Number.isFinite(node.lon) || !Number.isFinite(node.lat)) return
    if (!index.has(node.routeId)) index.set(node.routeId, [])
    index.get(node.routeId).push(node)
  })
  index.forEach(function(nodes) {
    nodes.sort(function(a, b) { return Number(a.seq) - Number(b.seq) })
  })
  return index
}

function legacyRouteFor(routeId) {
  var legacyId = LEGACY_ROUTE_MATCH[routeId]
  return TEA_TRADE_DATA.find(function(route) { return Number(route.id) === Number(legacyId) }) || null
}

function buildRuntimeRoute(routeId) {
  var features = ancientRouteFeatureIndex.get(routeId) || []
  var nodes = ancientNodeFeatureIndex.get(routeId) || []
  var properties = features.length ? (features[0].properties || {}) : ((nodes[0] && nodes[0].properties) || {})
  var legacy = legacyRouteFor(routeId)
  var routeName = properties.route_name || properties['路线名称'] || (nodes[0] && nodes[0].routeName) || routeId
  var dynastyValue = properties.dynasty || properties['展示朝代'] || (nodes[0] && nodes[0].dynasty) || (legacy && legacy.dynasty)
  var dynastyNames = parseDynasties(dynastyValue)
  var firstDynasty = dynastyNames[0]
  var lastDynasty = dynastyNames[dynastyNames.length - 1]
  var firstStage = dynasties.find(function(item) { return item.name === firstDynasty }) || dynasties[0]
  var lastStage = dynasties.find(function(item) { return item.name === lastDynasty }) || firstStage
  var routeType = String(properties.route_type || '').toLowerCase()
  if (!['land', 'sea', 'mixed'].includes(routeType)) routeType = legacy ? routeTypeCode(legacy) : 'land'
  var geometrySegments = mergeOrderedSegments(features)
  var routeMode = geometrySegments.length ? 'digitized' : 'node_arc'
  var firstNode = nodes[0]
  var lastNode = nodes[nodes.length - 1]
  if ((!firstNode || !lastNode) && geometrySegments.length) {
    var firstCoordinate = geometrySegments[0][0]
    var lastSegment = geometrySegments[geometrySegments.length - 1]
    var lastCoordinate = lastSegment[lastSegment.length - 1]
    firstNode = firstNode || { name: '起点', lat: firstCoordinate[0], lon: firstCoordinate[1], seq: 1 }
    lastNode = lastNode || { name: '终点', lat: lastCoordinate[0], lon: lastCoordinate[1], seq: 2 }
    nodes = [firstNode, lastNode]
  }
  var origin = firstNode ? firstNode.name : (legacy && legacy.origin) || '起点'
  var destination = lastNode ? lastNode.name : (legacy && legacy.destination) || '终点'
  var via = nodes.slice(1, -1).map(function(node) { return node.name }).filter(Boolean)
  var modeText = routeMode === 'digitized' ? '历史路线复原' : '节点推定路线'
  var baseFact = legacy && legacy.note ? legacy.note : (properties.note || '')
  var sourceRefs = []
  if (legacy && Array.isArray(legacy.sourceRefs)) sourceRefs.push.apply(sourceRefs, legacy.sourceRefs)
  if (properties.source_url) sourceRefs.push(properties.source_url)
  return {
    ...(legacy || {}),
    id: routeId,
    routeId,
    title: routeName,
    routeName,
    type: routeType === 'sea' ? '海上' : routeType === 'mixed' ? '水陆联运' : '陆路',
    routeType: routeType === 'sea' ? '海路' : routeType === 'mixed' ? '水陆联运' : '陆路',
    routeTypeCode: routeType,
    routeMode,
    routeModeLabel: modeText,
    geometrySegments,
    dynasty: dynastyNames.join('至'),
    dynastyNames,
    startDynasty: firstDynasty,
    endDynasty: lastDynasty,
    startYear: firstStage.start,
    endYear: lastStage.end,
    yearText: dynastyNames.join('至'),
    origin,
    destination,
    points: nodes,
    via,
    historicalBackground: `${routeName}是${dynastyNames.join('至')}茶叶跨区域流通的重要通道。${baseFact || properties.note || ''}`,
    routeStory: `茶叶由${origin}出发${via.length ? `，依次经过${via.join('、')}` : ''}，抵达${destination}。地图以${modeText}方式呈现该通道；${routeMode === 'node_arc' ? '线形依据有序历史节点推定，不表示精确历史轨迹。' : '线形保留人工数字化成果的原始折点顺序与行进方向。'}`,
    tradeSignificance: legacy && legacy.tradeSignificance ? legacy.tradeSignificance : `该路线连接了${origin}与${destination}，反映茶叶贸易带动的区域交流与市场扩展。`,
    sourceRefs: Array.from(new Set(sourceRefs)),
    rawIndex: Number(routeId.replace(/\D/g, '')) || 0,
  }
}

function rebuildAncientTradeRoutes() {
  var ids = new Set()
  ancientRouteFeatureIndex.forEach(function(_, id) { ids.add(id) })
  ancientNodeFeatureIndex.forEach(function(_, id) { ids.add(id) })
  ancientTradeRoutes = Array.from(ids).sort(function(a, b) {
    return Number(a.replace(/\D/g, '')) - Number(b.replace(/\D/g, ''))
  }).map(buildRuntimeRoute).filter(function(route) {
    return route.points.length >= 2 || route.geometrySegments.length
  })
}

async function loadAncientRouteData() {
  var routeResult
  var nodeResult
  try {
    var response = await fetch(ANCIENT_ROUTE_URL)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    routeResult = await response.json()
  } catch (error) {
    console.error(`古代数字化路线加载失败（${ANCIENT_ROUTE_URL}）:`, error)
    routeResult = { features: [] }
  }
  try {
    var nodeResponse = await fetch(ANCIENT_NODE_URL)
    if (!nodeResponse.ok) throw new Error(`HTTP ${nodeResponse.status}`)
    nodeResult = await nodeResponse.json()
  } catch (error) {
    console.error(`古代路线节点加载失败（${ANCIENT_NODE_URL}）:`, error)
    nodeResult = { features: [] }
  }
  ancientRouteFeatureIndex = groupRouteFeatures(routeResult && routeResult.features)
  ancientNodeFeatureIndex = groupNodeFeatures(nodeResult && nodeResult.features)
  rebuildAncientTradeRoutes()
  if (!ancientTradeRoutes.length) {
    console.error('古代贸易 GeoJSON 未生成任何有效路线，保留旧数据作为页面降级显示。')
    ancientTradeRoutes = TEA_TRADE_DATA
  }
}
var sectionEl = ref(null)
var mapEl = ref(null)
var sliderTrack = ref(null)
var isPlaying = ref(false)
var routeFilter = ref('all')
const routeFilterOptions = [
  { label: '全部', value: 'all' },
  { label: '陆路', value: 'land' },
  { label: '海路', value: 'sea' },
]
var panelMode = ref('dynasty')
var selectedRoute = ref(null)
const chapter = CHAPTER_META.ch4
var selectedNodeName = ref('')
var nodeRouteOptions = ref([])
var introDone = ref(false)

var progress = ref(0.0)
var currentYear = computed(function() {
  return Math.floor(MIN_YEAR + progress.value * (MAX_YEAR - MIN_YEAR) + 1e-8)
})
var ancientLoading = ref(true)
var ancientError = ref(null)
var ancientMapReady = ref(false)
var isDraggingTimeline = ref(false)
var isAnimatingProgress = false

var map = null
var worldCountriesLayer = null
var routeLayer = null
var routeHitLayer = null
var nodeLayer = null
var nodeLabelLayer = null
var nodeHitLayer = null
var nodeRegistry = new Map()
var lastFrameTime = null
var animationFrameId = null

// Pre-computed route data with progress ranges
var routeProgressData = []
var routeProgressMap = new Map()
var cameraInitialized = false
var cameraUserControlled = false
var programmaticCameraMove = false
var lastCameraSignature = ''

const INITIAL_ROUTE_ZOOM = 7
const MIN_ROUTE_ZOOM = 2.25
const LABEL_FULL_SCALE = 5000000
const LABEL_HIDDEN_SCALE = 15000000

// Active routes cache
var activeRouteLayers = new Map()

var dynastyName = computed(function() { return getDynastyByProgress(progress.value).name })
var currentDynastyInfo = computed(function() { return DYNASTY_INFO[dynastyName.value] })
var panelKey = computed(function() {
  if (panelMode.value === 'dynasty') return 'dynasty-' + dynastyName.value
  if (selectedRoute.value) return 'route-' + selectedRoute.value.id
  return 'node-' + selectedNodeName.value
})
function pausePlayback() {
  isPlaying.value = false
  stopAnimationLoop()
}

function showDynastyPanel() {
  panelMode.value = 'dynasty'
  selectedRoute.value = null
  selectedNodeName.value = ''
  nodeRouteOptions.value = []
  if (map && routeLayer) renderCurrentProgress()
}

function jumpToDynasty(tick) {
  pausePlayback()
  showDynastyPanel()
  animateProgressTo(tick.progress, 500)
}

function openRouteDetail(route, event) {
  if (event && event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent)
  pausePlayback()
  panelMode.value = 'route'
  selectedRoute.value = route
  nodeRouteOptions.value = []
  renderCurrentProgress()
}

function selectRoute(route) {
  openRouteDetail(route)
}

function routeForVisual(rp) {
  var eligible = (rp.routes || [rp.route])
    .filter(function(route) { return routePassesFilter(route) })
    .filter(function(route) { return Number(route.startYear) <= currentYear.value + 1 })
    .sort(function(a, b) { return Number(b.startYear) - Number(a.startYear) })
  return eligible[0] || rp.route
}

// 资料卡时间显示
// 如果 yearText 包含具体年份（如"1607年"、"1701-1710年"），显示 yearText
// 如果 yearText 只包含朝代（如"唐宋-明清"、"宋"），显示"时间：" + yearText
var routeDisplayTime = computed(function() {
  if (!selectedRoute.value) return ''
  if (selectedRoute.value.yearText) return selectedRoute.value.yearText
  if (selectedRoute.value.startYear != null && selectedRoute.value.endYear != null) {
    return selectedRoute.value.startYear + '—' + selectedRoute.value.endYear + '年'
  }
  if (selectedRoute.value.startYear != null) return selectedRoute.value.startYear + '年'
  return selectedRoute.value.dynasty
})

var routeViaText = computed(function() {
  if (!selectedRoute.value) return ''
  var via = selectedRoute.value.via || []
  return via.length ? via.join(' → ') : '直达'
})
var routeModeLabel = computed(function() {
  if (!selectedRoute.value) return ''
  return selectedRoute.value.routeModeLabel || (selectedRoute.value.routeMode === 'node_arc' ? '节点推定路线' : '历史路线复原')
})

// 五种生命周期状态判断
function getRouteState(rp, targetProgress) {
  if (targetProgress < rp.startProgress) return 'hidden'
  if (targetProgress < rp.drawEndProgress) return 'drawing'
  if (targetProgress < rp.retireStartProgress) return 'active'
  if (targetProgress < rp.retireEndProgress) return 'retiring'
  return 'historical'
}

const NODE_FADE_PROGRESS = 0.008 // 60 秒完整播放时约 480ms
const DYNASTY_PLAY_DURATION_MS = {
  '唐代': 9000,
  '宋代': 9000,
  '元代': 8000,
  '明代': 9000,
  '清代': 15000,
  '抗战时期': 8000,
}
const DYNASTY_SETTLE_MS = 1500

function dynastyStage(name) {
  var index = Math.max(0, dynastyTicks.findIndex(function(tick) { return tick.name === name }))
  return {
    index,
    start: dynastyTicks[index].progress,
    end: index < dynastyTicks.length - 1 ? dynastyTicks[index + 1].progress : 1,
    duration: DYNASTY_PLAY_DURATION_MS[name] || 8000,
  }
}

function visualGeometryKey(route) {
  return route.routeId || route.id || visualPoints(route).map(function(point) {
    return point.name + ':' + Number(point.lon).toFixed(5) + ':' + Number(point.lat).toFixed(5)
  }).join('|')
}

// 同一朝代、同一节点序列的年度记录合并为一条视觉路线，再把视觉路线
// 分布到该朝代的叙事时长中；全部绘制在最后 1.5 秒稳定展示前完成。
function precomputeRouteProgress() {
  routeProgressData = []
  routeProgressMap = new Map()
  var groups = new Map()
  ancientTradeRoutes.forEach(function(route) {
    var key = route.startDynasty + '|' + visualGeometryKey(route)
    var group = groups.get(key)
    if (!group) {
      group = { key, routes: [], route }
      groups.set(key, group)
    }
    group.routes.push(route)
  })

  dynastyTicks.forEach(function(tick) {
    var stage = dynastyStage(tick.name)
    var stageGroups = Array.from(groups.values())
      .filter(function(group) { return group.route.startDynasty === tick.name })
      .sort(function(a, b) {
        return Number(a.route.startYear) - Number(b.route.startYear) || a.route.rawIndex - b.route.rawIndex
      })
    var count = stageGroups.length
    var drawingEndRatio = (stage.duration - DYNASTY_SETTLE_MS) / stage.duration
    var routeDrawRatio = count <= 1
      ? drawingEndRatio - 0.05
      : count <= 3
        ? Math.max(0.48, drawingEndRatio * 0.72)
        : Math.max(0.22, drawingEndRatio * 0.38)
    var startWindow = Math.max(0, drawingEndRatio - routeDrawRatio - 0.05)

    stageGroups.forEach(function(group, index) {
      var startRatio = count <= 1
        ? 0.05
        : 0.05 + startWindow * (index / Math.max(1, count - 1))
      var endRatio = Math.min(drawingEndRatio, startRatio + routeDrawRatio)
      if (index === count - 1) endRatio = drawingEndRatio
      var endDynastyIndex = Math.max.apply(null, group.routes.map(function(route) {
        return Math.max(stage.index, dynastyTicks.findIndex(function(item) { return item.name === route.endDynasty }))
      }))
      var lifeEnd = endDynastyIndex < dynastyTicks.length - 1
        ? dynastyTicks[endDynastyIndex + 1].progress
        : 1
      var nextStage = dynastyTicks[Math.min(dynastyTicks.length - 1, endDynastyIndex + 1)]
      var nextDuration = DYNASTY_PLAY_DURATION_MS[nextStage.name] || 8000
      var nextEnd = endDynastyIndex + 2 < dynastyTicks.length ? dynastyTicks[endDynastyIndex + 2].progress : 1
      var retireSpan = Math.max(0.004, (nextEnd - lifeEnd) * (1000 / nextDuration))
      var data = {
        route: group.route,
        routes: group.routes,
        startProgress: stage.start + (stage.end - stage.start) * startRatio,
        drawEndProgress: stage.start + (stage.end - stage.start) * endRatio,
        retireStartProgress: lifeEnd,
        retireEndProgress: Math.min(1, lifeEnd + retireSpan),
        nodeFadeProgress: (stage.end - stage.start) * (600 / stage.duration),
        key: 'visual-' + group.key,
        visual: null,
      }
      routeProgressData.push(data)
      group.routes.forEach(function(route) { routeProgressMap.set(String(route.id), data) })
    })
  })

  routeProgressData.sort(function(a, b) { return a.startProgress - b.startProgress })
}

function getVisiblePathSegments(fullSegments, routeProgress) {
  var segments = (fullSegments || []).filter(function(segment) { return segment && segment.length >= 2 })
  if (routeProgress <= 0 || !segments.length) return []
  if (routeProgress >= 1) return segments
  var totalEdges = segments.reduce(function(total, segment) { return total + segment.length - 1 }, 0)
  var remaining = Math.max(1, Math.floor(totalEdges * routeProgress))
  var visible = []
  for (var i = 0; i < segments.length && remaining > 0; i++) {
    var edgeCount = segments[i].length - 1
    var take = Math.min(edgeCount, remaining)
    visible.push(segments[i].slice(0, take + 1))
    remaining -= take
  }
  return visible
}

var routeFromTo = computed(function() {
  if (!selectedRoute.value) return ''
  return selectedRoute.value.origin + ' → ' + selectedRoute.value.destination
})

function onSliderMouseDown(e) {
  isDraggingTimeline.value = true
  pausePlayback()
  showDynastyPanel()
  updateProgressFromEvent(e)
  window.addEventListener('mousemove', onSliderMouseMove)
  window.addEventListener('mouseup', onSliderMouseUp)
}

function onSliderMouseMove(e) {
  if (!isDraggingTimeline.value) return
  updateProgressFromEvent(e)
}

function onSliderMouseUp(e) {
  isDraggingTimeline.value = false
  window.removeEventListener('mousemove', onSliderMouseMove)
  window.removeEventListener('mouseup', onSliderMouseUp)
}

function updateProgressFromEvent(e) {
  if (!sliderTrack.value) return
  var rect = sliderTrack.value.getBoundingClientRect()
  var x = Math.max(0, Math.min(rect.width, e.clientX - rect.left))
  var newProgress = rect.width > 0 ? x / rect.width : 0
  progress.value = newProgress
  renderCurrentProgress()
}

function animateProgressTo(targetProgress, duration) {
  if (isAnimatingProgress) return
  isAnimatingProgress = true
  if (isPlaying.value) {
    isPlaying.value = false
    stopAnimationLoop()
  }
  var startProgress = progress.value
  var startTime = null
  function step(timestamp) {
    if (!isAnimatingProgress) return
    if (startTime === null) startTime = timestamp
    var elapsed = timestamp - startTime
    var t = Math.min(1, elapsed / duration)
    var eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
    progress.value = startProgress + (targetProgress - startProgress) * eased
    renderCurrentProgress()
    if (t < 1) {
      requestAnimationFrame(step)
    } else {
      isAnimatingProgress = false
    }
  }
  requestAnimationFrame(step)
}

function renderCurrentProgress() {
  if (!map || !routeLayer || !nodeLayer) return
  drawRoutesAtProgress(progress.value)
}

function cameraRoutesAtProgress(targetProgress) {
  if (targetProgress <= 0.000001) return []
  return routeProgressData.filter(function(rp) {
    return routePassesFilter(routeForVisual(rp)) && targetProgress + 0.000001 >= rp.startProgress
  })
}

function initialRouteCoordinate() {
  for (var i = 0; i < routeProgressData.length; i++) {
    var segments = routePathSegments(routeProgressData[i].route)
    if (segments.length && segments[0].length) return L.latLng(segments[0][0])
  }
  return L.latLng(31, 103)
}

function updateMapViewForProgress(targetProgress) {
  if (!map || !mapEl.value) return
  if (cameraUserControlled) return

  var cameraRoutes = cameraRoutesAtProgress(targetProgress)
  var signature = routeFilter.value + ':' + cameraRoutes.map(function(rp) {
    return routeForVisual(rp).id
  }).sort().join('|')
  if (cameraInitialized && signature === lastCameraSignature) return

  var coordinates = []
  cameraRoutes.forEach(function(rp) {
    routePathSegments(routeForVisual(rp)).forEach(function(segment) {
      segment.forEach(function(coordinate) { coordinates.push(coordinate) })
    })
  })
  var targetCenter
  var targetZoom
  if (coordinates.length < 2) {
    targetCenter = initialRouteCoordinate()
    targetZoom = INITIAL_ROUTE_ZOOM
  } else {
    var bounds = L.latLngBounds(coordinates)
    targetCenter = bounds.getCenter()
    targetZoom = map.getBoundsZoom(bounds, false, [420, 180])
    targetZoom = Math.max(MIN_ROUTE_ZOOM, Math.min(INITIAL_ROUTE_ZOOM, targetZoom))
    // 右侧资料卡会占用地图空间；轻微向东移动镜头中心，使中国落在可视区中部偏右。
    var projectedCenter = map.project(targetCenter, targetZoom).add(L.point(90, 0))
    targetCenter = map.unproject(projectedCenter, targetZoom)
  }

  if (!cameraInitialized) {
    programmaticCameraMove = true
    map.setView(targetCenter, targetZoom, { animate: false })
    cameraInitialized = true
    lastCameraSignature = signature
    programmaticCameraMove = false
    return
  }

  lastCameraSignature = signature
  programmaticCameraMove = true
  map.stop()
  map.flyTo(targetCenter, targetZoom, {
    animate: true,
    duration: 2.2,
    easeLinearity: 0.22,
    noMoveStart: false,
  })
  map.once('moveend', function() { programmaticCameraMove = false })
}

function currentScaleDenominator() {
  if (!map) return LABEL_HIDDEN_SCALE
  var latitude = Math.max(-85, Math.min(85, map.getCenter().lat))
  var metresPerPixel = 156543.03392 * Math.cos(latitude * Math.PI / 180) / Math.pow(2, map.getZoom())
  return metresPerPixel * 96 * 39.37007874
}

function labelVisibilityFactor() {
  var scale = currentScaleDenominator()
  if (scale <= LABEL_FULL_SCALE) return 1
  if (scale >= LABEL_HIDDEN_SCALE) return 0
  return 1 - (scale - LABEL_FULL_SCALE) / (LABEL_HIDDEN_SCALE - LABEL_FULL_SCALE)
}

function stableLabelRank(name, lat, lng) {
  var value = String(name || '') + '|' + Number(lat).toFixed(4) + '|' + Number(lng).toFixed(4)
  var hash = 0
  for (var i = 0; i < value.length; i++) hash = ((hash << 5) - hash + value.charCodeAt(i)) | 0
  return (Math.abs(hash) % 1000) / 1000
}

function escapeNodeLabel(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function routeNodeFractions(points, pathSegments) {
  if (!points || points.length <= 1) return [0]
  var samples = []
  var total = 0
  ;(pathSegments || []).forEach(function(segment) {
    segment.forEach(function(coordinate, index) {
      if (index > 0) total += L.latLng(segment[index - 1]).distanceTo(L.latLng(coordinate))
      samples.push({ coordinate, distance: total })
    })
  })
  if (!samples.length || total <= 0) return points.map(function(_, index) { return index / (points.length - 1) })
  var lastIndex = 0
  return points.map(function(point, pointIndex) {
    var bestIndex = lastIndex
    var bestDistance = Infinity
    for (var i = lastIndex; i < samples.length; i++) {
      var sampleDistance = L.latLng(point.lat, point.lon).distanceTo(L.latLng(samples[i].coordinate))
      if (sampleDistance < bestDistance) {
        bestDistance = sampleDistance
        bestIndex = i
      }
    }
    lastIndex = bestIndex
    if (pointIndex === points.length - 1) return 1
    return Math.max(0, Math.min(1, samples[bestIndex].distance / total))
  })
}

function buildRouteRegistry() {
  routeLayer.clearLayers()
  routeHitLayer.clearLayers()
  routeProgressData.forEach(function(rp) {
    var fullPathSegments = routePathSegments(rp.route)
    if (!fullPathSegments.length) return
    var baseColor = kind(rp.route) === 'sea' ? '#5C7C3A' : '#B28F4C'
    var historicalColor = kind(rp.route) === 'sea' ? '#6B8060' : '#8A8270'
    var primaryLine = L.polyline([], {
      pane: 'tradeRoutePane', color: baseColor, weight: 2.8, opacity: 0, dashArray: null,
      smoothFactor: 0.5, lineCap: 'round', lineJoin: 'round', interactive: false,
    }).addTo(routeLayer)
    var historicalLine = L.polyline([], {
      pane: 'tradeRoutePane', color: historicalColor, weight: 1.8, opacity: 0,
      smoothFactor: 0.5, dashArray: '6 4', lineCap: 'round', lineJoin: 'round', interactive: false,
    }).addTo(routeLayer)
    var hitLine = L.polyline([], {
      pane: 'routeHitPane', color: '#000000', weight: 14, opacity: 0.001,
      interactive: true, bubblingMouseEvents: false,
    }).addTo(routeHitLayer)
    rp.visual = { fullPathSegments, primaryLine, historicalLine, hitLine, hover: false }
    hitLine.on('click', function(event) { openRouteDetail(routeForVisual(rp), event) })
    hitLine.on('mouseover', function() {
      rp.visual.hover = true
      map.getContainer().style.cursor = 'pointer'
      updateRouteVisual(rp, progress.value)
    })
    hitLine.on('mouseout', function() {
      rp.visual.hover = false
      map.getContainer().style.cursor = ''
      updateRouteVisual(rp, progress.value)
    })
    hitLine.bindTooltip('', { sticky: true, direction: 'top', offset: [0, -6], className: 'ch4-tip' })
  })
}

function updateRouteVisual(rp, targetProgress) {
  if (!rp.visual) return
  var visual = rp.visual
  var passes = routePassesFilter(rp.route)
  var state = passes ? getRouteState(rp, targetProgress) : 'hidden'
  if (state === 'hidden') {
    visual.primaryLine.setLatLngs([])
    visual.historicalLine.setLatLngs([])
    visual.hitLine.setLatLngs([])
    return
  }
  var drawSpan = Math.max(0.000001, rp.drawEndProgress - rp.startProgress)
  var local = state === 'drawing'
    ? Math.max(0, Math.min(1, (targetProgress - rp.startProgress) / drawSpan))
    : 1
  var visiblePath = getVisiblePathSegments(visual.fullPathSegments, local)
  if (!visiblePath.length) {
    visual.primaryLine.setLatLngs([])
    visual.historicalLine.setLatLngs([])
    visual.hitLine.setLatLngs([])
    return
  }
  var highlighted = visual.hover || (selectedRoute.value && routeProgressMap.get(String(selectedRoute.value.id)) === rp)
  var weightBoost = highlighted ? 1.5 : 0
  var primaryOpacity = state === 'historical' ? 0 : 0.9
  var historicalOpacity = state === 'historical' ? 0.6 : 0
  if (state === 'drawing') primaryOpacity = 0.95
  if (state === 'retiring') {
    var retireSpan = Math.max(0.000001, rp.retireEndProgress - rp.retireStartProgress)
    var retire = Math.max(0, Math.min(1, (targetProgress - rp.retireStartProgress) / retireSpan))
    primaryOpacity = (1 - retire) * 0.9
    historicalOpacity = retire * 0.6
  }
  if (highlighted) {
    if (primaryOpacity > 0) primaryOpacity = 1
    if (historicalOpacity > 0) historicalOpacity = 0.9
  }
  visual.primaryLine.setLatLngs(visiblePath)
  visual.primaryLine.setStyle({ weight: 2.8 + weightBoost, opacity: primaryOpacity })
  visual.historicalLine.setLatLngs(state === 'drawing' ? [] : visiblePath)
  visual.historicalLine.setStyle({ weight: 1.8 + weightBoost, opacity: historicalOpacity })
  visual.hitLine.setLatLngs(visiblePath)
  var detailRoute = routeForVisual(rp)
  visual.hitLine.setTooltipContent((detailRoute.yearText || detailRoute.dynasty) + '｜' + detailRoute.origin + '→' + detailRoute.destination)
}

function buildNodeRegistry() {
  nodeLayer.clearLayers()
  nodeLabelLayer.clearLayers()
  nodeHitLayer.clearLayers()
  nodeRegistry.clear()
  routeProgressData.forEach(function(rp) {
    var points = visualPoints(rp.route)
    var fractions = routeNodeFractions(points, routePathSegments(rp.route))
    points.forEach(function(point, nodeIndex) {
      if (!point || point.lon == null || point.lat == null) return
      var nodeKey = (point.name || '路线节点') + '|' + Number(point.lat).toFixed(6) + '|' + Number(point.lon).toFixed(6)
      var node = nodeRegistry.get(nodeKey)
      if (!node) {
        var marker = L.circleMarker([point.lat, point.lon], {
          pane: 'tradeNodePane', radius: 5, fillColor: '#B28F4C', color: '#ffffff',
          weight: 2, fillOpacity: 0, opacity: 0, interactive: false,
        }).addTo(nodeLayer)
        var hitMarker = L.circleMarker([point.lat, point.lon], {
          pane: 'nodeHitPane', radius: 10, color: '#000000', weight: 0,
          opacity: 0, fillOpacity: 0, interactive: true, bubblingMouseEvents: false,
        })
        var labelMarker = L.marker([point.lat, point.lon], {
          pane: 'tradeNodeLabelPane', interactive: false, keyboard: false, opacity: 0,
          icon: L.divIcon({
            className: 'ch4-node-label-icon',
            html: '<span>' + escapeNodeLabel(point.name || '路线节点') + '</span>',
            iconSize: null,
            iconAnchor: [-9, 13],
          }),
        }).addTo(nodeLabelLayer)
        node = {
          marker, hitMarker, labelMarker, routeIds: new Set(), routeFractions: new Map(),
          name: point.name || '路线节点', lat: Number(point.lat), lng: Number(point.lon), hitEnabled: false,
          currentOpacity: 0, labelRank: stableLabelRank(point.name, point.lat, point.lon),
        }
        hitMarker.bindTooltip(node.name, { direction: 'top', offset: [0, -6], className: 'ch4-node-tip' })
        hitMarker.on('click', function(event) {
          openNodeDetail(node, event)
        })
        nodeRegistry.set(nodeKey, node)
      }
      ;(rp.routes || [rp.route]).forEach(function(route) {
        var id = String(route.id)
        node.routeIds.add(id)
        node.routeFractions.set(id, fractions[nodeIndex] || 0)
      })
    })
  })
}

function nodeOpacityForRoute(node, routeId, targetProgress) {
  var rp = routeProgressMap.get(String(routeId))
  if (!rp || !routePassesFilter(rp.route) || targetProgress < rp.startProgress) return 0
  var fraction = node.routeFractions.get(String(routeId)) || 0
  var trigger = rp.startProgress + (rp.drawEndProgress - rp.startProgress) * fraction
  var fadeSpan = Math.max(0.0001, rp.nodeFadeProgress || NODE_FADE_PROGRESS)
  var opacity = Math.max(0, Math.min(1, (targetProgress - trigger) / fadeSpan))
  var state = getRouteState(rp, targetProgress)
  if (state === 'retiring') {
    var span = Math.max(0.000001, rp.retireEndProgress - rp.retireStartProgress)
    opacity *= 1 - Math.max(0, Math.min(1, (targetProgress - rp.retireStartProgress) / span)) * 0.5
  } else if (state === 'historical') opacity = Math.min(opacity, 0.5)
  return opacity
}

function updateNodeMarkers(targetProgress) {
  var labelFactor = labelVisibilityFactor()
  nodeRegistry.forEach(function(node) {
    var bestOpacity = 0
    var bestRoute = null
    node.routeIds.forEach(function(routeId) {
      var opacity = nodeOpacityForRoute(node, routeId, targetProgress)
      if (opacity > bestOpacity) {
        bestOpacity = opacity
        var rp = routeProgressMap.get(String(routeId))
        bestRoute = rp && routeForVisual(rp)
      }
    })
    node.marker.setStyle({
      fillColor: bestRoute && kind(bestRoute) === 'sea' ? '#5C7C3A' : '#B28F4C',
      fillOpacity: bestOpacity, opacity: bestOpacity,
    })
    node.currentOpacity = bestOpacity
    var labelVisible = labelFactor > 0 && node.labelRank <= labelFactor && bestOpacity > 0.12
    var labelOpacity = labelVisible ? Math.min(1, bestOpacity) * Math.min(1, labelFactor * 1.7) : 0
    node.labelMarker.setOpacity(labelOpacity)
    var enabled = bestOpacity > 0.05
    if (enabled && !node.hitEnabled) {
      nodeHitLayer.addLayer(node.hitMarker)
      node.hitEnabled = true
    } else if (!enabled && node.hitEnabled) {
      nodeHitLayer.removeLayer(node.hitMarker)
      node.hitEnabled = false
    }
    node.hitMarker.setStyle({ opacity: enabled ? 0.001 : 0, fillOpacity: enabled ? 0.001 : 0 })
    var hitElement = node.hitMarker.getElement()
    if (hitElement) hitElement.style.pointerEvents = enabled ? 'auto' : 'none'
  })
}

function getRoutesForNode(node) {
  var candidates = []
  node.routeIds.forEach(function(routeId) {
    var rp = routeProgressMap.get(String(routeId))
    if (!rp || !routePassesFilter(rp.route) || rp.startProgress > progress.value + 1e-8) return
    candidates.push({ rp, route: routeForVisual(rp) })
  })
  if (!candidates.length) return []
  var current = candidates.filter(function(item) {
    return getDynastyByProgress(item.rp.startProgress).name === dynastyName.value
  })
  var list = current.length ? current : candidates
  list.sort(function(a, b) {
    return b.rp.startProgress - a.rp.startProgress || Number(b.route.startYear) - Number(a.route.startYear)
  })
  return list.map(function(item) { return item.route }).filter(function(route, index, routes) {
    return routes.findIndex(function(candidate) { return candidate.id === route.id }) === index
  })
}

function openNodeDetail(node, event) {
  if (event && event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent)
  var routes = getRoutesForNode(node)
  if (!routes.length) return
  pausePlayback()
  if (routes.length === 1) {
    openRouteDetail(routes[0], event)
    return
  }
  panelMode.value = 'route'
  selectedRoute.value = null
  selectedNodeName.value = node.name
  nodeRouteOptions.value = routes
}

function drawRoutesAtProgress(targetProgress) {
  updateMapViewForProgress(targetProgress)
  routeProgressData.forEach(function(rp) { updateRouteVisual(rp, targetProgress) })
  updateNodeMarkers(targetProgress)
}

function startAnimationLoop() {
  if (animationFrameId) return
  lastFrameTime = null
  isAnimatingProgress = false
  
  function animate(currentTime) {
    if (!isPlaying.value) {
      animationFrameId = null
      return
    }

    if (lastFrameTime === null) {
      lastFrameTime = currentTime
    }

    var deltaTime = currentTime - lastFrameTime
    lastFrameTime = currentTime

    var activeTick = getDynastyByProgress(progress.value)
    var stage = dynastyStage(activeTick.name)
    var stageSpan = Math.max(0.000001, stage.end - stage.start)
    var newProgress = progress.value + deltaTime * (stageSpan / stage.duration)
    newProgress = Math.min(stage.end, newProgress)

    if (newProgress >= 1.0) {
      progress.value = 1.0
      isPlaying.value = false
      stopAnimationLoop()
      renderCurrentProgress()
      return
    }

    progress.value = newProgress
    renderCurrentProgress()
    animationFrameId = requestAnimationFrame(animate)
  }
  
  animationFrameId = requestAnimationFrame(animate)
}

function stopAnimationLoop() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function togglePlay() {
  if (isDraggingTimeline.value) return
  
  if (!isPlaying.value) {
    if (progress.value >= 1.0) {
      progress.value = 0
      cameraInitialized = false
      cameraUserControlled = false
      programmaticCameraMove = false
      lastCameraSignature = ''
    }
    showDynastyPanel()
    isPlaying.value = true
    startAnimationLoop()
  } else {
    isPlaying.value = false
    stopAnimationLoop()
  }
}

function resetView() {
  stopAnimationLoop()
  isAnimatingProgress = false
  isPlaying.value = false
  progress.value = 0
  cameraInitialized = false
  cameraUserControlled = false
  programmaticCameraMove = false
  lastCameraSignature = ''
  showDynastyPanel()
  renderCurrentProgress()
}

function reloadMap() {
  ancientError.value = null
  ancientLoading.value = true
  nextTick(function() {
    initMap()
  })
}

function initMap() {
  if (!mapEl.value) {
    console.error('地图容器不存在')
    ancientError.value = '地图容器未找到，请刷新页面'
    ancientLoading.value = false
    return
  }

  var rect = mapEl.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    console.warn('地图容器尺寸为0，延迟初始化')
    setTimeout(function() { initMap() }, 100)
    return
  }

  ancientLoading.value = true
  ancientError.value = null
  ancientMapReady.value = false

  try {
    if (map) {
      map.remove()
      map = null
    }

    map = L.map(mapEl.value, {
      center: [31, 103],
      zoom: INITIAL_ROUTE_ZOOM,
      minZoom: 1.5,
      maxZoom: 7,
      zoomSnap: 0.25,
      zoomDelta: 0.5,
      worldCopyJump: true,
      zoomControl: false,
      attributionControl: false,
      preferCanvas: true,
    })

    map.createPane('chinaProvincePane')
    map.getPane('chinaProvincePane').style.zIndex = 340
    map.createPane('worldCountriesPane')
    map.getPane('worldCountriesPane').style.zIndex = 220
    map.createPane('chinaBorderHaloPane')
    map.getPane('chinaBorderHaloPane').style.zIndex = 350
    map.createPane('chinaBorderPane')
    map.getPane('chinaBorderPane').style.zIndex = 355
    map.createPane('tradeRoutePane')
    map.getPane('tradeRoutePane').style.zIndex = 460
    map.createPane('routeHitPane')
    map.getPane('routeHitPane').style.zIndex = 470
    map.createPane('tradeNodePane')
    map.getPane('tradeNodePane').style.zIndex = 480
    map.createPane('tradeNodeLabelPane')
    map.getPane('tradeNodeLabelPane').style.zIndex = 485
    map.createPane('nodeHitPane')
    map.getPane('nodeHitPane').style.zIndex = 490

    L.control.zoom({ position: 'bottomright' }).addTo(map)

    routeLayer = L.layerGroup().addTo(map)
    routeHitLayer = L.layerGroup().addTo(map)
    nodeLayer = L.layerGroup().addTo(map)
    nodeLabelLayer = L.layerGroup().addTo(map)
    nodeHitLayer = L.layerGroup().addTo(map)

    map.on('click', function() {
      if (panelMode.value === 'route') showDynastyPanel()
    })
    map.on('zoom', function() {
      if (nodeRegistry.size) updateNodeMarkers(progress.value)
    })

    // 用户开始拖动、触摸或滚轮操作时立即接管镜头，瓦片加载期间也能自由移动。
    var takeManualCameraControl = function() {
      cameraUserControlled = true
      programmaticCameraMove = false
      if (map) map.stop()
    }
    map.getContainer().addEventListener('pointerdown', takeManualCameraControl, { passive: true })
    map.getContainer().addEventListener('wheel', takeManualCameraControl, { passive: true })

    loadWorldBoundary()
    loadChinaBoundary()

    precomputeRouteProgress()
    buildRouteRegistry()
    buildNodeRegistry()

    progress.value = 0
    cameraInitialized = false
    cameraUserControlled = false
    programmaticCameraMove = false
    lastCameraSignature = ''
    nextTick(function() {
      map.invalidateSize()
      renderCurrentProgress()
      ancientLoading.value = false
      ancientMapReady.value = true
    })

    setupMapResizeObserver()

    console.log('古代贸易地图初始化成功')
  } catch (err) {
    console.error('地图初始化失败:', err)
    ancientError.value = '地图初始化失败: ' + (err.message || '未知错误')
    ancientLoading.value = false
  }
}

function fitToShowAllRoutes() {
  if (!map) return

  // Calculate bounds from all routes
  var allLatLngs = []
  routeProgressData.forEach(function(rp) {
    var route = rp.route
    try {
      var segments = routePathSegments(route)
      segments.forEach(function(segment) {
        segment.forEach(function(pt) {
          allLatLngs.push([pt[0], pt[1]])
        })
      })
    } catch (e) {}
  })

  if (allLatLngs.length > 0) {
    var bounds = L.latLngBounds(allLatLngs)
    // Add padding and show most of the world
    map.fitBounds(bounds.pad(0.3), { duration: 0.5, maxZoom: 4 })
  } else {
    // Fallback: show a large area covering China to Europe/Africa
    map.setView([25, 100], 3)
  }
}

function setupMapResizeObserver() {
  if (!mapEl.value) return

  if (window._ch4ResizeObserver) {
    window._ch4ResizeObserver.disconnect()
  }

  var observer = new ResizeObserver(function(entries) {
    for (var i = 0; i < entries.length; i++) {
      var entry = entries[i]
      if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
        if (map) map.invalidateSize()
      }
    }
  })

  observer.observe(mapEl.value)
  window._ch4ResizeObserver = observer

  // Also handle visibility changes
  document.addEventListener('visibilitychange', onVisibilityChange)
}

function onVisibilityChange() {
  if (!document.hidden && map) {
    setTimeout(function() {
      if (map) map.invalidateSize()
    }, 100)
  }
}

function loadWorldBoundary() {
  fetch(WORLD_COUNTRIES_URL)
    .then(function(response) {
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return response.json()
    })
    .then(function(geo) {
      if (!map || !geo || geo.type !== 'FeatureCollection') return
      if (worldCountriesLayer) worldCountriesLayer.remove()
      worldCountriesLayer = L.geoJSON(geo, {
        pane: 'worldCountriesPane',
        interactive: false,
        smoothFactor: 0.7,
        style: function() {
          return {
            color: '#D8CDAF',
            weight: 0.72,
            opacity: 0.8,
            fillColor: '#F7F4EB',
            fillOpacity: 0.96,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: false,
          }
        },
      }).addTo(map)
    })
    .catch(function(error) {
      console.warn(`本地世界底图加载失败（${WORLD_COUNTRIES_URL}）:`, error)
    })
}

function loadChinaBoundary() {
  // 省界和国界使用独立 pane；任一请求失败都不影响路线与另一边界层。
  fetch(assetUrl('data/2/china-provinces.geojson'))
    .then(function(r) { return r.json() })
    .then(function(geo) {
      if (!map) return
      try {
        if (!geo || !geo.type) {
          console.warn('中国边界数据加载失败，无有效GeoJSON')
          return
        }
        L.geoJSON(geo, {
          pane: 'chinaProvincePane',
          interactive: false,
          style: function() {
            return {
              color: '#D8CDAF',
              weight: 0.8,
              opacity: 0.85,
              dashArray: '3 4',
              lineCap: 'round',
              fillColor: '#F7F4EB',
              fillOpacity: 0.42,
              interactive: false,
            }
          },
        }).addTo(map)
      } catch (renderErr) {
        console.warn('中国省界渲染失败:', renderErr)
      }
    })
    .catch(function(err) {
      console.warn('中国省界数据加载失败:', err)
    })

  fetch(assetUrl('data/1/china_outline.geojson'))
    .then(function(r) { return r.json() })
    .then(function(geo) {
      if (!map || !geo || !geo.type) return
      L.geoJSON(geo, {
        pane: 'chinaBorderHaloPane',
        interactive: false,
        style: function() {
          return {
            color: '#F7F4EB', weight: 4.6, opacity: 0.95,
            fillOpacity: 0, interactive: false,
          }
        },
      }).addTo(map)
      L.geoJSON(geo, {
        pane: 'chinaBorderPane',
        interactive: false,
        style: function() {
          return {
            color: '#9A712C',
            weight: 2.5,
            opacity: 1,
            dashArray: null,
            lineCap: 'round',
            lineJoin: 'round',
            fillOpacity: 0,
            interactive: false,
          }
        },
      }).addTo(map)
    })
    .catch(function(err) {
      console.warn('中国国界轮廓加载失败，已保留省界与贸易路线:', err)
    })
}

function onKeydown(e) {
  if (e.code === 'ArrowRight') {
    e.preventDefault()
    pausePlayback()
    showDynastyPanel()
    progress.value = Math.min(1, progress.value + 0.005)
    renderCurrentProgress()
  } else if (e.code === 'ArrowLeft') {
    e.preventDefault()
    pausePlayback()
    showDynastyPanel()
    progress.value = Math.max(0, progress.value - 0.005)
    renderCurrentProgress()
  } else if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  }
}

function onIntroDone() {
  introDone.value = true
  setTimeout(function() {
    if (map) {
      map.invalidateSize()
      renderCurrentProgress()
    }
  }, 300)
}

// ==========================================================================
// Part 2: 当代贸易情况
// ==========================================================================
var modernMapEl = ref(null)
// 2015 年仅作为 2016 年同比计算的内部基期，不在年份选择器中展示。
var modernYears = MODERN_YEARS.filter(function(y) { return y >= 2016 && y <= 2025 })
var modernYear = ref(2024)
var isModernChinaMode = ref(true)
var selectedModernProvince = ref(null)
var hoveredProvince = ref(null)

var modernMap = null
var modernProvLayer = null
var modernFlowLayer = null
var modernMarkersLayer = null
var modernBubbleLayer = null
var modernProvinceGeoJsonPromise = null
var modernHighlightedCountry = null

var modernProvinceInfo = reactive({
  provinceValue: null,
  totalValue: 0,
  flows: [],
  year: 2024,
  share: null,
  yoy: null,
  hasData: false,
})

const MIN_LEAF_SIZE = 14
const MAX_LEAF_SIZE = 50
const MODERN_FLOW_DRAW_DURATION = 2600
const MODERN_FLOW_START_DELAY_STEP = 45
const MODERN_FLOW_INITIAL_DELAY = 140
// 页面以 0.01 亿元显示出口额；低于 0.005 亿元时会显示为 0.00，
// 因而按无有效贸易额处理：不绘制、不悬停展示、不可点击进入详情。
const MIN_VISIBLE_EXPORT_VALUE = 0.005 * 1e8

function hasVisibleExportValue(value) {
  var number = Number(value)
  return value != null && Number.isFinite(number) && number >= MIN_VISIBLE_EXPORT_VALUE
}

const MODERN_GLOBAL_MAX_VALUE = Math.max.apply(null, modernYears.flatMap(function(year) {
  return getProvinceExports(year)
    .filter(function(item) { return item && hasVisibleExportValue(item.value) })
    .map(function(item) { return Number(item.value) })
}).concat([0]))

function normalizeProvinceName(name) {
  return String(name || '').replace(/省|市|自治区|壮族|回族|维吾尔|特别行政区|特别行政/g, '')
}

function findProvinceRecord(records, provinceName) {
  var target = normalizeProvinceName(provinceName)
  return (records || []).find(function(item) {
    return item.name === provinceName || normalizeProvinceName(item.name) === target
  }) || null
}

function resolveProvinceName(featureName) {
  var target = normalizeProvinceName(featureName)
  var knownNames = Object.keys(PROVINCE_CENTER)
  for (var i = 0; i < knownNames.length; i++) {
    if (normalizeProvinceName(knownNames[i]) === target) return knownNames[i]
  }
  var current = findProvinceRecord(getProvinceExports(modernYear.value), featureName)
  return current ? current.name : featureName
}

function calculateYoY(currentValue, previousValue) {
  if (currentValue == null || previousValue == null || Number(previousValue) <= 0) return null
  return ((Number(currentValue) - Number(previousValue)) / Number(previousValue)) * 100
}

function formatYoY(yoy) {
  if (yoy == null || !Number.isFinite(Number(yoy))) return '暂无可比数据'
  var value = Number(yoy)
  return (value > 0 ? '+' : '') + value.toFixed(1) + '%'
}

function getCountryBarStyle(value) {
  var firstValue = modernProvinceInfo.flows.length ? Number(modernProvinceInfo.flows[0].value) : 0
  var ratio = firstValue > 0 ? Math.max(0.0001, Math.min(1, Number(value) / firstValue)) : 0.0001
  return {
    '--w': (ratio * 100) + '%',
    // 渐变层始终保持第一名对应的完整宽度，外层按当前数值比例裁切。
    '--gradient-width': (100 / ratio) + '%',
  }
}

function getYoYColor(yoy) {
  if (yoy == null || !Number.isFinite(Number(yoy))) return '#D8D2C2'
  if (yoy >= 20) return '#516D33'
  if (yoy >= 5) return '#7F985D'
  if (yoy >= 0) return '#A8B68D'
  if (yoy >= -5) return '#C3C19A'
  return '#B28F4C'
}

function getLeafSize(value, globalMaxValue) {
  if (!hasVisibleExportValue(value) || Number(globalMaxValue) <= 0) return 0
  return MIN_LEAF_SIZE + Math.sqrt(Number(value) / Number(globalMaxValue)) * (MAX_LEAF_SIZE - MIN_LEAF_SIZE)
}

var provinceBubbleData = computed(function() {
  var currentRecords = getProvinceExports(modernYear.value)
  var previousRecords = getProvinceExports(modernYear.value - 1)
  var total = currentRecords.reduce(function(sum, item) {
    return item && item.value != null ? sum + Number(item.value) : sum
  }, 0)
  var names = new Set(Object.keys(PROVINCE_CENTER))
  currentRecords.forEach(function(item) { names.add(item.name) })

  return Array.from(names).map(function(provinceName) {
    var current = findProvinceRecord(currentRecords, provinceName)
    var previous = findProvinceRecord(previousRecords, provinceName)
    var currentValue = current && current.value != null ? Number(current.value) : null
    var previousValue = previous && previous.value != null ? Number(previous.value) : null
    var hasData = hasVisibleExportValue(currentValue)
    return {
      provinceName: current ? current.name : provinceName,
      currentValue: currentValue,
      previousValue: previousValue,
      valueYi: hasData ? currentValue / 1e8 : null,
      yoy: calculateYoY(currentValue, previousValue),
      share: hasData && total > 0 ? currentValue / total * 100 : null,
      center: PROVINCE_CENTER[(current && current.name) || provinceName] || null,
      hasData: hasData,
    }
  })
})

function getProvinceBubble(provinceName) {
  var target = normalizeProvinceName(provinceName)
  return provinceBubbleData.value.find(function(item) {
    return normalizeProvinceName(item.provinceName) === target
  }) || null
}

var leafSizeLegendItems = computed(function() {
  return [0.25, 0.5, 1].map(function(ratio) {
    var value = MODERN_GLOBAL_MAX_VALUE * ratio
    return {
      ratio: ratio,
      valueYi: value / 1e8,
      displaySize: getLeafSize(value, MODERN_GLOBAL_MAX_VALUE),
    }
  })
})

const leafColorLegendItems = [
  { label: '≥20%', color: '#516D33' },
  { label: '5%—20%', color: '#7F985D' },
  { label: '0—5%', color: '#A8B68D' },
  { label: '-5%—0', color: '#C3C19A' },
  { label: '＜-5%', color: '#B28F4C' },
]

function createLeafSvg(color, selected, opacity) {
  var stroke = selected ? '#B28F4C' : '#F7F4EB'
  var strokeWidth = selected ? 4 : 1.4
  return '<svg class="province-leaf-svg" viewBox="0 0 64 64" aria-hidden="true" style="opacity:' + (opacity == null ? 1 : opacity) + '">' +
    '<path class="leaf-body" d="M55 7C36 8 18 16 10 31C4 42 9 53 20 56C34 60 47 45 52 28C55 18 55 11 55 7Z" fill="' + color + '" stroke="' + stroke + '" stroke-width="' + strokeWidth + '" stroke-linejoin="round" vector-effect="non-scaling-stroke" />' +
    '<path class="leaf-vein" d="M15 50C25 39 35 28 49 15" />' +
    '<path class="leaf-vein secondary" d="M25 39L23 27M34 30L34 19M28 36L41 37" />' +
    '</svg>'
}

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
  // Leaflet 的 padding 坐标顺序为 [横向, 纵向]；上下保持一致，让中国位于地图区的垂直中央。
  modernMap.fitBounds([[-45, -40], [55, 150]], { paddingTopLeft: [40, 40], paddingBottomRight: [360, 40], animate: true })
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

function modernProvinceStyle(featureName) {
  var selected = selectedModernProvince.value &&
    normalizeProvinceName(selectedModernProvince.value) === normalizeProvinceName(featureName)
  return selected ? {
    pane: 'modernProvincePane',
    color: '#B28F4C', weight: 2, opacity: 1,
    fillColor: '#F7F4EB', fillOpacity: 0.34,
    dashArray: null, lineCap: 'round', lineJoin: 'round',
    interactive: true, bubblingMouseEvents: false,
  } : {
    pane: 'modernProvincePane',
    color: '#D8CDAF', weight: 0.8, opacity: 0.85,
    fillColor: '#F7F4EB', fillOpacity: 0.28,
    dashArray: null, lineCap: 'round', lineJoin: 'round',
    interactive: true, bubblingMouseEvents: false,
  }
}

function hoverProvinceData(provinceName) {
  var item = getProvinceBubble(provinceName)
  if (!item) return { name: provinceName, hasData: false, valueYi: null, share: null, yoy: null, markets: '暂无数据' }
  var flowInfo = item.hasData ? estimateProvinceFlows(item.provinceName, modernYear.value, 3) : null
  return {
    name: item.provinceName,
    hasData: item.hasData,
    valueYi: item.valueYi,
    share: item.share,
    yoy: item.yoy,
    markets: flowInfo && flowInfo.flows.length
      ? flowInfo.flows.map(function(flow) { return flow.country }).join('、')
      : '暂无数据',
  }
}

function provinceBubbleTooltip(item) {
  if (!item || !item.hasData) return '<b>' + (item ? item.provinceName : '省份') + '</b><br/>该年份暂无数据'
  return '<b>' + item.provinceName + '</b>' +
    '<br/>出口额：' + fmtNum(item.valueYi) + ' 亿元' +
    '<br/>全国占比：' + fmtNum(item.share) + '%' +
    '<br/>同比增速：' + formatYoY(item.yoy)
}

function stopModernMapEvent(event) {
  if (event && event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent)
}

function ensureModernProvinceLayer() {
  if (!modernMap) return Promise.resolve(null)
  if (modernProvLayer) {
    modernProvLayer.setStyle(function(feature) {
      var featureName = feature.properties.name || feature.properties.NAME || feature.properties.NL_NAME_1 || ''
      return modernProvinceStyle(resolveProvinceName(featureName))
    })
    return Promise.resolve(modernProvLayer)
  }
  if (!modernProvinceGeoJsonPromise) {
    modernProvinceGeoJsonPromise = fetch(assetUrl('data/2/china-provinces.geojson')).then(function(response) {
      if (!response.ok) throw new Error('省级GeoJSON加载失败：' + response.status)
      return response.json()
    })
  }
  return modernProvinceGeoJsonPromise.then(function(geo) {
    if (!modernMap) return null
    modernProvLayer = L.geoJSON(geo, {
      pane: 'modernProvincePane',
      interactive: true,
      bubblingMouseEvents: false,
      style: function(feature) {
        var featureName = feature.properties.name || feature.properties.NAME || feature.properties.NL_NAME_1 || ''
        return modernProvinceStyle(resolveProvinceName(featureName))
      },
      onEachFeature: function(feature, layer) {
        var featureName = feature.properties.name || feature.properties.NAME || feature.properties.NL_NAME_1 || ''
        var provinceName = resolveProvinceName(featureName)
        layer.on('mouseover', function() {
          var bubble = getProvinceBubble(provinceName)
          var clickable = Boolean(bubble && bubble.hasData)
          hoveredProvince.value = clickable ? hoverProvinceData(provinceName) : null
          var path = layer.getElement && layer.getElement()
          if (path) path.style.cursor = clickable ? 'pointer' : 'default'
          if (!clickable) return
          var selected = selectedModernProvince.value &&
            normalizeProvinceName(selectedModernProvince.value) === normalizeProvinceName(provinceName)
          layer.setStyle({ color: selected ? '#B28F4C' : '#516D33', weight: selected ? 2.2 : 1.5 })
          layer.bringToFront()
        })
        layer.on('mouseout', function() {
          hoveredProvince.value = null
          if (modernProvLayer) modernProvLayer.resetStyle(layer)
        })
        layer.on('click', function(event) {
          stopModernMapEvent(event)
          var bubble = getProvinceBubble(provinceName)
          if (!bubble || !bubble.hasData) return
          enterWorldMode(provinceName)
        })
      },
    }).addTo(modernMap)
    return modernProvLayer
  }).catch(function(error) {
    console.warn('当代贸易省界加载失败:', error)
    return null
  })
}

function renderModernProvinceBubbles(options) {
  if (!modernMap || !modernBubbleLayer) return
  var opts = options || {}
  var selectedProvince = opts.selectedProvince || null
  var detailMode = Boolean(opts.detailMode)
  var modeScale = detailMode ? 0.72 : 1
  modernBubbleLayer.clearLayers()

  provinceBubbleData.value.forEach(function(item) {
    if (!item.hasData || !item.center) return
    var selected = selectedProvince &&
      normalizeProvinceName(selectedProvince) === normalizeProvinceName(item.provinceName)
    var baseSize = getLeafSize(item.currentValue, MODERN_GLOBAL_MAX_VALUE)
    var size = baseSize * modeScale * (selected ? 1.08 : 1)
    var opacity = detailMode && !selected ? 0.5 : 1
    var icon = L.divIcon({
      className: 'province-tea-leaf-icon' + (selected ? ' selected' : '') + (detailMode && !selected ? ' muted' : ''),
      html: createLeafSvg(getYoYColor(item.yoy), selected, opacity),
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
      tooltipAnchor: [0, -size * 0.35],
    })
    var marker = L.marker(item.center, {
      icon: icon,
      pane: selected
        ? 'modernSelectedBubblePane'
        : (detailMode ? 'modernDetailBubblePane' : 'modernBubblePane'),
      interactive: true,
      bubblingMouseEvents: false,
      keyboard: true,
      riseOnHover: true,
      riseOffset: 1200,
      zIndexOffset: selected ? 1800 : 0,
      title: item.provinceName,
    })
    marker.bindTooltip(provinceBubbleTooltip(item), {
      direction: 'top', offset: [0, -4], opacity: 0.96, className: 'route-tip province-bubble-tip',
    })
    marker.on('mouseover', function() {
      hoveredProvince.value = hoverProvinceData(item.provinceName)
      marker.setZIndexOffset(selected ? 2400 : 1600)
      var el = marker.getElement()
      if (el) el.classList.add('hovered')
    })
    marker.on('mouseout', function() {
      hoveredProvince.value = null
      marker.setZIndexOffset(selected ? 1800 : 0)
      var el = marker.getElement()
      if (el) el.classList.remove('hovered')
    })
    marker.on('click', function(event) {
      stopModernMapEvent(event)
      enterWorldMode(item.provinceName)
    })
    marker.addTo(modernBubbleLayer)
  })
}

function onModernYearChange() {
  hoveredProvince.value = null
  if (isModernChinaMode.value) renderModernChinaProvinces()
  else if (selectedModernProvince.value) enterWorldMode(selectedModernProvince.value, { preserveView: true, allowEmpty: true })
}

function renderModernChinaProvinces() {
  if (!modernMap) return
  selectedModernProvince.value = null
  ensureModernProvinceLayer()
  renderModernProvinceBubbles({ selectedProvince: null, detailMode: false })
}

function enterWorldMode(provinceName, options) {
  var opts = options || {}
  var bubble = getProvinceBubble(provinceName)
  var hasData = Boolean(bubble && bubble.hasData)
  if (!hasData && !opts.allowEmpty) return
  selectedModernProvince.value = provinceName
  isModernChinaMode.value = false
  var info = hasData ? estimateProvinceFlows(provinceName, modernYear.value, 20) : null
  Object.assign(modernProvinceInfo, {
    provinceValue: hasData ? bubble.currentValue : null,
    totalValue: info ? info.totalValue : 0,
    flows: info ? info.flows : [],
    year: modernYear.value,
    share: hasData ? bubble.share : null,
    yoy: hasData ? bubble.yoy : null,
    hasData: hasData,
  })

  nextTick(function() {
    if (!modernMap) return
    modernMap.invalidateSize()
    if (!opts.preserveView) fitModernWorldBounds()
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

  var bubble = getProvinceBubble(provinceName)
  var center = (bubble && bubble.center) || PROVINCE_CENTER[provinceName]
  ensureModernProvinceLayer()
  renderModernProvinceBubbles({ selectedProvince: provinceName, detailMode: true })
  if (!center) return
  var fromLat = center[0], fromLon = center[1]

  // 阻止事件冒泡到地图 click 空白区返回逻辑
  var stopClick = function(ev) { L.DomEvent.stopPropagation(ev) }

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
    var finalOpacity = 0.45 + itemNorm * 0.45
    var tipHtml = '<b>' + provinceName + ' → ' + f.country + '</b><br/>出口额：' + fmtNum(f.value / 1e8) + ' 亿元'

    // ========== 1. 创建线路（初始只含起点，动画中逐点追加）==========
    var startPts = [pts[0]]
    var line = L.polyline(startPts, {
      pane: 'modernFlowPane',
      color: col, weight: Math.max(0.7, w * 0.35), opacity: finalOpacity * 0.2,
      lineCap: 'round', lineJoin: 'round', interactive: false,
      bubblingMouseEvents: true,
    })
    line._flowData = { country: f.country, value: f.value }
    line._baseStyle = { weight: w, opacity: finalOpacity }
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
      pane: 'modernFlowMarkerPane',
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
    var startDelay = MODERN_FLOW_INITIAL_DELAY + MODERN_FLOW_START_DELAY_STEP * sortIdx  // 大额先绘制

    function animateFlow(timestamp) {
      if (!startTime) startTime = timestamp
      var elapsed = timestamp - startTime
      if (elapsed < startDelay) {
        window._ch4FlowAnimTimers.push(requestAnimationFrame(animateFlow))
        return
      }
      var localElapsed = elapsed - startDelay
      var progress = Math.min(1, localElapsed / MODERN_FLOW_DRAW_DURATION)
      // easeInOutSine：起止柔和，中段匀速，避免线路突然冲出。
      var eased = 0.5 - Math.cos(Math.PI * progress) / 2
      var targetIndex = Math.floor(eased * (totalPts - 1)) + 1
      if (targetIndex < totalPts) {
        var subPts = pts.slice(0, targetIndex)
        line.setLatLngs(subPts)
      } else {
        line.setLatLngs(pts)
      }
      // 路线从中心向外舒展时同步由淡变实、由细变粗，形成花瓣绽放感。
      line.setStyle({
        weight: Math.max(0.7, w * (0.35 + eased * 0.65)),
        opacity: finalOpacity * (0.2 + eased * 0.8),
      })

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
        line.setStyle({ interactive: true, weight: w, opacity: finalOpacity })
        marker.setStyle({ interactive: true, radius: r, fillOpacity: 1, opacity: 0.95 })

        // 命中辅助线
        var hitLine = L.polyline(pts, {
          pane: 'modernFlowPane',
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

  // 省级起点由选中的茶叶符号承担；流向线直接从同一省级中心出发。
  // Pane 层级已固定，无需对 LayerGroup 调用不存在的 bringToFront()。
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
  modernMap.createPane('modernProvincePane')
  modernMap.getPane('modernProvincePane').style.zIndex = 410
  // 详情模式中的未选中茶叶位于流向线下方，避免遮挡路线。
  modernMap.createPane('modernDetailBubblePane')
  modernMap.getPane('modernDetailBubblePane').style.zIndex = 430
  modernMap.createPane('modernFlowPane')
  modernMap.getPane('modernFlowPane').style.zIndex = 440
  modernMap.createPane('modernFlowMarkerPane')
  modernMap.getPane('modernFlowMarkerPane').style.zIndex = 450
  modernMap.createPane('modernBubblePane')
  modernMap.getPane('modernBubblePane').style.zIndex = 470
  modernMap.createPane('modernSelectedBubblePane')
  modernMap.getPane('modernSelectedBubblePane').style.zIndex = 480
  L.control.zoom({ position: 'bottomright' }).addTo(modernMap)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 9, subdomains: 'abcd',
  }).addTo(modernMap)
  modernBubbleLayer = L.layerGroup().addTo(modernMap)

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
  if (nv === 'ancient') {
    nextTick(function() {
      if (map) {
        map.invalidateSize()
        renderCurrentProgress()
      } else {
        initMap()
      }
    })
  }
})

onMounted(async function() {
  await nextTick()
  await loadAncientRouteData()
  initMap()

  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', onWindowResize)
})

onBeforeUnmount(function() {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onWindowResize)
  document.removeEventListener('visibilitychange', onVisibilityChange)

  stopAnimationLoop()
  isAnimatingProgress = false

  if (window._ch4ResizeObserver) {
    window._ch4ResizeObserver.disconnect()
    window._ch4ResizeObserver = null
  }

  window.removeEventListener('mousemove', onSliderMouseMove)
  window.removeEventListener('mouseup', onSliderMouseUp)

  if (map) {
    map.remove()
    map = null
  }
  routeLayer = null
  routeHitLayer = null
  nodeLayer = null
  nodeHitLayer = null
  nodeRegistry.clear()
  activeRouteLayers.clear()

  if (modernMap) {
    modernMap.remove()
    modernMap = null
  }
  modernProvLayer = null
  modernFlowLayer = null
  modernMarkersLayer = null
  modernBubbleLayer = null
  modernProvinceGeoJsonPromise = null
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
  transition: opacity 1.45s ease-in-out;
  display: flex;
  flex-direction: column;
}
.map-fullscreen.show {
  opacity: 1;
}

/* ================================================================
   古代贸易发展 - 新布局
   ================================================================ */
.ch4-view-ancient {
  --serif: var(--font-body);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.ch4-ancient-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 520px;
  position: relative;
  padding: 12px 16px 0;
  gap: 0;
}

/* Loading State */
.map-loading, .map-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(247, 244, 235, 0.95);
  z-index: 100;
  border-radius: 12px;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(92, 124, 58, 0.2);
  border-top-color: #5C7C3A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text, .error-text {
  font: 600 15px/1 var(--serif);
  color: #516D33;
  letter-spacing: 0.1em;
}

.error-icon { font-size: 36px; }
.error-hint { font-size: 13px; color: #7A7060; max-width: 280px; text-align: center; }
.reload-btn {
  padding: 8px 20px;
  border: 1.5px solid #B28F4C;
  border-radius: 8px;
  background: #fff;
  color: #B28F4C;
  font: 600 13px/1 var(--serif);
  cursor: pointer;
  transition: all 0.25s ease;
}
.reload-btn:hover { background: #B28F4C; color: #fff; }

/* Map Stage - the main area */
.ch4-stage {
  position: relative;
  flex: 1;
  min-height: calc(100vh - 200px);
  border-radius: 12px;
  overflow: hidden;
  background: #F7F4EB;
  box-shadow: 0 2px 12px rgba(81, 109, 51, 0.08);
  border: 1px solid rgba(81, 109, 51, 0.12);
}

.ch4-stage .map {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 200px);
  z-index: 1;
  background: #D7E0E1;
}

.route-filter-control {
  align-self: center;
  flex-shrink: 0;
  display: flex;
  gap: 5px;
  padding: 5px;
  border: 1px solid rgba(178, 143, 76, 0.3);
  border-radius: 18px;
  background: rgba(247, 244, 235, 0.9);
  backdrop-filter: blur(6px);
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.08);
}
.route-filter-btn {
  padding: 5px 10px;
  border: 0;
  border-radius: 13px;
  background: transparent;
  color: #516D33;
  font: 600 11px/1 var(--serif);
  cursor: pointer;
}
.route-filter-btn:hover { background: rgba(81, 109, 51, 0.1); }
.route-filter-btn.active { background: #516D33; color: #F7F4EB; }

/* Legend - compact, bottom-left overlay (raised above floating timeline) */
.map-legend {
  position: absolute;
  bottom: clamp(248px, 33vh, 300px);
  left: 12px;
  z-index: 400;
  background: rgba(247, 244, 235, 0.92);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(178, 143, 76, 0.3);
  border-radius: 10px;
  padding: 10px 14px;
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.08);
  min-width: 160px;
}

.legend-title {
  font: 600 11px/1 var(--serif);
  color: #516D33;
  letter-spacing: 0.12em;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(178, 143, 76, 0.2);
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font: 500 11px/1 var(--sans);
  color: #5A6655;
  margin-bottom: 5px;
}

.legend-row:last-child { margin-bottom: 0; }

.legend-line {
  width: 20px;
  height: 3px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-line.land { background: #B28F4C; }
.legend-line.sea { background: #5C7C3A; }
.legend-line.digitized { background: #7C765F; height: 2px; }
.legend-line.inferred {
  height: 0;
  background: none;
  border-top: 2px dashed #8A8270;
  opacity: 0.65;
}

:deep(.ch4-node-label-icon) {
  width: max-content !important;
  height: auto !important;
  background: rgba(247, 244, 235, 0.94);
  border: 1px solid rgba(178, 143, 76, 0.48);
  border-radius: 12px;
  box-shadow: 0 2px 7px rgba(72, 64, 43, 0.13);
  color: #4d5f35;
  font-family: var(--font-body, inherit);
  font-size: 13px;
  font-weight: 500;
  line-height: 1;
  padding: 5px 9px;
  white-space: nowrap;
  pointer-events: none;
  transition: opacity 180ms linear;
}

.legend-row.nodes .legend-line {
  height: 8px;
  width: 8px;
  border-radius: 50%;
}

.legend-node {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid #fff;
}

.legend-node.origin { background: #196c58; }
.legend-node.destination { background: #B28F4C; }

/* Route Info Panel - right side overlay */
.route-detail-panel {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 280px;
  max-height: calc(100% - 24px);
  z-index: 400;
  background: rgba(247, 244, 235, 0.96);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(178, 143, 76, 0.4);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(81, 109, 51, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(178, 143, 76, 0.2);
  flex-shrink: 0;
}

.panel-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.panel-type-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font: 600 11px/1 var(--serif);
  letter-spacing: 0.05em;
}

.panel-type-tag.land { background: rgba(178, 143, 76, 0.15); color: #8E6E32; }
.panel-type-tag.sea { background: rgba(92, 124, 58, 0.15); color: #5C7C3A; }
.panel-type-tag.dynasty { background: rgba(81, 109, 51, 0.12); color: #516D33; }

.panel-dynasty-tag {
  padding: 3px 10px;
  background: rgba(81, 109, 51, 0.1);
  color: #516D33;
  border-radius: 12px;
  font: 600 11px/1 var(--serif);
}

.panel-back {
  border: 0;
  background: transparent;
  color: #5C7C3A;
  font: 600 10px/1.2 var(--serif);
  cursor: pointer;
  padding: 4px 0 4px 8px;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.panel-back:hover { color: #8E6E32; }

.panel-title-row {
  padding: 10px 14px;
  flex-shrink: 0;
}

.panel-title {
  font: 700 16px/1.3 var(--serif);
  color: #516D33;
  letter-spacing: 0.05em;
  margin: 0;
}

.panel-subtitle {
  margin: 6px 0 0;
  color: #7A7060;
  font: 500 11px/1.5 var(--sans);
}

.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 4px 14px 14px;
}

.panel-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(178, 143, 76, 0.15);
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font: 500 10px/1 var(--sans);
  color: #9A9080;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.info-value {
  font: 600 12px/1.3 var(--serif);
  color: #3A4A2A;
}

.info-item-wide { grid-column: 1 / -1; }

.panel-section {
  margin-bottom: 14px;
}

.section-label {
  font: 600 11px/1 var(--serif);
  color: #516D33;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(81, 109, 51, 0.15);
}

.section-text {
  font: 500 12px/1.7 var(--sans);
  color: #4A5A3A;
  margin: 0;
  text-align: justify;
}

/* 朝代切换仅做 280ms 透明度过渡，信息框不会关闭或位移。 */
.ancient-panel-fade-enter-active,
.ancient-panel-fade-leave-active { transition: opacity 0.28s ease; }
.ancient-panel-fade-enter-from,
.ancient-panel-fade-leave-to { opacity: 0; }

.node-route-list { display: flex; flex-direction: column; gap: 8px; }
.node-route-option {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  width: 100%;
  padding: 9px 10px;
  border: 1px solid rgba(178, 143, 76, 0.25);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.45);
  color: #3A4A2A;
  text-align: left;
  cursor: pointer;
}
.node-route-option:hover { border-color: #B28F4C; background: rgba(178, 143, 76, 0.08); }
.node-route-option strong { font: 600 12px/1.45 var(--serif); }
.node-route-kind { color: #7A7060; font: 500 10px/1 var(--sans); }

/* ================================================================
   Floating Timeline (inside map container, half-floating)
   ================================================================ */
.timeline-floating {
  position: absolute;
  bottom: clamp(96px, 13vh, 122px);
  left: 50%;
  transform: translateX(-50%);
  width: min(72%, 980px);
  z-index: 1000;
  pointer-events: auto;
  padding: 12px 18px 14px;
  background: rgba(250, 247, 239, 0.82);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(178, 143, 76, 0.4);
  border-radius: 14px;
  box-shadow: 0 6px 24px rgba(81, 109, 51, 0.16);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 90px;
  max-height: 170px;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.current-dynasty-label {
  font: 700 18px/1 var(--serif);
  color: #516D33;
  letter-spacing: 0.08em;
}

.timeline-controls {
  display: flex;
  gap: 8px;
}

.play-btn, .reset-btn {
  padding: 6px 16px;
  border-radius: 8px;
  font: 600 13px/1 var(--serif);
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.25s ease;
  letter-spacing: 0.05em;
}

.play-btn {
  background: #5C7C3A;
  color: #fff;
  border: 1.5px solid #5C7C3A;
}

.play-btn:hover {
  background: #516D33;
  border-color: #516D33;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.2);
}

.play-btn.playing {
  background: #B28F4C;
  border-color: #B28F4C;
}

.reset-btn {
  background: transparent;
  color: #5C7C3A;
  border: 1.5px solid #C3C19A;
}

.reset-btn:hover {
  background: rgba(92, 124, 58, 0.1);
  border-color: #5C7C3A;
  color: #5C7C3A;
}

.timeline-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-height: 0;
}

.timeline-axis {
  position: relative;
  height: 44px;
  margin: 0 32px;
}

.dynasty-tick {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 72px;
  padding: 0;
  transform: translateX(-50%);
  border: 0;
  background: transparent;
  cursor: pointer;
  z-index: 2;
}

.dynasty-tick:hover .tick-label,
.dynasty-tick.active .tick-label { color: #516D33; font-weight: 700; }

.tick-mark {
  position: absolute;
  left: 50%;
  bottom: 4px;
  width: 2px;
  height: 8px;
  transform: translateX(-50%);
  background: #B28F4C;
  border-radius: 1px;
  transition: height 0.2s ease, background 0.2s ease;
}

.dynasty-tick.active .tick-mark { height: 11px; background: #516D33; }

.tick-label {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  font: 600 12px/1.15 var(--serif);
  color: #7A7060;
  letter-spacing: 0.05em;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.dynasty-tick.alternate .tick-label { top: 0; }

.slider-track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 6px;
  height: 4px;
  background: rgba(195, 193, 154, 0.3);
  border-radius: 2px;
  cursor: pointer;
  pointer-events: auto;
  z-index: 1;
}

.slider-fill {
  height: 100%;
  background: linear-gradient(90deg, #B28F4C, #5C7C3A);
  border-radius: 2px;
}

.slider-thumb {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  background: #fff;
  border: 2.5px solid #5C7C3A;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: grab;
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.slider-thumb:hover {
  transform: translate(-50%, -50%) scale(1.15);
  box-shadow: 0 2px 12px rgba(81, 109, 51, 0.35);
}

.slider-thumb:active {
  cursor: grabbing;
}

/* ================================================================
   Leaflet map custom styles
   ================================================================ */
.ch4-tip, .ch4-node-tip {
  background: rgba(247, 244, 235, 0.97) !important;
  border: 1px solid rgba(178, 143, 76, 0.4) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(81, 109, 51, 0.15) !important;
  color: #3A4A2A !important;
  font: 500 12px/1.5 var(--serif) !important;
  padding: 6px 12px !important;
}

.ch4-tip::before, .ch4-node-tip::before {
  border-top-color: rgba(178, 143, 76, 0.4) !important;
}

.leaflet-control-zoom {
  background: rgba(247, 244, 235, 0.9) !important;
  border: 1px solid rgba(178, 143, 76, 0.3) !important;
  border-radius: 8px !important;
  overflow: hidden;
}

.leaflet-control-zoom a {
  background: transparent !important;
  color: #516D33 !important;
  font-weight: bold;
  border-color: rgba(178, 143, 76, 0.2) !important;
}

.leaflet-control-zoom a:hover {
  background: rgba(92, 124, 58, 0.1) !important;
  color: #516D33 !important;
}

/* Scrollbar styling */
.panel-scroll::-webkit-scrollbar {
  width: 4px;
}
.panel-scroll::-webkit-scrollbar-track {
  background: rgba(178, 143, 76, 0.1);
  border-radius: 2px;
}
.panel-scroll::-webkit-scrollbar-thumb {
  background: rgba(178, 143, 76, 0.4);
  border-radius: 2px;
}
.panel-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(178, 143, 76, 0.6);
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .play-btn,
  .reset-btn {
    transition: none;
  }
  .loading-spinner {
    animation-duration: 2s;
  }
}

/* Responsive adjustments */
@media (max-width: 900px) {
  .route-detail-panel {
    width: 240px;
    right: 8px;
    top: 8px;
  }

  .ch4-ancient-container {
    padding: 8px;
    min-height: 480px;
  }

  .ch4-stage {
    min-height: calc(100vh - 180px);
  }

  .timeline-floating {
    width: 90%;
    padding: 10px 14px;
    bottom: clamp(96px, 13vh, 122px);
  }

  .map-legend {
    padding: 8px 12px;
    min-width: 140px;
  }

  .legend-row {
    font-size: 10px;
  }
}

@media (max-width: 640px) {
  .route-detail-panel {
    width: calc(100% - 16px);
    right: 8px;
    left: 8px;
    top: auto;
    bottom: 160px;
    max-height: 45%;
  }

  .current-dynasty-label {
    font-size: 16px;
  }

  .legend-row {
    font-size: 10px;
    gap: 6px;
  }

  .timeline-floating {
    width: 92%;
    padding: 8px 12px;
  }
}

/* ================================================================
   当代贸易情况
   ================================================================ */
.ch4-view-modern { padding-top: 8px; }

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

.ch4-view-ancient .ch4-stage {
  min-height: calc(100vh - 200px);
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
.modern-topbar,
.modern-topbar :deep(*) {
  font-family: var(--font-body) !important;
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
.hc-row.market-row { align-items: flex-start; gap: 12px; }
.hc-row.market-row b { max-width: 126px; white-space: normal; text-align: right; line-height: 1.35; }
.hc-empty { padding-top: 4px; color: var(--c-beige-dark); font-size: 12px; }

:deep(.province-tea-leaf-icon) {
  border: 0;
  background: transparent;
  cursor: pointer;
  overflow: visible;
}
:deep(.province-tea-leaf-icon::before) {
  content: '';
  position: absolute;
  inset: -5px;
}
:deep(.province-leaf-svg) {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
  transform-origin: 50% 50%;
  animation: province-leaf-in 400ms ease both;
}
:deep(.province-leaf-svg .leaf-vein) {
  fill: none;
  stroke: #F7F4EB;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.76;
  vector-effect: non-scaling-stroke;
}
:deep(.province-leaf-svg .leaf-vein.secondary) {
  stroke-width: 1.7;
  opacity: 0.62;
}
:deep(.province-tea-leaf-icon.hovered .province-leaf-svg) {
  filter: drop-shadow(0 2px 3px rgba(81, 109, 51, 0.26));
  transform: scale(1.04);
}
:deep(.province-tea-leaf-icon.selected .province-leaf-svg) {
  filter: drop-shadow(0 2px 4px rgba(178, 143, 76, 0.38));
}
@keyframes province-leaf-in {
  from { opacity: 0; transform: scale(0.84); }
  to { opacity: 1; transform: scale(1); }
}

:deep(.province-bubble-tip) {
  background: rgba(247, 244, 235, 0.98) !important;
  border: 1px solid rgba(178, 143, 76, 0.34) !important;
  color: #516D33 !important;
  box-shadow: 0 4px 14px rgba(81, 109, 51, 0.15);
  font: 500 12px/1.55 var(--serif);
}

.modern-legend {
  left: 16px !important;
  top: auto !important;
  bottom: 16px !important;
  z-index: 950;
  width: 248px;
  min-width: 0;
  padding: 9px 11px;
}
.modern-legend,
.modern-legend :deep(*) {
  font-family: var(--font-body), KaiTi, STKaiti, serif !important;
  font-style: normal !important;
}
.modern-legend-section + .modern-legend-section {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(178, 143, 76, 0.26);
}
.modern-legend-title {
  margin-bottom: 6px;
  color: #516D33;
  font: normal 700 11px/1.35 var(--font-body), KaiTi, STKaiti, serif;
}
.modern-legend-guide {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(178, 143, 76, 0.26);
  color: #516D33;
  font: normal 500 11px/1.55 var(--font-body), KaiTi, STKaiti, serif;
}
.leaf-size-legend {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: end;
  gap: 4px;
}
.leaf-size-item {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 3px;
  color: var(--c-beige-dark);
  font: normal 600 10px/1 var(--font-body), KaiTi, STKaiti, serif;
}
.legend-leaf {
  display: inline-block;
  flex: none;
}
.legend-leaf :deep(.province-leaf-svg) {
  animation: none;
}
.leaf-color-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 5px 8px;
}
.leaf-color-item {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 5px;
  color: var(--c-beige-dark);
  font: normal 500 10px/1.2 var(--font-body), KaiTi, STKaiti, serif;
}
.color-leaf {
  width: 18px;
  height: 18px;
}
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
.province-trade-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
  margin: 0 12px 8px;
  padding: 9px 10px;
  border-radius: 8px;
  background: rgba(239, 233, 218, 0.58);
}
.province-trade-summary div { min-width: 0; }
.province-trade-summary span,
.province-trade-summary b { display: block; }
.province-trade-summary span { margin-bottom: 4px; color: var(--c-beige-dark); font-size: 10px; }
.province-trade-summary b { color: var(--c-olive); font: 700 11px/1.2 var(--serif); white-space: nowrap; }
.modern-empty-state {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding: 24px;
  color: var(--c-beige-dark);
  font: 500 13px/1.6 var(--serif);
  text-align: center;
}
.country-row {
  display: grid;
  grid-template-columns: 22px 108px minmax(48px, 1fr) auto;
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
.cr-name { font: 600 12px/1 var(--serif); color: var(--c-olive); white-space: nowrap; overflow: visible; text-overflow: clip; }
.cr-bar-wrap { height: 7px; background: rgba(178,143,76,0.15); border-radius: 4px; overflow: hidden; }
.cr-bar { height: 100%; width: var(--w); border-radius: 4px; overflow: hidden; }
.cr-bar::before {
  content: '';
  display: block;
  width: var(--gradient-width);
  height: 100%;
  background: linear-gradient(90deg, #516D33 0%, #C28B3E 55%, #C8462E 100%);
  border-radius: 4px;
}
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
