<template>
  <section class="chapter chapter-scaffold" :id="id">
    <header class="ch-header">
      <span class="ch-no">{{ no }}</span>
      <h2 class="ch-name">{{ name }}</h2>
      <p class="ch-desc">{{ desc }}</p>
    </header>
    <div class="scaffold">
      <div class="scaffold-visual" :data-placeholder="placeholder"></div>
      <div class="scaffold-note">
        <p><b>原型设计：</b>{{ design }}</p>
        <p><b>交互：</b>{{ interact }}</p>
        <p class="muted">{{ notes }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  id:       { type: String, required: true },
  no:       { type: String, required: true },
  name:     { type: String, required: true },
  desc:     { type: String, required: true },
  placeholder: { type: String, required: true },
  design:   { type: String, required: true },
  interact: { type: String, required: true },
  notes:    { type: String, required: true }
})
</script>
