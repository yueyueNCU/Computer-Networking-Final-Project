import { createRouter, createWebHistory } from 'vue-router'
// 引入座位圖組件
import SeatMap from '../components/SeatMap.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 當使用者訪問根目錄 (http://localhost:5173/) 時
      path: '/',
      name: 'home',
      // 直接導向到第一家餐廳的座位圖 (方便測試)
      redirect: '/restaurant/1/table'
    },
    {
      // 這是你剛剛設定的動態路由
      path: '/restaurant/:id/table', 
      name: 'seat-map',
      component: SeatMap
    }
  ]
})

export default router