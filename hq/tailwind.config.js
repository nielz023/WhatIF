/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        hq: {
          bg: '#070b1a',
          panel: '#0d1430',
          panel2: '#121b3d',
          line: '#22305e',
          blue: '#3b82f6',
          cyan: '#22d3ee',
          purple: '#a855f7',
          orange: '#fb923c',
          red: '#f43f5e',
          green: '#22c55e',
          coral: '#f2775b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        neon: '0 0 0 1px rgba(99,102,241,.35), 0 0 24px rgba(99,102,241,.25)',
        glow: '0 0 18px rgba(34,211,238,.35)',
      },
    },
  },
  plugins: [],
};
