import { createRouter, createWebHistory } from 'vue-router'

// 1. 引入 Layout (容器)
import CustomerMain from '../views/CustomerMain.vue'
import RestaurantMain from '../views/RestaurantMain.vue'

// 2. 引入頁面組件
import HomeView from '../views/HomeView.vue'
import QueueView from '../views/QueueView.vue'
import SeatMap from '../components/SeatMap.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ====================================================
    // 區域 A: 客戶端 (使用 CustomerMain 作為佈局，包含底部導覽列)
    // ====================================================
    {
      path: '/',
      component: CustomerMain,
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
    // 區域 B: 店家端 (使用 RestaurantMain 作為佈局)
    // ====================================================
    {
      path: '/restaurant',
      component: RestaurantMain,
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