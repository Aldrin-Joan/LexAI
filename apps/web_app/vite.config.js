import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/legal': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/core-api': {
        target: 'https://core-api-584212158273.asia-south1.run.app',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/core-api/, ''),
      },
    },
  },
})
