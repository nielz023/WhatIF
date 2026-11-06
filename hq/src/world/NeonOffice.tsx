/**
 * HET NEON-KANTOOR v2 (niels 2026-11-06: "moet lijken op het referentiebeeld").
 * Achthoekige ring van glazen afdelingen rond een ronde receptie met een glazen
 * hologramzuil, DRIFTMARK HQ-neonbord en het hoofdpersonage achter de balie.
 * Vooraan een trap naar de ingang. Spiegelende vloer, nachtstad met bokeh erachter,
 * neonranden per afdeling en grote lichtgevende borden.
 * Eén blijvende scène achter de hele HQ; de camera vliegt naar een afdeling bij klik,
 * maakt een intro van 1 s bij openen en een kleine beweging bij elke paginawissel.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Billboard, Environment, Html, Lightformer, MeshReflectorMaterial, OrbitControls, PerformanceMonitor, PerspectiveCamera, Sparkles } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import type { OrbitControls as OC } from 'three-stdlib';
import { useShallow } from 'zustand/react/shallow';
import { useGame } from '../store/useGame';
import { useLive } from '../services/live';
import { Box, Chair, Bookshelf, MicStand, Easel, Sofa, MeetingTable, ServerRack } from '../components/office/Furniture';
import { Mascot } from '../components/office/DriftmarkDecor';
import { ROOMS, threadsPerRoom, statusOf, STATUS, SPAN, R_HUB, R_IN, R_OUT, R_BASE, slotAngle, roomCenter, type RoomDef, type RoomId, type Status } from './rooms';
import { useWorld, reducedMotion } from './useWorld';
import { useOffice, BakedOffice, type OfficeModel } from './BakedOffice';

type V3 = [number, number, number];
export type WorldMode = 'home' | 'studio' | 'panel';
const ease = (t: number) => 1 - Math.pow(1 - t, 4); // ~ cubic-bezier(0.22, 1, 0.36, 1)
const GAPA = 0.035; // hoekspleet tussen afdelingen (rad)
const polar = (r: number, a: number, y = 0): V3 => [Math.sin(a) * r, y, Math.cos(a) * r];

/* ================= textures ================= */
function canvasTex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
const rr = (g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };

/** Schermtexturen met dashboards (grafiek, balken, video, golf). */
function useScreens() {
  return useMemo(() => {
    const kinds = ['chart', 'bars', 'video', 'wave', 'grid', 'thumbs'] as const;
    const hues = ['#20D9FF', '#FF7A24', '#A855F7', '#21D6A0', '#FF4DB8', '#398CFF'];
    return kinds.map((k, i) => canvasTex(256, 160, (g) => {
      const c = hues[i];
      const bg = g.createLinearGradient(0, 0, 0, 160); bg.addColorStop(0, '#0b1636'); bg.addColorStop(1, '#060b1e');
      g.fillStyle = bg; g.fillRect(0, 0, 256, 160);
      g.fillStyle = c; g.globalAlpha = 0.9; g.fillRect(10, 10, 70, 8); g.globalAlpha = 0.35; g.fillRect(10, 24, 110, 5);
      g.globalAlpha = 1; g.strokeStyle = c; g.lineWidth = 4; g.shadowColor = c; g.shadowBlur = 10;
      if (k === 'chart') { g.beginPath(); for (let x = 0; x <= 236; x += 12) g.lineTo(10 + x, 130 - (x / 236) * 70 - Math.sin(x / 18) * 14); g.stroke(); }
      if (k === 'bars') for (let j = 0; j < 9; j++) { g.fillStyle = j % 3 ? c : '#FFB070'; const h = 20 + ((j * 37) % 80); g.fillRect(14 + j * 26, 145 - h, 16, h); }
      if (k === 'video') { g.fillStyle = '#1b2a5a'; g.fillRect(20, 40, 216, 100); g.fillStyle = c; g.beginPath(); g.moveTo(112, 66); g.lineTo(150, 90); g.lineTo(112, 114); g.fill(); }
      if (k === 'wave') { g.beginPath(); for (let x = 0; x <= 236; x += 4) g.lineTo(10 + x, 95 + Math.sin(x / 6) * Math.sin(x / 40) * 38); g.stroke(); }
      if (k === 'grid') for (let j = 0; j < 12; j++) { g.fillStyle = j % 4 === 1 ? '#FF7A24' : c; g.globalAlpha = 0.35 + (j % 3) * 0.25; g.fillRect(14 + (j % 4) * 58, 42 + Math.floor(j / 4) * 38, 50, 30); }
      if (k === 'thumbs') for (let j = 0; j < 6; j++) { const gg = g.createLinearGradient(0, 0, 70, 0); gg.addColorStop(0, hues[j]); gg.addColorStop(1, '#FF7A24'); g.fillStyle = gg; g.fillRect(14 + (j % 3) * 78, 42 + Math.floor(j / 3) * 56, 70, 46); }
    }));
  }, []);
}

/** Namen op de borden zoals op het referentiebeeld (Engels + Nederlandse ondertitel). */
const SIGN: Partial<Record<string, [string, string]>> = {
  onderzoek: ['RESEARCH', 'Onderzoek'], creatief: ['CREATIVE', 'Ideeën & titels'], script: ['SCRIPT', 'Scripts & verhaallijn'],
  stem: ['VOICE', 'Stem & audio'], productie: ['PRODUCTION', 'Animatie & montage'], thumbnail: ['THUMBNAIL', 'Design & CTR'],
  publicatie: ['PUBLISHING', 'Upload & SEO'], ceo: ['CEO & ANALYTICS', 'Strategie & prestaties'], crisis: ['CRISIS KAMER', 'Analyse & oplossingen'],
};
/** Groot lichtbord per afdeling (icoon + naam + ondertitel), net als op het referentiebeeld. */
function signTex(r: RoomDef) {
  return canvasTex(1024, 300, (g) => {
    g.clearRect(0, 0, 1024, 300);
    rr(g, 8, 8, 1008, 284, 40);
    const bg = g.createLinearGradient(0, 0, 0, 300); bg.addColorStop(0, 'rgba(26,20,58,0.96)'); bg.addColorStop(1, 'rgba(10,12,32,0.96)');
    g.fillStyle = bg; g.fill();
    g.shadowColor = r.color; g.shadowBlur = 30; g.lineWidth = 9; g.strokeStyle = r.color; g.stroke();
    g.shadowBlur = 0;
    rr(g, 44, 50, 200, 200, 34); g.fillStyle = r.color + '33'; g.fill(); g.lineWidth = 5; g.strokeStyle = r.color; g.stroke();
    g.font = '120px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(r.icon, 144, 158);
    g.textAlign = 'left'; g.fillStyle = '#ffffff'; g.shadowColor = r.color; g.shadowBlur = 18;
    const [name, sub] = SIGN[r.id] ?? [r.naam.toUpperCase(), r.sub];
    g.font = `900 ${name.length > 14 ? 74 : 92}px Inter, "Arial Black", sans-serif`; g.fillText(name, 284, 124);
    g.shadowBlur = 0; g.fillStyle = '#cbd5f5'; g.font = '600 52px Inter, Arial, sans-serif'; g.fillText(sub, 288, 214);
  });
}

/* ================= camera ================= */
const ELEV = 0.66; // ~38°, zoals het referentiebeeld
const FOV = 40;
function CameraRig({ mode }: { mode: WorldMode }) {
  const { camera, size } = useThree();
  const cam = camera as THREE.PerspectiveCamera;
  const controls = useRef<OC>(null);
  const focus = useWorld((s) => s.focus);
  const introKey = useWorld((s) => s.introKey);
  const fit = useMemo(() => {
    const tv = Math.tan(THREE.MathUtils.degToRad(cam.fov / 2));
    const aspect = size.width / Math.max(1, size.height);
    const dh = (R_BASE * 1.5) / (tv * aspect);
    const dv = (R_BASE * 0.74) / tv;
    return Math.max(dh, dv);
  }, [size.width, size.height, cam.fov]);
  const dir = useMemo(() => new THREE.Vector3(0, Math.sin(ELEV), Math.cos(ELEV)), []);
  const anim = useRef<{ t: number; dur: number; fT: THREE.Vector3; tT: THREE.Vector3; fD: number; tD: number; fLift: number } | null>(null);
  const first = useRef(true);
  const cur = useRef({ d: fit });

  const goal = () => {
    const r = ROOMS.find((x) => x.id === focus);
    const wide = size.width >= 900;
    if (mode === 'home' && r) { const p = roomCenter(r); return { t: new THREE.Vector3(p[0] + (wide ? 3 : 0), 0.6, p[2] + 0.6), d: fit * 0.5 }; }
    if (mode === 'panel') return { t: new THREE.Vector3(0, 0.5, 1.5), d: fit * 1.04 };
    return { t: new THREE.Vector3(0, 0.5, wide ? 0.6 : 0), d: fit };
  };

  useEffect(() => {
    const g = goal();
    const c = controls.current;
    if (first.current) {
      first.current = false;
      anim.current = reducedMotion() ? { t: 1, dur: 1, fT: g.t, tT: g.t, fD: g.d, tD: g.d, fLift: 0 } : { t: 0, dur: 1.0, fT: g.t.clone().add(new THREE.Vector3(0, 0, -4)), tT: g.t, fD: g.d * 1.55, tD: g.d, fLift: 0.25 };
      return;
    }
    anim.current = { t: reducedMotion() ? 1 : 0, dur: 0.85, fT: c ? c.target.clone() : g.t, tT: g.t, fD: cur.current.d, tD: g.d, fLift: 0 };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus, mode, fit]);

  useEffect(() => {
    if (first.current || reducedMotion()) return;
    const g = goal();
    anim.current = { t: 0, dur: 0.7, fT: g.t.clone().add(new THREE.Vector3(1.5, 0, -1.5)), tT: g.t, fD: g.d * 1.05, tD: g.d, fLift: 0 };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [introKey]);

  useFrame((_, dt) => {
    const a = anim.current; const c = controls.current;
    if (!a || !c) return;
    a.t = Math.min(1, a.t + dt / a.dur);
    const k = ease(a.t);
    const tgt = a.fT.clone().lerp(a.tT, k);
    const d = a.fD + (a.tD - a.fD) * k;
    cur.current.d = d;
    const el = ELEV + a.fLift * (1 - k);
    c.target.copy(tgt);
    cam.position.set(tgt.x, tgt.y + Math.sin(el) * d, tgt.z + Math.cos(el) * d);
    c.update();
    if (a.t >= 1) anim.current = null;
  });
  void dir;

  return (
    <OrbitControls ref={controls as never} enabled={mode !== 'panel'} enableRotate={mode === 'studio'} enablePan
      minPolarAngle={0.45} maxPolarAngle={1.05} minAzimuthAngle={-0.6} maxAzimuthAngle={0.6}
      minDistance={fit * 0.3} maxDistance={fit * 1.5} enableDamping dampingFactor={0.08} screenSpacePanning={false} />
  );
}

/** Telt beelden per seconde en zet ze in de bovenbalk (#dm-fps). */
function FpsProbe() {
  const acc = useRef({ n: 0, t: 0 });
  useFrame((_, dt) => {
    const a = acc.current; a.n++; a.t += dt;
    if (a.t >= 0.5) { const el = document.getElementById('dm-fps'); if (el) el.textContent = `${Math.round(a.n / a.t)} fps`; a.n = 0; a.t = 0; }
  });
  return null;
}

/* ================= kleine bouwstenen ================= */
function Neon({ pts, color, r = 0.05, i = 2.6 }: { pts: V3[]; color: string; r?: number; i?: number }) {
  const geo = useMemo(() => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...p))), Math.max(8, pts.length * 4), r, 6, false), [pts, r]);
  return <mesh geometry={geo}><meshStandardMaterial color={color} emissive={color} emissiveIntensity={i} toneMapped={false} /></mesh>;
}
const arc = (r: number, a0: number, a1: number, y: number, n = 16): V3[] => Array.from({ length: n + 1 }, (_, k) => polar(r, a0 + ((a1 - a0) * k) / n, y));

function Palm({ p, s = 1 }: { p: V3; s?: number }) {
  const leaves = useMemo(() => Array.from({ length: 7 }, (_, i) => ({ a: (i / 7) * Math.PI * 2 + Math.random() * 0.4, t: 0.55 + Math.random() * 0.35, l: 0.9 + Math.random() * 0.4 })), []);
  return (
    <group position={p} scale={s}>
      <mesh position={[0, 0.25, 0]} castShadow><cylinderGeometry args={[0.32, 0.24, 0.5, 14]} /><meshStandardMaterial color="#e9edf6" roughness={0.35} metalness={0.1} /></mesh>
      <mesh position={[0, 0.85, 0]} castShadow><cylinderGeometry args={[0.05, 0.07, 0.9, 6]} /><meshStandardMaterial color="#5b3d22" /></mesh>
      {leaves.map((L, i) => (
        <group key={i} position={[0, 1.25, 0]} rotation={[0, L.a, 0]}>
          <mesh rotation={[L.t, 0, 0]} position={[0, 0.1, L.l * 0.45]} castShadow>
            <boxGeometry args={[0.32, 0.03, L.l]} />
            <meshStandardMaterial color={i % 2 ? '#2f9e4f' : '#46c063'} roughness={0.6} emissive="#0d3a1a" emissiveIntensity={0.4} />
          </mesh>
        </group>
      ))}
      <mesh position={[0, 1.35, 0]} castShadow><icosahedronGeometry args={[0.28, 0]} /><meshStandardMaterial color="#3aa957" flatShading /></mesh>
    </group>
  );
}

/** Bureau met 2-3 schermen (dashboards), toetsenbord en stoel. Schermen kijken naar +z (de camera). */
function ProDesk({ p, tex, active, n = 2 }: { p: V3; tex: THREE.Texture[]; active: boolean; n?: number }) {
  const mats = useRef<THREE.MeshBasicMaterial[]>([]);
  const seed = useMemo(() => Math.random() * 10, []);
  useFrame(({ clock }) => { const f = active ? 1 + Math.sin(clock.elapsedTime * 3 + seed) * 0.08 : 0.55; mats.current.forEach((m) => m && m.color.setScalar(f)); });
  const xs = n === 3 ? [-0.62, 0, 0.62] : [-0.33, 0.33];
  return (
    <group position={p}>
      <Box p={[0, 0.74, 0]} s={[1.9, 0.07, 0.8]} c="#f1f4fa" rough={0.3} metal={0.1} />
      <Box p={[0, 0.72, -0.38]} s={[1.9, 0.03, 0.04]} c="#20D9FF" e="#20D9FF" ei={1.4} cast={false} />
      <Box p={[-0.86, 0.36, 0]} s={[0.06, 0.72, 0.7]} c="#cfd6e6" />
      <Box p={[0.86, 0.36, 0]} s={[0.06, 0.72, 0.7]} c="#cfd6e6" />
      {xs.map((x, i) => (
        <group key={i} position={[x, 1.08, -0.22]} rotation={[0, n === 3 ? -x * 0.35 : -x * 0.3, 0]}>
          <Box p={[0, -0.24, 0]} s={[0.06, 0.18, 0.06]} c="#20263b" />
          <Box p={[0, 0, -0.02]} s={[0.62, 0.38, 0.03]} c="#0d1120" />
          <mesh position={[0, 0, 0.001]}>
            <planeGeometry args={[0.57, 0.34]} />
            <meshBasicMaterial ref={(m) => { if (m) mats.current[i] = m; }} map={tex[(i + Math.floor(seed * 7)) % tex.length]} toneMapped={false} />
          </mesh>
        </group>
      ))}
      <Box p={[0, 0.79, 0.12]} s={[0.55, 0.02, 0.16]} c="#dfe4f2" cast={false} />
      <Chair p={[0, 0, 0.72]} />
    </group>
  );
}

/* ================= medewerker ================= */
function Worker({ p, rot = 0, shirt, status, skin = '#f2c49b', hair = '#2b1d14', onClick, label, big }: { p: V3; rot?: number; shirt: string; status: Status; skin?: string; hair?: string; onClick?: () => void; label?: string; big?: boolean }) {
  const body = useRef<THREE.Group>(null); const armL = useRef<THREE.Mesh>(null); const armR = useRef<THREE.Mesh>(null); const dot = useRef<THREE.Mesh>(null);
  const seed = useMemo(() => Math.random() * 10, []);
  const [hover, setHover] = useState(false);
  const col = STATUS[status].kleur;
  const busy = status === 'werkt' || status === 'bezig';
  useFrame(({ clock }) => {
    const t = clock.elapsedTime + seed;
    if (body.current) body.current.position.y = Math.sin(t * 2) * 0.012;
    const typ = busy ? Math.sin(t * (status === 'werkt' ? 14 : 8)) * 0.18 : 0;
    if (armL.current) armL.current.rotation.x = -1.1 + typ;
    if (armR.current) armR.current.rotation.x = -1.1 - typ;
    if (dot.current) dot.current.position.y = 1.78 + Math.sin(t * 2.4) * 0.05;
  });
  return (
    <group position={p} rotation={[0, rot, 0]} scale={big ? 1.12 : 1}
      onClick={onClick ? (e) => { e.stopPropagation(); onClick(); } : undefined}
      onPointerOver={onClick ? (e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; } : undefined}
      onPointerOut={onClick ? () => { setHover(false); document.body.style.cursor = 'auto'; } : undefined}>
      <group ref={body}>
        <Box p={[-0.1, 0.5, -0.12]} s={[0.13, 0.13, 0.4]} c="#1f2a44" />
        <Box p={[0.1, 0.5, -0.12]} s={[0.13, 0.13, 0.4]} c="#1f2a44" />
        <Box p={[-0.1, 0.26, -0.3]} s={[0.12, 0.42, 0.12]} c="#1f2a44" />
        <Box p={[0.1, 0.26, -0.3]} s={[0.12, 0.42, 0.12]} c="#1f2a44" />
        <mesh position={[0, 0.86, 0.04]} castShadow><capsuleGeometry args={[0.17, 0.3, 4, 10]} /><meshStandardMaterial color={shirt} roughness={0.55} emissive={hover ? shirt : '#000'} emissiveIntensity={hover ? 0.5 : 0} /></mesh>
        <mesh ref={armL} position={[-0.22, 0.98, 0.02]} castShadow><capsuleGeometry args={[0.05, 0.3, 3, 6]} /><meshStandardMaterial color={shirt} /></mesh>
        <mesh ref={armR} position={[0.22, 0.98, 0.02]} castShadow><capsuleGeometry args={[0.05, 0.3, 3, 6]} /><meshStandardMaterial color={shirt} /></mesh>
        <mesh position={[0, 1.33, 0.02]} castShadow><sphereGeometry args={[0.17, 16, 14]} /><meshStandardMaterial color={skin} roughness={0.5} /></mesh>
        <mesh position={[0, 1.39, 0.05]} castShadow><sphereGeometry args={[0.175, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2.1]} /><meshStandardMaterial color={hair} roughness={0.7} /></mesh>
      </group>
      <mesh ref={dot} position={[0, 1.78, 0]}><sphereGeometry args={[0.08, 12, 10]} /><meshStandardMaterial color={col} emissive={col} emissiveIntensity={2.4} toneMapped={false} /></mesh>
      <mesh position={[0, 0.02, -0.05]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[0.38, 0.45, 32]} /><meshBasicMaterial color={col} transparent opacity={0.85} toneMapped={false} /></mesh>
      {hover && label && (
        <Html position={[0, 2.1, 0]} center zIndexRange={[30, 20]} style={{ pointerEvents: 'none' }}>
          <div className="whitespace-nowrap rounded-lg border border-white/15 bg-[#0a1124]/90 px-2 py-1 text-[12px] font-semibold text-white shadow-xl backdrop-blur">
            <span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ background: col }} />{label} · {STATUS[status].label}
          </div>
        </Html>
      )}
    </group>
  );
}

/* ================= afdeling (ringsegment) ================= */
interface Seat { status: Status; shirt: string; skin?: string; hair?: string; label: string; onClick?: () => void; big?: boolean }

function Special({ r, at, faceOut }: { r: RoomDef; at: (u: number, v: number) => V3; faceOut: number }) {
  const c = r.color;
  switch (r.props) {
    case 'voice': return (<group position={at(0, 1.9)}>
      <Box p={[0, 1.25, 0]} s={[2.3, 2.5, 2.1]} c="#3b1d63" opacity={0.5} rough={0.1} />
      <Box p={[0, 2.52, 0]} s={[2.34, 0.06, 2.14]} c={c} e={c} ei={2.6} cast={false} />
      {[[-1.15, -1.05], [1.15, -1.05], [-1.15, 1.05], [1.15, 1.05]].map(([x, z], i) => <Box key={i} p={[x, 1.25, z]} s={[0.06, 2.5, 0.06]} c={c} e={c} ei={2.2} cast={false} />)}
      <MicStand p={[0, 0, 0]} />
    </group>);
    case 'crisis': return (<group position={at(0, 1.0)}><MeetingTable p={[0, 0, 0]} color={c} /></group>);
    case 'ceo': return (<group position={at(0, 3.0)}><MeetingTable p={[0, 0, 0]} color={c} /></group>);
    case 'creative': return (<><Easel p={at(0, 3.0)} rot={faceOut} /></>);
    case 'script': return <Bookshelf p={at(0, 3.3)} rot={faceOut} />;
    case 'production': return (<><ServerRack p={at(-0.6, 3.3)} rot={faceOut} /><ServerRack p={at(0.6, 3.3)} rot={faceOut} /></>);
    case 'publishing': return <Rocket p={at(0, 3.0)} color={c} />;
    case 'research': return <Globe p={at(0, 3.0)} color={c} />;
    case 'thumbnail': return <Easel p={at(0, 3.0)} rot={faceOut} />;
    default: return null;
  }
}
function Globe({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Mesh>(null);
  useFrame((_, dt) => { if (g.current) g.current.rotation.y += dt * 0.4; });
  return (<group position={p}><Box p={[0, 0.45, 0]} s={[0.5, 0.9, 0.5]} c="#141a30" metal={0.5} rough={0.3} />
    <mesh ref={g} position={[0, 1.5, 0]}><icosahedronGeometry args={[0.55, 2]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} wireframe toneMapped={false} /></mesh></group>);
}
function Rocket({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Group>(null);
  useFrame(({ clock }) => { if (g.current) g.current.position.y = 0.3 + Math.sin(clock.elapsedTime * 1.6) * 0.12; });
  return (<group position={p}><Box p={[0, 0.15, 0]} s={[0.9, 0.3, 0.9]} c="#141a30" />
    <group ref={g}>
      <mesh position={[0, 1, 0]} castShadow><capsuleGeometry args={[0.28, 0.8, 4, 12]} /><meshStandardMaterial color="#e8edf7" metalness={0.4} roughness={0.3} /></mesh>
      <mesh position={[0, 1.75, 0]}><coneGeometry args={[0.28, 0.4, 12]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} /></mesh>
      <mesh position={[0, 0.3, 0]}><coneGeometry args={[0.16, 0.4, 10]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
    </group></group>);
}

function Wing({ r, seats, lit, alert, onSelect, onHover, screens, baked }: { r: RoomDef; seats: Seat[]; lit: boolean; alert: boolean; onSelect: () => void; onHover: (h: boolean) => void; screens: THREE.Texture[]; baked?: OfficeModel | null }) {
  const a = slotAngle(r.slot);
  const a0 = a - SPAN / 2 + GAPA, a1 = a + SPAN / 2 - GAPA;
  const c = r.color;
  const front = Math.cos(a) > 0.35; // vooraan: hoge wand aan de binnenkant, lage glaswand naar de camera
  const H = 3.0, HG = front ? 1.1 : 2.5;
  const rm = (R_IN + R_OUT) / 2;
  // lokaal assenstelsel: u = langs de ring, v = naar buiten
  const at = (u: number, v: number, y = 0): V3 => { const rad = rm + v; const ang = a + u / rad; return polar(rad, ang, y); };
  const sign = useMemo(() => signTex(r), [r]);
  const edge = useRef<THREE.MeshStandardMaterial[]>([]);
  useFrame(({ clock }) => {
    const pulse = alert ? 1.2 + Math.sin(clock.elapsedTime * 5) * 1 : 0;
    edge.current.forEach((m) => { if (m) m.emissiveIntensity = (lit ? 4 : 2.4) + pulse; });
  });
  const tallR = front ? R_IN + 0.08 : R_OUT - 0.08;
  const glassR = front ? R_OUT - 0.05 : R_IN + 0.05;
  const desks: [number, number][] = [[-1.25, -1.5], [1.25, -1.5], [-1.25, 1.3], [1.25, 1.3]];
  const nDesk = r.props === 'crisis' ? 2 : r.props === 'voice' ? 2 : Math.max(2, Math.min(4, seats.length + 1));
  const deskPts = (r.props === 'crisis' ? [[-1.6, -2.2], [1.6, -2.2]] : r.props === 'voice' ? [[-1.25, -1.5], [1.25, -1.5]] : desks).slice(0, nDesk) as [number, number][];
  const warm = useMemo(() => new THREE.Color(c).lerp(new THREE.Color('#ffd9b0'), 0.45), [c]);
  const NeonMat = ({ i = 0 }: { i?: number }) => <meshStandardMaterial ref={(m) => { if (m) edge.current[i] = m; }} color={c} emissive={c} emissiveIntensity={2.4} toneMapped={false} />;

  const handlers = {
    onClick: (e: { stopPropagation: () => void }) => { e.stopPropagation(); onSelect(); },
    onPointerOver: (e: { stopPropagation: () => void }) => { e.stopPropagation(); onHover(true); document.body.style.cursor = 'pointer'; },
    onPointerOut: () => { onHover(false); document.body.style.cursor = 'auto'; },
  };
  const signEl = (
    <Billboard position={polar(tallR, a, H + (baked ? (r.props === 'ceo' ? 0.55 : 1.15) : 1.4))}>
      <mesh renderOrder={r.props === 'ceo' ? 11 : 0} onClick={(e) => { e.stopPropagation(); onSelect(); }}>
        <planeGeometry args={baked ? [5.4, 1.58] : [7.2, 2.1]} />
        <meshBasicMaterial map={sign} transparent toneMapped={false} depthWrite={false} depthTest={!(baked && r.props === 'ceo')} opacity={lit ? 1 : 0.95} />
      </mesh>
    </Billboard>
  );
  const alertEl = alert && (
    <Html position={polar(tallR, a, H + 2.0)} center zIndexRange={[20, 10]} style={{ pointerEvents: 'none' }}>
      <span className="rounded-full bg-[#FF9F1C] px-2 py-0.5 text-[11px] font-bold text-black shadow-[0_0_12px_#FF9F1C]">wacht op jou</span>
    </Html>
  );
  if (baked) {
    const pts = baked.seats[r.id] ?? [];
    return (
      <group {...handlers}>
        {/* onzichtbaar klikvlak over de hele afdeling */}
        <mesh position={[0, 1.4, 0]} visible={false}><cylinderGeometry args={[R_OUT, R_OUT, 2.8, 20, 1, true, a0, a1 - a0]} /><meshBasicMaterial side={THREE.DoubleSide} /></mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.09, 0]}>
          <ringGeometry args={[R_IN, R_OUT, 24, 1, a0 - Math.PI / 2, a1 - a0]} />
          <meshBasicMaterial color={c} transparent opacity={lit ? 0.12 : 0} depthWrite={false} toneMapped={false} />
        </mesh>
        {seats.slice(0, pts.length).map((s, i) => pts[i] && <Worker key={i} p={pts[i]} {...s} />)}
        {r.props === 'research' && <Globe p={at(1.4, 2.4, 0.45)} color={c} />}
        {r.props === 'publishing' && <Rocket p={at(1.2, 2.6, 0.3)} color={c} />}
        {signEl}{alertEl}
      </group>
    );
  }
  return (
    <group {...handlers}>
      {/* vloer */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 0]} receiveShadow>
        <ringGeometry args={[R_IN, R_OUT, 40, 1, a0 - Math.PI / 2, a1 - a0]} />
        <meshStandardMaterial color="#1b2246" roughness={0.25} metalness={0.45} emissive={c} emissiveIntensity={lit ? 0.14 : 0.06} />
      </mesh>
      {/* tapijt */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.04, 0]} receiveShadow>
        <ringGeometry args={[R_IN + 1.6, R_OUT - 1.6, 30, 1, a0 + 0.06 - Math.PI / 2, a1 - a0 - 0.12]} />
        <meshStandardMaterial color="#1d2448" roughness={0.95} />
      </mesh>
      {/* hoge wand (donker glas/metaal) */}
      <mesh position={[0, H / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[tallR, tallR, H, 32, 1, true, a0, a1 - a0]} />
        <meshStandardMaterial color="#121a36" roughness={0.3} metalness={0.6} side={THREE.DoubleSide} />
      </mesh>
      {/* glaswand naar de gang / camera */}
      <mesh position={[0, HG / 2, 0]}>
        <cylinderGeometry args={[glassR, glassR, HG, 32, 1, true, a0, a1 - a0]} />
        <meshStandardMaterial color="#9fdcff" transparent opacity={0.12} roughness={0.05} metalness={0.3} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      {/* glazen zijwanden */}
      {[a0, a1].map((ang, i) => (
        <mesh key={i} position={polar(rm, ang, 1.25)} rotation={[0, ang, 0]}>
          <boxGeometry args={[0.04, 2.5, R_OUT - R_IN]} />
          <meshStandardMaterial color="#9fdcff" transparent opacity={0.1} roughness={0.05} side={THREE.DoubleSide} depthWrite={false} />
        </mesh>
      ))}
      {/* neonranden: vloer, bovenkant van de wanden, hoekstijlen */}
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(R_OUT - 0.05, a0, a1, 0.06).map((p) => new THREE.Vector3(...p))), 40, 0.06, 6, false]} /><NeonMat i={0} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(R_IN + 0.05, a0, a1, 0.06).map((p) => new THREE.Vector3(...p))), 30, 0.05, 6, false]} /><NeonMat i={1} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(tallR, a0, a1, H).map((p) => new THREE.Vector3(...p))), 40, 0.06, 6, false]} /><NeonMat i={2} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(glassR, a0, a1, HG).map((p) => new THREE.Vector3(...p))), 40, 0.04, 6, false]} /><NeonMat i={3} /></mesh>
      {[a0, a1].map((ang, i) => (<group key={i}>
        <Neon pts={[polar(R_IN, ang, 0.06), polar(R_OUT, ang, 0.06)]} color={c} r={0.04} i={2} />
        <Neon pts={[polar(R_OUT - 0.05, ang, 0), polar(R_OUT - 0.05, ang, front ? HG : H)]} color={c} r={0.05} i={2.4} />
        <Neon pts={[polar(R_IN + 0.05, ang, 0), polar(R_IN + 0.05, ang, front ? H : HG)]} color={c} r={0.05} i={2.4} />
      </group>))}
      {/* warm binnenlicht */}
      <pointLight position={polar(rm, a, 2.6)} color={warm} intensity={lit ? 30 : 20} distance={10} decay={1.6} />
      {/* groot scherm op de hoge wand */}
      <mesh position={polar(front ? R_IN + 0.2 : R_OUT - 0.2, a, 1.75)} rotation={[0, front ? a : a + Math.PI, 0]}>
        <planeGeometry args={[3.0, 1.35]} />
        <meshBasicMaterial map={screens[(r.slot + 2) % screens.length]} toneMapped={false} />
      </mesh>
      <mesh position={polar(front ? R_IN + 0.19 : R_OUT - 0.19, a, 1.75)} rotation={[0, front ? a : a + Math.PI, 0]}>
        <planeGeometry args={[3.15, 1.5]} />
        <meshStandardMaterial color={c} emissive={c} emissiveIntensity={1.2} toneMapped={false} />
      </mesh>
      {/* bureaus + medewerkers (schermen naar de camera) */}
      {deskPts.map(([u, v], i) => <ProDesk key={i} p={at(u, v)} tex={screens} n={i === 0 ? 3 : 2} active={!!seats[i] && (seats[i].status === 'werkt' || seats[i].status === 'bezig')} />)}
      {seats.slice(0, deskPts.length).map((s, i) => { const p = at(deskPts[i][0], deskPts[i][1]); return <Worker key={i} p={[p[0], 0, p[2] + 0.66]} {...s} />; })}
      <Special r={r} at={at} faceOut={a + Math.PI} />
      {/* planten in de hoeken */}
      <Palm p={at(-3.1, 3.2)} s={0.95} />
      <Palm p={at(3.1, 3.2)} s={0.8} />
      {signEl}{alertEl}
    </group>
  );
}

/* ================= receptie in het midden ================= */
function hqSignTex() {
  return canvasTex(1024, 512, (g) => {
    g.clearRect(0, 0, 1024, 512);
    rr(g, 24, 40, 976, 420, 70); const bg = g.createLinearGradient(0, 40, 0, 460); bg.addColorStop(0, 'rgba(40,18,40,.92)'); bg.addColorStop(1, 'rgba(14,12,34,.92)');
    g.fillStyle = bg; g.fill(); g.lineWidth = 10; g.strokeStyle = '#FF7A24'; g.shadowColor = '#FF7A24'; g.shadowBlur = 40; g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'middle';
    const gr = g.createLinearGradient(0, 120, 0, 280); gr.addColorStop(0, '#FFE0A8'); gr.addColorStop(1, '#FF8A3D');
    g.fillStyle = gr; g.shadowBlur = 36; g.font = '900 168px Inter, "Arial Black", sans-serif'; g.fillText('DRIFTMARK', 512, 210);
    g.shadowColor = '#398CFF'; g.fillStyle = '#E6F0FF'; g.font = '900 120px Inter, "Arial Black", sans-serif'; g.fillText('HQ', 512, 360);
  });
}
function playTex() {
  return canvasTex(256, 256, (g) => {
    g.shadowColor = '#FF7A24'; g.shadowBlur = 34; g.strokeStyle = '#FFB070'; g.lineWidth = 16; g.lineJoin = 'round';
    g.beginPath(); g.moveTo(88, 58); g.lineTo(202, 128); g.lineTo(88, 198); g.closePath(); g.stroke();
    g.globalAlpha = 0.25; g.fillStyle = '#FF7A24'; g.fill();
  });
}

function Reception({ screens, onSelect, lit, baked }: { screens: THREE.Texture[]; onSelect: () => void; lit: boolean; baked?: boolean }) {
  const holo = useRef<THREE.MeshStandardMaterial>(null); const ring1 = useRef<THREE.Mesh>(null); const ring2 = useRef<THREE.Mesh>(null); const play = useRef<THREE.Group>(null);
  const sign = useMemo(hqSignTex, []); const pt = useMemo(playTex, []);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (holo.current) holo.current.opacity = 0.2 + Math.sin(t * 2) * 0.05;
    if (ring1.current) { const k = (t * 0.5) % 1; ring1.current.position.y = 1.3 + k * 6; (ring1.current.material as THREE.MeshBasicMaterial).opacity = 1 - k; }
    if (ring2.current) { const k = ((t * 0.5) + 0.5) % 1; ring2.current.position.y = 1.3 + k * 6; (ring2.current.material as THREE.MeshBasicMaterial).opacity = 1 - k; }
    if (play.current) play.current.position.y = 4.4 + Math.sin(t * 1.4) * 0.15;
  });
  return (
    <group onClick={(e) => { e.stopPropagation(); onSelect(); }} onPointerOver={() => { document.body.style.cursor = 'pointer'; }} onPointerOut={() => { document.body.style.cursor = 'auto'; }}>
      {!baked && (<>
      {/* podium */}
      <mesh position={[0, 0.25, 0]} castShadow receiveShadow><cylinderGeometry args={[R_HUB, R_HUB + 0.3, 0.5, 64]} /><meshStandardMaterial color="#121a38" metalness={0.6} roughness={0.2} /></mesh>
      <mesh position={[0, 0.51, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[R_HUB - 0.05, 0.07, 8, 96]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
      <mesh position={[0, 0.52, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[3.6, 3.72, 96]} /><meshBasicMaterial color="#20D9FF" toneMapped={false} /></mesh>
      <mesh position={[0, 0.52, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[4.7, 4.76, 96]} /><meshBasicMaterial color="#398CFF" toneMapped={false} /></mesh>
      {/* ronde balie */}
      <mesh position={[0, 1.05, 0]} castShadow><cylinderGeometry args={[2.7, 2.7, 1.1, 48, 1, true, Math.PI * 0.18, Math.PI * 1.64]} /><meshStandardMaterial color="#1a2550" metalness={0.6} roughness={0.25} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, 1.61, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.72, 0.06, 8, 96, Math.PI * 2]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
      <mesh position={[0, 0.6, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.75, 0.05, 8, 96]} /><meshStandardMaterial color="#20D9FF" emissive="#20D9FF" emissiveIntensity={2.4} toneMapped={false} /></mesh>
      {/* schermen op de balie */}
      {[-1.1, 0, 1.1].map((x, i) => (
        <group key={i} position={[x, 1.95, 1.35 - Math.abs(x) * 0.25]} rotation={[0, -x * 0.35, 0]}>
          <Box p={[0, 0, -0.02]} s={[0.9, 0.52, 0.04]} c="#0d1120" />
          <mesh position={[0, 0, 0.001]}><planeGeometry args={[0.84, 0.47]} /><meshBasicMaterial map={screens[i]} toneMapped={false} /></mesh>
        </group>
      ))}
      </>)}
      {/* het hoofdpersonage achter de balie */}
      <Mascot p={[0, 0.5, -0.4]} rot={0} s={1.05} />
      {/* glazen hologramzuil */}
      <mesh position={[0, 5.0, 0]}><cylinderGeometry args={[2.3, 2.3, 7, 64, 1, true]} /><meshStandardMaterial ref={holo} color="#7fe8ff" emissive="#20D9FF" emissiveIntensity={0.9} transparent opacity={0.2} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} /></mesh>
      <mesh ref={ring1} position={[0, 1.3, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.32, 0.035, 6, 80]} /><meshBasicMaterial color="#b8f6ff" transparent toneMapped={false} /></mesh>
      <mesh ref={ring2} position={[0, 1.3, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.32, 0.035, 6, 80]} /><meshBasicMaterial color="#b8f6ff" transparent toneMapped={false} /></mesh>
      {!baked && (<>
      <mesh position={[0, 8.5, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.35, 0.09, 8, 80]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3.2} toneMapped={false} /></mesh>
      <mesh position={[0, 8.55, 0]}><cylinderGeometry args={[2.4, 2.4, 0.12, 64]} /><meshStandardMaterial color="#1a1530" metalness={0.6} roughness={0.3} /></mesh>
      </>)}
      <group ref={play} position={[0, 4.4, 0]}>
        <Billboard><mesh><planeGeometry args={[2.4, 2.4]} /><meshBasicMaterial map={pt} transparent toneMapped={false} depthWrite={false} /></mesh></Billboard>
      </group>
      {/* zwevende schermpjes rond de zuil */}
      {[-1, 1].map((sd) => (
        <mesh key={sd} position={[sd * 3.3, 3.0, 1.2]} rotation={[0, -sd * 0.5, 0]}>
          <planeGeometry args={[1.6, 1]} /><meshBasicMaterial map={screens[sd > 0 ? 3 : 0]} transparent opacity={0.85} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      ))}
      <Billboard position={[0, baked ? 7.7 : 10.2, 0]}><mesh renderOrder={10}><planeGeometry args={baked ? [6.0, 3.0] : [7.4, 3.7]} /><meshBasicMaterial map={sign} transparent toneMapped={false} depthWrite={false} depthTest={!baked} /></mesh></Billboard>
      <pointLight position={[0, 4, 0]} color="#20D9FF" intensity={lit ? 60 : 40} distance={16} decay={1.5} />
      <pointLight position={[0, 2.2, 2.5]} color="#FFB070" intensity={22} distance={8} decay={1.6} />
      {!baked && (<>
      {/* planten op het podium */}
      <Palm p={[-3.9, 0.5, -3.1]} s={1.0} />
      <Palm p={[3.9, 0.5, -3.1]} s={1.0} />
      <Sofa p={[-4.1, 0.5, 1.6]} rot={Math.PI / 2 + 0.4} color="#26305e" />
      <Sofa p={[4.1, 0.5, 1.6]} rot={-Math.PI / 2 - 0.4} color="#26305e" />
      </>)}
    </group>
  );
}

/** Trap vooraan + lichtgevende ingang (zeshoek). */
function Entrance() {
  const n = 7;
  return (
    <group>
      {Array.from({ length: n }, (_, i) => {
        const z = R_HUB + 0.3 + i * ((R_OUT - R_HUB - 1) / n); const y = 0.5 - (i + 1) * (0.6 / n);
        const w = 3.6 + i * 0.22;
        return (<group key={i}>
          <Box p={[0, y / 2 - 0.05, z]} s={[w, y + 0.1, (R_OUT - R_HUB - 1) / n]} c="#151d3d" metal={0.5} rough={0.25} />
          <Box p={[0, y + 0.01, z + (R_OUT - R_HUB - 1) / n / 2 - 0.02]} s={[w, 0.03, 0.04]} c="#20D9FF" e="#20D9FF" ei={2.2} cast={false} />
        </group>);
      })}
      {[-1, 1].map((sd) => <Neon key={sd} pts={[[sd * 1.9, 0.6, R_HUB + 0.2], [sd * 2.6, 0.1, R_OUT]]} color="#20D9FF" r={0.05} i={2.2} />)}
      <mesh position={[0, 0.05, R_OUT + 0.6]} rotation={[-Math.PI / 2, 0, Math.PI / 6]}><ringGeometry args={[1.5, 1.68, 6]} /><meshBasicMaterial color="#20D9FF" toneMapped={false} /></mesh>
      <mesh position={[0, 0.04, R_OUT + 0.6]} rotation={[-Math.PI / 2, 0, Math.PI / 6]}><circleGeometry args={[1.5, 6]} /><meshBasicMaterial color="#123a66" transparent opacity={0.6} toneMapped={false} /></mesh>
      <Palm p={[-3.0, 0, R_OUT - 0.4]} s={1.1} />
      <Palm p={[3.0, 0, R_OUT - 0.4]} s={1.1} />
    </group>
  );
}

/** Nachtstad met verlichte ramen en bokeh. */
function City() {
  const win = useMemo(() => {
    const t = canvasTex(64, 128, (g) => {
      g.fillStyle = '#070b1c'; g.fillRect(0, 0, 64, 128);
      for (let y = 4; y < 128; y += 8) for (let x = 4; x < 64; x += 8) if (Math.random() < 0.38) { g.fillStyle = Math.random() < 0.6 ? '#ffb46b' : '#7fc8ff'; g.globalAlpha = 0.4 + Math.random() * 0.6; g.fillRect(x, y, 4, 4); }
    });
    t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }, []);
  const blds = useMemo(() => Array.from({ length: 70 }, (_, i) => {
    const a = (i / 70) * Math.PI * 2 + Math.random() * 0.05; const r = 62 + Math.random() * 40;
    return { p: polar(r, a, 0), h: 14 + Math.random() * 46, w: 5 + Math.random() * 8, a };
  }).filter((b) => Math.cos(b.a) < 0.55), []);
  return (
    <group>
      {blds.map((b, i) => (
        <mesh key={i} position={[b.p[0], b.h / 2 - 22, b.p[2]]} rotation={[0, b.a, 0]}>
          <boxGeometry args={[b.w, b.h, b.w]} />
          <meshBasicMaterial map={win} color="#5a5a5a" toneMapped={false} fog />
        </mesh>
      ))}
      <Sparkles count={60} scale={[140, 30, 60]} position={[0, 14, -55]} size={26} speed={0.15} opacity={0.5} color="#FFB070" />
      <Sparkles count={40} scale={[140, 30, 60]} position={[0, 18, -60]} size={22} speed={0.1} opacity={0.45} color="#7fc8ff" />
    </group>
  );
}

/* ================= de scène ================= */
function Scene({ mode }: { mode: WorldMode }) {
  const activity = useLive((s) => s.data.activity);
  const { agents, selectDept, selectAgent, setPage } = useGame(useShallow((s) => ({ agents: s.agents, selectDept: s.selectDept, selectAgent: s.selectAgent, setPage: s.setPage })));
  const { focus, setFocus, openWorker, hover, setHover } = useWorld(useShallow((s) => ({ focus: s.focus, setFocus: s.setFocus, openWorker: s.openWorker, hover: s.hover, setHover: s.setHover })));
  const per = useMemo(() => threadsPerRoom(activity), [activity]);
  const screens = useScreens();
  const office = useOffice();
  const SHIRTS = ['#FF7A24', '#398CFF', '#A855F7', '#21D6A0', '#FF4DB8', '#20D9FF'];

  const seatsFor = (r: RoomDef): Seat[] => {
    if (mode === 'studio' && r.game) {
      const list = agents.filter((a) => (r.game === 'warroom' ? false : a.department === r.game)).slice(0, 4);
      return list.map((a) => ({
        status: a.state === 'working' ? 'werkt' : a.state === 'meeting' ? 'bezig' : a.state === 'training' ? 'wacht' : 'offline',
        shirt: a.avatar.shirt, skin: a.avatar.skin, hair: a.avatar.hair, label: a.name, onClick: () => selectAgent(a.id),
      }));
    }
    const list = per[r.id];
    const st = statusOf(list);
    const main: Seat = { status: st, shirt: r.color, label: r.agent, big: true, onClick: () => { if (mode === 'panel') setPage('driftmark'); openWorker(r.id); } };
    const extra = list.filter((a) => a.state === 'working' || a.state === 'blocked' || a.state === 'review_ready').slice(0, 2)
      .map((a, i): Seat => ({ status: statusOf([a]), shirt: SHIRTS[(i + r.slot) % SHIRTS.length], label: a.title, onClick: main.onClick }));
    // altijd een paar collega's, zodat elke afdeling bemand oogt (grijs = geen taak)
    const fill = [main, ...extra];
    while (fill.length < 3) fill.push({ status: 'offline', shirt: SHIRTS[(fill.length + r.slot * 2) % SHIRTS.length], label: `${r.agent} (team)`, onClick: main.onClick });
    return fill;
  };

  const select = (r: RoomDef) => {
    if (mode === 'studio') { if (r.game) selectDept(r.game as never); else setPage(r.page ?? 'coach'); return; }
    if (mode === 'panel') setPage('driftmark');
    setFocus(r.id as RoomId);
  };
  const coach = ROOMS.find((x) => x.id === 'coach')!;

  return (
    <>
      <color attach="background" args={['#060a1c']} />
      <fog attach="fog" args={['#0a0f2a', 70, 170]} />
      <PerspectiveCamera makeDefault fov={FOV} near={0.5} far={400} position={[0, 60, 45]} />
      <CameraRig mode={mode} />
      <FpsProbe />
      <Environment resolution={128} frames={1}>
        <Lightformer form="ring" intensity={3} color="#FF7A24" scale={14} position={[-18, 8, -10]} />
        <Lightformer form="ring" intensity={3} color="#20D9FF" scale={14} position={[18, 8, -10]} />
        <Lightformer form="rect" intensity={1.5} color="#A855F7" scale={[30, 6, 1]} position={[0, 12, -30]} />
        <Lightformer form="rect" intensity={1} color="#ffffff" scale={[20, 20, 1]} position={[0, 30, 0]} rotation-x={Math.PI / 2} />
      </Environment>
      <ambientLight intensity={0.35} color="#8fa0ff" />
      <hemisphereLight args={['#b9c7ff', '#1a0f2e', 0.5]} />
      <directionalLight position={[16, 40, 22]} intensity={1.1} color="#fff1e0" castShadow={!office} shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-20} shadow-camera-right={20} shadow-camera-top={20} shadow-camera-bottom={-20} shadow-bias={-0.0004} />
      <pointLight position={[-30, 12, 6]} color="#FF7A24" intensity={90} distance={80} decay={1.4} />
      <pointLight position={[30, 12, 6]} color="#398CFF" intensity={90} distance={80} decay={1.4} />

      {!office && (<>
      {/* grondplaat: spiegelende vloer met oranje rand */}
      <mesh position={[0, -0.6, 0]} receiveShadow><cylinderGeometry args={[R_BASE, R_BASE + 0.4, 1.2, 8, 1]} /><meshStandardMaterial color="#0a0f24" roughness={0.35} metalness={0.6} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, 0.005, 0]}>
        <circleGeometry args={[R_BASE - 0.2, 8]} />
        <MeshReflectorMaterial blur={[300, 80]} resolution={512} mixBlur={1} mixStrength={18} roughness={0.75} depthScale={1} minDepthThreshold={0.4} maxDepthThreshold={1.4} color="#0d1330" metalness={0.6} mirror={0.6} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, 0.02, 0]}><ringGeometry args={[R_BASE - 0.35, R_BASE - 0.15, 8]} /><meshBasicMaterial color="#FF7A24" toneMapped={false} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, -1.15, 0]}><ringGeometry args={[R_BASE + 0.2, R_BASE + 0.6, 8]} /><meshBasicMaterial color="#FF7A24" toneMapped={false} /></mesh>
      {/* lichtlijnen in de gang */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}><ringGeometry args={[R_IN - 0.42, R_IN - 0.34, 96]} /><meshBasicMaterial color="#398CFF" toneMapped={false} /></mesh>

      </>)}
      {office && <BakedOffice model={office} screens={screens} lit={(id) => focus === id || hover === id} alert={(id) => { const rr = ROOMS.find((x) => x.id === id); if (!rr || mode === 'studio') return false; const st = statusOf(per[rr.id]); return st === 'wacht' || st === 'probleem'; }} />}
      <Reception screens={screens} baked={!!office} lit={focus === 'coach' || hover === 'coach'} onSelect={() => select(coach)} />
      {!office && <Entrance />}
      {ROOMS.filter((r) => r.slot >= 0).map((r) => {
        const st = statusOf(per[r.id]);
        return (
          <Wing key={r.id} r={r} baked={office} screens={screens} seats={seatsFor(r)} lit={focus === r.id || hover === r.id} alert={mode !== 'studio' && (st === 'wacht' || st === 'probleem')}
            onHover={(h) => setHover(h ? r.id : null)} onSelect={() => select(r)} />
        );
      })}
      <City />
      <EffectComposer multisampling={0}>
        <Bloom intensity={office ? 0.9 : 1.05} luminanceThreshold={office ? 0.8 : 0.62} luminanceSmoothing={0.25} mipmapBlur />
        <Vignette eskil={false} offset={0.3} darkness={0.55} />
      </EffectComposer>
    </>
  );
}

export default function NeonOffice({ mode }: { mode: WorldMode }) {
  const [dpr, setDpr] = useState(1.5);
  const setFocus = useWorld((s) => s.setFocus);
  return (
    <Canvas shadows dpr={mode === 'panel' ? 1 : dpr} gl={{ antialias: true, powerPreference: 'high-performance', toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.25 }}
      onPointerMissed={(e) => { if (mode === 'home' && (e.target as HTMLElement)?.tagName === 'CANVAS') setFocus(null); }}>
      <PerformanceMonitor onDecline={() => setDpr(1)} onIncline={() => setDpr(1.6)} />
      <Scene mode={mode} />
    </Canvas>
  );
}
