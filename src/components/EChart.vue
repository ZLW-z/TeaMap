<template>
  <div ref="el" class="echart-container" :style="{ width: '100%', height: '100%' }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
})

const emit = defineEmits(['ready', 'click'])

const el = ref(null)
let chart = null
let ro = null

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value, undefined, { renderer: 'canvas' })
  chart.setOption(props.option, { notMerge: true })
  emit('ready', chart)

  chart.on('click', (params) => emit('click', params))

  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
})

watch(() => props.option, (newOption) => {
  if (chart) chart.setOption(newOption, { notMerge: true })
}, { deep: true })

onBeforeUnmount(() => {
  if (ro) { ro.disconnect(); ro = null }
  if (chart) { chart.dispose(); chart = null }
})
</script>

<style scoped>
.echart-container {
  min-height: 200px;
}
</style>
