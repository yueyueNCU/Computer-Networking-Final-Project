<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { RouterView, useRoute } from 'vue-router';
// 引入我們寫好的 API，用來查餐廳名字
import { getRestaurants } from '@/services/restaurant';

const route = useRoute();
// 1. 抓取網址上的 ID (例如 /restaurant/1/table -> 拿到 1)
const restaurantId = Number(route.params.id);
const restaurantName = ref("載入中...");

// 2. 定義讀取餐廳名稱的函式
const loadRestaurantInfo = async () => {
  try {
    // 取得所有餐廳列表
    const allRestaurants = await getRestaurants();
    
    // 比對 ID，找出是哪一家
    const target = allRestaurants.find(r => r.restaurant_id === restaurantId);
    
    if (target) {
      restaurantName.value = target.restaurant_name;
    } else {
      restaurantName.value = "未知餐廳";
    }
  } catch (e) {
    console.error("無法讀取餐廳資訊", e);
    restaurantName.value = "店家後台";
  }
};

onMounted(() => {
  loadRestaurantInfo();
});
</script>

<template>
  <div class="restaurant-layout">
    <header class="admin-header">
      <h1>{{ restaurantName }}座位管理系統 (餐廳 ID: {{ restaurantId }})</h1>
    </header>

    <main class="admin-content">
      <RouterView :key="$route.fullPath" />
    </main>
  </div>
</template>

<style scoped>
.restaurant-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.admin-header {
  background-color: #333; /* 深色背景 */
  color: white;           /* 白色文字 */
  padding: 1rem;
  text-align: center;
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}
</style>