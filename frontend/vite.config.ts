import react from '@vitejs/plugin-react-swc'
import path from 'path'
import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

export default defineConfig({
  base: '/',
  root: 'frontend',
  plugins: [react(), viteSingleFile()],
  resolve: {
    alias: {
      '@frontend/apis': path.resolve(__dirname, './src/apis'),
      '@frontend/contexts': path.resolve(__dirname, './src/contexts'),
      '@frontend/elements': path.resolve(__dirname, './src/components/elements'),
      '@frontend/hooks': path.resolve(__dirname, './src/hooks'),
      '@frontend/layouts': path.resolve(__dirname, './src/components/layouts'),
      '@frontend/pages': path.resolve(__dirname, './src/components/pages'),
      '@frontend/schemas': path.resolve(__dirname, './src/schemas'),
      '@frontend/utils': path.resolve(__dirname, './src/utils'),
    },
  },
})
