<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="app-layout">
    <div class="main-content">
      <RouterView />
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
</style>