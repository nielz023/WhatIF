/**
 * DE ECHTE CAST IN HET KANTOOR (verbeterlijst punt 34).
 * Het hoofdpersonage (CEO) en de vaste cast van video 1 (mama, papa, broertje, opa, oma, beste vriend, pestkop)
 * als de echte modellen uit de projectbestanden: hoofdpersonage/hoofdpersonage.glb en cast/glb/<figuur>.glb,
 * met gltf-transform verkleind (meshopt, vereenvoudigd, palettextuur in webp): samen ~1,3 MB in plaats van ~25 MB.
 * Ze staan als base64-tekst in public/models (net als het kantoor), omdat de pagina alleen gewone webbestanden serveert.
 * Elk model krijgt de glans-look van de video's: vinyl met een heldere lak (clearcoat 1, clearcoatRoughness 0,1).
 * Lukt laden niet (geen WebAssembly voor meshopt of een fout bestand), dan blijft het gewone poppetje staan.
 */
import { useEffect, useMemo, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader, MeshoptDecoder } from 'three-stdlib';

export type CastModel = 'hoofdpersonage' | 'mama' | 'papa' | 'broertje' | 'opa' | 'oma' | 'beste_vriend' | 'pestkop';
const URL_OF = (n: CastModel) => (n === 'hoofdpersonage' ? './models/hoofdpersonage.glb.txt' : `./models/cast_${n}.glb.txt`);

const cache = new Map<CastModel, Promise<THREE.Group>>();
let decoder: Promise<unknown> | null = null;
function getDecoder() {
  return (decoder ??= (async () => { const d = MeshoptDecoder() as { ready?: Promise<void>; supported?: boolean }; if (!d.supported) throw new Error('meshopt niet beschikbaar'); await d.ready; return d; })());
}

/** glanzend vinyl zoals in de video's; de kleuren (palettextuur of kleur) blijven */
export function vinyl(src: THREE.Material): THREE.MeshPhysicalMaterial {
  const s = src as THREE.MeshStandardMaterial;
  return new THREE.MeshPhysicalMaterial({
    map: s.map ?? null, color: s.color ? s.color.clone() : new THREE.Color('#ffffff'), vertexColors: s.vertexColors,
    roughness: 0.42, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.1, sheen: 0.25, sheenRoughness: 0.6, envMapIntensity: 1.1,
    transparent: s.transparent, opacity: s.opacity ?? 1, side: s.side,
  });
}

export function loadCast(name: CastModel): Promise<THREE.Group> {
  let p = cache.get(name);
  if (!p) {
    p = (async () => {
      const r = await fetch(URL_OF(name)); if (!r.ok) throw new Error(`${name} ${r.status}`);
      const bin = atob((await r.text()).trim()); const buf = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      const loader = new GLTFLoader(); loader.setMeshoptDecoder(await getDecoder() as never);
      const scene = await new Promise<THREE.Group>((ok, bad) => loader.parse(buf.buffer, '', (g) => ok(g.scene), bad));
      const mats = new Map<THREE.Material, THREE.MeshPhysicalMaterial>();
      scene.traverse((o) => {
        const m = o as THREE.Mesh; if (!m.isMesh) return;
        m.castShadow = true; m.receiveShadow = false;
        const conv = (x: THREE.Material) => { let v = mats.get(x); if (!v) { v = vinyl(x); mats.set(x, v); } return v; };
        m.material = Array.isArray(m.material) ? m.material.map(conv) : conv(m.material);
      });
      return scene;
    })();
    p.catch((e) => console.warn('[HQ] castmodel niet geladen', name, e));
    cache.set(name, p);
  }
  return p;
}

/** Een kopie van het model, op de grond gezet (voeten op y = 0, midden op x/z = 0) en geschaald naar `height` meter. */
export function useCastModel(name: CastModel | undefined, height: number): THREE.Group | null {
  const [scene, setScene] = useState<THREE.Group | null>(null);
  useEffect(() => { if (!name) return; let on = true; loadCast(name).then((s) => on && setScene(s)).catch(() => {}); return () => { on = false; }; }, [name]);
  return useMemo(() => {
    if (!scene) return null;
    const c = scene.clone(true);
    const box = new THREE.Box3().setFromObject(c); const size = box.getSize(new THREE.Vector3());
    c.scale.setScalar(height / (size.y || 1));
    const b2 = new THREE.Box3().setFromObject(c); const ctr = b2.getCenter(new THREE.Vector3());
    c.position.set(-ctr.x, -b2.min.y, -ctr.z);
    const g = new THREE.Group(); g.add(c); return g;
  }, [scene, height]);
}

// alleen bij lokaal testen: laden van een castmodel controleren
if (typeof window !== 'undefined' && window.location?.hostname === 'localhost') (window as unknown as { __dmCast: unknown }).__dmCast = loadCast;
