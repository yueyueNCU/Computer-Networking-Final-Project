<script setup lang="ts">
import { computed } from 'vue'
import { LMarker, LPopup, LIcon } from '@vue-leaflet/vue-leaflet'
import type { RestaurantItem } from '@/types/RestaurantApi'

// 接收 Props
const props = defineProps<{
  restaurant: RestaurantItem
  isSelected?: boolean // [新增] 是否被選中
}>()

// 定義事件 (通知父層被點擊了)
const emit = defineEmits(['marker-click'])

// [新增] 圖標 URL 設定
// 使用 GitHub 上穩定的 leaflet-color-markers 資源
const blueIconUrl =
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png'
const redIconUrl =
  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'
const shadowUrl = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png'

// 根據 props 決定顯示哪種顏色的圖標
const currentIconUrl = computed(() => (props.isSelected ? redIconUrl : blueIconUrl))

// 狀態文字轉換
const getStatusText = (status: string) => {
  switch (status) {
    case 'green':
      return '空閒'
    case 'yellow':
      return '普通'
    case 'red':
      return '客滿'
    default:
      return '未知'
  }
}

// 點擊處理
const handleClick = () => {
  emit('marker-click', props.restaurant.restaurant_id)
}
</script>

<template>
  <l-marker :lat-lng="[restaurant.lat, restaurant.lng]" @click="handleClick">
    <l-icon
      :icon-url="currentIconUrl"
      :icon-size="[25, 41]"
      :icon-anchor="[12, 41]"
      :popup-anchor="[1, -34]"
      :shadow-url="shadowUrl"
      :shadow-size="[41, 41]"
    />

    <l-popup>
      <div class="simple-popup">
        <h3 class="popup-title">{{ restaurant.restaurant_name }}</h3>
        <div class="popup-status" :class="restaurant.status">
          {{ getStatusText(restaurant.status) }}
        </div>
      </div>
    </l-popup>
  </l-marker>
</template>

<style scoped>
/* 簡化版 Popup 樣式 */
.simple-popup {
  text-align: center;
  min-width: 100px;
}

.popup-title {
  margin: 0 0 5px 0;
  font-size: 1rem;
  font-weight: bold;
  color: #333;
}

.popup-status {
  font-size: 0.9rem;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

/* 狀態顏色 */
.popup-status.green {
  color: #2e7d32;
  background: #e8f5e9;
}
.popup-status.yellow {
  color: #f57f17;
  background: #fffde7;
}
.popup-status.red {
  color: #c62828;
  background: #ffebee;
}
</style>
