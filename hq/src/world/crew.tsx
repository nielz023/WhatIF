/**
 * DE MEDEWERKERS (verbeterpunt 1, niels 2026-11-06: "medewerkers die lopen, typen en naar elkaar toe gaan").
 * niels 2026-11-06 01:52: "alle medewerkers moeten er hetzelfde uitzien als de main karakter, maar ieder
 * poppetje zijn eigen stijl". Elke medewerker is dus het hoofdpersonage (maten en gezicht uit
 * hoofdpersonage.glb: grote ronde kop, grote oren, open lach, korte armen, hoodie-model), maar met een
 * eigen kapsel, muts of pet, bril, baard, koptelefoon, kleding en schoenen. Kleding in de afdelingskleur.
 *
 * Ze typen aan hun bureau, staan op om koffie te halen, lopen naar collega's en brengen een map
 * naar de afdeling die als volgende aan de video werkt (zichtbare overdracht). Bij een mijlpaal juicht iedereen.
 * Alle medewerkers samen zijn een paar tientallen InstancedMeshes (één tekenopdracht per onderdeel),
 * zodat het ook met veertig man soepel blijft. De looproutes komen uit nav.ts (A* over de kaart uit Blender).
 *
 * niels 2026-11-07: "poppetjes die niks aan het doen zijn ... met elkaar aan het kletsen en een beetje aan het
 * gamen" en "een trap omhoog ... dat poppetjes erop kunnen lopen". Wie geen werk heeft, loopt via de zijtrap op het
 * podium naar de bovenverdieping (upstairs.ts: kantine, gamekamer, lounge), gaat daar zitten of spelen en komt later
 * weer terug. De vaste cast uit de video's (staff.ts) staat in de afdeling waar hun hulp nodig is, met een eigen
 * houding: zingen in de microfoon, luisteren bij de briefing, poseren voor de fotoshoot, spelen voor de camera.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame, type ThreeEvent } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { mergeBufferGeometries } from 'three-stdlib';
import { loadNav, findPath, nearestFree, type Nav } from './nav';
import { Y1, groundY, stairPoint, stairStepY, STAIR_FOOT, STAIR_LAND, STAIR_LEN, useFloor, type Floor } from './floors';
import { buildNav1, SPOTS, occupied, type Spot, type SpotPose } from './upstairs';
import { STATUS, R_IN, R_OUT, SPAN, type Status } from './rooms';
import { reducedMotion, useWorld } from './useWorld';
import { useLive } from '../services/live';
import { useTalk, crewIndex, begin, spreek } from './talk';
import { personaOf, losZin } from './persona';
import { walkLock } from './walkState';
import { useCastModel, type CastModel } from './castModels';

type V2 = [number, number];
type V3 = [number, number, number];

/** De eigen stijl van een medewerker. */
export interface Look {
  top: 'hoodie' | 'trui' | 'shirt' | 'jas' | 'tee';
  topColor: string; // hoodie/trui/tee/jas: die kleur; shirt: wit met das in innerColor
  innerColor?: string; // das (shirt) of shirt onder het jasje
  hair: 'kaal' | 'kort' | 'kuif' | 'krul' | 'knot' | 'lang' | 'muts' | 'pet';
  hairColor: string;
  hatColor?: string;
  glasses?: string; beard?: boolean; moustache?: boolean; headphones?: string;
  pants: string; shoes: string; skin?: string;
}
/** vaste houding van de cast op hun plek */
export type CastAct = 'mic' | 'listen' | 'pose' | 'act' | 'chat';
export interface CrewMember {
  key: string; room: string; seat: number; status: Status; label: string; role?: string;
  task?: string; taskDone?: boolean; thread?: string; look: Look; big?: boolean;
  /** staat in plaats van te zitten (bijv. de derde in de crisiskamer bij het grote scherm); fl = verdieping,
   *  fixed = niet naar de looproutekaart schuiven (in de stemcabine) */
  standAt?: { p: V2; face: V2; fl?: Floor; fixed?: boolean };
  /** kleiner figuur (het broertje) */
  small?: boolean;
  /** houding op zijn plek (cast) */
  act?: CastAct;
  /** blijft op zijn plek: geen koffie en geen rondjes (cast aan het werk) */
  stay?: boolean;
  /** cast zonder klus: gaat vaak naar boven om te kletsen en te gamen */
  guest?: boolean;
  /** hover-tekst "Nu:" zolang hij op zijn plek is */
  doing?: string;
  /** het echte model uit de video's (castModels.tsx) in plaats van het poppetje, zodra het geladen is */
  model?: CastModel;
  onClick?: () => void;
}
export interface Handoff { from: string; to: string; label: string }

type Pose = 'stand' | 'talk' | 'pour' | 'listen' | SpotPose;
type Carry = 'none' | 'cup' | 'folder';
type Act =
  | { k: 'walk'; to: V2 }
  | { k: 'wait'; t: number; face?: V2; pose: Pose; carry?: Carry; meet?: number }
  | { k: 'carry'; c: Carry }
  /** naar een andere verdieping (via de zijtrap) en daar eventueel naar een plek */
  | { k: 'go'; fl: Floor; to?: V2 }
  | { k: 'stairs'; dir: 1 | -1 }
  /** op een plek boven: zitten of spelen */
  | { k: 'hang'; spot: Spot; t: number }
  | { k: 'up' } | { k: 'sit'; tried?: boolean };

interface Sim {
  m: CrewMember; seatP: V2; standP: V2 | null; stander: boolean; homeFace?: V2;
  x: number; z: number; yaw: number; y: number;
  sit: number; // 1 = zit, 0 = staat
  mode: 'sit' | 'up' | 'down' | 'walk' | 'wait' | 'climb' | 'hang';
  path: V2[]; pi: number; queue: Act[]; wait: number; pose: Pose; face?: V2; carry: Carry;
  next: number; phase: number; seed: number; look: number; lookT: number; meet: number; walkAmt: number;
  upFrom?: V2; upTo?: V2 | null; blink: number; stretch: number; target?: string; snapped?: boolean;
  /** verdieping waar hij nu is en waar zijn eigen plek is */
  fl: Floor; homeFl: Floor;
  /** trap: voortgang 0..1 en richting */
  cu: number; cdir: 1 | -1;
  /** plek boven (hang), gereserveerde plek, en of hij al opstaat */
  spot?: Spot; res?: string; leaving?: boolean; hangFrom?: V2;
  /** heuphoogte als hij zit (wereld): bureaustoel of een stoel boven */
  sitW: number;
  /** houding van de cast (kan wisselen: om de beurt in de stemcabine) */
  act?: CastAct;
}

/* ---------- maten (uit hoofdpersonage.glb, 1,77 m hoog; FIG schaalt naar het kantoor) ---------- */
const FIG = 0.9, BIG = 1.1;
const HIP = 0.70; // heuphoogte staand (modelmaat)
const HIP_SIT_W = 0.61; // heup op de zitting (wereldhoogte)
const SIT_Z = -0.05; // zittend iets naar het bureau toe
const THIGH = 0.33, SHIN = 0.30, UARM = 0.25, FARM = 0.19;
const SH_X = 0.2, SH_Y = 0.40; // schouder t.o.v. de heup
const HEAD_Y = 0.77, HEAD_R = 0.3;
const MAXN = 48;
const MAX_WALK = 8;
const MAX_UP = 13; // hooguit zoveel medewerkers tegelijk boven (niet te druk)
const SMALL = 0.74; // het broertje
const TURN = new Set<CastAct | undefined>(['mic', 'listen']);
const SPEED = 1.15;
const BIG_SPHERE = new THREE.Sphere(new THREE.Vector3(0, 1, 0), 40); // voor klikken op bewegende medewerkers
const SKIN = '#F1C19E'; // huid van het hoofdpersonage

const rnd = (a: number, b: number) => a + Math.random() * (b - a);
import { hash } from './seed';
export { hash };
const angDiff = (a: number, b: number) => { let d = b - a; while (d > Math.PI) d -= Math.PI * 2; while (d < -Math.PI) d += Math.PI * 2; return d; };
const yawTo = (dx: number, dz: number) => Math.atan2(-dx, -dz); // figuur kijkt naar -z

/** hoogte van de vloer: gang 0, afdeling 6 cm, tapijt 7,5 cm, podium 6 cm (sinds 9 nov) en de loopbrug vooraan */
function floorY(x: number, z: number) {
  const gy = groundY(x, z); if (gy !== null) return gy;
  const r = Math.hypot(x, z);
  if (r < R_IN - 0.02 || r > R_OUT + 0.02) return 0;
  const a = ((Math.atan2(x, z) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const slot = Math.round(a / SPAN); const da = Math.abs(angDiff(slot * SPAN, a));
  if (da > SPAN / 2 - 0.035) return 0; // spleet tussen afdelingen
  const carpet = r > R_IN + 1.0 && r < R_OUT - 1.0 && da < SPAN / 2 - 0.085;
  return carpet ? 0.075 : 0.06;
}

/* =================== geometrie =================== */
const tr = <G extends THREE.BufferGeometry>(g: G, x: number, y: number, z: number) => { g.translate(x, y, z); return g; };
const sc = <G extends THREE.BufferGeometry>(g: G, x: number, y: number, z: number) => { g.scale(x, y, z); return g; };
const sph = (r: number, w = 16, h = 12) => new THREE.SphereGeometry(r, w, h);
function limbGeo(r: number, len: number, seg = 10) { const g = new THREE.CapsuleGeometry(r, len, 4, seg); g.translate(0, -len / 2, 0); return g; }
function merge(list: THREE.BufferGeometry[]) {
  const norm = list.map((g) => { const x = g.index ? g : g; if (!x.getAttribute('uv')) x.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(x.getAttribute('position').count * 2), 2)); return x; });
  return mergeBufferGeometries(norm) ?? list[0];
}
function tint(g: THREE.BufferGeometry, r: number, gg: number, b: number) {
  const n = g.getAttribute('position').count; const a = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { a[i * 3] = r; a[i * 3 + 1] = gg; a[i * 3 + 2] = b; }
  g.setAttribute('color', new THREE.BufferAttribute(a, 3)); return g;
}
/**
 * Bolkapje boven op het hoofd (haar, muts). De onderrand ligt op poolhoek `front` vooraan (-z),
 * `side` opzij en `back` achteraan; `from` laat het kapje pas lager beginnen (een rand), `flare` laat
 * de onderkant uitwaaieren (lang haar).
 */
function capGeo(r: number, front: number, side: number, back: number, from = 0, flare = 0, segU = 36, segV = 12) {
  const pos: number[] = [], uv: number[] = [], idx: number[] = [];
  for (let j = 0; j <= segV; j++) for (let i = 0; i <= segU; i++) {
    const az = (i / segU) * Math.PI * 2; const c = Math.cos(az); // +1 achter, -1 voor
    const rim = c >= 0 ? side * (1 - c) + back * c : side * (1 + c) + front * -c;
    const f = from + (1 - from) * (j / segV); const th = f * rim; const rr = r * (1 + flare * f * f);
    pos.push(rr * Math.sin(th) * Math.sin(az), rr * Math.cos(th), rr * Math.sin(th) * c); uv.push(i / segU, 1 - j / segV);
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) { const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); return g;
}
/** iets (kegel, bol) op het hoofdoppervlak zetten, langs de normaal */
function onHead(g: THREE.BufferGeometry, th: number, az: number, r: number, tilt = 0) {
  const d = new THREE.Vector3(Math.sin(th) * Math.sin(az), Math.cos(th), Math.sin(th) * Math.cos(az));
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d);
  if (tilt) q.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), tilt));
  g.applyQuaternion(q); const p = d.multiplyScalar(r); g.translate(p.x, p.y, p.z); return g;
}
function beardGeo() {
  const pos: number[] = [], uv: number[] = [], idx: number[] = []; const segU = 24, segV = 8, W = 1.35;
  for (let j = 0; j <= segV; j++) for (let i = 0; i <= segU; i++) {
    const off = -W + (2 * W * i) / segU; const a = Math.abs(off) / W; const s = a * a * (3 - 2 * a);
    const th0 = 2.02 - 0.55 * s, th1 = 2.62 - 0.3 * a; const f = j / segV; const th = th0 + (th1 - th0) * f; const az = Math.PI + off;
    const rr = 0.31 + 0.012 * f;
    pos.push(rr * Math.sin(th) * Math.sin(az), rr * Math.cos(th), rr * Math.sin(th) * Math.cos(az)); uv.push(i / segU, 1 - f);
  }
  for (let j = 0; j < segV; j++) for (let i = 0; i < segU; i++) { const a = j * (segU + 1) + i, b = a + segU + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); return g;
}

/* ---------- het gezicht van het hoofdpersonage (4 uitdrukkingen naast elkaar) ---------- */
const FACE_W = 1.2, TH0 = 1.05, TH1 = 2.1; // breedte (rad) en poolhoeken van het gezichtsvlak
function faceAtlas() {
  const C = 256; const cv = document.createElement('canvas'); cv.width = C * 4; cv.height = C; const g = cv.getContext('2d')!;
  // modelmaat -> pixels: horizontaal over de boog, verticaal via de poolhoek
  const PX = (x: number) => C / 2 + Math.atan2(x, 0.29) * HEAD_R * (C / (FACE_W * HEAD_R));
  const PY = (y: number) => (Math.acos(Math.max(-1, Math.min(1, y / HEAD_R))) - TH0) * (C / (TH1 - TH0));
  const sx = C / (FACE_W * HEAD_R), sy = C / ((TH1 - TH0) * HEAD_R);
  const ell = (x: number, y: number, rx: number, ry: number, col: string) => { g.fillStyle = col; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2); g.fill(); };
  const DARK = '#2E211E', IRIS = '#885A2F', IRIS2 = '#764E28', TONGUE = '#DF6F69';
  const eyeOpen = (side: number) => {
    const ex = PX(side * 0.077), ey = PY(0.026);
    ell(ex, ey, 0.035 * sx, 0.044 * sy, '#100c0e');
    ell(ex, ey, 0.030 * sx, 0.039 * sy, '#F6EFE3');
    const ix = ex - side * 0.005 * sx, iy = ey + 0.003 * sy; // iris iets naar de neus en omlaag
    ell(ix, iy, 0.022 * sx, 0.026 * sy, IRIS); ell(ix, iy, 0.015 * sx, 0.014 * sy, IRIS2); ell(ix, iy, 0.011 * sx, 0.012 * sy, '#0b0809');
    ell(ex - side * 0.014 * sx, ey - 0.008 * sy, 0.005 * sx, 0.005 * sy, '#ffffff'); ell(ex + side * 0.002 * sx, ey + 0.013 * sy, 0.0022 * sx, 0.0022 * sy, '#ffffff');
  };
  const eyeArc = (side: number, up: boolean) => {
    const ex = PX(side * 0.077), ey = PY(0.026); g.strokeStyle = '#100c0e'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath();
    if (up) g.ellipse(ex, ey + 0.012 * sy, 0.03 * sx, 0.026 * sy, 0, Math.PI * 1.08, Math.PI * 1.92); else g.ellipse(ex, ey - 0.01 * sy, 0.03 * sx, 0.02 * sy, 0, Math.PI * 0.12, Math.PI * 0.88);
    g.stroke();
  };
  const brows = (lift = 0) => {
    g.strokeStyle = DARK; g.lineWidth = 0.014 * sy; g.lineCap = 'round';
    for (const side of [-1, 1]) {
      g.beginPath(); g.moveTo(PX(side * 0.045), PY(0.088 + lift)); g.quadraticCurveTo(PX(side * 0.075), PY(0.108 + lift), PX(side * 0.103), PY(0.09 + lift)); g.stroke();
    }
  };
  const mouth = (rx: number, ry: number, top = -0.078, round = false) => {
    const mx = C / 2, my = PY(top);
    g.save(); g.beginPath();
    if (round) g.ellipse(mx, my + ry * sy * 0.5, rx * sx, ry * sy * 0.55, 0, 0, Math.PI * 2); else g.ellipse(mx, my, rx * sx, ry * sy, 0, 0, Math.PI);
    g.closePath(); g.fillStyle = DARK; g.fill(); g.clip();
    ell(mx, PY(-0.1 - (round ? 0.006 : 0)) + (ry - 0.045) * sy * 0.6, 0.028 * sx * (rx / 0.055), 0.013 * sy * (ry / 0.045), TONGUE);
    g.restore();
  };
  for (let k = 0; k < 4; k++) {
    g.save(); g.translate(k * C, 0);
    if (k === 0) { eyeOpen(-1); eyeOpen(1); brows(); mouth(0.055, 0.045); }
    if (k === 1) { eyeArc(-1, false); eyeArc(1, false); brows(); mouth(0.055, 0.045); } // knipperen
    if (k === 2) { eyeArc(-1, true); eyeArc(1, true); brows(0.008); mouth(0.062, 0.058); } // blij / juichen
    if (k === 3) { eyeOpen(-1); eyeOpen(1); brows(0.004); mouth(0.034, 0.05, -0.074, true); } // praten
    g.restore();
  }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}

function buildGeos() {
  const torso = sc(tr(new THREE.CapsuleGeometry(0.2, 0.2, 8, 20), 0, 0.2, 0), 1, 1, 0.78);
  const ring = (R: number, tube: number, rx: number, y: number, z: number) => { const g = new THREE.TorusGeometry(R, tube, 10, 26); g.rotateX(rx); g.translate(0, y, z); return g; };
  const hood = merge([ring(0.105, 0.045, -1.97, 0.49, 0.04), tr(new THREE.BoxGeometry(0.22, 0.1, 0.03), 0, 0.06, -0.152)]);
  const string = (x: number) => { const c = new THREE.CylinderGeometry(0.009, 0.009, 0.17, 6); c.rotateX(0.18); c.translate(x, 0.365, -0.155); return c; };
  const strings = merge([string(-0.043), string(0.043), tr(sph(0.014, 8, 6), -0.043, 0.28, -0.162), tr(sph(0.014, 8, 6), 0.043, 0.28, -0.162)]);
  const collar = ring(0.108, 0.03, -1.75, 0.485, 0.01);
  const tie = (() => {
    const knot = tr(new THREE.BoxGeometry(0.05, 0.045, 0.03), 0, 0.43, -0.13);
    const blade = new THREE.CylinderGeometry(0.03, 0.045, 0.3, 4); blade.rotateY(Math.PI / 4); blade.scale(1, 1, 0.35); blade.rotateX(0.107); blade.translate(0, 0.265, -0.152);
    return merge([knot, blade]);
  })();
  const vpanel = (() => { const s = new THREE.Shape([new THREE.Vector2(0, 0), new THREE.Vector2(0.075, 0.24), new THREE.Vector2(-0.075, 0.24)]); const g = new THREE.ShapeGeometry(s); g.rotateX(0.165); g.translate(0, 0.2, -0.159); return g; })();
  const lapel = (() => {
    const one = (sd: number) => { const g = new THREE.BoxGeometry(0.035, 0.27, 0.016); g.rotateZ(-sd * 0.3); g.rotateX(0.165); g.translate(sd * 0.048, 0.33, -0.15); return g; };
    return merge([one(-1), one(1)]);
  })();
  const uarm = limbGeo(0.05, UARM), farm = limbGeo(0.046, FARM);
  const cuff = tr(new THREE.CylinderGeometry(0.051, 0.051, 0.05, 12), 0, -FARM + 0.012, 0);
  const hand = merge([
    tr(sc(sph(0.05, 12, 10), 0.85, 1.05, 0.7), 0, -FARM - 0.035, 0),
    tr(sc(sph(0.04, 10, 8), 0.8, 0.9, 0.62), 0, -FARM - 0.085, 0),
    tr(sc(sph(0.022, 8, 6), 1, 1.4, 1), 0, -FARM - 0.02, -0.042),
  ]);
  const thigh = limbGeo(0.068, THIGH), shin = limbGeo(0.064, SHIN);
  const shoe = tr(sc(sph(0.072, 16, 10), 0.95, 0.75, 1.5), 0, -0.015, -0.04);
  const head = sph(HEAD_R, 30, 22);
  const face = new THREE.SphereGeometry(HEAD_R * 1.006, 22, 16, Math.PI * 1.5 - FACE_W / 2, FACE_W, TH0, TH1 - TH0);
  face.setAttribute('aFace', new THREE.InstancedBufferAttribute(new Float32Array(MAXN), 1));
  const ear = merge([tint(sc(sph(0.082, 14, 10), 0.5, 1, 0.75), 1, 1, 1), tint(tr(sc(sph(0.05, 12, 8), 0.3, 0.7, 0.5), 0.03, 0, -0.012), 0.8, 0.72, 0.7)]);
  // haar en hoofddeksels
  const kort = capGeo(0.31, 0.76, 1.45, 1.85);
  const kuif = merge([capGeo(0.308, 0.72, 1.35, 1.75), ...[[0.28, Math.PI, 0.16], [0.42, Math.PI - 0.55, 0.13], [0.42, Math.PI + 0.55, 0.13], [0.55, Math.PI, 0.15], [0.18, Math.PI - 0.9, 0.12], [0.18, Math.PI + 0.9, 0.12], [0.1, 0.4, 0.11], [0.35, 0.3, 0.1]].map(([th, az, h]) => {
    const c = new THREE.ConeGeometry(0.055, h, 8); c.translate(0, h / 2, 0); return onHead(c, th, az, 0.285, -0.35);
  })]);
  const krul = merge([capGeo(0.302, 0.8, 1.45, 1.8), ...Array.from({ length: 34 }, (_, i) => {
    const y = 1 - (i + 0.5) / 34 * 1.1; const th = Math.acos(Math.max(-1, Math.min(1, y))); const az = i * 2.399963; const c = Math.cos(az);
    const rim = c >= 0 ? 1.45 * (1 - c) + 1.8 * c : 1.45 * (1 + c) + 0.8 * -c;
    if (th > rim - 0.12) return null;
    return onHead(sph(0.07 + (i % 3) * 0.006, 10, 8), th, az, 0.302);
  }).filter((g): g is THREE.SphereGeometry => !!g)]);
  const knot = merge([capGeo(0.31, 0.76, 1.42, 1.8), tr(sph(0.115, 16, 12), 0, 0.28, 0.172)]);
  const lang = capGeo(0.318, 0.74, 1.95, 2.15, 0, 0.12);
  const muts = merge([capGeo(0.322, 0.92, 1.3, 1.6), capGeo(0.338, 0.92, 1.3, 1.6, 0.76), tr(sph(0.075, 12, 10), 0, 0.392, 0.03)]);
  const pet = (() => {
    const visor = new THREE.CylinderGeometry(0.2, 0.2, 0.018, 20, 1, false, Math.PI / 2, Math.PI); visor.scale(1, 1, 1.05); visor.rotateX(-0.22); visor.translate(0, 0.176, -0.25);
    return merge([capGeo(0.316, 0.98, 1.3, 1.45), tr(sph(0.022, 8, 6), 0, 0.318, 0), visor]);
  })();
  const beard = beardGeo();
  const moustache = (() => { const g = new THREE.CapsuleGeometry(0.022, 0.07, 4, 8); g.rotateZ(Math.PI / 2); g.scale(1, 0.8, 0.6); g.translate(0, -0.052, -0.297); return g; })();
  const glasses = (() => {
    const rg = (x: number) => tr(new THREE.TorusGeometry(0.052, 0.009, 6, 22), x, 0.026, -0.3);
    const bridge = new THREE.CylinderGeometry(0.007, 0.007, 0.05, 6); bridge.rotateZ(Math.PI / 2); bridge.translate(0, 0.04, -0.305);
    return merge([rg(-0.077), rg(0.077), bridge, tr(new THREE.BoxGeometry(0.012, 0.012, 0.09), -0.13, 0.03, -0.265), tr(new THREE.BoxGeometry(0.012, 0.012, 0.09), 0.13, 0.03, -0.265)]);
  })();
  const phones = (() => {
    const band = new THREE.TorusGeometry(0.335, 0.022, 8, 28, Math.PI); band.translate(0, -0.01, 0.02);
    const cup = (x: number) => { const c = new THREE.CylinderGeometry(0.085, 0.085, 0.07, 18); c.rotateZ(Math.PI / 2); c.translate(x, -0.02, 0.01); return c; };
    return merge([band, cup(-0.335), cup(0.335)]);
  })();
  return {
    torso, hood, strings, collar, tie, vpanel, lapel, uarm, farm, cuff, hand, thigh, shin, shoe, head, face, ear,
    kort, kuif, krul, knot, lang, muts, pet, beard, moustache, glasses, phones,
    dot: new THREE.SphereGeometry(0.075, 12, 10),
    ring: (() => { const g = new THREE.RingGeometry(0.36, 0.43, 32); g.rotateX(-Math.PI / 2); return g; })(),
    blob: (() => { const g = new THREE.PlaneGeometry(1.0, 1.0); g.rotateX(-Math.PI / 2); return g; })(),
    cup: (() => { const g = new THREE.CylinderGeometry(0.042, 0.036, 0.1, 12); g.translate(0, 0.05, 0); return g; })(),
    folder: (() => { const g = new THREE.BoxGeometry(0.035, 0.3, 0.23); g.translate(0, 0, -0.02); return g; })(),
  };
}
type Geos = ReturnType<typeof buildGeos>;
type PartKey = keyof Geos;
const HAIRS = ['kort', 'kuif', 'krul', 'knot', 'lang', 'muts', 'pet'] as const;

/** Hoe vaak een onderdeel per medewerker voorkomt (2 = links en rechts). */
const PER: Partial<Record<PartKey, number>> = { uarm: 2, farm: 2, cuff: 2, hand: 2, thigh: 2, shin: 2, shoe: 2, ear: 2 };

const shade = (hex: string, f: number) => { const c = new THREE.Color(hex); if (f > 1) c.lerp(new THREE.Color('#ffffff'), f - 1); else c.multiplyScalar(f); return '#' + c.getHexString(); };

export function Crew({ members, seats, chairs, handoffs, onHoverRoom, roomName }: {
  members: CrewMember[]; seats: Record<string, V3[]>; chairs?: Record<string, THREE.Object3D[]>; handoffs: Handoff[];
  onHoverRoom?: (room: string | null) => void; roomName?: (room: string) => string;
}) {
  const [nav, setNav] = useState<Nav | null>(null);
  useEffect(() => { let on = true; loadNav().then((n) => on && setNav(n)); return () => { on = false; }; }, []);
  const party = useWorld((s) => s.party);
  const partyAt = useRef(-99);
  useEffect(() => { if (party) partyAt.current = performance.now() / 1000; }, [party]);

  // ---- simulatie (blijft bestaan als de lijst ververst; sleutel = afdeling:stoel) ----
  const sims = useRef<Sim[]>([]);
  // bij het openen en net nadat de echte gegevens binnenkomen: nieuwe plekken meteen innemen in plaats van erheen te lopen
  const boot = useRef(performance.now()); const firstLive = useRef(0); const booted = useRef(new Set<string>());
  const list = useMemo(() => members.filter((m) => m.standAt || seats[m.room]?.[m.seat]).slice(0, MAXN), [members, seats]);
  useEffect(() => { crewIndex.members = new Map(list.map((m) => [m.key, m])); }, [list]);
  useMemo(() => {
    const old = new Map(sims.current.map((s) => [s.m.key, s]));
    const now0 = performance.now();
    if (!firstLive.current && useLive.getState().source !== 'ingebouwd') firstLive.current = now0;
    const booting = now0 - boot.current < 20000 || (!!firstLive.current && now0 - firstLive.current < 8000);
    sims.current = list.map((m) => {
      const o = old.get(m.key);
      const home: V2 = m.standAt ? m.standAt.p : [seats[m.room][m.seat][0], seats[m.room][m.seat][2] + 0.06];
      const hf: Floor = m.standAt?.fl ?? 0; const stander = !!m.standAt;
      if (o) {
        // andere rol of plek (de cast gaat naar een andere klus, het hoofdpersonage naar de fotoshoot): erheen lopen
        const moved = o.stander !== stander || o.homeFl !== hf || (stander && Math.hypot(o.seatP[0] - home[0], o.seatP[1] - home[1]) > 0.05);
        // andere stoel (bv. als het Blender-kantoor binnenkomt): opstaplek opnieuw bepalen
        if (!o.stander && !moved && (o.seatP[0] !== home[0] || o.seatP[1] !== home[1])) o.standP = null;
        const wasStander = o.stander;
        // om de beurt in de stemcabine: die wissel blijft staan als de lijst ververst
        if (o.m.room === m.room && TURN.has(o.act) && TURN.has(m.act)) { o.m = m; return o; }
        o.m = m; o.seatP = home; o.homeFace = m.standAt?.face; o.snapped = false; o.act = m.act;
        if (moved) {
          o.stander = stander; o.homeFl = hf; o.standP = stander ? home : null;
          if (booting && o.mode !== 'climb' && o.mode !== 'hang') { // net geopend: meteen op de nieuwe plek
            o.queue = []; o.path = []; o.fl = hf; o.x = home[0]; o.z = home[1]; o.y = hf === 1 ? Y1 : 0; o.sit = stander ? 0 : 1; o.mode = 'sit'; o.carry = 'none';
            o.yaw = stander && m.standAt ? yawTo(m.standAt.face[0] - home[0], m.standAt.face[1] - home[1]) : 0;
          // (het volgende beeld begint de rij: nextAct hier kan nog niet, de hooks eronder bestaan dan nog niet)
          } else if (o.mode === 'sit') { o.queue = [...(wasStander ? [] : [{ k: 'up' } as Act]), { k: 'sit' }]; kick(o); }
        }
        return o;
      }
      const seed = hash(m.key);
      const s = {
        m, seatP: home, standP: stander ? home : null, stander, homeFace: m.standAt?.face, x: home[0], z: home[1], y: hf === 1 ? Y1 : 0,
        yaw: stander && m.standAt ? yawTo(m.standAt.face[0] - home[0], m.standAt.face[1] - home[1]) : 0, sit: stander ? 0 : 1, mode: 'sit',
        path: [], pi: 0, queue: [], wait: 0, pose: 'stand', carry: 'none', next: rnd(4, 26) + seed * 10, phase: seed * 6, seed,
        look: 0, lookT: 0, meet: -1, walkAmt: 0, blink: rnd(1, 5), stretch: rnd(10, 40),
        fl: hf, homeFl: hf, cu: 0, cdir: 1, sitW: HIP_SIT_W, act: m.act,
      } as Sim;
      return s;
    });
    // bij het openen zit een deel van wie niets te doen heeft al boven (kantine, gamekamer)
    if (booting) {
      let n = sims.current.filter((s) => s.fl === 1 && s.homeFl === 0).length;
      for (const s of sims.current) {
        if (booted.current.has(s.m.key) || !(s.m.status === 'klaar' || s.m.status === 'offline')) continue;
        booted.current.add(s.m.key);
        if (n >= 7 || s.stander || s.m.stay || s.mode !== 'sit' || hash(s.m.key + 'boven') > 0.45) continue;
        const spot = pickSpot(); if (!spot) break;
        occupied.set(spot.id, 1); s.res = spot.id; s.fl = 1; s.x = spot.p[0]; s.z = spot.p[1]; s.y = Y1; s.sit = 0;
        s.yaw = yawTo(spot.face[0] - s.x, spot.face[1] - s.z);
        s.queue = [{ k: 'hang', spot, t: reducedMotion() ? 1e9 : rnd(25, 110) }, { k: 'sit' }]; kick(s); n++;
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [list, seats]);

  /** de rij acties beginnen in het volgende beeld */
  function kick(s: Sim) { s.mode = 'wait'; s.wait = 0; s.meet = -1; s.face = undefined; s.pose = 'stand'; }
  /** een vrije plek boven; liefst bij iemand die er al zit (dan kletsen of spelen ze samen) */
  function pickSpot(): Spot | null {
    const free = SPOTS.filter((sp) => !occupied.has(sp.id));
    if (!free.length) return null;
    const busy = new Set(SPOTS.filter((sp) => occupied.has(sp.id) && sp.group).map((sp) => sp.group));
    const w = free.map((sp) => (sp.group && busy.has(sp.group) ? 4 : 1) * (sp.zone === 'kantine' ? 1.1 : 1));
    let r = Math.random() * w.reduce((a, b) => a + b, 0);
    for (let i = 0; i < free.length; i++) { r -= w[i]; if (r <= 0) return free[i]; }
    return free[free.length - 1];
  }

  // alleen bij lokaal testen: waar is iedereen
  useEffect(() => {
    if (window.location?.hostname !== 'localhost') return;
    (window as unknown as { __dmCrew: unknown }).__dmCrew = () => sims.current.map((s) => ({ key: s.m.key, room: s.m.room, st: s.m.status, home: s.seatP.map((v) => +v.toFixed(2)), mode: s.mode, fl: s.fl, homeFl: s.homeFl, x: +s.x.toFixed(2), z: +s.z.toFixed(2), y: +s.y.toFixed(2), spot: s.spot?.id, act: s.act, q: s.queue.map((a) => a.k).join(',') }));
  }, []);

  // ---- onderdelen en materialen ----
  const geos = useMemo(buildGeos, []);
  const faceTex = useMemo(faceAtlas, []);
  const mats = useMemo(() => {
    // glans-look van de video's (punt 33): vinyl met een heldere lak
    const vinyl = new THREE.MeshPhysicalMaterial({ roughness: 0.4, clearcoat: 1, clearcoatRoughness: 0.1, metalness: 0 });
    const vinyl2 = vinyl.clone(); vinyl2.side = THREE.DoubleSide;
    const skin = new THREE.MeshPhysicalMaterial({ roughness: 0.48, sheen: 0.6, sheenRoughness: 0.5, sheenColor: new THREE.Color('#ffb59a'), clearcoat: 0.7, clearcoatRoughness: 0.12 });
    const skinV = skin.clone(); skinV.vertexColors = true;
    const hair = new THREE.MeshPhysicalMaterial({ roughness: 0.5, clearcoat: 0.8, clearcoatRoughness: 0.15, side: THREE.DoubleSide });
    const face = new THREE.MeshPhysicalMaterial({ map: faceTex, alphaTest: 0.5, roughness: 0.48, clearcoat: 0.3, clearcoatRoughness: 0.45, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    face.onBeforeCompile = (sh) => {
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aFace;')
        .replace('#include <uv_vertex>', '#include <uv_vertex>\n#ifdef USE_MAP\n  vMapUv.x = (vMapUv.x + aFace) * 0.25;\n#endif');
    };
    face.customProgramCacheKey = () => 'dm-face-atlas';
    const gloss = new THREE.MeshPhysicalMaterial({ roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.1, metalness: 0.1 });
    const glow = new THREE.MeshBasicMaterial({ toneMapped: false });
    const ring = new THREE.MeshBasicMaterial({ toneMapped: false, transparent: true, opacity: 0.8, depthWrite: false });
    const bt = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d')!; const gr = g.createRadialGradient(32, 32, 2, 32, 32, 31); gr.addColorStop(0, 'rgba(0,0,0,0.55)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
    const blob = new THREE.MeshBasicMaterial({ map: bt, transparent: true, depthWrite: false, toneMapped: false });
    const cup = new THREE.MeshPhysicalMaterial({ color: '#f4f6fb', roughness: 0.3, clearcoat: 0.6 });
    const folder = new THREE.MeshPhysicalMaterial({ roughness: 0.5, clearcoat: 0.4 });
    return { vinyl, vinyl2, skin, skinV, hair, face, gloss, glow, ring, blob, cup, folder };
  }, [faceTex]);
  const PARTS: [PartKey, THREE.Material, boolean][] = useMemo(() => [
    ['torso', mats.vinyl, true], ['hood', mats.vinyl2, false], ['strings', mats.vinyl, false], ['collar', mats.vinyl, false], ['tie', mats.vinyl, false],
    ['vpanel', mats.vinyl2, false], ['lapel', mats.vinyl, false],
    ['uarm', mats.vinyl, false], ['farm', mats.vinyl, false], ['cuff', mats.vinyl, false], ['hand', mats.skin, false],
    ['thigh', mats.vinyl, false], ['shin', mats.vinyl, false], ['shoe', mats.vinyl, false],
    ['head', mats.skin, true], ['face', mats.face, false], ['ear', mats.skinV, false],
    ['kort', mats.hair, false], ['kuif', mats.hair, false], ['krul', mats.hair, false], ['knot', mats.hair, false], ['lang', mats.hair, false],
    ['muts', mats.vinyl2, false], ['pet', mats.vinyl2, false], ['beard', mats.hair, false], ['moustache', mats.hair, false],
    ['glasses', mats.gloss, false], ['phones', mats.gloss, false],
    ['dot', mats.glow, false], ['ring', mats.ring, false], ['blob', mats.blob, false], ['cup', mats.cup, false], ['folder', mats.folder, false],
  ], [mats]);
  const refs = useRef<Partial<Record<PartKey, THREE.InstancedMesh | null>>>({});
  const inited = useRef(new WeakSet<THREE.InstancedMesh>());
  const R = (k: PartKey, cap: number) => (el: THREE.InstancedMesh | null) => {
    refs.current[k] = el;
    if (el && !inited.current.has(el)) {
      inited.current.add(el); el.boundingSphere = BIG_SPHERE; el.count = 0;
      el.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(cap * 3).fill(1), 3);
    }
  };

  // kleuren per medewerker
  useEffect(() => {
    const c = new THREE.Color();
    const set = (k: PartKey, i: number, col: string) => { const m = refs.current[k]; if (m) m.setColorAt(i, c.set(col)); };
    sims.current.forEach((s, i) => {
      const L = s.m.look; const skin = L.skin ?? SKIN;
      const torsoCol = L.top === 'shirt' ? '#F3F4F8' : L.topColor;
      const sleeve = L.top === 'shirt' ? '#F3F4F8' : L.topColor;
      set('torso', i, torsoCol); set('hood', i, L.topColor); set('strings', i, '#F5F2EA');
      set('collar', i, L.top === 'shirt' ? '#FFFFFF' : shade(L.topColor, 0.86)); set('tie', i, L.innerColor ?? '#FF7A24');
      set('vpanel', i, L.innerColor ?? '#F3F4F8'); set('lapel', i, shade(L.topColor, 0.8));
      set('head', i, skin); set('face', i, '#ffffff');
      for (const h of HAIRS) set(h, i, h === 'muts' || h === 'pet' ? (L.hatColor ?? L.hairColor) : L.hairColor);
      set('beard', i, L.hairColor); set('moustache', i, L.hairColor);
      set('glasses', i, L.glasses ?? '#1C1F2B'); set('phones', i, L.headphones ?? '#1C1F2B');
      for (const sd of [0, 1]) {
        const j = i * 2 + sd;
        set('uarm', j, sleeve); set('farm', j, L.top === 'tee' ? skin : sleeve); set('hand', j, skin); set('ear', j, skin);
        set('cuff', j, L.top === 'trui' ? shade(L.topColor, 0.85) : L.top === 'jas' ? '#F3F4F8' : '#F5F2EA');
        set('thigh', j, L.pants); set('shin', j, L.pants); set('shoe', j, L.shoes);
      }
      const st = STATUS[s.m.status].kleur; set('dot', i, st); set('ring', i, st);
      set('folder', i, s.m.room === 'stem' ? '#21D6C4' : s.m.room === 'script' ? '#FF6A3D' : '#FACC15');
    });
    Object.values(refs.current).forEach((m) => { if (m?.instanceColor) m.instanceColor.needsUpdate = true; });
  }, [list]);

  // ---- hover ----
  const [hover, setHover] = useState<number | null>(null);
  const [nu, setNu] = useState<string | null>(null); const nuRef = useRef<string | null>(null);
  const label = useRef<THREE.Group>(null);
  /** groepen met het echte castmodel per medewerker (zie CrewModel hieronder) */
  const modelRefs = useRef(new Map<string, THREE.Group>());
  const idxOf = (e: ThreeEvent<PointerEvent | MouseEvent>) => { const i = e.instanceId ?? -1; return PER[e.object.name as PartKey] === 2 ? Math.floor(i / 2) : i; };
  const onOver = (e: ThreeEvent<PointerEvent>) => { e.stopPropagation(); const ii = idxOf(e); if (ii >= 0 && sims.current[ii]) { setHover(ii); onHoverRoom?.(sims.current[ii].m.room); document.body.style.cursor = 'pointer'; } };
  const onOut = () => { setHover(null); onHoverRoom?.(null); document.body.style.cursor = 'auto'; };
  const onClick = (e: ThreeEvent<MouseEvent>) => { e.stopPropagation(); const m = sims.current[idxOf(e)]?.m; if (!m) return; if (useWorld.getState().walk) begin(m); else m.onClick?.(); };
  const onDouble = (e: ThreeEvent<MouseEvent>) => { e.stopPropagation(); const m = sims.current[idxOf(e)]?.m; if (m) begin(m); };
  // praten: wie er vlak voor je staat, losse zinnetjes als je langsloopt, en tekstballonnetjes
  const talkT = useRef(0); const zegT = useRef(0); const gezegd = useRef(new Map<string, number>());
  const bubbles = useTalk((st) => st.bubbles); const bubbleRefs = useRef(new Map<string, THREE.Group>());

  // ---- gedrag ----
  const plansThisFrame = useRef(0);
  const handoffT = useRef(rnd(18, 35));
  const turnT = useRef(rnd(10, 18));
  const still = useMemo(() => reducedMotion(), []);

  /** looproutekaart van een verdieping (boven wordt hij pas gemaakt als iemand naar boven gaat) */
  const navOf = (fl: Floor): Nav | null => (fl === 1 ? buildNav1() : nav);
  const standPoint = (s: Sim): V2 | null => {
    if (s.stander) return s.seatP;
    if (!nav) return null;
    if (!s.standP) s.standP = nearestFree(nav, s.seatP[0], s.seatP[1] + 0.45);
    return s.standP;
  };
  const walking = () => sims.current.filter((s) => s.mode === 'walk' || s.mode === 'climb' || s.mode === 'up' || s.mode === 'down').length;
  const upstairs = () => sims.current.filter((s) => s.fl === 1 || s.res || s.mode === 'climb').length;
  const plan = (s: Sim, acts: Act[]) => { s.queue = [...(s.stander ? [] : [{ k: 'up' } as Act]), ...acts, { k: 'sit' }]; nextAct(s); };
  const nearPoint = (s: Sim, off: V2): V2 | null => nav ? nearestFree(nav, s.seatP[0] + off[0], s.seatP[1] + off[1]) : null;
  const release = (s: Sim) => { if (s.res) { occupied.delete(s.res); s.res = undefined; } };

  function nextAct(s: Sim) {
    const a = s.queue.shift();
    if (!a) { s.mode = 'sit'; s.next = rnd(20, 55); s.target = undefined; return; }
    if (a.k === 'up') {
      s.mode = 'up'; s.upFrom = [s.x, s.z];
      const n = navOf(s.fl); s.upTo = s.stander || !n ? [s.x, s.z] : nearestFree(n, s.x, s.z + 0.45);
      return;
    }
    if (a.k === 'carry') { s.carry = a.c; nextAct(s); return; }
    if (a.k === 'go') {
      if (s.fl !== a.fl) { // eerst naar de trap, dan de trap op of af
        s.queue.unshift({ k: 'walk', to: s.fl === 0 ? STAIR_FOOT : STAIR_LAND }, { k: 'stairs', dir: s.fl === 0 ? 1 : -1 }, a);
      } else if (a.to) s.queue.unshift({ k: 'walk', to: a.to });
      nextAct(s); return;
    }
    if (a.k === 'stairs') { s.mode = 'climb'; s.cdir = a.dir; s.cu = a.dir > 0 ? 0 : 1; s.carry = 'none'; return; }
    if (a.k === 'hang') {
      s.mode = 'hang'; s.spot = a.spot; s.res = a.spot.id; occupied.set(a.spot.id, 2); s.wait = a.t; s.pose = a.spot.pose; s.face = a.spot.face;
      s.leaving = false; s.hangFrom = [s.x, s.z]; s.carry = a.spot.pose === 'pour' ? 'none' : s.carry;
      return;
    }
    if (a.k === 'walk') {
      const n = navOf(s.fl); const p = n ? findPath(n, [s.x, s.z], a.to) : null; plansThisFrame.current++;
      if (!p) {
        // geen route (bv. boven nog geen kaart): terug naar de eigen plek, desnoods zonder lopen
        release(s); s.spot = undefined;
        if (s.fl !== s.homeFl) { s.fl = s.homeFl; const sp = standPoint(s) ?? s.seatP; s.x = sp[0]; s.z = sp[1]; }
        s.queue = [{ k: 'sit', tried: true }]; nextAct(s); return;
      }
      s.path = p; s.pi = 1; s.mode = 'walk'; return;
    }
    if (a.k === 'wait') { s.mode = 'wait'; s.wait = a.t; s.pose = a.pose; s.face = a.face; if (a.carry) s.carry = a.carry; s.meet = a.meet ?? -1; return; }
    if (a.k === 'sit') {
      if (s.fl !== s.homeFl) { s.queue.unshift({ k: 'go', fl: s.homeFl }, a); nextAct(s); return; } // eerst naar de eigen verdieping
      const sp = standPoint(s);
      if (sp && !a.tried && Math.hypot(s.x - sp[0], s.z - sp[1]) > 0.08) { // eerst terug naar de eigen plek lopen
        const n = navOf(s.fl); const p = n ? findPath(n, [s.x, s.z], sp) : null; plansThisFrame.current++;
        if (p) { s.queue.unshift({ k: 'sit', tried: true }); s.path = p; s.pi = 1; s.mode = 'walk'; return; }
      }
      s.carry = 'none'; s.target = undefined; release(s);
      if (s.stander) { s.mode = 'sit'; s.next = rnd(25, 60); s.pose = 'stand'; return; }
      s.mode = 'down'; s.upFrom = [s.x, s.z]; s.pose = 'stand'; return;
    }
  }

  /** naar boven: een plek in de kantine, de gamekamer of de lounge (soms daarna nog een tweede) */
  function goUp(s: Sim) {
    if (upstairs() >= MAX_UP) return false;
    const n1 = navOf(1); const spot = pickSpot(); if (!n1 || !spot) return false;
    const tp = nearestFree(n1, spot.p[0], spot.p[1]); if (!tp) return false;
    occupied.set(spot.id, 1); s.res = spot.id; s.target = undefined;
    const acts: Act[] = [{ k: 'go', fl: 1, to: tp }, { k: 'hang', spot, t: rnd(40, 120) }];
    plan(s, acts);
    return true;
  }

  function decide(s: Sim) {
    if (!nav || still || s.m.stay) { s.next = 60; return; }
    const st = s.m.status; const busy = st === 'werkt' || st === 'bezig';
    const idle = st === 'klaar' || st === 'offline' || !!s.m.guest;
    if (walking() >= MAX_WALK || plansThisFrame.current > 0) { s.next = rnd(2, 6); return; }
    if (busy && Math.random() < 0.7) { s.next = rnd(25, 60); return; }
    // niets te doen: naar boven om te kletsen en te gamen
    if (idle && Math.random() < (s.m.guest ? 0.9 : 0.55) && goUp(s)) return;
    const r = Math.random(); const coffee = nav.meta.coffee[s.m.room];
    const sp = standPoint(s); if (!sp) { s.next = 40; return; }
    if (s.homeFl === 1) { s.next = rnd(10, 30); return; } // gast boven: alleen de plekken boven
    if (r < 0.45 && coffee) { // koffie halen
      plan(s, [{ k: 'walk', to: coffee.p }, { k: 'wait', t: rnd(3.5, 6), face: coffee.l, pose: 'pour' }, { k: 'carry', c: 'cup' }, { k: 'walk', to: sp }]);
      return;
    }
    // naar een collega (vaker in de eigen afdeling)
    const others = sims.current.filter((o) => o !== s && o.mode === 'sit' && !o.stander && o.fl === 0 && (r < 0.75 ? o.m.room === s.m.room : o.m.room !== s.m.room));
    const o = others[Math.floor(Math.random() * others.length)];
    if (!o) { s.next = rnd(15, 40); return; }
    const side = Math.random() < 0.5 ? -0.66 : 0.66;
    const tp = nearPoint(o, [side, 0.35]); if (!tp) { s.next = 30; return; }
    const oi = sims.current.indexOf(o);
    s.target = o.m.room; o.next = Math.max(o.next, 45); // de collega blijft zitten tot het gesprek klaar is
    plan(s, [{ k: 'walk', to: tp }, { k: 'wait', t: rnd(5, 9), face: [o.seatP[0], o.seatP[1]], pose: 'talk', meet: oi }]);
  }

  function courier(h: Handoff) {
    if (!nav || still || walking() >= MAX_WALK) return false;
    const from = sims.current.filter((s) => s.m.room === h.from && s.mode === 'sit' && !s.stander);
    const to = sims.current.filter((s) => s.m.room === h.to && s.mode === 'sit' && !s.stander);
    const s = from[Math.floor(Math.random() * from.length)]; const o = to.find((x) => x.m.big) ?? to[0];
    if (!s || !o) return false;
    const tp = nearPoint(o, [0.66, 0.35]); if (!tp || !standPoint(s)) return false;
    s.target = h.to; o.next = Math.max(o.next, 45);
    plan(s, [{ k: 'carry', c: 'folder' }, { k: 'walk', to: tp }, { k: 'wait', t: 4.5, face: [o.seatP[0], o.seatP[1]], pose: 'talk', meet: sims.current.indexOf(o) }, { k: 'carry', c: 'none' }]);
    return true;
  }

  // ---- per beeld: bewegen + matrices ----
  const tmp = useMemo(() => ({
    root: new THREE.Matrix4(), a: new THREE.Matrix4(), b: new THREE.Matrix4(), c: new THREE.Matrix4(), chest: new THREE.Matrix4(), head: new THREE.Matrix4(),
    hr: new THREE.Matrix4(), hl: new THREE.Matrix4(), e: new THREE.Euler(0, 0, 0, 'ZXY'), q: new THREE.Quaternion(), v: new THREE.Vector3(), s: new THREE.Vector3(1, 1, 1),
    zero: new THREE.Matrix4().makeScale(0, 0, 0), earR: new THREE.Matrix4(), earL: new THREE.Matrix4(),
  }), []);
  useMemo(() => {
    const q = new THREE.Quaternion();
    tmp.earR.compose(new THREE.Vector3(0.299, -0.021, -0.021), q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0.25), new THREE.Vector3(1, 1, 1));
    tmp.earL.compose(new THREE.Vector3(-0.299, -0.021, -0.021), q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI - 0.25), new THREE.Vector3(1, 1, 1));
  }, [tmp]);

  const doing = (s: Sim) => s.mode === 'hang' && s.spot ? s.spot.doing
    : s.mode === 'climb' ? (s.cdir > 0 ? 'loopt de trap op naar de kantine' : 'loopt de trap af')
      : s.fl === 1 && s.homeFl === 0 ? 'heeft pauze boven'
        : (s.mode === 'sit' || s.mode === 'down') && s.m.doing ? s.m.doing
          : s.mode === 'sit' || s.mode === 'down' ? null
    : s.carry === 'folder' ? `brengt een map${s.target && roomName ? ` naar ${roomName(s.target)}` : ''}`
      : s.carry === 'cup' || s.pose === 'pour' ? 'haalt koffie'
        : s.target && s.target !== s.m.room && roomName ? `overlegt bij ${roomName(s.target)}` : s.target ? 'overlegt met een collega' : 'loopt even rond';
  useFrame(({ clock, camera }, dtRaw) => {
    const dt = Math.min(0.05, dtRaw); const t = clock.elapsedTime; const now = performance.now() / 1000;
    const talkKey = useTalk.getState().open?.key; const walkOn = useWorld.getState().walk;
    plansThisFrame.current = 0;
    const cheer = now - partyAt.current < 4.5;
    const all = sims.current;
    // overdracht van een map naar de volgende afdeling
    handoffT.current -= dt;
    if (handoffT.current <= 0) { handoffT.current = rnd(40, 75); const h = handoffs[Math.floor(Math.random() * handoffs.length)]; if (h) courier(h); }

    // stemcabine: om de beurt aan de microfoon (wie klaar is, gaat achteraan staan)
    turnT.current -= dt;
    if (turnT.current <= 0) {
      turnT.current = rnd(16, 26);
      const mic = all.find((s) => s.act === 'mic' && s.mode === 'sit');
      const wait = mic ? all.filter((s) => s !== mic && s.act === 'listen' && s.m.room === mic.m.room && s.mode === 'sit') : [];
      const nx = wait[Math.floor(Math.random() * wait.length)];
      if (mic && nx) {
        const a = { p: mic.seatP, f: mic.homeFace }; mic.seatP = nx.seatP; mic.homeFace = nx.homeFace; mic.standP = nx.seatP; nx.seatP = a.p; nx.homeFace = a.f; nx.standP = a.p;
        mic.act = 'listen'; nx.act = 'mic';
        for (const s of [mic, nx]) { s.queue = [{ k: 'sit' }]; kick(s); }
      }
    }
    // stoelen eerst terug op hun plek; hieronder schuiven alleen de stoelen van de huidige medewerkers opzij
    if (chairs) for (const arr of Object.values(chairs)) for (const ch of arr) { const b = ch?.userData.base as THREE.Vector3 | undefined; if (b) ch.position.z = b.z; }
    for (const s of all) {
      // een staande medewerker op de dichtstbijzijnde vrije plek zetten (niet in een tafel)
      if (s.stander && !s.snapped && !s.m.standAt?.fixed) { const n = navOf(s.homeFl); if (n) { s.snapped = true; const p = nearestFree(n, s.seatP[0], s.seatP[1]); if (p) { s.seatP = p; s.standP = p; } } }
      // ---- toestand ----
      if (talkKey === s.m.key) {
        // in gesprek: blijft staan (of zitten) en kijkt naar jou
        s.walkAmt = Math.max(0, s.walkAmt - dt * 4);
        const dx = camera.position.x - s.x, dz = camera.position.z - s.z;
        if (s.sit < 0.5) s.yaw += angDiff(s.yaw, yawTo(dx, dz)) * Math.min(1, dt * 5);
        else { s.look = THREE.MathUtils.clamp(angDiff(s.mode === 'hang' ? s.yaw : s.stander ? s.yaw : 0, yawTo(dx, dz)), -1.3, 1.3); s.lookT = 0.5; }
      } else if (s.mode === 'sit') {
        s.walkAmt = Math.max(0, s.walkAmt - dt * 4);
        s.x += (s.seatP[0] - s.x) * Math.min(1, dt * 6); s.z += (s.seatP[1] - s.z) * Math.min(1, dt * 6);
        if (s.stander) { s.sit = 0; if (s.homeFace) s.yaw += angDiff(s.yaw, yawTo(s.homeFace[0] - s.x, s.homeFace[1] - s.z)) * Math.min(1, dt * 4); }
        else { s.sit = Math.min(1, s.sit + dt * 2); s.yaw += angDiff(s.yaw, 0) * Math.min(1, dt * 5); }
        s.next -= dt; if (s.next <= 0 && plansThisFrame.current === 0) decide(s);
      } else if (s.mode === 'up' || s.mode === 'down') {
        const sp = standPoint(s) ?? s.seatP;
        s.sit += (s.mode === 'up' ? -1 : 1) * dt * 1.6;
        const k = THREE.MathUtils.clamp(s.sit, 0, 1);
        const from = s.upFrom ?? (s.mode === 'up' ? s.seatP : sp); const to = s.mode === 'up' ? (s.upTo ?? sp) : s.seatP;
        const w = s.mode === 'up' ? THREE.MathUtils.smoothstep(1 - k, 0.35, 1) : THREE.MathUtils.smoothstep(k, 0, 0.65);
        s.x = from[0] + (to[0] - from[0]) * w; s.z = from[1] + (to[1] - from[1]) * w;
        if (s.mode === 'down') s.yaw += angDiff(s.yaw, 0) * Math.min(1, dt * 6);
        if (s.mode === 'up' && s.sit <= 0) { s.sit = 0; nextAct(s); } else if (s.mode === 'down' && s.sit >= 1) { s.sit = 1; s.mode = 'sit'; s.next = rnd(25, 70); }
      } else if (s.mode === 'walk') {
        const p = s.path[s.pi];
        if (!p) { nextAct(s); } else {
          const dx = p[0] - s.x, dz = p[1] - s.z; const d = Math.hypot(dx, dz);
          const step = SPEED * dt * Math.min(1, 0.35 + s.walkAmt);
          if (d <= step) { s.x = p[0]; s.z = p[1]; s.pi++; if (s.pi >= s.path.length) nextAct(s); }
          else { s.x += (dx / d) * step; s.z += (dz / d) * step; s.yaw += angDiff(s.yaw, yawTo(dx, dz)) * Math.min(1, dt * 7); }
          s.walkAmt = Math.min(1, s.walkAmt + dt * 3); s.phase += dt * SPEED * 6.6;
        }
      } else if (s.mode === 'climb') {
        // de zijtrap op of af, trede voor trede (stairStepY hieronder)
        s.cu = THREE.MathUtils.clamp(s.cu + (s.cdir * SPEED * 0.8 * dt) / STAIR_LEN, 0, 1);
        const [px, , pz] = stairPoint(s.cu); const dx = px - s.x, dz = pz - s.z;
        if (dx * dx + dz * dz > 1e-8) s.yaw += angDiff(s.yaw, yawTo(dx, dz)) * Math.min(1, dt * 8);
        s.x = px; s.z = pz; s.walkAmt = Math.min(1, s.walkAmt + dt * 3); s.phase += dt * SPEED * 6.6;
        if ((s.cdir > 0 && s.cu >= 1) || (s.cdir < 0 && s.cu <= 0)) { s.fl = s.cdir > 0 ? 1 : 0; nextAct(s); }
      } else if (s.mode === 'hang' && s.spot) {
        // boven: gaan zitten (stoel, kruk, racestoel, bank) of staan spelen; daarna weer opstaan
        const sp = s.spot; const from = s.hangFrom ?? sp.p;
        s.walkAmt = Math.max(0, s.walkAmt - dt * 4);
        if (sp.sit) s.sitW = Y1 + (sp.seatH ?? 0.45) + 0.14;
        if (!s.leaving) {
          s.wait -= dt;
          if (sp.sit) {
            s.sit = Math.min(1, s.sit + dt * 1.5); const w = THREE.MathUtils.smoothstep(s.sit, 0, 0.7);
            s.x = from[0] + (sp.sit[0] - from[0]) * w; s.z = from[1] + (sp.sit[1] - from[1]) * w;
          } else { s.x += (sp.p[0] - s.x) * Math.min(1, dt * 3); s.z += (sp.p[1] - s.z) * Math.min(1, dt * 3); }
          s.yaw += angDiff(s.yaw, yawTo(sp.face[0] - s.x, sp.face[1] - s.z)) * Math.min(1, dt * 5);
          if (s.wait <= 0) { s.leaving = true; s.hangFrom = sp.sit ? from : [s.x, s.z]; }
        } else {
          let done = true;
          if (sp.sit) {
            s.sit = Math.max(0, s.sit - dt * 1.5); const w = THREE.MathUtils.smoothstep(s.sit, 0.3, 1);
            s.x = from[0] + (sp.sit[0] - from[0]) * w; s.z = from[1] + (sp.sit[1] - from[1]) * w; done = s.sit <= 0;
          }
          if (done) { s.sit = 0; s.sitW = HIP_SIT_W; release(s); s.spot = undefined; s.leaving = false; nextAct(s); }
        }
      } else if (s.mode === 'wait') {
        s.walkAmt = Math.max(0, s.walkAmt - dt * 4); s.wait -= dt;
        if (s.face) s.yaw += angDiff(s.yaw, yawTo(s.face[0] - s.x, s.face[1] - s.z)) * Math.min(1, dt * 5);
        const o = s.meet >= 0 ? all[s.meet] : undefined;
        if (o && (o.mode === 'sit' || o.stander)) { o.lookT = 0.4; o.look = THREE.MathUtils.clamp(angDiff(o.stander ? o.yaw : 0, yawTo(s.x - o.x, s.z - o.z)), -1.3, 1.3); }
        else if (o) s.wait = Math.min(s.wait, 0.5); // collega is weg: gesprek kort afronden
        if (s.wait <= 0) { s.meet = -1; nextAct(s); }
      }
      s.lookT -= dt; if (s.lookT <= 0) s.look *= 1 - Math.min(1, dt * 2);
      s.blink -= dt; if (s.blink < -0.13) s.blink = rnd(2.2, 6);
      s.stretch -= dt; if (s.stretch < -1.8) s.stretch = rnd(14, 40);
      // stoel opzij schuiven als iemand opstaat
      const ch = chairs?.[s.m.room]?.[s.m.seat];
      if (ch && !s.stander) { const b = (ch.userData.base ??= ch.position.clone()) as THREE.Vector3; ch.position.z = b.z + (1 - s.sit) * 0.32; }
      const fy = s.mode === 'climb' ? stairStepY(s.z) : s.fl === 1 ? Y1 : floorY(s.x, s.z); s.y += (fy - s.y) * Math.min(1, dt * 12);
    }

    // ---- matrices ----
    const M = refs.current; const { root, a, b, c, e, q, v, s: sv, zero, chest, head, hr, hl, earR, earL } = tmp;
    const put = (k: PartKey, i: number, m: THREE.Matrix4) => { M[k]?.setMatrixAt(i, m); };
    const joint = (base: THREE.Matrix4, ox: number, oy: number, oz: number, pitch: number, roll: number, out: THREE.Matrix4) => {
      e.set(pitch, 0, roll); q.setFromEuler(e); out.compose(v.set(ox, oy, oz), q, sv.set(1, 1, 1)); out.premultiply(base); return out;
    };
    const faceAttr = geos.face.getAttribute('aFace') as THREE.InstancedBufferAttribute; const fa = faceAttr.array as Float32Array;
    const view = useFloor.getState().floor;
    all.forEach((s, i) => {
      const L = s.m.look;
      const k = THREE.MathUtils.clamp(s.sit, 0, 1); const wa = s.walkAmt; const ph = s.phase;
      const scale = FIG * (s.m.big ? BIG : 1) * (s.m.small ? SMALL : 1);
      const hang = s.mode === 'hang' ? s.pose : null; // houding boven (spel, racen, kletsen ...)
      const act = s.stander && s.mode === 'sit' ? s.act : undefined; // houding van de cast op hun plek
      // beneden kijken: wie boven is, zie je niet (de bovenverdieping is dan weg)
      const hidden = view === 0 && s.fl === 1 && s.mode !== 'climb';
      const done = s.m.status === 'klaar';
      const chr = cheer ? Math.max(0, Math.sin(Math.min(1, (now - partyAt.current) / 4.5) * Math.PI)) : 0;
      const str = done && s.mode === 'sit' && s.stretch < 0 ? Math.sin(Math.min(1, -s.stretch / 1.8) * Math.PI) : 0; // even uitrekken
      const up = Math.max(chr, str);
      const bob = wa * Math.abs(Math.sin(ph)) * 0.035 + chr * Math.abs(Math.sin(t * 9 + s.seed * 5)) * 0.06 * (1 - k * 0.7);
      const hipY = k * ((s.sitW - s.y) / scale) + (1 - k) * HIP + bob;
      const busy = (s.m.status === 'werkt' || s.m.status === 'bezig') && s.mode === 'sit' && !s.stander;
      // wortel: plek + draaiing (+ zittend iets naar het bureau)
      e.set(0, s.yaw, 0); q.setFromEuler(e);
      root.compose(v.set(s.x, s.y, s.z + (hang ? 0 : k * SIT_Z)), q, sv.set(scale, scale, scale));
      if (hidden) root.copy(zero);
      // echt castmodel geladen: poppetje weg, model volgt de plek (met een vinyl-huppel als hij loopt)
      const mg = s.m.model ? modelRefs.current.get(s.m.key) : undefined;
      if (mg && mg.userData.ready) {
        root.copy(zero);
        mg.visible = !hidden;
        mg.position.set(s.x, s.y + wa * Math.abs(Math.sin(ph)) * 0.07 + chr * Math.abs(Math.sin(t * 9 + s.seed * 5)) * 0.12, s.z);
        mg.rotation.set(0, s.yaw + Math.PI, Math.sin(ph) * 0.07 * wa);
      }
      // romp (licht voorover bij typen, achterover als het af is)
      const lean = k * (busy ? 0.14 : done ? -0.06 : 0.04) + wa * 0.06;
      joint(root, 0, hipY, 0, -lean, Math.sin(ph) * 0.03 * wa, chest); put('torso', i, chest);
      put('hood', i, L.top === 'hoodie' ? chest : zero); put('strings', i, L.top === 'hoodie' ? chest : zero);
      put('collar', i, L.top === 'trui' || L.top === 'tee' || L.top === 'shirt' ? chest : zero);
      put('tie', i, L.top === 'shirt' ? chest : zero);
      put('vpanel', i, L.top === 'jas' ? chest : zero); put('lapel', i, L.top === 'jas' ? chest : zero);
      // hoofd
      const chat = (s.pose === 'talk' && (s.mode === 'wait' || hang)) || act === 'chat' || act === 'act';
      const sing = act === 'mic';
      const nod = busy ? Math.sin(t * 1.3 + s.seed * 9) * 0.05 + 0.1 : chat ? Math.sin(t * 4 + s.seed * 3) * 0.07 : sing ? -0.12 + Math.sin(t * 3.1) * 0.06
        : hang === 'game' || hang === 'race' || hang === 'tv' ? 0.12 : up > 0 ? -0.15 * up : 0;
      const idleTurn = s.mode === 'sit' && !busy && !act ? Math.sin(t * 0.4 + s.seed * 7) * 0.5 : act === 'listen' ? Math.sin(t * 0.5 + s.seed * 7) * 0.2 : 0;
      e.set(nod, s.look + idleTurn, 0, 'YXZ'); q.setFromEuler(e); e.order = 'ZXY';
      head.compose(v.set(0, HEAD_Y, 0), q, sv.set(1, 1, 1)); head.premultiply(chest);
      put('head', i, head); put('face', i, head);
      const hideEars = L.hair === 'lang' || !!L.headphones;
      b.multiplyMatrices(head, earR); put('ear', i * 2 + 1, hideEars ? zero : b);
      b.multiplyMatrices(head, earL); put('ear', i * 2, hideEars ? zero : b);
      for (const h of HAIRS) put(h, i, L.hair === h ? head : zero);
      put('beard', i, L.beard ? head : zero); put('moustache', i, L.moustache ? head : zero);
      put('glasses', i, L.glasses ? head : zero); put('phones', i, L.headphones ? head : zero);
      // gezichtsuitdrukking: 0 gewoon, 1 knipperen, 2 blij, 3 praten
      // om de beurt praten aan tafel; de cast zingt in de microfoon of speelt voor de camera
      const praat = (bubbles[s.m.key]?.tot ?? 0) > now;
      const talking = praat || (s.mode === 'wait' && s.pose === 'talk') || ((hang === 'talk' || act === 'chat') && Math.sin(t * 0.55 + s.seed * 11) > 0.1) || sing || act === 'act';
      const glee = (hang === 'game' || hang === 'race' || hang === 'tv' || hang === 'paddle' || hang === 'foos' || act === 'pose') && Math.sin(t * 0.45 + s.seed * 4) > 0.55;
      fa[i] = up > 0.15 || glee ? 2 : s.blink < 0 ? 1 : talking ? (Math.sin(t * (sing ? 11 : 14) + s.seed * 3) > 0.2 ? 3 : 0) : done && Math.sin(t * 0.3 + s.seed * 6) > 0.6 ? 2 : 0;
      // status-bolletje boven het hoofd
      c.makeTranslation(0, 0.5 + Math.sin(t * 2.4 + s.seed * 4) * 0.04, 0); c.premultiply(head); put('dot', i, c);
      // benen (aan de wortel, niet aan de romp)
      for (const sd of [0, 1]) {
        const sg = sd ? 1 : -1; const sw = Math.sin(ph + (sd ? Math.PI : 0));
        const thigh = k * 1.45 + wa * sw * 0.5 * (1 - k);
        const knee = -k * 1.25 - wa * Math.max(0, -Math.sin(ph + (sd ? Math.PI : 0) + 0.9)) * 0.9 * (1 - k);
        joint(root, sg * 0.087, hipY, 0, thigh, 0, a); put('thigh', i * 2 + sd, a);
        joint(a, 0, -THIGH, 0, knee, 0, b); put('shin', i * 2 + sd, b);
        joint(b, 0, -SHIN, 0, -(thigh + knee) * 0.9 + k * 0.15, 0, c); put('shoe', i * 2 + sd, c);
      }
      // armen
      for (const sd of [0, 1]) {
        const sg = sd ? 1 : -1; const right = sd === 1;
        let sh = 0.06, el = 0.16, roll = sg * 0.26;
        if (k > 0.5) { // zittend
          if (busy) { const typ = Math.sin(t * (s.m.status === 'werkt' ? 15 : 10) + sd * 2.1 + s.seed * 5) * 0.07; sh = 0.72 + typ; el = 0.78 - typ; roll = sg * 0.1; }
          else { sh = 0.5; el = 0.95; roll = sg * 0.2; }
        } else if (s.mode === 'walk' || s.mode === 'climb') { sh = -Math.sin(ph + (sd ? Math.PI : 0)) * 0.45 * wa; el = 0.3; }
        else if (act) { // de cast op hun plek
          const j = Math.sin(t * 2.2 + s.seed * 5 + sd);
          if (act === 'mic') { if (right) { sh = 1.0; el = 1.75; roll = 0.35; } else { sh = 0.55 + j * 0.08; el = 0.6; roll = -0.2; } } // hand bij de koptelefoon, papiertje in de andere
          else if (act === 'listen') { sh = 0.62; el = 1.55; roll = -sg * 0.42; } // armen over elkaar
          else if (act === 'chat') { if (right) { sh = 0.55 + Math.sin(t * 3.2 + s.seed) * 0.25; el = 0.95; roll = 0.14; } }
          else if (act === 'act') { sh = 1.25 + Math.sin(t * 2.4 + sd * 2.6 + s.seed) * 0.55; el = 0.45; roll = sg * 0.35; } // groot spelen voor de camera
          else if (act === 'pose') { // fotoshoot: om de paar seconden een andere pose
            const pz = Math.floor((t + s.seed * 7) / 2.6) % 3;
            if (pz === 0) { sh = 2.7; el = 0.15; roll = sg * 0.45; } // armen omhoog
            else if (pz === 1) { if (right) { sh = 1.35; el = 0.2; roll = 0.1; } else { sh = 0.2; el = 1.4; roll = -0.9; } } // duim naar de camera, hand in de zij
            else { sh = 0.25; el = 1.5; roll = sg * 0.95; } // handen in de zij
          }
        }
        else if (s.stander && s.mode === 'sit') { // staand bij het scherm: wijzen en een tablet vasthouden
          if (right) { const pt = Math.max(0, Math.sin(t * 0.5 + s.seed * 3)); sh = 0.2 + pt * 1.3; el = 0.3 - pt * 0.2; roll = 0.2 + pt * 0.1; }
          else { sh = 0.55; el = 1.25; roll = -0.25; }
        }
        if (s.mode === 'wait' && s.pose === 'talk' && right) { sh = 0.55 + Math.sin(t * 3.2 + s.seed) * 0.25; el = 0.95; roll = 0.14; }
        if (praat && right && k < 0.5 && !hang) { sh = 0.55 + Math.sin(t * 3.4 + s.seed) * 0.3; el = 0.95; roll = 0.14; }
        if (hang) { // boven
          const j = Math.sin(t * 12 + sd * 1.7 + s.seed * 9) * 0.06;
          if (hang === 'game') { sh = 1.0 + j; el = 0.55 - j; roll = -sg * 0.08; } // knoppen en joystick van de gamekast
          else if (hang === 'race') { sh = 1.05; el = 0.5; roll = sg * 0.12 + Math.sin(t * 1.3 + s.seed * 4) * 0.18; } // sturen
          else if (hang === 'tv') { sh = 0.8 + j * 0.5; el = 1.2; roll = -sg * 0.18; } // controller
          else if (hang === 'paddle') { if (right) { sh = 0.7 + Math.sin(t * 4.2 + s.seed * 10) * 0.55; el = 0.55; roll = 0.3; } else { sh = 0.35; el = 0.6; } }
          else if (hang === 'foos') { sh = 0.7 + Math.sin(t * 7 + sd * 2) * 0.12; el = 0.35; roll = -sg * 0.05; }
          else if (hang === 'talk' && right && k > 0.5) { sh = 0.65 + Math.sin(t * 3.0 + s.seed) * 0.2; el = 1.0; roll = 0.12; }
          else if (hang === 'pour' && right) { sh = 1.15; el = 0.25; }
          else if (hang === 'look' && k > 0.5) { sh = 0.45; el = 1.0; roll = sg * 0.15; }
        }
        if (s.mode === 'wait' && s.pose === 'pour' && right) { sh = 1.15; el = 0.25; }
        if (s.carry === 'cup' && right && k < 0.5) { sh = 0.45; el = 1.35; roll = 0.16; }
        if (s.carry === 'folder' && !right && k < 0.5) { sh = 0.2; el = 1.2; roll = -0.26; }
        if (up > 0) { sh = sh * (1 - up) + (2.75 + Math.sin(t * 8 + sd) * 0.15 * chr) * up; el = el * (1 - up) + 0.2 * up; roll = roll * (1 - up) + sg * 0.4 * up; }
        joint(chest, sg * SH_X, SH_Y, 0, sh, roll, a); put('uarm', i * 2 + sd, a);
        joint(a, 0, -UARM, 0, el, 0, b); put('farm', i * 2 + sd, b); put('hand', i * 2 + sd, b);
        put('cuff', i * 2 + sd, L.top === 'tee' ? zero : b);
        (right ? hr : hl).copy(b);
      }
      // koffiebeker / map in de hand (de staande houdt de map als tablet)
      if (s.carry === 'cup' && k < 0.5) { c.makeTranslation(0, -FARM - 0.05, -0.02); c.premultiply(hr); put('cup', i, c); }
      else if ((s.mode === 'wait' && s.pose === 'pour') || hang === 'pour' || (hang === 'talk' && s.spot?.zone === 'kantine' && s.seed > 0.4)) { c.makeTranslation(0, -FARM - 0.06, 0); c.premultiply(hr); put('cup', i, c); }
      else put('cup', i, zero);
      if ((s.carry === 'folder' || (s.stander && s.mode === 'sit' && !act)) && k < 0.5) { c.makeTranslation(0.02, -FARM - 0.06, 0); c.premultiply(hl); put('folder', i, c); } else put('folder', i, zero);
      // ring en schaduw op de vloer
      q.identity(); c.compose(v.set(s.x, s.y + 0.012, s.z), q, sv.set(scale / FIG, 1, scale / FIG)); put('ring', i, hidden || s.mode === 'climb' ? zero : c);
      c.compose(v.set(s.x, s.y + 0.008, s.z + k * 0.02), q, sv.set((scale / FIG) * (1 + (1 - k) * 0.1), 1, scale / FIG)); put('blob', i, hidden ? zero : c);
    });
    faceAttr.needsUpdate = true;
    for (const [key, m] of Object.entries(M) as [PartKey, THREE.InstancedMesh | null][]) if (m) { m.count = all.length * (PER[key] ?? 1); m.instanceMatrix.needsUpdate = true; }
    { const d = hover !== null && all[hover] ? doing(all[hover]) : null; if (d !== nuRef.current) { nuRef.current = d; setNu(d); } }
    // ---- praten (alleen tijdens het rondlopen) ----
    talkT.current -= dt;
    if (talkT.current <= 0) {
      talkT.current = 0.15;
      const T = useTalk.getState();
      if (!walkOn) { if (T.near) T.setNear(null); }
      else {
        camera.getWorldDirection(v); const fx = v.x, fz = v.z; const fl = Math.hypot(fx, fz) || 1;
        let best: Sim | null = null; let bd = 2.6; let los: Sim | null = null; let ld = 4.6;
        for (const s of all) {
          if (s.fl !== view && s.mode !== 'climb') continue;
          const dx = s.x - camera.position.x, dz = s.z - camera.position.z; const d = Math.hypot(dx, dz);
          const dot = (dx * fx + dz * fz) / (fl * (d || 1));
          if (d < bd && dot > 0.5) { bd = d; best = s; }
          if (d < ld && dot > 0.35 && s.m.key !== talkKey) { ld = d; los = s; }
        }
        const nb = best ? personaOf(best.m) : null;
        T.setNear(best && nb ? { key: best.m.key, naam: nb.naam, kleur: nb.kleur, d: bd } : null);
        // als je langsloopt zegt iemand soms iets (niet te vaak, en niet als je al praat)
        zegT.current -= 0.15;
        if (los && !talkKey && !walkLock.on && zegT.current <= 0 && now - (gezegd.current.get(los.m.key) ?? -99) > 45 && Math.random() < 0.35) {
          zegT.current = rnd(6, 11); gezegd.current.set(los.m.key, now);
          const p = personaOf(los.m); const z = losZin(p, los.m); T.zeg(los.m.key, z);
          if (ld < 3.2) spreek(p, z);
        }
      }
      // verlopen ballonnetjes opruimen
      const b = T.bubbles; const weg = Object.keys(b).filter((k) => b[k].tot < now);
      if (weg.length) useTalk.setState((st) => { const nb2 = { ...st.bubbles }; weg.forEach((k) => delete nb2[k]); return { bubbles: nb2 }; });
    }
    for (const [key, g] of bubbleRefs.current) {
      const s = all.find((x) => x.m.key === key); if (!s) { g.visible = false; continue; }
      const scale = FIG * (s.m.big ? BIG : 1) * (s.m.small ? SMALL : 1);
      const top = s.sit > 0.5 ? s.sitW - s.y + (HEAD_Y + HEAD_R) * scale : (HIP + HEAD_Y + HEAD_R) * scale;
      g.position.set(s.x, s.y + top + 0.45, s.z); g.visible = !(view === 0 && s.fl === 1 && s.mode !== 'climb') && !(view === 1 && s.fl === 0 && s.mode !== 'climb');
    }
    if (hover !== null && label.current && all[hover]) {
      const s = all[hover]; const scale = FIG * (s.m.big ? BIG : 1) * (s.m.small ? SMALL : 1);
      const top = (s.sit > 0.5 ? s.sitW - s.y + (HEAD_Y + HEAD_R) * scale : (HIP + HEAD_Y + HEAD_R) * scale);
      label.current.position.set(s.x, s.y + top + 0.5, s.z);
    }
  });

  const hovered = hover !== null ? sims.current[hover] : null;
  return (
    <group>
      {PARTS.map(([k, mat, events]) => {
        const per = PER[k] ?? 1; const cap = MAXN * per;
        return (
          <instancedMesh key={k} name={k} ref={R(k, cap)} args={[geos[k], mat, cap]} frustumCulled={false} renderOrder={k === 'ring' || k === 'blob' ? 1 : 0}
            {...(events ? { onPointerOver: onOver, onPointerOut: onOut, onClick, onDoubleClick: onDouble } : { raycast: () => null })} />
        );
      })}
      {list.filter((m) => m.model).map((m) => (
        <CrewModel key={m.key} m={m} reg={(g) => { if (g) modelRefs.current.set(m.key, g); else modelRefs.current.delete(m.key); }}
          onOver={() => { const i = sims.current.findIndex((x) => x.m.key === m.key); if (i >= 0) { setHover(i); onHoverRoom?.(m.room); document.body.style.cursor = 'pointer'; } }}
          onOut={onOut} onClick={() => { if (useWorld.getState().walk) begin(m); else m.onClick?.(); }} onDouble={() => begin(m)} />
      ))}
      {Object.entries(bubbles).map(([key, bb]) => (
        <group key={key} ref={(g) => { if (g) bubbleRefs.current.set(key, g); else bubbleRefs.current.delete(key); }}>
          <Html center zIndexRange={[28, 18]} style={{ pointerEvents: 'none' }}>
            <div className="dm-ballon relative w-max max-w-[230px] rounded-2xl bg-white px-3 py-1.5 text-[13px] font-semibold leading-snug text-[#141a33] shadow-[0_6px_20px_rgba(0,0,0,.45)]">
              {bb.tekst}
              <span className="absolute -bottom-1.5 left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 bg-white" />
            </div>
          </Html>
        </group>
      ))}
      <group ref={label}>
        {hovered && (
          <Html center zIndexRange={[30, 20]} style={{ pointerEvents: 'none' }}>
            <div className="w-max max-w-[260px] rounded-lg border border-white/15 bg-[#0a1124]/92 px-2.5 py-1.5 text-[12px] text-slate-200 shadow-xl backdrop-blur">
              <div className="flex items-center gap-1.5 font-semibold text-white">
                <span className="inline-block h-2 w-2 shrink-0 rounded-full" style={{ background: STATUS[hovered.m.status].kleur }} />
                <span className="truncate">{hovered.m.label}{hovered.m.role ? <span className="font-normal text-slate-400"> · {hovered.m.role}</span> : null}</span>
              </div>
              {hovered.m.task && <div className="mt-0.5 leading-snug">{hovered.m.taskDone ? <span className="text-[#4ADE80]">✓ Klaar: </span> : <span className="text-sky-300">Verbetert: </span>}{hovered.m.task}</div>}
              {hovered.m.thread && <div className="mt-0.5 leading-snug text-slate-300"><span className="text-orange-300">Taak: </span>{hovered.m.thread}</div>}
              {nu && <div className="mt-0.5 text-slate-400">Nu: {nu}</div>}
              <div className="mt-0.5 text-[11px] text-[#FFB070]">{useWorld.getState().walk ? 'Klik of E: praten' : 'Dubbelklik: praten'}</div>
            </div>
          </Html>
        )}
      </group>
    </group>
  );
}

/** Eén echt castmodel; Crew zet elke frame de plek en draaiing. Zolang het laadt, staat het poppetje er nog. */
function CrewModel({ m, reg, onOver, onOut, onClick, onDouble }: { m: CrewMember; reg: (g: THREE.Group | null) => void; onOver: () => void; onOut: () => void; onClick: () => void; onDouble: () => void }) {
  const h = (m.big ? 1.72 : 1.55) * (m.small ? 0.78 : 1);
  const obj = useCastModel(m.model, h);
  return (
    <group ref={(g) => { if (g) g.userData.ready = !!obj; reg(g); }} visible={!!obj}
      onPointerOver={(e) => { e.stopPropagation(); onOver(); }} onPointerOut={onOut}
      onClick={(e) => { e.stopPropagation(); onClick(); }} onDoubleClick={(e) => { e.stopPropagation(); onDouble(); }}>
      {obj && <primitive object={obj} />}
    </group>
  );
}
