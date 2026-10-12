import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { connectomePlugin } from './server/connectome';

export default defineConfig({
  base: process.env.FLYWORLD_BASE ?? '/',
  plugins: [react(), connectomePlugin()],
  server: { port: 5173, strictPort: false },
  build: { rollupOptions: { output: { manualChunks: {
    three: ['three'],
    renderer: ['@react-three/fiber', '@react-three/drei'],
  } } } },
  test: { include: ['tests/**/*.test.ts'], environment: 'node' },
});
