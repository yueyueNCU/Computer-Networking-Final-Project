import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'test_user_id'

function readFromStorage(): number | null {
  if (typeof sessionStorage === 'undefined') return null
  const raw = sessionStorage.getItem(STORAGE_KEY)
  if (raw == null || raw === '') return null
  const n = parseInt(raw, 10)
  return Number.isNaN(n) || n < 1 ? null : n
}

export const useUserStore = defineStore('user', () => {
  const userId = ref<number | null>(readFromStorage())

  const hasUserId = computed(() => userId.value != null)

  function setUserId(id: number) {
    userId.value = id
    try {
      sessionStorage.setItem(STORAGE_KEY, String(id))
    } catch {
      // ignore
    }
  }

  function clearUserId() {
    userId.value = null
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  return { userId: computed(() => userId.value), hasUserId, setUserId, clearUserId }
})
