import { Suspense, useMemo } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, OrthographicCamera } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { useGame } from '../../store/useGame';
import { DEPARTMENTS, WAR_ROOM } from '../../modules/departments/departments';
import { Room, ROOM } from './Room';
import { Plant } from './Furniture';
import { DM, Mascot, NeonSign, Portal, FloatingMarks } from './DriftmarkDecor';
import { useShallow } from 'zustand/react/shallow';
import { stageById } from '../../modules/workflows/pipeline';

const GAP = 1.2;
const cell = (c: number, r: number): [number, number, number] => [(c - 1) * (ROOM + GAP), 0, (r - 1) * (ROOM + GAP)];

function ResponsiveZoom() {
  const { size, camera } = useThree();
  // op een smal (telefoon)scherm verder inzoomen, anders is het kantoor piepklein
  const z = Math.min(size.width / (size.width < 600 ? 34 : 52), size.height / 46);
  if ((camera as { zoom: number }).zoom !== z) {
    (camera as { zoom: number }).zoom = z;
    camera.updateProjectionMatrix();
  }
  return null;
}

export default function OfficeScene() {
  const { agents, tasks, warCases, selectedDept, selectDept, selectAgent } = useGame(
    useShallow((s) => ({ agents: s.agents, tasks: s.tasks, warCases: s.warCases, selectedDept: s.selectedDept, selectDept: s.selectDept, selectAgent: s.selectAgent })),
  );

  const warAgents = useMemo(() => new Set(warCases.filter((w) => w.status === 'Investigating').flatMap((w) => w.agentIds)), [warCases]);
  const pendingFor = (deptId: string) =>
    tasks.filter((t) => (t.status === 'Pending' || t.status === 'Review') && agents.find((a) => a.id === t.agentId)?.department === deptId).length +
    tasks.filter((t) => t.status === 'Pending' && !t.agentId && t.stage && stageById(t.stage).department === deptId).length;

  const openAgent = (id: string) => { selectAgent(id); };

  return (
    <Canvas shadows dpr={[1, 1.75]} gl={{ antialias: true }} onPointerMissed={() => selectDept(null)}>
      <color attach="background" args={['#070b1a']} />
      <fog attach="fog" args={['#070b1a', 60, 110]} />
      <OrthographicCamera makeDefault position={[30.5, 30, 30.5]} zoom={20} near={-100} far={300} />
      <ResponsiveZoom />
      <OrbitControls
        target={[-3.5, 0, -3.5]}
        enableRotate
        minPolarAngle={0.6}
        maxPolarAngle={1.1}
        minAzimuthAngle={0.25}
        maxAzimuthAngle={1.35}
        minZoom={10}
        maxZoom={70}
        enableDamping
        dampingFactor={0.08}
        screenSpacePanning
      />
      <ambientLight intensity={0.55} color="#9aa8ff" />
      <hemisphereLight args={['#b4c6ff', '#1a1030', 0.5]} />
      <directionalLight
        position={[18, 30, 12]}
        intensity={1.5}
        color="#fff4e6"
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-24}
        shadow-camera-right={24}
        shadow-camera-top={24}
        shadow-camera-bottom={-24}
        shadow-bias={-0.0004}
      />
      {/* Driftmark glans-licht: oranje en blauw randlicht */}
      <pointLight position={[-22, 9, 10]} color={DM.orange} intensity={60} distance={60} decay={1.4} />
      <pointLight position={[10, 9, -22]} color={DM.blue} intensity={60} distance={60} decay={1.4} />
      <Suspense fallback={null}>
        {/* Driftmark-podium achter het kantoor */}
        <mesh position={[-19, -0.45, -19]} receiveShadow>
          <cylinderGeometry args={[5.2, 5.6, 0.5, 48]} />
          <meshStandardMaterial color="#141a3a" roughness={0.4} metalness={0.3} />
        </mesh>
        <mesh position={[-19, -0.18, -19]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[5.25, 0.07, 8, 80]} />
          <meshStandardMaterial color={DM.blue} emissive={DM.blue} emissiveIntensity={2.4} toneMapped={false} />
        </mesh>
        <Mascot p={[-19, -0.2, -19]} rot={Math.PI / 4} s={1.7} />
        <Portal p={[-22.6, 2.6, -15.6]} rot={Math.PI / 4} color={DM.orange} />
        <Portal p={[-15.6, 2.6, -22.6]} rot={Math.PI / 4} color={DM.blue} />
        <NeonSign p={[-21.5, 9.2, -21.5]} rot={Math.PI / 4} width={16} />
        <FloatingMarks center={[-19, 0, -19]} spread={7} />

        {/* base slab */}
        <mesh position={[0, -0.45, 0]} receiveShadow>
          <boxGeometry args={[3 * ROOM + 2 * GAP + 2, 0.5, 3 * ROOM + 2 * GAP + 2]} />
          <meshStandardMaterial color="#2a2f45" roughness={0.9} />
        </mesh>
        <mesh position={[0, -0.72, 0]}>
          <boxGeometry args={[3 * ROOM + 2 * GAP + 2.6, 0.08, 3 * ROOM + 2 * GAP + 2.6]} />
          <meshStandardMaterial color={DM.orange} emissive={DM.orange} emissiveIntensity={1.6} toneMapped={false} />
        </mesh>
        {/* corridor plants */}
        {[-1, 1].map((x) => [-1, 1].map((z) => <Plant key={`${x}${z}`} p={[x * (ROOM / 2 + GAP / 2), 0, z * (ROOM / 2 + GAP / 2)]} scale={0.6} />))}

        {DEPARTMENTS.map((d) => (
          <Room
            key={d.id}
            id={d.id}
            name={d.short}
            icon={d.icon}
            color={d.color}
            wall={d.wall}
            floor={d.floor}
            position={cell(d.grid[0], d.grid[1])}
            agents={agents.filter((a) => a.department === d.id && !warAgents.has(a.id))}
            pending={pendingFor(d.id)}
            selected={selectedDept === d.id}
            onSelect={() => selectDept(d.id)}
            onSelectAgent={openAgent}
          />
        ))}
        <Room
          id="warroom"
          name={WAR_ROOM.name}
          icon="🛡️"
          color={WAR_ROOM.color}
          wall={WAR_ROOM.wall}
          floor={WAR_ROOM.floor}
          position={cell(WAR_ROOM.grid[0], WAR_ROOM.grid[1])}
          agents={agents.filter((a) => warAgents.has(a.id))}
          pending={warCases.filter((w) => w.status === 'Ready').length}
          selected={selectedDept === 'warroom'}
          onSelect={() => selectDept('warroom')}
          onSelectAgent={openAgent}
        />
      </Suspense>
      <EffectComposer multisampling={4}>
        <Bloom intensity={0.9} luminanceThreshold={0.75} luminanceSmoothing={0.2} mipmapBlur />
        <Vignette eskil={false} offset={0.25} darkness={0.55} />
      </EffectComposer>
    </Canvas>
  );
}
