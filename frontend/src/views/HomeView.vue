<script setup lang="ts">
import { ref, onMounted } from 'vue'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'

import type { RestaurantItem } from '@/types/RestaurantApi'
import { getRestaurants } from '@/services/restaurant'
import MapMarker from '@/components/MapMarker.vue'

// 資料狀態
const restaurants = ref<RestaurantItem[]>([])

// 地圖設定
const zoom = ref(15)
const center = ref<[number, number]>([24.9698, 121.1915])

// 取得資料
onMounted(async () => {
  try {
    restaurants.value = await getRestaurants()
  } catch (error) {
    console.error('Failed to fetch restaurants:', error)
  }
})

// 將狀態代碼轉為中文
const getStatusLabel = (status: string) => {
  switch (status) {
    case 'green':
      return '🟢 目前空閒'
    case 'yellow':
      return '🟡 人潮普通'
    case 'red':
      return '🔴 客滿'
    default:
      return '⚪️ 未知'
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

        <MapMarker v-for="r in restaurants" :key="r.restaurant_id" :restaurant="r" />
      </l-map>
    </div>

    <div class="list-section">
      <div class="list-header">
        <h2>附近餐廳</h2>
      </div>

      <div class="list-content">
        <div v-for="item in restaurants" :key="item.restaurant_id" class="restaurant-card">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 1. 外框容器：使用 Flex Column 讓地圖跟列表垂直排列 */
.home-container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 佔滿整個螢幕高度 */
  background-color: #f8f9fa;
  overflow: hidden; /* 防止整個頁面捲動 */
}

/* 2. 地圖區塊 */
.map-section {
  flex: 1; /* 自動填滿剩餘空間 (大約佔 55-60%) */
  position: relative;
  min-height: 0; /* 修正 Flex 子元素高度溢出問題 */
  z-index: 1;
}

/* 3. 列表區塊 */
.list-section {
  height: 45%; /* 設定列表佔據螢幕下方 45% */
  background-color: white;
  display: flex;
  flex-direction: column;

  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1);
  z-index: 10; /* 確保蓋在地圖上面 */
  position: relative;
}

.list-header {
  padding: 15px 20px 5px;
  text-align: center;
}
.list-header h2 {
  font-size: 1.1rem;
  color: #333;
  margin: 0;
}

/* 列表內容捲動區 */
.list-content {
  flex: 1; /* 佔滿 list-section 剩下的高度 */
  overflow-y: auto; /* 內容多時可垂直捲動 */
  padding: 10px 15px;
}

/* 4. 卡片樣式 */
.restaurant-card {
  display: flex;
  background: white;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}
.restaurant-card:last-child {
  border-bottom: none;
}

/* 卡片左側圖片 */
.card-img-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #eee;
  margin-right: 15px;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 卡片右側資訊 */
.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.card-info h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: bold;
  color: #2c3e50;
}

.card-info .specialties {
  font-size: 0.85rem;
  color: #666;
  margin: 2px 0;
}

.card-info .price {
  font-size: 0.85rem;
  color: #888;
  margin: 2px 0;
}

/* 狀態標籤 */
.status-badge {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}
/* 根據狀態變色 */
.status-badge.green {
  color: #2e7d32;
  background: #e8f5e9;
}
.status-badge.yellow {
  color: #f57f17;
  background: #fffde7;
}
.status-badge.red {
  color: #c62828;
  background: #ffebee;
}
</style>
