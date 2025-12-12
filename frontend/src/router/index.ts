import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import QueueView from '../views/QueueView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 主畫面
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // 排隊頁面
    {
      path: '/queue',
      name: 'queue',
      component: QueueView,
    },
  ],
})

export default router
