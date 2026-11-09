/**
 * RONDLOPEN (niels 2026-11-06): "een knopje rechtsboven ... dat je kan rondlopen in het kantoor. Gewoon in
 * first person weergave. En elke keer als je een kamer inkomt, krijg je een melding of je het menu wil openen."
 *
 * Eerste-persoonscamera op ooghoogte. Computer: WASD of de pijltjes lopen, Shift loopt sneller, de muis kijkt
 * rond met pointer lock na een klik; weigert de browser dat (bv. in de claude.ai-iframe), dan kijk je rond
 * door te slepen met de muisknop ingedrukt. Telefoon: joystick linksonder (WalkHud) en vegen op de rest.
 *
 * Botsen gaat via de looproutekaart (nav.ts). Die is in Blender al ~0,18 m rond elk obstakel opgedikt (een halve
 * medewerker), dus het middelpunt komt nooit op een zwarte cel: dat is het harde lichaam. Een vaste straal van
 * 0,25 m daarbovenop sluit de smalle doorgang boven aan de trap (tussen leuning en afdelingshoek, 10 cm vrij op
 * de kaart) af, en dan kom je vanaf de ingang nergens meer. Daarom duwt een zachte kracht je tijdens het lopen
 * zijwaarts tot ~0,28 m van wanden waar dat past, en in smalle doorgangen naar het midden. Lukt een stap niet,
 * dan glijd je langs de wand. Zonder kaart loop je zonder botsen, binnen de rand van het kantoor.
 * Zolang je loopt staan de orbit-besturing en CameraRig stil; de terugvlucht doet CameraRig (NeonOffice.tsx).
 *
 * Verdiepingen (niels 2026-11-07, floors.ts): het podium ligt sinds 9 nov op de hoogte van de afdelingen, zodat je
 * vanaf de balie zo de kamers in loopt. De zijtrap op het podium is een smalle looplijn die je alleen aan de uiteinden op- en afloopt: onder
 * vanaf het podium, boven vanaf de bovenverdieping (eigen looproutekaart, buildNav1). Halverwege de trap wisselt
 * het beeld naar de bovenverdieping. Het knopje rechts in het midden brengt je in één vloeiende beweging naar de
 * andere verdieping.
 */
import { useEffect, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { loadNav, isFree, nearestFree, type Nav } from './nav';
import { Y1, groundY, stairUV, stairRampY, STAIR_HALF, ARRIVE_UP, ARRIVE_DOWN, useFloor, type Floor } from './floors';
import { buildNav1 } from './upstairs';
import { roomAt } from './BakedOffice';
import { ROOMS, R_IN, R_OUT, SPAN, type RoomId } from './rooms';
import { useWorld, reducedMotion } from './useWorld';
import { useGame } from '../store/useGame';
import { useWalk, walkInput, walkLock } from './walkState';
import type { WorldMode } from './NeonOffice';

export const EYE = 1.6; // ooghoogte (de medewerkers zijn ~1,6 m)
export const WALK_NEAR = 0.08; // dichtbij een wand niet door het beeld heen kijken
/** verticale kijkhoek tijdens het lopen: breed genoeg, ook op een staande telefoon */
export const walkFov = (aspect: number) => THREE.MathUtils.clamp(THREE.MathUtils.radToDeg(2 * Math.atan(1.04 / Math.max(0.3, aspect))), 62, 88);
export const angDiff = (a: number, b: number) => { const T = Math.PI * 2; return ((((b - a + Math.PI) % T) + T) % T) - Math.PI; };
/** draaihoek en kijkhoek van een kijkrichting (camera kijkt bij 0 naar -z) */
export const lookAngles = (dir: THREE.Vector3) => ({ yaw: Math.atan2(-dir.x, -dir.z), pitch: Math.asin(THREE.MathUtils.clamp(dir.y, -1, 1)) });

const START: [number, number] = [0, 12.4]; // ingang vooraan, op de loopbrug naar de receptie
const SPEED = 2.2, RUN = 4.3; // m/s
const ACC = 8, BRAKE = 11; // optrekken en afremmen (1/s)
const STEP = 0.025; // botsen in stapjes van een halve cel
const SOFT = 0.13; // zachte afstand tot het midden van de dichtstbijzijnde zwarte cel (≈0,1 m bovenop de opdikking)
const FAN = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.35, 1.48].map((a) => [Math.cos(a), Math.sin(a)] as const); // langs de wand glijden (bijna recht ertegenaan: langzaam)
const SENS = { lock: 0.0022, drag: 0.0045, touch: 0.006 }; // rad per pixel
const MAXPITCH = 1.3;
const BOUND = R_OUT - 0.3; // zonder kaart: binnen de rand van het kantoor blijven
const ROOM_IDS = new Set<string>(ROOMS.map((r) => r.id));
const EDGE_IN = 0.5, EDGE_OUT = 0.25; // zo ver (m) moet je binnen de zijgrenzen van een afdeling staan om erin te tellen
/** afstand (m) tot de dichtstbijzijnde zijgrens van de taartpunt waar je in staat (zelfde indeling als roomAt).
 *  De gangen naast de trap en de kieren tussen twee afdelingen liggen precies op zo'n grens: daar vraagt hij niets. */
const edgeDist = (x: number, z: number) => {
  const a = Math.atan2(x, z); const slot = Math.round((((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2)) / SPAN) % 10;
  return Math.hypot(x, z) * Math.sin(Math.max(0, SPAN / 2 - Math.abs(angDiff(slot * SPAN, a))));
};
/** op de looplijn van de trap (stairUV) */
const inStair = ([u, d]: [number, number]) => u >= -0.03 && u <= 1.04 && Math.abs(d) < STAIR_HALF;
const STAIR_END = 0.15; // zo ver (u) van een uiteinde mag je de trap op- of aflopen
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const coarse = () => typeof window !== 'undefined' && !!window.matchMedia?.('(pointer: coarse)').matches;

/** afstand (m) van elk celmidden tot het midden van de dichtstbijzijnde zwarte cel (twee keer over het raster) */
function distField(nav: Nav): Float32Array {
  const n = nav.n, f = nav.free, d = new Float32Array(n * n), D = Math.SQRT2;
  for (let i = 0; i < n * n; i++) d[i] = f[i] ? 1e6 : 0;
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const id = j * n + i; let v = d[id]; if (!v) continue;
    if (i > 0) v = Math.min(v, d[id - 1] + 1);
    if (j > 0) { v = Math.min(v, d[id - n] + 1); if (i > 0) v = Math.min(v, d[id - n - 1] + D); if (i < n - 1) v = Math.min(v, d[id - n + 1] + D); }
    d[id] = v;
  }
  for (let j = n - 1; j >= 0; j--) for (let i = n - 1; i >= 0; i--) {
    const id = j * n + i; let v = d[id]; if (!v) continue;
    if (i < n - 1) v = Math.min(v, d[id + 1] + 1);
    if (j < n - 1) { v = Math.min(v, d[id + n] + 1); if (i < n - 1) v = Math.min(v, d[id + n + 1] + D); if (i > 0) v = Math.min(v, d[id + n - 1] + D); }
    d[id] = v;
  }
  for (let i = 0; i < n * n; i++) d[i] *= nav.meta.res;
  return d;
}
/** zelfde afstand op een willekeurige plek (bilineair tussen de celmiddens) */
function distAt(nav: Nav, d: Float32Array, x: number, z: number) {
  const n = nav.n, u = (x + nav.meta.half) / nav.meta.res - 0.5, v = (z + nav.meta.half) / nav.meta.res - 0.5;
  const i = Math.floor(u), j = Math.floor(v); if (i < 0 || j < 0 || i >= n - 1 || j >= n - 1) return 0;
  const fx = u - i, fz = v - j, id = j * n + i;
  return (d[id] * (1 - fx) + d[id + 1] * fx) * (1 - fz) + (d[id + n] * (1 - fx) + d[id + n + 1] * fx) * fz;
}

export function WalkController({ mode }: { mode: WorldMode }) {
  const { camera, gl, size, setEvents } = useThree();
  const cam = camera as THREE.PerspectiveCamera;
  const walk = useWorld((s) => s.walk);
  const setWalk = useWorld((s) => s.setWalk);
  const nav = useRef<Nav | null>(null);
  const nav1 = useRef<Nav | null>(null);
  const field = useRef<Float32Array | null>(null);
  const field1 = useRef<Float32Array | null>(null);
  const keys = useRef(new Set<string>());
  const look = useRef({ x: 0, y: 0 });
  const st = useRef({
    phase: 'off' as 'off' | 'in' | 'on', t: 0,
    x: START[0], z: START[1], yaw: 0, pitch: 0, vx: 0, vz: 0, side: 1, bob: 0, bobAmt: 0,
    from: { p: new THREE.Vector3(), yaw: 0, pitch: 0, fov: 40, near: 0.5 },
    room: null as RoomId | null, roomT: 0,
    fl: 0 as Floor, stair: false, y: 0, // verdieping, op de trap, vloerhoogte onder je voeten (vloeiend)
    lift: null as null | { t: number; to: Floor; p0: THREE.Vector3; yaw0: number; pitch0: number; x: number; z: number; yaw: number },
  });
  const eul = useRef(new THREE.Euler(0, 0, 0, 'YXZ'));
  const stepRef = useRef<(dt: number) => void>(() => {});

  // looproutekaart (al geladen voor de medewerkers); de afstandskaart pas bij het eerste rondje
  useEffect(() => { let on = true; loadNav().then((n) => { if (on) nav.current = n; }); return () => { on = false; }; }, []);
  const navOf = (fl: Floor) => { if (fl === 1 && !nav1.current) nav1.current = buildNav1(); return fl === 1 ? nav1.current : nav.current; };
  const fieldOf = (fl: Floor) => {
    const n = navOf(fl); if (!n) return null;
    const f = fl === 1 ? field1 : field; if (!f.current) f.current = distField(n); return f.current;
  };
  // de knop mag zichtbaar zijn zolang het 3D-kantoor er staat; valt het weg, dan stopt het rondlopen
  useEffect(() => { useWalk.setState({ ready: true }); return () => { useWalk.setState({ ready: false }); useWorld.getState().setWalk(false); }; }, []);
  // een andere pagina openen stopt het rondlopen
  useEffect(() => { if (mode !== 'home') setWalk(false); }, [mode, setWalk]);

  // alleen bij lokaal testen: stand opvragen en verplaatsen
  useEffect(() => {
    if (window.location?.hostname !== 'localhost') return;
    (window as unknown as { __dmWalk: unknown }).__dmWalk = {
      state: () => { const s = st.current; const n = navOf(s.fl); return { phase: s.phase, x: s.x, z: s.z, y: s.y, fl: s.fl, stair: s.stair, yaw: s.yaw, pitch: s.pitch, vx: s.vx, vz: s.vz, room: s.room, nav: !!n, free: n ? isFree(n, s.x, s.z) : null }; },
      teleport: (x: number, z: number, yaw?: number, fl?: Floor) => { const s = st.current; s.x = x; s.z = z; if (yaw != null) s.yaw = yaw; if (fl != null) { s.fl = fl; s.stair = false; useFloor.getState().setFloor(fl); } s.vx = s.vz = 0; },
      face: (yaw: number, pitch?: number) => { const s = st.current; s.yaw = yaw; if (pitch != null) s.pitch = pitch; }, // draaien zonder af te remmen
      isFree: (x: number, z: number, fl: Floor = 0) => { const n = navOf(fl); return n ? isFree(n, x, z) : null; },
      clear: (x: number, z: number, fl: Floor = 0) => { const n = navOf(fl); const f = fieldOf(fl); return n && f ? distAt(n, f, x, z) : null; },
      // dezelfde stappen als in beeld, zonder te tekenen (de testbrowser tekent maar een paar beelden per minuut)
      sim: (frames: number, dt = 1 / 60, held: string[] = []) => {
        if (st.current.phase !== 'on') return false;
        const K = keys.current; const prev = [...K]; K.clear(); held.forEach((k) => K.add(k));
        for (let i = 0; i < frames; i++) stepRef.current(dt);
        K.clear(); prev.forEach((k) => K.add(k)); return true;
      },
      page: (id: Parameters<ReturnType<typeof useGame.getState>['setPage']>[0]) => useGame.getState().setPage(id),
    };
  }, []);

  // knopje "verdieping hoger/lager" tijdens het rondlopen (WalkHud): Walk.tsx doet de overgang
  useEffect(() => useFloor.subscribe((f, prev) => {
    if (f.req === prev.req) return;
    const s = st.current; if (s.phase !== 'on' || s.lift) return;
    const to = f.want; if (to === s.fl && !s.stair) return;
    const a = to === 1 ? ARRIVE_UP : ARRIVE_DOWN; const n = navOf(to); const p = (n && nearestFree(n, a[0], a[1])) || a;
    const la = lookAngles(cam.getWorldDirection(new THREE.Vector3()));
    s.lift = { t: 0, to, p0: cam.position.clone(), yaw0: la.yaw, pitch0: la.pitch, x: p[0], z: p[1], yaw: to === 1 ? Math.atan2(p[0], p[1]) : Math.PI };
    s.vx = s.vz = 0; s.room = null; useWalk.getState().enter(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }), []);

  const freeOn = (fl: Floor, x: number, z: number) => { const n = navOf(fl); return n ? isFree(n, x, z) : fl === 0 && Math.hypot(x, z) <= BOUND; };
  /**
   * Mag je hierheen? Op de trap blijf je op de looplijn en stap je er alleen aan een uiteinde af (op de verdieping
   * van dat uiteinde); van een verdieping stap je de trap alleen aan jouw uiteinde op. Zet s.stair en s.fl.
   */
  const free = (x: number, z: number) => {
    const s = st.current; const b = stairUV(x, z);
    if (s.stair) {
      if (inStair(b)) { s.fl = b[0] > 0.5 ? 1 : 0; return true; }
      if (b[0] < STAIR_END && freeOn(0, x, z)) { s.stair = false; s.fl = 0; return true; }
      if (b[0] > 1 - STAIR_END && freeOn(1, x, z)) { s.stair = false; s.fl = 1; return true; }
      return false;
    }
    if (inStair(b) && (s.fl === 0 ? b[0] < STAIR_END : b[0] > 1 - STAIR_END)) { s.stair = true; return true; }
    return freeOn(s.fl, x, z);
  };

  /** verplaatsen met botsen: in halve cellen; lukt een stap niet, dan draaien we hem steeds verder langs de wand (en korter) */
  const move = (dx: number, dz: number) => {
    const s = st.current; const L = Math.hypot(dx, dz); if (L < 1e-5) return;
    const steps = Math.ceil(L / STEP); const sx = dx / steps, sz = dz / steps;
    for (let i = 0; i < steps; i++) {
      if (free(s.x + sx, s.z + sz)) { s.x += sx; s.z += sz; continue; }
      let ok = false;
      for (const [c, sn] of FAN) {
        for (const sg of [s.side, -s.side]) {
          const ax = (sx * c - sz * sn * sg) * c, az = (sx * sn * sg + sz * c) * c;
          if (free(s.x + ax, s.z + az)) { s.x += ax; s.z += az; s.side = sg; ok = true; break; }
        }
        if (ok) break;
      }
      if (!ok) break; // in een hoek: blijven staan
    }
  };

  /** zachte afstand tot wanden, alleen dwars op de looprichting (remt dus nooit af, trekt je wel netjes door deuren) */
  const soft = (dt: number) => {
    const s = st.current; if (s.stair) return;
    const n = navOf(s.fl); const d = fieldOf(s.fl); if (!n || !d) return;
    const sp = Math.hypot(s.vx, s.vz); if (sp < 0.25) return;
    const here = distAt(n, d, s.x, s.z); if (here >= SOFT) return;
    const h = 0.03;
    let gx = (distAt(n, d, s.x + h, s.z) - distAt(n, d, s.x - h, s.z)) / (2 * h);
    let gz = (distAt(n, d, s.x, s.z + h) - distAt(n, d, s.x, s.z - h)) / (2 * h);
    const ux = s.vx / sp, uz = s.vz / sp; const along = gx * ux + gz * uz; gx -= along * ux; gz -= along * uz;
    const k = (SOFT - here) * Math.min(0.6, dt * 9) * Math.min(1, sp / SPEED);
    const nx = s.x + gx * k, nz = s.z + gz * k;
    if (free(nx, nz)) { s.x = nx; s.z = nz; }
  };

  // ---- rondlopen aan: invliegen naar de ingang en de bediening aanzetten ----
  useEffect(() => {
    if (!walk) return;
    const s = st.current; const el = gl.domElement;
    // begin waar je kijkt: beneden bij de ingang, boven net voorbij de trap
    const fl0 = useFloor.getState().floor; s.fl = fl0; s.stair = false; s.lift = null;
    const n0 = navOf(fl0); fieldOf(fl0);
    const want = fl0 === 1 ? ARRIVE_UP : START;
    const p = (n0 && nearestFree(n0, want[0], want[1])) || want;
    s.x = p[0]; s.z = p[1]; s.yaw = Math.atan2(s.x, s.z); s.pitch = 0.07; s.vx = s.vz = 0; s.bob = 0; s.bobAmt = 0; s.room = null; s.roomT = 0;
    s.y = fl0 === 1 ? Y1 : groundY(s.x, s.z) ?? 0;
    const a = lookAngles(cam.getWorldDirection(new THREE.Vector3()));
    s.from = { p: cam.position.clone(), yaw: a.yaw, pitch: a.pitch, fov: cam.fov, near: cam.near };
    s.phase = 'in'; s.t = reducedMotion() ? 1 : 0;
    keys.current.clear(); look.current.x = look.current.y = 0; walkInput.jx = walkInput.jy = 0;
    useWalk.setState({ room: null, ask: null, locked: false, touch: coarse() });
    setEvents({ enabled: false }); // geen klikken op afdelingen, bureaus of medewerkers en geen hover-labels
    document.body.style.cursor = 'auto';
    (document.activeElement as HTMLElement | null)?.blur?.(); // Enter of spatie mag geen knop meer indrukken

    // ---- toetsen ----
    const MOVE = new Set(['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ShiftLeft', 'ShiftRight']);
    const typing = (e: Event) => !!(e.target as HTMLElement | null)?.closest?.('input,textarea,select,[contenteditable="true"]');
    const down = (e: KeyboardEvent) => { if (typing(e) || e.ctrlKey || e.metaKey || e.altKey || !MOVE.has(e.code)) return; keys.current.add(e.code); e.preventDefault(); };
    const up = (e: KeyboardEvent) => { keys.current.delete(e.code); };
    // ---- kijken: muis met pointer lock (anders slepen), aanraken: vegen ----
    const drag = new Map<number, { x: number; y: number; touch: boolean }>();
    const locked = () => document.pointerLockElement === el;
    const refuse = () => { if (!useWalk.getState().noLock) useWalk.setState({ noLock: true }); };
    const turn = (dx: number, dy: number, k: number) => { look.current.x += dx * k; look.current.y += dy * k; };
    const pdown = (e: PointerEvent) => {
      const touch = e.pointerType !== 'mouse';
      if (useWalk.getState().touch !== touch) useWalk.setState({ touch });
      if (!touch && !locked() && !useWalk.getState().noLock && st.current.phase === 'on' && !walkLock.on) {
        try { const r = el.requestPointerLock() as unknown; (r as Promise<void> | undefined)?.catch?.(refuse); } catch { refuse(); }
      }
      drag.set(e.pointerId, { x: e.clientX, y: e.clientY, touch });
      try { el.setPointerCapture(e.pointerId); } catch { /* */ }
    };
    const JUMP = 300; // px in één beweging: een sprong van de browser (bv. net na het vastzetten van de muis), geen echte draai
    const pmove = (e: PointerEvent) => {
      const d = drag.get(e.pointerId); if (!d) return;
      if (!d.touch && locked()) return; // met pointer lock kijkt mousemove hieronder
      const dx = e.clientX - d.x, dy = e.clientY - d.y; d.x = e.clientX; d.y = e.clientY;
      if (Math.abs(dx) < JUMP && Math.abs(dy) < JUMP) turn(dx, dy, d.touch ? SENS.touch : SENS.drag);
    };
    const pup = (e: PointerEvent) => { drag.delete(e.pointerId); };
    let fresh = false; // de eerste beweging na het vastzetten slaan we over (vaak een sprong)
    const mmove = (e: MouseEvent) => {
      if (!locked()) return;
      if (fresh) { fresh = false; return; }
      if (Math.abs(e.movementX) < JUMP && Math.abs(e.movementY) < JUMP) turn(e.movementX, e.movementY, SENS.lock);
    };
    let quit = 0;
    const lockChange = () => {
      const on = locked(); useWalk.setState({ locked: on });
      if (on) { drag.clear(); fresh = true; return; }
      // Esc maakt eerst de muis los en de browser geeft die toets dan niet door: houdt de pagina de focus, dan stoppen we ook
      window.clearTimeout(quit);
      quit = window.setTimeout(() => { if (useWorld.getState().walk && !locked() && !walkLock.on && document.hasFocus() && document.visibilityState === 'visible') useWorld.getState().setWalk(false); }, 150);
    };
    const blur = () => { keys.current.clear(); drag.clear(); };
    const noMenu = (e: MouseEvent) => e.preventDefault();
    window.addEventListener('keydown', down); window.addEventListener('keyup', up); window.addEventListener('blur', blur);
    el.addEventListener('pointerdown', pdown); el.addEventListener('pointermove', pmove); el.addEventListener('pointerup', pup); el.addEventListener('pointercancel', pup);
    el.addEventListener('contextmenu', noMenu);
    document.addEventListener('mousemove', mmove);
    document.addEventListener('pointerlockchange', lockChange); document.addEventListener('pointerlockerror', refuse);
    return () => {
      window.removeEventListener('keydown', down); window.removeEventListener('keyup', up); window.removeEventListener('blur', blur);
      el.removeEventListener('pointerdown', pdown); el.removeEventListener('pointermove', pmove); el.removeEventListener('pointerup', pup); el.removeEventListener('pointercancel', pup);
      el.removeEventListener('contextmenu', noMenu);
      document.removeEventListener('mousemove', mmove);
      document.removeEventListener('pointerlockchange', lockChange); document.removeEventListener('pointerlockerror', refuse);
      window.clearTimeout(quit);
      if (locked()) { try { document.exitPointerLock(); } catch { /* */ } }
      keys.current.clear(); walkInput.jx = walkInput.jy = 0;
      st.current.phase = 'off';
      setEvents({ enabled: true });
      useWalk.setState({ room: null, ask: null, locked: false });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [walk]);

  /** één stap lopen: kijken, versnellen, botsen, deinen en bijhouden in welke afdeling je staat */
  const step = (dt: number) => {
    const s = st.current; const n = navOf(s.fl);
    if (n) fieldOf(s.fl);
    // kaart kwam later binnen, of je staat op een geblokkeerde plek: naar de dichtstbijzijnde vrije plek
    if (n && !s.stair && !isFree(n, s.x, s.z)) { const q = nearestFree(n, s.x, s.z); if (q) { s.x = q[0]; s.z = q[1]; } }
    // praten of gamen: niet lopen en niet rondkijken
    if (walkLock.on) { keys.current.clear(); look.current.x = look.current.y = 0; walkInput.jx = walkInput.jy = 0; }
    // ---- kijken ----
    s.yaw = angDiff(0, s.yaw - look.current.x); s.pitch = THREE.MathUtils.clamp(s.pitch - look.current.y, -MAXPITCH, MAXPITCH); look.current.x = look.current.y = 0;
    // ---- lopen (vooruit = waar je naartoe kijkt) ----
    const K = keys.current;
    let fwd = (K.has('KeyW') || K.has('ArrowUp') ? 1 : 0) - (K.has('KeyS') || K.has('ArrowDown') ? 1 : 0);
    let side = (K.has('KeyD') || K.has('ArrowRight') ? 1 : 0) - (K.has('KeyA') || K.has('ArrowLeft') ? 1 : 0);
    let sp = K.has('ShiftLeft') || K.has('ShiftRight') ? RUN : SPEED;
    const jl = Math.hypot(walkInput.jx, walkInput.jy);
    if (jl > 0.15) { const g = Math.min(1, (jl - 0.15) / 0.75) / jl; fwd += walkInput.jy * g; side += walkInput.jx * g; if (jl > 0.96) sp = Math.max(sp, SPEED * 1.35); }
    const L = Math.hypot(fwd, side); if (L > 1) { fwd /= L; side /= L; }
    const sn = Math.sin(s.yaw), cs = Math.cos(s.yaw);
    const tvx = (-sn * fwd + cs * side) * sp, tvz = (-cs * fwd - sn * side) * sp;
    const a = 1 - Math.exp(-dt * (tvx * tvx + tvz * tvz > s.vx * s.vx + s.vz * s.vz ? ACC : BRAKE));
    s.vx += (tvx - s.vx) * a; s.vz += (tvz - s.vz) * a;
    if (!fwd && !side && s.vx * s.vx + s.vz * s.vz < 1e-4) s.vx = s.vz = 0;
    const ox = s.x, oz = s.z;
    move(s.vx * dt, s.vz * dt);
    soft(dt);
    if (!n && !s.stair) { const r = Math.hypot(s.x, s.z); if (r > BOUND) { s.x *= BOUND / r; s.z *= BOUND / r; } }
    // ---- hoogte: podium, trap vooraan, zijtrap of bovenverdieping; halverwege de trap wisselt het beeld ----
    const fy = s.stair ? stairRampY(s.z) : s.fl === 1 ? Y1 : groundY(s.x, s.z) ?? 0;
    s.y += (fy - s.y) * Math.min(1, dt * (s.stair ? 14 : 9));
    const F = useFloor.getState(); const u = s.stair ? stairUV(s.x, s.z)[0] : s.fl;
    const view: Floor = s.stair ? (u > 0.36 ? 1 : u < 0.28 ? 0 : F.floor) : s.fl;
    if (view !== F.floor) F.setFloor(view);
    // ---- hoofd deint een beetje mee ----
    const moved = Math.hypot(s.x - ox, s.z - oz);
    s.bobAmt += (Math.min(1, moved / dt / SPEED) - s.bobAmt) * Math.min(1, dt * 6);
    s.bob += moved * (Math.PI / 0.7); // een stap ≈ 0,7 m
    // ---- in welke afdeling sta je? (gangen, de ingang en de receptie tellen niet) ----
    s.roomT -= dt;
    if (s.roomT <= 0) {
      s.roomT = 0.1;
      const id = roomAt(s.x, s.z); const r = Math.hypot(s.x, s.z); const e = edgeDist(s.x, s.z);
      let cur = s.room;
      if (s.fl === 1 || s.stair) cur = null; // boven en op de trap zijn geen afdelingen
      else if (cur && (id !== cur || r < R_IN + 0.05 || r > R_OUT || e < EDGE_OUT)) cur = null; // de afdeling uit gelopen
      if (!cur && s.fl === 0 && !s.stair && ROOM_IDS.has(id) && r > R_IN + 0.3 && r < R_OUT - 0.1 && e > EDGE_IN) cur = id as RoomId; // binnen (voorbij de deur)
      if (cur !== s.room) { s.room = cur; useWalk.getState().enter(cur); }
    }
  };
  stepRef.current = step;

  useFrame((_, rawDt) => {
    const s = st.current;
    if (s.phase === 'off') return;
    const dt = Math.min(rawDt, 0.1);
    const fov = walkFov(size.width / Math.max(1, size.height));
    if (s.phase === 'in') {
      // vlucht van het overzicht naar de ingang, met een boogje over het kantoor heen
      s.t = Math.min(1, s.t + dt / 1.5);
      const k = easeInOut(s.t); const f = s.from;
      cam.position.set(f.p.x + (s.x - f.p.x) * k, f.p.y + (s.y + EYE - f.p.y) * k + Math.sin(Math.PI * k) * 6, f.p.z + (s.z - f.p.z) * k);
      eul.current.set(f.pitch + (s.pitch - f.pitch) * k, f.yaw + angDiff(f.yaw, s.yaw) * k, 0, 'YXZ'); cam.quaternion.setFromEuler(eul.current);
      cam.fov = f.fov + (fov - f.fov) * k; cam.near = f.near + (WALK_NEAR - f.near) * k; cam.updateProjectionMatrix();
      look.current.x = look.current.y = 0;
      if (s.t >= 1) s.phase = 'on';
      return;
    }
    // ---- knopje "verdieping hoger/lager": in één beweging naar de andere verdieping ----
    const lf = s.lift;
    if (lf) {
      lf.t = Math.min(1, lf.t + dt / (reducedMotion() ? 0.01 : 1.25));
      const k = easeInOut(lf.t); const ty = (lf.to === 1 ? Y1 : groundY(lf.x, lf.z) ?? 0) + EYE;
      cam.position.set(lf.p0.x + (lf.x - lf.p0.x) * k, lf.p0.y + (ty - lf.p0.y) * k + Math.sin(Math.PI * k) * 1.2, lf.p0.z + (lf.z - lf.p0.z) * k);
      eul.current.set(lf.pitch0 + (0.04 - lf.pitch0) * k, lf.yaw0 + angDiff(lf.yaw0, lf.yaw) * k, 0, 'YXZ'); cam.quaternion.setFromEuler(eul.current);
      if (k > 0.5 && useFloor.getState().floor !== lf.to) useFloor.getState().setFloor(lf.to);
      look.current.x = look.current.y = 0;
      if (lf.t >= 1) { s.x = lf.x; s.z = lf.z; s.yaw = lf.yaw; s.pitch = 0.04; s.fl = lf.to; s.stair = false; s.y = ty - EYE; s.vx = s.vz = 0; s.lift = null; }
      return;
    }
    step(dt);
    // ---- camera op ooghoogte; het hoofd deint niet bij "minder beweging" ----
    const rm = reducedMotion(); const sn = Math.sin(s.yaw), cs = Math.cos(s.yaw);
    const by = rm ? 0 : Math.sin(s.bob * 2) * 0.026 * s.bobAmt;
    const bx = rm ? 0 : Math.sin(s.bob) * 0.012 * s.bobAmt;
    cam.position.set(s.x + cs * bx, s.y + EYE + by, s.z - sn * bx);
    eul.current.set(s.pitch, s.yaw, 0, 'YXZ'); cam.quaternion.setFromEuler(eul.current);
    if (Math.abs(cam.fov - fov) > 0.01 || cam.near !== WALK_NEAR) { cam.fov = fov; cam.near = WALK_NEAR; cam.updateProjectionMatrix(); }
  });
  return null;
}
