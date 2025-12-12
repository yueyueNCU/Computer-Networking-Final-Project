<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { UserQueueStatusResponse } from '@/types/RestaurantApi'
import { getUserQueueStatus, leaveQueue } from '@/services/restaurant' // 改用這個 Service

// 這裡模擬當前登入的使用者 ID (實際專案可能是從 Pinia 或 Cookie 取得)
const currentUserId = 25
const router = useRouter()

// 2. 排隊狀態 (改用 UserQueueStatusResponse 格式)
const myQueueStatus = ref<UserQueueStatusResponse>({
  restaurant_id: 0,
  restaurant_name: '載入中...',
  ticket_number: 0,
  people_ahead: 0,
  estimated_wait_time: 0,
})

// 載入狀態與時間
const isLoading = ref(false)
const lastUpdated = ref('')

// 結果視窗狀態
const showResultModal = ref(false)
const resultType = ref<'success' | 'error'>('success') // 'success' | 'error'
const resultTitle = ref('')
const resultMessage = ref('')

const showConfirmCancelModal = ref(false)
// 獲取最新排隊狀態
const fetchQueueData = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    const data = await getUserQueueStatus(currentUserId)
    if (data) {
      myQueueStatus.value = data
    } else {
      // 若回傳 null 重置狀態
      myQueueStatus.value = {
        restaurant_id: 0,
        restaurant_name: '未排隊',
        ticket_number: 0,
        people_ahead: 0,
        estimated_wait_time: 0,
      }
    }
    const now = new Date()
    lastUpdated.value = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch (error) {
    console.error('更新排隊狀態失敗', error)
    
    // [修改這裡] 當發生錯誤 (例如 400 Not In Queue)，強制重置狀態為「無排隊」
    myQueueStatus.value = {
      restaurant_id: 0, // 關鍵：設為 0 會觸發 v-else 顯示空狀態
      restaurant_name: '未排隊',
      ticket_number: 0,
      people_ahead: 0,
      estimated_wait_time: 0,
    }
  } finally {
    isLoading.value = false
  }
}

// 初始化時抓取一次
onMounted(() => {
  fetchQueueData()
})

// [修改] 根據 API 資料計算 "目前叫號" (作為 UI 顯示用)
// 邏輯：如果前面有 4 人，我是 106 號，那目前大概是叫到 106 - 4 = 102 號 (或是正在服務 101)
const approxCurrentNumber = computed(() => {
  const current = myQueueStatus.value.ticket_number - myQueueStatus.value.people_ahead
  return current > 0 ? current : 0
})

// 開啟取消確認視窗
const openCancelModal = () => {
  showConfirmCancelModal.value = true
}

// 關閉取消確認視窗
const closeCancelModal = () => {
  showConfirmCancelModal.value = false
}

// 模擬取消排隊
// [修改] 執行取消排隊 (按下確認視窗的「確認」後觸發)
const handleConfirmCancel = async () => {
  // 1. 關閉確認視窗
  closeCancelModal()

  const restaurantId = myQueueStatus.value.restaurant_id
  if (!restaurantId) return

  isLoading.value = true

  try {
    // 2. 呼叫後端 API
    await leaveQueue(restaurantId, currentUserId)

    // 3. 成功
    resultType.value = 'success'
    resultTitle.value = '取消成功'
    resultMessage.value = '您已成功取消排隊。'
    showResultModal.value = true

  } catch (error: any) {
    // 4. 失敗
    resultType.value = 'error'
    resultTitle.value = '取消失敗'

    if (error.code === 'NOT_IN_QUEUE') {
      resultMessage.value = '您目前不在排隊隊伍中，無法取消。'
    } else if (error.code === 'RESTAURANT_NOT_FOUND') {
      resultMessage.value = '找不到該餐廳，無法執行取消操作。'
    } else {
      resultMessage.value = error.message || '發生未知錯誤，請稍後再試。'
    }
    
    showResultModal.value = true
  } finally {
    isLoading.value = false
  }
}
// [新增] 關閉結果視窗後的動作
const closeResultModal = () => {
  showResultModal.value = false
  
  // 如果是成功取消，導回首頁或重整狀態
  if (resultType.value === 'success') {
    // 清空狀態並導回首頁 (或停留在原頁顯示無排隊)
    myQueueStatus.value = {
        restaurant_id: 0,
        restaurant_name: '未排隊',
        ticket_number: 0,
        people_ahead: 0,
        estimated_wait_time: 0,
    }
    router.push('/')
  }
}
</script>

<template>
  <div class="queue-container">
    <div class="refresh-controls">
      <button class="reload-btn" @click="fetchQueueData" :disabled="isLoading">
        <span v-if="isLoading">更新中...</span>
        <span v-else>更新資訊</span>
      </button>
      <div v-if="lastUpdated" class="last-updated-label">最後更新於: {{ lastUpdated }}</div>
    </div>

    <div class="header">
      <h2>排隊狀態</h2>
    </div>

    <div class="ticket-card" v-if="myQueueStatus.restaurant_id">
      <div class="restaurant-name">{{ myQueueStatus.restaurant_name }}</div>

      <div class="ticket-info">
        <span class="label">您的號碼</span>
        <span class="number">{{ myQueueStatus.ticket_number }}</span>
      </div>

      <div class="status-grid">
        <div class="status-item highlight full-width">
          <span class="label">目前叫號 (預估)</span>
          <span class="value big-text">{{ approxCurrentNumber }}</span>
        </div>

        <div class="status-item">
          <span class="label">前方還有</span>
          <span class="value">{{ myQueueStatus.people_ahead }} 組</span>
        </div>

        <div class="status-item">
          <span class="label">預估時間</span>
          <span class="value">{{ myQueueStatus.estimated_wait_time }} 分</span>
        </div>
      </div>

      <div class="card-footer">
        <p>請留意現場叫號，過號需重新取號</p>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>您目前沒有正在排隊的餐廳</p>
      <router-link to="/" class="go-home-btn">前往餐廳列表</router-link>
    </div>

    <button 
      v-if="myQueueStatus.restaurant_id" 
      class="cancel-btn" 
      @click="openCancelModal"
      :disabled="isLoading"
    >
      取消排隊
    </button>

    <div v-if="showConfirmCancelModal" class="modal-overlay" @click.self="closeCancelModal">
      <div class="modal-content result-content">
        <div class="modal-header warning-header">
          <h3>取消確認</h3>
        </div>
        <div class="modal-body">
          <p class="confirm-text">您確定要取消排隊嗎？</p>
          <p class="note">取消後若要用餐需重新取號</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCancelModal">保留</button>
          <button class="btn-confirm warning-btn" @click="handleConfirmCancel">確認取消</button>
        </div>
      </div>
    </div>

    <div v-if="showResultModal" class="modal-overlay" @click.self="closeResultModal">
      <div class="modal-content result-content">
        <div class="modal-header" :class="resultType === 'success' ? 'success-header' : 'error-header'">
          <h3>{{ resultTitle }}</h3>
        </div>

        <div class="modal-body">
          <div class="icon-wrapper">
            <span v-if="resultType === 'success'">✅</span>
            <span v-else>⚠️</span>
          </div>
          <p class="result-text">{{ resultMessage }}</p>
        </div>

        <div class="modal-footer single-btn">
          <button 
            class="btn-confirm full-width" 
            :class="resultType === 'success' ? 'success-btn' : 'error-btn'"
            @click="closeResultModal"
          >
            確定
          </button>
        </div>
      </div>
    </div>

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
  position: relative;
}

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

.reload-btn {
  background-color: white;
  border: 1px solid #ddd;
  padding: 8px 14px;
  border-radius: 50px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

/* Grid Layout */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 25px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 8px;
}

/* 跨滿兩欄 */
.status-item.full-width {
  grid-column: 1 / -1;
  padding: 15px;
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

.status-item .value.big-text {
  font-size: 1.8rem;
  line-height: 1.2;
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

.empty-state {
  margin-top: 50px;
  text-align: center;
  color: #666;
}
.go-home-btn {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #ff9800;
  color: white;
  border-radius: 25px;
  text-decoration: none;
  font-weight: bold;
}

/* --- [新增] 通用結果 Modal 樣式 --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(3px);
}

.modal-content.result-content {
  background: white;
  width: 85%;
  max-width: 320px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: popIn 0.3s ease-out;
}

@keyframes popIn {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  padding: 15px;
  text-align: center;
}
.modal-header h3 {
  margin: 0;
  color: white;
  font-size: 1.2rem;
}

/* 成功綠色主題 */
.success-header { background-color: #4caf50; }
.success-btn { background-color: #4caf50; }
.success-btn:hover { background-color: #43a047; }

/* 失敗紅色主題 */
.error-header { background-color: #f44336; }
.error-btn { background-color: #f44336; }
.error-btn:hover { background-color: #d32f2f; }

.modal-body {
  padding: 20px;
  text-align: center;
}

.icon-wrapper {
  font-size: 3rem;
  margin-bottom: 15px;
}

.result-text {
  font-size: 1.1rem;
  color: #333;
  margin: 0;
  line-height: 1.5;
}

.modal-footer.single-btn {
  padding: 0;
}

.btn-confirm.full-width {
  width: 100%;
  padding: 15px;
  color: white;
  border: none;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.queue-container {
  height: 100%;
  background-color: #f8f9fa;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  position: relative;
}
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
.reload-btn {
  background-color: white;
  border: 1px solid #ddd;
  padding: 8px 14px;
  border-radius: 50px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: bold;
  color: #333;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}
.reload-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.last-updated-label {
  font-size: 0.75rem;
  color: #555;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.header h2 { color: #333; margin-bottom: 20px; font-size: 1.5rem; }
.ticket-card {
  background: white;
  width: 100%;
  max-width: 340px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 30px;
  border-top: 6px solid #ff9800;
}
.restaurant-name { font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 25px; }
.ticket-info { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px dashed #eee; }
.ticket-info .label { display: block; font-size: 1rem; color: #888; margin-bottom: 5px; }
.ticket-info .number { font-size: 4.5rem; font-weight: 800; color: #333; line-height: 1; font-family: sans-serif; }
.status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
.status-item { display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f9f9f9; padding: 12px; border-radius: 8px; }
.status-item.full-width { grid-column: 1 / -1; padding: 15px; }
.status-item.highlight { background-color: #fff8e1; border: 1px solid #ffe0b2; }
.status-item.highlight .value { color: #ff9800; }
.status-item .label { font-size: 0.85rem; color: #666; margin-bottom: 4px; }
.status-item .value { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }
.status-item .value.big-text { font-size: 1.8rem; line-height: 1.2; }
.card-footer p { font-size: 0.85rem; color: #aaa; margin: 0; }
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
.cancel-btn:hover { background-color: #ff5252; color: white; box-shadow: 0 4px 10px rgba(255, 82, 82, 0.3); }
.empty-state { margin-top: 50px; text-align: center; color: #666; }
.go-home-btn { display: inline-block; margin-top: 15px; padding: 10px 20px; background-color: #ff9800; color: white; border-radius: 25px; text-decoration: none; font-weight: bold; }

/* Modal 通用樣式 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 3000; backdrop-filter: blur(3px);
}
.modal-content {
  background: white; width: 85%; max-width: 320px;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: popIn 0.3s ease-out;
}
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.modal-header { padding: 15px; text-align: center; }
.modal-header h3 { margin: 0; color: white; font-size: 1.2rem; }
.modal-body { padding: 20px; text-align: center; }

/* 警告/確認 橘色主題 (用來做取消確認) */
.warning-header { background-color: #ff9800; }
.warning-btn { color: #ff9800; font-weight: bold; }
.warning-btn:active { background-color: #fff3e0; }

/* 成功 綠色主題 */
.success-header { background-color: #4caf50; }
.success-btn { background-color: #4caf50; }
.success-btn:hover { background-color: #43a047; }

/* 失敗 紅色主題 */
.error-header { background-color: #f44336; }
.error-btn { background-color: #f44336; }
.error-btn:hover { background-color: #d32f2f; }

/* 文字樣式 */
.confirm-text { margin: 0 0 10px; font-size: 1rem; color: #333; }
.note { font-size: 0.85rem; color: #999; margin: 0; }
.result-text { font-size: 1.1rem; color: #333; margin: 0; line-height: 1.5; }
.icon-wrapper { font-size: 3rem; margin-bottom: 15px; }

/* Footer */
.modal-footer { display: flex; border-top: 1px solid #eee; }
.modal-footer button { flex: 1; border: none; background: white; padding: 15px; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
.btn-cancel { color: #888; border-right: 1px solid #eee !important; }
.btn-cancel:active { background-color: #f5f5f5; }

.modal-footer.single-btn { padding: 0; }
.btn-confirm.full-width { width: 100%; padding: 15px; color: white; border: none; font-size: 1.1rem; font-weight: bold; cursor: pointer; }
</style>
