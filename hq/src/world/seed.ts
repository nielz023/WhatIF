/** Kleine, stabiele hash (0..1) van een tekst. Los bestand, zodat het hoofdscherm geen three.js hoeft te laden. */
export const hash = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; };
