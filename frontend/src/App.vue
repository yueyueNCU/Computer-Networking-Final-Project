<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 全域樣式設定：移除預設邊距，讓地圖滿版 */
body,
html,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}
</style>
