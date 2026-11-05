/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        hq: {
          bg: '#070b1a',
          panel: '#0f1630',
          panel2: '#141d3d',
          line: '#1f2a4d',
          blue: '#3b82f6',
          cyan: '#3db8ff',
          purple: '#a855f7',
          orange: '#ff8a3d',
          red: '#ff4d6d',
          green: '#3ddc97',
          coral: '#f2775b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        neon: '0 0 0 1px rgba(255,138,61,.45), 0 0 24px rgba(255,138,61,.25)',
        glow: '0 0 18px rgba(34,211,238,.35)',
      },
    },
  },
  plugins: [],
};
