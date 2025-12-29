import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/docs': {
        target: 'http://localhost:5106/swagger',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/docs/, ''),
      },
      '/swagger': {
        target: 'http://localhost:5106',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:5106',
        changeOrigin: true,
      }
    }
  },
})
