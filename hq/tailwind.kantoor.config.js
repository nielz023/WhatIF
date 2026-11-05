import base from './tailwind.config.js';
/** Alleen de utilities die het 3D-kantoor gebruikt, zonder preflight (telefoonversie). */
export default { ...base, content: ['./src/components/office/**/*.{ts,tsx}'], corePlugins: { preflight: false } };
