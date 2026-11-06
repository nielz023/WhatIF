/**
 * DE LOPENDE BAND (verbeterpunt 2): een zwevende lichtbaan boven de gang rond de receptie.
 * Elke video in productie is een pakketje dat bij de afdeling hangt die er nu aan werkt
 * (Idee → Onderzoek, Script → Script, Stemmen → Stem, Cast t/m Montage → Productie, enz.).
 * Schuift een video een stap door, dan glijdt het pakketje over de band naar de volgende
 * afdeling (met een ping). Kleine lichtdeeltjes stromen de hele tijd mee in de richting van de band.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Billboard, Html } from '@react-three/drei';
import * as THREE from 'three';
import { STEPS, type RealVideo } from '../data/driftmark';
import { ROOMS, SPAN, type RoomId } from './rooms';
import { play } from './sound';
import type { Handoff } from './crew';

export const STEP_ROOM: Record<string, RoomId> = {
  Idee: 'onderzoek', Verloop: 'creatief', Script: 'script', Stemmen: 'stem', Cast: 'productie', Sets: 'productie',
  Animatie: 'productie', Render: 'productie', Montage: 'productie', 'Upload-tekst': 'publicatie', Shorts: 'publicatie', Online: 'ceo',
};
export function currentStep(v: RealVideo): number {
  const a = v.steps.findIndex((s) => s.active); if (a >= 0) return a;
  const nd = v.steps.findIndex((s) => !s.done); return nd < 0 ? v.steps.length - 1 : nd;
}
export const isLive = (v: RealVideo) => v.status === 'Online' || v.steps.every((s) => s.done);
export const roomOfStep = (label: string): RoomId => STEP_ROOM[label] ?? 'productie';
/** wie brengt er een map naar wie: van de vorige afdeling naar de afdeling die nu aan de video werkt */
export function handoffsFor(videos: RealVideo[]): Handoff[] {
  const out: Handoff[] = [];
  for (const v of videos.filter((x) => !isLive(x))) {
    const i = currentStep(v); const to = roomOfStep(v.steps[i]?.label ?? '');
    for (let j = i - 1; j >= 0; j--) { const from = roomOfStep(v.steps[j].label); if (from !== to) { out.push({ from, to, label: `video ${v.nr}` }); break; } }
  }
  // en de vaste route door het kantoor, zodat er altijd iets gebeurt
  const base: [RoomId, RoomId][] = [['onderzoek', 'creatief'], ['creatief', 'script'], ['script', 'stem'], ['productie', 'thumbnail'], ['thumbnail', 'publicatie'], ['publicatie', 'ceo']];
  return [...out, ...out, ...base.map(([from, to]) => ({ from, to, label: 'overleg' }))];
}

/* ---------- baan ---------- */
const RT = 6.55, YT = 2.95;
const slotOf = (id: RoomId) => ROOMS.find((r) => r.id === id)?.slot ?? 1;
/** hoek op de baan; afdelingen 1-5 krijgen er een rondje bij zodat de band altijd "vooruit" draait */
const bandAngle = (id: RoomId) => { const s = slotOf(id); return s * SPAN + (s <= 5 ? Math.PI * 2 : 0); };
const onBand = (a: number, y = YT): [number, number, number] => [Math.sin(a) * RT, y, Math.cos(a) * RT];
const VCOL = ['#FF7A24', '#A855F7', '#20D9FF', '#21D6A0', '#FF4DB8', '#FACC15'];

function labelTex(text: string, col: string) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d')!;
  g.fillStyle = 'rgba(8,12,30,0.88)'; g.beginPath(); g.roundRect(6, 14, 500, 100, 46); g.fill();
  g.lineWidth = 6; g.strokeStyle = col; g.shadowColor = col; g.shadowBlur = 16; g.stroke(); g.shadowBlur = 0;
  g.fillStyle = '#fff'; g.font = '800 54px Inter, Arial, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, 256, 66);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

function Package({ v, idx, onPick }: { v: RealVideo; idx: number; onPick: (room: RoomId) => void }) {
  const step = currentStep(v); const label = v.steps[step]?.label ?? '';
  const room = roomOfStep(label); const col = VCOL[(v.nr - 1) % VCOL.length];
  const target = bandAngle(room) + (idx % 2 ? 0.07 : -0.07);
  const g = useRef<THREE.Group>(null); const box = useRef<THREE.Mesh>(null);
  const tex = useMemo(() => labelTex(`V${v.nr} · ${label}`, col), [v.nr, label, col]);
  const [hover, setHover] = useState(false);
  // vorige stand onthouden: is de video doorgeschoven, dan glijdt het pakketje er naartoe
  const anim = useRef<{ from: number; t: number } | null>(null);
  const cur = useRef(target);
  useEffect(() => {
    let seen: Record<string, string> = {};
    try { seen = JSON.parse(localStorage.getItem('dm-band') ?? '{}'); } catch { /* */ }
    const prev = seen[v.nr];
    if (prev && prev !== label) {
      const pi = STEPS.indexOf(prev); const pr = pi >= 0 ? roomOfStep(prev) : room;
      if (pr !== room && STEPS.indexOf(label) > pi) { anim.current = { from: bandAngle(pr), t: 0 }; cur.current = bandAngle(pr); setTimeout(() => play('success'), 3200); }
    }
    seen[v.nr] = label; try { localStorage.setItem('dm-band', JSON.stringify(seen)); } catch { /* */ }
  }, [v.nr, label, room]);
  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime;
    const a = anim.current;
    if (a) { a.t = Math.min(1, a.t + dt / 3.6); const k = a.t < 0.5 ? 4 * a.t ** 3 : 1 - (-2 * a.t + 2) ** 3 / 2; cur.current = a.from + (target - a.from) * k; if (a.t >= 1) anim.current = null; }
    else cur.current += (target - cur.current) * Math.min(1, dt * 2);
    if (g.current) g.current.position.set(...onBand(cur.current, YT + 0.32 + Math.sin(t * 1.6 + idx) * 0.06));
    if (box.current) { box.current.rotation.y = t * 0.6 + idx; box.current.rotation.x = Math.sin(t * 0.8 + idx) * 0.15; }
  });
  return (
    <group ref={g}>
      <mesh ref={box} onClick={(e) => { e.stopPropagation(); onPick(room); }}
        onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; }} onPointerOut={() => { setHover(false); document.body.style.cursor = 'auto'; }}>
        <boxGeometry args={[0.44, 0.44, 0.44]} />
        <meshPhysicalMaterial color={col} emissive={col} emissiveIntensity={hover ? 1.6 : 0.8} roughness={0.25} clearcoat={1} toneMapped={false} />
      </mesh>
      <Billboard position={[0, 0.55, 0]}><mesh><planeGeometry args={[1.5, 0.375]} /><meshBasicMaterial map={tex} transparent depthWrite={false} toneMapped={false} /></mesh></Billboard>
      {hover && (
        <Html position={[0, 1.05, 0]} center zIndexRange={[30, 20]} style={{ pointerEvents: 'none' }}>
          <div className="w-[230px] rounded-lg border border-white/15 bg-[#0a1124]/95 px-3 py-2 text-[12px] text-slate-200 shadow-xl backdrop-blur">
            <div className="font-semibold text-white">Video {v.nr}: {v.werktitel}</div>
            <div className="mt-0.5">Nu: <b style={{ color: col }}>{label}</b> · stap {step + 1} van {v.steps.length}</div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full" style={{ width: `${(v.steps.filter((s) => s.done).length / v.steps.length) * 100}%`, background: col }} /></div>
          </div>
        </Html>
      )}
    </group>
  );
}

export function Pipeline({ videos, onPick }: { videos: RealVideo[]; onPick: (room: RoomId) => void }) {
  const active = videos.filter((v) => !isLive(v));
  // baan met lopende streepjes (in de richting van de band)
  const mat = useMemo(() => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, toneMapped: false,
    uniforms: { t: { value: 0 }, c: { value: new THREE.Color('#20D9FF') } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform float t; uniform vec3 c; varying vec2 vUv;
      void main(){ float a = vUv.x; float f = fract(a * 90.0 + t * 1.4); float dash = smoothstep(0.35, 0.5, f) * (1.0 - smoothstep(0.5, 0.65, f));
        float front = smoothstep(0.015, 0.07, abs(a - 0.5)); // voorkant (boven de trap) zachter
        gl_FragColor = vec4(c * (0.55 + dash * 1.6), (0.35 + dash * 0.6) * (0.35 + 0.65 * front)); }`,
  }), []);
  const geo = useMemo(() => { const g = new THREE.TorusGeometry(RT, 0.035, 6, 220); g.rotateX(Math.PI / 2); g.rotateY(Math.PI / 2); return g; }, []);
  // stroom van lichtdeeltjes
  const NP = 36; const dots = useRef<THREE.InstancedMesh>(null);
  const seeds = useMemo(() => Array.from({ length: NP }, (_, i) => ({ a: (i / NP) * Math.PI * 2, s: 0.18 + Math.random() * 0.12, y: (Math.random() - 0.5) * 0.08 })), []);
  const m4 = useMemo(() => new THREE.Matrix4(), []);
  useFrame(({ clock }, dt) => {
    mat.uniforms.t.value = clock.elapsedTime;
    const d = dots.current; if (!d) return;
    seeds.forEach((s, i) => { s.a += dt * s.s; const p = onBand(s.a, YT + s.y); m4.makeTranslation(p[0], p[1], p[2]); d.setMatrixAt(i, m4); });
    d.instanceMatrix.needsUpdate = true;
  });
  return (
    <group>
      <mesh geometry={geo} material={mat} raycast={() => null} />
      {/* stations bij elke afdeling */}
      {ROOMS.filter((r) => r.slot > 0).map((r) => (
        <mesh key={r.id} position={onBand(r.slot * SPAN)} rotation={[Math.PI / 2, 0, 0]} raycast={() => null}>
          <torusGeometry args={[0.16, 0.025, 6, 20]} />
          <meshBasicMaterial color={r.color} toneMapped={false} />
        </mesh>
      ))}
      <instancedMesh ref={dots} args={[undefined, undefined, NP]} frustumCulled={false} raycast={() => null}>
        <sphereGeometry args={[0.045, 6, 6]} />
        <meshBasicMaterial color="#b8f6ff" toneMapped={false} />
      </instancedMesh>
      {active.map((v, i) => <Package key={v.nr} v={v} idx={i} onPick={onPick} />)}
    </group>
  );
}
