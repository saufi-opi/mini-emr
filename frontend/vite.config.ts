import path from 'node:path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import Pages from 'vite-plugin-pages'
import Layouts from 'vite-plugin-vue-layouts-next'

export default defineConfig({ 
  plugins: [vue(), tailwindcss(), Pages(), Layouts()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
