/**
 * Het in Blender gebouwde kantoor (hq/blender/office_build.py) met ingebakken licht en schaduw.
 * Laadt public/models/office.glb.txt (base64, meshopt-gecomprimeerd), zet live dashboards op de
 * grote wandschermen (muur van roem, whiteboard, renderstand, alarmen ...), maakt glas doorzichtig
 * en laat de neon per afdeling pulseren. In de GLB zit een kleine voorlopige lightmap; daarna laden
 * we de scherpe versie los (2K, 4K of 8K, afhankelijk van de kwaliteitsstand).
 * Medewerkers en borden blijven in NeonOffice.tsx (die zijn live); stoelen en zitplekken komen uit dit model.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { GLTFLoader, MeshoptDecoder } from 'three-stdlib';
import { ROOMS, SPAN, R_IN, R_OUT } from './rooms';
import { useWorld, type Quality } from './useWorld';
import type { Dashboards } from './dashboards';
import { sky } from './extras';
import { setLoad, useOfficeLoad } from './loadState';

const URL = './models/office.glb.txt';
type V3 = [number, number, number];
export interface Screen { mesh: THREE.Mesh; kind: string; room: string }
export interface OfficeModel {
  scene: THREE.Group; seats: Record<string, V3[]>; chairs: Record<string, THREE.Object3D[]>;
  neon: Record<string, THREE.MeshStandardMaterial[]>; screens: Screen[]; lightmapped: THREE.MeshStandardMaterial[]; floor: THREE.Mesh[];
}

/** bij welke afdeling hoort een punt (op hoek in de ring), 'hub' in het midden */
export function roomAt(x: number, z: number): string {
  const r = Math.hypot(x, z);
  if (r < R_IN - 0.3) return 'hub';
  const a = ((Math.atan2(x, z) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const slot = Math.round(a / SPAN) % 10;
  return ROOMS.find((q) => q.slot === slot)?.id ?? (r > R_OUT + 0.5 ? 'buiten' : 'gang');
}

let promise: Promise<OfficeModel> | null = null;
function load(): Promise<OfficeModel> {
  if (!promise) {
    setLoad(0.04, 'Kantoor downloaden…');
    promise = fetch(URL)
      .then(async (r) => {
        if (!r.ok) throw new Error('office ' + r.status);
        // voortgang voor het laadscherm
        const total = Number(r.headers.get('content-length')) || 6_000_000;
        if (!r.body) return r.text();
        const rd = r.body.getReader(); const parts: Uint8Array[] = []; let got = 0;
        for (;;) { const { done, value } = await rd.read(); if (done) break; parts.push(value); got += value.length; setLoad(0.05 + 0.75 * Math.min(1, got / total)); }
        const all = new Uint8Array(got); let o = 0; for (const p of parts) { all.set(p, o); o += p.length; }
        return new TextDecoder().decode(all);
      })
      .then((b64) => {
        setLoad(0.82, 'Kantoor in elkaar zetten…');
        const bin = atob(b64.trim()); const buf = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
        const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
        return new Promise<THREE.Group>((res, rej) => loader.parse(buf.buffer, '', (g) => res(g.scene), rej));
      })
      .then((scene) => {
        const seats: Record<string, V3[]> = {}; const chairs: Record<string, THREE.Object3D[]> = {};
        const neon: Record<string, THREE.MeshStandardMaterial[]> = {}; const screens: Screen[] = [];
        const lightmapped: THREE.MeshStandardMaterial[] = []; const floor: THREE.Mesh[] = [];
        const glass = new THREE.MeshStandardMaterial({ color: '#9fdcff', transparent: true, opacity: 0.13, roughness: 0.05, metalness: 0.3, depthWrite: false, side: THREE.DoubleSide });
        scene.updateMatrixWorld(true);
        const p = new THREE.Vector3();
        scene.traverse((o) => {
          const n = o.name;
          if (n.startsWith('seat_')) {
            const [, room, i] = n.split('_'); o.getWorldPosition(p);
            (seats[room] ??= [])[Number(i)] = [p.x, p.y, p.z];
            return;
          }
          const cm = /^chair_([a-z]+)_(\d+)/.exec(n);
          if (cm && !/^chair_/.test(o.parent?.name ?? '')) { (chairs[cm[1]] ??= [])[Number(cm[2])] = o; }
          const m = o as THREE.Mesh; if (!m.isMesh) return;
          const base = n.replace(/_\d+$/, '').replace(/\.\d+$/, '');
          const mats = (Array.isArray(m.material) ? m.material : [m.material]) as THREE.MeshStandardMaterial[];
          if (mats.some((x) => x.name?.startsWith('baked'))) {
            for (const mt of mats) {
              mt.roughness = 0.42; mt.metalness = 0.0; mt.envMapIntensity = 0.5; mt.emissiveIntensity = 1.0; mt.toneMapped = false;
              if (mt.emissiveMap) { mt.emissiveMap.anisotropy = 8; mt.emissiveMap.colorSpace = THREE.SRGBColorSpace; }
              // vloer: glanzender, zodat het neonlicht en de lucht erin weerkaatsen
              if (mt.name?.startsWith('baked_floor')) { mt.roughness = 0.18; mt.metalness = 0.12; mt.envMapIntensity = 1.15; }
              if (!lightmapped.includes(mt)) lightmapped.push(mt);
            }
            if (mats.some((x) => x.name?.startsWith('baked_floor'))) floor.push(m);
            m.receiveShadow = true;
          } else if (base.startsWith('glass')) {
            m.material = glass; m.renderOrder = 2;
          } else if (n.startsWith('scr_')) {
            m.getWorldPosition(p);
            screens.push({ mesh: m, kind: n.split('_')[2]?.replace(/\.\d+$/, '') ?? 'd', room: roomAt(p.x, p.z) });
          } else if (n.startsWith('neon_')) {
            const room = n.split('_')[1].replace(/\.\d+$/, '');
            const cl = mats.map((x) => { const c = x.clone(); c.toneMapped = false; c.userData.base = c.emissiveIntensity || 1; c.userData.hsl = c.emissive.getHSL({ h: 0, s: 0, l: 0 }); return c; });
            m.material = Array.isArray(m.material) ? cl : cl[0];
            (neon[room] ??= []).push(...cl);
          }
        });
        setLoad(1, 'Klaar'); useOfficeLoad.setState({ done: true });
        return { scene, seats, chairs, neon, screens, lightmapped, floor };
      });
    promise.catch((e) => { useOfficeLoad.setState({ failed: true, done: true }); console.warn('[HQ] Blender-kantoor niet geladen, ik toon het eenvoudige kantoor', e); });
  }
  return promise;
}

/** null zolang het model laadt of als het niet lukt (dan toont NeonOffice zijn eigen kantoor). */
export function useOffice(): OfficeModel | null {
  const [m, setM] = useState<OfficeModel | null>(null);
  useEffect(() => { let on = true; load().then((x) => on && setM(x)).catch(() => {}); return () => { on = false; }; }, []);
  return m;
}

/* ---------- scherpe lightmap los laden ---------- */
const LM = { '2k': './models/office_lm_2k.webp', '4k': './models/office_lm_4k.webp', '8k': './models/office_lm_8k.webp' } as const;
type LmRes = keyof typeof LM;
function wantRes(q: Quality): LmRes[] {
  const small = typeof window !== 'undefined' && Math.min(window.innerWidth, window.innerHeight) < 700;
  const gl = (() => { try { const c = document.createElement('canvas').getContext('webgl2'); return c ? (c.getParameter(c.MAX_TEXTURE_SIZE) as number) : 4096; } catch { return 4096; } })();
  if (q === 'snel' || small) return ['2k'];
  if (q === '4k' && gl >= 8192) return ['8k', '4k', '2k'];
  return ['4k', '2k'];
}
const lmCache = new Map<string, Promise<THREE.Texture>>();
function loadLm(res: LmRes): Promise<THREE.Texture> {
  if (!lmCache.has(res)) {
    lmCache.set(res, new Promise((ok, bad) => new THREE.TextureLoader().load(LM[res], (t) => {
      t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; ok(t);
    }, undefined, bad)));
  }
  return lmCache.get(res)!;
}

export function BakedOffice({ model, screens, dash, lit, alert }: {
  model: OfficeModel; screens: THREE.Texture[]; dash: Dashboards | null; lit: (room: string) => boolean; alert: (room: string) => boolean;
}) {
  const quality = useWorld((s) => s.quality);
  // scherpe lightmap: probeer de gewenste resolutie, anders een kleinere
  useEffect(() => {
    let on = true;
    (async () => {
      for (const r of wantRes(quality)) {
        try { const t = await loadLm(r); if (!on) return; for (const m of model.lightmapped) { m.emissiveMap = t; m.needsUpdate = true; } return; } catch { /* volgende */ }
      }
    })();
    return () => { on = false; };
  }, [model, quality]);

  // schermen: wandschermen live (per afdeling), de rest met de algemene dashboards
  useMemo(() => {
    const flipped = new Map<THREE.Texture, THREE.Texture>();
    const gen = (t: THREE.Texture) => { let c = flipped.get(t); if (!c) { c = t.clone(); c.flipY = false; c.needsUpdate = true; flipped.set(t, c); } return c; };
    model.screens.forEach(({ mesh, kind, room }, i) => {
      mesh.geometry.computeBoundingBox(); const bb = mesh.geometry.boundingBox!; const sz = new THREE.Vector3(); bb.getSize(sz);
      const aspect = Math.max(sz.x, sz.z) / Math.max(0.01, sz.y);
      let map: THREE.Texture;
      if (dash && kind === 'w' && room !== 'hub' && room !== 'gang') map = dash.get(room, aspect);
      else if (dash && kind === 'm') map = dash.get('crisis', aspect);
      else if (dash && kind === 't' && room === 'thumbnail') map = dash.get('thumbnail', aspect);
      else map = gen(kind === 't' ? screens[5] : screens[(i * 7) % screens.length]);
      mesh.material = new THREE.MeshBasicMaterial({ map, toneMapped: false, color: new THREE.Color(kind === 'w' || kind === 'm' ? 0.95 : 0.85, kind === 'w' || kind === 'm' ? 0.95 : 0.85, kind === 'w' || kind === 'm' ? 0.95 : 0.85) });
    });
  }, [model, screens, dash]);

  const lm = useRef(-1);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    let i = 0;
    for (const [room, mats] of Object.entries(model.neon)) {
      i++;
      // neon kleurt heel licht mee in de tijd; bij het feestthema draait hij door de regenboog
      const shift = sky.feest ? (t * 0.09 + i * 0.13) % 1 : Math.sin(t * 0.22 + i * 1.7) * 0.022;
      for (const m of mats) { const c = m.userData.hsl as { h: number; s: number; l: number } | undefined; if (c) m.emissive.setHSL((c.h + shift + 1) % 1, sky.feest ? 1 : c.s, c.l); }
      if (room === 'hub') continue;
      const k = (alert(room) ? 1.0 + Math.max(0, Math.sin(t * 5)) * 0.9 : 1) * (lit(room) ? 1.45 : 1);
      for (const m of mats) m.emissiveIntensity = (m.userData.base as number) * k;
    }
    // overdag een tikje lichter binnen
    const want = Math.round((0.97 + sky.day * 0.09) * 100) / 100;
    if (want !== lm.current) { lm.current = want; for (const m of model.lightmapped) m.emissiveIntensity = want; }
  });
  return <primitive object={model.scene} />;
}
