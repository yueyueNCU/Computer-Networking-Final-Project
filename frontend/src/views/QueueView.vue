<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { QueueStatusResponse } from '@/types/RestaurantApi'
import { getQueueStatus } from '@/services/restaurant'

// 1. 模擬使用者的票號 (假設使用者手上拿的是 110 號)
const myTicketNumber = ref(110)

// 2. 排隊狀態 (改為空值或預設值，等待 API 更新)
const queueStatus = ref<QueueStatusResponse>({
  restaurant_id: 4,
  restaurant_name: '麥克小姐',
  current_number: 100, // 預設值
  total_waiting: 0,
  avg_wait_time: 0
})

// 載入狀態與時間
const isLoading = ref(false)
const lastUpdated = ref('')

// 獲取最新排隊狀態
const fetchQueueData = async () => {
  if (isLoading.value) return
  isLoading.value = true
  
  try {
    // 這裡模擬去抓 "麥克小姐" (ID: 4) 的最新狀態
    // 實際專案中，這裡的 ID 應該是從使用者的排隊紀錄 (LocalStorage/Pinia) 拿出來的
    const data = await getQueueStatus(4)
    
    // 更新資料
    queueStatus.value = data
    
    // 更新時間
    const now = new Date()
    lastUpdated.value = now.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
    
  } catch (error) {
    console.error('更新排隊狀態失敗', error)
  } finally {
    isLoading.value = false
  }
}

// 初始化時抓取一次
onMounted(() => {
  fetchQueueData()
})

// 計算前方還有幾組人
const peopleAhead = computed(() => {
  const diff = myTicketNumber.value - queueStatus.value.current_number
  return diff > 0 ? diff : 0
})

// 模擬取消排隊
const cancelQueue = () => {
  if (confirm('確定要取消排隊嗎？')) {
    alert('已取消排隊')
  }
}
</script>

<template>
  <div class="queue-container">
    <div class="refresh-controls">
      <button 
        class="reload-btn" 
        @click="fetchQueueData" 
        :disabled="isLoading"
      >
        <span v-if="isLoading">更新中...</span>
        <span v-else>更新資訊</span>
      </button>
      <div v-if="lastUpdated" class="last-updated-label">
        最後更新於: {{ lastUpdated }}
      </div>
    </div>

    <div class="header">
      <h2>排隊狀態</h2>
    </div>

    <div class="ticket-card">
      <div class="restaurant-name">{{ queueStatus.restaurant_name }}</div>
      
      <div class="ticket-info">
        <span class="label">您的號碼</span>
        <span class="number">{{ myTicketNumber }}</span>
      </div>

      <div class="status-grid">
        <div class="status-item highlight">
          <span class="label">目前叫號</span>
          <span class="value">{{ queueStatus.current_number }}</span>
        </div>

        <div class="status-item">
          <span class="label">前方還有</span>
          <span class="value">{{ peopleAhead }} 組</span>
        </div>

        <div class="status-item">
          <span class="label">現場排隊</span>
          <span class="value">{{ queueStatus.total_waiting }} 組</span>
        </div>

        <div class="status-item">
          <span class="label">預估時間</span>
          <span class="value">{{ queueStatus.avg_wait_time }} 分</span>
        </div>
      </div>

      <div class="card-footer">
        <p>請留意現場叫號，過號需重新取號</p>
      </div>
    </div>

    <button class="cancel-btn" @click="cancelQueue">取消排隊</button>
  </div>
</template>

<style scoped>
.queue-container {
  height: 100%;
  background-color: #f8f9fa;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  position: relative; /* 為了讓絕對定位的按鈕參考 */
}

/* [新增] 重整按鈕容器樣式 */
.refresh-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  z-index: 100;
}

/* 復用 HomeView 的按鈕樣式 */
.reload-btn {
  background-color: white;
  border: 1px solid #ddd;
  padding: 8px 14px; /* 稍微小一點點，因為排隊頁面比較緊湊 */
  border-radius: 50px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  cursor: pointer;
  font-size: 0.85rem;
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* ... (保留原本的 header, ticket-card, status-grid 等樣式) ... */
.header h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.ticket-card {
  background: white;
  width: 100%;
  max-width: 340px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 30px;
  border-top: 6px solid #ff9800;
}

.restaurant-name {
  font-size: 1.4rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 25px;
}

.ticket-info {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px dashed #eee;
}
.ticket-info .label {
  display: block;
  font-size: 1rem;
  color: #888;
  margin-bottom: 5px;
}
.ticket-info .number {
  font-size: 4.5rem;
  font-weight: 800;
  color: #333;
  line-height: 1;
  font-family: sans-serif;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 8px;
}

.status-item.highlight {
  background-color: #fff8e1;
  border: 1px solid #ffe0b2;
}
.status-item.highlight .value {
  color: #ff9800;
}

.status-item .label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 4px;
}

.status-item .value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
}

.card-footer p {
  font-size: 0.85rem;
  color: #aaa;
  margin: 0;
}

.cancel-btn {
  background-color: white;
  border: 2px solid #ff5252;
  color: #ff5252;
  padding: 12px 40px;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}
.cancel-btn:hover {
  background-color: #ff5252;
  color: white;
  box-shadow: 0 4px 10px rgba(255, 82, 82, 0.3);
}
</style>