import { useState } from 'react';
import { Html } from '@react-three/drei';
import type { Agent, DepartmentId } from '../../types';
import { Box, Bookshelf, Cooler, Desk, Easel, Frame, MeetingTable, MicStand, Plant, ServerRack, Sofa, WallScreen, Whiteboard, Chair } from './Furniture';
import { Employee } from './Employee';

export const ROOM = 10;
const H = 2.7; // wall height
const HALF = ROOM / 2;

const DESK_SLOTS: [number, number][] = [[-2.4, 0.6], [0.4, 0.6], [3.1, 0.6], [-2.4, 3.1], [0.4, 3.1], [3.1, 3.1]];
const MEET_CENTER: [number, number, number] = [-2.4, 0, -2.5];
const IDLE: [number, number][] = [[1.6, -0.9], [-0.4, -1.0], [2.8, -1.5], [0.2, 1.9], [-3.6, 1.8], [3.9, 1.9], [1.0, -2.2], [-1.2, 4.2]];

export interface RoomProps {
  id: DepartmentId | 'warroom';
  name: string;
  icon: string;
  color: string;
  wall: string;
  floor: string;
  position: [number, number, number];
  agents: Agent[];
  pending: number;
  selected: boolean;
  onSelect: () => void;
  onSelectAgent: (id: string) => void;
}

export function Room({ id, name, icon, color, wall, floor, position, agents, pending, selected, onSelect, onSelectAgent }: RoomProps) {
  const [hover, setHover] = useState(false);
  const working = agents.filter((a) => a.state === 'working').length;
  const deskCount = id === 'warroom' ? 0 : id === 'ceo' ? Math.max(3, Math.min(6, agents.length)) : Math.max(4, Math.min(6, agents.length));
  const lit = hover || selected;

  return (
    <group
      position={position}
      onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { setHover(false); document.body.style.cursor = 'auto'; }}
      onClick={(e) => { e.stopPropagation(); onSelect(); }}
    >
      {/* floor */}
      <mesh position={[0, -0.1, 0]} receiveShadow>
        <boxGeometry args={[ROOM, 0.2, ROOM]} />
        <meshStandardMaterial color={floor} roughness={0.85} emissive={color} emissiveIntensity={lit ? 0.12 : 0.02} />
      </mesh>
      {/* floor edge glow */}
      <Box p={[0, 0.01, HALF - 0.03]} s={[ROOM, 0.03, 0.06]} c={color} e={color} ei={lit ? 3 : 1.2} cast={false} />
      <Box p={[HALF - 0.03, 0.01, 0]} s={[0.06, 0.03, ROOM]} c={color} e={color} ei={lit ? 3 : 1.2} cast={false} />
      {/* rug */}
      <mesh position={[0.4, 0.005, 1.9]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[8.6, 4.6]} />
        <meshStandardMaterial color="#2a3150" roughness={1} />
      </mesh>

      {/* back walls */}
      <Box p={[-HALF + 0.08, H / 2, 0]} s={[0.16, H, ROOM]} c={wall} rough={0.9} />
      <Box p={[0, H / 2, -HALF + 0.08]} s={[ROOM, H, 0.16]} c={wall} rough={0.9} />
      {/* wall skirting & neon strips */}
      <Box p={[-HALF + 0.18, H - 0.06, 0]} s={[0.04, 0.05, ROOM]} c={color} e={color} ei={2.4} cast={false} />
      <Box p={[0, H - 0.06, -HALF + 0.18]} s={[ROOM, 0.05, 0.04]} c={color} e={color} ei={2.4} cast={false} />
      <Box p={[-HALF + 0.17, 0.08, 0]} s={[0.03, 0.16, ROOM]} c="#0f172a" cast={false} />
      <Box p={[0, 0.08, -HALF + 0.17]} s={[ROOM, 0.16, 0.03]} c="#0f172a" cast={false} />

      {/* glass partitions on the front edges (door gaps) */}
      <Glass p={[HALF - 0.05, 1.05, -2.6]} s={[0.05, 2.1, 4.6]} color={color} />
      <Glass p={[HALF - 0.05, 1.05, 3.4]} s={[0.05, 2.1, 3.0]} color={color} />
      <Glass p={[-2.6, 1.05, HALF - 0.05]} s={[4.6, 2.1, 0.05]} color={color} />
      <Glass p={[3.4, 1.05, HALF - 0.05]} s={[3.0, 2.1, 0.05]} color={color} />

      {/* wall decor */}
      <Frame p={[-HALF + 0.19, 1.6, 1.2]} rot={Math.PI / 2} color={color} />
      <Frame p={[-HALF + 0.19, 1.6, 2.2]} rot={Math.PI / 2} color="#f8fafc" />
      <mesh position={[-HALF + 0.19, 2.0, 3.6]} rotation={[0, Math.PI / 2, 0]}>
        <circleGeometry args={[0.28, 24]} />
        <meshStandardMaterial color="#f8fafc" />
      </mesh>

      {/* furniture */}
      {id !== 'warroom' && <MeetingTable p={MEET_CENTER} color={color} />}
      {DESK_SLOTS.slice(0, deskCount).map(([x, z], i) => (
        <Desk key={i} p={[x, 0, z]} screen={i % 2 ? color : '#3b82f6'} active={agents[i]?.state === 'working'} dual={id === 'production' || id === 'ceo'} />
      ))}
      <DeptDecor id={id} color={color} />
      <Plant p={[HALF - 0.6, 0, -HALF + 0.6]} />
      <Plant p={[-HALF + 0.6, 0, HALF - 0.6]} scale={0.8} />

      {/* employees */}
      {agents.map((a, i) => {
        const [sx, sz] = DESK_SLOTS[i % DESK_SLOTS.length];
        const ang = (i / Math.max(5, agents.length)) * Math.PI * 2 + 0.3;
        const meet: [number, number, number] = id === 'warroom'
          ? [-2.2 + (i % 4) * 1.4, 0, i < 4 ? -1.4 : 0.6]
          : [MEET_CENTER[0] + Math.cos(ang) * 1.35, 0, MEET_CENTER[2] + Math.sin(ang) * 1.35];
        const [ix, iz] = IDLE[i % IDLE.length];
        return (
          <Employee
            key={a.id}
            agent={a}
            seat={[sx, 0, sz + 0.62]}
            meet={meet}
            meetCenter={id === 'warroom' ? [0, 0, -0.4] : MEET_CENTER}
            idleSpot={[ix, 0, iz]}
            onSelect={onSelectAgent}
          />
        );
      })}

      {/* room light */}
      <pointLight position={[0, 2.6, 0]} intensity={lit ? 9 : 5} distance={9} color={color} decay={1.6} />

      {/* label */}
      <Html position={[-HALF + 1.2, H + 0.7, -HALF + 1.2]} center zIndexRange={[30, 0]} style={{ pointerEvents: 'none' }}>
        <div
          className="select-none whitespace-nowrap rounded-xl border px-3 py-1.5 text-center shadow-2xl transition-transform"
          style={{ borderColor: `${color}88`, background: 'rgba(8,12,30,.82)', boxShadow: `0 0 ${lit ? 26 : 14}px ${color}55`, transform: `scale(${lit ? 1.08 : 1})` }}
        >
          <div className="text-[12px] font-bold tracking-wide text-white">{icon} {name}</div>
          <div className="mt-0.5 flex items-center justify-center gap-2 text-[10px] text-slate-300">
            <span><span className="text-emerald-400">●</span> {working} working</span>
            <span>👥 {agents.length}</span>
            {pending > 0 && <span className="text-amber-300">⏳ {pending}</span>}
          </div>
        </div>
      </Html>
    </group>
  );
}

function Glass({ p, s, color }: { p: [number, number, number]; s: [number, number, number]; color: string }) {
  return (
    <group>
      <mesh position={p}>
        <boxGeometry args={s} />
        <meshPhysicalMaterial color="#9fd8ff" transparent opacity={0.13} roughness={0.05} metalness={0.1} />
      </mesh>
      {/* frame top */}
      <mesh position={[p[0], p[1] + s[1] / 2, p[2]]}>
        <boxGeometry args={[Math.max(s[0], 0.06), 0.05, Math.max(s[2], 0.06)]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} toneMapped={false} />
      </mesh>
      <mesh position={[p[0], 0.02, p[2]]}>
        <boxGeometry args={[Math.max(s[0], 0.08), 0.04, Math.max(s[2], 0.08)]} />
        <meshStandardMaterial color="#cbd5e1" metalness={0.6} roughness={0.3} />
      </mesh>
    </group>
  );
}

function DeptDecor({ id, color }: { id: RoomProps['id']; color: string }) {
  const back = -HALF + 0.2;
  switch (id) {
    case 'research':
      return (<><Bookshelf p={[1.6, 0, back + 0.25]} /><Bookshelf p={[3.1, 0, back + 0.25]} /><WallScreen p={[back + 0.02, 1.6, -0.6]} rot={Math.PI / 2} w={1.8} h={1} color="#1d4ed8" /></>);
    case 'creative':
      return (<><Whiteboard p={[2.2, 0, back + 0.3]} accent={color} /><Sofa p={[3.4, 0, -2.6]} rot={-Math.PI / 2} color="#5b3fa8" /><WallScreen p={[back + 0.02, 1.6, -0.6]} rot={Math.PI / 2} w={1.6} h={0.9} color="#7c3aed" /></>);
    case 'script':
      return (<><Bookshelf p={[1.4, 0, back + 0.25]} /><Whiteboard p={[3.2, 0, back + 0.3]} accent={color} /><Cooler p={[4.3, 0, -2.0]} /></>);
    case 'voice':
      return (<><MicStand p={[1.6, 0, -2.6]} /><MicStand p={[3.2, 0, -2.6]} />{[0, 1, 2, 3].map((i) => <Box key={i} p={[0.9 + i * 0.9, 1.5, back + 0.05]} s={[0.7, 1.4, 0.08]} c="#3b1d3a" />)}<Box p={[2.4, 0.4, -3.6]} s={[2.6, 0.8, 0.6]} c="#1f2937" /></>);
    case 'production':
      return (<><WallScreen p={[2.4, 1.6, back + 0.02]} w={3.4} h={1.3} color="#be123c" /><ServerRack p={[4.2, 0, -3.0]} /><Box p={[2.4, 0.4, -3.4]} s={[3, 0.8, 0.7]} c="#1f2937" /></>);
    case 'thumbnail':
      return (<><Easel p={[1.6, 0, -2.8]} rot={0.3} /><Easel p={[3.3, 0, -2.8]} rot={-0.3} /><WallScreen p={[back + 0.02, 1.6, -0.6]} rot={Math.PI / 2} w={1.6} h={1} color="#d97706" /></>);
    case 'publishing':
      return (<><ServerRack p={[1.4, 0, back + 0.4]} /><ServerRack p={[2.3, 0, back + 0.4]} /><ServerRack p={[3.2, 0, back + 0.4]} /><WallScreen p={[back + 0.02, 1.6, -0.6]} rot={Math.PI / 2} w={1.6} h={1} color="#0e7490" /></>);
    case 'ceo':
      return (<><WallScreen p={[2.3, 1.55, back + 0.02]} w={3.4} h={1.5} color="#a16207" /><Sofa p={[2.3, 0, -2.6]} rot={Math.PI} color="#3a2a52" /><Bookshelf p={[back + 0.25, 0, -0.4]} rot={Math.PI / 2} /></>);
    case 'warroom':
      return (
        <>
          <Box p={[0, 0.72, -0.4]} s={[5.6, 0.08, 1.6]} c="#0f172a" rough={0.2} metal={0.5} />
          <Box p={[0, 0.77, -0.4]} s={[5.2, 0.01, 0.06]} c="#ef4444" e="#ef4444" ei={2.5} cast={false} />
          <Box p={[0, 0.36, -0.4]} s={[4.8, 0.7, 0.4]} c="#1e293b" />
          {[-2.2, -0.8, 0.6, 2.0].map((x) => (<group key={x}><Chair p={[x, 0, -1.6]} rot={Math.PI} /><Chair p={[x, 0, 0.8]} /></group>))}
          <WallScreen p={[0, 1.6, back + 0.02]} w={5} h={1.6} color="#991b1b" />
          <WallScreen p={[back + 0.02, 1.6, 0.4]} rot={Math.PI / 2} w={2.4} h={1.2} color="#b91c1c" />
        </>
      );
  }
}
