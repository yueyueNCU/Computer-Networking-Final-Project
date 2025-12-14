<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 這裡放置全域樣式 (Global CSS)。
  這些設定會同時套用到客戶端和店家端。
*/
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: Arial, sans-serif;
  overflow: hidden; /* 避免最外層出現捲軸 */
}
</style>