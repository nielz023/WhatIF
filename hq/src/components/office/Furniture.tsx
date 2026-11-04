import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import type { Mesh, MeshStandardMaterial } from 'three';

const WOOD = '#d08a4e';
const WOOD_DARK = '#a8693a';
const CHAIR = '#1e2336';

type V3 = [number, number, number];

export function Box({ p, s, c, e, ei = 1, r = [0, 0, 0], cast = true, rough = 0.7, metal = 0.05, opacity }: { p: V3; s: V3; c: string; e?: string; ei?: number; r?: V3; cast?: boolean; rough?: number; metal?: number; opacity?: number }) {
  return (
    <mesh position={p} rotation={r} castShadow={cast} receiveShadow>
      <boxGeometry args={s} />
      <meshStandardMaterial color={c} emissive={e ?? '#000'} emissiveIntensity={e ? ei : 0} roughness={rough} metalness={metal} transparent={opacity != null} opacity={opacity ?? 1} />
    </mesh>
  );
}

/** Desk with monitor(s), keyboard and office chair. Faces -z (monitor on the far side). */
export function Desk({ p, screen, active, dual }: { p: V3; screen: string; active: boolean; dual?: boolean }) {
  const scr = useRef<Mesh>(null);
  useFrame(({ clock }) => {
    if (!scr.current) return;
    const m = scr.current.material as MeshStandardMaterial;
    m.emissiveIntensity = active ? 1.6 + Math.sin(clock.elapsedTime * 6 + p[0] * 3) * 0.35 : 0.35;
  });
  const [x, , z] = p;
  return (
    <group position={[x, 0, z]}>
      {/* top + legs */}
      <Box p={[0, 0.74, 0]} s={[1.5, 0.08, 0.75]} c={WOOD} />
      <Box p={[-0.68, 0.36, 0]} s={[0.07, 0.72, 0.68]} c={WOOD_DARK} />
      <Box p={[0.68, 0.36, 0]} s={[0.07, 0.72, 0.68]} c={WOOD_DARK} />
      <Box p={[0.45, 0.5, 0.05]} s={[0.4, 0.4, 0.6]} c={WOOD_DARK} />
      {/* monitor */}
      <Box p={[dual ? -0.3 : 0, 0.83, -0.22]} s={[0.12, 0.1, 0.12]} c="#20263b" />
      <Box p={[dual ? -0.3 : 0, 1.05, -0.24]} s={[0.66, 0.4, 0.04]} c="#141826" />
      <mesh ref={scr} position={[dual ? -0.3 : 0, 1.05, -0.215]}>
        <planeGeometry args={[0.6, 0.34]} />
        <meshStandardMaterial color={screen} emissive={screen} emissiveIntensity={1.4} toneMapped={false} />
      </mesh>
      {dual && (
        <>
          <Box p={[0.38, 1.05, -0.22]} s={[0.56, 0.36, 0.04]} c="#141826" r={[0, -0.25, 0]} />
          <mesh position={[0.385, 1.05, -0.195]} rotation={[0, -0.25, 0]}>
            <planeGeometry args={[0.5, 0.3]} />
            <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={active ? 1.2 : 0.3} toneMapped={false} />
          </mesh>
        </>
      )}
      {/* keyboard & mouse */}
      <Box p={[0, 0.79, 0.08]} s={[0.5, 0.02, 0.16]} c="#dfe4f2" cast={false} />
      <Box p={[0.36, 0.79, 0.1]} s={[0.07, 0.02, 0.1]} c="#dfe4f2" cast={false} />
      {/* mug */}
      <mesh position={[-0.55, 0.83, 0.12]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, 0.1, 10]} />
        <meshStandardMaterial color="#f8fafc" />
      </mesh>
      <Chair p={[0, 0, 0.62]} />
    </group>
  );
}

export function Chair({ p, rot = 0 }: { p: V3; rot?: number }) {
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 0.46, 0]} s={[0.5, 0.08, 0.48]} c={CHAIR} />
      <Box p={[0, 0.78, 0.22]} s={[0.48, 0.6, 0.07]} c={CHAIR} />
      <Box p={[0, 0.24, 0]} s={[0.06, 0.42, 0.06]} c="#596079" metal={0.6} rough={0.3} />
      <Box p={[0, 0.04, 0]} s={[0.5, 0.04, 0.08]} c="#596079" />
      <Box p={[0, 0.04, 0]} s={[0.08, 0.04, 0.5]} c="#596079" />
    </group>
  );
}

export function Plant({ p, scale = 1 }: { p: V3; scale?: number }) {
  return (
    <group position={p} scale={scale}>
      <mesh position={[0, 0.22, 0]} castShadow>
        <cylinderGeometry args={[0.2, 0.15, 0.44, 12]} />
        <meshStandardMaterial color="#f1f5f9" roughness={0.6} />
      </mesh>
      <mesh position={[0, 0.7, 0]} castShadow>
        <icosahedronGeometry args={[0.36, 0]} />
        <meshStandardMaterial color="#3fa34d" roughness={0.8} flatShading />
      </mesh>
      <mesh position={[0.12, 0.98, 0.05]} castShadow>
        <icosahedronGeometry args={[0.22, 0]} />
        <meshStandardMaterial color="#57c26a" roughness={0.8} flatShading />
      </mesh>
    </group>
  );
}

export function Bookshelf({ p, rot = 0 }: { p: V3; rot?: number }) {
  const colors = ['#ef4444', '#3b82f6', '#f59e0b', '#22c55e', '#a855f7', '#e2e8f0'];
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 1.0, 0]} s={[1.3, 2.0, 0.4]} c={WOOD_DARK} />
      {[0.45, 1.0, 1.55].map((y, i) => (
        <group key={i}>
          {colors.map((c, j) => (
            <Box key={j} p={[-0.48 + j * 0.19, y + 0.17, 0.08]} s={[0.14, 0.34 - (j % 3) * 0.04, 0.28]} c={colors[(j + i) % colors.length]} cast={false} />
          ))}
        </group>
      ))}
    </group>
  );
}

export function MeetingTable({ p, color }: { p: V3; color: string }) {
  return (
    <group position={p}>
      <mesh position={[0, 0.72, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.9, 0.9, 0.07, 28]} />
        <meshStandardMaterial color="#f8fafc" roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.36, 0]}>
        <cylinderGeometry args={[0.08, 0.2, 0.7, 10]} />
        <meshStandardMaterial color="#64748b" metalness={0.6} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.77, 0]}>
        <torusGeometry args={[0.55, 0.012, 6, 40]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2} toneMapped={false} />
      </mesh>
      {[0, 1, 2, 3, 4].map((i) => {
        const a = (i / 5) * Math.PI * 2 + 0.3;
        return <Chair key={i} p={[Math.cos(a) * 1.35, 0, Math.sin(a) * 1.35]} rot={-a - Math.PI / 2} />;
      })}
    </group>
  );
}

export function Whiteboard({ p, rot = 0, accent }: { p: V3; rot?: number; accent: string }) {
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 1.3, 0]} s={[1.6, 1.0, 0.05]} c="#f8fafc" rough={0.2} />
      <Box p={[-0.3, 1.45, 0.03]} s={[0.7, 0.04, 0.01]} c={accent} cast={false} />
      <Box p={[-0.2, 1.3, 0.03]} s={[0.9, 0.04, 0.01]} c="#334155" cast={false} />
      <Box p={[-0.35, 1.15, 0.03]} s={[0.6, 0.04, 0.01]} c="#334155" cast={false} />
      <Box p={[-0.55, 0.4, 0]} s={[0.05, 0.8, 0.05]} c="#94a3b8" />
      <Box p={[0.55, 0.4, 0]} s={[0.05, 0.8, 0.05]} c="#94a3b8" />
    </group>
  );
}

export function Sofa({ p, rot = 0, color = '#2a2f45' }: { p: V3; rot?: number; color?: string }) {
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 0.25, 0]} s={[2.0, 0.4, 0.85]} c={color} />
      <Box p={[0, 0.6, -0.35]} s={[2.0, 0.6, 0.18]} c={color} />
      <Box p={[-0.95, 0.45, 0]} s={[0.15, 0.45, 0.85]} c={color} />
      <Box p={[0.95, 0.45, 0]} s={[0.15, 0.45, 0.85]} c={color} />
      <Box p={[-0.45, 0.5, 0.05]} s={[0.8, 0.12, 0.65]} c="#3b4262" />
      <Box p={[0.45, 0.5, 0.05]} s={[0.8, 0.12, 0.65]} c="#3b4262" />
    </group>
  );
}

export function ServerRack({ p, rot = 0 }: { p: V3; rot?: number }) {
  const ref = useRef<Mesh>(null);
  useFrame(({ clock }) => {
    if (ref.current) (ref.current.material as MeshStandardMaterial).emissiveIntensity = 1 + Math.sin(clock.elapsedTime * 9) * 0.9;
  });
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 1.0, 0]} s={[0.7, 2.0, 0.7]} c="#111827" metal={0.4} rough={0.4} />
      {[0.4, 0.75, 1.1, 1.45, 1.8].map((y) => (
        <Box key={y} p={[0, y, 0.36]} s={[0.55, 0.05, 0.01]} c="#22d3ee" e="#22d3ee" ei={1.4} cast={false} />
      ))}
      <mesh ref={ref} position={[0.22, 1.9, 0.36]}>
        <boxGeometry args={[0.06, 0.06, 0.02]} />
        <meshStandardMaterial color="#22c55e" emissive="#22c55e" toneMapped={false} />
      </mesh>
    </group>
  );
}

export function WallScreen({ p, rot = 0, w = 2.2, h = 1.2, color }: { p: V3; rot?: number; w?: number; h?: number; color: string }) {
  const ref = useRef<Mesh>(null);
  useFrame(({ clock }) => {
    if (ref.current) (ref.current.material as MeshStandardMaterial).emissiveIntensity = 0.9 + Math.sin(clock.elapsedTime * 1.5) * 0.2;
  });
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 0, 0]} s={[w + 0.1, h + 0.1, 0.06]} c="#0b0f1d" />
      <mesh ref={ref} position={[0, 0, 0.035]}>
        <planeGeometry args={[w, h]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1} toneMapped={false} />
      </mesh>
      {/* chart bars */}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <Box key={i} p={[-w / 2 + 0.3 + i * (w - 0.5) / 5, -h / 2 + 0.15 + (0.15 + ((i * 37) % 5) * 0.12) / 2, 0.05]} s={[0.16, 0.15 + ((i * 37) % 5) * 0.12, 0.01]} c="#ffffff" e="#ffffff" ei={0.8} cast={false} />
      ))}
    </group>
  );
}

export function Frame({ p, rot = 0, color }: { p: V3; rot?: number; color: string }) {
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[0, 0, 0]} s={[0.55, 0.7, 0.04]} c="#f8fafc" cast={false} />
      <Box p={[0, 0.02, 0.025]} s={[0.42, 0.52, 0.01]} c={color} cast={false} />
    </group>
  );
}

export function MicStand({ p }: { p: V3 }) {
  return (
    <group position={p}>
      <Box p={[0, 0.02, 0]} s={[0.4, 0.04, 0.4]} c="#1f2937" />
      <Box p={[0, 0.75, 0]} s={[0.04, 1.5, 0.04]} c="#94a3b8" metal={0.7} rough={0.3} />
      <mesh position={[0, 1.55, 0.05]} castShadow>
        <capsuleGeometry args={[0.07, 0.15, 4, 10]} />
        <meshStandardMaterial color="#334155" metalness={0.5} />
      </mesh>
      <mesh position={[0, 1.55, 0.25]}>
        <circleGeometry args={[0.16, 20]} />
        <meshStandardMaterial color="#ec4899" emissive="#ec4899" emissiveIntensity={0.6} transparent opacity={0.6} />
      </mesh>
    </group>
  );
}

export function Easel({ p, rot = 0 }: { p: V3; rot?: number }) {
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <Box p={[-0.35, 0.7, 0]} s={[0.05, 1.4, 0.05]} c={WOOD} r={[0.12, 0, 0.1]} />
      <Box p={[0.35, 0.7, 0]} s={[0.05, 1.4, 0.05]} c={WOOD} r={[0.12, 0, -0.1]} />
      <Box p={[0, 1.15, 0.06]} s={[0.95, 0.65, 0.04]} c="#fde047" e="#f59e0b" ei={0.25} />
      <Box p={[-0.15, 1.15, 0.09]} s={[0.35, 0.3, 0.01]} c="#ef4444" cast={false} />
    </group>
  );
}

export function Cooler({ p }: { p: V3 }) {
  return (
    <group position={p}>
      <Box p={[0, 0.5, 0]} s={[0.4, 1.0, 0.4]} c="#e2e8f0" />
      <mesh position={[0, 1.2, 0]}>
        <cylinderGeometry args={[0.16, 0.16, 0.4, 14]} />
        <meshStandardMaterial color="#60a5fa" transparent opacity={0.6} roughness={0.1} />
      </mesh>
    </group>
  );
}
