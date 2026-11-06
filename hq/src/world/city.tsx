/**
 * De stad rond het kantoor (wens niels 6 nov: "de gebouwen mogen meer spanning hebben, en op de grond gewoon
 * wegen, bomen en parkjes, voor de sier"). Alles staat op een stratenraster op straatniveau (y = -40):
 * - grond: één vlak met een shader die straten, zebrapaden, verkeer, straatlantaarns, parken met vijvers
 *   en pleinen met fonteinen tekent (welke cel wat is, staat in een kleine DataTexture);
 * - gebouwen: één InstancedMesh voor torens, kronen, dakopbouw en antennes, met per gebouw een eigen stijl
 *   (ramen, glazen kantoorbanden of neonvinnen), neonranden, hoekstrepen die oplichten en ramen die aan/uit gaan;
 * - bomen in parken en op pleinen (november: een deel in herfstkleuren);
 * - knipperende vliegtuiglichten, lichtreclames met de video's van het kanaal en zoeklichten in de nacht.
 * De indeling komt uit een vaste seed, dus de stad ziet er elke keer hetzelfde uit.
 */
import { useEffect, useMemo, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Sparkles } from '@react-three/drei';
import * as THREE from 'three';
import { useWorld, dayPhase, dayAmount } from './useWorld';

const Y = -40; // straatniveau
const P = 22; // raster: blok + straat
const B = 16; // blok (straat is P - B = 6 breed)
const HALF = 8; // cellen -8..8
const NC = HALF * 2 + 1;
const R_CITY = 172;
const MOON_A = Math.atan2(0.45, -0.87); // richting van de maan (zie extras.tsx)
const SIGNS = ['DRIFTMARK', 'WHAT IF?', '10x FASTER', 'NO RULES', 'NEVER DIE', '2x STRONGER', 'SUBSCRIBE', 'OPEN 24/7'];
const SIGN_COLORS = ['#FF7A24', '#20D9FF', '#A855F7', '#FF3D9A', '#20D9FF', '#FF7A24', '#FF3D9A', '#A855F7'];

function rng(seed: number) {
  return () => { seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

type Bld = { x: number; y: number; z: number; w: number; h: number; d: number; seed: number; kind: number }; // kind 0 toren, 1 kroon, 2 dakopbouw, 3 antenne
type Tree = { x: number; z: number; s: number; c: THREE.Color };
type Sign = { p: [number, number, number]; ry: number; w: number; slot: number };
type Light = { p: [number, number, number]; ph: number };

function layout() {
  const r = rng(20261106);
  const kinds = new Uint8Array(NC * NC * 4);
  const blds: Bld[] = []; const trees: Tree[] = []; const signs: Sign[] = []; const lights: Light[] = []; const beams: [number, number, number][] = [];
  const green = ['#2f7a3a', '#3b8f45', '#25663a', '#4a9a4a', '#2c7048'];
  const autumn = ['#d9822b', '#c4561f', '#e0a83a', '#a8452a'];
  const tree = (x: number, z: number, s: number) => {
    const c = new THREE.Color(r() < 0.3 ? autumn[Math.floor(r() * autumn.length)] : green[Math.floor(r() * green.length)]);
    trees.push({ x, z, s, c });
  };
  for (let j = -HALF; j <= HALF; j++) for (let i = -HALF; i <= HALF; i++) {
    const cx = i * P, cz = j * P; const dist = Math.hypot(cx, cz);
    let k = 0;
    if (dist < 40) k = 2; // groot park onder het kantoor
    else if (dist < R_CITY) { const q = r(); k = q < 0.13 ? 2 : q < 0.19 ? 3 : 1; }
    kinds[((j + HALF) * NC + (i + HALF)) * 4] = k;
    if (k === 2) {
      // bomen op een verspringend raster, niet op de paden en niet in de vijver
      for (let u = -6.4; u <= 6.4; u += 2.6) for (let v = -6.4; v <= 6.4; v += 2.6) {
        const x = u + (r() - 0.5) * 1.4, z = v + (r() - 0.5) * 1.4;
        if (Math.abs(x - z) < 1.3 || Math.abs(x + z) < 1.3 || Math.hypot(x, z) < 4.3 || r() < 0.2) continue;
        tree(cx + x, cz + z, 0.75 + r() * 0.6);
      }
    } else if (k === 3) {
      for (const [x, z] of [[-5.2, -5.2], [5.2, -5.2], [-5.2, 5.2], [5.2, 5.2]]) tree(cx + x, cz + z, 0.8 + r() * 0.3);
    } else if (k === 1) {
      const ang = Math.atan2(cx, cz); const dA = Math.abs(Math.atan2(Math.sin(ang - MOON_A), Math.cos(ang - MOON_A)));
      const lowMoon = dA < 0.32 ? 0.45 : 1;
      const s = B / 2 - 1.2; // bebouwbaar halfvlak (stoep eromheen)
      const q = r();
      const lots: [number, number, number, number][] = q < 0.3 ? [[0, 0, s, s]]
        : q < 0.65 ? (r() < 0.5 ? [[-s / 2 - 0.2, 0, s / 2 - 0.2, s], [s / 2 + 0.2, 0, s / 2 - 0.2, s]] : [[0, -s / 2 - 0.2, s, s / 2 - 0.2], [0, s / 2 + 0.2, s, s / 2 - 0.2]])
          : [[-s / 2 - 0.2, -s / 2 - 0.2, s / 2 - 0.2, s / 2 - 0.2], [s / 2 + 0.2, -s / 2 - 0.2, s / 2 - 0.2, s / 2 - 0.2], [-s / 2 - 0.2, s / 2 + 0.2, s / 2 - 0.2, s / 2 - 0.2], [s / 2 + 0.2, s / 2 + 0.2, s / 2 - 0.2, s / 2 - 0.2]];
      for (const [lx, lz, hx, hz] of lots) {
        let h: number;
        if (dist < 62) h = 5 + r() * 9; // dichtbij laag, zodat het kantoor goed zichtbaar blijft
        else if (r() < 0.09 && dist > 80 && lots.length < 4) h = 58 + r() * 22; // wolkenkrabber
        else h = 12 + Math.pow(r(), 1.5) * 44;
        if (lots.length === 4) h *= 0.7;
        h *= lowMoon;
        const slim = h > 55 ? 0.62 + r() * 0.15 : 0.75 + r() * 0.22;
        const w = 2 * hx * slim, d = 2 * hz * (h > 55 ? slim : 0.75 + r() * 0.22);
        const x = cx + lx + (r() - 0.5) * (2 * hx - w) * 0.8, z = cz + lz + (r() - 0.5) * (2 * hz - d) * 0.8;
        const seed = r();
        blds.push({ x, y: Y, z, w, h, d, seed, kind: 0 });
        let top = Y + h;
        if (h > 30 && r() < 0.55) { // kroon(en) op hoge torens
          const ch = 3 + r() * 8; blds.push({ x, y: top, z, w: w * 0.68, h: ch, d: d * 0.68, seed, kind: 1 }); top += ch;
          if (r() < 0.45) { const c2 = 2 + r() * 4; blds.push({ x, y: top, z, w: w * 0.38, h: c2, d: d * 0.38, seed, kind: 1 }); top += c2; }
        } else if (r() < 0.75) { // dakopbouw: installaties, liftkoker, watertank
          const n = 1 + Math.floor(r() * 3);
          for (let m = 0; m < n; m++) {
            const bw = 1 + r() * Math.min(3, w * 0.35), bd = 1 + r() * Math.min(3, d * 0.35);
            blds.push({ x: x + (r() - 0.5) * (w - bw) * 0.8, y: top, z: z + (r() - 0.5) * (d - bd) * 0.8, w: bw, h: 0.8 + r() * 1.6, d: bd, seed: r(), kind: 2 });
          }
        }
        if (h > 40 && r() < 0.65) { // antenne met knipperlicht
          const ah = 5 + r() * 9; blds.push({ x, y: top, z, w: 0.35, h: ah, d: 0.35, seed, kind: 3 });
          lights.push({ p: [x, top + ah + 0.2, z], ph: r() });
        } else if (h > 26) {
          lights.push({ p: [x + w * 0.45, top + 0.3, z + d * 0.45], ph: r() });
        }
        if (h > 60 && beams.length < 4) beams.push([x, top + 0.5, z]);
        // lichtreclame op de gevel die naar het kantoor kijkt
        if (h > 22 && dist > 62 && dist < 150 && signs.length < SIGNS.length * 2 && r() < 0.55) {
          const fx = Math.abs(x) > Math.abs(z); const faceW = fx ? d : w;
          if (faceW >= 6) {
            const sw = Math.min(faceW * 0.86, 12); const sh = sw / 4;
            const sy = Y + h - sh / 2 - 1.4;
            const p: [number, number, number] = fx ? [x - Math.sign(x) * (w / 2 + 0.08), sy, z] : [x, sy, z - Math.sign(z) * (d / 2 + 0.08)];
            const ry = fx ? (x > 0 ? -Math.PI / 2 : Math.PI / 2) : (z > 0 ? Math.PI : 0);
            signs.push({ p, ry, w: sw, slot: signs.length % SIGNS.length });
          }
        }
      }
    }
  }
  return { kinds, blds, trees, signs, lights, beams };
}

/* ---------------- grond: straten, verkeer, lantaarns, parken, pleinen ---------------- */
const GROUND_FRAG = `
uniform sampler2D uMap; uniform float uTime; uniform float uDay; uniform vec3 uFog; uniform float uNear; uniform float uFar;
varying vec2 vP; varying float vDist;
const float P = ${P.toFixed(1)}; const float HB = ${(B / 2).toFixed(1)}; const float NC = ${NC.toFixed(1)};
float h1(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float kindAt(vec2 c){ vec2 uv = (c + ${HALF.toFixed(1)} + 0.5) / NC; if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) return 0.0; return floor(texture2D(uMap, uv).r * 255.0 + 0.5); }
// auto's op een straat: along = positie langs de straat, off = afstand tot de middenlijn (-3..3)
vec3 cars(vec3 col, float along, float off, float rid, float night){
  float lane = off < 0.0 ? 1.0 : -1.0;
  float lo = abs(off) - 1.5;
  if (abs(lo) > 0.6) return col;
  float sp = 5.0 + h1(vec2(rid, lane)) * 6.0;
  float u = along - uTime * sp * lane + rid * 37.0;
  float id = floor(u / 8.0); float f = fract(u / 8.0) * 8.0;
  if (h1(vec2(id, rid * 1.7 + lane)) < 0.5 || f > 2.4) return col;
  float ff = lane > 0.0 ? f / 2.4 : 1.0 - f / 2.4; // 0 = achterkant, 1 = voorkant
  float k = h1(vec2(id, rid + 9.0));
  vec3 body = k < 0.25 ? vec3(0.75, 0.12, 0.1) : k < 0.5 ? vec3(0.85, 0.85, 0.88) : k < 0.75 ? vec3(0.15, 0.3, 0.75) : vec3(0.9, 0.7, 0.15);
  vec3 c = body * mix(0.12, 1.0, 1.0 - night);
  if (ff > 0.3 && ff < 0.7) c *= 0.75; // dak
  float lamp = step(0.22, abs(lo)) * step(abs(lo), 0.48);
  c += lamp * step(0.9, ff) * vec3(2.6, 2.4, 2.0) * (0.25 + night);
  c += lamp * step(ff, 0.08) * vec3(2.2, 0.15, 0.1) * (0.2 + night);
  return c;
}
void main(){
  vec2 p = vP; float night = 1.0 - uDay;
  vec2 c = floor(p / P + 0.5); vec2 lp = p - c * P; vec2 al = abs(lp);
  bool inX = al.x < HB; bool inY = al.y < HB;
  vec3 asphalt = mix(vec3(0.03, 0.035, 0.06), vec3(0.3, 0.32, 0.36), uDay);
  vec3 walk = mix(vec3(0.065, 0.07, 0.1), vec3(0.55, 0.55, 0.57), uDay);
  vec3 col = asphalt;
  if (inX && inY) {
    float k = kindAt(c);
    float edge = HB - max(al.x, al.y);
    if (k < 0.5) col = mix(vec3(0.028, 0.032, 0.055), vec3(0.26, 0.27, 0.29), uDay);
    else if (k < 1.5) { col = mix(vec3(0.04, 0.045, 0.075), vec3(0.37, 0.38, 0.41), uDay); if (edge < 1.2) col = walk; }
    else if (k < 2.5) {
      float n = h1(floor(p * 1.5));
      col = mix(vec3(0.02, 0.07, 0.04), vec3(0.25, 0.52, 0.2), uDay) * (0.85 + 0.3 * n);
      float path = min(abs(lp.x - lp.y), abs(lp.x + lp.y)) * 0.7071;
      float rr = length(lp);
      if (path < 0.5 || abs(rr - 3.4) < 0.4) col = mix(vec3(0.08, 0.075, 0.09), vec3(0.66, 0.6, 0.48), uDay);
      if (rr < 2.8) {
        col = mix(vec3(0.02, 0.07, 0.17), vec3(0.22, 0.48, 0.72), uDay);
        col += step(0.94, h1(floor(p * 4.0 + vec2(uTime * 0.6, 0.0)))) * vec3(0.3, 0.6, 0.9) * (0.3 + night * 0.9);
      }
      // lampjes rond de vijver
      float la = atan(lp.y, lp.x); float seg = abs(fract(la / 6.2832 * 8.0) - 0.5) * 6.2832 / 8.0 * 3.9;
      float dl = length(vec2(seg, rr - 3.9));
      col += night * (smoothstep(0.2, 0.06, dl) * vec3(2.2, 1.7, 1.0) + exp(-dl * dl * 1.5) * vec3(0.5, 0.35, 0.15) * 0.5);
      if (edge < 0.6) col = walk;
    } else {
      vec2 tile = fract(lp * 0.8);
      col = mix(vec3(0.06, 0.06, 0.09), vec3(0.56, 0.54, 0.5), uDay) * (0.82 + 0.18 * step(0.07, tile.x) * step(0.07, tile.y));
      float rr = length(lp);
      if (rr < 2.1) col = mix(vec3(0.03, 0.12, 0.2), vec3(0.3, 0.6, 0.82), uDay) + (0.5 + 0.5 * sin(rr * 7.0 - uTime * 3.0)) * vec3(0.05, 0.35, 0.5) * (0.3 + night);
      col += smoothstep(0.25, 0.0, abs(rr - 2.25)) * vec3(0.2, 1.4, 1.9) * (0.25 + night);
    }
  } else if (inX || inY) {
    float along = inX ? p.x : p.y;
    float o = inX ? lp.y : lp.x;
    float off = o - sign(o) * P * 0.5;
    float rid = (inX ? c.y : c.x) + (o > 0.0 ? 0.5 : -0.5) + (inX ? 0.0 : 100.0);
    float toCross = HB - (inX ? al.x : al.y);
    if (abs(off) < 0.1 && fract(along / 3.0) < 0.5 && toCross > 1.6) col = mix(vec3(0.3, 0.25, 0.1), vec3(0.92, 0.86, 0.55), uDay);
    if (toCross < 1.3 && toCross > 0.2) col = mix(col, mix(vec3(0.16, 0.16, 0.2), vec3(0.85, 0.85, 0.85), uDay), step(0.5, fract(off * 1.1)));
    if (toCross > 1.4) col = cars(col, along, off, rid, night);
  }
  // straatlantaarns langs de stoepranden (om de 4 m)
  float L = HB + 0.35;
  float dl = 9.0;
  if (al.x <= L) dl = min(dl, length(vec2(abs(mod(lp.x + 2.0, 4.0) - 2.0), abs(al.y - L))));
  if (al.y <= L) dl = min(dl, length(vec2(abs(mod(lp.y + 2.0, 4.0) - 2.0), abs(al.x - L))));
  col += night * (exp(-dl * dl * 0.8) * vec3(1.0, 0.6, 0.28) * 0.3 + smoothstep(0.2, 0.07, dl) * vec3(2.4, 1.7, 0.9));
  col = mix(col, uFog, smoothstep(uNear, uFar, vDist));
  gl_FragColor = vec4(col, 1.0 - smoothstep(172.0, 205.0, length(p)));
}`;

/* ---------------- gebouwen ---------------- */
const BLD_VERT = `attribute vec3 aSize; attribute float aSeed; attribute float aKind;
varying vec2 vUv; varying vec3 vN; varying float vSeed; varying vec3 vSize; varying float vDist; varying float vKind;
void main(){ vUv = uv; vN = normal; vSeed = aSeed; vSize = aSize; vKind = aKind;
  vec4 mv = viewMatrix * modelMatrix * instanceMatrix * vec4(position, 1.0); vDist = -mv.z; gl_Position = projectionMatrix * mv; }`;
const BLD_FRAG = `uniform float uTime; uniform float uDay; uniform vec3 uFog; uniform float uNear; uniform float uFar;
varying vec2 vUv; varying vec3 vN; varying float vSeed; varying vec3 vSize; varying float vDist; varying float vKind;
float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec3 neon(float s){ return s < 0.25 ? vec3(1.0, 0.48, 0.14) : s < 0.5 ? vec3(0.13, 0.85, 1.0) : s < 0.75 ? vec3(0.66, 0.33, 0.97) : vec3(1.0, 0.24, 0.6); }
void main(){
  vec3 dayCol = mix(mix(vec3(0.2, 0.25, 0.34), vec3(0.34, 0.3, 0.26), step(0.55, h(vec2(vSeed, 6.1)))), vec3(0.3, 0.33, 0.38), step(0.8, h(vec2(vSeed, 3.3))));
  vec3 base = mix(vec3(0.02, 0.03, 0.08), dayCol, uDay) * (0.8 + 0.45 * h(vec2(vSeed, 4.2)));
  vec3 col = base;
  float lit = 1.0 - uDay * 0.65;
  float style = h(vec2(vSeed, 1.3));
  vec3 nc = neon(h(vec2(vSeed, 7.7)));
  bool side = abs(vN.y) < 0.5;
  float fw = abs(vN.x) > 0.5 ? vSize.z : vSize.x;
  float yy = vUv.y * vSize.y;
  if (vKind > 2.5) {
    col = base * 0.7;
  } else if (vKind > 1.5) {
    col = base * (side ? 0.7 : 1.15);
  } else if (side) {
    if (style < 0.45) { // klassieke ramen die op hun eigen moment aan en uit gaan
      vec2 cell = vec2(vUv.x * fw / 1.5, yy / 2.1); vec2 id = floor(cell); vec2 f = fract(cell);
      float win = step(0.22, f.x) * step(f.x, 0.78) * step(0.28, f.y) * step(f.y, 0.82);
      float k = h(id + vSeed * 17.0);
      float on = step(mix(0.58, 0.93, uDay), h(id * 1.31 + vec2(vSeed * 29.0, floor(uTime / 22.0 + k * 50.0) * 0.37)));
      vec3 warm = mix(vec3(1.0, 0.68, 0.38), vec3(0.5, 0.78, 1.0), step(0.62, h(id + 3.7)));
      col += win * on * warm * (0.45 + 0.55 * h(id + 9.1)) * lit;
      col += win * (1.0 - on) * uDay * vec3(0.12, 0.16, 0.22);
    } else if (style < 0.78) { // glazen kantoor: doorlopende raambanden per verdieping
      float fl = floor(yy / 2.4); float fy = fract(yy / 2.4);
      float band = step(0.3, fy) * step(fy, 0.86);
      float seg = floor(vUv.x * fw / 3.2);
      float on = step(mix(0.62, 0.92, uDay), h(vec2(fl, seg) + vSeed * 13.0 + floor(uTime / 30.0 + h(vec2(fl, seg + 2.0)) * 40.0) * 0.21));
      col = mix(base, base * mix(1.35, 1.15, uDay) + vec3(0.01, 0.02, 0.05) * (1.0 + uDay * 3.0), band);
      col += band * on * mix(vec3(0.45, 0.7, 1.0), vec3(1.0, 0.75, 0.45), step(0.6, h(vec2(fl, vSeed)))) * 0.42 * lit;
    } else { // neonvinnen: verticale lichtstrepen die zacht pulseren, met kleine ramen ertussen
      float fx = fract(vUv.x * fw / 3.0);
      float fin = step(abs(fx - 0.5), 0.05);
      col += fin * nc * 1.5 * lit * (0.7 + 0.3 * sin(uTime * 1.4 + vSeed * 20.0 - yy * 0.15));
      vec2 cell = vec2(vUv.x * fw / 1.5, yy / 2.1); vec2 id = floor(cell); vec2 f = fract(cell);
      float win = step(0.3, f.x) * step(f.x, 0.7) * step(0.35, f.y) * step(f.y, 0.75) * (1.0 - step(abs(fx - 0.5), 0.12));
      col += win * step(0.7, h(id + vSeed * 11.0)) * vec3(1.0, 0.75, 0.5) * 0.5 * lit;
    }
    // neonrand langs het dak en oplichtende hoeken
    {
      col += step(0.6, h(vec2(vSeed, 2.9))) * step(vSize.y - 0.5, yy) * step(yy, vSize.y - 0.12) * nc * 2.4 * lit;
      float ex = min(vUv.x, 1.0 - vUv.x) * fw;
      float corner = step(0.8, h(vec2(vSeed, 5.3))) * step(ex, 0.16);
      col += corner * nc * lit * (0.9 + 1.8 * step(0.82, fract(yy / max(vSize.y, 1.0) * 1.5 - uTime * 0.35 + vSeed)));
    }
  } else {
    col = base * 1.25;
    // helikopterplatform op een deel van de platte daken
    if (vKind < 0.5 && vSize.x > 8.0 && vSize.z > 8.0 && h(vec2(vSeed, 8.8)) > 0.6) {
      vec2 q = (vUv - 0.5) * vec2(vSize.x, vSize.z); float rr = length(q);
      col += smoothstep(0.18, 0.0, abs(rr - 3.0)) * vec3(1.0, 0.85, 0.3) * (0.5 + 1.4 * lit);
      float hh = step(abs(q.x), 1.1) * step(abs(q.y), 0.18) + step(abs(abs(q.x) - 1.0), 0.18) * step(abs(q.y), 1.4);
      col += min(hh, 1.0) * vec3(0.9, 0.9, 0.95) * (0.3 + 0.6 * lit);
    }
  }
  gl_FragColor = vec4(mix(col, uFog, smoothstep(uNear, uFar, vDist)), 1.0);
}`;

function signAtlas() {
  const W = 1024, H = 256;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H * SIGNS.length;
  const g = cv.getContext('2d')!;
  SIGNS.forEach((t, i) => {
    const y0 = i * H; const col = SIGN_COLORS[i];
    g.fillStyle = '#070a1a'; g.fillRect(0, y0, W, H);
    g.strokeStyle = col; g.lineWidth = 10; g.shadowColor = col; g.shadowBlur = 24; g.strokeRect(18, y0 + 18, W - 36, H - 36);
    g.font = '900 150px system-ui, -apple-system, Segoe UI, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = '#ffffff'; g.shadowBlur = 30; g.fillText(t, W / 2, y0 + H / 2 + 8, W - 90);
    g.fillStyle = col; g.shadowBlur = 0; g.globalAlpha = 0.55; g.fillText(t, W / 2, y0 + H / 2 + 8, W - 90); g.globalAlpha = 1;
  });
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  return tex;
}

export function City() {
  const L = useMemo(layout, []);
  const theme = useWorld((s) => s.theme);
  const fog = useThree((s) => s.scene.fog) as THREE.Fog | null;

  // grond
  const groundMat = useMemo(() => {
    const map = new THREE.DataTexture(L.kinds, NC, NC, THREE.RGBAFormat); map.magFilter = THREE.NearestFilter; map.minFilter = THREE.NearestFilter; map.needsUpdate = true;
    return new THREE.ShaderMaterial({
      uniforms: { uMap: { value: map }, uTime: { value: 0 }, uDay: { value: 0 }, uFog: { value: new THREE.Color('#0a0f2a') }, uNear: { value: 170 }, uFar: { value: 460 } },
      vertexShader: 'varying vec2 vP; varying float vDist; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vP = w.xz; vec4 mv = viewMatrix * w; vDist = -mv.z; gl_Position = projectionMatrix * mv; }',
      fragmentShader: GROUND_FRAG, transparent: true, depthWrite: true,
    });
  }, [L]);

  // gebouwen
  const bRef = useRef<THREE.InstancedMesh>(null);
  const bGeo = useMemo(() => {
    const g = new THREE.BoxGeometry(1, 1, 1); g.translate(0, 0.5, 0);
    g.setAttribute('aSize', new THREE.InstancedBufferAttribute(new Float32Array(L.blds.flatMap((b) => [b.w, b.h, b.d])), 3));
    g.setAttribute('aSeed', new THREE.InstancedBufferAttribute(new Float32Array(L.blds.map((b) => b.seed)), 1));
    g.setAttribute('aKind', new THREE.InstancedBufferAttribute(new Float32Array(L.blds.map((b) => b.kind)), 1));
    return g;
  }, [L]);
  const bMat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uDay: { value: 0 }, uFog: { value: new THREE.Color('#0a0f2a') }, uNear: { value: 170 }, uFar: { value: 460 } },
    vertexShader: BLD_VERT, fragmentShader: BLD_FRAG,
  }), []);
  useEffect(() => {
    const m = bRef.current; if (!m) return; const o = new THREE.Object3D();
    L.blds.forEach((b, i) => { o.position.set(b.x, b.y, b.z); o.rotation.set(0, 0, 0); o.scale.set(b.w, b.h, b.d); o.updateMatrix(); m.setMatrixAt(i, o.matrix); });
    m.instanceMatrix.needsUpdate = true; m.computeBoundingSphere();
  }, [L]);

  // bomen: stam + kruin
  const trunkRef = useRef<THREE.InstancedMesh>(null);
  const crownRef = useRef<THREE.InstancedMesh>(null);
  const treeGeo = useMemo(() => {
    const trunk = new THREE.CylinderGeometry(0.12, 0.18, 1.2, 6); trunk.translate(0, 0.6, 0);
    const crown = new THREE.IcosahedronGeometry(1, 1); crown.scale(1, 1.15, 1); crown.translate(0, 1.9, 0);
    return { trunk, crown };
  }, []);
  const treeMat = useMemo(() => ({
    trunk: new THREE.MeshStandardMaterial({ color: '#4a3324', roughness: 1 }),
    crown: new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.85, emissive: '#0b1a12', flatShading: true }),
  }), []);
  useEffect(() => {
    const t = trunkRef.current, c = crownRef.current; if (!t || !c) return; const o = new THREE.Object3D();
    L.trees.forEach((tr, i) => {
      o.position.set(tr.x, Y, tr.z); o.rotation.set(0, tr.x * 0.7 + tr.z, 0); o.scale.setScalar(tr.s); o.updateMatrix();
      t.setMatrixAt(i, o.matrix); c.setMatrixAt(i, o.matrix); c.setColorAt(i, tr.c);
    });
    t.instanceMatrix.needsUpdate = true; c.instanceMatrix.needsUpdate = true; if (c.instanceColor) c.instanceColor.needsUpdate = true;
    t.computeBoundingSphere(); c.computeBoundingSphere();
  }, [L]);

  // knipperende vliegtuiglichten
  const lightGeo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(L.lights.flatMap((l) => l.p), 3));
    g.setAttribute('aPh', new THREE.Float32BufferAttribute(L.lights.map((l) => l.ph), 1));
    return g;
  }, [L]);
  const lightMat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uDay: { value: 0 } },
    vertexShader: 'attribute float aPh; uniform float uTime; varying float vOn; void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.0); vOn = 0.15 + 0.85 * step(0.55, fract(uTime * 0.7 + aPh)); gl_PointSize = 520.0 / -mv.z; gl_Position = projectionMatrix * mv; }',
    fragmentShader: 'uniform float uDay; varying float vOn; void main(){ float d = length(gl_PointCoord - 0.5); float a = smoothstep(0.5, 0.0, d); gl_FragColor = vec4(vec3(3.0, 0.25, 0.18) * vOn * (1.0 - uDay * 0.5), a * a); }',
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false,
  }), []);

  // lichtreclames (één atlas, elke reclame een eigen strook)
  const signTex = useMemo(() => (typeof document !== 'undefined' ? signAtlas() : null), []);
  const signMats = useMemo(() => L.signs.map((s) => {
    const t = signTex?.clone(); if (t) { t.repeat.set(1, 1 / SIGNS.length); t.offset.set(0, 1 - (s.slot + 1) / SIGNS.length); t.needsUpdate = true; }
    return new THREE.MeshBasicMaterial({ map: t ?? null, toneMapped: false, color: new THREE.Color(1.5, 1.5, 1.5), side: THREE.DoubleSide });
  }), [L, signTex]);

  // zoeklichten vanaf de hoogste torens ('s nachts)
  const beamGeo = useMemo(() => { const g = new THREE.CylinderGeometry(9, 0.9, 120, 24, 1, true); g.translate(0, 60, 0); return g; }, []);
  const beamMat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: { uNight: { value: 1 } },
    vertexShader: 'varying float vY; void main(){ vY = uv.y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'uniform float uNight; varying float vY; void main(){ gl_FragColor = vec4(vec3(0.75, 0.85, 1.0) * pow(1.0 - vY, 0.9) * 0.2 * uNight, 1.0); }',
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false,
  }), []);
  const beamRefs = useRef<(THREE.Mesh | null)[]>([]);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime; const day = dayAmount(dayPhase(theme));
    for (const m of [groundMat, bMat]) {
      m.uniforms.uTime.value = t; m.uniforms.uDay.value = day;
      if (fog) m.uniforms.uFog.value.copy(fog.color);
    }
    lightMat.uniforms.uTime.value = t; lightMat.uniforms.uDay.value = day;
    beamMat.uniforms.uNight.value = Math.max(0, 1 - day * 1.6);
    beamRefs.current.forEach((b, i) => { if (b) b.rotation.set(0.42 + Math.sin(t * 0.21 + i) * 0.12, t * (0.18 + i * 0.05) + i * 2.1, 0, 'YXZ'); });
    signMats.forEach((m, i) => {
      // af en toe even flikkeren, zoals echte neonreclame
      const f = Math.sin(t * 13 + i * 7) > 0.97 && Math.sin(t * 0.7 + i) > 0.6 ? 0.35 : 1;
      m.color.setScalar((1.6 - day * 0.7) * f);
    });
  });

  return (
    <group>
      <mesh material={groundMat} position={[0, Y, 0]} rotation={[-Math.PI / 2, 0, 0]} raycast={() => null} renderOrder={-1}>
        <planeGeometry args={[420, 420]} />
      </mesh>
      <instancedMesh ref={bRef} args={[bGeo, bMat, L.blds.length]} raycast={() => null} />
      <instancedMesh ref={trunkRef} args={[treeGeo.trunk, treeMat.trunk, L.trees.length]} raycast={() => null} />
      <instancedMesh ref={crownRef} args={[treeGeo.crown, treeMat.crown, L.trees.length]} raycast={() => null} />
      <points geometry={lightGeo} material={lightMat} raycast={() => null} />
      {L.signs.map((s, i) => (
        <mesh key={i} position={s.p} rotation={[0, s.ry, 0]} material={signMats[i]} raycast={() => null}>
          <planeGeometry args={[s.w, s.w / 4]} />
        </mesh>
      ))}
      {L.beams.map((p, i) => (
        <mesh key={i} ref={(el) => { beamRefs.current[i] = el; }} position={p} geometry={beamGeo} material={beamMat} raycast={() => null} renderOrder={2} />
      ))}
      <Sparkles count={60} scale={[140, 30, 60]} position={[0, 14, -55]} size={26} speed={0.15} opacity={0.5} color="#FFB070" />
      <Sparkles count={40} scale={[140, 30, 60]} position={[0, 18, -60]} size={22} speed={0.1} opacity={0.45} color="#7fc8ff" />
    </group>
  );
}
