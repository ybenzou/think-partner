import { createApp } from 'vue'
import App from './App.vue'
import './assets/tailwind.css'
import '@vue-flow/core/dist/style.css'                   // 核心样式
import '@vue-flow/core/dist/theme-default.css'           // 默认主题（可选）

createApp(App).mount('#app')
