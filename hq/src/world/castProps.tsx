/**
 * Spullen voor de cast (niels 2026-11-07): een flip-over bij de script-briefing, een fotostudio (achtergrond, camera
 * op statief, twee softboxen met flits) voor de thumbnail en een filmcamera in de productiekamer. Alleen zichtbaar
 * zolang de cast daar aan het werk is (staff.ts). De microfoon staat al in de stemcabine (office_build.py).
 */
import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { CrewMember } from './crew';
import { R_IN, R_OUT, slotAngle, roomById, type RoomId } from './rooms';
import { useFloor } from './floors';

type V3 = [number, number, number];
const at = (room: RoomId, u: number, v: number, y = 0): V3 => {
  const r = roomById(room)!; const a = slotAngle(r.slot); const rad = (R_IN + R_OUT) / 2 + v; const ang = a + u / rad;
  return [Math.sin(ang) * rad, y, Math.cos(ang) * rad];
};
const yawAt = (from: V3, to: V3) => Math.atan2(to[0] - from[0], to[2] - from[2]); // lokale +z wijst naar `to`

function tex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}

const DARK = new THREE.MeshStandardMaterial({ color: '#1a1d2a', roughness: 0.45, metalness: 0.5 });
const METAL = new THREE.MeshStandardMaterial({ color: '#8b93a8', roughness: 0.3, metalness: 0.8 });

/** statief met drie poten */
function Tripod({ h }: { h: number }) {
  return (
    <group>
      {[0, 1, 2].map((k) => {
        const a = (k / 3) * Math.PI * 2; const sp = 0.32;
        const len = Math.hypot(sp, h); const tilt = Math.atan2(sp, h);
        return (
          <mesh key={k} material={DARK} position={[Math.sin(a) * sp / 2, h / 2, Math.cos(a) * sp / 2]} rotation={[-tilt * Math.cos(a), 0, tilt * Math.sin(a)]}>
            <cylinderGeometry args={[0.014, 0.018, len, 6]} />
          </mesh>
        );
      })}
      <mesh material={METAL} position={[0, h, 0]}><cylinderGeometry args={[0.04, 0.05, 0.08, 10]} /></mesh>
    </group>
  );
}

function Flipchart({ p, ry }: { p: V3; ry: number }) {
  const map = useMemo(() => tex(256, 320, (g) => {
    g.fillStyle = '#f7f5ef'; g.fillRect(0, 0, 256, 320);
    g.fillStyle = '#FF6A3D'; g.font = 'bold 40px sans-serif'; g.textAlign = 'center'; g.fillText('SCRIPT', 128, 52);
    g.strokeStyle = '#2b3350'; g.lineWidth = 5; g.lineCap = 'round';
    [92, 128, 164, 200].forEach((y, i) => { g.beginPath(); g.moveTo(34, y); g.lineTo(222 - i * 22, y); g.stroke(); });
    g.strokeStyle = '#398CFF'; g.lineWidth = 6; g.beginPath(); g.moveTo(40, 280); g.lineTo(90, 236); g.lineTo(140, 262); g.lineTo(210, 222); g.stroke();
    g.fillStyle = '#FF7A24'; g.beginPath(); g.arc(210, 222, 9, 0, Math.PI * 2); g.fill();
  }), []);
  return (
    <group position={p} rotation={[0, ry, 0]}>
      {[-0.42, 0.42].map((x) => <mesh key={x} material={DARK} position={[x, 0.85, -0.08]} rotation={[0.12, 0, 0]}><cylinderGeometry args={[0.02, 0.02, 1.72, 6]} /></mesh>)}
      <mesh material={DARK} position={[0, 0.8, -0.32]} rotation={[-0.32, 0, 0]}><cylinderGeometry args={[0.018, 0.018, 1.62, 6]} /></mesh>
      <mesh position={[0, 1.22, 0.0]} rotation={[-0.12, 0, 0]}><boxGeometry args={[0.92, 1.12, 0.03]} /><meshStandardMaterial color="#d9dbe3" roughness={0.6} /></mesh>
      <mesh position={[0, 1.22, 0.018]} rotation={[-0.12, 0, 0]}><planeGeometry args={[0.86, 1.06]} /><meshStandardMaterial map={map} roughness={0.85} emissive="#ffffff" emissiveMap={map} emissiveIntensity={0.18} /></mesh>
    </group>
  );
}

function PhotoStudio({ room }: { room: RoomId }) {
  const back = useMemo(() => tex(512, 320, (g) => {
    const gr = g.createLinearGradient(0, 0, 512, 320); gr.addColorStop(0, '#FF7A24'); gr.addColorStop(0.55, '#d0428f'); gr.addColorStop(1, '#3b2a8f');
    g.fillStyle = gr; g.fillRect(0, 0, 512, 320);
    const rg = g.createRadialGradient(256, 150, 20, 256, 150, 260); rg.addColorStop(0, 'rgba(255,240,220,.45)'); rg.addColorStop(1, 'rgba(255,240,220,0)');
    g.fillStyle = rg; g.fillRect(0, 0, 512, 320);
    g.fillStyle = 'rgba(255,255,255,.18)'; g.font = 'bold 54px sans-serif'; g.textAlign = 'center'; g.fillText('WHAT IF?', 256, 296);
  }), []);
  const flash = useRef<THREE.MeshBasicMaterial>(null);
  const soft = useRef<THREE.MeshStandardMaterial[]>([]);
  useFrame(({ clock }) => {
    // flits vlak na elke nieuwe pose (crew.tsx wisselt elke 2,6 s)
    const ph = (clock.elapsedTime % 2.6) / 2.6; const f = ph < 0.12 ? Math.pow(1 - ph / 0.12, 2) : 0;
    if (flash.current) flash.current.opacity = f * 0.9;
    soft.current.forEach((m) => { if (m) m.emissiveIntensity = 0.8 + f * 5; });
  });
  const subj = at(room, 0, 3.2, 1.2);
  const bp = at(room, 0, 3.72); const cam = at(room, 0, 2.3);
  const camYaw = yawAt(cam, subj);
  return (
    <group>
      {/* achtergrond op twee palen */}
      <group position={bp} rotation={[0, yawAt(bp, at(room, 0, 0)), 0]}>
        {[-1.55, 1.55].map((x) => <mesh key={x} material={DARK} position={[x, 1.25, 0]}><cylinderGeometry args={[0.025, 0.03, 2.5, 6]} /></mesh>)}
        <mesh material={DARK} position={[0, 2.48, 0]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.03, 0.03, 3.2, 8]} /></mesh>
        <mesh position={[0, 1.3, 0.02]}><planeGeometry args={[3.0, 2.3]} /><meshStandardMaterial map={back} roughness={0.9} emissive="#ffffff" emissiveMap={back} emissiveIntensity={0.35} side={THREE.DoubleSide} /></mesh>
      </group>
      {/* camera op statief */}
      <group position={cam} rotation={[0, camYaw, 0]}>
        <Tripod h={1.25} />
        <mesh material={DARK} position={[0, 1.36, 0]}><boxGeometry args={[0.2, 0.15, 0.12]} /></mesh>
        <mesh material={METAL} position={[0, 1.36, 0.11]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.045, 0.05, 0.12, 14]} /></mesh>
        <mesh position={[0.06, 1.45, 0.0]}><boxGeometry args={[0.05, 0.03, 0.05]} /><meshStandardMaterial color="#222" /></mesh>
        <mesh position={[0, 1.36, 0.18]}><circleGeometry args={[0.12, 18]} /><meshBasicMaterial ref={flash} color="#fff6e6" transparent opacity={0} depthWrite={false} toneMapped={false} /></mesh>
      </group>
      {/* softboxen */}
      {[-1, 1].map((sd, i) => {
        const p = at(room, sd * 1.95, 2.72);
        return (
          <group key={sd} position={p} rotation={[0, yawAt(p, subj), 0]}>
            <Tripod h={1.55} />
            <mesh material={DARK} position={[0, 1.7, -0.08]}><boxGeometry args={[0.62, 0.62, 0.2]} /></mesh>
            <mesh position={[0, 1.7, 0.025]}><planeGeometry args={[0.56, 0.56]} />
              <meshStandardMaterial ref={(m) => { if (m) soft.current[i] = m; }} color="#ffffff" emissive="#fff3e0" emissiveIntensity={0.8} toneMapped={false} />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}

function FilmCamera({ room }: { room: RoomId }) {
  const rec = useRef<THREE.MeshBasicMaterial>(null);
  useFrame(({ clock }) => { if (rec.current) rec.current.opacity = Math.sin(clock.elapsedTime * 4) > 0 ? 1 : 0.15; });
  const p = at(room, -1.75, 1.5); const yaw = yawAt(p, at(room, -1.75, 2.4));
  return (
    <group position={p} rotation={[0, yaw, 0]}>
      <Tripod h={1.2} />
      <mesh material={DARK} position={[0, 1.33, -0.04]}><boxGeometry args={[0.24, 0.24, 0.42]} /></mesh>
      <mesh material={METAL} position={[0, 1.33, 0.24]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.07, 0.085, 0.16, 16]} /></mesh>
      {[-0.07, 0.11].map((z) => <mesh key={z} material={DARK} position={[0, 1.55, z]} rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[0.1, 0.1, 0.04, 18]} /></mesh>)}
      <mesh position={[0.1, 1.45, 0.1]}><sphereGeometry args={[0.018, 8, 6]} /><meshBasicMaterial ref={rec} color="#ff2a3a" transparent toneMapped={false} /></mesh>
      {/* klapbord op de grond ernaast */}
      <group position={[0.42, 0.02, 0.1]} rotation={[-Math.PI / 2, 0, 0.4]}>
        <mesh><boxGeometry args={[0.3, 0.24, 0.02]} /><meshStandardMaterial color="#14161f" /></mesh>
        <mesh position={[0, 0.13, 0.012]}><boxGeometry args={[0.3, 0.05, 0.02]} /><meshStandardMaterial color="#f4f4f4" /></mesh>
      </group>
    </group>
  );
}

export function CastProps({ members }: { members: CrewMember[] }) {
  const floor = useFloor((s) => s.floor);
  const here = (room: string, act: CrewMember['act']) => members.some((m) => m.room === room && m.act === act);
  const script = here('script', 'listen'), shoot = here('thumbnail', 'pose'), film = here('productie', 'act');
  if (floor === 1 || (!script && !shoot && !film)) return null;
  return (
    <group>
      {script && <Flipchart p={at('script', -2.05, 2.8)} ry={yawAt(at('script', -2.05, 2.8), at('script', -2.0, 1.5))} />}
      {shoot && <PhotoStudio room="thumbnail" />}
      {film && <FilmCamera room="productie" />}
    </group>
  );
}
