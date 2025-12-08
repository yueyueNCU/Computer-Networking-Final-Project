<!-- 地圖 -->
<script setup lang="ts">
import { computed } from 'vue'
import { LMarker, LPopup } from '@vue-leaflet/vue-leaflet'
import type { RestaurantItem } from '@/types/RestaurantApi'

// 定義 Props：此元件必須接收一個 restaurant 物件
const props = defineProps<{
  restaurant: RestaurantItem
}>()

// 根據餐廳狀態 (status) 決定圖釘顏色或圖示 (這裡先用簡單的範例)
// TS 會知道 props.restaurant 裡面一定有 status 欄位
const statusText = computed(() => {
  switch (props.restaurant.status) {
    case 'green':
      return '🟢 目前空閒'
    case 'yellow':
      return '🟡 人潮普通'
    case 'red':
      return '🔴 客滿'
    default:
      return '未知'
  }
})
</script>

<template>
  <l-marker :lat-lng="[props.restaurant.lat, props.restaurant.lng]">
    <l-popup>
      <div class="popup-content">
        <h3>{{ props.restaurant.restaurant_name }}</h3>
        <img :src="props.restaurant.image_url" alt="餐廳照片" class="preview-img" />
        <p><strong>特色：</strong>{{ props.restaurant.specialties }}</p>
        <p><strong>均價：</strong>{{ props.restaurant.average_price }}</p>
        <p><strong>狀態：</strong>{{ statusText }}</p>
      </div>
    </l-popup>
  </l-marker>
</template>

<style scoped>
.preview-img {
  width: 100%;
  max-height: 100px;
  object-fit: cover;
  border-radius: 4px;
  margin: 5px 0;
}
.popup-content h3 {
  margin: 0 0 5px 0;
  font-size: 1.1em;
}
.popup-content p {
  margin: 3px 0;
  font-size: 0.9em;
}
</style>
