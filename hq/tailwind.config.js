/** @type {import('tailwindcss').Config} */
// Driftmark-huisstijl (verbeterlijst punt 26-28): één vaste letterschaal, nachtblauw met blauwe gloed, warm oranje accent.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        hq: {
          bg: '#060a1c',
          panel: '#0e1631',
          panel2: '#131d3f',
          line: '#1f2b52',
          blue: '#398CFF',
          cyan: '#3db8ff',
          purple: '#a855f7',
          orange: '#ff8a3d',
          accent: '#FF7A24',
          red: '#ff4d6d',
          green: '#3ddc97',
          coral: '#f2775b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Inter Tight"', 'Inter', 'system-ui', 'sans-serif'],
      },
      // vaste letterschaal: 12 · 13 · 14 · 15 · 17 · 20 · 24 · 30 · 36
      fontSize: {
        xs: ['12px', { lineHeight: '16px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['15px', { lineHeight: '23px' }],
        lg: ['17px', { lineHeight: '25px' }],
        xl: ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '30px', letterSpacing: '-0.01em' }],
        '3xl': ['30px', { lineHeight: '36px', letterSpacing: '-0.015em' }],
        '4xl': ['36px', { lineHeight: '42px', letterSpacing: '-0.02em' }],
      },
      boxShadow: {
        neon: '0 0 0 1px rgba(255,122,36,.45), 0 0 24px rgba(255,122,36,.25)',
        glow: '0 0 18px rgba(57,140,255,.35)',
        glans: 'inset 0 1px 0 rgba(255,255,255,.07), 0 12px 32px rgba(0,0,0,.35)',
      },
      transitionTimingFunction: { dm: 'cubic-bezier(0.22, 1, 0.36, 1)' },
    },
  },
  plugins: [],
};
