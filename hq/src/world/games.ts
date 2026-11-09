/**
 * DE SPELLEN VAN DE GAME ROOM (niels 2026-11-09: "je kan zelf ook gamen in de rondloopmodus"). Negen kleine, eigen,
 * verzonnen spellen op een canvas, zonder plaatjes of bestanden: zes gamekasten, de racesimulator, de airhockeytafel en
 * de grijpmachine. Elk spel heeft een vaste logische maat (w x h); GamePanel.tsx schaalt het canvas en geeft de
 * toetsen, het aanraken en de muis door. Geen bestaande games nagemaakt: alleen algemene spelsoorten.
 */
import { soundOn } from './sound';
import type { GameId } from './play';

export interface Input {
  l: boolean; r: boolean; u: boolean; d: boolean; a: boolean;
  /** net ingedrukt (alleen deze stap) */
  lHit: boolean; rHit: boolean; uHit: boolean; dHit: boolean; aHit: boolean;
  /** muis of vinger in spelcoördinaten (null = niet gebruikt), en net ingedrukt */
  px: number | null; py: number | null; pDown: boolean; pHit: boolean;
}
export interface Game {
  w: number; h: number; score: number; over: boolean;
  /** extra regel onder de score (levens, tijd, ...) */
  info: string;
  step(dt: number, k: Input): void;
  draw(g: CanvasRenderingContext2D, t: number): void;
}
export interface GameDef { naam: string; uitleg: string; knoppen: ('l' | 'r' | 'u' | 'd' | 'a')[]; kleur: string; make: () => Game }

/* ---------- hulpjes ---------- */
const rnd = (a: number, b: number) => a + Math.random() * (b - a);
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
let ac: AudioContext | null = null;
/** piepje (zacht, alleen als het geluid in de HQ aan staat) */
export function blip(f: number, d = 0.08, type: OscillatorType = 'square', v = 0.035) {
  if (!soundOn()) return;
  try {
    const C = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext; if (!C) return;
    ac ??= new C(); const o = ac.createOscillator(); const gn = ac.createGain(); const t0 = ac.currentTime;
    o.type = type; o.frequency.setValueAtTime(f, t0); gn.gain.setValueAtTime(v, t0); gn.gain.exponentialRampToValueAtTime(0.0001, t0 + d);
    o.connect(gn).connect(ac.destination); o.start(t0); o.stop(t0 + d + 0.02);
  } catch { /* geen geluid */ }
}
function glow(g: CanvasRenderingContext2D, col: string, blur: number) { g.shadowColor = col; g.shadowBlur = blur; }
function noGlow(g: CanvasRenderingContext2D) { g.shadowBlur = 0; }
function rrect(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) { g.beginPath(); g.roundRect(x, y, w, h, r); g.fill(); }
function starShape(g: CanvasRenderingContext2D, x: number, y: number, r: number, rot = 0) {
  g.beginPath(); for (let i = 0; i < 10; i++) { const a = rot + (i * Math.PI) / 5 - Math.PI / 2; const rr = i % 2 ? r * 0.45 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill();
}
/** het hoofdpersonage als klein poppetje (grote kale ronde kop, grote oren, oranje hoodie), voor SKY HOP en SNAIL RUN */
function hero(g: CanvasRenderingContext2D, x: number, y: number, s: number, run = 0, duck = false) {
  const leg = Math.sin(run * 14) * 5 * s;
  g.fillStyle = '#2b3150'; g.fillRect(x - 5 * s + leg * 0.3, y - 9 * s, 4 * s, 9 * s); g.fillRect(x + 1 * s - leg * 0.3, y - 9 * s, 4 * s, 9 * s);
  g.fillStyle = '#ffffff'; g.fillRect(x - 6 * s + leg * 0.3, y - 2 * s, 6 * s, 2 * s); g.fillRect(x + 1 * s - leg * 0.3, y - 2 * s, 6 * s, 2 * s);
  const bodyH = duck ? 10 * s : 15 * s;
  g.fillStyle = '#FF7A24'; rrect(g, x - 8 * s, y - 9 * s - bodyH, 16 * s, bodyH, 4 * s);
  const hx = x + (duck ? 4 * s : 0), hy = y - 9 * s - bodyH - 9 * s;
  g.fillStyle = '#e9b48f'; g.beginPath(); g.ellipse(hx - 11 * s, hy + 1 * s, 3.5 * s, 4.5 * s, 0, 0, Math.PI * 2); g.ellipse(hx + 11 * s, hy + 1 * s, 3.5 * s, 4.5 * s, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#f2c4a0'; g.beginPath(); g.arc(hx, hy, 11 * s, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#ffffff'; g.beginPath(); g.arc(hx + 2 * s, hy - 1 * s, 2.6 * s, 0, Math.PI * 2); g.arc(hx + 7.5 * s, hy - 1 * s, 2.6 * s, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#111'; g.beginPath(); g.arc(hx + 2.8 * s, hy - 0.6 * s, 1.3 * s, 0, Math.PI * 2); g.arc(hx + 8.2 * s, hy - 0.6 * s, 1.3 * s, 0, Math.PI * 2); g.fill();
  g.strokeStyle = '#7a2e12'; g.lineWidth = 1.4 * s; g.beginPath(); g.arc(hx + 5 * s, hy + 4 * s, 3 * s, 0.15, Math.PI - 0.15); g.stroke();
}
function sky(g: CanvasRenderingContext2D, w: number, h: number, a: string, b: string) {
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.fillRect(0, 0, w, h);
}
const BG_STARS = Array.from({ length: 60 }, (_, i) => [((i * 97) % 100) / 100, ((i * 61 + 13) % 100) / 100, (i % 3) + 1] as const);
function stars(g: CanvasRenderingContext2D, w: number, h: number, t: number, off = 0) {
  BG_STARS.forEach(([x, y, s], i) => { g.globalAlpha = 0.35 + 0.35 * Math.sin(t * 2 + i); g.fillStyle = '#ffffff'; g.fillRect(x * w, ((y * h + off * s * 0.3) % h + h) % h, s * 0.8, s * 0.8); });
  g.globalAlpha = 1;
}
function hud(g: CanvasRenderingContext2D, w: number, left: string, right: string, col = '#ffffff') {
  g.font = 'bold 15px ui-monospace, monospace'; g.fillStyle = col; g.textAlign = 'left'; g.textBaseline = 'top'; g.fillText(left, 10, 8);
  g.textAlign = 'right'; g.fillText(right, w - 10, 8); g.textBaseline = 'alphabetic';
}
const hearts = (n: number) => '♥'.repeat(Math.max(0, n));

/* =================== 1. NEON BREAK: kaats de neonstenen kapot =================== */
function neonBreak(): Game {
  const W = 360, H = 480; const pw = 72, py = 446;
  type Brick = { x: number; y: number; w: number; h: number; hp: number; row: number };
  let px = W / 2; let bricks: Brick[] = []; let lvl = 1; let lives = 3; let sp = 330;
  const ball = { x: W / 2, y: py - 9, vx: 0, vy: 0, stuck: true };
  const COLS = ['#FF4DB8', '#FF7A24', '#FACC15', '#4ADE80', '#20D9FF', '#A855F7'];
  const build = () => { bricks = []; const bw = (W - 24) / 8; for (let r = 0; r < 6; r++) for (let c = 0; c < 8; c++) if (lvl < 3 || (r + c + lvl) % 7) bricks.push({ x: 12 + c * bw + 2, y: 54 + r * 20, w: bw - 4, h: 15, hp: lvl >= 2 && r < 2 ? 2 : 1, row: r }); };
  build();
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      if (k.px !== null) px = k.px; else px += ((k.r ? 1 : 0) - (k.l ? 1 : 0)) * 420 * dt;
      px = clamp(px, pw / 2 + 4, W - pw / 2 - 4);
      if (ball.stuck) {
        ball.x = px; ball.y = py - 9;
        if (k.aHit || k.uHit || k.pHit) { ball.stuck = false; const a = rnd(-0.5, 0.5); ball.vx = Math.sin(a) * sp; ball.vy = -Math.cos(a) * sp; blip(520); }
      } else {
        const n = 4;
        for (let s = 0; s < n; s++) {
          ball.x += (ball.vx * dt) / n; ball.y += (ball.vy * dt) / n;
          if (ball.x < 7) { ball.x = 7; ball.vx = Math.abs(ball.vx); blip(300, 0.03); }
          if (ball.x > W - 7) { ball.x = W - 7; ball.vx = -Math.abs(ball.vx); blip(300, 0.03); }
          if (ball.y < 36) { ball.y = 36; ball.vy = Math.abs(ball.vy); blip(300, 0.03); }
          if (ball.vy > 0 && ball.y > py - 8 && ball.y < py + 6 && Math.abs(ball.x - px) < pw / 2 + 6) {
            const f = clamp((ball.x - px) / (pw / 2), -1, 1); const a = f * 1.05; ball.vx = Math.sin(a) * sp; ball.vy = -Math.cos(a) * sp; ball.y = py - 8; blip(440, 0.04);
          }
          for (const b of bricks) {
            if (b.hp <= 0) continue;
            const cx = clamp(ball.x, b.x, b.x + b.w), cy = clamp(ball.y, b.y, b.y + b.h);
            if ((ball.x - cx) ** 2 + (ball.y - cy) ** 2 > 36) continue;
            const ox = Math.min(Math.abs(ball.x - b.x), Math.abs(ball.x - b.x - b.w)), oy = Math.min(Math.abs(ball.y - b.y), Math.abs(ball.y - b.y - b.h));
            if (ox < oy && (ball.x < b.x || ball.x > b.x + b.w)) ball.vx = -ball.vx; else ball.vy = -ball.vy;
            b.hp--; if (b.hp <= 0) { game.score += 10 * (6 - b.row) * lvl; sp = Math.min(560, sp + 4); }
            blip(660 + (6 - b.row) * 60, 0.05); break;
          }
          if (ball.y > H + 10) { lives--; blip(160, 0.3, 'sawtooth'); ball.stuck = true; if (lives <= 0) game.over = true; break; }
        }
      }
      if (!bricks.some((b) => b.hp > 0)) { lvl++; sp = 330 + lvl * 20; build(); ball.stuck = true; game.score += 250; blip(880, 0.2, 'triangle'); }
      game.info = `${hearts(lives)}  level ${lvl}`;
    },
    draw(g, t) {
      sky(g, W, H, '#070a1f', '#160b33'); stars(g, W, H, t);
      for (const b of bricks) { if (b.hp <= 0) continue; const c = COLS[b.row]; glow(g, c, 10); g.fillStyle = b.hp > 1 ? '#ffffff' : c; rrect(g, b.x, b.y, b.w, b.h, 4); }
      glow(g, '#20D9FF', 16); g.fillStyle = '#20D9FF'; rrect(g, px - pw / 2, py, pw, 10, 5);
      glow(g, '#ffffff', 14); g.fillStyle = '#ffffff'; g.beginPath(); g.arc(ball.x, ball.y, 6, 0, Math.PI * 2); g.fill(); noGlow(g);
      hud(g, W, `${game.score}`, game.info);
      if (ball.stuck) { g.fillStyle = '#ffffffcc'; g.font = '14px system-ui'; g.textAlign = 'center'; g.fillText('spatie of tik: bal afschieten', W / 2, H * 0.62); }
    },
  };
  return game;
}

/* =================== 2. SKY HOP: spring zo hoog mogelijk over de wolken =================== */
function skyHop(): Game {
  const W = 360, H = 540;
  type P = { x: number; y: number; w: number; kind: 0 | 1 | 2; dx: number; gone: boolean };
  const pl: P[] = []; let top = H - 30; let camY = 0; let best = 0;
  const p = { x: W / 2, y: H - 60, vx: 0, vy: -650 };
  const add = (y: number) => { const hgt = (H - y) / 10; const kind = (hgt > 150 && Math.random() < 0.22 ? 1 : hgt > 300 && Math.random() < 0.15 ? 2 : 0) as 0 | 1 | 2; pl.push({ x: rnd(10, W - 80), y, w: kind === 2 ? 60 : 70, kind, dx: kind === 1 ? rnd(50, 110) * (Math.random() < 0.5 ? -1 : 1) : 0, gone: false }); };
  pl.push({ x: W / 2 - 40, y: H - 30, w: 80, kind: 0, dx: 0, gone: false });
  while (top > -H) { top -= rnd(60, 95); add(top); }
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      const dir = k.px !== null ? clamp((k.px - p.x) / 40, -1, 1) : (k.r ? 1 : 0) - (k.l ? 1 : 0);
      p.vx += (dir * 1500 - p.vx * 4) * dt; p.x += p.vx * dt;
      if (p.x < -12) p.x = W + 12; if (p.x > W + 12) p.x = -12;
      const vy0 = p.vy; p.vy += 1300 * dt; const y0 = p.y; p.y += p.vy * dt;
      if (vy0 > 0 || p.vy > 0) for (const q of pl) {
        if (q.gone || p.x < q.x - 8 || p.x > q.x + q.w + 8) continue;
        if (y0 <= q.y && p.y >= q.y) { p.y = q.y; p.vy = -660; blip(q.kind === 2 ? 240 : 520, 0.06, 'triangle'); if (q.kind === 2) q.gone = true; break; }
      }
      for (const q of pl) if (q.dx) { q.x += q.dx * dt; if (q.x < 0 || q.x > W - q.w) q.dx = -q.dx; }
      if (p.y < camY + H * 0.42) camY = p.y - H * 0.42;
      while (top > camY - 80) { const hgt = (H - top) / 10; top -= rnd(60, Math.min(125, 85 + hgt * 0.06)); add(top); }
      for (let i = pl.length - 1; i >= 0; i--) if (pl[i].y > camY + H + 40) pl.splice(i, 1);
      best = Math.max(best, Math.round((H - 60 - p.y) / 10)); game.score = best;
      if (p.y > camY + H + 30) { game.over = true; blip(150, 0.4, 'sawtooth'); }
      game.info = `${best} m hoog`;
    },
    draw(g, t) {
      const hgt = clamp(best / 600, 0, 1);
      sky(g, W, H, hgt > 0.5 ? '#070a24' : '#1b3f8a', hgt > 0.5 ? '#2a1a5e' : '#6fb2ff'); if (hgt > 0.3) { g.globalAlpha = hgt; stars(g, W, H, t, -camY * 0.05); g.globalAlpha = 1; }
      for (const q of pl) {
        if (q.gone) continue; const y = q.y - camY;
        g.fillStyle = q.kind === 1 ? '#c9f7ff' : q.kind === 2 ? '#ffd6e8' : '#ffffff';
        rrect(g, q.x, y - 4, q.w, 12, 6); g.beginPath(); g.arc(q.x + q.w * 0.3, y - 2, 9, 0, Math.PI * 2); g.arc(q.x + q.w * 0.62, y - 4, 11, 0, Math.PI * 2); g.fill();
        if (q.kind === 2) { g.strokeStyle = '#ff7cc9'; g.lineWidth = 2; g.beginPath(); g.moveTo(q.x + q.w / 2, y - 8); g.lineTo(q.x + q.w / 2 + 4, y + 6); g.stroke(); }
      }
      hero(g, p.x, p.y - camY, 1, t, false);
      hud(g, W, `${game.score}`, game.info, hgt > 0.4 ? '#ffffff' : '#0b1130');
    },
  };
  return game;
}

/* =================== 3. ORBIT RUN: wissel van baan rond de planeet =================== */
function orbitRun(): Game {
  const W = 360, H = 480, cx = W / 2, cy = H / 2 + 14; const R = [64, 112, 160];
  let o = 1, rr = R[1], a = -Math.PI / 2, w = 1.35, spawn = 0.6, tt = 0, nStars = 0;
  type Ob = { o: number; a: number; star: boolean; age: number; rot: number };
  const obs: Ob[] = []; const trail: [number, number][] = [];
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      tt += dt; w = Math.min(2.6, 1.35 + tt * 0.025);
      let to = o;
      if (k.uHit || k.aHit) to = Math.min(2, o + 1);
      if (k.dHit) to = Math.max(0, o - 1);
      if (k.pHit && k.px !== null && k.py !== null) to = Math.hypot(k.px - cx, k.py - cy) > R[o] ? Math.min(2, o + 1) : Math.max(0, o - 1);
      if (to !== o) { o = to; blip(380 + o * 140, 0.05, 'triangle'); }
      rr += (R[o] - rr) * Math.min(1, dt * 14); a += w * dt;
      const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr; trail.unshift([x, y]); if (trail.length > 14) trail.pop();
      spawn -= dt;
      if (spawn <= 0) { spawn = Math.max(0.32, 0.85 - tt * 0.01); const n = Math.random() < Math.min(0.5, tt * 0.01) ? 2 : 1; const used = new Set<number>(); for (let i = 0; i < n; i++) { let oo = Math.floor(Math.random() * 3); while (used.has(oo)) oo = (oo + 1) % 3; used.add(oo); obs.push({ o: oo, a: a + Math.PI * rnd(0.85, 1.15), star: Math.random() < 0.28, age: 0, rot: rnd(0, 6) }); } }
      for (let i = obs.length - 1; i >= 0; i--) {
        const b = obs[i]; b.age += dt; b.a -= 0.25 * dt; b.rot += dt * 2;
        const bx = cx + Math.cos(b.a) * R[b.o], by = cy + Math.sin(b.a) * R[b.o];
        if (Math.hypot(bx - x, by - y) < (b.star ? 18 : 15)) {
          if (b.star) { nStars++; obs.splice(i, 1); blip(990, 0.08, 'triangle'); continue; }
          game.over = true; blip(120, 0.5, 'sawtooth'); return;
        }
        if (b.age > 7) obs.splice(i, 1);
      }
      game.score = Math.floor(tt * 10) + nStars * 25; game.info = `★ ${nStars}`;
    },
    draw(g, t) {
      sky(g, W, H, '#05061a', '#140a33'); stars(g, W, H, t);
      g.strokeStyle = '#A855F755'; g.lineWidth = 2; R.forEach((r, i) => { g.strokeStyle = i === o ? '#A855F7aa' : '#A855F740'; g.beginPath(); g.arc(cx, cy, r, 0, Math.PI * 2); g.stroke(); });
      const pg = g.createRadialGradient(cx - 10, cy - 10, 4, cx, cy, 40); pg.addColorStop(0, '#ffb27a'); pg.addColorStop(1, '#c2410c');
      glow(g, '#FF7A24', 30); g.fillStyle = pg; g.beginPath(); g.arc(cx, cy, 36, 0, Math.PI * 2); g.fill(); noGlow(g);
      for (const b of obs) {
        const bx = cx + Math.cos(b.a) * R[b.o], by = cy + Math.sin(b.a) * R[b.o];
        if (b.star) { glow(g, '#FACC15', 12); g.fillStyle = '#FACC15'; starShape(g, bx, by, 10, b.rot); noGlow(g); }
        else { g.fillStyle = '#8b93ad'; g.beginPath(); for (let i = 0; i < 7; i++) { const aa = b.rot + (i * Math.PI * 2) / 7; const r = 11 + ((i * 5) % 3) * 2; g.lineTo(bx + Math.cos(aa) * r, by + Math.sin(aa) * r); } g.closePath(); g.fill(); g.fillStyle = '#5d6480'; g.beginPath(); g.arc(bx - 3, by - 2, 3, 0, Math.PI * 2); g.fill(); }
      }
      trail.forEach(([x, y], i) => { g.globalAlpha = 1 - i / trail.length; g.fillStyle = '#20D9FF'; g.beginPath(); g.arc(x, y, 7 * (1 - i / trail.length), 0, Math.PI * 2); g.fill(); });
      g.globalAlpha = 1; const [x, y] = trail[0] ?? [cx, cy - rr]; glow(g, '#20D9FF', 18); g.fillStyle = '#ffffff'; g.beginPath(); g.arc(x, y, 8, 0, Math.PI * 2); g.fill(); noGlow(g);
      hud(g, W, `${game.score}`, game.info);
    },
  };
  return game;
}

/* =================== 4. DRIFT DASH: ontwijk kegels en auto's =================== */
function driftDash(): Game {
  const W = 360, H = 540, L0 = 40, LW = 70; let x = W / 2, v = 260, dist = 0, coins = 0, lives = 3, inv = 0, spawn = 0.4, off = 0;
  type Ob = { lane: number; y: number; kind: 'kegel' | 'auto' | 'munt'; col: string };
  const obs: Ob[] = [];
  const lx = (lane: number) => L0 + LW * lane + LW / 2;
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      v = Math.min(640, v + 7 * dt); dist += v * dt; off = (off + v * dt) % 60; inv -= dt;
      if (k.px !== null) x += clamp(k.px - x, -420 * dt, 420 * dt); else x += ((k.r ? 1 : 0) - (k.l ? 1 : 0)) * 330 * dt;
      x = clamp(x, L0 + 18, L0 + 4 * LW - 18);
      spawn -= dt;
      if (spawn <= 0) {
        spawn = Math.max(0.3, 0.62 - dist / 40000) * (260 / v) * 1.6;
        const free = Math.floor(Math.random() * 4); const n = Math.random() < 0.45 ? 2 : 1;
        const lanes = [0, 1, 2, 3].filter((l) => l !== free).sort(() => Math.random() - 0.5).slice(0, n);
        lanes.forEach((l) => obs.push({ lane: l, y: -50, kind: Math.random() < 0.55 ? 'kegel' : 'auto', col: ['#20D9FF', '#A855F7', '#4ADE80', '#FACC15'][Math.floor(Math.random() * 4)] }));
        if (Math.random() < 0.55) obs.push({ lane: free, y: -50, kind: 'munt', col: '#FACC15' });
      }
      for (let i = obs.length - 1; i >= 0; i--) {
        const b = obs[i]; b.y += v * dt * (b.kind === 'auto' ? 0.72 : 1);
        const bw = b.kind === 'auto' ? 40 : 24, bh = b.kind === 'auto' ? 64 : 24;
        if (Math.abs(lx(b.lane) - x) < bw / 2 + 16 && Math.abs(b.y - 468) < bh / 2 + 28) {
          if (b.kind === 'munt') { coins++; obs.splice(i, 1); blip(1046, 0.07, 'triangle'); continue; }
          if (inv <= 0) { lives--; inv = 1.4; v = Math.max(240, v * 0.7); blip(140, 0.35, 'sawtooth'); obs.splice(i, 1); if (lives <= 0) { game.over = true; return; } continue; }
        }
        if (b.y > H + 80) obs.splice(i, 1);
      }
      game.score = Math.floor(dist / 10) + coins * 50; game.info = `${hearts(lives)}  ${Math.round(v * 0.4)} km/u`;
    },
    draw(g) {
      g.fillStyle = '#0c1430'; g.fillRect(0, 0, W, H);
      g.fillStyle = '#16203d'; g.fillRect(L0, 0, LW * 4, H);
      for (const sx of [L0, L0 + LW * 4]) { glow(g, '#FF3B4E', 12); g.fillStyle = '#FF3B4E'; g.fillRect(sx - 3, 0, 6, H); }
      noGlow(g); g.fillStyle = '#ffffff55';
      for (let l = 1; l < 4; l++) for (let y = -60 + off; y < H; y += 60) g.fillRect(L0 + l * LW - 2, y, 4, 30);
      for (const b of obs) {
        const bx = lx(b.lane);
        if (b.kind === 'kegel') { g.fillStyle = '#FF7A24'; g.beginPath(); g.moveTo(bx, b.y - 14); g.lineTo(bx + 12, b.y + 12); g.lineTo(bx - 12, b.y + 12); g.closePath(); g.fill(); g.fillStyle = '#fff'; g.fillRect(bx - 7, b.y + 1, 14, 3); }
        else if (b.kind === 'auto') { g.fillStyle = b.col; rrect(g, bx - 20, b.y - 32, 40, 64, 8); g.fillStyle = '#0b1130'; rrect(g, bx - 15, b.y - 18, 30, 14, 3); rrect(g, bx - 15, b.y + 10, 30, 10, 3); }
        else { glow(g, '#FACC15', 10); g.fillStyle = '#FACC15'; g.beginPath(); g.arc(bx, b.y, 10, 0, Math.PI * 2); g.fill(); noGlow(g); g.fillStyle = '#b45309'; g.font = 'bold 11px system-ui'; g.textAlign = 'center'; g.fillText('D', bx, b.y + 4); }
      }
      if (inv <= 0 || Math.floor(inv * 10) % 2) { glow(g, '#FF3B4E', 16); g.fillStyle = '#FF3B4E'; rrect(g, x - 17, 440, 34, 58, 9); noGlow(g); g.fillStyle = '#0b1130'; rrect(g, x - 13, 452, 26, 13, 3); g.fillStyle = '#ffe9a8'; g.fillRect(x - 13, 438, 7, 4); g.fillRect(x + 6, 438, 7, 4); }
      hud(g, W, `${game.score}`, game.info);
    },
  };
  return game;
}

/* =================== 5. COMET CATCH: vang de sterren, ontwijk de meteorieten =================== */
function cometCatch(): Game {
  const W = 360, H = 480, BW = 66; let x = W / 2, lives = 3, combo = 0, spawn = 0.5, tt = 0;
  type It = { x: number; y: number; v: number; kind: 'ster' | 'groot' | 'meteor' | 'hart'; r: number };
  const items: It[] = []; const pops: { x: number; y: number; t: number; s: string }[] = [];
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      tt += dt;
      if (k.px !== null) x += clamp(k.px - x, -520 * dt, 520 * dt); else x += ((k.r ? 1 : 0) - (k.l ? 1 : 0)) * 380 * dt;
      x = clamp(x, BW / 2, W - BW / 2);
      spawn -= dt;
      if (spawn <= 0) {
        spawn = Math.max(0.28, 0.75 - tt * 0.008); const r = Math.random();
        const kind = r < 0.05 && lives < 5 ? 'hart' : r < 0.14 ? 'groot' : r < 0.42 + Math.min(0.2, tt * 0.003) ? 'meteor' : 'ster';
        items.push({ x: rnd(16, W - 16), y: -20, v: rnd(140, 200) + tt * 2.4, kind, r: kind === 'meteor' ? 13 : kind === 'groot' ? 14 : 10 });
      }
      for (let i = items.length - 1; i >= 0; i--) {
        const it = items[i]; it.y += it.v * dt;
        if (it.y > 432 && it.y < 456 && Math.abs(it.x - x) < BW / 2 + it.r * 0.6) {
          items.splice(i, 1);
          if (it.kind === 'meteor') { lives--; combo = 0; blip(130, 0.35, 'sawtooth'); pops.push({ x: it.x, y: 430, t: 0, s: 'au!' }); if (lives <= 0) { game.over = true; return; } }
          else if (it.kind === 'hart') { lives = Math.min(5, lives + 1); blip(880, 0.12, 'triangle'); pops.push({ x: it.x, y: 430, t: 0, s: '+♥' }); }
          else { combo++; const pts = (it.kind === 'groot' ? 50 : 10) * Math.min(5, 1 + Math.floor(combo / 8)); game.score += pts; blip(it.kind === 'groot' ? 1175 : 784 + Math.min(combo, 12) * 20, 0.06, 'triangle'); pops.push({ x: it.x, y: 430, t: 0, s: `+${pts}` }); }
          continue;
        }
        if (it.y > H + 20) { if (it.kind === 'ster' || it.kind === 'groot') combo = 0; items.splice(i, 1); }
      }
      for (let i = pops.length - 1; i >= 0; i--) { pops[i].t += dt; if (pops[i].t > 0.8) pops.splice(i, 1); }
      game.info = `${hearts(lives)}  x${Math.min(5, 1 + Math.floor(combo / 8))}`;
    },
    draw(g, t) {
      sky(g, W, H, '#03051a', '#1a1046'); stars(g, W, H, t, t * 20);
      g.fillStyle = '#2a1a5e'; g.beginPath(); g.arc(W * 0.8, H * 0.2, 46, 0, Math.PI * 2); g.fill(); g.fillStyle = '#3b2a7e'; g.beginPath(); g.arc(W * 0.8 - 12, H * 0.2 - 10, 14, 0, Math.PI * 2); g.fill();
      for (const it of items) {
        if (it.kind === 'meteor') { g.fillStyle = '#ff5a3d55'; g.beginPath(); g.moveTo(it.x - 8, it.y - 6); g.lineTo(it.x, it.y - 40); g.lineTo(it.x + 8, it.y - 6); g.fill(); glow(g, '#FF3B4E', 14); g.fillStyle = '#c2410c'; g.beginPath(); g.arc(it.x, it.y, it.r, 0, Math.PI * 2); g.fill(); }
        else if (it.kind === 'hart') { glow(g, '#FF4DB8', 14); g.fillStyle = '#FF4DB8'; g.font = '24px system-ui'; g.textAlign = 'center'; g.fillText('♥', it.x, it.y + 8); }
        else { glow(g, '#FACC15', 14); g.fillStyle = it.kind === 'groot' ? '#ffffff' : '#FACC15'; starShape(g, it.x, it.y, it.r, t * 2); }
        noGlow(g);
      }
      glow(g, '#398CFF', 14); g.fillStyle = '#398CFF'; g.beginPath(); g.moveTo(x - BW / 2, 436); g.lineTo(x + BW / 2, 436); g.lineTo(x + BW / 2 - 8, 466); g.lineTo(x - BW / 2 + 8, 466); g.closePath(); g.fill(); noGlow(g);
      g.fillStyle = '#ffffff33'; for (let i = 1; i < 4; i++) g.fillRect(x - BW / 2 + (i * BW) / 4, 438, 2, 26);
      for (const p of pops) { g.globalAlpha = 1 - p.t / 0.8; g.fillStyle = '#ffffff'; g.font = 'bold 15px system-ui'; g.textAlign = 'center'; g.fillText(p.s, p.x, p.y - p.t * 50); }
      g.globalAlpha = 1; hud(g, W, `${game.score}`, game.info);
    },
  };
  return game;
}

/* =================== 6. SNAIL RUN: het hoofdpersonage rent en springt =================== */
function snailRun(): Game {
  const W = 480, H = 270, GY = 222; let y = GY, vy = 0, v = 300, dist = 0, next = 320, run = 0, duck = false;
  type Ob = { x: number; w: number; h: number; fly: boolean };
  const obs: Ob[] = [];
  const city = Array.from({ length: 16 }, (_, i) => [i * 40, 40 + ((i * 37) % 70), ['#FF4DB8', '#20D9FF', '#A855F7', '#FF7A24'][i % 4]] as const);
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      v = Math.min(720, v + 9 * dt); dist += v * dt; run += dt * (v / 300);
      const ground = y >= GY - 0.5; duck = k.d && ground;
      if ((k.uHit || k.aHit || k.pHit) && ground) { vy = -600; blip(520, 0.07, 'triangle'); }
      const hold = (k.u || k.a || k.pDown) && vy < 0;
      vy += (hold ? 1250 : 2300) * dt; if (k.d && !ground) vy += 2000 * dt; y = Math.min(GY, y + vy * dt); if (y >= GY) vy = 0;
      next -= v * dt;
      if (next <= 0) {
        const fly = dist > 2500 && Math.random() < 0.3;
        obs.push(fly ? { x: W + 20, w: 34, h: 16, fly: true } : { x: W + 20, w: rnd(18, 34), h: rnd(26, 50), fly: false });
        next = rnd(240, 480) * (v / 300) * 0.9;
      }
      const hx = 80, hw = 14, hh = duck ? 30 : 44;
      for (let i = obs.length - 1; i >= 0; i--) {
        const o = obs[i]; o.x -= v * dt; if (o.x < -60) { obs.splice(i, 1); continue; }
        const oy0 = o.fly ? GY - 60 : GY - o.h, oy1 = o.fly ? GY - 60 + o.h : GY;
        if (o.x < hx + hw && o.x + o.w > hx - hw && y - hh < oy1 && y > oy0) { game.over = true; blip(130, 0.45, 'sawtooth'); return; }
      }
      game.score = Math.floor(dist / 10); game.info = `${Math.floor(dist / 10)} m`;
    },
    draw(g, t) {
      sky(g, W, H, '#0a0f33', '#3b1a5e'); stars(g, W, H * 0.6, t);
      const sh = (dist * 0.15) % 640;
      city.forEach(([cx, ch, col]) => { const x = ((cx - sh) % 640 + 640) % 640 - 40; g.fillStyle = '#141a40'; g.fillRect(x, GY - ch, 36, ch); g.fillStyle = col + '88'; for (let wy = GY - ch + 8; wy < GY - 6; wy += 12) g.fillRect(x + 6, wy, 6, 4), g.fillRect(x + 22, wy, 6, 4); });
      g.fillStyle = '#16203d'; g.fillRect(0, GY, W, H - GY); glow(g, '#FF7A24', 10); g.fillStyle = '#FF7A24'; g.fillRect(0, GY, W, 3); noGlow(g);
      g.fillStyle = '#ffffff22'; for (let x = -((dist * 1) % 40); x < W; x += 40) g.fillRect(x, GY + 16, 18, 3);
      for (const o of obs) {
        if (o.fly) { glow(g, '#20D9FF', 10); g.fillStyle = '#20D9FF'; rrect(g, o.x, GY - 60, o.w, o.h, 6); noGlow(g); g.fillStyle = '#c9d1e0'; const f = Math.sin(t * 40) * 6; g.fillRect(o.x - 4, GY - 64 + f * 0.1, 12, 2); g.fillRect(o.x + o.w - 8, GY - 64, 12, 2); }
        else { g.fillStyle = '#4ADE80'; rrect(g, o.x, GY - o.h, o.w, o.h, 4); g.fillStyle = '#16a34a'; g.fillRect(o.x + 3, GY - o.h + 6, o.w - 6, 3); }
      }
      hero(g, 80, y, 1.35, y < GY ? 0 : run, duck);
      hud(g, W, `${game.score}`, 'spring: spatie / ▲ · bukken: ▼');
    },
  };
  return game;
}

/* =================== 7. DRIFT GP: racen met bochten en verkeer (racesimulator) =================== */
function driftGp(): Game {
  const W = 480, H = 300, HOR = 116, D = 230, MAXV = 70;
  let pos = 0, sp = 0, x = 0, time = 45, next = 1500, crash = 0, bg = 0, cps = 0, steer = 0;
  const curve = (z: number) => 0.0042 * Math.sin(z / 150) + 0.003 * Math.sin(z / 57 + 2) * Math.max(0, Math.min(1, (z - 400) / 400));
  const cars = Array.from({ length: 7 }, (_, i) => ({ z: 60 + i * 55, x: rnd(-0.7, 0.7), v: rnd(26, 44), col: ['#20D9FF', '#4ADE80', '#A855F7', '#FACC15', '#ffffff'][i % 5] }));
  const zs: number[] = [], xs: number[] = [];
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      crash = Math.max(0, crash - dt);
      const gas = !k.d && crash <= 0; sp += (gas ? (MAXV - sp) * 0.45 : -sp * 1.8) * dt;
      const off = Math.abs(x) > 1.0; if (off) sp = Math.max(sp - 60 * dt, Math.min(sp, 22));
      const want = k.px !== null && k.pDown ? clamp((k.px - W / 2) / (W * 0.3), -1, 1) : (k.r ? 1 : 0) - (k.l ? 1 : 0);
      steer += (want - steer) * Math.min(1, dt * 8);
      x += steer * dt * 1.9 * (0.35 + sp / MAXV) - curve(pos) * sp * 2.0 * dt; x = clamp(x, -1.9, 1.9);
      pos += sp * dt; bg -= curve(pos) * sp * dt * 260; time -= dt;
      if (pos >= next) { time += 25; cps++; next += 1500 + cps * 150; blip(988, 0.25, 'triangle'); }
      for (const c of cars) {
        c.z += c.v * dt; const dz = c.z - pos;
        if (dz < -6) { c.z = pos + rnd(180, 260); c.x = rnd(-0.75, 0.75); c.v = rnd(24, 46); }
        if (dz > 0.6 && dz < 2.3 && Math.abs(c.x - x) < 0.42 && sp > c.v && crash <= 0) { sp = c.v * 0.45; crash = 0.9; c.z = pos + 3; blip(110, 0.4, 'sawtooth'); }
      }
      if (time <= 0) { time = 0; game.over = true; blip(220, 0.5, 'triangle'); }
      game.score = Math.floor(pos * 4); game.info = `${Math.ceil(time)} s  ${Math.round(sp * 3.6)} km/u`;
    },
    draw(g) {
      sky(g, W, HOR, '#1b1150', '#ff6a3d');
      g.fillStyle = '#ffcf5a'; g.beginPath(); g.arc(W / 2 + ((bg * 0.2) % W), HOR - 6, 26, Math.PI, 0); g.fill();
      for (let layer = 0; layer < 2; layer++) {
        g.fillStyle = layer ? '#2a1650' : '#3d2370'; g.beginPath(); g.moveTo(0, HOR);
        const sh = bg * (layer ? 0.5 : 0.25);
        for (let px = 0; px <= W; px += 12) { const u = (px - sh) / (layer ? 60 : 90); g.lineTo(px, HOR - (layer ? 14 : 26) - Math.abs(Math.sin(u)) * (layer ? 18 : 22) - Math.abs(Math.sin(u * 0.37)) * 12); }
        g.lineTo(W, HOR); g.fill();
      }
      zs.length = 0; xs.length = 0; let X = 0, dx = 0, pz = 0;
      for (let y = H - 1; y > HOR; y--) {
        const z = D / (y - HOR); const dz = z - pz; pz = z; dx += curve(pos + z) * dz; X += dx * dz; zs.push(z); xs.push(X);
        const sc = D / z, cxp = W / 2 + (X - x) * sc, hw = sc; const band = Math.floor((pos + z) / 3) % 2;
        g.fillStyle = band ? '#0f3d2a' : '#124a33'; g.fillRect(0, y, W, 1);
        g.fillStyle = band ? '#FF7A24' : '#ffffff'; g.fillRect(cxp - hw * 1.14, y, hw * 2.28, 1);
        g.fillStyle = band ? '#262d47' : '#2c3452'; g.fillRect(cxp - hw, y, hw * 2, 1);
        if (band) { g.fillStyle = '#e8eefc'; g.fillRect(cxp - hw * 0.025, y, hw * 0.05, 1); }
      }
      const xAt = (z: number) => { for (let i = 0; i < zs.length; i++) if (zs[i] >= z) return xs[i]; return xs[xs.length - 1] ?? 0; };
      [...cars].sort((a, b) => b.z - a.z).forEach((c) => {
        const dz = c.z - pos; if (dz < 1.1 || dz > 210) return;
        const sc = D / dz, sy = HOR + sc, sx = W / 2 + (xAt(dz) + c.x - x) * sc, cw = 0.5 * sc, ch = 0.3 * sc;
        g.fillStyle = '#00000055'; g.fillRect(sx - cw / 2, sy - ch * 0.12, cw, ch * 0.15);
        g.fillStyle = c.col; g.fillRect(sx - cw / 2, sy - ch, cw, ch * 0.9); g.fillStyle = '#0b1130'; g.fillRect(sx - cw * 0.35, sy - ch * 1.25, cw * 0.7, ch * 0.4);
        g.fillStyle = '#ff3b4e'; g.fillRect(sx - cw / 2, sy - ch * 0.55, cw * 0.15, ch * 0.12); g.fillRect(sx + cw * 0.35, sy - ch * 0.55, cw * 0.15, ch * 0.12);
      });
      const bob = crash > 0 ? Math.sin(crash * 40) * 4 : 0; const cx = W / 2 + bob, cy = H - 26, tilt = steer * 6;
      g.fillStyle = '#00000066'; g.fillRect(cx - 46, cy + 14, 92, 8);
      g.fillStyle = '#FF4DB8'; g.beginPath(); g.moveTo(cx - 44, cy + 14); g.lineTo(cx - 40 - tilt, cy - 6); g.lineTo(cx + 40 - tilt, cy - 6); g.lineTo(cx + 44, cy + 14); g.closePath(); g.fill();
      g.fillStyle = '#20D9FF'; g.fillRect(cx - 28 - tilt, cy - 20, 56, 15); g.fillStyle = '#0b1130'; g.fillRect(cx - 24 - tilt, cy - 17, 48, 10);
      g.fillStyle = '#ff3b4e'; g.fillRect(cx - 40, cy, 14, 5); g.fillRect(cx + 26, cy, 14, 5);
      hud(g, W, `${game.score} m`, game.info);
      if (crash > 0) { g.fillStyle = `rgba(255,60,60,${crash * 0.25})`; g.fillRect(0, 0, W, H); }
      if (pos < 60) { g.fillStyle = '#ffffffdd'; g.font = 'bold 16px system-ui'; g.textAlign = 'center'; g.fillText('Gas gaat vanzelf · ◀ ▶ sturen · ▼ remmen', W / 2, 60); }
    },
  };
  return game;
}

/* =================== 8. AIRHOCKEY tegen de computer =================== */
function airHockey(): Game {
  const W = 300, H = 480, GW = 104, MR = 22, PR = 12; let me = 0, cpu = 0, pause = 0.6, tt = 0;
  const p = { x: W / 2, y: H - 70, vx: 0, vy: 0 }, c = { x: W / 2, y: 70, vx: 0, vy: 0 }, puck = { x: W / 2, y: H / 2 + 60, vx: 0, vy: 0 };
  const reset = (toMe: boolean) => { puck.x = W / 2; puck.y = H / 2 + (toMe ? 60 : -60); puck.vx = puck.vy = 0; pause = 0.7; };
  const hit = (m: { x: number; y: number; vx: number; vy: number }) => {
    const dx = puck.x - m.x, dy = puck.y - m.y, d = Math.hypot(dx, dy); if (d >= MR + PR || d === 0) return;
    const nx = dx / d, ny = dy / d; puck.x = m.x + nx * (MR + PR + 0.5); puck.y = m.y + ny * (MR + PR + 0.5);
    const rv = (puck.vx - m.vx) * nx + (puck.vy - m.vy) * ny; if (rv < 0) { puck.vx -= 1.9 * rv * nx; puck.vy -= 1.9 * rv * ny; blip(300, 0.04); }
    const s = Math.hypot(puck.vx, puck.vy); if (s > 950) { puck.vx *= 950 / s; puck.vy *= 950 / s; }
  };
  const move = (m: typeof p, tx: number, ty: number, maxV: number, dt: number, y0: number, y1: number) => {
    const ox = m.x, oy = m.y; const dx = tx - m.x, dy = ty - m.y, d = Math.hypot(dx, dy); const st = Math.min(d, maxV * dt);
    if (d > 0) { m.x += (dx / d) * st; m.y += (dy / d) * st; }
    m.x = clamp(m.x, 12 + MR, W - 12 - MR); m.y = clamp(m.y, y0, y1); m.vx = (m.x - ox) / Math.max(dt, 1e-3); m.vy = (m.y - oy) / Math.max(dt, 1e-3);
  };
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      // jij: muis/vinger of pijltjes
      const tx = k.px ?? p.x + ((k.r ? 1 : 0) - (k.l ? 1 : 0)) * 60, ty = k.py ?? p.y + ((k.d ? 1 : 0) - (k.u ? 1 : 0)) * 60;
      move(p, tx, ty, 1100, dt, H / 2 + MR, H - 12 - MR);
      // computer: verdedigen, en aanvallen als de puck aan zijn kant is
      tt += dt; const lvl = Math.min(1, (me + cpu) / 10); let aim: { x: number; y: number };
      if (puck.y < H / 2 - 16) {
        if (c.y > puck.y - 6) aim = { x: puck.x + (c.x < puck.x ? -1 : 1) * (MR + PR + 12), y: puck.y - MR }; // eerst om de puck heen
        else { const dx = puck.x - W / 2, dy = puck.y - H, dl = Math.hypot(dx, dy) || 1; aim = { x: puck.x + (dx / dl) * (MR + PR - 6), y: puck.y + (dy / dl) * (MR + PR - 6) }; } // richting jouw doel
      } else aim = { x: W / 2 + (puck.x - W / 2) * 0.4, y: 74 };
      move(c, aim.x + Math.sin(tt * 1.7) * 9, aim.y, 360 + lvl * 200, dt, 12 + MR, H / 2 - MR);
      if (pause > 0) { pause -= dt; return; }
      const n = 3;
      for (let s = 0; s < n; s++) {
        puck.x += (puck.vx * dt) / n; puck.y += (puck.vy * dt) / n;
        if (puck.x < 12 + PR) { puck.x = 12 + PR; puck.vx = Math.abs(puck.vx) * 0.92; blip(220, 0.03); }
        if (puck.x > W - 12 - PR) { puck.x = W - 12 - PR; puck.vx = -Math.abs(puck.vx) * 0.92; blip(220, 0.03); }
        const inGoal = Math.abs(puck.x - W / 2) < GW / 2 - 4;
        if (puck.y < 12 + PR && !inGoal) { puck.y = 12 + PR; puck.vy = Math.abs(puck.vy) * 0.92; blip(220, 0.03); }
        if (puck.y > H - 12 - PR && !inGoal) { puck.y = H - 12 - PR; puck.vy = -Math.abs(puck.vy) * 0.92; blip(220, 0.03); }
        if (puck.y < -PR) { me++; game.score += 100; blip(1046, 0.25, 'triangle'); reset(false); break; }
        if (puck.y > H + PR) { cpu++; blip(180, 0.3, 'sawtooth'); reset(true); break; }
        hit(p); hit(c);
        // klem tussen twee slagers: de puck schiet opzij weg
        if (Math.hypot(puck.x - p.x, puck.y - p.y) < MR + PR - 1 && Math.hypot(puck.x - c.x, puck.y - c.y) < MR + PR - 1) { const sd = puck.x < W / 2 ? 1 : puck.x > W / 2 ? -1 : Math.random() < 0.5 ? -1 : 1; puck.vx = sd * 420; puck.x += sd * 6; }
      }
      const f = Math.pow(0.55, dt); puck.vx *= f; puck.vy *= f;
      if (me >= 7 || cpu >= 7) { if (me >= 7) game.score += 500; game.over = true; }
      game.info = `jij ${me} - ${cpu} computer`;
    },
    draw(g) {
      g.fillStyle = '#e9f1ff'; g.fillRect(0, 0, W, H);
      g.fillStyle = '#d6e4ff'; for (let y = 20; y < H; y += 16) for (let x = 20; x < W; x += 16) g.fillRect(x, y, 2, 2);
      g.strokeStyle = '#FF4DB8'; g.lineWidth = 3; g.beginPath(); g.moveTo(12, H / 2); g.lineTo(W - 12, H / 2); g.stroke(); g.beginPath(); g.arc(W / 2, H / 2, 46, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = '#398CFF55'; g.beginPath(); g.arc(W / 2, 12, 60, 0, Math.PI); g.stroke(); g.beginPath(); g.arc(W / 2, H - 12, 60, Math.PI, 0); g.stroke();
      glow(g, '#20D9FF', 12); g.fillStyle = '#20D9FF'; g.fillRect(0, 0, W, 12); g.fillRect(0, H - 12, W, 12); g.fillRect(0, 0, 12, H); g.fillRect(W - 12, 0, 12, H); noGlow(g);
      g.fillStyle = '#0b1130'; g.fillRect(W / 2 - GW / 2, 0, GW, 12); g.fillRect(W / 2 - GW / 2, H - 12, GW, 12);
      g.fillStyle = '#1c1f2e'; g.beginPath(); g.arc(puck.x, puck.y, PR, 0, Math.PI * 2); g.fill();
      for (const [m, col] of [[c, '#FF3B4E'], [p, '#398CFF']] as const) { g.fillStyle = col; g.beginPath(); g.arc(m.x, m.y, MR, 0, Math.PI * 2); g.fill(); g.fillStyle = '#ffffff55'; g.beginPath(); g.arc(m.x, m.y, MR * 0.45, 0, Math.PI * 2); g.fill(); }
      g.font = 'bold 40px system-ui'; g.textAlign = 'center'; g.fillStyle = '#0b113022'; g.fillText(String(cpu), W / 2, H / 2 - 70); g.fillText(String(me), W / 2, H / 2 + 100);
      hud(g, W, '', '', '#0b1130');
    },
  };
  return game;
}

/* =================== 9. GRIJPMACHINE: grijp een knuffel van de cast =================== */
const KNUFFELS = [
  { naam: 'hoofdpersonage', col: '#FF7A24' }, { naam: 'dino van broertje', col: '#4ADE80' }, { naam: 'opa’s vis', col: '#20D9FF' },
  { naam: 'oma’s taart', col: '#FFD0A6' }, { naam: 'papa’s mok', col: '#398CFF' }, { naam: 'mama’s wekker', col: '#FF4DB8' },
  { naam: 'kraai', col: '#2b3150' }, { naam: 'ster', col: '#FACC15' }, { naam: 'pestkop', col: '#A855F7' }, { naam: 'beste vriend', col: '#FF3B4E' },
];
function claw(): Game {
  const W = 300, H = 420, FLOOR = 380, TOP = 64, CH = 70; let tries = 5, timer = 15, msg = '', msgT = 0;
  type K = { x: number; y: number; r: number; k: number; vy: number };
  const pile: K[] = Array.from({ length: 11 }, (_, i) => ({ x: rnd(100, 268), y: 0, r: rnd(17, 21), k: i % KNUFFELS.length, vy: 0 }));
  pile.sort((a, b) => a.x - b.x).forEach((p, i) => { p.y = FLOOR - p.r - (i % 3) * 16; });
  const cl = { x: 190, y: TOP, st: 'move' as 'move' | 'drop' | 'close' | 'lift' | 'carry' | 'open' | 'back', t: 0, held: null as K | null, grip: 0 };
  const won: number[] = [];
  const game: Game = {
    w: W, h: H, score: 0, over: false, info: '',
    step(dt, k) {
      msgT -= dt;
      if (cl.st === 'move') {
        timer -= dt;
        if (k.px !== null) cl.x += clamp(k.px - cl.x, -200 * dt, 200 * dt); else cl.x += ((k.r ? 1 : 0) - (k.l ? 1 : 0)) * 160 * dt;
        cl.x = clamp(cl.x, 98, W - 30);
        if (k.aHit || k.dHit || (k.pHit && k.py !== null && k.py > 300) || timer <= 0) { cl.st = 'drop'; blip(330, 0.1, 'triangle'); }
      } else if (cl.st === 'drop') {
        cl.y += 170 * dt; const under = pile.filter((p) => Math.abs(p.x - cl.x) < p.r + 6).map((p) => p.y - p.r - 18);
        const stop = Math.min(FLOOR - 26, ...under.map((u) => u + 10));
        if (cl.y >= stop) { cl.y = stop; cl.st = 'close'; cl.t = 0.45; }
      } else if (cl.st === 'close') {
        cl.t -= dt;
        if (cl.t <= 0) {
          let best: K | null = null; let bd = 26;
          for (const p of pile) { const d = Math.abs(p.x - cl.x); if (d < bd && Math.abs(p.y - (cl.y + 22)) < p.r + 16) { bd = d; best = p; } }
          if (best) { cl.held = best; cl.grip = 1 - bd / 26; blip(520, 0.06); }
          cl.st = 'lift';
        }
      } else if (cl.st === 'lift') {
        cl.y -= 120 * dt;
        if (cl.held && Math.random() < dt * (1.45 - cl.grip * 1.3)) { cl.held.vy = 0; cl.held = null; blip(200, 0.15, 'triangle'); msg = 'Net niet!'; msgT = 1.2; }
        if (cl.y <= TOP) { cl.y = TOP; cl.st = 'carry'; }
      } else if (cl.st === 'carry') {
        cl.x -= 130 * dt; if (cl.x <= 50) { cl.x = 50; cl.st = 'open'; cl.t = 0.5; }
      } else if (cl.st === 'open') {
        cl.t -= dt;
        if (cl.held) { const p = cl.held; cl.held = null; pile.splice(pile.indexOf(p), 1); won.push(p.k); game.score += 100; blip(880, 0.12, 'triangle'); setTimeout(() => blip(1175, 0.18, 'triangle'), 120); msg = `Gewonnen: ${KNUFFELS[p.k].naam}!`; msgT = 2; }
        if (cl.t <= 0) cl.st = 'back';
      } else if (cl.st === 'back') {
        cl.x += 160 * dt; if (cl.x >= 190) { cl.x = 190; tries--; timer = 15; cl.st = 'move'; if (tries <= 0 || !pile.length) game.over = true; }
      }
      if (cl.held) { cl.held.x = cl.x; cl.held.y = cl.y + 22 + cl.held.r * 0.6; }
      for (const p of pile) { if (p === cl.held) continue; const rest = FLOOR - p.r; if (p.y < rest - 0.5) { p.vy += 900 * dt; p.y = Math.min(rest, p.y + p.vy * dt); if (p.y >= rest) p.vy = 0; } }
      game.info = `${tries} ${tries === 1 ? 'poging' : 'pogingen'}${cl.st === 'move' ? ` · ${Math.ceil(timer)} s` : ''}`;
    },
    draw(g) {
      sky(g, W, H, '#2a1240', '#14102a');
      g.fillStyle = '#ffffff10'; g.fillRect(14, 40, W - 28, FLOOR - 40);
      g.fillStyle = '#3a1d55'; g.fillRect(14, FLOOR, W - 28, H - FLOOR);
      g.fillStyle = '#0b0718'; g.fillRect(16, FLOOR - 60, 66, 60); glow(g, '#FACC15', 10); g.fillStyle = '#FACC15'; g.fillRect(16, FLOOR - 62, 66, 3); noGlow(g);
      g.fillStyle = '#FACC15'; g.font = 'bold 11px system-ui'; g.textAlign = 'center'; g.fillText('PRIJS', 49, FLOOR - 30);
      for (const p of pile) {
        const K = KNUFFELS[p.k]; g.fillStyle = K.col; g.beginPath(); g.arc(p.x, p.y, p.r, 0, Math.PI * 2); g.fill();
        g.beginPath(); g.arc(p.x - p.r * 0.6, p.y - p.r * 0.75, p.r * 0.32, 0, Math.PI * 2); g.arc(p.x + p.r * 0.6, p.y - p.r * 0.75, p.r * 0.32, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#ffffff'; g.beginPath(); g.arc(p.x - p.r * 0.32, p.y - p.r * 0.1, p.r * 0.2, 0, Math.PI * 2); g.arc(p.x + p.r * 0.32, p.y - p.r * 0.1, p.r * 0.2, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#111'; g.beginPath(); g.arc(p.x - p.r * 0.3, p.y - p.r * 0.06, p.r * 0.1, 0, Math.PI * 2); g.arc(p.x + p.r * 0.34, p.y - p.r * 0.06, p.r * 0.1, 0, Math.PI * 2); g.fill();
        g.strokeStyle = '#111'; g.lineWidth = 1.5; g.beginPath(); g.arc(p.x, p.y + p.r * 0.2, p.r * 0.22, 0.2, Math.PI - 0.2); g.stroke();
      }
      g.fillStyle = '#c9d1e0'; g.fillRect(14, 36, W - 28, 6); g.fillRect(cl.x - 1.5, 40, 3, cl.y - 40);
      const open = cl.st === 'move' || cl.st === 'drop' || (cl.st === 'open' && cl.t < 0.35) || cl.st === 'back' ? 1 : 0.25;
      g.fillStyle = '#e5e7eb'; rrect(g, cl.x - 12, cl.y, 24, 12, 3); g.strokeStyle = '#e5e7eb'; g.lineWidth = 4; g.lineCap = 'round';
      for (const s of [-1, 1]) { g.beginPath(); g.moveTo(cl.x + s * 9, cl.y + 10); g.lineTo(cl.x + s * (9 + 12 * open), cl.y + 26); g.lineTo(cl.x + s * (4 + 8 * open), cl.y + 38); g.stroke(); }
      g.lineCap = 'butt';
      glow(g, '#FF4DB8', 14); g.fillStyle = '#FF4DB8'; g.fillRect(0, 0, W, 34); g.fillRect(0, 0, 14, H); g.fillRect(W - 14, 0, 14, H); noGlow(g);
      g.fillStyle = '#ffffff'; g.font = 'bold 15px ui-monospace, monospace'; g.textAlign = 'left'; g.fillText(`${game.score}`, 20, 23); g.textAlign = 'right'; g.fillText(game.info, W - 20, 23);
      if (won.length) won.forEach((k, i) => { g.fillStyle = KNUFFELS[k].col; g.beginPath(); g.arc(28 + i * 16, H - 16, 6, 0, Math.PI * 2); g.fill(); });
      if (msgT > 0 && msg) { g.fillStyle = '#000000aa'; g.fillRect(30, 160, W - 60, 40); g.fillStyle = '#FACC15'; g.font = 'bold 15px system-ui'; g.textAlign = 'center'; g.fillText(msg, W / 2, 186); }
      if (cl.st === 'move' && tries === 5 && timer > 13.5) { g.fillStyle = '#ffffffcc'; g.font = '13px system-ui'; g.textAlign = 'center'; g.fillText('◀ ▶ bewegen · spatie of ▼: grijpen', W / 2, 140); }
    },
  };
  return game;
}

export const GAMES: Record<GameId, GameDef> = {
  break: { naam: 'NEON BREAK', kleur: '#20D9FF', uitleg: 'Kaats alle neonstenen kapot. ◀ ▶ of de muis beweegt het plankje, spatie schiet de bal af.', knoppen: ['l', 'r', 'a'], make: neonBreak },
  hop: { naam: 'SKY HOP', kleur: '#4ADE80', uitleg: 'Spring zo hoog mogelijk over de wolken. Roze wolkjes breken. ◀ ▶ of de muis stuurt.', knoppen: ['l', 'r'], make: skyHop },
  orbit: { naam: 'ORBIT RUN', kleur: '#A855F7', uitleg: 'Draai rond de planeet. ▲ of spatie: baan naar buiten, ▼: naar binnen. Pak sterren, ontwijk stenen.', knoppen: ['d', 'u'], make: orbitRun },
  dash: { naam: 'DRIFT DASH', kleur: '#FF3B4E', uitleg: 'Ontwijk kegels en auto’s en pak de munten. ◀ ▶ of de muis stuurt.', knoppen: ['l', 'r'], make: driftDash },
  comet: { naam: 'COMET CATCH', kleur: '#FACC15', uitleg: 'Vang sterren in je mandje, ontwijk de meteorieten. Hartjes geven een leven.', knoppen: ['l', 'r'], make: cometCatch },
  snail: { naam: 'SNAIL RUN', kleur: '#FF7A24', uitleg: 'Het hoofdpersonage rent door de stad. Spatie of ▲ springt (langer drukken = hoger), ▼ bukt.', knoppen: ['d', 'u'], make: snailRun },
  gp: { naam: 'DRIFT GP', kleur: '#FF7A24', uitleg: 'Race door de bochten en haal het verkeer in. Elke finishboog geeft extra tijd. ◀ ▶ sturen, ▼ remmen.', knoppen: ['l', 'd', 'r'], make: driftGp },
  hockey: { naam: 'AIRHOCKEY', kleur: '#20D9FF', uitleg: 'Tegen de computer, wie het eerst 7 heeft. Beweeg je blauwe slager met de muis, je vinger of de pijltjes.', knoppen: ['l', 'u', 'd', 'r'], make: airHockey },
  claw: { naam: 'GRIJPMACHINE', kleur: '#FF4DB8', uitleg: 'Vijf pogingen om een knuffel van de cast te grijpen. ◀ ▶ bewegen, spatie of ▼ grijpt.', knoppen: ['l', 'r', 'a'], make: claw },
};
