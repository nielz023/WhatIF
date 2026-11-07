/**
 * DE BOVENVERDIEPING (niels 2026-11-07): kantine met koffiezetapparaten, keukentje en tafels; gamekamer met
 * gamekasten, racesimulators (stoel, stuur, pedalen, scherm) en een bank met een grote tv; een lounge met
 * pingpong en tafelvoetbal; een aquarium-hoek; planten en spullen, maar rustig gehouden.
 *
 * Alles wat stilstaat wordt per materiaal samengevoegd tot één geometrie met vertexkleuren (een handvol
 * tekenopdrachten voor de hele verdieping). Alleen de schermen, de vissen en de pingpongbal zijn losse meshes.
 * De indeling (en de plekken voor de medewerkers) staat in upstairs.ts; de vloer ligt op Y1 (floors.ts).
 * Spellen op de schermen zijn eigen, verzonnen spellen (geen bestaande games).
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { mergeBufferGeometries } from 'three-stdlib';
import { Y1, SLAB, UP_R, useFloor } from './floors';
import { VIDE_R, RAIL_R, HOLE, K, G, L, PLANTS, occupied } from './upstairs';
import { reducedMotion } from './useWorld';

type V2 = [number, number];
type V3 = [number, number, number];
type MatKey = 'std' | 'gloss' | 'soft' | 'leaf' | 'neon' | 'glass';

/* =================== bouwdoos: alles samenvoegen per materiaal =================== */
class Kit {
  parts: Record<MatKey, THREE.BufferGeometry[]> = { std: [], gloss: [], soft: [], leaf: [], neon: [], glass: [] };
  frame = new THREE.Matrix4();
  private m = new THREE.Matrix4(); private e = new THREE.Euler(); private q = new THREE.Quaternion(); private c = new THREE.Color();
  /** plek en draaiing voor de volgende onderdelen (lokaal: +z = voorkant) */
  at(x = 0, z = 0, ry = 0, y = 0) { this.frame.makeRotationY(ry).setPosition(x, y, z); return this; }
  add(g: THREE.BufferGeometry, p: V3, col: string, mat: MatKey, rot: V3 = [0, 0, 0], sc: V3 = [1, 1, 1], glow = 1) {
    this.e.set(rot[0], rot[1], rot[2]); this.q.setFromEuler(this.e);
    this.m.compose(new THREE.Vector3(...p), this.q, new THREE.Vector3(...sc)).premultiply(this.frame);
    const geo = (g.index ? g.toNonIndexed() : g); geo.applyMatrix4(this.m);
    for (const k of Object.keys(geo.attributes)) if (k !== 'position' && k !== 'normal') geo.deleteAttribute(k);
    this.c.set(col); const n = geo.getAttribute('position').count; const arr = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { arr[i * 3] = this.c.r * glow; arr[i * 3 + 1] = this.c.g * glow; arr[i * 3 + 2] = this.c.b * glow; }
    geo.setAttribute('color', new THREE.BufferAttribute(arr, 3));
    this.parts[mat].push(geo); return this;
  }
  box(p: V3, s: V3, col: string, mat: MatKey = 'std', rot?: V3) { return this.add(new THREE.BoxGeometry(...s), p, col, mat, rot); }
  cyl(p: V3, r: number, h: number, col: string, mat: MatKey = 'std', seg = 18, r2?: number, rot?: V3) { return this.add(new THREE.CylinderGeometry(r, r2 ?? r, h, seg), p, col, mat, rot); }
  sph(p: V3, r: number, col: string, mat: MatKey = 'std', sc?: V3, rot?: V3, detail = 1) { return this.add(new THREE.IcosahedronGeometry(r, detail), p, col, mat, rot, sc); }
  tor(p: V3, R: number, r: number, col: string, mat: MatKey = 'std', rot?: V3, arc = Math.PI * 2) { return this.add(new THREE.TorusGeometry(R, r, 8, 28, arc), p, col, mat, rot); }
  neon(p: V3, s: V3, col: string, glow = 2.6, rot?: V3) { return this.add(new THREE.BoxGeometry(...s), p, col, 'neon', rot, undefined, glow); }
  build() {
    const out = {} as Record<MatKey, THREE.BufferGeometry | null>;
    (Object.keys(this.parts) as MatKey[]).forEach((k) => { out[k] = this.parts[k].length ? mergeBufferGeometries(this.parts[k], false) : null; this.parts[k].forEach((g) => g.dispose()); });
    return out;
  }
}

/* =================== schermen (canvas) =================== */
function canvas(w: number, h: number) { const c = document.createElement('canvas'); c.width = w; c.height = h; return { c, g: c.getContext('2d')! }; }
function tex(c: HTMLCanvasElement) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }
function sign(text: string, col: string, w = 512, h = 128) {
  const { c, g } = canvas(w, h);
  g.font = `900 ${Math.round(h * 0.56)}px "Space Grotesk", system-ui, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.shadowColor = col; g.shadowBlur = h * 0.22; g.fillStyle = col; g.fillText(text, w / 2, h / 2 + 2);
  g.shadowBlur = h * 0.06; g.fillStyle = '#ffffff'; g.globalAlpha = 0.85; g.fillText(text, w / 2, h / 2 + 2);
  return tex(c);
}
/** racespel "DRIFT GP": weg met strepen die naar je toe komen */
function drawRace(g: CanvasRenderingContext2D, w: number, h: number, t: number) {
  const sky = g.createLinearGradient(0, 0, 0, h * 0.5); sky.addColorStop(0, '#1b1150'); sky.addColorStop(1, '#ff6a3d');
  g.fillStyle = sky; g.fillRect(0, 0, w, h * 0.5);
  g.fillStyle = '#ffcf5a'; g.beginPath(); g.arc(w * 0.5, h * 0.47, h * 0.16, Math.PI, 0); g.fill();
  g.fillStyle = '#2a1650'; g.beginPath(); g.moveTo(0, h * 0.5);
  for (let x = 0; x <= w; x += w / 8) g.lineTo(x, h * (0.5 - 0.08 - 0.06 * Math.abs(Math.sin(x * 0.03 + 1.3))));
  g.lineTo(w, h * 0.5); g.fill();
  g.fillStyle = '#0d1a3a'; g.fillRect(0, h * 0.5, w, h * 0.5);
  const cx = w / 2 + Math.sin(t * 0.7) * w * 0.08;
  g.fillStyle = '#22293f'; g.beginPath(); g.moveTo(w / 2 - 6, h * 0.5); g.lineTo(w / 2 + 6, h * 0.5); g.lineTo(cx + w * 0.55, h); g.lineTo(cx - w * 0.55, h); g.fill();
  for (let k = 0; k < 8; k++) { // strepen
    const f = ((k + (t * 2.2) % 1) / 8); const y = h * 0.5 + f * f * h * 0.5; const s = 1 + f * 9;
    const x = w / 2 + (cx - w / 2) * f;
    g.fillStyle = k % 2 ? '#20D9FF' : '#ffffff'; g.fillRect(x - s * 0.6, y, s * 1.2, s * 1.4);
  }
  for (const sd of [-1, 1]) { g.strokeStyle = '#FF7A24'; g.lineWidth = 2; g.beginPath(); g.moveTo(w / 2 + sd * 6, h * 0.5); g.lineTo(cx + sd * w * 0.55, h); g.stroke(); }
  g.fillStyle = '#FF4DB8'; const cw = w * 0.16; g.fillRect(w / 2 - cw / 2, h * 0.8, cw, h * 0.11); // auto
  g.fillStyle = '#20D9FF'; g.fillRect(w / 2 - cw / 2 + 3, h * 0.76, cw - 6, h * 0.06);
  g.fillStyle = '#ffffff'; g.font = `bold ${Math.round(h * 0.09)}px system-ui`; g.textAlign = 'left'; g.fillText('DRIFT GP', 6, h * 0.1);
  g.textAlign = 'right'; g.fillText(`${Math.floor(180 + Math.sin(t) * 40)} km/h`, w - 6, h * 0.1);
}
/** vier verzonnen arcadespellen */
const ARCADE = [
  { name: 'NEON BLOCKS', a: '#20D9FF', b: '#FF4DB8' },
  { name: 'SKY HOP', a: '#4ADE80', b: '#FACC15' },
  { name: 'ORBIT RUN', a: '#A855F7', b: '#FF7A24' },
  { name: 'DRIFT DASH', a: '#FF3B4E', b: '#20D9FF' },
];
function drawArcade(g: CanvasRenderingContext2D, w: number, h: number, k: number, t: number) {
  const A = ARCADE[k]; g.fillStyle = '#070a1a'; g.fillRect(0, 0, w, h);
  g.fillStyle = A.a; g.font = `bold ${Math.round(w * 0.12)}px system-ui`; g.textAlign = 'center'; g.fillText(A.name, w / 2, h * 0.12);
  if (k === 0) { // vallende blokken
    for (let i = 0; i < 6; i++) for (let j = 0; j < 4; j++) if ((i * 7 + j * 3) % 5 < 3) { g.fillStyle = (i + j) % 2 ? A.a : A.b; g.fillRect(w * 0.15 + i * w * 0.12, h * 0.82 - j * h * 0.07, w * 0.11, h * 0.06); }
    const y = ((t * 0.35) % 1) * h * 0.55 + h * 0.18; g.fillStyle = A.b; g.fillRect(w * 0.45, y, w * 0.24, h * 0.06); g.fillRect(w * 0.45, y + h * 0.06, w * 0.12, h * 0.06);
  } else if (k === 1) { // springende bal op wolkjes
    for (let i = 0; i < 4; i++) { g.fillStyle = '#e8f0ff'; g.fillRect(w * (0.1 + i * 0.22), h * (0.85 - i * 0.16), w * 0.2, h * 0.04); }
    const p = (t * 0.6) % 1; const i = Math.floor(p * 4); const f = p * 4 - i;
    g.fillStyle = A.a; g.beginPath(); g.arc(w * (0.2 + i * 0.22 + f * 0.22), h * (0.8 - i * 0.16 - Math.sin(f * Math.PI) * 0.12 - f * 0.16), w * 0.05, 0, Math.PI * 2); g.fill();
  } else if (k === 2) { // ringen om een planeet
    g.strokeStyle = A.a; g.lineWidth = 2; for (let r = 1; r <= 3; r++) { g.beginPath(); g.ellipse(w / 2, h * 0.55, w * 0.13 * r, h * 0.06 * r, 0, 0, Math.PI * 2); g.stroke(); }
    g.fillStyle = A.b; g.beginPath(); g.arc(w / 2, h * 0.55, w * 0.09, 0, Math.PI * 2); g.fill();
    const a = t * 1.4; g.fillStyle = '#ffffff'; g.beginPath(); g.arc(w / 2 + Math.cos(a) * w * 0.39, h * 0.55 + Math.sin(a) * h * 0.18, w * 0.03, 0, Math.PI * 2); g.fill();
  } else { // auto ontwijkt kegels
    g.fillStyle = '#16203d'; g.fillRect(w * 0.2, h * 0.18, w * 0.6, h * 0.8);
    for (let i = 0; i < 5; i++) { const y = ((t * 0.5 + i * 0.2) % 1) * h * 0.8 + h * 0.18; g.fillStyle = A.b; g.fillRect(w * (0.25 + ((i * 37) % 5) * 0.1), y, w * 0.06, h * 0.04); }
    g.fillStyle = A.a; g.fillRect(w * (0.45 + Math.sin(t * 2) * 0.15), h * 0.84, w * 0.1, h * 0.09);
  }
  g.fillStyle = '#ffffff'; g.font = `${Math.round(w * 0.075)}px monospace`; g.textAlign = 'left'; g.fillText(`${String(Math.floor(t * 37 + k * 1111) % 99999).padStart(5, '0')}`, w * 0.05, h * 0.97);
}
function vendingTex(hue: string) {
  const { c, g } = canvas(128, 256);
  g.fillStyle = '#0b1026'; g.fillRect(0, 0, 128, 256);
  g.fillStyle = hue; g.fillRect(0, 0, 128, 34); g.fillStyle = '#ffffff'; g.font = 'bold 20px system-ui'; g.textAlign = 'center'; g.fillText('SNACKS', 64, 24);
  const cols = ['#FF7A24', '#20D9FF', '#4ADE80', '#FF4DB8', '#FACC15', '#A855F7'];
  for (let r = 0; r < 5; r++) for (let k = 0; k < 4; k++) { g.fillStyle = cols[(r * 4 + k) % cols.length]; g.fillRect(10 + k * 28, 44 + r * 38, 22, 26); g.fillStyle = '#ffffff22'; g.fillRect(10 + k * 28, 70 + r * 38, 22, 3); }
  return tex(c);
}
function tileTex() {
  const { c, g } = canvas(256, 256);
  g.fillStyle = '#151d42'; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = '#26306055'; g.lineWidth = 3; g.strokeRect(1.5, 1.5, 253, 253);
  g.fillStyle = '#ffffff06'; g.fillRect(0, 0, 128, 128); g.fillRect(128, 128, 128, 128);
  const t = tex(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(0.5, 0.5); return t;
}
function woodTex() {
  const { c, g } = canvas(256, 256);
  g.fillStyle = '#6b4530'; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#7a4f36' : '#62402c'; g.fillRect(0, i * 32, 256, 31); g.fillStyle = '#00000030'; g.fillRect(((i * 97) % 200) + 20, i * 32, 2, 31); }
  const t = tex(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}

/* =================== de verdieping opbouwen =================== */
const polar = (r: number, a: number): V2 => [Math.sin(a) * r, Math.cos(a) * r];
const oct = (r: number) => Array.from({ length: 8 }, (_, k) => polar(r, Math.PI / 8 + (k * Math.PI) / 4));

function plant(kit: Kit, x: number, z: number, s: number, kind: number) {
  kit.at(x, z, (x * 7 + z * 3) % 6);
  const potC = ['#eef1f7', '#c96f43', '#1e2746'][kind % 3];
  kit.cyl([0, 0.22 * s, 0], 0.26 * s, 0.44 * s, potC, 'gloss', 20, 0.2 * s);
  kit.cyl([0, 0.43 * s, 0], 0.24 * s, 0.03, '#3a2a20', 'soft', 16);
  const greens = ['#2f9e5b', '#3cb36a', '#25804a', '#4cc27a'];
  if (kind === 0) { // dichte struik
    for (let i = 0; i < 6; i++) { const a = i * 1.05, r = i ? 0.17 * s : 0; kit.sph([Math.cos(a) * r, (0.7 + (i ? 0.05 : 0.22)) * s, Math.sin(a) * r], (i ? 0.2 : 0.24) * s, greens[i % 4], 'leaf', [1, 0.9, 1], undefined, 0); }
  } else if (kind === 1) { // hoge plant met lange bladeren
    kit.cyl([0, 0.75 * s, 0], 0.025 * s, 0.7 * s, '#4a6b2a', 'leaf', 6);
    for (let i = 0; i < 9; i++) { const a = i * 0.7, up = 0.55 + (i % 3) * 0.22; kit.sph([Math.cos(a) * 0.2 * s, up * s + 0.3 * s, Math.sin(a) * 0.2 * s], 0.2 * s, greens[i % 4], 'leaf', [0.35, 0.12, 1], [0.5, -a + Math.PI / 2, 0], 1); }
  } else { // vioolbladplant
    kit.cyl([0, 0.85 * s, 0], 0.03 * s, 0.9 * s, '#5b4a2e', 'soft', 6);
    for (let i = 0; i < 10; i++) { const a = i * 1.3, y = 0.55 + i * 0.075; kit.sph([Math.cos(a) * 0.14 * s, y * s, Math.sin(a) * 0.14 * s], 0.12 * s, greens[(i + 1) % 4], 'leaf', [1, 0.25, 0.8], [0.3, -a, 0.4], 1); }
  }
}
function chair(kit: Kit, x: number, z: number, ry: number, col: string) {
  kit.at(x, z, ry);
  kit.box([0, 0.45, 0], [0.44, 0.06, 0.42], col, 'soft');
  kit.box([0, 0.72, -0.19], [0.44, 0.48, 0.05], col, 'soft', [-0.08, 0, 0]);
  for (const [lx, lz] of [[-0.18, -0.17], [0.18, -0.17], [-0.18, 0.17], [0.18, 0.17]]) kit.cyl([lx, 0.21, lz], 0.016, 0.42, '#c9d1e0', 'gloss', 6);
}
function sofa(kit: Kit, x: number, z: number, ry: number, col: string, w = 2.2) {
  kit.at(x, z, ry);
  kit.box([0, 0.22, 0], [w, 0.3, 0.9], col, 'soft');
  kit.box([0, 0.55, -0.35], [w, 0.6, 0.2], col, 'soft');
  for (const sx of [-1, 1]) kit.box([sx * (w / 2 - 0.08), 0.4, 0], [0.16, 0.38, 0.9], col, 'soft');
  for (const sx of [-0.5, 0.5]) kit.box([sx * (w - 0.3) / 2, 0.41, 0.03], [(w - 0.34) / 2 - 0.02, 0.1, 0.72], '#e9ecf4', 'soft');
  kit.box([0, 0.05, 0], [w - 0.1, 0.1, 0.8], '#14182b', 'std');
}

function buildFloor() {
  const kit = new Kit();
  const [x0, x1, z0, z1] = [HOLE.x0, HOLE.x1, HOLE.z0, HOLE.z1];
  // ---- balustrade langs de rand (glas met neon) ----
  const rim = oct(UP_R - 0.35 / Math.cos(Math.PI / 8));
  for (let k = 0; k < 8; k++) {
    const [ax, az] = rim[k], [bx, bz] = rim[(k + 1) % 8]; const mx = (ax + bx) / 2, mz = (az + bz) / 2; const len = Math.hypot(bx - ax, bz - az); const ry = Math.atan2(bx - ax, bz - az) + Math.PI / 2;
    kit.at(mx, mz, ry);
    kit.add(new THREE.BoxGeometry(len, 1.0, 0.03), [0, 0.55, 0], '#ffffff', 'glass');
    kit.neon([0, 1.07, 0], [len, 0.045, 0.06], '#FF7A24', 2.4);
    kit.box([0, 0.03, 0], [len, 0.06, 0.12], '#1b2347', 'gloss');
    for (let p = 0; p <= 6; p++) kit.box([-len / 2 + (p * len) / 6, 0.53, 0], [0.04, 1.06, 0.04], '#c9d1e0', 'gloss');
  }
  // ---- gat rond de zuil (vide) met ronde balustrade ----
  kit.at();
  kit.add(new THREE.CylinderGeometry(RAIL_R, RAIL_R, 1.0, 64, 1, true), [0, 0.55, 0], '#ffffff', 'glass');
  kit.add(new THREE.TorusGeometry(RAIL_R, 0.03, 8, 96), [0, 1.07, 0], '#20D9FF', 'neon', [Math.PI / 2, 0, 0], undefined, 2.6);
  kit.add(new THREE.TorusGeometry(RAIL_R, 0.05, 8, 96), [0, 0.04, 0], '#1b2347', 'gloss', [Math.PI / 2, 0, 0]);
  kit.add(new THREE.TorusGeometry(VIDE_R + 0.02, 0.04, 6, 96), [0, -0.02, 0], '#FF7A24', 'neon', [Math.PI / 2, 0, 0], undefined, 2.4);
  // ---- balustrade rond het trapgat (open aan de kant van z0) ----
  const rail = (ax: number, az: number, bx: number, bz: number) => {
    const len = Math.hypot(bx - ax, bz - az); kit.at((ax + bx) / 2, (az + bz) / 2, Math.atan2(bx - ax, bz - az) + Math.PI / 2);
    kit.add(new THREE.BoxGeometry(len, 1.0, 0.03), [0, 0.55, 0], '#ffffff', 'glass'); kit.neon([0, 1.07, 0], [len, 0.04, 0.05], '#20D9FF', 2.4);
  };
  rail(x0 - 0.05, z0, x0 - 0.05, z1 + 0.05); rail(x1 + 0.05, z0, x1 + 0.05, z1 + 0.05); rail(x0 - 0.05, z1 + 0.05, x1 + 0.05, z1 + 0.05);
  kit.at(); kit.neon([(x0 + x1) / 2, 0.012, z0 - 0.04], [x1 - x0, 0.02, 0.05], '#20D9FF', 2.6); // lichtstreep op de rand van de bovenste trede

  // ---- KANTINE ----
  kit.at();
  kit.box([K.wall.c[0], 1.4, 0], [K.wall.w, 2.8, K.wall.d], '#1b2347', 'std');
  kit.neon([K.wall.c[0] - 0.11, 2.78, 0], [0.04, 0.05, K.wall.d], '#FF7A24', 2.6);
  kit.neon([K.wall.c[0] - 0.11, 0.08, 0], [0.04, 0.04, K.wall.d], '#FF7A24', 2.2);
  const [cx, cz] = K.counter.c; const cd = K.counter.d;
  kit.box([cx, 0.44, cz], [K.counter.w, 0.88, cd], '#eef1f7', 'std'); // kastjes
  for (let i = 0; i < 8; i++) kit.box([cx - K.counter.w / 2 - 0.005, 0.45, cz - cd / 2 + (i + 0.5) * (cd / 8)], [0.01, 0.7, cd / 8 - 0.04], '#d4d9e6', 'std');
  kit.box([cx, 0.9, cz], [K.counter.w + 0.04, 0.05, cd + 0.04], '#232a40', 'gloss'); // werkblad
  kit.box([cx + 0.22, 1.85, cz], [0.36, 0.65, cd], '#eef1f7', 'std'); // bovenkastjes
  kit.neon([cx + 0.03, 1.51, cz], [0.02, 0.02, cd], '#FFE2C4', 2.2); // werklicht onder de kastjes
  K.coffeeZ.forEach((z) => { // koffiezetapparaten
    kit.at(cx + 0.05, z, -Math.PI / 2);
    kit.box([0, 1.18, 0], [0.32, 0.5, 0.38], '#1c2135', 'gloss'); kit.box([0, 1.33, 0.2], [0.26, 0.16, 0.03], '#c9d1e0', 'gloss');
    kit.neon([0, 1.36, 0.215], [0.12, 0.05, 0.01], '#4ADE80', 2); kit.box([0, 0.98, 0.1], [0.3, 0.04, 0.2], '#2b3150', 'gloss');
    kit.cyl([0, 1.05, 0.12], 0.04, 0.09, '#ffffff', 'gloss', 10); kit.box([0, 1.12, 0.12], [0.05, 0.05, 0.05], '#c9d1e0', 'gloss');
  });
  kit.at(cx - 0.05, K.sinkZ, -Math.PI / 2); // spoelbak en kraan
  kit.box([0, 0.9, 0], [0.55, 0.06, 0.4], '#9aa5bd', 'gloss'); kit.cyl([0, 1.1, -0.15], 0.018, 0.35, '#c9d1e0', 'gloss', 8);
  kit.tor([0, 1.27, -0.07], 0.08, 0.016, '#c9d1e0', 'gloss', [0, Math.PI / 2, 0], Math.PI);
  kit.at(cx + 0.05, K.microZ, -Math.PI / 2); // magnetron
  kit.box([0, 1.1, 0], [0.52, 0.32, 0.38], '#eef1f7', 'std'); kit.box([-0.06, 1.1, 0.195], [0.34, 0.22, 0.01], '#0d1120', 'gloss'); kit.neon([0.18, 1.18, 0.196], [0.06, 0.03, 0.01], '#20D9FF', 2);
  kit.at(cx - 0.6, 0.6, 0); kit.cyl([0, 0.955, 0], 0.16, 0.06, '#eef1f7', 'gloss', 16); // fruitschaal
  ['#FF7A24', '#FACC15', '#4ADE80', '#FF3B4E'].forEach((c, i) => kit.sph([Math.cos(i * 1.6) * 0.07, 1.02, Math.sin(i * 1.6) * 0.07], 0.05, c, 'gloss', undefined, undefined, 1));
  kit.at(K.fridge.c[0], K.fridge.c[1]); kit.box([0, 1.0, 0], [K.fridge.w, 2.0, K.fridge.d], '#d7dce8', 'gloss'); kit.box([-0.4, 1.0, 0], [0.01, 1.96, 0.76], '#b9c0d1', 'gloss');
  kit.box([-0.41, 1.25, 0.28], [0.03, 0.5, 0.03], '#7d879e', 'gloss'); kit.box([-0.41, 0.5, 0.28], [0.03, 0.3, 0.03], '#7d879e', 'gloss');
  kit.at(K.cooler.c[0], K.cooler.c[1]); kit.box([0, 0.5, 0], [0.4, 1.0, 0.4], '#eef1f7', 'std'); kit.cyl([0, 1.22, 0], 0.15, 0.42, '#7fd3ff', 'glass', 18);
  // eiland met krukken
  kit.at(K.island.c[0], K.island.c[1]);
  kit.box([0, 0.48, 0], [K.island.w - 0.1, 0.96, K.island.d - 0.1], '#2a1c40', 'std'); kit.box([0, 1.0, 0], [K.island.w + 0.1, 0.06, K.island.d + 0.1], '#eef1f7', 'gloss');
  kit.neon([-K.island.w / 2 + 0.04, 0.08, 0], [0.03, 0.04, K.island.d - 0.1], '#FF7A24', 2.4);
  K.stoolsZ.forEach((z) => { kit.at(K.stoolX, z); kit.cyl([0, 0.73, 0], 0.19, 0.07, '#FF7A24', 'soft', 18); kit.cyl([0, 0.36, 0], 0.03, 0.72, '#c9d1e0', 'gloss', 8); kit.tor([0, 0.3, 0], 0.15, 0.012, '#c9d1e0', 'gloss', [Math.PI / 2, 0, 0]); kit.cyl([0, 0.01, 0], 0.18, 0.02, '#c9d1e0', 'gloss', 16); });
  [[11.0, -0.9], [11.15, 0.6]].forEach(([x, z], i) => { kit.at(x, z); kit.cyl([0, 1.08, 0], 0.045, 0.1, i ? '#FF7A24' : '#ffffff', 'gloss', 10); }); // bekers op het eiland
  // tafels met stoelen
  const chairCols = ['#20D9FF', '#FF7A24', '#A855F7', '#4ADE80'];
  K.tables.forEach(([tx, tz], t) => {
    kit.at(tx, tz); kit.cyl([0, 0.74, 0], 0.58, 0.04, '#eef1f7', 'gloss', 32); kit.cyl([0, 0.37, 0], 0.05, 0.72, '#c9d1e0', 'gloss', 10); kit.cyl([0, 0.015, 0], 0.3, 0.03, '#c9d1e0', 'gloss', 20);
    kit.cyl([0.12, 0.83, -0.08], 0.05, 0.14, '#ffffff', 'glass', 10); kit.sph([0.12, 0.93, -0.08], 0.07, '#4cc27a', 'leaf', undefined, undefined, 0);
    [[0.82, 0, -Math.PI / 2], [-0.82, 0, Math.PI / 2], [0, 0.82, Math.PI], [0, -0.82, 0]].forEach(([ox, oz, ry]) => chair(kit, tx + ox, tz + oz, ry, chairCols[t]));
    kit.at(tx, tz); kit.add(new THREE.CircleGeometry(1.55, 40), [0, 0.006, 0], ['#2a2040', '#1f2a46', '#2a2040', '#1f2a46'][t], 'soft', [-Math.PI / 2, 0, 0]);
  });

  // ---- GAMEKAMER ----
  kit.at();
  kit.box([G.wall.c[0], 1.4, 0], [G.wall.w, 2.8, G.wall.d], '#140f2e', 'std');
  for (let i = 0; i < 4; i++) kit.neon([G.wall.c[0] + 0.11, 0.6 + i * 0.6, 0], [0.03, 0.03, G.wall.d - 0.4], i % 2 ? '#A855F7' : '#20D9FF', 2.4);
  G.glass.forEach((w) => {
    kit.at(w.c[0], w.c[1]); kit.add(new THREE.BoxGeometry(0.03, 2.2, w.d), [0, 1.12, 0], '#ffffff', 'glass');
    kit.neon([0, 2.24, 0], [0.05, 0.05, w.d], '#A855F7', 2.6); kit.neon([0, 0.03, 0], [0.06, 0.03, w.d], '#A855F7', 2.2);
    for (const sz of [-1, 1]) kit.neon([0, 1.12, (sz * w.d) / 2], [0.05, 2.24, 0.05], '#A855F7', 2.4);
  });
  kit.at(-10.6, 0); kit.add(new THREE.PlaneGeometry(7.0, 11.4), [0, 0.006, 0], '#1d1438', 'soft', [-Math.PI / 2, 0, 0]);
  for (const sz of [-1, 1]) kit.neon([0, 0.012, sz * 5.65], [7.0, 0.012, 0.04], '#A855F7', 2.2);
  // gamekasten
  G.arcadeZ.forEach((z, k) => {
    const A = ARCADE[k]; kit.at(G.arcadeX, z, Math.PI / 2);
    kit.box([0, 0.5, 0], [0.7, 1.0, 0.7], '#11152a', 'gloss'); kit.box([0, 1.4, -0.12], [0.7, 0.8, 0.46], '#11152a', 'gloss');
    kit.box([0, 1.04, 0.2], [0.7, 0.08, 0.36], '#1d2340', 'gloss', [0.25, 0, 0]); kit.box([0, 1.88, -0.02], [0.7, 0.18, 0.6], '#11152a', 'gloss');
    kit.neon([0, 1.88, 0.285], [0.6, 0.12, 0.02], A.b, 2.2);
    for (const sx of [-1, 1]) { kit.box([sx * 0.36, 1.0, -0.02], [0.02, 1.96, 0.74], A.a, 'gloss'); kit.neon([sx * 0.375, 1.0, 0.34], [0.01, 1.9, 0.03], A.a, 2.4); }
    kit.cyl([-0.14, 1.12, 0.22], 0.012, 0.08, '#c9d1e0', 'gloss', 6); kit.sph([-0.14, 1.17, 0.22], 0.03, '#FF3B4E', 'gloss');
    [0.04, 0.12, 0.2].forEach((bx, i) => kit.cyl([bx, 1.09, 0.2 + (i % 2) * 0.04], 0.022, 0.02, i % 2 ? A.b : A.a, 'neon', 10));
  });
  // racesimulators
  G.raceX.forEach((x) => {
    kit.at(x, G.raceZ);
    for (const sx of [-0.34, 0.34]) kit.box([sx, 0.06, 0], [0.06, 0.06, 1.9], '#0f1222', 'gloss');
    kit.box([0, 0.06, -0.8], [0.74, 0.06, 0.06], '#0f1222', 'gloss'); kit.box([0, 0.06, 0.8], [0.74, 0.06, 0.06], '#0f1222', 'gloss');
    kit.box([0, 0.25, 0.5], [0.5, 0.12, 0.5], '#FF7A24', 'soft'); kit.box([0, 0.62, 0.78], [0.5, 0.75, 0.12], '#FF7A24', 'soft', [-0.3, 0, 0]); // kuipstoel
    for (const sx of [-0.22, 0.22]) kit.box([sx, 0.5, 0.62], [0.06, 0.5, 0.4], '#1c1f2e', 'soft', [-0.15, 0, 0]);
    kit.box([0, 0.36, -0.15], [0.08, 0.6, 0.08], '#0f1222', 'gloss', [0.35, 0, 0]); // stuurkolom
    kit.tor([0, 0.72, -0.02], 0.15, 0.022, '#1c1f2e', 'gloss', [0.35 + Math.PI / 2 - Math.PI / 2, 0, 0]);
    kit.box([0, 0.72, -0.02], [0.1, 0.06, 0.04], '#FF7A24', 'gloss', [0.35, 0, 0]);
    kit.box([-0.08, 0.14, -0.42], [0.07, 0.03, 0.14], '#c9d1e0', 'gloss', [-0.6, 0, 0]); kit.box([0.08, 0.14, -0.42], [0.07, 0.03, 0.16], '#c9d1e0', 'gloss', [-0.6, 0, 0]); // pedalen
    kit.box([0, 0.55, -0.8], [0.08, 1.1, 0.08], '#0f1222', 'gloss'); kit.box([0, 1.15, -0.82], [1.1, 0.66, 0.06], '#0f1222', 'gloss'); // scherm
    kit.neon([0, 0.8, -0.85], [1.0, 0.02, 0.02], '#20D9FF', 2.4);
  });
  // tv-hoek
  kit.at(G.tv.c[0], G.tv.c[1]);
  kit.box([0, 0.25, 0], [2.0, 0.5, 0.45], '#1d2340', 'std'); kit.box([0, 1.32, -0.08], [2.3, 1.32, 0.06], '#0b0e1c', 'gloss');
  kit.box([0.55, 0.55, 0.05], [0.42, 0.08, 0.3], '#eef1f7', 'gloss'); kit.neon([0.55, 0.55, 0.205], [0.3, 0.012, 0.01], '#20D9FF', 2.2); // spelcomputer
  kit.neon([0, 0.02, 0], [2.0, 0.02, 0.5], '#A855F7', 1.6);
  sofa(kit, G.sofa.c[0], G.sofa.c[1], Math.PI, '#3b2a6b');
  kit.at(G.table.c[0], G.table.c[1]); kit.box([0, 0.22, 0], [G.table.w, 0.06, G.table.d], '#eef1f7', 'gloss'); for (const sx of [-0.45, 0.45]) kit.box([sx, 0.1, 0], [0.05, 0.2, G.table.d - 0.05], '#c9d1e0', 'gloss');
  kit.box([-0.2, 0.27, 0], [0.16, 0.04, 0.1], '#1c1f2e', 'gloss'); kit.box([0.15, 0.27, 0.05], [0.16, 0.04, 0.1], '#1c1f2e', 'gloss'); // controllers
  G.beans.forEach(([x, z], i) => { kit.at(x, z); kit.sph([0, 0.24, 0], 0.48, i ? '#20D9FF' : '#FF4DB8', 'soft', [1, 0.55, 1], undefined, 2); });

  // ---- LOUNGE VOORAAN ----
  kit.at(L.pingpong.c[0], L.pingpong.c[1]);
  kit.box([0, 0.74, 0], [L.pingpong.w, 0.04, L.pingpong.d], '#1f4fa8', 'gloss');
  kit.box([0, 0.763, 0], [L.pingpong.w - 0.04, 0.005, 0.02], '#ffffff', 'std');
  for (const sx of [-1, 1]) kit.box([sx * (L.pingpong.w / 2 - 0.02), 0.763, 0], [0.02, 0.005, L.pingpong.d - 0.02], '#ffffff', 'std');
  for (const sz of [-1, 1]) kit.box([0, 0.763, sz * (L.pingpong.d / 2 - 0.02)], [L.pingpong.w - 0.02, 0.005, 0.02], '#ffffff', 'std');
  kit.add(new THREE.BoxGeometry(0.01, 0.15, L.pingpong.d + 0.15), [0, 0.84, 0], '#ffffff', 'glass');
  kit.box([0, 0.92, 0], [0.012, 0.012, L.pingpong.d + 0.15], '#eef1f7', 'std');
  for (const [lx, lz] of [[-1.2, -0.6], [1.2, -0.6], [-1.2, 0.6], [1.2, 0.6]]) kit.box([lx, 0.36, lz], [0.05, 0.72, 0.05], '#1c1f2e', 'gloss');
  kit.at(L.foos.c[0], L.foos.c[1]); // tafelvoetbal
  kit.box([0, 0.78, 0], [L.foos.w, 0.22, L.foos.d], '#8a5a3b', 'std'); kit.box([0, 0.885, 0], [L.foos.w - 0.08, 0.01, L.foos.d - 0.08], '#2f9e5b', 'std');
  for (const [lx, lz] of [[-0.55, -0.3], [0.55, -0.3], [-0.55, 0.3], [0.55, 0.3]]) kit.box([lx, 0.34, lz], [0.07, 0.68, 0.07], '#5b3d28', 'std');
  [-0.45, -0.15, 0.15, 0.45].forEach((rx, i) => {
    kit.cyl([rx, 0.92, 0], 0.01, L.foos.d + 0.36, '#c9d1e0', 'gloss', 6, undefined, [Math.PI / 2, 0, 0]);
    kit.cyl([rx, 0.92, (i % 2 ? 1 : -1) * (L.foos.d / 2 + 0.17)], 0.025, 0.1, '#1c1f2e', 'gloss', 8, undefined, [Math.PI / 2, 0, 0]);
    for (const pz of [-0.2, 0, 0.2]) kit.box([rx, 0.9, pz], [0.03, 0.08, 0.04], i % 2 ? '#FF3B4E' : '#398CFF', 'gloss');
  });
  sofa(kit, L.sofa.c[0], L.sofa.c[1], L.sofa.ry, '#26305e');
  kit.at(L.table.c[0], L.table.c[1]); kit.box([0, 0.38, 0], [L.table.w, 0.05, L.table.d], '#eef1f7', 'gloss'); kit.box([0, 0.18, 0], [L.table.w - 0.2, 0.36, 0.08], '#c9d1e0', 'gloss');
  kit.cyl([0.3, 0.45, 0], 0.045, 0.1, '#FF7A24', 'gloss', 10); kit.box([-0.25, 0.43, 0.05], [0.24, 0.04, 0.17], '#20D9FF', 'std');
  kit.at(L.sofa.c[0], 10.75); kit.add(new THREE.CircleGeometry(1.7, 40), [0, 0.006, 0], '#2a2040', 'soft', [-Math.PI / 2, 0, 0], [1.4, 1, 1]);
  kit.at(L.jukebox.c[0], L.jukebox.c[1], L.jukebox.ry); // jukebox
  kit.box([0, 0.65, 0], [0.9, 1.3, 0.55], '#3b1d63', 'gloss'); kit.add(new THREE.CylinderGeometry(0.45, 0.45, 0.55, 24, 1, false, -Math.PI / 2, Math.PI), [0, 1.3, 0], '#3b1d63', 'gloss', [Math.PI / 2, 0, 0]);
  kit.tor([0, 1.3, 0.29], 0.38, 0.02, '#FF4DB8', 'neon', undefined, Math.PI); kit.tor([0, 1.3, 0.29], 0.3, 0.02, '#FACC15', 'neon', undefined, Math.PI);
  kit.neon([0, 0.75, 0.28], [0.6, 0.4, 0.01], '#20D9FF', 1.6); for (const sx of [-1, 1]) kit.neon([sx * 0.42, 0.65, 0.28], [0.03, 1.2, 0.02], '#FF7A24', 2.4);
  for (let i = 0; i < 5; i++) kit.box([-0.24 + i * 0.12, 0.42, 0.28], [0.08, 0.04, 0.02], '#eef1f7', 'gloss');

  // ---- AQUARIUMHOEK ACHTERAAN ----
  kit.at(L.aquarium.c[0], L.aquarium.c[1]);
  kit.box([0, 0.35, 0], [L.aquarium.w, 0.7, L.aquarium.d], '#1b2347', 'std'); kit.neon([0, 0.71, L.aquarium.d / 2], [L.aquarium.w, 0.02, 0.02], '#20D9FF', 2.4);
  kit.add(new THREE.BoxGeometry(L.aquarium.w, 1.3, L.aquarium.d), [0, 1.36, 0], '#ffffff', 'glass');
  kit.neon([0, 1.36, -L.aquarium.d / 2 + 0.03], [L.aquarium.w - 0.04, 1.26, 0.01], '#1a7fd0', 0.75); // water (achterwand licht)
  kit.box([0, 0.75, 0], [L.aquarium.w - 0.04, 0.08, L.aquarium.d - 0.04], '#d9c38f', 'std'); // zand
  for (let i = 0; i < 9; i++) kit.sph([-2.0 + i * 0.5, 0.95 + (i % 3) * 0.08, -0.1 + (i % 2) * 0.15], 0.07 + (i % 3) * 0.02, '#3cb36a', 'leaf', [0.5, 2.6, 0.5], undefined, 0);
  kit.box([0, 2.04, 0], [L.aquarium.w + 0.04, 0.06, L.aquarium.d + 0.04], '#1b2347', 'gloss');
  L.chairs.forEach(([x, z], i) => { // fauteuils
    kit.at(x, z, Math.PI + (i ? -0.25 : 0.25));
    kit.box([0, 0.25, 0], [0.75, 0.32, 0.7], '#FF7A24', 'soft'); kit.box([0, 0.6, -0.3], [0.75, 0.55, 0.15], '#FF7A24', 'soft');
    for (const sx of [-1, 1]) kit.box([sx * 0.33, 0.45, 0], [0.12, 0.25, 0.7], '#FF7A24', 'soft');
    kit.box([0, 0.43, 0.04], [0.52, 0.08, 0.55], '#ffd0a6', 'soft');
  });
  L.vending.forEach((v, i) => { kit.at(v.c[0], v.c[1], v.ry); kit.box([0, 0.95, 0], [v.w, 1.9, v.d], i ? '#1f4fa8' : '#b0263a', 'gloss'); kit.neon([0, 1.9, v.d / 2], [v.w, 0.03, 0.02], '#ffffff', 1.6); });

  // ---- planten ----
  PLANTS.forEach(([x, z, s, k]) => plant(kit, x, z, s, k));
  return kit.build();
}

/** vloerplaat (achthoek met gaten voor de vide en de trap) */
function slabGeometry() {
  const shape = new THREE.Shape(); const pts = oct(UP_R);
  pts.forEach(([x, z], i) => (i ? shape.lineTo(x, -z) : shape.moveTo(x, -z))); shape.closePath();
  const vide = new THREE.Path(); vide.absarc(0, 0, VIDE_R, 0, Math.PI * 2, true); shape.holes.push(vide);
  const h = new THREE.Path(); h.moveTo(HOLE.x0, -HOLE.z0); h.lineTo(HOLE.x0, -HOLE.z1); h.lineTo(HOLE.x1, -HOLE.z1); h.lineTo(HOLE.x1, -HOLE.z0); h.closePath(); shape.holes.push(h);
  const g = new THREE.ExtrudeGeometry(shape, { depth: SLAB, bevelEnabled: false, curveSegments: 48 });
  g.rotateX(-Math.PI / 2); return g;
}

/* =================== component =================== */
export function Upstairs() {
  const floor = useFloor((s) => s.floor);
  const [seen, setSeen] = useState(floor === 1);
  useEffect(() => { if (floor === 1) setSeen(true); }, [floor]);
  return seen ? <group visible={floor === 1}><Level /></group> : null;
}

function Level() {
  const geos = useMemo(buildFloor, []);
  const slab = useMemo(slabGeometry, []);
  const tiles = useMemo(tileTex, []); const wood = useMemo(woodTex, []);
  const mats = useMemo(() => ({
    std: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.55, metalness: 0.08 }),
    gloss: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.22, metalness: 0.4 }),
    soft: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, metalness: 0 }),
    leaf: new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.6, metalness: 0, flatShading: true }),
    neon: new THREE.MeshBasicMaterial({ vertexColors: true, toneMapped: false }),
    glass: new THREE.MeshPhysicalMaterial({ color: '#a8dcff', transparent: true, opacity: 0.16, roughness: 0.05, metalness: 0, depthWrite: false, side: THREE.DoubleSide }),
  }), []);
  const slabMats = useMemo(() => [new THREE.MeshStandardMaterial({ map: tiles, roughness: 0.32, metalness: 0.35, color: '#c8d0ff' }), new THREE.MeshStandardMaterial({ color: '#0d1330', roughness: 0.5, metalness: 0.5 })], [tiles]);
  const signs = useMemo(() => ({ kantine: sign('KANTINE', '#FF9A4D'), game: sign('GAME ROOM', '#C77DFF'), lounge: sign('LOUNGE', '#20D9FF') }), []);
  const vend = useMemo(() => [vendingTex('#b0263a'), vendingTex('#1f4fa8')], []);
  useEffect(() => () => { Object.values(geos).forEach((g) => g?.dispose()); slab.dispose(); }, [geos, slab]);

  // ---- bewegende schermen: racespel (gedeeld) en vier gamekasten ----
  const race = useMemo(() => { const c = canvas(256, 144); return { ...c, t: tex(c.c) }; }, []);
  const arcade = useMemo(() => ARCADE.map(() => { const c = canvas(128, 160); return { ...c, t: tex(c.c) }; }), []);
  const tvc = useMemo(() => { const c = canvas(256, 144); return { ...c, t: tex(c.c) }; }, []);
  const ball = useRef<THREE.Mesh>(null);
  const fish = useRef<THREE.Group>(null);
  const acc = useRef(0);
  const still = useMemo(() => reducedMotion(), []);
  useEffect(() => { drawRace(race.g, 256, 144, 0); race.t.needsUpdate = true; arcade.forEach((a, k) => { drawArcade(a.g, 128, 160, k, 0); a.t.needsUpdate = true; }); drawRace(tvc.g, 256, 144, 3); tvc.t.needsUpdate = true; }, [race, arcade, tvc]);
  useFrame(({ clock }, dt) => {
    if (useFloor.getState().floor !== 1) return;
    const t = clock.elapsedTime;
    if (!still) {
      acc.current += dt;
      if (acc.current > 0.1) { // 10 beelden per seconde is genoeg voor de schermen
        acc.current = 0;
        drawRace(race.g, 256, 144, t); race.t.needsUpdate = true;
        drawRace(tvc.g, 256, 144, t * 1.3 + 2); tvc.t.needsUpdate = true;
        arcade.forEach((a, k) => { drawArcade(a.g, 128, 160, k, t + k * 1.7); a.t.needsUpdate = true; });
      }
      if (fish.current) fish.current.children.forEach((f, i) => { const s = 0.35 + (i % 3) * 0.12; const ph = t * s + i * 1.9; f.position.set(Math.sin(ph) * 1.9, 1.05 + (i % 4) * 0.17 + Math.sin(t * 1.3 + i) * 0.04, (i % 2 ? 0.08 : -0.1)); f.rotation.y = Math.cos(ph) > 0 ? 0 : Math.PI; });
    }
    // pingpongbal alleen als er aan beide kanten iemand staat
    if (ball.current) {
      const on = occupied.get('pingpong0') === 2 && occupied.get('pingpong1') === 2; // 2 = staat er echt (1 = onderweg)
      ball.current.visible = on;
      if (on) { const p = (t * 0.9) % 2; const k = p < 1 ? p : 2 - p; const x = -1.5 + k * 3.0; const hop = Math.abs(Math.sin(k * Math.PI * 2)); ball.current.position.set(L.pingpong.c[0] + x, 0.8 + hop * 0.32, L.pingpong.c[1] + Math.sin(t * 1.7) * 0.25); }
    }
  });

  const raceScreens = G.raceX.map((x) => [x, G.raceZ - 0.785] as V2);
  return (
    <group position={[0, Y1, 0]}>
      {/* vloerplaat: bovenkant op Y1 */}
      <mesh geometry={slab} material={slabMats} position={[0, -SLAB, 0]} receiveShadow />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[12.9, 0.004, 0]}><planeGeometry args={[2.6, 9.6]} /><meshStandardMaterial map={wood} roughness={0.5} metalness={0.05} /></mesh>
      {/* neonrand onder de vloer, zoals beneden */}
      <OctRing r={UP_R + 0.01} y={-SLAB * 0.5} col="#FF7A24" />
      {(Object.keys(mats) as MatKey[]).map((k) => geos[k] && <mesh key={k} geometry={geos[k]!} material={mats[k]} renderOrder={k === 'glass' ? 2 : 0} />)}
      {/* bordjes */}
      <mesh position={[K.wall.c[0] - 0.12, 2.38, 0]} rotation={[0, -Math.PI / 2, 0]}><planeGeometry args={[3.2, 0.8]} /><meshBasicMaterial map={signs.kantine} transparent toneMapped={false} depthWrite={false} /></mesh>
      <mesh position={[G.wall.c[0] + 0.12, 2.4, 2.4]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[3.6, 0.9]} /><meshBasicMaterial map={signs.game} transparent toneMapped={false} depthWrite={false} /></mesh>
      <mesh position={[G.glass[0].c[0] + 0.05, 2.62, 0]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[2.0, 0.5]} /><meshBasicMaterial map={signs.game} transparent toneMapped={false} depthWrite={false} /></mesh>
      <mesh position={[L.aquarium.c[0], 2.5, L.aquarium.c[1]]}><planeGeometry args={[2.4, 0.6]} /><meshBasicMaterial map={signs.lounge} transparent toneMapped={false} depthWrite={false} /></mesh>
      {/* schermen */}
      {G.arcadeZ.map((z, k) => (
        <mesh key={k} position={[G.arcadeX + 0.125, 1.45, z]} rotation={[0, Math.PI / 2, 0]}><planeGeometry args={[0.56, 0.7]} /><meshBasicMaterial map={arcade[k].t} toneMapped={false} /></mesh>
      ))}
      {raceScreens.map(([x, z], i) => <mesh key={i} position={[x, 1.15, z]}><planeGeometry args={[1.02, 0.58]} /><meshBasicMaterial map={race.t} toneMapped={false} /></mesh>)}
      <mesh position={[G.tv.c[0], 1.32, G.tv.c[1] - 0.045]}><planeGeometry args={[2.2, 1.22]} /><meshBasicMaterial map={tvc.t} toneMapped={false} /></mesh>
      {L.vending.map((v, i) => (
        <mesh key={i} position={[v.c[0] + Math.sin(v.ry) * (v.d / 2 + 0.006), 1.0, v.c[1] + Math.cos(v.ry) * (v.d / 2 + 0.006)]} rotation={[0, v.ry, 0]}><planeGeometry args={[0.8, 1.6]} /><meshBasicMaterial map={vend[i]} toneMapped={false} /></mesh>
      ))}
      {/* vissen */}
      <group ref={fish} position={[L.aquarium.c[0], 0, L.aquarium.c[1]]}>
        {Array.from({ length: 7 }, (_, i) => (
          <mesh key={i} scale={[1.6, 0.8, 0.5]}><sphereGeometry args={[0.06, 10, 8]} /><meshStandardMaterial color={['#FF7A24', '#FACC15', '#20D9FF', '#FF4DB8'][i % 4]} emissive={['#FF7A24', '#FACC15', '#20D9FF', '#FF4DB8'][i % 4]} emissiveIntensity={0.35} /></mesh>
        ))}
      </group>
      <mesh ref={ball} visible={false}><sphereGeometry args={[0.025, 10, 8]} /><meshBasicMaterial color="#ffffff" /></mesh>
      {/* licht per zone */}
      <pointLight position={[11.0, 2.6, 0]} color="#FFD9B0" intensity={18} distance={13} decay={1.5} />
      <pointLight position={[8.5, 2.4, 6.5]} color="#FFE6C8" intensity={9} distance={9} decay={1.6} />
      <pointLight position={[8.5, 2.4, -6.5]} color="#FFE6C8" intensity={9} distance={9} decay={1.6} />
      <pointLight position={[-10.5, 2.4, -1]} color="#B57BFF" intensity={16} distance={12} decay={1.5} />
      <pointLight position={[-10.5, 2.2, 4]} color="#20D9FF" intensity={8} distance={8} decay={1.6} />
      <pointLight position={[0, 2.6, 10]} color="#ffffff" intensity={10} distance={11} decay={1.6} />
      <pointLight position={[0.6, 2.2, -10.6]} color="#4aa8ff" intensity={8} distance={8} decay={1.6} />
    </group>
  );
}

function OctRing({ r, y, col }: { r: number; y: number; col: string }) {
  const geo = useMemo(() => {
    const pts = oct(r).map(([x, z]) => new THREE.Vector3(x, y, z)); pts.push(pts[0].clone());
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0), 160, 0.06, 6, false);
  }, [r, y]);
  return <mesh geometry={geo}><meshBasicMaterial color={col} toneMapped={false} /></mesh>;
}

