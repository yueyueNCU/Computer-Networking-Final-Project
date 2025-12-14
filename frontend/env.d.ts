/// <reference types="vite/client" />

// 新增這一段，讓 TypeScript 認得 .vue 檔案
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}