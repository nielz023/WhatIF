/**
 * LIVE WANDSCHERMEN (verbeterpunten 7 en "levend kantoor"): elk groot scherm in een afdeling toont
 * echte cijfers uit status.json. CEO = muur van roem met thumbnails en weergaven, Script = whiteboard
 * met het begin van het script in productie, Productie = renderstand en vrije schijf, Crisis = alarmen.
 * Alles wordt op een canvas getekend en elke minuut ververst.
 */
import * as THREE from 'three';
import type { Live } from '../services/live';
import { currentStep, isLive } from './pipeline';
import type { Alarm } from './alarms';

type G = CanvasRenderingContext2D;
const W = 1024;
const img = new Map<string, HTMLImageElement | null>();
let redraw: (() => void) | null = null;
function thumb(id: string): HTMLImageElement | null {
  if (img.has(id)) return img.get(id) ?? null;
  img.set(id, null);
  const im = new Image(); im.onload = () => { img.set(id, im); redraw?.(); }; im.onerror = () => img.set(id, null); im.src = `./thumbs/${id}.jpg`;
  return null;
}
const nl = (n: number | undefined) => (n ?? 0).toLocaleString('nl-NL');
function rr(g: G, x: number, y: number, w: number, h: number, r: number) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function wrap(g: G, text: string, x: number, y: number, maxW: number, lh: number, maxLines: number) {
  const words = text.split(/\s+/); let line = ''; let n = 0;
  for (const w of words) {
    const t = line ? line + ' ' + w : w;
    if (g.measureText(t).width > maxW && line) { g.fillText(line, x, y + n * lh); n++; line = w; if (n >= maxLines) return n; }
    else line = t;
  }
  if (line && n < maxLines) { g.fillText(line, x, y + n * lh); n++; }
  return n;
}
function frame(g: G, h: number, title: string, col: string, sub?: string) {
  const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#0b1636'); bg.addColorStop(1, '#050a1c');
  g.fillStyle = bg; g.fillRect(0, 0, W, h);
  g.fillStyle = col; g.globalAlpha = 0.12; g.fillRect(0, 0, W, 86); g.globalAlpha = 1;
  g.fillStyle = col; g.fillRect(0, 84, W, 4);
  g.font = '900 50px Inter, Arial, sans-serif'; g.fillStyle = '#fff'; g.textBaseline = 'middle'; g.textAlign = 'left';
  g.shadowColor = col; g.shadowBlur = 18; g.fillText(title, 34, 44); g.shadowBlur = 0;
  if (sub) { g.font = '600 26px Inter, Arial, sans-serif'; g.fillStyle = '#9fb3e8'; g.textAlign = 'right'; g.fillText(sub, W - 30, 46); g.textAlign = 'left'; }
}
function bar(g: G, x: number, y: number, w: number, h: number, k: number, col: string) {
  rr(g, x, y, w, h, h / 2); g.fillStyle = 'rgba(255,255,255,0.1)'; g.fill();
  rr(g, x, y, Math.max(h, w * Math.min(1, k)), h, h / 2); g.fillStyle = col; g.fill();
}
function tile(g: G, id: string | undefined, x: number, y: number, w: number, h: number, col: string, title: string) {
  const im = id ? thumb(id) : null;
  rr(g, x, y, w, h, 14); g.save(); g.clip();
  if (im) g.drawImage(im, x, y, w, h);
  else { const gr = g.createLinearGradient(x, y, x + w, y + h); gr.addColorStop(0, col); gr.addColorStop(1, '#1b2a5a'); g.fillStyle = gr; g.fillRect(x, y, w, h); g.fillStyle = '#fff'; g.font = '800 22px Inter, Arial, sans-serif'; wrap(g, title, x + 12, y + 30, w - 24, 26, 3); }
  g.restore(); rr(g, x, y, w, h, 14); g.lineWidth = 3; g.strokeStyle = col; g.stroke();
}

export interface DashData { live: Live; alarms: Alarm[]; scriptLines?: string[]; scriptVideo?: number }

/** tekent het scherm van een afdeling; h = hoogte van het canvas (breedte is altijd 1024) */
export function drawRoom(g: G, room: string, h: number, d: DashData) {
  const L = d.live; const yt = L.youtube; const vids = L.videos ?? [];
  const prod = vids.filter((v) => !isLive(v));
  const now = new Date().toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
  g.textBaseline = 'middle'; g.textAlign = 'left';
  switch (room) {
    case 'ceo': {
      frame(g, h, 'MUUR VAN ROEM', '#FACC15', `${nl(yt?.subscribers)} abonnees · ${nl(yt?.views)} weergaven`);
      const longs = (yt?.videos ?? []).filter((v) => v.type === 'long').slice(0, 2);
      const shorts = (yt?.videos ?? []).filter((v) => v.type === 'short').sort((a, b) => (b.views ?? 0) - (a.views ?? 0)).slice(0, 4);
      const items = [...longs, ...shorts];
      const cols = 3; const tw = 300, th = 169; const gap = (W - cols * tw) / (cols + 1);
      items.slice(0, Math.floor((h - 110) / (th + 50)) * cols || 3).forEach((v, i) => {
        const cx = gap + (i % cols) * (tw + gap); const cy = 108 + Math.floor(i / cols) * (th + 52);
        tile(g, v.id, cx, cy, tw, th, v.type === 'long' ? '#FACC15' : '#FF7A24', v.title);
        g.font = '800 26px Inter, Arial, sans-serif'; g.fillStyle = '#fff'; g.fillText(`${v.type === 'long' ? '🎬' : '⚡'} ${nl(v.views)}`, cx + 4, cy + th + 24);
        g.font = '600 20px Inter, Arial, sans-serif'; g.fillStyle = '#9fb3e8'; g.textAlign = 'right'; g.fillText(v.type === 'long' ? 'lange video' : 'short', cx + tw - 4, cy + th + 24); g.textAlign = 'left';
      });
      break;
    }
    case 'script': { // whiteboard
      g.fillStyle = '#eef1f6'; g.fillRect(0, 0, W, h);
      g.strokeStyle = '#c5ccd9'; g.lineWidth = 10; g.strokeRect(5, 5, W - 10, h - 10);
      const v = prod.find((x) => (x.steps[currentStep(x)]?.label ?? '') !== 'Animatie') ?? prod[prod.length - 1] ?? vids[vids.length - 1];
      g.fillStyle = '#d6451b'; g.font = '700 46px "Comic Sans MS", "Segoe Print", "Bradley Hand", cursive'; const nr = d.scriptLines?.length && d.scriptVideo ? d.scriptVideo : v?.nr; g.fillText(nr ? `VIDEO ${nr} · SCRIPT` : 'SCRIPT', 36, 52);
      g.fillStyle = '#1d3b8a'; g.font = '600 30px "Comic Sans MS", "Segoe Print", "Bradley Hand", cursive';
      const lines = d.scriptLines?.length ? d.scriptLines : v ? [v.title, v.kern, `Twist: ${v.twist}`] : [];
      let y = 110; for (const ln of lines.slice(0, 6)) { const n = wrap(g, '• ' + ln, 36, y, W - 330, 36, 2); y += n * 36 + 8; if (y > h - 40) break; }
      // geeltjes met de vaste regels
      const notes = [['Hook < 5 s', '#FFE66D'], ['Abo-oproep ~60%', '#B8F2A8'], ['Geen "volgende video"', '#FFB3C7']];
      notes.forEach(([t, c], i) => { const x = W - 270, yy = 30 + i * ((h - 60) / 3); g.save(); g.translate(x + 115, yy + 55); g.rotate((i - 1) * 0.05); g.fillStyle = c; g.shadowColor = 'rgba(0,0,0,.25)'; g.shadowBlur = 10; g.fillRect(-115, -55, 230, Math.min(110, (h - 80) / 3)); g.shadowBlur = 0; g.fillStyle = '#333'; g.font = '700 26px "Comic Sans MS", cursive'; g.textAlign = 'center'; g.fillText(t, 0, 0); g.restore(); });
      g.textAlign = 'left';
      break;
    }
    case 'productie': {
      frame(g, h, 'RENDER & PRODUCTIE', '#FF4DB8', `bijgewerkt ${L.blender?.bijgewerkt?.slice(5, 16).replace('T', ' ') ?? '-'}`);
      g.font = '600 28px Inter, Arial, sans-serif'; g.fillStyle = '#dbe4ff';
      const n = wrap(g, L.blender?.stand ?? 'Geen renderstatus bekend.', 34, 132, W - 68, 36, 4);
      let y = 140 + n * 36 + 18;
      for (const v of prod.slice(0, 3)) {
        const done = v.steps.filter((s) => s.done).length; const lab = v.steps[currentStep(v)]?.label ?? '';
        g.font = '800 28px Inter, Arial, sans-serif'; g.fillStyle = '#fff'; g.fillText(`Video ${v.nr}: ${lab}`, 34, y);
        bar(g, 420, y - 12, W - 460, 24, done / v.steps.length, '#FF4DB8'); y += 50; if (y > h - 30) break;
      }
      const disk = /schijf\s*([\d.,]+)\s*GB/i.exec(L.blender?.stand ?? '')?.[1];
      if (disk && y < h - 30) { g.font = '700 26px Inter, Arial, sans-serif'; g.fillStyle = parseFloat(disk.replace(',', '.')) < 25 ? '#FF9F1C' : '#21D6A0'; g.fillText(`💽 Vrije schijf: ${disk} GB`, 34, y); }
      break;
    }
    case 'crisis': {
      const red = d.alarms.some((a) => a.level === 'rood');
      frame(g, h, d.alarms.length ? (red ? '⚠ ALARM' : '⚠ LET OP') : 'CRISISKAMER', '#FF3B4E', now);
      if (!d.alarms.length) { g.font = '800 54px Inter, Arial, sans-serif'; g.fillStyle = '#21D6A0'; g.textAlign = 'center'; g.fillText('✓ Alles rustig', W / 2, h / 2 + 30); g.textAlign = 'left'; break; }
      let y = 140;
      for (const a of d.alarms.slice(0, 5)) {
        g.fillStyle = a.level === 'rood' ? '#FF3B4E' : '#FF9F1C'; g.beginPath(); g.arc(50, y, 12, 0, Math.PI * 2); g.fill();
        g.font = '700 30px Inter, Arial, sans-serif'; g.fillStyle = '#fff'; const n = wrap(g, a.text, 80, y, W - 120, 36, 2); y += n * 36 + 20; if (y > h - 30) break;
      }
      break;
    }
    case 'stem': {
      frame(g, h, 'VOICE-OVERS', '#21D6C4', 'ElevenLabs');
      g.strokeStyle = '#21D6C4'; g.lineWidth = 5; g.shadowColor = '#21D6C4'; g.shadowBlur = 12; g.beginPath();
      for (let x = 0; x <= W - 80; x += 5) { const yy = 190 + Math.sin(x / 9) * Math.sin(x / 61) * 60 * (0.4 + 0.6 * Math.abs(Math.sin(x / 140))); if (x) g.lineTo(40 + x, yy); else g.moveTo(40, yy); }
      g.stroke(); g.shadowBlur = 0;
      g.font = '600 28px Inter, Arial, sans-serif'; g.fillStyle = '#dbe4ff'; let y = 300;
      for (const v of prod.slice(0, 3)) { const st = v.steps.find((s) => s.label === 'Stemmen'); g.fillText(`Video ${v.nr}: ${st?.done ? 'stemmen klaar ✓' : st?.active ? 'stemmen bezig…' : 'stemmen nog niet gestart'}`, 40, y); y += 42; if (y > h - 20) break; }
      break;
    }
    case 'thumbnail': {
      frame(g, h, 'THUMBNAILS', '#FF7A24', 'Test & compare');
      const tw = 440, th = 248; const y = 112;
      tile(g, 'v3', 40, y, tw, th, '#FF7A24', 'Video 3');
      const last = (yt?.videos ?? []).find((v) => v.type === 'long');
      tile(g, last?.id, W - 40 - tw, y, tw, th, '#FACC15', last?.title ?? 'Laatste video');
      g.font = '700 26px Inter, Arial, sans-serif'; g.fillStyle = '#fff';
      if (y + th + 36 < h) { g.fillText('Video 3 (definitief)', 44, y + th + 32); g.textAlign = 'right'; g.fillText(`Laatste: ${nl(last?.views)} weergaven`, W - 44, y + th + 32); g.textAlign = 'left'; }
      break;
    }
    case 'publicatie': {
      frame(g, h, 'PLANNING & UPLOAD', '#398CFF', now);
      g.font = '600 28px Inter, Arial, sans-serif'; g.fillStyle = '#dbe4ff'; let y = 132;
      for (const t of (L.next ?? []).slice(0, 5)) { g.fillStyle = '#398CFF'; g.fillText('▸', 36, y); g.fillStyle = '#dbe4ff'; const n = wrap(g, t, 70, y, W - 110, 34, 2); y += n * 34 + 14; if (y > h - 30) break; }
      break;
    }
    case 'creatief': {
      frame(g, h, 'IDEEËNBORD', '#A855F7', `${(L.ideas ?? []).length} ideeën`);
      const ideas = (L.ideas ?? []).slice(0, 6); const cw = (W - 100) / 3;
      ideas.forEach((it, i) => {
        const x = 30 + (i % 3) * (cw + 20), y = 110 + Math.floor(i / 3) * 150; if (y + 130 > h) return;
        rr(g, x, y, cw, 130, 16); g.fillStyle = 'rgba(168,85,247,0.16)'; g.fill(); g.strokeStyle = '#A855F7'; g.lineWidth = 2; g.stroke();
        g.font = '700 26px Inter, Arial, sans-serif'; g.fillStyle = '#fff'; wrap(g, it.title, x + 16, y + 36, cw - 32, 30, 2);
        g.font = '600 20px Inter, Arial, sans-serif'; g.fillStyle = '#c9a6ff'; g.fillText(it.groep, x + 16, y + 108);
      });
      break;
    }
    case 'onderzoek': {
      frame(g, h, 'WAT WERKT', '#20D9FF', 'shorts · weergaven');
      const sh = (yt?.videos ?? []).filter((v) => v.type === 'short').sort((a, b) => (b.views ?? 0) - (a.views ?? 0)).slice(0, 6);
      const max = Math.max(1, ...sh.map((v) => v.views ?? 0)); let y = 130;
      for (const v of sh) { g.font = '600 24px Inter, Arial, sans-serif'; g.fillStyle = '#dbe4ff'; const t = v.title.length > 38 ? v.title.slice(0, 37) + '…' : v.title; g.fillText(t, 34, y); bar(g, 560, y - 11, 330, 22, (v.views ?? 0) / max, '#20D9FF'); g.fillStyle = '#fff'; g.font = '800 24px Inter, Arial, sans-serif'; g.textAlign = 'right'; g.fillText(nl(v.views), W - 30, y); g.textAlign = 'left'; y += 44; if (y > h - 20) break; }
      break;
    }
    default: frame(g, h, 'DRIFTMARK', '#FF7A24');
  }
}

/** één canvas-textuur per afdeling en schermvorm (zelfde verhouding = zelfde textuur); tekent opnieuw bij nieuwe gegevens */
export class Dashboards {
  tex = new Map<string, { t: THREE.CanvasTexture; h: number; room: string }>();
  data: DashData | null = null;
  constructor() { redraw = () => this.draw(); }
  get(room: string, aspect: number) {
    const h = Math.round(W / Math.max(1.2, Math.min(3, aspect)));
    const key = room + ':' + h;
    let e = this.tex.get(key);
    if (!e) {
      const c = document.createElement('canvas'); c.width = W; c.height = h;
      const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.flipY = false;
      e = { t, h, room }; this.tex.set(key, e); this.drawOne(key);
    }
    return e.t;
  }
  set(d: DashData) { this.data = d; this.draw(); }
  draw() { for (const k of this.tex.keys()) this.drawOne(k); }
  drawOne(key: string) {
    const e = this.tex.get(key); if (!e || !this.data) return;
    const c = e.t.image as HTMLCanvasElement; const g = c.getContext('2d')!;
    g.save(); g.clearRect(0, 0, c.width, c.height);
    try { drawRoom(g, e.room, e.h, this.data); } catch (err) { console.warn('[HQ] scherm', e.room, err); }
    g.restore(); e.t.needsUpdate = true;
  }
}
