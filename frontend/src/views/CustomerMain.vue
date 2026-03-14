<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, RouterLink } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userIdInput = ref('')
const inputError = ref('')

const showUserIdOverlay = computed(() => userStore.userId == null)

function submitUserId() {
  // #region agent log
  fetch('http://127.0.0.1:7545/ingest/a962af08-672b-4568-a06a-7b03bb8b9125', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '0666a0' },
    body: JSON.stringify({
      sessionId: '0666a0',
      location: 'CustomerMain.vue:submitUserId',
      message: 'submitUserId entry',
      data: {
        valueType: typeof userIdInput.value,
        value: userIdInput.value,
        hasTrim: typeof (userIdInput.value && userIdInput.value.trim) === 'function',
      },
      timestamp: Date.now(),
      hypothesisId: 'A',
    }),
  }).catch(() => {})
  // #endregion
  inputError.value = ''
  const raw = String(userIdInput.value ?? '').trim()
  if (!raw) {
    inputError.value = '請輸入 User ID'
    return
  }
  const n = parseInt(raw, 10)
  if (Number.isNaN(n) || n < 1 || !Number.isInteger(n)) {
    inputError.value = '請輸入正整數'
    return
  }
  userStore.setUserId(n)
  userIdInput.value = ''
}

function switchUserId() {
  userStore.clearUserId()
  userIdInput.value = ''
  inputError.value = ''
}
</script>

<template>
  <div class="app-layout">
    <!-- 未設定 user_id 時顯示輸入遮罩 -->
    <div v-if="showUserIdOverlay" class="user-id-overlay">
      <div class="user-id-card">
        <h3>測試用身份</h3>
        <p class="hint">請輸入 User ID（多分頁可輸入不同 ID 測試多人邏輯）</p>
        <input
          v-model="userIdInput"
          type="number"
          min="1"
          step="1"
          placeholder="例如 1"
          class="user-id-input"
          @keydown.enter="submitUserId"
        />
        <p v-if="inputError" class="input-error">{{ inputError }}</p>
        <button type="button" class="btn-confirm-id" @click="submitUserId">確認</button>
      </div>
    </div>

    <div class="main-content">
      <RouterView />
    </div>

    <!-- 已設定時顯示目前測試 ID，可更換 -->
    <div v-if="userStore.userId != null" class="test-user-badge">
      <span>測試 User ID: {{ userStore.userId }}</span>
      <button type="button" class="btn-switch-id" @click="switchUserId">更換</button>
    </div>

    <nav class="bottom-nav">
      <RouterLink to="/" class="nav-item" exact-active-class="active">
        <span>首頁</span>
      </RouterLink>

      <RouterLink to="/queue" class="nav-item" active-class="active">
        <span>我的排隊</span>
      </RouterLink>
    </nav>
  </div>
</template>

<style>
/* 全域設定 */
body,
html,
#app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>

<style scoped>
/* App 佈局容器 */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* 內容區塊 */
.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 底部導覽列樣式 */
.bottom-nav {
  height: 60px;
  background-color: white;
  border-top: 1px solid #ddd;
  display: flex;
  justify-content: space-around;
  align-items: center;
  flex-shrink: 0;
  z-index: 2000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.nav-item {
  text-decoration: none;
  color: #888;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* [修改] 調整字體大小 */
  font-size: 1.2rem; /*原本是 0.8rem，這裡加大 */
  font-weight: 500; /* 稍微加粗一點比較好看 */

  flex: 1;
  height: 100%;
  justify-content: center; /* 確保文字垂直居中 */
  transition: all 0.2s;
}

/* 由於移除了 icon，我們可以移除 .nav-item .icon 的樣式 */

/* 當前選中的路由樣式 */
.nav-item.active {
  color: #ff9800;
  font-weight: bold;
  background-color: #fff8e1; /* (選用) 加一點淡黃色背景讓選取狀態更明顯 */
}

/* 測試用 User ID 輸入遮罩 */
.user-id-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(4px);
}
.user-id-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 320px;
  text-align: center;
}
.user-id-card h3 {
  margin: 0 0 8px;
  font-size: 1.25rem;
  color: #333;
}
.user-id-card .hint {
  font-size: 0.9rem;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.4;
}
.user-id-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 16px;
  font-size: 1.1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 8px;
}
.user-id-input:focus {
  outline: none;
  border-color: #ff9800;
}
.input-error {
  margin: 0 0 12px;
  font-size: 0.9rem;
  color: #c62828;
}
.btn-confirm-id {
  width: 100%;
  padding: 12px;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
}
.btn-confirm-id:hover {
  background: #f57c00;
}
.test-user-badge {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1500;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #666;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.btn-switch-id {
  padding: 2px 8px;
  font-size: 0.8rem;
  color: #ff9800;
  background: transparent;
  border: 1px solid #ff9800;
  border-radius: 4px;
  cursor: pointer;
}
.btn-switch-id:hover {
  background: #fff3e0;
}
</style>
