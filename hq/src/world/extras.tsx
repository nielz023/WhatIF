/**
 * Sfeer rond het kantoor (verbeterpunten "mooier" en "animatie"):
 * lucht met dag en nacht (volgt de klok of het thema), sterren, maan of zon, wolken onder het kantoor,
 * een vliegtuigje en een drone, lichtbundels in de hal, confetti bij mijlpalen, een zwaailicht bij de
 * crisiskamer als er iets misgaat, sneeuw in december en een discobal bij het feestthema.
 */
import { useEffect, useMemo, useRef, useState, type RefObject } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useWorld, dayPhase, dayAmount, reducedMotion, type Theme } from './useWorld';
import { ROOMS, slotAngle, R_IN, R_OUT } from './rooms';
import type { Alarm } from './alarms';
import { play } from './sound';
import { loadNav, nearestFree } from './nav';

const smooth = (a: number, b: number, x: number) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
/** schemering: 0..1 rond zonsopkomst en zonsondergang */
function duskAmount(ph: number) {
  const h = ph * 24;
  return Math.max(smooth(6.6, 7.9, h) * (1 - smooth(8.4, 9.6, h)), smooth(15.8, 17.0, h) * (1 - smooth(17.6, 18.8, h)));
}

/** gedeelde stand van de lucht, één keer per frame bijgewerkt door <Sky/> */
export const sky = { day: 0, dusk: 0, feest: false, t: 0, sun: new THREE.Vector3(0.3, -0.3, -0.9).normalize() };
const MOON = new THREE.Vector3(0.45, 0.2, -0.87).normalize(); // achter het kantoor, rechts boven de skyline (zichtbaar als je laag kantelt)
const H0 = -0.12; // horizon van de lucht iets onder ooghoogte: het kantoor staat boven de stad

function canvasTex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

/* ---------------- lucht, sterren, maan, licht ---------------- */
export function Sky({ baked }: { baked: boolean }) {
  const theme = useWorld((s) => s.theme);
  const scene = useThree((s) => s.scene);
  const dome = useMemo(() => new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      uDay: { value: 0 }, uDusk: { value: 0 }, uSun: { value: sky.sun.clone() }, uHaze: { value: new THREE.Color('#0a0f2a') },
      uNT: { value: new THREE.Color('#02051a') }, uNH: { value: new THREE.Color('#0c1640') }, uGlow: { value: new THREE.Color('#33288a') },
      uDT: { value: new THREE.Color('#3f78c8') }, uDH: { value: new THREE.Color('#a9c6e6') }, uKH: { value: new THREE.Color('#ff8a4c') }, uKT: { value: new THREE.Color('#3b2a66') },
      uSunC: { value: new THREE.Color('#fff3dc') }, uSunG: { value: new THREE.Color('#ffb070') },
    },
    vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `
      uniform float uDay; uniform float uDusk; uniform vec3 uSun; uniform vec3 uHaze;
      uniform vec3 uNT; uniform vec3 uNH; uniform vec3 uGlow; uniform vec3 uDT; uniform vec3 uDH; uniform vec3 uKH; uniform vec3 uKT; uniform vec3 uSunC; uniform vec3 uSunG;
      varying vec3 vDir;
      void main(){
        vec3 d = normalize(vDir);
        float above = d.y + ${(-H0).toFixed(2)};
        float h = clamp(above / ${(1 - H0).toFixed(2)}, 0.0, 1.0);
        vec3 col = mix(mix(uNH, uNT, smoothstep(0.0, 0.75, h)), mix(uDH, uDT, smoothstep(0.0, 0.8, h)), uDay);
        col = mix(col, mix(uKH, uKT, smoothstep(0.0, 0.6, h)), uDusk * 0.8);
        float s = max(dot(d, normalize(uSun)), 0.0);
        col += uSunC * smoothstep(0.9993, 0.9997, s) * 3.0 * max(uDay, uDusk);
        col += uSunG * pow(s, 12.0) * 0.5 * max(uDay * 0.6, uDusk);
        col += uGlow * (1.0 - uDay) * pow(1.0 - h, 7.0) * 0.4; // blauwpaarse gloed van de stad
        col = mix(uHaze, col, smoothstep(-0.02, 0.12, above));
        gl_FragColor = vec4(col, 1.0);
      }`,
  }), []);

  // sterren: vaste richtingen, twinkelen, vervagen overdag
  const stars = useMemo(() => {
    const N = 900; const pos = new Float32Array(N * 3); const aux = new Float32Array(N * 2);
    for (let i = 0; i < N; i++) {
      const y = Math.min(0.995, H0 + 0.06 + Math.pow(Math.random(), 1.7) * (0.93 - H0)); const a = Math.random() * Math.PI * 2; const r = Math.sqrt(1 - y * y);
      pos.set([Math.sin(a) * r * 255, y * 255, Math.cos(a) * r * 255], i * 3);
      aux.set([1.7 + Math.pow(Math.random(), 3) * 3.2, Math.random() * 6.28], i * 2);
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aux', new THREE.BufferAttribute(aux, 2));
    const m = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, fog: false, blending: THREE.AdditiveBlending,
      uniforms: { uTime: { value: 0 }, uNight: { value: 1 }, uPx: { value: 1 } },
      vertexShader: `attribute vec2 aux; uniform float uTime; uniform float uPx; varying float vA;
        void main(){ vA = 0.55 + 0.45 * sin(uTime * (1.2 + aux.y * 0.3) + aux.y * 7.0); gl_PointSize = aux.x * uPx * (0.8 + 0.4 * vA); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `uniform float uNight; varying float vA; void main(){ vec2 p = gl_PointCoord - 0.5; float a = smoothstep(0.5, 0.0, length(p)); gl_FragColor = vec4(vec3(0.85, 0.9, 1.0) * a * vA * uNight, a * vA * uNight); }`,
    });
    return { g, m };
  }, []);

  const moonTex = useMemo(() => canvasTex(256, 256, (g) => {
    const glow = g.createRadialGradient(128, 128, 30, 128, 128, 128); glow.addColorStop(0, 'rgba(200,215,255,0.55)'); glow.addColorStop(1, 'rgba(120,140,255,0)');
    g.fillStyle = glow; g.fillRect(0, 0, 256, 256);
    const d = g.createRadialGradient(112, 112, 6, 128, 128, 44); d.addColorStop(0, '#fffdf2'); d.addColorStop(1, '#d9dcef');
    g.fillStyle = d; g.beginPath(); g.arc(128, 128, 42, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(150,160,190,0.35)';
    for (const [x, y, r] of [[114, 118, 9], [140, 136, 7], [128, 104, 5], [146, 116, 4], [116, 144, 6]]) { g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); }
  }), []);
  const moon = useRef<THREE.Sprite>(null);

  const fogNight = useMemo(() => new THREE.Color('#0a0f2a'), []);
  const fogDay = useMemo(() => new THREE.Color('#86a3c9'), []);
  const fogDusk = useMemo(() => new THREE.Color('#b47a6e'), []);
  const tick = useRef(0);
  const dpr = useThree((s) => s.viewport.dpr);

  useFrame(({ clock }, dt) => {
    sky.t = clock.elapsedTime;
    tick.current -= dt;
    if (tick.current <= 0) {
      tick.current = 1;
      const ph = dayPhase(theme as Theme);
      sky.day = dayAmount(ph); sky.dusk = theme === 'auto' ? duskAmount(ph) : 0; sky.feest = theme === 'feest';
      // zon: komt op in het oosten, gaat onder in het westen, laag boven de stad (november)
      const k = Math.max(0, Math.min(1, (ph * 24 - 7.5) / 10));
      const az = -1.15 + k * 2.3; const el = -0.16 + Math.sin(k * Math.PI) * 0.4; // overdag boven de nevel, zodat je de zon ziet
      sky.sun.set(Math.sin(az) * Math.sqrt(1 - el * el), el, -Math.cos(az) * Math.sqrt(1 - el * el)).normalize();
    }
    const u = dome.uniforms;
    u.uDay.value += (sky.day - u.uDay.value) * Math.min(1, dt * 2);
    u.uDusk.value += (sky.dusk - u.uDusk.value) * Math.min(1, dt * 2);
    (u.uSun.value as THREE.Vector3).copy(sky.sun);
    const fog = scene.fog as THREE.Fog | null;
    if (fog) { fog.color.copy(fogNight).lerp(fogDay, u.uDay.value).lerp(fogDusk, u.uDusk.value * 0.6); (u.uHaze.value as THREE.Color).copy(fog.color); }
    stars.m.uniforms.uTime.value = clock.elapsedTime;
    stars.m.uniforms.uNight.value = Math.max(0, 1 - u.uDay.value * 1.4 - u.uDusk.value * 0.5);
    stars.m.uniforms.uPx.value = dpr;
    if (moon.current) (moon.current.material as THREE.SpriteMaterial).opacity = Math.max(0, 1 - u.uDay.value * 1.2);
  });

  return (
    <group>
      <mesh material={dome} renderOrder={-10} frustumCulled={false} raycast={() => null}><sphereGeometry args={[280, 48, 24]} /></mesh>
      <points geometry={stars.g} material={stars.m} renderOrder={-9} frustumCulled={false} raycast={() => null} />
      <sprite ref={moon} position={MOON.clone().multiplyScalar(235).toArray()} scale={[27, 27, 1]} renderOrder={-8} raycast={() => null}>
        <spriteMaterial map={moonTex} transparent depthWrite={false} fog={false} toneMapped={false} />
      </sprite>
      <DayLights baked={baked} />
      <Clouds />
    </group>
  );
}

/** licht in het kantoor: 's nachts koel en neon, overdag helderder en warmer */
function DayLights({ baked }: { baked: boolean }) {
  const amb = useRef<THREE.AmbientLight>(null); const hemi = useRef<THREE.HemisphereLight>(null); const dir = useRef<THREE.DirectionalLight>(null);
  const c = useMemo(() => ({ ambN: new THREE.Color('#8fa0ff'), ambD: new THREE.Color('#e4ecff'), dirN: new THREE.Color('#fff1e0'), dirD: new THREE.Color('#fff6ea'), dirDusk: new THREE.Color('#ffb27a') }), []);
  useFrame(() => {
    const d = sky.day, k = sky.dusk;
    if (amb.current) { amb.current.intensity = 0.35 + d * 0.25; amb.current.color.copy(c.ambN).lerp(c.ambD, d); }
    if (hemi.current) hemi.current.intensity = 0.5 + d * 0.35;
    if (dir.current) { dir.current.intensity = 1.1 + d * 0.5; dir.current.color.copy(c.dirN).lerp(c.dirD, d).lerp(c.dirDusk, k * 0.7); }
  });
  return (<>
    <ambientLight ref={amb} intensity={0.35} color="#8fa0ff" />
    <hemisphereLight ref={hemi} args={['#b9c7ff', '#1a0f2e', 0.5]} />
    <directionalLight ref={dir} position={[16, 40, 22]} intensity={1.1} color="#fff1e0" castShadow={!baked} shadow-mapSize={[2048, 2048]}
      shadow-camera-left={-20} shadow-camera-right={20} shadow-camera-top={20} shadow-camera-bottom={-20} shadow-bias={-0.0004} />
  </>);
}

/* ---------------- wolken onder het kantoor ---------------- */
function Clouds() {
  const tex = useMemo(() => canvasTex(256, 128, (g) => {
    for (let i = 0; i < 9; i++) {
      const x = 50 + Math.random() * 156, y = 58 + Math.random() * 30, r = 22 + Math.random() * 30;
      const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.fillRect(0, 0, 256, 128);
    }
  }), []);
  const list = useMemo(() => Array.from({ length: 16 }, (_, i) => {
    const a = (i / 16) * Math.PI * 2 + Math.random() * 0.3; const r = 27 + Math.random() * 42; const w = 16 + Math.random() * 20;
    return { p: [Math.sin(a) * r, -13 - Math.random() * 12, Math.cos(a) * r] as [number, number, number], w };
  }), []);
  const mats = useMemo(() => list.map(() => new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 0.36, color: '#5a63b8' })), [list, tex]);
  const grp = useRef<THREE.Group>(null);
  const night = useMemo(() => new THREE.Color('#5a63b8'), []); const day = useMemo(() => new THREE.Color('#ffffff'), []); const dusk = useMemo(() => new THREE.Color('#ffb48a'), []);
  useFrame((_, dt) => {
    if (grp.current && !reducedMotion()) grp.current.rotation.y += dt * 0.006;
    for (const m of mats) { m.color.copy(night).lerp(day, sky.day).lerp(dusk, sky.dusk * 0.5); m.opacity = 0.36 + sky.day * 0.32; }
  });
  return (
    <group ref={grp}>
      {list.map((c, i) => <sprite key={i} position={c.p} scale={[c.w, c.w * 0.45, 1]} material={mats[i]} raycast={() => null} />)}
      <Plane />
    </group>
  );
}

/* ---------------- vliegtuigje en drone ---------------- */
const blink = (t: number, period: number, on: number, off = 0) => ((t + off) % period) < on;
function NavLight({ color, refEl, pos, size = 0.12 }: { color: string; refEl: RefObject<THREE.Mesh>; pos: [number, number, number]; size?: number }) {
  return <mesh ref={refEl} position={pos}><sphereGeometry args={[size, 8, 6]} /><meshBasicMaterial color={color} toneMapped={false} /></mesh>;
}
function Plane() {
  const g = useRef<THREE.Group>(null); const red = useRef<THREE.Mesh>(null); const green = useRef<THREE.Mesh>(null); const strobe = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime; const a = t * 0.07 + 2.2; const r = 52;
    if (g.current) {
      g.current.position.set(Math.sin(a) * r, -5 + Math.sin(t * 0.2) * 1.5, Math.cos(a) * r);
      g.current.rotation.set(0, Math.atan2(Math.cos(a), -Math.sin(a)), -0.12);
    }
    if (strobe.current) strobe.current.visible = blink(t, 1.4, 0.08);
    const n = Math.max(0.35, sky.day < 0.5 ? 1 : 0.5);
    if (red.current) red.current.scale.setScalar(n); if (green.current) green.current.scale.setScalar(n);
  });
  return (
    <group ref={g} scale={1.7}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.2, 0.15, 3.2, 10]} /><meshStandardMaterial color="#dfe6f2" roughness={0.4} metalness={0.3} /></mesh>
      <mesh position={[0, 0, 0.2]}><boxGeometry args={[3.6, 0.06, 0.6]} /><meshStandardMaterial color="#c8d0de" roughness={0.5} /></mesh>
      <mesh position={[0, 0, -1.45]}><boxGeometry args={[1.2, 0.05, 0.35]} /><meshStandardMaterial color="#c8d0de" roughness={0.5} /></mesh>
      <mesh position={[0, 0.32, -1.4]}><boxGeometry args={[0.06, 0.6, 0.45]} /><meshStandardMaterial color="#FF7A24" roughness={0.5} /></mesh>
      <NavLight color="#ff2a2a" refEl={red} pos={[-1.8, 0, 0.2]} />
      <NavLight color="#2aff6a" refEl={green} pos={[1.8, 0, 0.2]} />
      <NavLight color="#ffffff" refEl={strobe} pos={[0, 0.65, -1.6]} size={0.16} />
    </group>
  );
}

export function Drone() {
  const g = useRef<THREE.Group>(null); const led = useRef<THREE.Mesh>(null);
  const rotors = useRef<(THREE.Mesh | null)[]>([]);
  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime; const a = -t * 0.14; const r = 20.5;
    if (g.current) {
      g.current.position.set(Math.sin(a) * r, 6.4 + Math.sin(t * 0.9) * 0.35, Math.cos(a) * r);
      g.current.rotation.set(Math.sin(t * 0.7) * 0.06, Math.atan2(-Math.cos(a), Math.sin(a)), 0.1);
    }
    for (const m of rotors.current) if (m) m.rotation.y += dt * 40;
    if (led.current) led.current.visible = blink(t, 1.0, 0.5);
  });
  return (
    <group ref={g} scale={2.1}>
      <mesh><boxGeometry args={[0.5, 0.14, 0.5]} /><meshStandardMaterial color="#1b2030" roughness={0.35} metalness={0.5} /></mesh>
      <mesh position={[0, -0.12, 0.12]}><sphereGeometry args={[0.08, 10, 8]} /><meshStandardMaterial color="#0a0a10" roughness={0.1} metalness={0.8} /></mesh>
      {[[1, 1], [1, -1], [-1, 1], [-1, -1]].map(([x, z], i) => (
        <group key={i} position={[x * 0.42, 0.05, z * 0.42]}>
          <mesh rotation={[0, Math.atan2(x, z), 0]} position={[-x * 0.2, 0, -z * 0.2]}><boxGeometry args={[0.05, 0.04, 0.55]} /><meshStandardMaterial color="#2a3042" /></mesh>
          <mesh ref={(el) => { rotors.current[i] = el; }} position={[0, 0.06, 0]}><boxGeometry args={[0.5, 0.01, 0.06]} /><meshBasicMaterial color="#9aa4bc" transparent opacity={0.55} /></mesh>
        </group>
      ))}
      <NavLight color="#FF7A24" refEl={led} pos={[0, -0.09, -0.24]} size={0.05} />
    </group>
  );
}

/* ---------------- lichtbundels in de hal ---------------- */
export function GodRays() {
  const mat = useMemo(() => new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false,
    uniforms: { uStrength: { value: 0.1 }, uColor: { value: new THREE.Color('#ffe7c4') }, uTime: { value: 0 } },
    vertexShader: `varying vec2 vUv; varying float vF; void main(){ vUv = uv; vec3 n = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vF = abs(dot(n, normalize(-mv.xyz))); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float uStrength; uniform vec3 uColor; uniform float uTime; varying vec2 vUv; varying float vF;
      void main(){ float s = 0.7 + 0.3 * sin(vUv.x * 37.0 + uTime * 0.35) * sin(vUv.x * 13.0 - uTime * 0.22);
        float a = uStrength * pow(vF, 2.0) * smoothstep(0.0, 0.3, vUv.y) * (1.0 - smoothstep(0.75, 1.0, vUv.y)) * s; gl_FragColor = vec4(uColor * a, a); }`,
  }), []);
  const g = useRef<THREE.Group>(null);
  const night = useMemo(() => new THREE.Color('#7fa8ff'), []); const day = useMemo(() => new THREE.Color('#ffe7c4'), []);
  useFrame(({ clock }) => {
    mat.uniforms.uTime.value = clock.elapsedTime;
    mat.uniforms.uStrength.value = sky.feest ? 0.04 : 0.05 + sky.day * 0.09 + sky.dusk * 0.04;
    (mat.uniforms.uColor.value as THREE.Color).copy(night).lerp(day, Math.max(sky.day, sky.dusk));
    if (g.current) { const s = sky.sun; g.current.rotation.set(Math.atan2(s.z, 3) * 0.5, 0, -Math.atan2(s.x, 3) * 0.5); }
  });
  return (
    <group ref={g} position={[0, 0, 0]}>
      {[[0, 0, 0], [1.6, 0, -0.9], [-1.4, 0, 1.1]].map(([x, , z], i) => (
        <mesh key={i} material={mat} position={[x, 9, z]} raycast={() => null} renderOrder={3}><cylinderGeometry args={[0.5 + i * 0.15, 2.2 + i * 0.4, 18, 24, 1, true]} /></mesh>
      ))}
    </group>
  );
}

/* ---------------- confetti bij een mijlpaal ---------------- */
const CONF_N = 320;
const CONF_COLORS = ['#FF7A24', '#FACC15', '#22D3EE', '#A855F7', '#4ADE80', '#FF4DB8', '#ffffff', '#398CFF'];
export function Confetti() {
  const party = useWorld((s) => s.party);
  const ref = useRef<THREE.InstancedMesh>(null);
  const st = useMemo(() => ({ p: new Float32Array(CONF_N * 3), v: new Float32Array(CONF_N * 3), r: new Float32Array(CONF_N * 3), w: new Float32Array(CONF_N * 3), born: -99, auto: 0 }), []);
  const o = useMemo(() => new THREE.Object3D(), []);
  const burst = (now: number) => {
    st.born = now;
    for (let i = 0; i < CONF_N; i++) {
      const a = Math.random() * Math.PI * 2, sp = 2 + Math.random() * 6;
      st.p.set([Math.cos(a) * Math.random() * 1.5, 9 + Math.random() * 2, Math.sin(a) * Math.random() * 1.5], i * 3);
      st.v.set([Math.cos(a) * sp, 3 + Math.random() * 7, Math.sin(a) * sp], i * 3);
      st.r.set([Math.random() * 6, Math.random() * 6, Math.random() * 6], i * 3);
      st.w.set([(Math.random() - 0.5) * 12, (Math.random() - 0.5) * 12, (Math.random() - 0.5) * 12], i * 3);
    }
  };
  useEffect(() => {
    const m = ref.current; if (!m) return;
    const c = new THREE.Color();
    for (let i = 0; i < CONF_N; i++) m.setColorAt(i, c.set(CONF_COLORS[i % CONF_COLORS.length]));
    if (m.instanceColor) m.instanceColor.needsUpdate = true;
    m.count = 0;
  }, []);
  useEffect(() => { if (party && !reducedMotion()) burst(performance.now() / 1000); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [party]);
  useFrame((_, dtRaw) => {
    const m = ref.current; if (!m) return;
    const now = performance.now() / 1000; const dt = Math.min(dtRaw, 0.05);
    // feestthema: af en toe een kleine regen confetti
    if (sky.feest && !reducedMotion() && now - st.born > 7) { st.auto -= dt; if (st.auto <= 0) { st.auto = 18; burst(now); } }
    const age = now - st.born;
    if (age > 7) { if (m.count) m.count = 0; return; }
    m.count = CONF_N;
    for (let i = 0; i < CONF_N; i++) {
      const j = i * 3;
      st.v[j + 1] -= 9.8 * 0.32 * dt; st.v[j] *= 1 - dt * 0.9; st.v[j + 2] *= 1 - dt * 0.9; if (st.v[j + 1] < -2.2) st.v[j + 1] = -2.2;
      st.p[j] += st.v[j] * dt; st.p[j + 1] += st.v[j + 1] * dt; st.p[j + 2] += st.v[j + 2] * dt;
      if (st.p[j + 1] < 0.05) { st.p[j + 1] = 0.05; st.v[j] = st.v[j + 1] = st.v[j + 2] = 0; st.w[j] *= 0.9; st.w[j + 1] *= 0.9; st.w[j + 2] *= 0.9; }
      st.r[j] += st.w[j] * dt; st.r[j + 1] += st.w[j + 1] * dt; st.r[j + 2] += st.w[j + 2] * dt;
      o.position.set(st.p[j], st.p[j + 1], st.p[j + 2]); o.rotation.set(st.r[j], st.r[j + 1], st.r[j + 2]);
      o.scale.setScalar(age > 6 ? Math.max(0.001, 7 - age) : 1); o.updateMatrix(); m.setMatrixAt(i, o.matrix);
    }
    m.instanceMatrix.needsUpdate = true;
  });
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, CONF_N]} frustumCulled={false} raycast={() => null}>
      <planeGeometry args={[0.16, 0.26]} />
      <meshBasicMaterial side={THREE.DoubleSide} toneMapped={false} />
    </instancedMesh>
  );
}

/* ---------------- zwaailicht bij de crisiskamer ---------------- */
const HEARD = 'dm-alarm-gehoord';
const heardHere = new Set<string>(); // sirenes die in deze sessie al klonken
export function Beacon({ alarms }: { alarms: Alarm[] }) {
  const level = alarms.some((a) => a.level === 'rood') ? 'rood' : alarms.some((a) => a.level === 'oranje') ? 'oranje' : null;
  const room = ROOMS.find((r) => r.id === 'crisis');
  const pos = useMemo<[number, number, number]>(() => {
    if (!room) return [0, 0, 0]; const rad = (R_IN + R_OUT) / 2 + 1.2, a = slotAngle(room.slot);
    return [Math.sin(a) * rad, 4.4, Math.cos(a) * rad];
  }, [room]);
  // sirene één keer per nieuw rood alarm (niet bij elke keer openen)
  // (pas als "gehoord" opslaan als de sirene echt speelt; het effect hangt aan de rode sleutels, niet aan elke nieuwe lijst)
  const roodKeys = alarms.filter((a) => a.level === 'rood').map((a) => a.key).join('|');
  useEffect(() => {
    if (!roodKeys) return;
    let heard: string[] = []; try { heard = JSON.parse(localStorage.getItem(HEARD) ?? '[]'); } catch { /* */ }
    const fresh = roodKeys.split('|').filter((k) => !heard.includes(k) && !heardHere.has(k)); if (!fresh.length) return;
    const t = setTimeout(() => {
      fresh.forEach((k) => heardHere.add(k)); // ook als localStorage geblokkeerd is: niet bij elke verversing opnieuw
      play('alarm');
      try { localStorage.setItem(HEARD, JSON.stringify([...heard, ...fresh].slice(-60))); } catch { /* */ }
    }, 1800);
    return () => clearTimeout(t);
  }, [roodKeys]);
  const spin = useRef<THREE.Group>(null); const dome = useRef<THREE.MeshBasicMaterial>(null); const light = useRef<THREE.PointLight>(null);
  const beamTex = useMemo(() => canvasTex(256, 32, (g) => {
    const gr = g.createLinearGradient(0, 0, 256, 0); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 32);
    const v = g.createLinearGradient(0, 0, 0, 32); v.addColorStop(0, 'rgba(0,0,0,1)'); v.addColorStop(0.5, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,1)');
    g.globalCompositeOperation = 'destination-out'; g.fillStyle = v; g.fillRect(0, 0, 256, 32);
  }), []);
  useFrame(({ clock }, dt) => {
    if (!level) return;
    const t = clock.elapsedTime; const fast = level === 'rood';
    if (spin.current) spin.current.rotation.y += dt * (reducedMotion() ? 0.6 : fast ? 4.2 : 2.2);
    const pulse = 0.5 + 0.5 * Math.sin(t * (fast ? 8 : 4));
    if (dome.current) dome.current.color.setRGB(1.6 + pulse, fast ? 0.15 : 0.7 + pulse * 0.3, 0.08);
    if (light.current) light.current.intensity = 10 + pulse * 30;
  });
  if (!level || !room) return null;
  const col = level === 'rood' ? '#ff2a2a' : '#ff9a1f';
  return (
    <group position={pos}>
      <mesh position={[0, -0.12, 0]}><cylinderGeometry args={[0.34, 0.38, 0.16, 20]} /><meshStandardMaterial color="#1a1d29" metalness={0.6} roughness={0.3} /></mesh>
      <mesh position={[0, 0.06, 0]}><sphereGeometry args={[0.3, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2]} /><meshBasicMaterial ref={dome} color={col} toneMapped={false} /></mesh>
      <group ref={spin} position={[0, 0.12, 0]}>
        {[0, Math.PI].map((r) => (
          <mesh key={r} rotation={[0, r, 0]} position={[Math.cos(r) * 2.6, 0, -Math.sin(r) * 2.6]} raycast={() => null}>
            <planeGeometry args={[5.2, 0.9]} />
            <meshBasicMaterial map={beamTex} color={col} transparent opacity={0.55} depthWrite={false} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} toneMapped={false} />
          </mesh>
        ))}
      </group>
      <pointLight ref={light} color={col} intensity={20} distance={13} decay={1.6} />
    </group>
  );
}

/* ---------------- sneeuw in december ---------------- */
export function Snow() {
  const isDec = new Date().getMonth() === 11;
  const data = useMemo(() => {
    if (!isDec) return null;
    const N = 1600; const p = new Float32Array(N * 3); const a = new Float32Array(N * 2);
    for (let i = 0; i < N; i++) { const r = Math.sqrt(Math.random()) * 58, t = Math.random() * Math.PI * 2; p.set([Math.sin(t) * r, Math.random() * 56, Math.cos(t) * r], i * 3); a.set([0.7 + Math.random() * 1.1, Math.random() * 6.28], i * 2); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('aux', new THREE.BufferAttribute(a, 2));
    const m = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, uniforms: { uTime: { value: 0 }, uPx: { value: 1 } },
      vertexShader: `attribute vec2 aux; uniform float uTime; uniform float uPx;
        void main(){ vec3 q = position; q.y = mod(q.y - uTime * aux.x, 56.0) - 20.0; q.x += sin(uTime * 0.6 + aux.y) * 0.7; q.z += cos(uTime * 0.5 + aux.y * 1.3) * 0.7;
          vec4 mv = modelViewMatrix * vec4(q, 1.0); gl_PointSize = uPx * (2.0 + aux.x * 1.4) * (60.0 / -mv.z); gl_Position = projectionMatrix * mv; }`,
      fragmentShader: `void main(){ float a = smoothstep(0.5, 0.1, length(gl_PointCoord - 0.5)); gl_FragColor = vec4(vec3(1.0), a * 0.85); }`,
    });
    return { g, m };
  }, [isDec]);
  const dpr = useThree((s) => s.viewport.dpr);
  useFrame(({ clock }) => { if (data) { data.m.uniforms.uTime.value = clock.elapsedTime; data.m.uniforms.uPx.value = dpr; } });
  if (!data) return null;
  return <points geometry={data.g} material={data.m} frustumCulled={false} raycast={() => null} />;
}

/* ---------------- discobal bij het feestthema ---------------- */
export function Disco() {
  const theme = useWorld((s) => s.theme);
  const g = useRef<THREE.Group>(null);
  const beams = useMemo(() => Array.from({ length: 7 }, (_, i) => ({ tilt: 0.5 + (i % 3) * 0.22, yaw: (i / 7) * Math.PI * 2, c: CONF_COLORS[i % CONF_COLORS.length] })), []);
  const beamMats = useMemo(() => beams.map((b) => new THREE.MeshBasicMaterial({ color: b.c, transparent: true, opacity: 0.22, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false, side: THREE.DoubleSide })), [beams]);
  const lights = useRef<(THREE.PointLight | null)[]>([]);
  useFrame(({ clock }, dt) => {
    if (theme !== 'feest' || !g.current) return;
    const t = clock.elapsedTime;
    g.current.rotation.y += dt * 0.6;
    beamMats.forEach((m, i) => { m.color.setHSL((t * 0.07 + i / 7) % 1, 1, 0.55); m.opacity = 0.16 + 0.1 * Math.sin(t * 3 + i); });
    lights.current.forEach((l, i) => { if (!l) return; const a = t * 0.9 + i * 2.1; l.position.set(Math.sin(a) * 9, 3, Math.cos(a) * 9); l.color.setHSL((t * 0.1 + i / 3) % 1, 1, 0.55); });
  });
  if (theme !== 'feest') return null;
  return (
    <>
      <group ref={g} position={[0, 7.2, 4.6]}>
        <mesh><icosahedronGeometry args={[0.6, 2]} /><meshStandardMaterial color="#e8ecf5" metalness={1} roughness={0.12} flatShading envMapIntensity={2.2} /></mesh>
        <mesh position={[0, 1.6, 0]}><cylinderGeometry args={[0.02, 0.02, 2.6, 6]} /><meshStandardMaterial color="#888" /></mesh>
        {beams.map((b, i) => (
          <group key={i} rotation={[0, b.yaw, 0]}>
            <mesh rotation={[-b.tilt, 0, 0]} position={[0, -Math.cos(b.tilt) * 6, Math.sin(b.tilt) * 6]} material={beamMats[i]} raycast={() => null}>
              <cylinderGeometry args={[0.04, 0.6, 12, 10, 1, true]} />
            </mesh>
          </group>
        ))}
      </group>
      {[0, 1, 2].map((i) => <pointLight key={i} ref={(el) => { lights.current[i] = el; }} intensity={35} distance={16} decay={1.5} />)}
    </>
  );
}

/* ---------------- stemstudio: dansende speaker en microfoon met popfilter ---------------- */
export function VoiceProps() {
  const room = ROOMS.find((r) => r.id === 'stem');
  const [spot, setSpot] = useState<{ s: [number, number]; m: [number, number]; face: number } | null>(null);
  useEffect(() => {
    if (!room) return; let on = true;
    void loadNav().then((nav) => {
      if (!on) return;
      const at = (u: number, v: number): [number, number] => { const rad = (R_IN + R_OUT) / 2 + v, a = slotAngle(room.slot) + u / rad; return [Math.sin(a) * rad, Math.cos(a) * rad]; };
      const c = at(0, 0); const want = at(2.5, 2.7); const want2 = at(1.6, 2.9);
      const s = (nav && nearestFree(nav, want[0], want[1])) || want; const m = (nav && nearestFree(nav, want2[0], want2[1])) || want2;
      setSpot({ s, m, face: Math.atan2(c[0] - s[0], c[1] - s[1]) });
    });
    return () => { on = false; };
  }, [room]);
  const box = useRef<THREE.Group>(null); const woof = useRef<THREE.Mesh>(null); const notes = useRef<(THREE.Sprite | null)[]>([]);
  const noteTex = useMemo(() => canvasTex(64, 64, (g) => { g.fillStyle = '#ffffff'; g.font = 'bold 52px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('♪', 32, 34); }), []);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime; const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.05)), 10);
    if (box.current) { box.current.scale.set(1 + beat * 0.03, 1 + beat * 0.06, 1 + beat * 0.03); box.current.rotation.z = Math.sin(t * 2.1) * 0.025; }
    if (woof.current) woof.current.scale.setScalar(1 + beat * 0.22);
    notes.current.forEach((n, i) => {
      if (!n) return; const k = ((t * 0.35 + i / 3) % 1);
      n.position.set(Math.sin(k * 6 + i) * 0.25, 1.0 + k * 1.3, 0.1); (n.material as THREE.SpriteMaterial).opacity = Math.sin(k * Math.PI) * 0.9;
      (n.material as THREE.SpriteMaterial).color.setHSL((0.52 + i * 0.12) % 1, 1, 0.65);
    });
  });
  if (!room || !spot) return null;
  return (
    <group>
      <group position={[spot.s[0], 0, spot.s[1]]} rotation={[0, spot.face, 0]}>
        <group ref={box}>
          <mesh position={[0, 0.45, 0]} castShadow><boxGeometry args={[0.5, 0.9, 0.42]} /><meshStandardMaterial color="#14161f" roughness={0.55} /></mesh>
          <mesh ref={woof} position={[0, 0.34, 0.215]}><circleGeometry args={[0.17, 28]} /><meshStandardMaterial color="#2a2f3e" roughness={0.3} metalness={0.4} /></mesh>
          <mesh position={[0, 0.34, 0.218]}><ringGeometry args={[0.17, 0.19, 28]} /><meshBasicMaterial color="#22D3EE" toneMapped={false} /></mesh>
          <mesh position={[0, 0.7, 0.216]}><circleGeometry args={[0.065, 20]} /><meshStandardMaterial color="#3a4055" roughness={0.3} metalness={0.5} /></mesh>
        </group>
        {[0, 1, 2].map((i) => (
          <sprite key={i} ref={(el) => { notes.current[i] = el; }} scale={[0.28, 0.28, 1]} raycast={() => null}>
            <spriteMaterial map={noteTex} transparent depthWrite={false} toneMapped={false} />
          </sprite>
        ))}
      </group>
      <group position={[spot.m[0], 0, spot.m[1]]} rotation={[0, spot.face, 0]}>
        <mesh position={[0, 0.02, 0]}><cylinderGeometry args={[0.18, 0.2, 0.04, 16]} /><meshStandardMaterial color="#1d2130" metalness={0.6} roughness={0.35} /></mesh>
        <mesh position={[0, 0.72, 0]}><cylinderGeometry args={[0.018, 0.018, 1.4, 8]} /><meshStandardMaterial color="#9aa3b5" metalness={0.8} roughness={0.25} /></mesh>
        <mesh position={[0, 1.44, 0.05]} rotation={[Math.PI / 2.4, 0, 0]}><capsuleGeometry args={[0.045, 0.12, 4, 10]} /><meshStandardMaterial color="#c9ced9" metalness={0.7} roughness={0.25} /></mesh>
        <group position={[0, 1.47, 0.2]}>
          <mesh><torusGeometry args={[0.1, 0.008, 6, 24]} /><meshStandardMaterial color="#111" /></mesh>
          <mesh><circleGeometry args={[0.1, 24]} /><meshStandardMaterial color="#0b0b10" transparent opacity={0.55} side={THREE.DoubleSide} depthWrite={false} /></mesh>
        </group>
      </group>
    </group>
  );
}

/**
 * Post-its op de randen van de bureauschermen (verbeterpunt s4). Kabels, bekers, koptelefoons, lampjes
 * en notitieblokken zitten al in het gebakken kantoor; dit zijn de briefjes erbij. Eén tekenaanroep.
 * Hetzelfde materiaal-type als het gebakken licht (onverlicht), dus ze passen bij dag en nacht.
 */
const POSTIT = ['#ffe066', '#ff9ec4', '#8be9fd', '#a6f28f', '#ffb86b'];
export function PostIts({ screens }: { screens: { mesh: THREE.Mesh; kind: string }[] }) {
  const tex = useMemo(() => canvasTex(64, 64, (g) => {
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, 64, 64);
    const gr = g.createLinearGradient(0, 0, 0, 64); gr.addColorStop(0, 'rgba(0,0,0,0.16)'); gr.addColorStop(0.22, 'rgba(0,0,0,0.04)'); gr.addColorStop(1, 'rgba(0,0,0,0.1)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    g.strokeStyle = 'rgba(30,35,60,0.55)'; g.lineWidth = 2.4; g.lineCap = 'round';
    for (let r = 0; r < 3; r++) { g.beginPath(); const y = 24 + r * 12; const end = r === 2 ? 34 : 54; g.moveTo(10, y);
      for (let x = 10; x <= end; x += 4) g.lineTo(x, y + Math.sin(x * 0.7 + r * 2) * 1.6); g.stroke(); }
  }), []);
  const data = useMemo(() => {
    let seed = 11; const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    const out: { m: THREE.Matrix4; c: THREE.Color }[] = [];
    const up = new THREE.Vector3(0, 1, 0); const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
    for (const s of screens) {
      if (s.kind !== 'd' || rnd() > 0.55) continue;
      const g = s.mesh.geometry; const pos = g.getAttribute('position'); if (!pos || pos.count < 3) continue;
      s.mesh.updateWorldMatrix(true, false); const mw = s.mesh.matrixWorld;
      const idx = g.getIndex(); const i0 = idx ? idx.getX(0) : 0, i1 = idx ? idx.getX(1) : 1, i2 = idx ? idx.getX(2) : 2;
      a.fromBufferAttribute(pos, i0).applyMatrix4(mw); b.fromBufferAttribute(pos, i1).applyMatrix4(mw); c.fromBufferAttribute(pos, i2).applyMatrix4(mw);
      const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)); n.y = 0; if (n.lengthSq() < 1e-10) continue; n.normalize();
      const right = new THREE.Vector3().crossVectors(up, n).normalize();
      const ctr = new THREE.Vector3(); const v = new THREE.Vector3(); let hw = 0, hh = 0;
      for (let k = 0; k < pos.count; k++) ctr.add(v.fromBufferAttribute(pos, k).applyMatrix4(mw)); ctr.divideScalar(pos.count);
      for (let k = 0; k < pos.count; k++) { v.fromBufferAttribute(pos, k).applyMatrix4(mw).sub(ctr); hw = Math.max(hw, Math.abs(v.dot(right))); hh = Math.max(hh, Math.abs(v.dot(up))); }
      if (hw < 0.1 || hw > 0.6) continue; // alleen bureauschermen
      const notes = rnd() < 0.3 ? 2 : 1; const side = rnd() < 0.5 ? -1 : 1;
      for (let k = 0; k < notes; k++) {
        const sz = 0.07 + rnd() * 0.012;
        // eerste briefje op een bovenhoek (half over de rand), tweede onderaan op de rand ernaast
        const p = ctr.clone().addScaledVector(right, side * (hw - 0.012 - k * 0.02)).addScaledVector(up, k ? -hh + 0.02 : hh - 0.022).addScaledVector(n, 0.006 + k * 0.001);
        const q = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(right, up, n));
        q.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), (rnd() - 0.5) * 0.5));
        out.push({ m: new THREE.Matrix4().compose(p, q, new THREE.Vector3(sz, sz, 1)), c: new THREE.Color(POSTIT[Math.floor(rnd() * POSTIT.length)]).multiplyScalar(0.8) });
      }
    }
    return out;
  }, [screens]);
  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    const im = ref.current; if (!im) return;
    data.forEach((d, i) => { im.setMatrixAt(i, d.m); im.setColorAt(i, d.c); });
    im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; im.computeBoundingSphere();
  }, [data]);
  if (!data.length) return null;
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, data.length]} raycast={() => null} frustumCulled={false}>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial map={tex} side={THREE.DoubleSide} />
    </instancedMesh>
  );
}
