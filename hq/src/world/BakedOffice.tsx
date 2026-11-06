/**
 * Het in Blender gebouwde kantoor (hq/blender/office_build.py) met ingebakken licht en schaduw.
 * Laadt public/models/office.glb.txt (base64), zet live dashboards op de schermen,
 * maakt glas doorzichtig en laat de neon per afdeling pulseren. Medewerkers en borden
 * blijven in NeonOffice.tsx (die zijn live); de stoelposities komen uit dit model.
 */
import { useEffect, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { GLTFLoader } from 'three-stdlib';

const URL = './models/office.glb.txt';
type V3 = [number, number, number];
export interface OfficeModel { scene: THREE.Group; seats: Record<string, V3[]>; neon: Record<string, THREE.MeshStandardMaterial[]>; screens: { mesh: THREE.Mesh; kind: string }[] }

let promise: Promise<OfficeModel> | null = null;
function load(): Promise<OfficeModel> {
  if (!promise) {
    promise = fetch(URL)
      .then((r) => { if (!r.ok) throw new Error('office ' + r.status); return r.text(); })
      .then((b64) => {
        const bin = atob(b64.trim()); const buf = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        return new Promise<THREE.Group>((res, rej) => new GLTFLoader().parse(buf.buffer, '', (g) => res(g.scene), rej));
      })
      .then((scene) => {
        const seats: Record<string, V3[]> = {}; const neon: Record<string, THREE.MeshStandardMaterial[]> = {}; const screens: OfficeModel['screens'] = [];
        const glass = new THREE.MeshStandardMaterial({ color: '#9fdcff', transparent: true, opacity: 0.13, roughness: 0.05, metalness: 0.3, depthWrite: false, side: THREE.DoubleSide });
        scene.updateMatrixWorld(true);
        scene.traverse((o) => {
          const n = o.name;
          if (n.startsWith('seat_')) {
            const [, room, i] = n.split('_'); const p = new THREE.Vector3(); o.getWorldPosition(p);
            (seats[room] ??= [])[Number(i)] = [p.x, p.y, p.z];
            return;
          }
          const m = o as THREE.Mesh; if (!m.isMesh) return;
          const base = n.replace(/_\d+$/, '').replace(/\.\d+$/, '');
          if (base.startsWith('baked')) {
            const mt = m.material as THREE.MeshStandardMaterial;
            mt.roughness = 0.42; mt.metalness = 0.0; mt.envMapIntensity = 0.5; mt.emissiveIntensity = 1.0; mt.toneMapped = false;
            if (mt.emissiveMap) { mt.emissiveMap.anisotropy = 8; mt.emissiveMap.colorSpace = THREE.SRGBColorSpace; }
            m.receiveShadow = true;
          } else if (base.startsWith('glass')) {
            m.material = glass; m.renderOrder = 2;
          } else if (n.startsWith('scr_')) {
            screens.push({ mesh: m, kind: n.split('_')[2] ?? 'd' });
          } else if (n.startsWith('neon_')) {
            const room = n.split('_')[1].replace(/\.\d+$/, '');
            const list = (Array.isArray(m.material) ? m.material : [m.material]) as THREE.MeshStandardMaterial[];
            const cl = list.map((x) => { const c = x.clone(); c.toneMapped = false; c.userData.base = c.emissiveIntensity || 1; return c; });
            m.material = Array.isArray(m.material) ? cl : cl[0];
            (neon[room] ??= []).push(...cl);
          }
        });
        return { scene, seats, neon, screens };
      });
    promise.catch((e) => console.warn('[HQ] Blender-kantoor niet geladen, ik toon het eenvoudige kantoor', e));
  }
  return promise;
}

/** null zolang het model laadt of als het niet lukt (dan toont NeonOffice zijn eigen kantoor). */
export function useOffice(): OfficeModel | null {
  const [m, setM] = useState<OfficeModel | null>(null);
  useEffect(() => { let on = true; load().then((x) => on && setM(x)).catch(() => {}); return () => { on = false; }; }, []);
  return m;
}

export function BakedOffice({ model, screens, lit, alert }: { model: OfficeModel; screens: THREE.Texture[]; lit: (room: string) => boolean; alert: (room: string) => boolean }) {
  // schermen: per soort een eigen reeks dashboards
  useMemo(() => {
    model.screens.forEach(({ mesh, kind }, i) => {
      const t = kind === 't' ? screens[5] : kind === 'm' ? screens[4] : screens[(i * 7 + (kind === 'w' ? 2 : 0)) % screens.length];
      mesh.material = new THREE.MeshBasicMaterial({ map: t, toneMapped: false, color: new THREE.Color(0.85, 0.85, 0.85) });
    });
  }, [model, screens]);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    for (const [room, mats] of Object.entries(model.neon)) {
      if (room === 'hub') continue;
      const k = (alert(room) ? 1.0 + Math.max(0, Math.sin(t * 5)) * 0.9 : 1) * (lit(room) ? 1.45 : 1);
      for (const m of mats) m.emissiveIntensity = (m.userData.base as number) * k;
    }
  });
  return <primitive object={model.scene} />;
}
