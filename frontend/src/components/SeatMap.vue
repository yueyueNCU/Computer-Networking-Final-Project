<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
// 引入 API
import { getSeats, updateTableStatus, getNextQueueInfo } from '@/services/restaurant'
import type { SeatDetail } from '@/types/RestaurantApi'

const route = useRoute()
const restaurantId = Number(route.params.id)
const seats = ref<SeatDetail[]>([])
// 增加一個簡單的讀取狀態，讓畫面更順暢
const isLoading = ref(true)

// 讀取座位畫面
const loadSeats = async () => {
  if (!restaurantId) return
  isLoading.value = true
  try {
    const data = await getSeats(restaurantId)
    seats.value = data
  } catch (error) {
    console.error('讀取座位失敗:', error)
  } finally {
    isLoading.value = false
  }
}

// [核心] 點擊座位的處理流程 (維持你原本的 window.confirm 邏輯)
const handleSeatClick = async (seat: SeatDetail) => {
  let ticketToSeat = 0 // 這次要帶位的號碼

  // --- 狀況 A：空桌 (empty) -> 要帶客人入座 (eating) ---
  if (seat.status === 'empty') {
    try {
      // 步驟 1：前端主動去問後端「現在下一號是誰？」
      const queueInfo = await getNextQueueInfo(restaurantId)

      // 步驟 2：判斷有沒有人排隊
      if (queueInfo && queueInfo.next_queue_to_call > 0) {
        ticketToSeat = queueInfo.next_queue_to_call

        // 步驟 3：跳出確認視窗
        const confirmSeat = window.confirm(
          `【帶位確認】\n\n下一組等待客人是： ${ticketToSeat} 號\n請確認讓客人入座 ${seat.label} 嗎？`,
        )

        if (!confirmSeat) return
      } else {
        const confirmForce = window.confirm('目前沒有排隊的客人，要直接開桌嗎？')
        if (!confirmForce) return
        ticketToSeat = 0
      }
    } catch (e) {
      alert('無法取得排隊資訊，請檢查網路')
      return
    }

    // 步驟 4：呼叫 API 更新
    await sendUpdate(seat, 'eating', ticketToSeat)
  }

  // --- 狀況 B：用餐中 (eating) -> 客人走了要清桌 (empty) ---
  else {
    const confirmClear = window.confirm(`確認 ${seat.label} 已結帳離席，要清空桌子嗎？`)
    if (!confirmClear) return

    await sendUpdate(seat, 'empty', 0)
  }
}

// 輔助函式：發送更新請求
const sendUpdate = async (seat: SeatDetail, status: 'eating' | 'empty', ticket: number) => {
  try {
    const success = await updateTableStatus(restaurantId, seat.table_id, status, ticket)

    if (success) {
      seat.status = status
    } else {
      alert('更新失敗！後端拒絕了請求')
    }
  } catch (error) {
    console.error('更新錯誤:', error)
    alert('連線錯誤')
  }
}

onMounted(() => {
  loadSeats()
})
</script>

<template>
  <div class="seat-map-container">
    <div v-if="isLoading" class="loading-state">
      <h2>資料讀取中...</h2>
    </div>

    <div v-else class="content-wrapper">
      <div class="grid-container">
        <div
          v-for="seat in seats"
          :key="seat.table_id"
          class="seat-item"
          :class="{
            'status-eating': seat.status === 'eating',
            'status-empty': seat.status === 'empty',
          }"
          :style="{ gridColumn: seat.x, gridRow: seat.y }"
          @click="handleSeatClick(seat)"
        >
          <div class="seat-icon">
            <span v-if="seat.status === 'eating'">🍽️</span>
          </div>
          <div class="seat-label">{{ seat.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 版面設定 */
.seat-map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  /* background-color: #cccccc; */ /* 移除灰色背景，讓它融入外層 */
  width: 100%;
}

/* 網格系統 CSS Grid */
.grid-container {
  display: grid;
  grid-template-columns: repeat(4, 100px); /* 4欄 */
  grid-template-rows: repeat(2, 100px); /* 2列 */
  gap: 20px; /* 間距 */
}

/* 座位卡片樣式 */
.seat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  width: 100px;
  height: 100px;
  transition: transform 0.2s;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
  border-radius: 12px; /* 圓角好看一點 */
}

.seat-item:hover {
  transform: scale(1.05); /* 滑鼠移過去放大 */
}

/* 狀態顏色 */
.status-empty {
  background-color: #bdc3c7; /* 灰色代表空桌 */
  color: #2c3e50;
}

.status-eating {
  background-color: #e74c3c; /* 紅色代表用餐 */
  color: white;
  border: 3px solid #c0392b;
}

.seat-icon {
  font-size: 2rem;
  height: 40px;
}

.seat-label {
  margin-top: 5px;
  font-weight: bold;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  width: 100%;
  color: #666;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}
</style>
