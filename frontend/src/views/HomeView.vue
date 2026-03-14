<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'

import type { RestaurantItem, QueueStatusResponse, JoinQueueResponse } from '@/types/RestaurantApi'
import { getRestaurants, getQueueStatus, joinQueue } from '@/services/restaurant'
import MapMarker from '@/components/MapMarker.vue'
import { useUserStore } from '@/stores/user'

// 資料狀態
const restaurants = ref<RestaurantItem[]>([])
const isLoading = ref(false)
const lastUpdated = ref('')
const cardRefs = ref<Record<number, HTMLElement>>({})
const router = useRouter()
const userStore = useUserStore()

const API_ORIGIN = 'http://localhost:8000'
function restaurantImageSrc(url: string | undefined) {
  if (!url) return ''
  return url.startsWith('http') ? url : `${API_ORIGIN}${url}`
}

// 紀錄目前被選中的餐廳 ID (拿來變色用)
const selectedId = ref<number | null>(null)

// 地圖設定
const zoom = ref(15)
const center = ref<[number, number]>([24.9698, 121.1915]) // 中央大學座標

// Modal 控制狀態 (用來等下顯示排隊確認視窗)
const showModal = ref(false)
// 暫存要排隊的餐廳資訊 (用於顯示在 Modal 中)
const pendingQueueInfo = ref<{
  restaurant: RestaurantItem
  status: QueueStatusResponse
} | null>(null)

// 排隊成功 Modal
const showSuccessModal = ref(false)
const successQueueInfo = ref<JoinQueueResponse | null>(null)

// 排隊失敗 Modal
const showErrorModal = ref(false)
const errorMessage = ref('')

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
      second: '2-digit',
    })
  } catch (error) {
    console.error('Failed to fetch restaurants:', error)
  } finally {
    isLoading.value = false
  }
}

// [修改] 點擊排隊按鈕 -> 取得資料 -> 開啟 Modal
const handleJoinQueue = async (restaurant: RestaurantItem) => {
  try {
    document.body.style.cursor = 'wait'

    // 取得排隊狀態
    const status = await getQueueStatus(restaurant.restaurant_id)

    document.body.style.cursor = 'default'

    // 設定暫存資訊並開啟 Modal
    pendingQueueInfo.value = {
      restaurant: restaurant,
      status: status,
    }
    showModal.value = true
  } catch (error) {
    document.body.style.cursor = 'default'
    console.error('Failed to fetch queue status:', error)
    alert('無法取得排隊資訊')
  }
}

// Modal 確認按鈕邏輯
const confirmQueue = async () => {
  if (pendingQueueInfo.value) {
    const { restaurant } = pendingQueueInfo.value
    const userId = userStore.userId
    if (userId == null) {
      alert('請先設定測試用 User ID')
      return
    }

    try {
      document.body.style.cursor = 'wait'

      // 呼叫 API
      const response = await joinQueue(restaurant.restaurant_id, userId)

      // 成功邏輯
      successQueueInfo.value = response
      closeModal()
      showSuccessModal.value = true
    } catch (error: any) {
      console.error('排隊失敗:', error)

      // 錯誤處理邏輯
      // 設定錯誤訊息 (直接顯示後端回傳的 message，或進行簡易翻譯)
      let msg = error.message
      if (msg === 'You are already in the queue.') {
        msg = '您已經在其他隊伍中排隊了！'
      } else if (msg === 'Restaurant does not exist.') {
        msg = '該餐廳不存在或是已下架。'
      }

      errorMessage.value = msg

      // 關閉確認視窗，開啟錯誤視窗
      closeModal()
      showErrorModal.value = true
    } finally {
      document.body.style.cursor = 'default'
    }
  }
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}

// 關閉成功視窗並前往排隊頁面
const handleSuccessConfirm = () => {
  showSuccessModal.value = false
  successQueueInfo.value = null
  router.push('/queue')
}

// 關閉 Modal
const closeModal = () => {
  showModal.value = false
  pendingQueueInfo.value = null
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
          <span v-else> 更新餐廳狀態</span>
        </button>
        <div v-if="lastUpdated" class="last-updated-label">最後更新於: {{ lastUpdated }}</div>
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
          :ref="
            (el) => {
              if (el) cardRefs[item.restaurant_id] = el as HTMLElement
            }
          "
          @click="selectedId = item.restaurant_id"
        >
          <div class="card-img-wrapper">
            <img :src="restaurantImageSrc(item.image_url)" class="card-img" alt="餐廳圖片" />
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
            <button class="queue-action-btn" @click.stop="handleJoinQueue(item)">我要排隊 !</button>
          </div>
        </div>
      </div>

      <div v-if="showModal && pendingQueueInfo" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>排隊確認</h3>
          </div>

          <div class="modal-body">
            <p class="confirm-text">
              您想要排隊 <strong>{{ pendingQueueInfo.restaurant.restaurant_name }}</strong> 嗎？
            </p>

            <div class="info-box">
              <div class="info-row">
                <span class="label">目前等待</span>
                <span class="value">{{ pendingQueueInfo.status.total_waiting }} 組</span>
              </div>
              <div class="info-row">
                <span class="label">預計時間</span>
                <span class="value highlight"
                  >{{ pendingQueueInfo.status.avg_wait_time }} 分鐘</span
                >
              </div>
            </div>

            <p class="note">過號需重新取號，請留意現場叫號</p>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="closeModal">取消</button>
            <button class="btn-confirm" @click="confirmQueue">確認排隊</button>
          </div>
        </div>
      </div>

      <div v-if="showSuccessModal && successQueueInfo" class="modal-overlay success-overlay">
        <div class="modal-content success-content">
          <div class="modal-header success-header">
            <h3>🎉 取號成功！</h3>
          </div>

          <div class="modal-body">
            <div class="ticket-display">
              <span class="ticket-label">您的號碼</span>
              <span class="ticket-number">{{ successQueueInfo.ticket_number }}</span>
            </div>

            <div class="info-box">
              <div class="info-row">
                <span class="label">前方等待</span>
                <span class="value">{{ successQueueInfo.people_ahead }} 組</span>
              </div>
              <div class="info-row">
                <span class="label">預估時間</span>
                <span class="value highlight">{{ successQueueInfo.estimated_wait_time }} 分鐘</span>
              </div>
            </div>

            <p class="note">請前往「我的排隊」頁面隨時關注叫號進度</p>
          </div>

          <div class="modal-footer single-btn">
            <button class="btn-confirm full-width" @click="handleSuccessConfirm">前往查看</button>
          </div>
        </div>
      </div>

      <div v-if="showErrorModal" class="modal-overlay error-overlay" @click.self="closeErrorModal">
        <div class="modal-content error-content">
          <div class="modal-header error-header">
            <h3>排隊失敗</h3>
          </div>

          <div class="modal-body">
            <div class="error-icon-wrapper">⚠️</div>
            <p class="error-text">{{ errorMessage }}</p>
          </div>

          <div class="modal-footer single-btn">
            <button class="btn-confirm full-width error-btn" @click="closeErrorModal">關閉</button>
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
  background-color: #fff8e1; /* 淡藍色背景 */
  border-left: 4px solid #ffb74d;
}

/* ... (其他樣式保持不變) ... */
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f8f9fa;
  overflow: hidden;
}
.map-section {
  flex: 1;
  position: relative;
  min-height: 0;
  z-index: 1;
}
.map-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.reload-btn {
  background-color: white;
  border: 1px solid #ddd;
  padding: 10px 16px;
  border-radius: 50px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  color: #333;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}
.reload-btn:hover {
  background-color: #f0f0f0;
  transform: translateY(-1px);
}
.reload-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.last-updated-label {
  font-size: 0.75rem;
  color: #555;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(2px);
}
.list-section {
  height: 45%;
  background-color: white;
  display: flex;
  flex-direction: column;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1);
  z-index: 10;
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
.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px 15px;
  scroll-behavior: smooth;
}
.restaurant-card {
  display: flex;
  background: white;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
  cursor: pointer;
}
.restaurant-card:last-child {
  border-bottom: none;
}
.card-img-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #eee;
  margin-right: 15px;
  margin-top: 15px;
  margin-left: 10px;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
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
.status-badge {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}
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
.queue-action-btn {
  margin-top: 8px;
  align-self: flex-start;
  background-color: #ff9800;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(255, 152, 0, 0.3);
  transition: all 0.2s;
}
.queue-action-btn:hover {
  background-color: #f57c00;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(255, 152, 0, 0.4);
}
.queue-action-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000; /* 確保比地圖和導覽列都高 */
  backdrop-filter: blur(3px); /* 背景模糊效果 */
}

/* Modal 本體 */
.modal-content {
  background: white;
  width: 85%;
  max-width: 320px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: popIn 0.3s ease-out;
}

/* 彈出動畫 */
@keyframes popIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-header {
  background-color: #ff9800;
  padding: 15px;
  text-align: center;
}
.modal-header h3 {
  margin: 0;
  color: white;
  font-size: 1.1rem;
}

.modal-body {
  padding: 20px;
  text-align: center;
}

.confirm-text {
  margin: 0 0 15px;
  font-size: 1rem;
  color: #333;
}
.confirm-text strong {
  color: #e65100;
}

/* 資訊框框 */
.info-box {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  color: #666;
  font-size: 0.9rem;
}
.info-row .value {
  font-weight: bold;
  color: #333;
}
.info-row .value.highlight {
  color: #ff9800;
}

.note {
  font-size: 0.8rem;
  color: #999;
  margin: 0;
}

.modal-footer {
  display: flex;
  border-top: 1px solid #eee;
}

.modal-footer button {
  flex: 1;
  border: none;
  background: white;
  padding: 15px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel {
  color: #888;
  border-right: 1px solid #eee !important;
}
.btn-cancel:active {
  background-color: #f5f5f5;
}

.btn-confirm {
  color: #ff9800;
  font-weight: bold;
}
.btn-confirm:active {
  background-color: #fff3e0;
}

.success-header {
  background-color: #4caf50; /* 綠色代表成功 */
  padding: 20px 15px;
}

/* 號碼牌大字顯示 */
.ticket-display {
  margin: 10px 0 25px;
  padding: 15px;
  border: 2px dashed #ddd;
  border-radius: 12px;
  background-color: #fafafa;
}

.ticket-label {
  display: block;
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 5px;
}

.ticket-number {
  display: block;
  font-size: 3.5rem;
  font-weight: 800;
  color: #333;
  line-height: 1;
}

/* 按鈕樣式調整 */
.modal-footer.single-btn {
  padding: 0;
}

.btn-confirm.full-width {
  width: 100%;
  padding: 18px;
  background-color: #4caf50;
  color: white;
  font-size: 1.1rem;
}
.btn-confirm.full-width:hover {
  background-color: #43a047;
}

.error-header {
  background-color: #f44336; /* 紅色代表錯誤 */
  padding: 20px 15px;
  text-align: center;
}
.error-header h3 {
  margin: 0;
  color: white;
  font-size: 1.2rem;
}

/* 錯誤內容區 */
.error-icon-wrapper {
  font-size: 3rem;
  text-align: center;
  margin-top: 15px;
}

.error-text {
  font-size: 1.1rem;
  color: #333;
  margin: 15px 0 25px;
  text-align: center;
  font-weight: 500;
  line-height: 1.5;
}

/* 按鈕樣式 (複用 btn-confirm 但改顏色) */
.btn-confirm.full-width.error-btn {
  background-color: #f44336;
}
.btn-confirm.full-width.error-btn:hover {
  background-color: #d32f2f;
}
.btn-confirm.full-width.error-btn:active {
  background-color: #c62828;
}
</style>
