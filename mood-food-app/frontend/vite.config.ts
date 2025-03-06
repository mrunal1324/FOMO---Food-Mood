import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Provide polyfills for Node.js built-ins
      crypto: resolve('node_modules/crypto-browserify'),
      stream: resolve('node_modules/stream-browserify'),
      assert: resolve('node_modules/assert'),
      util: resolve('node_modules/util'),
      buffer: resolve('node_modules/buffer'),
    }
  },
  define: {
    // Ensure process.env is available
    'process.env': {},
    // Polyfill for global
    global: 'globalThis',
  },
  optimizeDeps: {
    esbuildOptions: {
      // Node.js global to browser globalThis
      define: {
        global: 'globalThis'
      }
    }
  },
  // Ensure proper handling of Node.js built-ins
  build: {
    rollupOptions: {
      external: ['fsevents']
    }
  }
})