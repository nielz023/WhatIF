import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import type { Group, Mesh, MeshStandardMaterial } from 'three';
import { Vector3 } from 'three';
import type { Agent } from '../../types';

const STATE_COLOR: Record<Agent['state'], string> = {
  working: '#22c55e',
  meeting: '#3b82f6',
  idle: '#94a3b8',
  training: '#a855f7',
};

interface Props {
  agent: Agent;
  seat: [number, number, number]; // world position of desk chair
  meet: [number, number, number]; // world position near meeting table
  meetCenter: [number, number, number];
  idleSpot: [number, number, number];
  onSelect: (id: string) => void;
}

export function Employee({ agent, seat, meet, meetCenter, idleSpot, onSelect }: Props) {
  const root = useRef<Group>(null);
  const legL = useRef<Group>(null);
  const legR = useRef<Group>(null);
  const armL = useRef<Group>(null);
  const armR = useRef<Group>(null);
  const orb = useRef<Mesh>(null);
  const [hover, setHover] = useState(false);
  const target = useRef(new Vector3());
  const seed = useRef(Math.random() * 10);

  useFrame(({ clock }, dt) => {
    const g = root.current;
    if (!g) return;
    const t = clock.elapsedTime + seed.current;
    const s = agent.state;
    if (s === 'working') target.current.set(seat[0], 0, seat[2]);
    else if (s === 'meeting') target.current.set(meet[0], 0, meet[2]);
    else if (s === 'training') target.current.set(idleSpot[0] + Math.sin(t * 0.3) * 0.2, 0, idleSpot[2]);
    else target.current.set(idleSpot[0] + Math.sin(t * 0.25) * 0.9, 0, idleSpot[2] + Math.cos(t * 0.21) * 0.6);

    const dist = g.position.distanceTo(target.current);
    const walking = dist > 0.08;
    if (walking) {
      const dir = target.current.clone().sub(g.position).normalize();
      g.position.addScaledVector(dir, Math.min(dist, dt * 1.6));
      g.rotation.y = Math.atan2(dir.x, dir.z);
    } else if (s === 'working') {
      g.rotation.y = Math.PI; // face monitor (-z)
    } else if (s === 'meeting') {
      g.rotation.y = Math.atan2(meetCenter[0] - g.position.x, meetCenter[2] - g.position.z);
    }
    const seated = !walking && (s === 'working' || s === 'meeting');
    g.position.y = seated ? -0.28 : Math.abs(Math.sin(t * 8)) * (walking ? 0.04 : 0);

    const swing = walking ? Math.sin(t * 9) * 0.6 : 0;
    if (legL.current && legR.current) {
      legL.current.rotation.x = seated ? -Math.PI / 2 : swing;
      legR.current.rotation.x = seated ? -Math.PI / 2 : -swing;
    }
    if (armL.current && armR.current) {
      const typing = s === 'working' && seated;
      armL.current.rotation.x = typing ? -1.1 + Math.sin(t * 18) * 0.12 : -swing * 0.8 + (s === 'meeting' ? Math.sin(t * 2) * 0.3 - 0.3 : 0);
      armR.current.rotation.x = typing ? -1.1 + Math.cos(t * 17) * 0.12 : swing * 0.8 + (s === 'training' ? -2.4 + Math.sin(t * 3) * 0.3 : 0);
    }
    if (orb.current) {
      orb.current.position.y = 1.85 + Math.sin(t * 2.5) * 0.05;
      (orb.current.material as MeshStandardMaterial).emissiveIntensity = 1.6 + Math.sin(t * 4) * 0.6;
    }
  });

  const { skin, hair, shirt } = agent.avatar;
  return (
    <group
      ref={root}
      position={idleSpot}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { setHover(false); document.body.style.cursor = 'auto'; }}
      onClick={(e) => { e.stopPropagation(); onSelect(agent.id); }}
      scale={0.82}
    >
      {/* legs */}
      <group ref={legL} position={[-0.1, 0.62, 0]}>
        <mesh position={[0, -0.3, 0]} castShadow><boxGeometry args={[0.15, 0.6, 0.16]} /><meshStandardMaterial color="#1e293b" /></mesh>
      </group>
      <group ref={legR} position={[0.1, 0.62, 0]}>
        <mesh position={[0, -0.3, 0]} castShadow><boxGeometry args={[0.15, 0.6, 0.16]} /><meshStandardMaterial color="#1e293b" /></mesh>
      </group>
      {/* torso */}
      <mesh position={[0, 0.95, 0]} castShadow>
        <capsuleGeometry args={[0.2, 0.32, 4, 10]} />
        <meshStandardMaterial color={shirt} roughness={0.6} emissive={hover ? shirt : '#000'} emissiveIntensity={hover ? 0.5 : 0} />
      </mesh>
      {/* arms */}
      <group ref={armL} position={[-0.27, 1.12, 0]}>
        <mesh position={[0, -0.22, 0]} castShadow><capsuleGeometry args={[0.06, 0.3, 4, 6]} /><meshStandardMaterial color={shirt} /></mesh>
      </group>
      <group ref={armR} position={[0.27, 1.12, 0]}>
        <mesh position={[0, -0.22, 0]} castShadow><capsuleGeometry args={[0.06, 0.3, 4, 6]} /><meshStandardMaterial color={shirt} /></mesh>
      </group>
      {/* head */}
      <mesh position={[0, 1.45, 0]} castShadow>
        <sphereGeometry args={[0.19, 16, 14]} />
        <meshStandardMaterial color={skin} roughness={0.7} />
      </mesh>
      <mesh position={[0, 1.52, -0.02]} castShadow>
        <sphereGeometry args={[0.2, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial color={hair} roughness={0.9} />
      </mesh>
      {/* status orb */}
      <mesh ref={orb} position={[0, 1.85, 0]}>
        <sphereGeometry args={[0.065, 10, 10]} />
        <meshStandardMaterial color={STATE_COLOR[agent.state]} emissive={STATE_COLOR[agent.state]} emissiveIntensity={2} toneMapped={false} />
      </mesh>
      {hover && (
        <Html position={[0, 2.25, 0]} center distanceFactor={undefined} zIndexRange={[40, 0]}>
          <div className="pointer-events-none whitespace-nowrap rounded-lg border border-white/10 bg-slate-950/90 px-2 py-1 text-[13px] text-white shadow-xl">
            <div className="font-semibold">{agent.name}</div>
            <div className="text-slate-400">Lv {agent.level} · {agent.state}</div>
          </div>
        </Html>
      )}
    </group>
  );
}
