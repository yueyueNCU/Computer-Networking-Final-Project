<script setup lang="ts">
// 引入剛剛寫好的座位圖組件
import SeatMap from './components/SeatMap.vue'
</script>

<template>
  <main>
    <SeatMap />
  </main>
</template>

<style>
/* 重置瀏覽器的預設邊距，讓畫面滿版 */
body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
}
</style>