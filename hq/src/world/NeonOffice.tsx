/**
 * HET NEON-KANTOOR (niels 2026-11-05, redesign "futuristisch 3D-command center").
 * Eén blijvende 3D-scène achter de hele HQ: 9 afdelingen + de Coachkamer rond een
 * centrale receptie met DRIFTMARK HQ-hologram. De camera vliegt naar een afdeling
 * als je erop klikt, maakt een intro van 1 s bij het openen en een kleine beweging
 * bij elke paginawissel. Medewerkers tonen de echte status van de Claude-taken.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Html, OrbitControls, OrthographicCamera, PerformanceMonitor } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import type { OrbitControls as OC } from 'three-stdlib';
import { useShallow } from 'zustand/react/shallow';
import { useGame } from '../store/useGame';
import { useLive } from '../services/live';
import { Box, Chair, Desk, Plant, ServerRack, WallScreen, Whiteboard, Bookshelf, MicStand, Easel, Sofa, MeetingTable, Frame } from '../components/office/Furniture';
import { Mascot, NeonSign, FloatingMarks } from '../components/office/DriftmarkDecor';
import { ROOMS, ROOM, GAP, cellPos, threadsPerRoom, statusOf, STATUS, type RoomDef, type RoomId, type Status } from './rooms';
import { useWorld, reducedMotion } from './useWorld';

type V3 = [number, number, number];
export type WorldMode = 'home' | 'studio' | 'panel';
const HALF = ROOM / 2;
const H = 2.6;
const ease = (t: number) => 1 - Math.pow(1 - t, 4); // ~ cubic-bezier(0.22, 1, 0.36, 1)
const DIR = new THREE.Vector3(1, 0.92, 1).normalize();

/* ---------------- camera ---------------- */
function CameraRig({ mode }: { mode: WorldMode }) {
  const { camera, size } = useThree();
  const cam = camera as THREE.OrthographicCamera;
  const controls = useRef<OC>(null);
  const focus = useWorld((s) => s.focus);
  const introKey = useWorld((s) => s.introKey);
  const base = Math.min(size.width / 64, size.height / 50);
  const anim = useRef<{ t: number; dur: number; fromT: THREE.Vector3; toT: THREE.Vector3; fromZ: number; toZ: number; fromLift: number } | null>(null);
  const first = useRef(true);

  const goal = () => {
    const r = ROOMS.find((x) => x.id === focus);
    if (mode === 'home' && r) { const p = cellPos(r.cell[0], r.cell[1]); return { t: new THREE.Vector3(p[0] + 2.2, 0, p[2] - 0.6), z: base * 1.75 }; }
    if (mode === 'panel') return { t: new THREE.Vector3(-4.6, 0, -4.6), z: base * 0.9 };
    return { t: new THREE.Vector3(-4.6, 0, -4.6), z: base };
  };

  // start een vlucht naar het doel
  useEffect(() => {
    const g = goal();
    const c = controls.current;
    const curT = c ? c.target.clone() : new THREE.Vector3();
    if (first.current) {
      first.current = false;
      // intro: iets uitgezoomd en hoger, dan in 1 s naar de normale stand
      cam.zoom = g.z * 0.62; cam.position.copy(g.t).addScaledVector(DIR, 80).add(new THREE.Vector3(0, 18, 0)); cam.updateProjectionMatrix();
      anim.current = reducedMotion() ? { t: 1, dur: 1, fromT: g.t, toT: g.t, fromZ: g.z, toZ: g.z, fromLift: 0 } : { t: 0, dur: 1.0, fromT: g.t.clone(), toT: g.t, fromZ: g.z * 0.62, toZ: g.z, fromLift: 18 };
      return;
    }
    anim.current = { t: reducedMotion() ? 1 : 0, dur: 0.8, fromT: curT, toT: g.t, fromZ: cam.zoom, toZ: g.z, fromLift: 0 };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus, mode, base]);

  // kleine camerabeweging bij elke paginawissel
  useEffect(() => {
    if (first.current || reducedMotion()) return;
    const g = goal();
    anim.current = { t: 0, dur: 0.7, fromT: g.t.clone().add(new THREE.Vector3(-1.2, 0, 1.2)), toT: g.t, fromZ: g.z * 0.96, toZ: g.z, fromLift: 0 };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [introKey]);

  useFrame((_, dt) => {
    const a = anim.current; const c = controls.current;
    if (!a || !c) return;
    a.t = Math.min(1, a.t + dt / a.dur);
    const k = ease(a.t);
    const tgt = a.fromT.clone().lerp(a.toT, k);
    c.target.copy(tgt);
    cam.zoom = a.fromZ + (a.toZ - a.fromZ) * k;
    cam.position.copy(tgt).addScaledVector(DIR, 80).add(new THREE.Vector3(0, a.fromLift * (1 - k), 0));
    cam.updateProjectionMatrix();
    c.update();
    if (a.t >= 1) anim.current = null;
  });

  return (
    <OrbitControls
      ref={controls as never}
      enabled={mode !== 'panel'}
      enableRotate={mode === 'studio'}
      minPolarAngle={0.65} maxPolarAngle={1.05}
      minAzimuthAngle={0.35} maxAzimuthAngle={1.2}
      minZoom={base * 0.6} maxZoom={base * 4}
      enableDamping dampingFactor={0.08}
      screenSpacePanning
    />
  );
}

/* ---------------- medewerker ---------------- */
function Worker({ p, rot = 0, shirt, status, skin = '#f2c49b', hair = '#2b1d14', onClick, label, big }: { p: V3; rot?: number; shirt: string; status: Status; skin?: string; hair?: string; onClick?: () => void; label?: string; big?: boolean }) {
  const body = useRef<THREE.Group>(null);
  const armL = useRef<THREE.Mesh>(null);
  const armR = useRef<THREE.Mesh>(null);
  const dot = useRef<THREE.Mesh>(null);
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
    if (dot.current) { dot.current.position.y = 1.72 + Math.sin(t * 2.4) * 0.05; (dot.current.material as THREE.MeshStandardMaterial).emissiveIntensity = 1.6 + Math.sin(t * 4) * 0.6; }
  });
  return (
    <group position={p} rotation={[0, rot, 0]} scale={big ? 1.12 : 1}
      onClick={onClick ? (e) => { e.stopPropagation(); onClick(); } : undefined}
      onPointerOver={onClick ? (e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; } : undefined}
      onPointerOut={onClick ? () => { setHover(false); document.body.style.cursor = 'auto'; } : undefined}>
      <group ref={body}>
        {/* benen (zittend) */}
        <Box p={[-0.1, 0.5, -0.12]} s={[0.13, 0.13, 0.4]} c="#1f2a44" />
        <Box p={[0.1, 0.5, -0.12]} s={[0.13, 0.13, 0.4]} c="#1f2a44" />
        <Box p={[-0.1, 0.26, -0.3]} s={[0.12, 0.42, 0.12]} c="#1f2a44" />
        <Box p={[0.1, 0.26, -0.3]} s={[0.12, 0.42, 0.12]} c="#1f2a44" />
        {/* romp */}
        <mesh position={[0, 0.86, 0.04]} castShadow>
          <capsuleGeometry args={[0.17, 0.3, 4, 10]} />
          <meshStandardMaterial color={shirt} roughness={0.55} emissive={hover ? shirt : '#000'} emissiveIntensity={hover ? 0.35 : 0} />
        </mesh>
        {/* armen naar het toetsenbord */}
        <mesh ref={armL} position={[-0.22, 0.98, 0.02]} castShadow><capsuleGeometry args={[0.05, 0.3, 3, 6]} /><meshStandardMaterial color={shirt} /></mesh>
        <mesh ref={armR} position={[0.22, 0.98, 0.02]} castShadow><capsuleGeometry args={[0.05, 0.3, 3, 6]} /><meshStandardMaterial color={shirt} /></mesh>
        {/* hoofd */}
        <mesh position={[0, 1.33, 0.02]} castShadow><sphereGeometry args={[0.17, 16, 14]} /><meshStandardMaterial color={skin} roughness={0.5} /></mesh>
        <mesh position={[0, 1.39, 0.05]} castShadow><sphereGeometry args={[0.175, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2.1]} /><meshStandardMaterial color={hair} roughness={0.7} /></mesh>
      </group>
      {/* statusbolletje en ring */}
      <mesh ref={dot} position={[0, 1.72, 0]}><sphereGeometry args={[0.075, 12, 10]} /><meshStandardMaterial color={col} emissive={col} emissiveIntensity={2} toneMapped={false} /></mesh>
      <mesh position={[0, 0.02, -0.05]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[0.36, 0.42, 32]} /><meshBasicMaterial color={col} transparent opacity={0.8} toneMapped={false} /></mesh>
      {hover && label && (
        <Html position={[0, 2.05, 0]} center zIndexRange={[30, 20]} style={{ pointerEvents: 'none' }}>
          <div className="whitespace-nowrap rounded-lg border border-white/15 bg-[#0a1124]/90 px-2 py-1 text-[12px] font-semibold text-white shadow-xl backdrop-blur">
            <span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ background: col }} />{label} · {STATUS[status].label}
          </div>
        </Html>
      )}
    </group>
  );
}

/* ---------------- props per afdeling ---------------- */
function Props({ r, active }: { r: RoomDef; active: boolean }) {
  const c = r.color;
  switch (r.props) {
    case 'research': return (<>
      <WallScreen p={[-1.6, 1.6, -HALF + 0.2]} w={2.6} h={1.3} color={c} />
      <WallScreen p={[1.4, 1.6, -HALF + 0.2]} w={2.2} h={1.3} color="#398CFF" />
      <Globe p={[3.4, 0, -2.8]} color={c} />
      <Bookshelf p={[-HALF + 0.4, 0, -2.6]} rot={Math.PI / 2} />
    </>);
    case 'creative': return (<>
      <Whiteboard p={[-0.6, 0, -HALF + 0.3]} accent={c} />
      <Easel p={[3.2, 0, -3]} rot={-0.4} />
      <Frame p={[-HALF + 0.2, 1.7, -1.8]} rot={Math.PI / 2} color={c} />
      <Frame p={[-HALF + 0.2, 1.7, 0.4]} rot={Math.PI / 2} color="#FF4DB8" />
      <Lamp p={[2, 0, -1.6]} color={c} />
    </>);
    case 'script': return (<>
      <Bookshelf p={[-1.2, 0, -HALF + 0.4]} />
      <Bookshelf p={[0.6, 0, -HALF + 0.4]} />
      <WallScreen p={[-HALF + 0.2, 1.6, -1.6]} rot={Math.PI / 2} w={2.4} h={1.2} color={c} />
      <Sofa p={[3.2, 0, -3]} rot={-Math.PI / 2} color="#3a2340" />
    </>);
    case 'voice': return (<>
      <Booth p={[2.4, 0, -2.4]} color={c} active={active} />
      <MicStand p={[-1.2, 0, -2.6]} />
      <WallScreen p={[-HALF + 0.2, 1.6, -1.4]} rot={Math.PI / 2} w={2.2} h={1.1} color={c} />
    </>);
    case 'production': return (<>
      <WallScreen p={[0.2, 1.7, -HALF + 0.2]} w={4.2} h={1.8} color={c} />
      <ServerRack p={[-HALF + 0.5, 0, -3.6]} rot={Math.PI / 2} />
      <ServerRack p={[-HALF + 0.5, 0, -2.6]} rot={Math.PI / 2} />
      <Sofa p={[3.4, 0, -2.2]} rot={-Math.PI / 2} color="#2a2350" />
    </>);
    case 'thumbnail': return (<>
      {[-2.6, -0.6, 1.4].map((x, i) => <Frame key={i} p={[x, 1.7, -HALF + 0.2]} color={[c, '#FF4DB8', '#20D9FF'][i]} />)}
      <Easel p={[3.2, 0, -2.8]} rot={-0.5} />
      <WallScreen p={[-HALF + 0.2, 1.6, -0.6]} rot={Math.PI / 2} w={2.4} h={1.2} color={c} />
    </>);
    case 'publishing': return (<>
      <WallScreen p={[-1.2, 1.6, -HALF + 0.2]} w={3} h={1.4} color={c} />
      <Rocket p={[3.2, 0, -3]} color={c} />
      <WallScreen p={[-HALF + 0.2, 1.6, -0.8]} rot={Math.PI / 2} w={2} h={1.1} color="#20D9FF" />
    </>);
    case 'ceo': return (<>
      <WallScreen p={[-0.8, 1.7, -HALF + 0.2]} w={3.6} h={1.6} color={c} />
      <WallScreen p={[-HALF + 0.2, 1.7, -1.2]} rot={Math.PI / 2} w={2.6} h={1.3} color="#21D6A0" />
      <MeetingTable p={[2.2, 0, -2.4]} color={c} />
      <Crown p={[3.6, 2.2, -HALF + 0.5]} />
    </>);
    case 'crisis': return (<>
      <WallScreen p={[0, 1.7, -HALF + 0.2]} w={4.4} h={1.8} color={c} />
      <MeetingTable p={[0.4, 0, -1.4]} color={c} />
      <Beacon p={[-HALF + 0.6, 2.4, -HALF + 0.6]} color={c} />
    </>);
    case 'coach': return (<>
      <ClaudeCore p={[0, 0, -1.2]} />
      <Sofa p={[-3, 0, 1.6]} rot={Math.PI / 2} color="#3a2a20" />
      <Sofa p={[3, 0, 1.6]} rot={-Math.PI / 2} color="#3a2a20" />
    </>);
  }
}

function Globe({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Mesh>(null);
  useFrame((_, dt) => { if (g.current) g.current.rotation.y += dt * 0.4; });
  return (<group position={p}>
    <Box p={[0, 0.45, 0]} s={[0.5, 0.9, 0.5]} c="#141a30" metal={0.5} rough={0.3} />
    <mesh ref={g} position={[0, 1.45, 0]}><icosahedronGeometry args={[0.5, 2]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} wireframe toneMapped={false} /></mesh>
  </group>);
}
function Lamp({ p, color }: { p: V3; color: string }) {
  return (<group position={p}><Box p={[0, 0.7, 0]} s={[0.06, 1.4, 0.06]} c="#2a3150" /><mesh position={[0, 1.5, 0]}><sphereGeometry args={[0.2, 12, 10]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.2} toneMapped={false} /></mesh></group>);
}
function Booth({ p, color, active }: { p: V3; color: string; active: boolean }) {
  return (<group position={p}>
    <Box p={[0, 1.2, 0]} s={[2, 2.4, 2]} c="#2a1640" opacity={0.55} />
    <Box p={[0, 2.42, 0]} s={[2.04, 0.06, 2.04]} c={color} e={color} ei={active ? 2.4 : 1} cast={false} />
    <Box p={[0, 0.02, 1.0]} s={[2.04, 0.05, 0.05]} c={color} e={color} ei={2} cast={false} />
    <MicStand p={[0, 0, 0]} />
  </group>);
}
function Rocket({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Group>(null);
  useFrame(({ clock }) => { if (g.current) g.current.position.y = 0.3 + Math.sin(clock.elapsedTime * 1.6) * 0.12; });
  return (<group position={p}><Box p={[0, 0.15, 0]} s={[0.9, 0.3, 0.9]} c="#141a30" />
    <group ref={g}>
      <mesh position={[0, 1, 0]} castShadow><capsuleGeometry args={[0.28, 0.8, 4, 12]} /><meshStandardMaterial color="#e8edf7" metalness={0.4} roughness={0.3} /></mesh>
      <mesh position={[0, 1.75, 0]}><coneGeometry args={[0.28, 0.4, 12]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.2} /></mesh>
      <mesh position={[0, 0.3, 0]}><coneGeometry args={[0.16, 0.4, 10]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
    </group></group>);
}
function Crown({ p }: { p: V3 }) {
  const g = useRef<THREE.Mesh>(null);
  useFrame((_, dt) => { if (g.current) g.current.rotation.y += dt * 0.6; });
  return <mesh ref={g} position={p}><torusKnotGeometry args={[0.22, 0.06, 48, 6, 2, 5]} /><meshStandardMaterial color="#FACC15" emissive="#FACC15" emissiveIntensity={1.6} metalness={0.8} roughness={0.2} toneMapped={false} /></mesh>;
}
function Beacon({ p, color }: { p: V3; color: string }) {
  const m = useRef<THREE.MeshStandardMaterial>(null);
  useFrame(({ clock }) => { if (m.current) m.current.emissiveIntensity = 1 + (Math.sin(clock.elapsedTime * 5) > 0.3 ? 3 : 0.2); });
  return <mesh position={p}><cylinderGeometry args={[0.18, 0.22, 0.3, 14]} /><meshStandardMaterial ref={m} color={color} emissive={color} toneMapped={false} /></mesh>;
}
function ClaudeCore({ p }: { p: V3 }) {
  const a = useRef<THREE.Mesh>(null); const b = useRef<THREE.Mesh>(null); const o = useRef<THREE.Mesh>(null);
  useFrame(({ clock }, dt) => {
    if (a.current) a.current.rotation.z += dt * 0.8;
    if (b.current) b.current.rotation.x += dt * 0.6;
    if (o.current) { o.current.position.y = 1.9 + Math.sin(clock.elapsedTime * 1.5) * 0.12; o.current.rotation.y += dt * 0.5; }
  });
  return (<group position={p}>
    <mesh position={[0, 0.3, 0]} castShadow><cylinderGeometry args={[1.1, 1.3, 0.6, 32]} /><meshStandardMaterial color="#141a30" metalness={0.5} roughness={0.3} /></mesh>
    <mesh position={[0, 0.61, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.12, 0.04, 8, 60]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={2.6} toneMapped={false} /></mesh>
    <mesh ref={o} position={[0, 1.9, 0]}><icosahedronGeometry args={[0.55, 1]} /><meshStandardMaterial color="#FF7A24" emissive="#FF9F5A" emissiveIntensity={1.8} flatShading toneMapped={false} /></mesh>
    <mesh ref={a} position={[0, 1.9, 0]}><torusGeometry args={[0.9, 0.025, 6, 64]} /><meshStandardMaterial color="#20D9FF" emissive="#20D9FF" emissiveIntensity={2.2} toneMapped={false} /></mesh>
    <mesh ref={b} position={[0, 1.9, 0]}><torusGeometry args={[1.05, 0.02, 6, 64]} /><meshStandardMaterial color="#A855F7" emissive="#A855F7" emissiveIntensity={2.2} toneMapped={false} /></mesh>
  </group>);
}

/* ---------------- één ruimte ---------------- */
interface Seat { status: Status; shirt: string; skin?: string; hair?: string; label: string; onClick?: () => void; big?: boolean }
const DESKS: V3[] = [[-2.4, 0, 1.0], [0.4, 0, 1.0], [3.0, 0, 1.0], [-2.4, 0, 3.4], [0.4, 0, 3.4], [3.0, 0, 3.4]];

function NeonRoom({ r, seats, lit, alert, onSelect, onHover }: { r: RoomDef; seats: Seat[]; lit: boolean; alert: boolean; onSelect: () => void; onHover: (h: boolean) => void }) {
  const pos = cellPos(r.cell[0], r.cell[1]);
  const c = r.color;
  const deskN = r.props === 'coach' ? 0 : Math.max(2, Math.min(6, seats.length + 1));
  const edge = useRef<THREE.MeshStandardMaterial>(null);
  useFrame(({ clock }) => {
    if (!edge.current) return;
    const pulse = alert ? 1.4 + Math.sin(clock.elapsedTime * 5) * 1 : 0;
    edge.current.emissiveIntensity = (lit ? 3.2 : 1.5) + pulse;
  });
  return (
    <group position={pos}
      onClick={(e) => { e.stopPropagation(); onSelect(); }}
      onPointerOver={(e) => { e.stopPropagation(); onHover(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { onHover(false); document.body.style.cursor = 'auto'; }}>
      {/* vloer */}
      <mesh position={[0, -0.08, 0]} receiveShadow>
        <boxGeometry args={[ROOM, 0.16, ROOM]} />
        <meshStandardMaterial color="#0d1428" roughness={0.35} metalness={0.4} emissive={c} emissiveIntensity={lit ? 0.09 : 0.025} />
      </mesh>
      <mesh position={[0.4, 0.003, 1.6]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[8.4, 5.4]} />
        <meshStandardMaterial color="#141c36" roughness={0.9} />
      </mesh>
      {/* neonrand rondom de vloer */}
      {([[0, HALF - 0.04, ROOM, 0.05], [0, -HALF + 0.04, ROOM, 0.05]] as const).map(([x, z, w, d], i) => (
        <mesh key={`z${i}`} position={[x, 0.02, z]}><boxGeometry args={[w, 0.04, d]} /><meshStandardMaterial ref={i === 0 ? edge : undefined} color={c} emissive={c} emissiveIntensity={1.5} toneMapped={false} /></mesh>
      ))}
      {([HALF - 0.04, -HALF + 0.04] as const).map((x, i) => (
        <mesh key={`x${i}`} position={[x, 0.02, 0]}><boxGeometry args={[0.05, 0.04, ROOM]} /><meshStandardMaterial color={c} emissive={c} emissiveIntensity={lit ? 3 : 1.5} toneMapped={false} /></mesh>
      ))}
      {/* achterwanden: donker metaal met lichtlijn */}
      <Box p={[-HALF + 0.07, H / 2, 0]} s={[0.14, H, ROOM]} c="#101830" metal={0.5} rough={0.35} />
      <Box p={[0, H / 2, -HALF + 0.07]} s={[ROOM, H, 0.14]} c="#101830" metal={0.5} rough={0.35} />
      <Box p={[-HALF + 0.15, H - 0.12, 0]} s={[0.03, 0.05, ROOM]} c={c} e={c} ei={lit ? 2.6 : 1.3} cast={false} />
      <Box p={[0, H - 0.12, -HALF + 0.15]} s={[ROOM, 0.05, 0.03]} c={c} e={c} ei={lit ? 2.6 : 1.3} cast={false} />
      {/* glazen voorwanden met stijlen */}
      <mesh position={[HALF - 0.03, 1.1, 0]}><boxGeometry args={[0.04, 2.2, ROOM]} /><meshStandardMaterial color="#8fd6ff" transparent opacity={0.1} roughness={0.05} metalness={0.2} depthWrite={false} /></mesh>
      <mesh position={[0, 1.1, HALF - 0.03]}><boxGeometry args={[ROOM, 2.2, 0.04]} /><meshStandardMaterial color="#8fd6ff" transparent opacity={0.1} roughness={0.05} metalness={0.2} depthWrite={false} /></mesh>
      {[-HALF, 0, HALF].map((t) => (<group key={t}>
        <Box p={[HALF - 0.03, 1.1, t]} s={[0.07, 2.2, 0.07]} c="#1b2442" e={c} ei={0.4} metal={0.6} rough={0.3} />
        <Box p={[t, 1.1, HALF - 0.03]} s={[0.07, 2.2, 0.07]} c="#1b2442" e={c} ei={0.4} metal={0.6} rough={0.3} />
      </group>))}
      <Box p={[HALF - 0.03, 2.22, 0]} s={[0.06, 0.04, ROOM]} c={c} e={c} ei={lit ? 2.4 : 1} cast={false} />
      <Box p={[0, 2.22, HALF - 0.03]} s={[ROOM, 0.04, 0.06]} c={c} e={c} ei={lit ? 2.4 : 1} cast={false} />
      {/* bureaus + medewerkers */}
      {DESKS.slice(0, deskN).map((d, i) => <Desk key={i} p={d} screen={c} active={!!seats[i] && (seats[i].status === 'werkt' || seats[i].status === 'bezig')} dual={i === 0} />)}
      {seats.slice(0, deskN).map((s, i) => (
        <Worker key={i} p={[DESKS[i][0], 0, DESKS[i][2] + 0.55]} rot={Math.PI} {...s} />
      ))}
      {r.props === 'coach' && seats[0] && <Worker p={[1.8, 0, 0.6]} rot={Math.PI * 0.75} {...seats[0]} />}
      {r.props === 'crisis' && seats.length === 0 && [0, 1, 2].map((i) => <Chair key={i} p={[-0.8 + i * 1.2, 0, -0.3]} rot={Math.PI} />)}
      <Props r={r} active={lit || seats.some((s) => s.status === 'werkt')} />
      <Plant p={[HALF - 0.6, 0, -HALF + 0.6]} scale={0.8} />
      <Plant p={[-HALF + 0.6, 0, HALF - 0.6]} scale={0.7} />
      {/* bord */}
      <Html position={[-1.4, H + 0.5, -1.4]} center zIndexRange={[20, 10]}>
        <button onClick={onSelect} className="dm-roomsign" style={{ ['--c' as string]: c, opacity: lit ? 1 : 0.92 }}>
          <span className="dm-roomsign-ico">{r.icon}</span>
          <span className="text-left leading-tight"><span className="block text-[13px] font-extrabold uppercase tracking-wide text-white">{r.naam}</span><span className="block text-[11px] text-slate-300">{r.sub}</span></span>
          {alert && <span className="ml-1 h-2 w-2 rounded-full bg-[#FF9F1C] shadow-[0_0_8px_#FF9F1C]" />}
        </button>
      </Html>
    </group>
  );
}

/* ---------------- receptie in het midden ---------------- */
function Reception() {
  const holo = useRef<THREE.Mesh>(null); const ring1 = useRef<THREE.Mesh>(null); const ring2 = useRef<THREE.Mesh>(null);
  const play = useMemo(() => {
    const cv = document.createElement('canvas'); cv.width = 256; cv.height = 256; const g = cv.getContext('2d')!;
    g.shadowColor = '#FF7A24'; g.shadowBlur = 30; g.strokeStyle = '#FFB070'; g.lineWidth = 14; g.lineJoin = 'round';
    g.beginPath(); g.moveTo(92, 64); g.lineTo(196, 128); g.lineTo(92, 192); g.closePath(); g.stroke();
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
  }, []);
  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime;
    if (holo.current) (holo.current.material as THREE.MeshStandardMaterial).opacity = 0.16 + Math.sin(t * 2) * 0.04;
    if (ring1.current) { ring1.current.position.y = 1 + ((t * 0.6) % 1) * 4.5; (ring1.current.material as THREE.MeshBasicMaterial).opacity = 1 - ((t * 0.6) % 1); }
    if (ring2.current) ring2.current.rotation.z += dt * 0.5;
  });
  const W = 2 * ROOM + GAP;
  return (
    <group position={[0, 0, 0]}>
      {/* vloer receptie */}
      <mesh position={[0, -0.08, 0]} receiveShadow><boxGeometry args={[W, 0.16, ROOM]} /><meshStandardMaterial color="#0b1124" roughness={0.25} metalness={0.5} /></mesh>
      <mesh position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[3.6, 3.75, 72]} /><meshBasicMaterial color="#20D9FF" toneMapped={false} /></mesh>
      <mesh position={[0, 0.006, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[4.4, 4.48, 72]} /><meshBasicMaterial color="#FF7A24" toneMapped={false} /></mesh>
      {/* podium */}
      <mesh position={[0, 0.2, 0]} castShadow receiveShadow><cylinderGeometry args={[3.2, 3.4, 0.4, 48]} /><meshStandardMaterial color="#141b36" metalness={0.5} roughness={0.25} /></mesh>
      <mesh position={[0, 0.41, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[3.22, 0.05, 8, 80]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={2.4} toneMapped={false} /></mesh>
      {/* gebogen balie */}
      <mesh position={[0, 0.95, 0]} rotation={[0, Math.PI * 0.25 + Math.PI * 0.15, 0]} castShadow>
        <cylinderGeometry args={[2.2, 2.2, 1.1, 40, 1, true, 0, Math.PI * 1.1]} />
        <meshStandardMaterial color="#1a2342" metalness={0.6} roughness={0.25} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0, 1.5, 0]} rotation={[0, Math.PI * 0.4, 0]}>
        <cylinderGeometry args={[2.22, 2.22, 0.05, 40, 1, true, 0, Math.PI * 1.1]} />
        <meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={2.2} toneMapped={false} side={THREE.DoubleSide} />
      </mesh>
      {/* het hoofdpersonage achter de balie */}
      <Mascot p={[-0.3, 0.4, -0.3]} rot={Math.PI / 4} s={1.0} />
      {/* hologramzuil */}
      <mesh ref={holo} position={[0, 3.6, 0]}><cylinderGeometry args={[1.6, 1.6, 5.2, 48, 1, true]} /><meshStandardMaterial color="#20D9FF" emissive="#20D9FF" emissiveIntensity={0.8} transparent opacity={0.16} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} /></mesh>
      <mesh ref={ring1} position={[0, 1, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.62, 0.03, 6, 64]} /><meshBasicMaterial color="#9ff0ff" transparent toneMapped={false} /></mesh>
      <mesh position={[0, 6.25, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.65, 0.06, 8, 64]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={2.4} toneMapped={false} /></mesh>
      <mesh ref={ring2} position={[0, 4.4, 0]} rotation={[0, Math.PI / 4, 0]}><planeGeometry args={[2, 2]} /><meshBasicMaterial map={play} transparent toneMapped={false} side={THREE.DoubleSide} depthWrite={false} /></mesh>
      <NeonSign p={[0, 8.2, 0]} rot={Math.PI / 4} width={11} />
      {/* trappen naar voren */}
      {[0, 1, 2].map((i) => <Box key={i} p={[3.6 + i * 0.5, 0.06 - i * 0.02, 3.6 + i * 0.5]} s={[3, 0.12, 0.5]} r={[0, Math.PI / 4, 0]} c="#141b36" e="#20D9FF" ei={0.25} />)}
      {/* lounge */}
      <Sofa p={[-7.2, 0, 2.6]} rot={Math.PI / 2} color="#22305a" />
      <Sofa p={[7.4, 0, -2.6]} rot={-Math.PI / 2} color="#22305a" />
      {[[-8.6, -3.6], [8.6, 3.6], [-8.6, 3.8], [8.6, -3.8]].map(([x, z], i) => <Plant key={i} p={[x, 0, z]} scale={0.9} />)}
      <FloatingMarks center={[0, 0, 0]} spread={8} n={6} />
    </group>
  );
}

/* ---------------- de scène ---------------- */
function Scene({ mode }: { mode: WorldMode }) {
  const activity = useLive((s) => s.data.activity);
  const { agents, selectDept, selectAgent, setPage } = useGame(useShallow((s) => ({ agents: s.agents, selectDept: s.selectDept, selectAgent: s.selectAgent, setPage: s.setPage })));
  const { focus, setFocus, openWorker, hover, setHover } = useWorld(useShallow((s) => ({ focus: s.focus, setFocus: s.setFocus, openWorker: s.openWorker, hover: s.hover, setHover: s.setHover })));
  const per = useMemo(() => threadsPerRoom(activity), [activity]);
  const SHIRTS = ['#FF7A24', '#398CFF', '#A855F7', '#21D6A0', '#FF4DB8', '#20D9FF'];

  const seatsFor = (r: RoomDef): Seat[] => {
    if (mode === 'studio' && r.game) {
      const list = agents.filter((a) => (r.game === 'warroom' ? false : a.department === r.game)).slice(0, 5);
      return list.map((a) => ({
        status: a.state === 'working' ? 'werkt' : a.state === 'meeting' ? 'bezig' : a.state === 'training' ? 'wacht' : 'offline',
        shirt: a.avatar.shirt, skin: a.avatar.skin, hair: a.avatar.hair, label: a.name, onClick: () => selectAgent(a.id),
      }));
    }
    const list = per[r.id];
    const st = statusOf(list);
    const main: Seat = { status: r.id === 'coach' ? 'werkt' : st, shirt: r.id === 'coach' ? '#FF7A24' : r.color, label: r.agent, big: true, onClick: () => { if (mode === 'panel') setPage('driftmark'); openWorker(r.id); } };
    const extra = list.filter((a) => a.state === 'working' || a.state === 'blocked' || a.state === 'review_ready').slice(0, 2)
      .map((a, i): Seat => ({ status: statusOf([a]), shirt: SHIRTS[(i + r.cell[0] + r.cell[1]) % SHIRTS.length], label: a.title, onClick: main.onClick }));
    return [main, ...extra];
  };

  return (
    <>
      <color attach="background" args={['#050816']} />
      <fog attach="fog" args={['#050816', 90, 160]} />
      <OrthographicCamera makeDefault position={[60, 56, 60]} zoom={14} near={-200} far={400} />
      <CameraRig mode={mode} />
      <ambientLight intensity={0.42} color="#8fa0ff" />
      <hemisphereLight args={['#a9bcff', '#120a26', 0.45]} />
      <directionalLight position={[24, 36, 14]} intensity={1.35} color="#fff1e0" castShadow shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-34} shadow-camera-right={34} shadow-camera-top={30} shadow-camera-bottom={-30} shadow-bias={-0.0004} />
      <pointLight position={[-26, 10, 12]} color="#FF7A24" intensity={70} distance={70} decay={1.4} />
      <pointLight position={[18, 10, -22]} color="#20D9FF" intensity={70} distance={70} decay={1.4} />
      <pointLight position={[0, 7, 0]} color="#20D9FF" intensity={25} distance={18} decay={1.6} />

      {/* grondplaat met lichtlijnen tussen de afdelingen */}
      <mesh position={[0, -0.45, 0]} receiveShadow><boxGeometry args={[4 * ROOM + 3 * GAP + 2.4, 0.6, 3 * ROOM + 2 * GAP + 2.4]} /><meshStandardMaterial color="#0a0f22" roughness={0.4} metalness={0.5} /></mesh>
      <mesh position={[0, -0.78, 0]}><boxGeometry args={[4 * ROOM + 3 * GAP + 3, 0.06, 3 * ROOM + 2 * GAP + 3]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={1.4} toneMapped={false} /></mesh>
      {[-1, 0, 1].map((i) => <Box key={`cx${i}`} p={[i * (ROOM + GAP), -0.13, 0]} s={[0.08, 0.02, 3 * ROOM + 2 * GAP]} c="#20D9FF" e="#20D9FF" ei={1.2} cast={false} />)}
      {[-0.5, 0.5].map((i) => <Box key={`cz${i}`} p={[0, -0.13, i * (ROOM + GAP)]} s={[4 * ROOM + 3 * GAP, 0.02, 0.08]} c="#A855F7" e="#A855F7" ei={1.2} cast={false} />)}

      <Reception />
      {ROOMS.map((r) => {
        const list = per[r.id];
        const alert = mode !== 'studio' && (statusOf(list) === 'wacht' || statusOf(list) === 'probleem');
        return (
          <NeonRoom key={r.id} r={r} seats={seatsFor(r)} lit={focus === r.id || hover === r.id} alert={alert}
            onHover={(h) => setHover(h ? r.id : null)}
            onSelect={() => {
              if (mode === 'studio') { if (r.game) selectDept(r.game as never); else setPage(r.page ?? 'coach'); return; }
              if (mode === 'panel') setPage('driftmark');
              setFocus(r.id as RoomId);
            }} />
        );
      })}
      <EffectComposer multisampling={0}>
        <Bloom intensity={0.75} luminanceThreshold={0.82} luminanceSmoothing={0.2} mipmapBlur />
        <Vignette eskil={false} offset={0.28} darkness={0.6} />
      </EffectComposer>
    </>
  );
}

export default function NeonOffice({ mode }: { mode: WorldMode }) {
  const [dpr, setDpr] = useState(1.5);
  const setFocus = useWorld((s) => s.setFocus);
  return (
    <Canvas shadows dpr={mode === 'panel' ? 1 : dpr} gl={{ antialias: true, powerPreference: 'high-performance' }}
      onPointerMissed={(e) => { if (mode === 'home' && (e.target as HTMLElement)?.tagName === 'CANVAS') setFocus(null); }}>
      <PerformanceMonitor onDecline={() => setDpr(1)} onIncline={() => setDpr(1.6)} />
      <Scene mode={mode} />
    </Canvas>
  );
}
