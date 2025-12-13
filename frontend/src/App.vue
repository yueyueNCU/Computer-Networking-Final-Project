<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
const route = useRoute();
</script>

<template>
  <main>
    <RouterView :key="$route.fullPath" />
  </main>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
}
</style>