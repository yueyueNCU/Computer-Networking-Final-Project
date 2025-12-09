<script setup lang="ts">
import { ref, onMounted } from 'vue'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'

import type { RestaurantItem } from '@/types/RestaurantApi'
import { getRestaurants } from '@/services/restaurant'
import MapMarker from '@/components/MapMarker.vue'

// 資料狀態
const restaurants = ref<RestaurantItem[]>([])
const isLoading = ref(false)
const lastUpdated = ref('')
const cardRefs = ref<Record<number, HTMLElement>>({})

// [新增] 紀錄目前被選中(點擊)的餐廳 ID
const selectedId = ref<number | null>(null)

// 地圖設定
const zoom = ref(15)
const center = ref<[number, number]>([24.9698, 121.1915])

// 資料獲取函式
const fetchData = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    restaurants.value = await getRestaurants()
    const now = new Date()
    lastUpdated.value = now.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  } catch (error) {
    console.error('Failed to fetch restaurants:', error)
  } finally {
    isLoading.value = false
  }
}

// 處理排隊按鈕點擊
const handleJoinQueue = (restaurant: RestaurantItem) => {
  if (confirm(`確定要加入「${restaurant.restaurant_name}」的排隊隊伍嗎？`)) {
    console.log(`User wants to join queue for: ${restaurant.restaurant_id}`)
  }
}

// 捲動到指定餐廳卡片 & 設定選中狀態 (變色)
const scrollToCard = (id: number) => {
  // 更新選中的 ID，讓 MapMarker 變色
  selectedId.value = id

  const targetCard = cardRefs.value[id]
  if (targetCard) {
    targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
    targetCard.classList.add('highlight-flash')
    setTimeout(() => targetCard.classList.remove('highlight-flash'), 1500)
  }
}

// [新增] 處理地圖標記點擊 (MapMarker emit 出來的事件)
const handleMarkerClick = (id: number) => {
  scrollToCard(id)
}

onMounted(() => {
  fetchData()
})

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'green': return '🟢 目前空閒'
    case 'yellow': return '🟡 人潮普通'
    case 'red': return '🔴 客滿'
    default: return '⚪️ 未知'
  }
}
</script>

<template>
  <div class="home-container">
    <div class="map-section">
      <l-map v-model:zoom="zoom" v-model:center="center" :use-global-leaflet="false">
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          layer-type="base"
          name="OpenStreetMap"
        ></l-tile-layer>

        <MapMarker 
          v-for="r in restaurants" 
          :key="r.restaurant_id" 
          :restaurant="r"
          :is-selected="selectedId === r.restaurant_id"
          @marker-click="handleMarkerClick"
        />
      </l-map>

      <div class="map-controls">
        <button class="reload-btn" @click="fetchData" :disabled="isLoading">
          <span v-if="isLoading">更新中...</span>
          <span v-else>🔄 重整地圖</span>
        </button>
        <div v-if="lastUpdated" class="last-updated-label">
          更新於: {{ lastUpdated }}
        </div>
      </div>
    </div>

    <div class="list-section">
      <div class="list-header">
        <h2>附近餐廳</h2>
      </div>

      <div class="list-content">
        <div 
          v-for="item in restaurants" 
          :key="item.restaurant_id" 
          class="restaurant-card"
          :class="{ 'selected-card': selectedId === item.restaurant_id }"
          :ref="(el) => { if(el) cardRefs[item.restaurant_id] = el as HTMLElement }"
          @click="selectedId = item.restaurant_id"
        >
          <div class="card-img-wrapper">
            <img :src="item.image_url" class="card-img" alt="餐廳圖片" />
          </div>

          <div class="card-info">
            <div class="card-header-row">
              <h3>{{ item.restaurant_name }}</h3>
              <span class="status-badge" :class="item.status">
                {{ getStatusLabel(item.status) }}
              </span>
            </div>
            <p class="specialties">特色: {{ item.specialties }}</p>
            <p class="price">均價: {{ item.average_price }}</p>
            <button class="queue-action-btn" @click.stop="handleJoinQueue(item)">
              我要排隊 🎫
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ... (保留之前的所有樣式) ... */

/* [新增] 當卡片被選中時的樣式 (可選) */
.restaurant-card.selected-card {
  background-color: #f0f7ff; /* 淡藍色背景 */
  border-left: 4px solid #2196f3;
}

/* ... (其他樣式保持不變) ... */
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f8f9fa;
  overflow: hidden;
}
.map-section { flex: 1; position: relative; min-height: 0; z-index: 1; }
.map-controls { position: absolute; top: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.reload-btn { background-color: white; border: 1px solid #ddd; padding: 10px 16px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; font-size: 0.9rem; font-weight: bold; color: #333; transition: all 0.2s ease; display: flex; align-items: center; gap: 5px; }
.reload-btn:hover { background-color: #f0f0f0; transform: translateY(-1px); }
.reload-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.last-updated-label { font-size: 0.75rem; color: #555; background-color: rgba(255, 255, 255, 0.9); padding: 4px 8px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); backdrop-filter: blur(2px); }
.list-section { height: 45%; background-color: white; display: flex; flex-direction: column; border-top-left-radius: 24px; border-top-right-radius: 24px; box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1); z-index: 10; position: relative; }
.list-header { padding: 15px 20px 5px; text-align: center; }
.list-header h2 { font-size: 1.1rem; color: #333; margin: 0; }
.list-content { flex: 1; overflow-y: auto; padding: 10px 15px; scroll-behavior: smooth; }
.restaurant-card { display: flex; background: white; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; transition: background-color 0.3s; cursor: pointer; }
.restaurant-card:last-child { border-bottom: none; }
.restaurant-card.highlight-flash { background-color: #fff8e1; border-color: #ffb74d; }
.card-img-wrapper { width: 80px; height: 80px; border-radius: 12px; overflow: hidden; flex-shrink: 0; background-color: #eee; margin-right: 15px; }
.card-img { width: 100%; height: 100%; object-fit: cover; }
.card-info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.card-info h3 { margin: 0; font-size: 1rem; font-weight: bold; color: #2c3e50; }
.card-info .specialties { font-size: 0.85rem; color: #666; margin: 2px 0; }
.card-info .price { font-size: 0.85rem; color: #888; margin: 2px 0; }
.status-badge { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
.status-badge.green { color: #2e7d32; background: #e8f5e9; }
.status-badge.yellow { color: #f57f17; background: #fffde7; }
.status-badge.red { color: #c62828; background: #ffebee; }
.queue-action-btn { margin-top: 8px; align-self: flex-start; background-color: #ff9800; color: white; border: none; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; cursor: pointer; box-shadow: 0 2px 5px rgba(255, 152, 0, 0.3); transition: all 0.2s; }
.queue-action-btn:hover { background-color: #f57c00; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(255, 152, 0, 0.4); }
.queue-action-btn:active { transform: translateY(0); box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3); }
</style>