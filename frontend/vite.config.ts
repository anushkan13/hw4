import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The FastAPI backend runs on :8000 in development. Proxying /api and /images keeps
// the frontend on same-origin relative URLs, so it reaches the backend without
// hard-coded hosts.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/images': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
