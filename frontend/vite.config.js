import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端接口地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'), // 可选：保持 /api 前缀
      },
    },
  },
})
