/**
 * Driftmark-stijl voor het 3D-kantoor (niels 2026-11-05: "versier het kantoor in Driftmark-stijl").
 * Huisstijl: oranje hoodie van het hoofdpersonage, nachtblauw/paars, geel accent,
 * glans-look (warm hoofdlicht + oranje/blauw randlicht), portalen zoals op de banner.
 */
import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

type V3 = [number, number, number];
export const DM = { orange: '#f97316', orangeHot: '#fb923c', blue: '#38bdf8', purple: '#8b5cf6', yellow: '#facc15', night: '#0b1030', skin: '#f2c49b' };

/* ---------- textures ---------- */
const texCache = new Map<string, THREE.Texture>();
function useImg(src: string) {
  return useMemo(() => {
    const hit = texCache.get(src);
    if (hit) return hit;
    const t = new THREE.TextureLoader().load(src);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    texCache.set(src, t);
    return t;
  }, [src]);
}

function canvasTex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d')!;
  draw(g);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

/* ---------- poster aan de muur ---------- */
export function Poster({ src, p, rot = 0, w = 1.7, h = 1.05, frame = DM.orange }: { src: string; p: V3; rot?: number; w?: number; h?: number; frame?: string }) {
  const tex = useImg(src);
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <mesh position={[0, 0, -0.01]}>
        <boxGeometry args={[w + 0.12, h + 0.12, 0.04]} />
        <meshStandardMaterial color={frame} emissive={frame} emissiveIntensity={0.9} toneMapped={false} />
      </mesh>
      <mesh position={[0, 0, 0.015]}>
        <planeGeometry args={[w, h]} />
        <meshStandardMaterial map={tex} roughness={0.35} emissive="#ffffff" emissiveMap={tex} emissiveIntensity={0.35} />
      </mesh>
    </group>
  );
}

/* ---------- groot neonbord DRIFTMARK ---------- */
export function NeonSign({ p, rot = 0, width = 16 }: { p: V3; rot?: number; width?: number }) {
  const tex = useMemo(() => canvasTex(2048, 512, (g) => {
    g.clearRect(0, 0, 2048, 512);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.font = '900 300px "Arial Black", Impact, sans-serif';
    const dW = g.measureText('DRIFT').width, mW = g.measureText('MARK').width, total = dW + mW, x0 = 1024 - total / 2;
    // donkere blokschaduw (huisstijl)
    g.fillStyle = '#1a0f3d';
    g.textAlign = 'left';
    g.fillText('DRIFT', x0 + 14, 214); g.fillText('MARK', x0 + dW + 14, 214);
    g.shadowColor = DM.orange; g.shadowBlur = 40;
    g.fillStyle = '#fff7ed'; g.fillText('DRIFT', x0, 200);
    const gr = g.createLinearGradient(x0 + dW, 0, x0 + total, 0);
    gr.addColorStop(0, DM.orangeHot); gr.addColorStop(1, DM.yellow);
    g.fillStyle = gr; g.fillText('MARK', x0 + dW, 200);
    g.shadowBlur = 24; g.shadowColor = DM.blue;
    g.font = '700 74px "Arial Black", Impact, sans-serif'; g.textAlign = 'center';
    g.fillStyle = DM.blue; g.fillText('A NEW 3D WHAT IF EVERY WEEK', 1024, 420);
  }), []);
  const ref = useRef<THREE.MeshBasicMaterial>(null);
  useFrame(({ clock }) => { if (ref.current) ref.current.opacity = 0.92 + Math.sin(clock.elapsedTime * 2.3) * 0.04 + (Math.random() < 0.004 ? -0.4 : 0); });
  return (
    <mesh position={p} rotation={[0, rot, 0]}>
      <planeGeometry args={[width, width / 4]} />
      <meshBasicMaterial ref={ref} map={tex} transparent toneMapped={false} depthWrite={false} side={THREE.DoubleSide} />
    </mesh>
  );
}

/* ---------- portaal (zoals op de banner) ---------- */
export function Portal({ p, rot = 0, color, r = 2.2 }: { p: V3; rot?: number; color: string; r?: number }) {
  const ring = useRef<THREE.Mesh>(null);
  const swirl = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (swirl.current) swirl.current.rotation.z = -t * 0.8;
    if (ring.current) (ring.current.material as THREE.MeshStandardMaterial).emissiveIntensity = 2.6 + Math.sin(t * 3) * 0.6;
  });
  const swirlTex = useMemo(() => canvasTex(512, 512, (g) => {
    const gr = g.createRadialGradient(256, 256, 10, 256, 256, 256);
    gr.addColorStop(0, '#ffffff'); gr.addColorStop(0.25, color); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = 'rgba(255,255,255,.55)'; g.lineWidth = 10;
    for (let i = 0; i < 5; i++) { g.beginPath(); for (let a = 0; a < 7; a += 0.05) { const rr = 20 + a * 32; g.lineTo(256 + Math.cos(a + i * 1.256) * rr, 256 + Math.sin(a + i * 1.256) * rr); } g.stroke(); }
  }), [color]);
  return (
    <group position={p} rotation={[0, rot, 0]}>
      <mesh ref={ring}>
        <torusGeometry args={[r, 0.18, 16, 64]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2.6} toneMapped={false} />
      </mesh>
      <mesh ref={swirl}>
        <circleGeometry args={[r - 0.1, 48]} />
        <meshBasicMaterial map={swirlTex} transparent opacity={0.85} toneMapped={false} depthWrite={false} side={THREE.DoubleSide} />
      </mesh>
      <pointLight color={color} intensity={18} distance={12} decay={1.6} />
    </group>
  );
}

/* ---------- het hoofdpersonage als glanzend vinyl beeld ---------- */
function Vinyl({ color, ...rest }: { color: string } & Partial<THREE.MeshPhysicalMaterialParameters>) {
  return <meshPhysicalMaterial color={color} roughness={0.38} clearcoat={0.8} clearcoatRoughness={0.25} sheen={0.4} {...rest} />;
}
export function Mascot({ p, rot = 0, s = 1 }: { p: V3; rot?: number; s?: number }) {
  const g = useRef<THREE.Group>(null);
  useFrame(({ clock }) => { if (g.current) { g.current.position.y = Math.sin(clock.elapsedTime * 1.4) * 0.08; g.current.rotation.y = Math.sin(clock.elapsedTime * 0.5) * 0.15; } });
  const M = (pp: V3, geo: React.ReactNode, mat: React.ReactNode, r: V3 = [0, 0, 0]) => <mesh position={pp} rotation={r} castShadow>{geo}{mat}</mesh>;
  return (
    <group position={p} rotation={[0, rot, 0]} scale={s}>
      {/* sokkel */}
      {M([0, 0.25, 0], <cylinderGeometry args={[1.25, 1.4, 0.5, 40]} />, <meshStandardMaterial color="#1a1f3d" roughness={0.3} metalness={0.4} />)}
      {M([0, 0.52, 0], <torusGeometry args={[1.28, 0.05, 8, 60]} />, <meshStandardMaterial color={DM.orange} emissive={DM.orange} emissiveIntensity={2.5} toneMapped={false} />, [Math.PI / 2, 0, 0])}
      <group ref={g}>
        <group position={[0, 0.5, 0]}>
          {/* sneakers */}
          {[-0.22, 0.22].map((x) => M([x, 0.08, 0.06], <boxGeometry args={[0.26, 0.16, 0.42]} />, <Vinyl color="#f8fafc" />))}
          {/* benen (jeans) */}
          {[-0.22, 0.22].map((x) => M([x, 0.5, 0], <capsuleGeometry args={[0.13, 0.55, 6, 16]} />, <Vinyl color="#2b4c8c" />))}
          {/* hoodie */}
          {M([0, 1.25, 0], <capsuleGeometry args={[0.42, 0.55, 8, 24]} />, <Vinyl color={DM.orange} />)}
          {M([0, 1.05, 0.38], <boxGeometry args={[0.5, 0.18, 0.06]} />, <Vinyl color="#ea580c" />)}
          {/* armen */}
          {M([-0.55, 1.25, 0.05], <capsuleGeometry args={[0.12, 0.55, 6, 16]} />, <Vinyl color={DM.orange} />, [0, 0, 0.35])}
          {M([0.55, 1.45, 0.05], <capsuleGeometry args={[0.12, 0.55, 6, 16]} />, <Vinyl color={DM.orange} />, [0, 0, -2.4])}
          {M([0.82, 1.92, 0.05], <sphereGeometry args={[0.13, 16, 16]} />, <Vinyl color={DM.skin} />)}
          {M([-0.73, 0.92, 0.05], <sphereGeometry args={[0.13, 16, 16]} />, <Vinyl color={DM.skin} />)}
          {/* capuchon */}
          {M([0, 1.86, -0.22], <sphereGeometry args={[0.5, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />, <Vinyl color="#ea580c" side={THREE.DoubleSide} />, [-0.9, 0, 0])}
          {/* hoofd */}
          {M([0, 2.25, 0.02], <sphereGeometry args={[0.55, 32, 24]} />, <Vinyl color={DM.skin} roughness={0.5} sheen={0.8} />)}
          {/* haar */}
          {M([0, 2.5, -0.04], <sphereGeometry args={[0.54, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2.6]} />, <Vinyl color="#5a3420" />)}
          {/* ogen */}
          {[-0.19, 0.19].map((x) => (
            <group key={x} position={[x, 2.3, 0.48]}>
              <mesh><sphereGeometry args={[0.13, 16, 16]} /><Vinyl color="#ffffff" /></mesh>
              <mesh position={[0, 0, 0.09]}><sphereGeometry args={[0.065, 12, 12]} /><meshStandardMaterial color="#111" roughness={0.2} /></mesh>
              <mesh position={[0.02, 0.025, 0.14]}><sphereGeometry args={[0.02, 8, 8]} /><meshBasicMaterial color="#fff" /></mesh>
            </group>
          ))}
          {/* glimlach + blos */}
          {M([0, 2.05, 0.5], <torusGeometry args={[0.12, 0.022, 8, 20, Math.PI]} />, <meshStandardMaterial color="#7a2e1f" />, [0, 0, Math.PI])}
          {[-0.33, 0.33].map((x) => M([x, 2.12, 0.42], <sphereGeometry args={[0.07, 12, 12]} />, <meshStandardMaterial color="#f28b82" transparent opacity={0.6} />))}
        </group>
      </group>
    </group>
  );
}

/* ---------- zwevende vraagtekens ---------- */
export function FloatingMarks({ center, spread = 10, n = 9 }: { center: V3; spread?: number; n?: number }) {
  const tex = useMemo(() => canvasTex(256, 256, (g) => {
    g.font = '900 220px "Arial Black", Impact, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.shadowColor = DM.yellow; g.shadowBlur = 30; g.fillStyle = DM.yellow; g.fillText('?', 128, 140);
  }), []);
  const items = useMemo(() => Array.from({ length: n }, (_, i) => ({ x: Math.cos(i * 2.4) * spread * (0.4 + (i % 3) * 0.25), z: Math.sin(i * 2.4) * spread * (0.4 + (i % 3) * 0.25), y: 2 + (i % 4) * 1.3, sp: 0.6 + (i % 5) * 0.15, s: 0.9 + (i % 3) * 0.45 })), [n, spread]);
  const refs = useRef<(THREE.Sprite | null)[]>([]);
  useFrame(({ clock }) => { const t = clock.elapsedTime; items.forEach((it, i) => { const r = refs.current[i]; if (r) r.position.y = it.y + Math.sin(t * it.sp + i) * 0.5; }); });
  return (
    <group position={center}>
      {items.map((it, i) => (
        <sprite key={i} ref={(el) => { refs.current[i] = el; }} position={[it.x, it.y, it.z]} scale={[it.s, it.s, it.s]}>
          <spriteMaterial map={tex} transparent toneMapped={false} depthWrite={false} />
        </sprite>
      ))}
    </group>
  );
}

/* ---------- welk beeld hangt in welke kamer ---------- */
export const ROOM_POSTERS: Record<string, string[]> = {
  research: ['./img/s1_22_ruimte.jpg', './img/s1_16_lab.jpg'],
  creative: ['./img/c3_01_hoofdpersonage_en_gezin.jpg', './img/s3_01_stad.jpg'],
  script: ['./img/c2_01_hoofdpersonage.jpg', './img/s2_02_slaapkamer.jpg'],
  publishing: ['./img/banner.jpg', './img/s3_06_stadsplein.jpg'],
  ceo: ['./img/banner.jpg', './img/c1_hoofdpersonage.jpg'],
  voice: ['./img/c3_02_vaste_cast.jpg', './img/s1_12_tvstudio.jpg'],
  thumbnail: ['./img/s3_05_brug_lab.jpg', './img/s1_01_pretpark.jpg'],
  production: ['./img/s3_03_strand.jpg', './img/s3_04_snelweg.jpg'],
  warroom: ['./img/s1_19_bunker.jpg', './img/s1_20_woestijnbasis.jpg'],
};
