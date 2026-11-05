import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Bouwt alleen het 3D-kantoor als module voor de telefoonversie (hq/mobiel/assets/kantoor).
export default defineConfig({
  base: './',
  plugins: [react()],
  publicDir: false,
  define: { 'process.env.NODE_ENV': '"production"' },
  build: {
    outDir: 'mobiel/assets/kantoor',
    emptyOutDir: true,
    lib: { entry: 'src/kantoor-mobiel.tsx', formats: ['es'], fileName: () => 'kantoor.js' },
    cssCodeSplit: false,
    rollupOptions: { output: { chunkFileNames: '[name]-[hash].js', assetFileNames: 'kantoor[extname]' } },
  },
});
