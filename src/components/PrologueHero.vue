<template>
  <section class="chapter hero" :id="id">
    <div class="hero-bg"></div>
    <div class="hero-inner">
      <p class="hero-kicker">中国茶文化空间</p>
      <h1 class="hero-title">茶<span>之</span>中国</h1>
      <p class="hero-sub">从一叶古茶树，到一片山水的呼应，<br/>再到万里茶路的流转——以地理之眼，重读中国茶。</p>
      <div class="hero-meta">
        <span>茶叶生产 · 贸易 · 发展</span>
        <span class="sep">·</span>
        <span>地理分析与可视化</span>
      </div>
      <div class="scroll-hint">
        <span>向下滚动 开启图志</span>
        <i class="arrow"></i>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({ id: { type: String, required: true } })
</script>
