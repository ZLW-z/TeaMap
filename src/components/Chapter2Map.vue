<template>
  <section class="chapter chapter-2">
    <ChapterIntro
      ch-no="贰"
      title="何以生茶"
      desc="得天独厚的光照、气候与土壤条件，编织出适配茶树生长的天然温床，一方水土的禀赋，悄悄决定了茶叶的诞生与品质。"
      :duration="2.5"
      @done="onIntroDone"
    />

    <div class="map-fullscreen" :class="{
      show: introDone,
      'mode-empty':     displayMode === 'empty',
      'mode-single':    displayMode === 'single',
      'mode-grid':      displayMode === 'grid',
      'mode-composite': displayMode === 'composite',
    }">
      <!-- 主地图 (Leaflet, 用于大图/综合图) -->
      <div
        class="map-stage"
        :class="{ active: displayMode === 'single' || displayMode === 'composite' || displayMode === 'empty' }"
      >
        <div ref="mapRef" class="map"></div>
        <!-- 因子图层淡入过渡包装 -->
        <div class="factor-fade-mask" :class="{ show: layerFading }"></div>
        <!-- 地图标题 (大图模式下显示) -->
        <div v-if="displayMode !== 'grid'" class="map-title-bar">
          <div v-if="isComposite" key="composite-title" class="map-title">
            茶树生态适宜性<strong>综合评价</strong>
          </div>
          <div v-else-if="currentFactor" :key="'title-'+currentFactor" class="map-title">
            {{ currentConfig.name }}适宜性分析
          </div>
          <div v-else class="map-title">开启转盘 · 抽取因子</div>
        </div>
      </div>

      <!-- 缩略图网格: 2 行 × 3 列, 用于 mode-grid (集齐5因子) -->
      <div v-if="displayMode === 'grid'" class="thumb-grid">
        <div v-for="(fid, idx) in pickedFactorHistory"
             :key="'thumb-grid-'+fid"
             class="thumb-cell"
             :class="{'pos-last': idx===4}"
             @click="openThumbAsMain(fid)"
        >
          <div class="thumb-tag">
            <span class="thumb-tag-name">{{ FACTORS[fid].name }}</span>
          </div>
          <div class="thumb-img-wrap">
            <img class="thumb-img" :src="FACTORS[fid].png" :alt="FACTORS[fid].name" />
          </div>
        </div>
      </div>

      <!-- 已抽取因子缩略条: 2~5 个, 位于左上 (mode-single) -->
      <transition-group v-if="displayMode === 'single' && pickedFactorHistory.length >= 2"
                        name="thumb-strip"
                        tag="div"
                        class="thumb-strip">
        <div v-for="(fid, i) in thumbnailsShown"
             :key="'thumb-strip-'+fid"
             class="strip-card"
             :class="{ active: fid === currentFactor }"
             @click="openThumbAsMain(fid)"
        >
          <div class="strip-img-wrap">
            <img class="strip-img" :src="FACTORS[fid].png" :alt="FACTORS[fid].name" />
          </div>
          <div class="strip-meta">
            <span class="strip-meta-name">{{ FACTORS[fid].name }}</span>
          </div>
        </div>
      </transition-group>

      <!-- 图例: 垂直居中左侧 (非 grid 模式显示) -->
      <div class="map-legend" :class="{ 'hide-in-grid': displayMode === 'grid' }">
        <div v-if="isComposite" key="legend-composite">
          <div class="legend-title">综合分级</div>
          <div v-for="lv in COMPOSITE.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
        <div v-else-if="currentFactor" :key="'legend-'+currentFactor">
          <div class="legend-title">{{ currentConfig.name }}</div>
          <div v-for="lv in currentConfig.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
        <div v-else>
          <div class="legend-title">五因子分级</div>
          <div v-for="lv in FACTORS.precip.levels" :key="lv.value" class="legend-row">
            <span class="sw" :style="{ background: lv.color }"></span>
            <span>{{ lv.label }}</span>
          </div>
        </div>
      </div>

      <!-- 转盘停靠区 (始终固定右下) -->
      <div class="wheel-dock">
        <transition name="card-expand">
          <div v-if="expandedFactor && (displayMode==='single' || displayMode==='composite')"
               class="factor-card" @click="collapseCard">
            <div class="card-header">
              <span class="card-title">{{ expandedConfig.name }}适宜性</span>
              <span class="card-close">×</span>
            </div>
            <div class="card-desc">{{ expandedConfig.desc }}</div>
            <div class="card-legend">
              <div v-for="lv in expandedConfig.levels" :key="lv.value" class="legend-item">
                <span class="swatch" :style="{ background: lv.color }"></span>
                <span>{{ lv.label }}</span>
              </div>
            </div>
          </div>
        </transition>

        <div
          class="wheel-wrap"
          ref="wheelRef"
        >
          <div class="wheel">
            <!-- 转盘 SVG: 5 独立扇区 (WHEEL_ORDER = [ph, precip, temp, accum, rad]) -->
            <svg viewBox="-110 -110 220 220" class="wheel-svg">
              <defs>
                <!-- 暖黄色外发光 -->
                <filter id="ch2-sector-glow" x="-60%" y="-60%" width="220%" height="220%">
                  <feGaussianBlur stdDeviation="3.5" result="b1" />
                  <feMerge>
                    <feMergeNode in="b1" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <!-- 内层提亮 (径向渐变) -->
                <radialGradient id="ch2-lock-highlight" cx="50%" cy="50%" r="50%">
                  <stop offset="0%"   stop-color="rgba(255,255,255,0.45)" />
                  <stop offset="60%"  stop-color="rgba(255,245,200,0.12)" />
                  <stop offset="100%" stop-color="rgba(255,245,200,0)" />
                </radialGradient>
              </defs>

              <!-- 外圈描边 -->
              <circle cx="0" cy="0" r="92" fill="none" stroke="#B2A67D" stroke-width="0.8" opacity="0.7"/>
              <circle cx="0" cy="0" r="60" fill="none" stroke="#B2A67D" stroke-width="0.4" stroke-dasharray="2 3" opacity="0.5"/>

              <!-- 5 独立扇区（面积相等 72° 每个，顺时针排列：ph 降水 气温 积温 光照） -->
              <g v-for="(fid, i) in WHEEL_ORDER" :key="'sec-'+fid">
                <path
                  :d="sectorPath(i, 10, 88)"
                  :fill="SectorFillColor(fid)"
                  class="sector"
                  :class="SectorClass(fid, i)"
                  :style="SectorStyle(fid, i)"
                />
                <!-- 锁定高亮扇区上方叠加一层内层提亮 + 描边 -->
                <path
                  v-if="lockedFactor === fid"
                  :d="sectorPath(i, 10, 90)"
                  fill="url(#ch2-lock-highlight)"
                  stroke="#EACF78"
                  stroke-width="1.8"
                  class="sector-lock-stroke"
                  filter="url(#ch2-sector-glow)"
                  :style="LockedSectorStyle(i)"
                  pointer-events="none"
                />
              </g>

              <!-- 扇区分隔线（浅色，不阻挡视觉） -->
              <line
                v-for="i in 5"
                :key="'sep'+i"
                :x1="Math.cos((i*72 - 90) * Math.PI/180) * 10"
                :y1="Math.sin((i*72 - 90) * Math.PI/180) * 10"
                :x2="Math.cos((i*72 - 90) * Math.PI/180) * 88"
                :y2="Math.sin((i*72 - 90) * Math.PI/180) * 88"
                stroke="rgba(139,125,90,0.5)"
                stroke-width="0.6"
              />
            </svg>

            <!-- 因子文字标签：保持正向（不随旋转倒置） -->
            <div
              v-for="(fid, i) in WHEEL_ORDER"
              :key="'lbl-'+fid"
              class="factor-label"
              :style="labelStyle(i)"
              :class="{
                'lbl-scan':   scanIndex === i && spinState === 'spinning',
                'lbl-locked': lockedFactor === fid,
                'lbl-picked': pickedFactors.has(fid) && lockedFactor !== fid,
              }"
            >
              <span class="label-name">{{ FACTORS[fid].name }}</span>
              <!-- 已抽取：克制的小圆点标记 -->
              <span v-if="pickedFactors.has(fid) && lockedFactor !== fid" class="picked-dot"></span>
            </div>
          </div>

          <!-- 中心按钮 -->
          <button
            class="center-btn"
            :class="{
              'composite':  spinState === 'completed' || isComposite,
              'ready-hl':   spinState === 'completed' && !isComposite,
              'busy':       spinState === 'spinning',
            }"
            :disabled="spinState === 'spinning'"
            @click.stop="onCenterClick"
          >
            <div class="center-text">{{ centerText }}</div>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import ChapterIntro from './ChapterIntro.vue'
import {
  FACTORS, COMPOSITE, FACTOR_ORDER,
  PROV_BG_URL, PROV_STYLE,
  loadFactorBounds,
} from '../config/ch2.js'
import { getMapOptions } from '../utils/crs.js'

// ============================================================
//  因子映射
// ============================================================
// 转盘扇区顺时针顺序：酸碱度 → 降水 → 气温 → 积温 → 光照
const WHEEL_ORDER = ['ph', 'precip', 'temp', 'accum', 'rad']

// 每个扇区的基础配色（与设计色板协调：茶绿、浅金系）
const WHEEL_SECTOR_COLORS = {
  ph:     '#516D33', // 酸碱度：深橄榄绿
  precip: '#5C7C3A', // 降水：茶绿
  temp:   '#5C9EAF', // 气温：柔和青蓝（保持原等级色一致）
  accum:  '#B28F4C', // 积温：浅金色
  rad:    '#C3C19A', // 光照：米杏
}

const mapRef = ref(null)
const wheelRef = ref(null)
const introDone = ref(false)

function onIntroDone() {
  introDone.value = true
  setTimeout(() => { if (map) map.invalidateSize() }, 300)
}

// ============================================================
//  核心状态
// ============================================================
const currentFactor = ref(null)      // 地图当前展示的因子
const expandedFactor = ref(null)

// 抽取记录
const pickedFactors = ref(new Set())        // 已抽过（不重复）
const pickedFactorHistory = ref([])         // 按顺序
const allPicked = computed(() => pickedFactors.value.size >= 5)

// 转盘状态机：idle → spinning → locked → completed
// 注：综合图进入后仍算 completed
const spinState = ref('idle') // idle | spinning | locked | completed

// 动画过程变量
const scanIndex   = ref(-1)   // 当前扫描扇区（-1 = 无）
const lockedFactor = ref(null)// 最终锁定的因子
const lockedIndex  = ref(-1)  // 锁定扇区索引
const tailIndex   = ref(-1)   // 短暂尾光
const layerFading = ref(false)// 地图图层淡入过渡
let _spinTimers   = []        // 所有 setTimeout 句柄（组件卸载时清理）

// 布局模式
const showGrid = ref(false)
const displayMode = computed(() => {
  if (isComposite.value) return 'composite'
  if (pickedFactorHistory.value.length === 0) return 'empty'
  if (allPicked.value && showGrid.value) return 'grid'
  return 'single'
})
const thumbnailsShown = computed(() =>
  pickedFactorHistory.value.filter(fid => fid !== currentFactor.value)
)

const isComposite = computed(() => currentFactor.value === 'composite')
const currentConfig = computed(() => {
  if (isComposite.value) return COMPOSITE
  if (!currentFactor.value) return FACTORS[WHEEL_ORDER[0]]
  return FACTORS[currentFactor.value] || COMPOSITE
})
const expandedConfig = computed(() =>
  expandedFactor.value === 'composite'
    ? COMPOSITE
    : (FACTORS[expandedFactor.value || ''] || COMPOSITE)
)

// ============================================================
//  中心按钮文案
// ============================================================
const centerText = computed(() => {
  if (spinState.value === 'spinning')           return '抽取中'
  if (isComposite.value)                        return '重抽'
  if (spinState.value === 'completed')          return '综合分析'
  if (pickedFactorHistory.value.length === 0)   return '开始'
  return '继续抽取'
})

// ============================================================
//  Leaflet 地图初始化 & 图层切换
// ============================================================
const CHINA_ALBERS_BOUNDS = [
  [1836948, -3917344],
  [6597902,  3710529],
]

let map = null
let provLayer = null
let factorLayer = null

async function initMap() {
  if (map) return
  const opts = getMapOptions()
  map = L.map(mapRef.value, {
    ...opts,
    zoomControl: true,
    attributionControl: false,
  })

  try {
    const res = await fetch(PROV_BG_URL)
    const provData = await res.json()
    provLayer = L.geoJSON(provData, {
      style: () => ({ ...PROV_STYLE }),
      coordsToLatLng: function (coords) {
        return new L.LatLng(coords[1], coords[0], true)
      },
    }).addTo(map)
    map.fitBounds(CHINA_ALBERS_BOUNDS, { padding: [20, 20] })
  } catch (e) { console.warn('[ch2] provinces failed:', e) }

  await updateFactorLayer()
  setTimeout(() => map && map.invalidateSize(), 300)
}

// 图层切换：仅在锁定后调用；保留当前 zoom/center；300-400ms 淡入过渡
async function updateFactorLayer() {
  if (!map) return
  if (factorLayer) { map.removeLayer(factorLayer); factorLayer = null }
  if (!currentFactor.value) return

  // 淡入过渡：先遮罩一层（30ms 让遮罩出现）→ 更新图层 → 400ms 后移除遮罩
  layerFading.value = true
  await new Promise(r => setTimeout(r, 30))

  const cfg = currentConfig.value
  try {
    const bounds = await loadFactorBounds(currentFactor.value)
    factorLayer = L.imageOverlay(cfg.png, bounds, {
      opacity: 0,
      interactive: false,
      crossOrigin: true,
    }).addTo(map)

    // 逐帧 opacity 到 1（400ms）
    const t0 = performance.now()
    const dur = 400
    const step = () => {
      if (!factorLayer) return
      const p = Math.min(1, (performance.now() - t0) / dur)
      factorLayer.setOpacity(p)
      if (p < 1) requestAnimationFrame(step)
      else layerFading.value = false
    }
    requestAnimationFrame(step)
  } catch (e) {
    console.warn('[ch2] factor overlay failed:', e)
    layerFading.value = false
  }
}

// 不改变 zoom/center，只切图层（watch 自动触发）
watch(currentFactor, () => { nextTick(updateFactorLayer) })

// ============================================================
//  转盘 SVG 几何
// ============================================================
function sectorPath(index, innerR, outerR) {
  // 每个扇区 72°，第一个(index=0) 从 -90° 开始（即顶部起点）
  const startAngle = index * 72 - 90 + 1.2
  const endAngle   = startAngle + 72 - 2.4
  const toRad = d => d * Math.PI / 180
  const s1 = { x: Math.cos(toRad(startAngle)) * outerR, y: Math.sin(toRad(startAngle)) * outerR }
  const e1 = { x: Math.cos(toRad(endAngle))   * outerR, y: Math.sin(toRad(endAngle))   * outerR }
  const e2 = { x: Math.cos(toRad(endAngle))   * innerR, y: Math.sin(toRad(endAngle))   * innerR }
  const s2 = { x: Math.cos(toRad(startAngle)) * innerR, y: Math.sin(toRad(startAngle)) * innerR }
  return `M ${s1.x} ${s1.y} A ${outerR} ${outerR} 0 0 1 ${e1.x} ${e1.y} L ${e2.x} ${e2.y} A ${innerR} ${innerR} 0 0 0 ${s2.x} ${s2.y} Z`
}

function SectorFillColor(fid) {
  return WHEEL_SECTOR_COLORS[fid] || '#8BA667'
}

// 扇区中心点角度（-90°起始 + 36° = 扇区中线）
function sectorCenterAngle(index) {
  return (index * 72 - 90 + 36) * Math.PI / 180
}

function SectorClass(fid) {
  const isScan = spinState.value === 'spinning' && WHEEL_ORDER[scanIndex.value] === fid
  const isTail = spinState.value === 'spinning' && WHEEL_ORDER[tailIndex.value] === fid
  const isPicked = pickedFactors.value.has(fid)
  return {
    'sec-scan':   isScan,
    'sec-tail':   isTail,
    'sec-picked': isPicked && lockedFactor.value !== fid,
  }
}

function SectorStyle(fid, i) {
  const isLocked = lockedFactor.value === fid
  if (!isLocked) return {}
  // 锁定：沿半径方向向外突出约 8px，轻微放大 1.03x
  // 突出方向 = 沿扇区中心角平移
  const ang = sectorCenterAngle(i)
  const tx = Math.cos(ang) * 8
  const ty = Math.sin(ang) * 8
  return {
    transform: `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(1.03)`,
    transformOrigin: '0 0',
  }
}

// 锁定叠加层样式（含弹性回落动画 class 已处理）
function LockedSectorStyle(i) {
  const ang = sectorCenterAngle(i)
  const tx = Math.cos(ang) * 8
  const ty = Math.sin(ang) * 8
  return {
    transform: `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(1.03)`,
    transformOrigin: '0 0',
    animation: 'sector-lock-bounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both',
  }
}

// 标签：固定方向（永不倒置）
function labelStyle(index) {
  const ang = sectorCenterAngle(index)
  const r = 70
  const x = Math.cos(ang) * r
  const y = Math.sin(ang) * r
  const pctX = 50 + (x / 110) * 50
  const pctY = 50 + (y / 110) * 50
  return { left: `${pctX}%`, top: `${pctY}%`, transform: 'translate(-50%, -50%)' }
}

// ============================================================
//  抽取逻辑：三阶段定时序列 + 先选目标
// ============================================================
function clearSpinTimers() {
  _spinTimers.forEach(t => clearTimeout(t))
  _spinTimers = []
}
function addTimer(fn, ms) {
  const h = setTimeout(fn, ms)
  _spinTimers.push(h)
  return h
}

// 从剩余未抽中随机选 1 个；返回 targetIndex (WHEEL_ORDER 下标) 或 -1
function pickRandomTargetIndex() {
  const remain = []
  for (let i = 0; i < WHEEL_ORDER.length; i++) {
    if (!pickedFactors.value.has(WHEEL_ORDER[i])) remain.push(i)
  }
  if (remain.length === 0) return -1
  return remain[Math.floor(Math.random() * remain.length)]
}

/**
 * 三阶段定时扫描序列：
 *   阶段1 快速:   80ms/step × 14 步 ≈ 1.12s
 *   阶段2 中速:  135ms/step × 6  步 ≈ 0.81s
 *   阶段3 减速:  180,240,320,420,520 × (N 步, 直到 target)  ≈ 1.0-1.7s
 *   总时长约 3.0-3.6s
 */
function runSpinAnimation() {
  if (spinState.value === 'spinning') return
  const targetIndex = pickRandomTargetIndex()
  if (targetIndex < 0) return

  spinState.value = 'spinning'
  scanIndex.value = -1
  tailIndex.value = -1
  lockedFactor.value = null
  lockedIndex.value  = -1

  // 生成整段步进序列（先确定全部 steps → 最后一步必定等于 targetIndex）
  const steps = []

  // 阶段1：快速 ~14 步（至少完整 2 圈 = 10 步 + 余量）
  let cur = 0
  for (let i = 0; i < 14; i++) {
    steps.push({ idx: cur, delay: 80 })
    cur = (cur + 1) % 5
  }
  // 阶段2：中速 6 步
  for (let i = 0; i < 6; i++) {
    steps.push({ idx: cur, delay: 135 })
    cur = (cur + 1) % 5
  }
  // 阶段3：减速。从当前位置顺时针走到 targetIndex
  // 先计算还要多少步
  const phase3Delays = [180, 240, 320, 420, 520]
  let remainingSteps = (targetIndex - cur + 5) % 5
  // 保证至少走 3 步（通过加整圈），自然感
  if (remainingSteps < 3) remainingSteps += 5
  let p3i = 0
  for (let i = 0; i < remainingSteps; i++) {
    const d = phase3Delays[Math.min(p3i, phase3Delays.length - 1)]
    steps.push({ idx: cur, delay: d })
    cur = (cur + 1) % 5
    p3i++
  }
  // 最后补锁定（target 高亮但还保持 scan 态一会）
  // —— 上面循环中 cur 走完后 cur 其实已经 == (targetIndex+1)%5，
  //    最后一个扫描帧应该是 targetIndex。修正：steps 追加 targetIndex。
  //    为避免错误，直接把最后一步设置为 targetIndex，并确保最后位置正确。
  if (steps.length) {
    steps[steps.length - 1].idx = targetIndex
  }

  // 依次调度
  let acc = 0
  for (let s = 0; s < steps.length; s++) {
    acc += steps[s].delay
    addTimer(() => {
      if (spinState.value !== 'spinning') return
      const prev = scanIndex.value
      scanIndex.value = steps[s].idx
      // 尾光：保留上一步（低透明度）
      if (prev >= 0 && prev !== steps[s].idx) {
        tailIndex.value = prev
        addTimer(() => { if (tailIndex.value === prev) tailIndex.value = -1 }, 80)
      }
    }, acc)
  }

  // 动画结束后，锁定结果
  acc += 80
  addTimer(() => {
    const fid = WHEEL_ORDER[targetIndex]
    // 标记抽取
    pickedFactors.value.add(fid)
    if (!pickedFactorHistory.value.includes(fid)) {
      pickedFactorHistory.value.push(fid)
    }
    // 视觉锁定
    lockedIndex.value  = targetIndex
    lockedFactor.value = fid
    scanIndex.value = -1
    tailIndex.value = -1
    spinState.value = allPicked.value ? 'completed' : 'locked'

    // 锁定后再切换地图（扫描期间地图不切换）
    nextTick(() => {
      currentFactor.value = fid
      expandedFactor.value = fid
    })
  }, acc)
}

// ============================================================
//  中心按钮 & 综合分析
// ============================================================
function onCenterClick() {
  if (spinState.value === 'spinning') return

  if (isComposite.value) {
    // 重抽：重置所有状态
    resetWheel()
    return
  }

  if (spinState.value === 'completed') {
    // 已解锁 → 综合分析
    selectComposite()
    return
  }

  // 第一次 / 继续抽取
  if (!allPicked.value) {
    runSpinAnimation()
  }
}

function resetWheel() {
  clearSpinTimers()
  pickedFactors.value = new Set()
  pickedFactorHistory.value = []
  showGrid.value = false
  currentFactor.value = null
  expandedFactor.value = null
  spinState.value = 'idle'
  scanIndex.value = -1
  tailIndex.value = -1
  lockedFactor.value = null
  lockedIndex.value  = -1
  layerFading.value = false
  nextTick(updateFactorLayer)
}

function selectComposite() {
  // 切换到综合评价（现有图层：composite_suitability.png + bounds）
  currentFactor.value = 'composite'
  expandedFactor.value = 'composite'
}

// 缩略条/缩略图点击切主图（不改抽取状态、不重复触发抽取）
function openThumbAsMain(fid) {
  if (isComposite.value) {
    currentFactor.value = fid
    expandedFactor.value = fid
    return
  }
  if (!pickedFactors.value.has(fid)) return // 未抽取的不能切
  const idx = WHEEL_ORDER.indexOf(fid)
  if (idx >= 0) {
    lockedFactor.value = fid
    lockedIndex.value  = idx
  }
  currentFactor.value = fid
  expandedFactor.value = fid
  showGrid.value = false
}

function collapseCard() {
  expandedFactor.value = null
}

// ============================================================
//  生命周期
// ============================================================
onMounted(async () => {
  await nextTick()
  initMap()
})

onBeforeUnmount(() => {
  clearSpinTimers()
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
/* ============================================================
   基础布局
   ============================================================ */
.chapter-2 {
  position: relative;
  background: var(--c-paper);
}
.map-fullscreen {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.8s ease;
}
.map-fullscreen.show { opacity: 1; }
.map {
  width: 100%;
  height: 100%;
  background: var(--c-paper-2);
}

/* 地图淡入遮罩 */
.factor-fade-mask {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: var(--c-paper-2);
  opacity: 0;
  transition: opacity 0.35s ease-out;
  z-index: 10;
}
.factor-fade-mask.show { opacity: 0.55; }

/* 地图标题 */
.map-title-bar {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 500;
  background: rgba(247, 244, 235, 0.92);
  backdrop-filter: blur(8px);
  padding: 6px 22px;
  border-radius: 20px;
  border: 1px solid rgba(81, 109, 51, 0.2);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.map-title {
  font-size: 15px;
  color: var(--c-olive);
  font-weight: 400;
  letter-spacing: 2px;
  text-align: center;
}
.map-title strong { font-weight: 700; color: #3D5428; }

.map-stage { position: absolute; inset: 0; }
.map-stage.active { display: block; }
.map-fullscreen.mode-grid .map-stage { display: none; }

/* 图例 - 左侧垂直居中 */
.map-legend {
  position: absolute;
  top: 50%;
  left: 16px;
  transform: translateY(-50%);
  z-index: 500;
  background: rgba(247, 244, 235, 0.95);
  backdrop-filter: blur(8px);
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(81, 109, 51, 0.2);
  min-width: 150px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: opacity 0.3s;
}
.map-legend.hide-in-grid { opacity: 0; pointer-events: none; }
.legend-title { font-size: 13px; font-weight: 600; color: var(--c-olive); margin-bottom: 6px; letter-spacing: 1px; }
.legend-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #5a4f38; margin-bottom: 3px; }
.legend-row .sw { width: 16px; height: 12px; border-radius: 2px; border: 0.5px solid rgba(0,0,0,0.08); }

/* ============================================================
   转盘停靠区
   ============================================================ */
.wheel-dock {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 600;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

/* 因子卡片 */
.factor-card {
  background: rgba(247, 244, 235, 0.97);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(81, 109, 51, 0.25);
  border-radius: 14px;
  padding: 14px 18px;
  width: 240px;
  box-shadow: 0 8px 32px rgba(81, 109, 51, 0.2);
  cursor: pointer;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.card-title { font: 600 14px var(--serif); color: var(--c-olive); flex: 1; }
.card-close { font-size: 16px; color: var(--muted); }
.card-desc { font-size: 11px; line-height: 1.6; color: #6B5F45; margin-bottom: 8px; }
.card-legend { display: flex; flex-wrap: wrap; gap: 4px 10px; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 10px; color: #5a4f38; }
.legend-item .swatch { width: 10px; height: 10px; border-radius: 2px; border: 0.5px solid rgba(0,0,0,0.1); }
.card-expand-enter-active, .card-expand-leave-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.card-expand-enter-from, .card-expand-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

/* ============================================================
   转盘本体
   ============================================================ */
.wheel-wrap {
  position: relative;
  width: 288px;
  height: 288px;
  user-select: none;
  touch-action: none;
}
.wheel {
  position: absolute;
  inset: 0;
}
.wheel-svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}

/* ---- 扇区基础样式 ---- */
.sector {
  opacity: 0.82;
  stroke: rgba(139, 125, 90, 0.55);
  stroke-width: 0.6;
  transition: opacity 0.15s ease, filter 0.15s ease, transform 0.25s ease;
  transform-origin: 0 0;
  transform-box: fill-box;
}

/* 已抽取过的：轻微提亮、浅色细描边（克制标记） */
.sector.sec-picked {
  opacity: 0.92;
  stroke: rgba(212, 180, 76, 0.55);
  stroke-width: 0.9;
}

/* 扫描中：暖黄高亮 + 描边 + 柔和光晕 */
.sector.sec-scan {
  opacity: 1;
  filter:
    brightness(1.25)
    saturate(1.35)
    drop-shadow(0 0 5px rgba(255, 228, 140, 0.75))
    drop-shadow(0 0 9px rgba(255, 210, 120, 0.45));
  stroke: rgba(255, 230, 160, 0.95);
  stroke-width: 1.3;
}

/* 尾光：短暂、低透明度 */
.sector.sec-tail {
  opacity: 0.92;
  filter:
    brightness(1.1)
    saturate(1.15)
    drop-shadow(0 0 3px rgba(255, 228, 140, 0.38));
}

/* 锁定扇区的描边/光晕层：弹性回落动画 */
.sector-lock-stroke {
  transform-origin: 0 0;
}
@keyframes sector-lock-bounce {
  0%   { transform: translate(var(--_tx0,0px), var(--_ty0,0px)) scale(1);        opacity: 0; }
  35%  { transform: translate(var(--_tx0,0px), var(--_ty0,0px)) scale(1.09);     opacity: 1; }
  60%  { transform: translate(var(--_tx0,0px), var(--_ty0,0px)) scale(0.985);    opacity: 1; }
  100% { transform: translate(var(--_tx0,0px), var(--_ty0,0px)) scale(1.03);     opacity: 1; }
}

/* ============================================================
   因子标签（保持正向，永不倒置）
   ============================================================ */
.factor-label {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 5px;
  pointer-events: none;
  padding: 3px 7px;
  border-radius: 6px;
  transition: background 0.2s, transform 0.2s, filter 0.2s, box-shadow 0.2s;
}
.label-name {
  font-size: 12px;
  color: #FBF8EF;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(30,40,20,0.55);
  white-space: nowrap;
}
.picked-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #EACF78;
  box-shadow: 0 0 3px rgba(234, 207, 120, 0.7);
}
/* 扫描中：标签加深、提亮、白底 */
.factor-label.lbl-scan {
  background: rgba(255, 248, 225, 0.96);
  box-shadow: 0 2px 8px rgba(212, 180, 76, 0.45);
  transform: translate(-50%, -50%) scale(1.1);
}
.factor-label.lbl-scan .label-name {
  color: #5A4A15;
  text-shadow: none;
  font-weight: 700;
}
/* 锁定：标签 + 粗描边、浅金 */
.factor-label.lbl-locked {
  background: rgba(255, 252, 238, 0.98);
  box-shadow: 0 2px 10px rgba(212, 180, 76, 0.55), 0 0 0 1.5px rgba(234, 207, 120, 0.75);
  transform: translate(-50%, -50%) scale(1.15);
}
.factor-label.lbl-locked .label-name {
  color: #3E4F26;
  text-shadow: none;
  font-weight: 800;
}
/* 已抽取：轻微暖光（不抢锁定） */
.factor-label.lbl-picked {
  filter: drop-shadow(0 0 2px rgba(234, 207, 120, 0.45));
}

/* ============================================================
   中心按钮
   ============================================================ */
.center-btn {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: linear-gradient(145deg, #FBF7EA 0%, #F0EAD6 100%);
  border: 2px solid var(--c-olive);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition:
    transform 0.3s ease,
    background  0.3s ease,
    color       0.3s ease,
    border-color 0.3s ease,
    box-shadow  0.3s ease,
    opacity     0.25s ease;
  box-shadow: 0 4px 12px rgba(81, 109, 51, 0.28), 0 0 18px rgba(255, 230, 160, 0.25);
  padding: 0;
  font-family: inherit;
}
.center-btn:hover:not(:disabled) {
  background: var(--c-olive);
  transform: translate(-50%, -50%) scale(1.1);
  color: #FBF8EF;
  box-shadow: 0 4px 16px rgba(81, 109, 51, 0.45), 0 0 28px rgba(255, 230, 160, 0.6);
}
.center-btn:disabled {
  cursor: not-allowed;
  filter: grayscale(0.15);
}
.center-btn.busy {
  color: #7C6C3A;
  border-color: #D4B44C;
  box-shadow: 0 4px 12px rgba(212, 180, 76, 0.35), 0 0 26px rgba(255, 230, 160, 0.65);
}
/* 综合分析：淡入 + 缩放 + 高亮色 */
.center-btn.ready-hl {
  border-color: #B28F4C;
  background: linear-gradient(145deg, #FFF2C2 0%, #F3D97E 100%);
  color: #5A4A15;
  animation: composite-btn-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  box-shadow: 0 4px 14px rgba(178, 143, 76, 0.4), 0 0 30px rgba(255, 220, 130, 0.75);
}
.center-btn.ready-hl:hover:not(:disabled) {
  background: linear-gradient(145deg, #EFD26B 0%, #D4B44C 100%);
  color: #3A2E10;
}
.center-btn.composite {
  background: var(--c-olive);
  color: #FBF8EF;
  box-shadow: 0 4px 14px rgba(81, 109, 51, 0.45);
}
.center-btn.composite:hover:not(:disabled) {
  background: #3E4F26;
  transform: translate(-50%, -50%) scale(1.08);
}
@keyframes composite-btn-in {
  0%   { transform: translate(-50%, -50%) scale(0.86); opacity: 0; }
  60%  { transform: translate(-50%, -50%) scale(1.12); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1);    opacity: 1; }
}
.center-text {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1.5px;
  line-height: 1;
}

/* ============================================================
   缩略图条 / 网格
   ============================================================ */
.thumb-strip {
  position: absolute;
  top: 90px;
  left: 14px;
  transform: none;
  z-index: 520;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: rgba(247, 244, 235, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(81, 109, 51, 0.18);
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}
.strip-card {
  flex: 0 0 auto;
  width: 200px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  background: #fff;
  border: 1px solid rgba(81, 109, 51, 0.15);
  transition: transform 0.28s, box-shadow 0.28s, border-color 0.28s;
}
.strip-card:hover { transform: translateX(4px); box-shadow: 0 6px 16px rgba(81, 109, 51, 0.18); border-color: rgba(81, 109, 51, 0.35); }
.strip-card.active { border-color: #D4B44C; box-shadow: 0 0 0 2px rgba(212, 180, 76, 0.3), 0 6px 16px rgba(0,0,0,0.08); }
.strip-img-wrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: var(--c-paper-2);
  overflow: hidden;
}
.strip-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center 5%;
  display: block;
  transform: scale(4);
}
.strip-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: #FBF9F1;
  border-top: 1px solid rgba(81, 109, 51, 0.08);
}
.strip-meta-name { font-size: 12px; color: var(--c-olive); font-weight: 600; letter-spacing: 0.5px; }

.thumb-strip-enter-active, .thumb-strip-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.thumb-strip-enter-from, .thumb-strip-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 缩略图网格 */
.thumb-grid {
  position: absolute;
  inset: 0;
  padding: 40px 360px 40px 80px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 24px;
  z-index: 400;
  align-content: center;
  justify-content: center;
}
.thumb-cell {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
  border: 1px solid rgba(81, 109, 51, 0.2);
  box-shadow: 0 6px 24px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.thumb-cell:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(81, 109, 51, 0.18);
}
.thumb-tag {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(247, 244, 235, 0.95);
  border-bottom: 1px solid rgba(81, 109, 51, 0.12);
}
.thumb-tag-name { font-size: 12px; color: var(--c-olive); font-weight: 700; letter-spacing: 1px; }
.thumb-img-wrap {
  flex: 1;
  min-height: 0;
  background: var(--c-paper-2);
  overflow: hidden;
}
.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center 30%;
  display: block;
  transition: transform 0.4s;
  transform: scale(4);
}
.thumb-cell:hover .thumb-img { transform: scale(2.58); }

@media (max-width: 1200px) {
  .thumb-grid { padding: 30px 340px 30px 40px; gap: 18px; }
}
@media (max-width: 880px) {
  .wheel-wrap { width: 220px; height: 220px; }
  .center-btn { width: 58px; height: 58px; }
  .center-text { font-size: 10px; letter-spacing: 1px; }
  .factor-card { width: 200px; }
  .map-title-bar { top: 10px; }
  .map-title { font-size: 13px; }
  .label-name { font-size: 10px; letter-spacing: 0.5px; }
  .thumb-strip { top: 70px; left: 8px; padding: 8px; gap: 6px; max-height: calc(100vh - 240px); }
  .strip-card { width: 140px; }
  .thumb-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
    padding: 20px 20px 280px 140px;
  }
}
</style>
