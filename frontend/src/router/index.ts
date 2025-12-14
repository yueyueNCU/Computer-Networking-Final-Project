// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

// 1. 引入 Layout (容器)
// 確保這兩個檔案已經建立在 src/views/ 下
import CustomerMain from '../views/CustomerMain.vue'
import RestaurantMain from '../views/RestaurantMain.vue'

// 2. 引入頁面組件
// 這些是你原本或主線已經有的頁面
import HomeView from '../views/HomeView.vue'
import QueueView from '../views/QueueView.vue'
import SeatMap from '../components/SeatMap.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ====================================================
    // 區域 A: 客戶端 (有底部導覽列)
    // ====================================================
    {
      path: '/',
      component: CustomerMain, // 使用帶有導覽列的 Layout
      children: [
        {
          path: '', // 網址: /
          name: 'home',
          component: HomeView,
        },
        {
          path: 'queue', // 網址: /queue
          name: 'queue',
          component: QueueView,
        },
      ],
    },

    // ====================================================
    // 區域 B: 店家端 (無導覽列，只有內容)
    // ====================================================
    {
      path: '/restaurant',
      component: RestaurantMain, // 使用你原本乾淨的 Layout
      children: [
        {
          // 網址: /restaurant/:id/table
          // 例如: /restaurant/1/table
          path: ':id/table', 
          name: 'seat-map',
          component: SeatMap
        }
      ]
    }
  ],
})

export default router