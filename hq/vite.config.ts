import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Sneller openen (verbeterlijst punt 68): grote bibliotheken in eigen bestanden, zodat de browser ze
 * tegelijk ophaalt en na een nieuwe versie uit de cache haalt. three.js en de 3D-bibliotheken zitten
 * alleen in het kantoor-deel; dat laadt pas als het 3D-kantoor opengaat (world/WorldLayer.tsx).
 */
const GROEPEN: [RegExp, string][] = [
  [/node_modules\/(three|three-stdlib|postprocessing|@react-three|@monogrid|fflate|troika-[^/]+|meshline|camera-controls|maath|detect-gpu|three-mesh-bvh|stats-gl|suspend-react|its-fine|react-use-measure)\//, '3d'],
  [/node_modules\/(react|react-dom|scheduler|zustand|immer|use-sync-external-store)\//, 'react'],
  [/node_modules\/(framer-motion|motion-dom|motion-utils)\//, 'beweging'],
  [/node_modules\/lucide-react\//, 'iconen'],
  [/node_modules\/(recharts|d3-[^/]+|victory-vendor|recharts-scale|react-smooth|decimal\.js-light|internmap|eventemitter3)\//, 'grafieken'],
];

export default defineConfig({
  base: './',
  plugins: [react()],
  server: { port: 5173 },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks(id) {
          // vite-hulpje voor dynamische imports hoort bij de basis, anders belandt het in de 3d-chunk
          if (id.includes('vite/preload-helper') || id.includes('commonjsHelpers')) return 'react';
          for (const [re, naam] of GROEPEN) if (re.test(id)) return naam;
          return undefined;
        },
      },
    },
  },
});
