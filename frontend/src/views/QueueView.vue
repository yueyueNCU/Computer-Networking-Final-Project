<script setup lang="ts">
import { ref, computed } from 'vue'
// import type { QueueStatusResponse } from '@/types/RestaurantApi'

// 模擬使用者的票號 (這通常是使用者抽號碼牌後存在前端的)
const myTicketNumber = ref(110)

// 餐廳排隊狀態資料 (符合您提供的 JSON 格式)
const queueStatus = ref({
  restaurant_id: 4,
  restaurant_name: '麥克小姐', // 範例填入
  current_number: 105, // 目前叫號 (API 資料)
  total_waiting: 5, // 總排隊組數 (API 資料)
  avg_wait_time: 25, // 預估時間 (API 資料)
})

// [新增] 計算前方還有幾組人 (我的號碼 - 目前叫號)
// 邏輯：如果現在叫 105，我是 110，代表還要等 105~109 消化完 (視規則而定，這裡簡單相減)
const peopleAhead = computed(() => {
  const diff = myTicketNumber.value - queueStatus.value.current_number
  return diff > 0 ? diff : 0
})

// 模擬取消排隊
const cancelQueue = () => {
  if (confirm('確定要取消排隊嗎？')) {
    alert('已取消排隊')
    // 實際邏輯可能會清空 myTicketNumber 或跳轉回首頁
  }
}
</script>

<template>
  <div class="queue-container">
    <div class="header">
      <h2>我的排隊</h2>
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
  overflow-y: auto; /* 內容多時可捲動 */
}

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
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 30px;
  border-top: 6px solid #ff9800; /* 頂部裝飾條 */
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
  border-bottom: 1px dashed #eee; /* 虛線分隔 */
}
.ticket-info .label {
  display: block;
  font-size: 1rem;
  color: #888;
  margin-bottom: 5px;
}
.ticket-info .number {
  font-size: 4.5rem;
  font-weight: 800; /* 特粗體 */
  color: #333;
  line-height: 1;
  font-family: sans-serif; /* 確保數字樣式清楚 */
}

/* 狀態網格：2x2 排列 */
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

/* 強調目前叫號 */
.status-item.highlight {
  background-color: #fff8e1; /* 淡黃色背景 */
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
