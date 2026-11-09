/**
 * HET NEON-KANTOOR v2 (niels 2026-11-06: "moet lijken op het referentiebeeld").
 * Achthoekige ring van glazen afdelingen rond een ronde receptie met een glazen
 * hologramzuil, DRIFTMARK HQ-neonbord en het hoofdpersonage achter de balie.
 * Vooraan een trap naar de ingang. Spiegelende vloer, nachtstad met bokeh erachter,
 * neonranden per afdeling en grote lichtgevende borden.
 * Eén blijvende scène achter de hele HQ; de camera vliegt naar een afdeling bij klik,
 * maakt een intro van 1 s bij openen en een kleine beweging bij elke paginawissel.
 */
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Billboard, Environment, Lightformer, MeshReflectorMaterial, OrbitControls, PerformanceMonitor, PerspectiveCamera } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import type { OrbitControls as OC } from 'three-stdlib';
import { useShallow } from 'zustand/react/shallow';
import { useGame } from '../store/useGame';
import { useLive } from '../services/live';
import { Box, Chair, Bookshelf, MicStand, Easel, Sofa, MeetingTable, ServerRack } from '../components/office/Furniture';
import { Mascot } from '../components/office/DriftmarkDecor';
import { ROOMS, STATUS, threadsPerRoom, statusOf, SPAN, R_HUB, R_IN, R_OUT, R_BASE, slotAngle, roomCenter, roomById, type RoomDef, type RoomId } from './rooms';
import { useWorld, reducedMotion, dprFor, isPhone, PERF_DPR } from './useWorld';
import { useOffice, BakedOffice, type OfficeModel } from './BakedOffice';
import { useOfficeLoad } from './loadState';
import { Crew } from './crew';
import { staffFor, gameStaff } from './staff';
import { Pipeline, handoffsFor } from './pipeline';
import { Dashboards } from './dashboards';
import { alarmsFrom } from './alarms';
import { mergePunten } from '../data/verbeter';
import { Sky, Drone, Confetti, Beacon, Snow, Disco, VoiceProps, PostIts } from './extras';
import { setAmbience } from './sound';
import { WalkController, lookAngles } from './Walk';
import { selectRoom } from './select';
import { City } from './city';
import { Upstairs, Plafond } from './Upstairs';
import { CastProps } from './castProps';
import { useFloor, Y1, HUB_Y } from './floors';
/** zoveel lager ligt het podium sinds 9 nov (was 0,5 m hoog) */
const DROP = 0.5 - HUB_Y;

type V3 = [number, number, number];
export type WorldMode = 'home' | 'studio' | 'panel';
const ease = (t: number) => 1 - Math.pow(1 - t, 4); // ~ cubic-bezier(0.22, 1, 0.36, 1)
const GAPA = 0.035; // hoekspleet tussen afdelingen (rad)
const polar = (r: number, a: number, y = 0): V3 => [Math.sin(a) * r, y, Math.cos(a) * r];
/** plek in een afdeling: u langs de ring, v naar buiten (zelfde assen als office_build.py) */
const atRoom = (r: RoomDef, u: number, v: number, y = 0): V3 => { const a = slotAngle(r.slot); const rad = (R_IN + R_OUT) / 2 + v; return polar(rad, a + u / rad, y); };

/* ================= textures ================= */
function canvasTex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d')!);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 16; return t;
}
const rr = (g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };

/** Schermtexturen met dashboards (grafiek, balken, video, golf). */
function useScreens() {
  return useMemo(() => {
    const kinds = ['chart', 'bars', 'video', 'wave', 'grid', 'thumbs'] as const;
    const hues = ['#20D9FF', '#FF7A24', '#A855F7', '#21D6A0', '#FF4DB8', '#398CFF'];
    return kinds.map((k, i) => canvasTex(256, 160, (g) => {
      const c = hues[i];
      const bg = g.createLinearGradient(0, 0, 0, 160); bg.addColorStop(0, '#0b1636'); bg.addColorStop(1, '#060b1e');
      g.fillStyle = bg; g.fillRect(0, 0, 256, 160);
      g.fillStyle = c; g.globalAlpha = 0.9; g.fillRect(10, 10, 70, 8); g.globalAlpha = 0.35; g.fillRect(10, 24, 110, 5);
      g.globalAlpha = 1; g.strokeStyle = c; g.lineWidth = 4; g.shadowColor = c; g.shadowBlur = 10;
      if (k === 'chart') { g.beginPath(); for (let x = 0; x <= 236; x += 12) g.lineTo(10 + x, 130 - (x / 236) * 70 - Math.sin(x / 18) * 14); g.stroke(); }
      if (k === 'bars') for (let j = 0; j < 9; j++) { g.fillStyle = j % 3 ? c : '#FFB070'; const h = 20 + ((j * 37) % 80); g.fillRect(14 + j * 26, 145 - h, 16, h); }
      if (k === 'video') { g.fillStyle = '#1b2a5a'; g.fillRect(20, 40, 216, 100); g.fillStyle = c; g.beginPath(); g.moveTo(112, 66); g.lineTo(150, 90); g.lineTo(112, 114); g.fill(); }
      if (k === 'wave') { g.beginPath(); for (let x = 0; x <= 236; x += 4) g.lineTo(10 + x, 95 + Math.sin(x / 6) * Math.sin(x / 40) * 38); g.stroke(); }
      if (k === 'grid') for (let j = 0; j < 12; j++) { g.fillStyle = j % 4 === 1 ? '#FF7A24' : c; g.globalAlpha = 0.35 + (j % 3) * 0.25; g.fillRect(14 + (j % 4) * 58, 42 + Math.floor(j / 4) * 38, 50, 30); }
      if (k === 'thumbs') for (let j = 0; j < 6; j++) { const gg = g.createLinearGradient(0, 0, 70, 0); gg.addColorStop(0, hues[j]); gg.addColorStop(1, '#FF7A24'); g.fillStyle = gg; g.fillRect(14 + (j % 3) * 78, 42 + Math.floor(j / 3) * 56, 70, 46); }
    }));
  }, []);
}

/** Namen op de borden, in het Nederlands (verbeterlijst punt 39). */
const SIGN: Partial<Record<string, [string, string]>> = {
  onderzoek: ['ONDERZOEK', 'Niches & trends'], creatief: ['CREATIEF', 'Ideeën & titels'], script: ['SCRIPT', 'Scripts & verhaallijn'],
  stem: ['STEM', 'Voice-overs & audio'], productie: ['PRODUCTIE', 'Animatie & montage'], thumbnail: ['THUMBNAIL', 'Ontwerp & klikratio'],
  publicatie: ['PUBLICATIE', 'Upload & planning'], ceo: ['CEO & CIJFERS', 'Strategie & prestaties'], crisis: ['CRISISKAMER', 'Analyse & oplossingen'],
};
/** Groot lichtbord per afdeling (icoon + naam + ondertitel), net als op het referentiebeeld. */
function signTex(r: RoomDef) {
  return canvasTex(1024, 300, (g) => {
    g.clearRect(0, 0, 1024, 300);
    rr(g, 8, 8, 1008, 284, 40);
    const bg = g.createLinearGradient(0, 0, 0, 300); bg.addColorStop(0, 'rgba(26,20,58,0.96)'); bg.addColorStop(1, 'rgba(10,12,32,0.96)');
    g.fillStyle = bg; g.fill();
    g.shadowColor = r.color; g.shadowBlur = 30; g.lineWidth = 9; g.strokeStyle = r.color; g.stroke();
    g.shadowBlur = 0;
    rr(g, 44, 50, 200, 200, 34); g.fillStyle = r.color + '33'; g.fill(); g.lineWidth = 5; g.strokeStyle = r.color; g.stroke();
    g.font = '120px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(r.icon, 144, 158);
    g.textAlign = 'left'; g.fillStyle = '#ffffff'; g.shadowColor = r.color; g.shadowBlur = 18;
    const [name, sub] = SIGN[r.id] ?? [r.naam.toUpperCase(), r.sub];
    g.font = `900 ${name.length > 14 ? 74 : 92}px Inter, "Arial Black", sans-serif`; g.fillText(name, 284, 124);
    g.shadowBlur = 0; g.fillStyle = '#cbd5f5'; g.font = '600 52px Inter, Arial, sans-serif'; g.fillText(sub, 288, 214);
  });
}

/* Lichtbolletje met ! in de hoek van het afdelingsbord (niels 2026-11-06: in plaats van het label "wacht op jou"). */
const badgeTexs = new Map<string, THREE.Texture>();
function badgeTex(color: string, ink: string) {
  const key = color + ink;
  let t = badgeTexs.get(key);
  if (!t) {
    t = canvasTex(256, 256, (g) => {
      g.clearRect(0, 0, 256, 256);
      const glow = g.createRadialGradient(128, 128, 48, 128, 128, 128);
      glow.addColorStop(0, color + 'aa'); glow.addColorStop(0.5, color + '40'); glow.addColorStop(1, color + '00');
      g.fillStyle = glow; g.fillRect(0, 0, 256, 256);
      g.beginPath(); g.arc(128, 128, 62, 0, Math.PI * 2); g.fillStyle = color; g.fill();
      g.lineWidth = 7; g.strokeStyle = 'rgba(255,255,255,0.92)'; g.stroke();
      g.fillStyle = ink; g.font = '900 92px Inter, "Arial Black", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillText('!', 128, 133);
    });
    badgeTexs.set(key, t);
  }
  return t;
}
function AlertBadge({ kind, size, pos, top }: { kind: 'wacht' | 'probleem'; size: number; pos: V3; top?: boolean }) {
  const tex = useMemo(() => badgeTex(STATUS[kind].kleur, kind === 'probleem' ? '#ffffff' : '#1a1030'), [kind]);
  const ref = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => { if (ref.current && !reducedMotion()) ref.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * 3.2) * 0.08); });
  return (
    <mesh ref={ref} position={pos} renderOrder={top ? 12 : 1}>
      <planeGeometry args={[size, size]} />
      <meshBasicMaterial map={tex} transparent toneMapped={false} depthWrite={false} depthTest={!top} />
    </mesh>
  );
}

/* ================= camera ================= */
const ELEV = 0.66; // ~38°, zoals het referentiebeeld
const FOV = 40;
const angDiff = (a: number, b: number) => { let d = b - a; while (d > Math.PI) d -= Math.PI * 2; while (d < -Math.PI) d += Math.PI * 2; return d; };
/** camera op afstand d, hoogtehoek el en draaihoek az (0 = vooraan) rond doel t */
const camPos = (t: THREE.Vector3, d: number, el: number, az: number) => new THREE.Vector3(t.x + Math.cos(el) * Math.sin(az) * d, t.y + Math.sin(el) * d, t.z + Math.cos(el) * Math.cos(az) * d);
interface CamAnim { t: number; dur: number; fT: THREE.Vector3; tT: THREE.Vector3; fD: number; tD: number; fEl: number; tEl: number; fAz: number; tAz: number; intro?: boolean; hold?: number }
/**
 * Camera: vliegt naar een afdeling bij klik, maakt bij openen een drone-intro van 3 s (klik of scroll slaat
 * hem over) en laat je met de ingedrukte scrollknop (of in de Studio met de linkermuisknop, op een telefoon
 * met één vinger) helemaal om het kantoor heen draaien (niels 2026-11-06).
 * Tijdens het rondlopen (Walk.tsx) staat hij stil; daarna vliegt hij zelf terug naar het gewone beeld.
 */
function CameraRig({ mode }: { mode: WorldMode }) {
  const { camera, size, gl, scene } = useThree();
  const cam = camera as THREE.PerspectiveCamera;
  const controls = useRef<OC>(null);
  // alleen bij lokaal testen: camera en besturing bereikbaar voor testscripts
  useEffect(() => { if (window.location?.hostname === 'localhost') (window as unknown as { __dmCam: unknown }).__dmCam = { camera, controls, scene }; }, [camera, scene]);
  const focus = useWorld((s) => s.focus);
  const floor = useFloor((s) => s.floor);
  const introKey = useWorld((s) => s.introKey);
  const setIntro = useWorld((s) => s.setIntro);
  // met de vaste FOV (niet cam.fov): bij het wisselen naar onze eigen camera mag de afstand niet veranderen,
  // anders start de camera opnieuw en is de drone-intro weg
  const fit = useMemo(() => {
    const tv = Math.tan(THREE.MathUtils.degToRad(FOV / 2));
    const aspect = size.width / Math.max(1, size.height);
    const dh = (R_BASE * 1.5) / (tv * aspect);
    const dv = (R_BASE * 0.74) / tv;
    return Math.max(dh, dv);
  }, [size.width, size.height]);
  const anim = useRef<CamAnim | null>(null);
  const first = useRef(true);
  const cur = useRef({ d: fit });
  const az = () => controls.current?.getAzimuthalAngle() ?? 0;
  const el = () => (controls.current ? Math.PI / 2 - controls.current.getPolarAngle() : ELEV);

  const goal = (keepAz: number) => {
    const r = ROOMS.find((x) => x.id === focus);
    const wide = size.width >= 900;
    const right = new THREE.Vector3(Math.cos(keepAz), 0, -Math.sin(keepAz)); const back = new THREE.Vector3(Math.sin(keepAz), 0, Math.cos(keepAz));
    if (mode === 'home' && r) { const p = roomCenter(r); return { t: new THREE.Vector3(p[0], 0.6, p[2]).addScaledVector(right, wide ? 3 : 0).addScaledVector(back, 0.6), d: fit * 0.5 }; }
    // bovenverdieping: zelfde beeld, maar op de vloer van boven (en iets dichterbij: hij is kleiner)
    const up = floor === 1 && mode !== 'studio' ? Y1 : 0;
    if (mode === 'panel') return { t: new THREE.Vector3(0, 0.5 + up, 1.5), d: fit * 1.04 };
    return { t: new THREE.Vector3(0, 0.5 + up, 0).addScaledVector(back, wide ? 0.6 : 0), d: fit * (up ? 0.92 : 1) };
  };
  const start = (dur: number, g: { t: THREE.Vector3; d: number }, tAz: number, tEl = ELEV) => {
    const c = controls.current; const fAz = az();
    if (anim.current?.intro) setIntro(false); // intro onderbroken (klik op een afdeling): de hint moet ook weg
    anim.current = { t: reducedMotion() ? 1 : 0, dur, fT: c ? c.target.clone() : g.t, tT: g.t, fD: cur.current.d, tD: g.d, fEl: el(), tEl, fAz, tAz: fAz + angDiff(fAz, tAz) };
  };

  // rondlopen: zolang je loopt doen camera en orbit-besturing niets; daarna een terugvlucht vanaf ooghoogte.
  // "flying" wordt al bij het renderen gezet, zodat de orbit-besturing geen enkel beeld te vroeg weer aan gaat.
  const walk = useWorld((s) => s.walk);
  const [flying, setFlying] = useState(false);
  const [prevWalk, setPrevWalk] = useState(walk);
  if (walk !== prevWalk) { setPrevWalk(walk); setFlying(!walk); }
  const back = useRef<{ t: number; p0: THREE.Vector3; yaw: number; pitch: number; fov: number; near: number } | null>(null);
  const wasWalk = useRef(false);
  const eul = useMemo(() => new THREE.Euler(0, 0, 0, 'YXZ'), []);
  useLayoutEffect(() => {
    if (walk) { wasWalk.current = true; if (anim.current?.intro) setIntro(false); anim.current = null; back.current = null; return; }
    if (!wasWalk.current) return;
    wasWalk.current = false;
    const a = lookAngles(cam.getWorldDirection(new THREE.Vector3()));
    back.current = { t: reducedMotion() ? 1 : 0, p0: cam.position.clone(), yaw: a.yaw, pitch: a.pitch, fov: cam.fov, near: cam.near };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [walk]);

  useEffect(() => {
    if (first.current) {
      first.current = false;
      const g = goal(0);
      let seen = false; try { seen = sessionStorage.getItem('dm-intro') === '1'; sessionStorage.setItem('dm-intro', '1'); } catch { /* */ }
      if (reducedMotion()) { anim.current = { t: 1, dur: 1, fT: g.t, tT: g.t, fD: g.d, tD: g.d, fEl: ELEV, tEl: ELEV, fAz: 0, tAz: 0 }; return; }
      // drone-intro: van ver en hoog, met een halve draai, naar het overzicht (de eerste keer per sessie 3 s, daarna 1 s)
      anim.current = seen
        ? { t: 0, dur: 1.0, fT: g.t.clone().add(new THREE.Vector3(0, 0, -4)), tT: g.t, fD: g.d * 1.55, tD: g.d, fEl: ELEV + 0.25, tEl: ELEV, fAz: 0, tAz: 0 }
        : { t: 0, dur: 3.2, fT: new THREE.Vector3(0, 2.5, -6), tT: g.t, fD: g.d * 2.3, tD: g.d, fEl: 1.12, tEl: ELEV, fAz: -2.4, tAz: 0, intro: true };
      if (!seen) setIntro(true);
      return;
    }
    if (useWorld.getState().walk || back.current) return; // rondlopen of de terugvlucht stuurt de camera al
    start(0.85, goal(az()), az(), mode === 'panel' ? ELEV : Math.min(Math.max(el(), 0.52), 1.1));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focus, mode, fit, floor]);

  const lastKey = useRef(introKey);
  useEffect(() => {
    // niet bij het openen (dan loopt de drone-intro) en nooit midden in de intro
    if (introKey === lastKey.current) return; lastKey.current = introKey;
    if (first.current || reducedMotion() || anim.current?.intro || useWorld.getState().walk || back.current) return;
    const g = goal(az());
    anim.current = { t: 0, dur: 0.7, fT: g.t.clone().add(new THREE.Vector3(1.5, 0, -1.5)), tT: g.t, fD: g.d * 1.05, tD: g.d, fEl: el(), tEl: el(), fAz: az(), tAz: az() };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [introKey]);

  // intro overslaan met een klik, scroll of toets; scrollknop: geen autoscroll van de browser
  useEffect(() => {
    const el2 = gl.domElement;
    const skip = () => { const a = anim.current; if (a?.intro) a.t = 1; };
    const mid = (e: MouseEvent) => { if (e.button === 1) e.preventDefault(); };
    const reset = () => { if (!useWorld.getState().walk && !back.current) start(0.9, goal(0), 0); };
    el2.addEventListener('pointerdown', skip); el2.addEventListener('wheel', skip, { passive: true }); window.addEventListener('keydown', skip);
    el2.addEventListener('mousedown', mid); el2.addEventListener('auxclick', mid);
    window.addEventListener('dm-reset-view', reset);
    return () => {
      el2.removeEventListener('pointerdown', skip); el2.removeEventListener('wheel', skip); window.removeEventListener('keydown', skip);
      el2.removeEventListener('mousedown', mid); el2.removeEventListener('auxclick', mid); window.removeEventListener('dm-reset-view', reset);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gl, focus, mode, fit]);

  const btn = useRef(0);
  useFrame((_, dt) => {
    if (useWorld.getState().walk) return; // Walk.tsx stuurt de camera
    const bk = back.current;
    if (bk && controls.current) {
      // terug uit het rondlopen: eerst omhoog over de wanden, dan naar het gewone Home-beeld (of de afdeling die net openging)
      const oc = controls.current;
      bk.t = Math.min(1, bk.t + dt / 1.35);
      const k = ease(bk.t); const ky = ease(Math.min(1, bk.t * 1.7));
      const g = goal(0); const pe = camPos(g.t, g.d, ELEV, 0); const e = lookAngles(g.t.clone().sub(pe).normalize());
      cam.position.set(bk.p0.x + (pe.x - bk.p0.x) * k, bk.p0.y + (pe.y - bk.p0.y) * ky + Math.sin(Math.PI * k) * 4, bk.p0.z + (pe.z - bk.p0.z) * k);
      eul.set(bk.pitch + (e.pitch - bk.pitch) * k, bk.yaw + angDiff(bk.yaw, e.yaw) * k, 0, 'YXZ'); cam.quaternion.setFromEuler(eul);
      cam.fov = bk.fov + (FOV - bk.fov) * k; cam.near = bk.near + (0.5 - bk.near) * k; cam.updateProjectionMatrix();
      if (bk.t >= 1) { back.current = null; oc.target.copy(g.t); cam.position.copy(pe); oc.update(); cur.current.d = g.d; setFlying(false); }
      return;
    }
    const a = anim.current; const c = controls.current;
    // knop "terug naar vooraanzicht" tonen zodra je flink gedraaid hebt
    btn.current -= dt;
    if (btn.current <= 0 && c) { btn.current = 0.25; const b = document.getElementById('dm-reset'); if (b) b.style.display = Math.abs(angDiff(0, c.getAzimuthalAngle())) > 0.35 && !a ? 'flex' : 'none'; }
    if (!a || !c) return;
    // de drone-intro wacht tot het kantoor geladen is (anders vliegt hij achter het laadscherm); hooguit 20 s
    if (a.intro && a.t < 1 && !useOfficeLoad.getState().done && (a.hold = (a.hold ?? 0) + dt) < 20) { /* wachten */ }
    else a.t = Math.min(1, a.t + dt / a.dur);
    const k = a.intro ? 1 - Math.pow(1 - a.t, 3) * (1 - a.t * 0.2) : ease(a.t);
    const tgt = a.fT.clone().lerp(a.tT, k);
    const d = a.fD + (a.tD - a.fD) * k;
    cur.current.d = d;
    c.target.copy(tgt);
    cam.position.copy(camPos(tgt, d, a.fEl + (a.tEl - a.fEl) * k, a.fAz + (a.tAz - a.fAz) * k));
    c.update();
    if (a.t >= 1) { if (a.intro) setIntro(false); anim.current = null; }
  });

  const studio = mode === 'studio';
  return (
    <OrbitControls ref={controls as never} enabled={mode !== 'panel' && !walk && !flying} enableRotate enablePan
      mouseButtons={{ ...(studio ? { LEFT: THREE.MOUSE.ROTATE } : {}), MIDDLE: THREE.MOUSE.ROTATE, RIGHT: THREE.MOUSE.PAN }}
      touches={{ ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN }}
      minPolarAngle={0.45} maxPolarAngle={mode === 'home' ? 1.38 : 1.05} rotateSpeed={0.7}
      minDistance={fit * 0.3} maxDistance={fit * 1.5} enableDamping dampingFactor={0.08} screenSpacePanning={false} />
  );
}

/** Telt beelden per seconde en zet ze in de bovenbalk (#dm-fps). */
function FpsProbe() {
  const acc = useRef({ n: 0, t: 0, slow: 0, since: performance.now() });
  const quality = useWorld((s) => s.quality); const setQuality = useWorld((s) => s.setQuality);
  useEffect(() => { acc.current.slow = 0; acc.current.since = performance.now(); }, [quality]);
  useFrame((_, dt) => {
    const a = acc.current; a.n++; a.t += dt;
    if (a.t >= 0.5) {
      const fps = a.n / a.t; const el = document.getElementById('dm-fps'); if (el) el.textContent = `${Math.round(fps)} fps`; a.n = 0; a.t = 0;
      // 4K hapert (onder de 24 fps, 6 seconden lang): automatisch terug naar Auto
      if (quality === '4k' && performance.now() - a.since > 8000 && document.visibilityState === 'visible') {
        a.slow = fps < 24 ? a.slow + 0.5 : Math.max(0, a.slow - 1);
        if (a.slow >= 6) { a.slow = 0; setQuality('auto'); useGame.getState().toast('Beeld haperde in 4K, ik heb hem op Auto gezet', 'info'); }
      }
    }
  });
  return null;
}

/* ================= kleine bouwstenen ================= */
function Neon({ pts, color, r = 0.05, i = 2.6 }: { pts: V3[]; color: string; r?: number; i?: number }) {
  const geo = useMemo(() => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(...p))), Math.max(8, pts.length * 4), r, 6, false), [pts, r]);
  return <mesh geometry={geo}><meshStandardMaterial color={color} emissive={color} emissiveIntensity={i} toneMapped={false} /></mesh>;
}
const arc = (r: number, a0: number, a1: number, y: number, n = 16): V3[] => Array.from({ length: n + 1 }, (_, k) => polar(r, a0 + ((a1 - a0) * k) / n, y));

function Palm({ p, s = 1 }: { p: V3; s?: number }) {
  const leaves = useMemo(() => Array.from({ length: 7 }, (_, i) => ({ a: (i / 7) * Math.PI * 2 + Math.random() * 0.4, t: 0.55 + Math.random() * 0.35, l: 0.9 + Math.random() * 0.4 })), []);
  return (
    <group position={p} scale={s}>
      <mesh position={[0, 0.25, 0]} castShadow><cylinderGeometry args={[0.32, 0.24, 0.5, 14]} /><meshStandardMaterial color="#e9edf6" roughness={0.35} metalness={0.1} /></mesh>
      <mesh position={[0, 0.85, 0]} castShadow><cylinderGeometry args={[0.05, 0.07, 0.9, 6]} /><meshStandardMaterial color="#5b3d22" /></mesh>
      {leaves.map((L, i) => (
        <group key={i} position={[0, 1.25, 0]} rotation={[0, L.a, 0]}>
          <mesh rotation={[L.t, 0, 0]} position={[0, 0.1, L.l * 0.45]} castShadow>
            <boxGeometry args={[0.32, 0.03, L.l]} />
            <meshStandardMaterial color={i % 2 ? '#2f9e4f' : '#46c063'} roughness={0.6} emissive="#0d3a1a" emissiveIntensity={0.4} />
          </mesh>
        </group>
      ))}
      <mesh position={[0, 1.35, 0]} castShadow><icosahedronGeometry args={[0.28, 0]} /><meshStandardMaterial color="#3aa957" flatShading /></mesh>
    </group>
  );
}

/** Bureau met 2-3 schermen (dashboards), toetsenbord en stoel. Schermen kijken naar +z (de camera). */
function ProDesk({ p, tex, active, n = 2 }: { p: V3; tex: THREE.Texture[]; active: boolean; n?: number }) {
  const mats = useRef<THREE.MeshBasicMaterial[]>([]);
  const seed = useMemo(() => Math.random() * 10, []);
  useFrame(({ clock }) => { const f = active ? 1 + Math.sin(clock.elapsedTime * 3 + seed) * 0.08 : 0.55; mats.current.forEach((m) => m && m.color.setScalar(f)); });
  const xs = n === 3 ? [-0.62, 0, 0.62] : [-0.33, 0.33];
  return (
    <group position={p}>
      <Box p={[0, 0.74, 0]} s={[1.9, 0.07, 0.8]} c="#f1f4fa" rough={0.3} metal={0.1} />
      <Box p={[0, 0.72, -0.38]} s={[1.9, 0.03, 0.04]} c="#20D9FF" e="#20D9FF" ei={1.4} cast={false} />
      <Box p={[-0.86, 0.36, 0]} s={[0.06, 0.72, 0.7]} c="#cfd6e6" />
      <Box p={[0.86, 0.36, 0]} s={[0.06, 0.72, 0.7]} c="#cfd6e6" />
      {xs.map((x, i) => (
        <group key={i} position={[x, 1.08, -0.22]} rotation={[0, n === 3 ? -x * 0.35 : -x * 0.3, 0]}>
          <Box p={[0, -0.24, 0]} s={[0.06, 0.18, 0.06]} c="#20263b" />
          <Box p={[0, 0, -0.02]} s={[0.62, 0.38, 0.03]} c="#0d1120" />
          <mesh position={[0, 0, 0.001]}>
            <planeGeometry args={[0.57, 0.34]} />
            <meshBasicMaterial ref={(m) => { if (m) mats.current[i] = m; }} map={tex[(i + Math.floor(seed * 7)) % tex.length]} toneMapped={false} />
          </mesh>
        </group>
      ))}
      <Box p={[0, 0.79, 0.12]} s={[0.55, 0.02, 0.16]} c="#dfe4f2" cast={false} />
      <Chair p={[0, 0, 0.72]} />
    </group>
  );
}

/* ================= afdeling (ringsegment) ================= */

function Special({ r, at, faceOut }: { r: RoomDef; at: (u: number, v: number) => V3; faceOut: number }) {
  const c = r.color;
  switch (r.props) {
    case 'voice': return (<group position={at(0, 1.9)}>
      <Box p={[0, 1.25, 0]} s={[2.3, 2.5, 2.1]} c="#3b1d63" opacity={0.5} rough={0.1} />
      <Box p={[0, 2.52, 0]} s={[2.34, 0.06, 2.14]} c={c} e={c} ei={2.6} cast={false} />
      {[[-1.15, -1.05], [1.15, -1.05], [-1.15, 1.05], [1.15, 1.05]].map(([x, z], i) => <Box key={i} p={[x, 1.25, z]} s={[0.06, 2.5, 0.06]} c={c} e={c} ei={2.2} cast={false} />)}
      <MicStand p={[0, 0, 0]} />
    </group>);
    case 'crisis': return (<group position={at(0, 1.0)}><MeetingTable p={[0, 0, 0]} color={c} /></group>);
    case 'ceo': return (<group position={at(0, 3.0)}><MeetingTable p={[0, 0, 0]} color={c} /></group>);
    case 'creative': return (<><Easel p={at(0, 3.0)} rot={faceOut} /></>);
    case 'script': return <Bookshelf p={at(0, 3.3)} rot={faceOut} />;
    case 'production': return (<><ServerRack p={at(-0.6, 3.3)} rot={faceOut} /><ServerRack p={at(0.6, 3.3)} rot={faceOut} /></>);
    case 'publishing': return <Rocket p={at(0, 3.0)} color={c} />;
    case 'research': return <Globe p={at(0, 3.0)} color={c} />;
    case 'thumbnail': return <Easel p={at(0, 3.0)} rot={faceOut} />;
    default: return null;
  }
}
function Globe({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Mesh>(null);
  useFrame((_, dt) => { if (g.current) g.current.rotation.y += dt * 0.4; });
  return (<group position={p}><Box p={[0, 0.45, 0]} s={[0.5, 0.9, 0.5]} c="#141a30" metal={0.5} rough={0.3} />
    <mesh ref={g} position={[0, 1.5, 0]}><icosahedronGeometry args={[0.55, 2]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} wireframe toneMapped={false} /></mesh></group>);
}
function Rocket({ p, color }: { p: V3; color: string }) {
  const g = useRef<THREE.Group>(null);
  useFrame(({ clock }) => { if (g.current) g.current.position.y = 0.3 + Math.sin(clock.elapsedTime * 1.6) * 0.12; });
  return (<group position={p}><Box p={[0, 0.15, 0]} s={[0.9, 0.3, 0.9]} c="#141a30" />
    <group ref={g}>
      <mesh position={[0, 1, 0]} castShadow><capsuleGeometry args={[0.28, 0.8, 4, 12]} /><meshStandardMaterial color="#e8edf7" metalness={0.4} roughness={0.3} /></mesh>
      <mesh position={[0, 1.75, 0]}><coneGeometry args={[0.28, 0.4, 12]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.6} /></mesh>
      <mesh position={[0, 0.3, 0]}><coneGeometry args={[0.16, 0.4, 10]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
    </group></group>);
}

function Wing({ r, lit, alert, busy, onSelect, onHover, screens, baked, walk }: { r: RoomDef; lit: boolean; alert: 'wacht' | 'probleem' | null; busy: boolean; onSelect: () => void; onHover: (h: boolean) => void; screens: THREE.Texture[]; baked?: OfficeModel | null; walk?: boolean }) {
  const a = slotAngle(r.slot);
  const a0 = a - SPAN / 2 + GAPA, a1 = a + SPAN / 2 - GAPA;
  const c = r.color;
  const front = Math.cos(a) > 0.35; // vooraan: hoge wand aan de binnenkant, lage glaswand naar de camera
  const H = 3.0, HG = front ? 1.1 : 2.5;
  const rm = (R_IN + R_OUT) / 2;
  // lokaal assenstelsel: u = langs de ring, v = naar buiten
  const at = (u: number, v: number, y = 0): V3 => { const rad = rm + v; const ang = a + u / rad; return polar(rad, ang, y); };
  const sign = useMemo(() => signTex(r), [r]);
  const edge = useRef<THREE.MeshStandardMaterial[]>([]);
  useFrame(() => {
    edge.current.forEach((m) => { if (m) m.emissiveIntensity = lit ? 2.4 : 1.4; });
  });
  const tallR = front ? R_IN + 0.08 : R_OUT - 0.08;
  const glassR = front ? R_OUT - 0.05 : R_IN + 0.05;
  const desks: [number, number][] = [[-1.25, -1.5], [1.25, -1.5], [-1.25, 1.3], [1.25, 1.3]];
  const nDesk = r.props === 'crisis' ? 2 : r.props === 'voice' ? 2 : 4;
  const deskPts = (r.props === 'crisis' ? [[-1.6, -2.2], [1.6, -2.2]] : r.props === 'voice' ? [[-1.25, -1.5], [1.25, -1.5]] : desks).slice(0, nDesk) as [number, number][];
  const warm = useMemo(() => new THREE.Color(c).lerp(new THREE.Color('#ffd9b0'), 0.45), [c]);
  const NeonMat = ({ i = 0 }: { i?: number }) => <meshStandardMaterial ref={(m) => { if (m) edge.current[i] = m; }} color={c} emissive={c} emissiveIntensity={2.4} toneMapped={false} />;

  const handlers = {
    onClick: (e: { stopPropagation: () => void }) => { e.stopPropagation(); onSelect(); },
    onPointerOver: (e: { stopPropagation: () => void }) => { e.stopPropagation(); onHover(true); document.body.style.cursor = 'pointer'; },
    onPointerOut: () => { onHover(false); document.body.style.cursor = 'auto'; },
  };
  const [sw, sh] = baked ? [5.4, 1.58] : [7.2, 2.1];
  // het CEO-bord staat in het overzicht altijd vooraan (door de zuil heen); tijdens het rondlopen niet door wanden heen
  const onTop = !!baked && r.props === 'ceo' && !walk;
  const signEl = (
    <Billboard position={polar(tallR, a, H + (baked ? (r.props === 'ceo' ? 0.55 : 1.15) : 1.4))}>
      <mesh renderOrder={r.props === 'ceo' ? 11 : 0} onClick={(e) => { e.stopPropagation(); onSelect(); }}>
        <planeGeometry args={[sw, sh]} />
        <meshBasicMaterial map={sign} transparent toneMapped={false} depthWrite={false} depthTest={!onTop} opacity={lit ? 1 : 0.95} />
      </mesh>
      {/* rechtsboven op de hoek van het bord, zoals een melding op een app-icoon */}
      {alert && <AlertBadge kind={alert} size={sh * 0.6} pos={[sw / 2 - sh * 0.12, sh / 2 - sh * 0.12, 0.02]} top={onTop} />}
    </Billboard>
  );
  if (baked) {
    return (
      <group {...handlers}>
        {/* onzichtbaar klikvlak over de hele afdeling */}
        <mesh position={[0, 1.4, 0]} visible={false}><cylinderGeometry args={[R_OUT, R_OUT, 2.8, 20, 1, true, a0, a1 - a0]} /><meshBasicMaterial side={THREE.DoubleSide} /></mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.09, 0]}>
          <ringGeometry args={[R_IN, R_OUT, 24, 1, a0 - Math.PI / 2, a1 - a0]} />
          <meshBasicMaterial color={c} transparent opacity={lit ? 0.12 : 0} depthWrite={false} toneMapped={false} />
        </mesh>
        {r.props === 'research' && <Globe p={at(1.4, 2.4, 0.45)} color={c} />}
        {r.props === 'publishing' && <Rocket p={at(1.2, 2.6, 0.3)} color={c} />}
        {signEl}
      </group>
    );
  }
  return (
    <group {...handlers}>
      {/* vloer */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 0]} receiveShadow>
        <ringGeometry args={[R_IN, R_OUT, 40, 1, a0 - Math.PI / 2, a1 - a0]} />
        <meshStandardMaterial color="#1b2246" roughness={0.25} metalness={0.45} emissive={c} emissiveIntensity={lit ? 0.14 : 0.06} />
      </mesh>
      {/* tapijt */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.04, 0]} receiveShadow>
        <ringGeometry args={[R_IN + 1.6, R_OUT - 1.6, 30, 1, a0 + 0.06 - Math.PI / 2, a1 - a0 - 0.12]} />
        <meshStandardMaterial color="#1d2448" roughness={0.95} />
      </mesh>
      {/* hoge wand (donker glas/metaal) */}
      <mesh position={[0, H / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[tallR, tallR, H, 32, 1, true, a0, a1 - a0]} />
        <meshStandardMaterial color="#121a36" roughness={0.3} metalness={0.6} side={THREE.DoubleSide} />
      </mesh>
      {/* glaswand naar de gang / camera */}
      <mesh position={[0, HG / 2, 0]}>
        <cylinderGeometry args={[glassR, glassR, HG, 32, 1, true, a0, a1 - a0]} />
        <meshStandardMaterial color="#9fdcff" transparent opacity={0.12} roughness={0.05} metalness={0.3} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
      {/* glazen zijwanden */}
      {[a0, a1].map((ang, i) => (
        <mesh key={i} position={polar(rm, ang, 1.25)} rotation={[0, ang, 0]}>
          <boxGeometry args={[0.04, 2.5, R_OUT - R_IN]} />
          <meshStandardMaterial color="#9fdcff" transparent opacity={0.1} roughness={0.05} side={THREE.DoubleSide} depthWrite={false} />
        </mesh>
      ))}
      {/* neonranden: vloer, bovenkant van de wanden, hoekstijlen */}
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(R_OUT - 0.05, a0, a1, 0.06).map((p) => new THREE.Vector3(...p))), 40, 0.06, 6, false]} /><NeonMat i={0} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(R_IN + 0.05, a0, a1, 0.06).map((p) => new THREE.Vector3(...p))), 30, 0.05, 6, false]} /><NeonMat i={1} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(tallR, a0, a1, H).map((p) => new THREE.Vector3(...p))), 40, 0.06, 6, false]} /><NeonMat i={2} /></mesh>
      <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3(arc(glassR, a0, a1, HG).map((p) => new THREE.Vector3(...p))), 40, 0.04, 6, false]} /><NeonMat i={3} /></mesh>
      {[a0, a1].map((ang, i) => (<group key={i}>
        <Neon pts={[polar(R_IN, ang, 0.06), polar(R_OUT, ang, 0.06)]} color={c} r={0.04} i={2} />
        <Neon pts={[polar(R_OUT - 0.05, ang, 0), polar(R_OUT - 0.05, ang, front ? HG : H)]} color={c} r={0.05} i={2.4} />
        <Neon pts={[polar(R_IN + 0.05, ang, 0), polar(R_IN + 0.05, ang, front ? H : HG)]} color={c} r={0.05} i={2.4} />
      </group>))}
      {/* warm binnenlicht */}
      <pointLight position={polar(rm, a, 2.6)} color={warm} intensity={lit ? 20 : 13} distance={10} decay={1.6} />
      {/* groot scherm op de hoge wand */}
      <mesh position={polar(front ? R_IN + 0.2 : R_OUT - 0.2, a, 1.75)} rotation={[0, front ? a : a + Math.PI, 0]}>
        <planeGeometry args={[3.0, 1.35]} />
        <meshBasicMaterial map={screens[(r.slot + 2) % screens.length]} toneMapped={false} />
      </mesh>
      <mesh position={polar(front ? R_IN + 0.19 : R_OUT - 0.19, a, 1.75)} rotation={[0, front ? a : a + Math.PI, 0]}>
        <planeGeometry args={[3.15, 1.5]} />
        <meshStandardMaterial color={c} emissive={c} emissiveIntensity={1.2} toneMapped={false} />
      </mesh>
      {/* bureaus + medewerkers (schermen naar de camera) */}
      {deskPts.map(([u, v], i) => <ProDesk key={i} p={at(u, v)} tex={screens} n={i === 0 ? 3 : 2} active={busy} />)}
      <Special r={r} at={at} faceOut={a + Math.PI} />
      {/* planten in de hoeken */}
      <Palm p={at(-3.1, 3.2)} s={0.95} />
      <Palm p={at(3.1, 3.2)} s={0.8} />
      {signEl}
    </group>
  );
}

/* ================= receptie in het midden ================= */
function hqSignTex() {
  return canvasTex(1024, 512, (g) => {
    g.clearRect(0, 0, 1024, 512);
    rr(g, 24, 40, 976, 420, 70); const bg = g.createLinearGradient(0, 40, 0, 460); bg.addColorStop(0, 'rgba(40,18,40,.92)'); bg.addColorStop(1, 'rgba(14,12,34,.92)');
    g.fillStyle = bg; g.fill(); g.lineWidth = 10; g.strokeStyle = '#FF7A24'; g.shadowColor = '#FF7A24'; g.shadowBlur = 40; g.stroke();
    g.textAlign = 'center'; g.textBaseline = 'middle';
    const gr = g.createLinearGradient(0, 120, 0, 280); gr.addColorStop(0, '#FFE0A8'); gr.addColorStop(1, '#FF8A3D');
    g.fillStyle = gr; g.shadowBlur = 36; g.font = '900 168px Inter, "Arial Black", sans-serif'; g.fillText('DRIFTMARK', 512, 210);
    g.shadowColor = '#398CFF'; g.fillStyle = '#E6F0FF'; g.font = '900 120px Inter, "Arial Black", sans-serif'; g.fillText('HQ', 512, 360);
  });
}
function playTex() {
  return canvasTex(256, 256, (g) => {
    g.shadowColor = '#FF7A24'; g.shadowBlur = 34; g.strokeStyle = '#FFB070'; g.lineWidth = 16; g.lineJoin = 'round';
    g.beginPath(); g.moveTo(88, 58); g.lineTo(202, 128); g.lineTo(88, 198); g.closePath(); g.stroke();
    g.globalAlpha = 0.25; g.fillStyle = '#FF7A24'; g.fill();
  });
}

function Reception({ screens, onSelect, lit, baked, walk }: { screens: THREE.Texture[]; onSelect: () => void; lit: boolean; baked?: boolean; walk?: boolean }) {
  const holo = useRef<THREE.MeshStandardMaterial>(null); const ring1 = useRef<THREE.Mesh>(null); const ring2 = useRef<THREE.Mesh>(null); const play = useRef<THREE.Group>(null);
  const sign = useMemo(hqSignTex, []); const pt = useMemo(playTex, []);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (holo.current) holo.current.opacity = 0.05 + Math.sin(t * 2) * 0.015;
    if (ring1.current) { const k = (t * 0.5) % 1; ring1.current.position.y = 1.3 - DROP + k * 6.4; (ring1.current.material as THREE.MeshBasicMaterial).opacity = (1 - k) * 0.45; }
    if (ring2.current) { const k = ((t * 0.5) + 0.5) % 1; ring2.current.position.y = 1.3 - DROP + k * 6.4; (ring2.current.material as THREE.MeshBasicMaterial).opacity = (1 - k) * 0.45; }
    if (play.current) play.current.position.y = 5.9 + Math.sin(t * 1.4) * 0.15;
  });
  return (
    <group onClick={(e) => { e.stopPropagation(); onSelect(); }} onPointerOver={() => { document.body.style.cursor = 'pointer'; }} onPointerOut={() => { document.body.style.cursor = 'auto'; }}>
      {!baked && (<>
      {/* podium */}
      <mesh position={[0, HUB_Y / 2, 0]} castShadow receiveShadow><cylinderGeometry args={[R_HUB, R_HUB + 0.3, HUB_Y, 64]} /><meshStandardMaterial color="#121a38" metalness={0.6} roughness={0.2} /></mesh>
      <mesh position={[0, HUB_Y + 0.012, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[R_HUB - 0.05, 0.035, 8, 96]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
      <mesh position={[0, HUB_Y + 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[3.6, 3.72, 96]} /><meshBasicMaterial color="#20D9FF" toneMapped={false} /></mesh>
      <mesh position={[0, HUB_Y + 0.012, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[4.7, 4.76, 96]} /><meshBasicMaterial color="#398CFF" toneMapped={false} /></mesh>
      {/* ronde balie */}
      <mesh position={[0, 1.05 - DROP, 0]} castShadow><cylinderGeometry args={[2.7, 2.7, 1.1, 48, 1, true, Math.PI * 0.18, Math.PI * 1.64]} /><meshStandardMaterial color="#1a2550" metalness={0.6} roughness={0.25} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, 1.61 - DROP, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.72, 0.06, 8, 96, Math.PI * 2]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3} toneMapped={false} /></mesh>
      <mesh position={[0, 0.6 - DROP, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.75, 0.05, 8, 96]} /><meshStandardMaterial color="#20D9FF" emissive="#20D9FF" emissiveIntensity={2.4} toneMapped={false} /></mesh>
      {/* schermen op de balie */}
      {[-1.1, 0, 1.1].map((x, i) => (
        <group key={i} position={[x, 1.95 - DROP, 1.35 - Math.abs(x) * 0.25]} rotation={[0, -x * 0.35, 0]}>
          <Box p={[0, 0, -0.02]} s={[0.9, 0.52, 0.04]} c="#0d1120" />
          <mesh position={[0, 0, 0.001]}><planeGeometry args={[0.84, 0.47]} /><meshBasicMaterial map={screens[i]} toneMapped={false} /></mesh>
        </group>
      ))}
      </>)}
      {/* het hoofdpersonage achter de balie */}
      <Mascot p={[0, HUB_Y, -0.4]} rot={0} s={1.05} />
      {/* glazen hologramzuil */}
      <mesh position={[0, (1.5 - DROP + 8.5) / 2, 0]}><cylinderGeometry args={[2.3, 2.3, 7 + DROP, 64, 1, true]} /><meshStandardMaterial ref={holo} color="#7fe8ff" emissive="#20D9FF" emissiveIntensity={0.2} transparent opacity={0.05} depthWrite={false} side={THREE.DoubleSide} toneMapped={false} /></mesh>
      <mesh ref={ring1} position={[0, 1.3 - DROP, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.32, 0.035, 6, 80]} /><meshBasicMaterial color="#b8f6ff" transparent toneMapped={false} /></mesh>
      <mesh ref={ring2} position={[0, 1.3 - DROP, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.32, 0.035, 6, 80]} /><meshBasicMaterial color="#b8f6ff" transparent toneMapped={false} /></mesh>
      {!baked && (<>
      <mesh position={[0, 8.5, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[2.35, 0.09, 8, 80]} /><meshStandardMaterial color="#FF7A24" emissive="#FF7A24" emissiveIntensity={3.2} toneMapped={false} /></mesh>
      <mesh position={[0, 8.55, 0]}><cylinderGeometry args={[2.4, 2.4, 0.12, 64]} /><meshStandardMaterial color="#1a1530" metalness={0.6} roughness={0.3} /></mesh>
      </>)}
      <group ref={play} position={[0, 5.9, 0]}>
        <Billboard><mesh><planeGeometry args={[2.1, 2.1]} /><meshBasicMaterial map={pt} transparent toneMapped={false} depthWrite={false} /></mesh></Billboard>
      </group>
      {/* zwevende schermpjes rond de zuil */}
      {[-1, 1].map((sd) => (
        <mesh key={sd} position={[sd * 3.3, 3.0, 1.2]} rotation={[0, -sd * 0.5, 0]}>
          <planeGeometry args={[1.6, 1]} /><meshBasicMaterial map={screens[sd > 0 ? 3 : 0]} transparent opacity={0.85} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      ))}
      <Billboard position={[0, baked ? 7.7 : 10.2, 0]}><mesh renderOrder={10}><planeGeometry args={baked ? [6.0, 3.0] : [7.4, 3.7]} /><meshBasicMaterial map={sign} transparent toneMapped={false} depthWrite={false} depthTest={!baked || !!walk} /></mesh></Billboard>
      <pointLight position={[0, 4, 0]} color="#20D9FF" intensity={lit ? 22 : 14} distance={16} decay={1.5} />
      <pointLight position={[0, 2.2, 2.5]} color="#FFE2C4" intensity={18} distance={8} decay={1.6} />
      {!baked && (<>
      {/* planten op het podium */}
      <Palm p={[-3.9, HUB_Y, -3.1]} s={1.0} />
      <Palm p={[3.9, HUB_Y, -3.1]} s={1.0} />
      <Sofa p={[-4.1, HUB_Y, 1.6]} rot={Math.PI / 2 + 0.4} color="#26305e" />
      <Sofa p={[4.1, HUB_Y, 1.6]} rot={-Math.PI / 2 - 0.4} color="#26305e" />
      </>)}
    </group>
  );
}

/** Vlakke loopbrug vooraan (was een trap toen het podium 0,5 m hoog lag) + lichtgevende ingang (zeshoek). */
function Entrance() {
  const n = 7;
  return (
    <group>
      {Array.from({ length: n }, (_, i) => {
        const z = R_HUB + 0.3 + i * ((R_OUT - R_HUB - 1) / n); const y = HUB_Y * (1 - (i + 1) / n) + 0.02 * ((i + 1) / n);
        const w = 3.6 + i * 0.22;
        return (<group key={i}>
          <Box p={[0, y / 2, z]} s={[w, y, (R_OUT - R_HUB - 1) / n]} c="#151d3d" metal={0.5} rough={0.25} />
          <Box p={[0, y + 0.006, z + (R_OUT - R_HUB - 1) / n / 2 - 0.02]} s={[w, 0.012, 0.04]} c="#20D9FF" e="#20D9FF" ei={2.2} cast={false} />
        </group>);
      })}
      {[-1, 1].map((sd) => <Neon key={sd} pts={[[sd * 1.9, 1.0, R_HUB + 0.2], [sd * 2.7, 1.0, R_OUT]]} color="#20D9FF" r={0.04} i={2.2} />)}
      <mesh position={[0, 0.05, R_OUT + 0.6]} rotation={[-Math.PI / 2, 0, Math.PI / 6]}><ringGeometry args={[1.5, 1.68, 6]} /><meshBasicMaterial color="#20D9FF" toneMapped={false} /></mesh>
      <mesh position={[0, 0.04, R_OUT + 0.6]} rotation={[-Math.PI / 2, 0, Math.PI / 6]}><circleGeometry args={[1.5, 6]} /><meshBasicMaterial color="#123a66" transparent opacity={0.6} toneMapped={false} /></mesh>
      <Palm p={[-3.0, 0, R_OUT - 0.4]} s={1.1} />
      <Palm p={[3.0, 0, R_OUT - 0.4]} s={1.1} />
    </group>
  );
}

/* ================= glans-look (punt 33) =================
 * Zoals de renders van de video's: een warm hoofdlicht schuin van voren, en een oranje en een blauw randlicht
 * van achteren die de lak van de vinylfiguren laten glanzen. Geen schaduw (die zit al in het kantoor gebakken). */
function GlansLicht() {
  return (
    <>
      <directionalLight position={[-14, 20, 24]} color="#FFD7AE" intensity={1.25} />
      <directionalLight position={[-22, 9, -20]} color="#FF8A3D" intensity={1.6} />
      <directionalLight position={[22, 9, -20]} color="#3D9BFF" intensity={1.6} />
    </>
  );
}
/** Houdt de 3D-tekening even groot als het venster. Soms bleef het kantoor op een oude, smallere maat staan
 *  (bv. als het HQ eerst in een smal paneel opende en daarna groot werd): links beeld, rechts zwart. */
function PasMaat() {
  const gl = useThree((s) => s.gl);
  const setSize = useThree((s) => s.setSize);
  const get = useThree((s) => s.get);
  useEffect(() => {
    const doos = gl.domElement.parentElement;
    if (!doos) return;
    const check = () => {
      const w = doos.clientWidth, h = doos.clientHeight;
      const st = get();
      if ( w < 2 || h < 2) return;
      if (Math.abs(st.size.width - w) > 1 || Math.abs(st.size.height - h) > 1) {
        const r = doos.getBoundingClientRect();
        setSize(w, h, undefined, r.top, r.left);
      }
    };
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(check) : null;
    ro?.observe(doos);
    window.addEventListener('resize', check);
    document.addEventListener('visibilitychange', check);
    const t = setInterval(check, 1000);
    check();
    return () => { ro?.disconnect(); window.removeEventListener('resize', check); document.removeEventListener('visibilitychange', check); clearInterval(t); };
  }, [gl, setSize, get]);
  return null;
}

/* ================= de scène ================= */
function Scene({ mode }: { mode: WorldMode }) {
  const live = useLive((s) => s.data);
  const activity = live.activity;
  const { agents, selectAgent, setPage } = useGame(useShallow((s) => ({ agents: s.agents, selectAgent: s.selectAgent, setPage: s.setPage })));
  const { focus, openWorker, hover, setHover, walk } = useWorld(useShallow((s) => ({ focus: s.focus, openWorker: s.openWorker, hover: s.hover, setHover: s.setHover, walk: s.walk })));
  const per = useMemo(() => threadsPerRoom(activity), [activity]);
  const quality = useWorld((s) => s.quality);
  const perf = useWorld((s) => s.perf);
  /** 0 = licht t/m 3 = alles: snel is altijd licht, 4K altijd alles, Auto volgt de gemeten beeldsnelheid */
  const lvl = quality === 'snel' ? 0 : quality === '4k' ? 3 : perf;
  /* het nabewerkingslaagje past zich alleen aan bij een andere venstergrootte, niet bij een andere pixeldichtheid;
     zonder dit tekent het na een kwaliteitsstap maar een deel van het scherm (rest zwart) */
  const fxRef = useRef<any>(null);
  const { width: fxW, height: fxH } = useThree((s) => s.size);
  const fxDpr = useThree((s) => s.viewport.dpr);
  useEffect(() => { fxRef.current?.setSize?.(fxW, fxH); }, [fxW, fxH, fxDpr, lvl]);
  const phone = useMemo(() => isPhone(), []);
  const screens = useScreens();
  const office = useOffice();
  const dash = useMemo(() => (typeof document !== 'undefined' ? new Dashboards() : null), []);
  const alarms = useMemo(() => alarmsFrom(live), [live]);
  useEffect(() => { dash?.set({ live, alarms, scriptLines: live.script?.regels, scriptVideo: live.script?.video }); }, [dash, live, alarms]);
  const punten = useMemo(() => mergePunten(live.verbeter), [live.verbeter]);

  // zitplekken: uit het Blender-model, anders uit de eenvoudige indeling
  const seats = useMemo(() => {
    if (office) return office.seats;
    const out: Record<string, V3[]> = {};
    for (const r of ROOMS) {
      if (r.slot < 0) continue;
      const pts = r.props === 'crisis' ? [[-1.6, -2.2], [1.6, -2.2]] : r.props === 'voice' ? [[-1.25, -1.5], [1.25, -1.5]] : [[-1.25, -1.5], [1.25, -1.5], [-1.25, 1.3], [1.25, 1.3]];
      out[r.id] = pts.map(([u, v]) => { const p = atRoom(r, u, v); return [p[0], 0, p[2] + 0.66] as V3; });
    }
    return out;
  }, [office]);
  const open = (room: RoomId) => { if (mode === 'panel') setPage('driftmark'); openWorker(room); };
  const members = useMemo(() => mode === 'studio'
    ? gameStaff(agents, (id) => selectAgent(id))
    : staffFor({ per, all: activity, punten, seats, videos: live.videos ?? [], at: (room, u, v) => { const p = atRoom(roomById(room)!, u, v); return [p[0], p[2]]; }, onOpen: open }),
  // eslint-disable-next-line react-hooks/exhaustive-deps
  [mode, agents, per, activity, punten, seats, live.videos]);
  const handoffs = useMemo(() => handoffsFor(live.videos ?? []), [live.videos]);
  // kantoorgeluid: harder geroezemoes en meer toetsenborden als er meer agents werken
  useEffect(() => { const n = members.filter((m) => m.status === 'werkt' || m.status === 'bezig').length; setAmbience(Math.min(8, n), Math.min(1, n / 14)); }, [members]);
  const roomName = (id: string) => roomById(id as RoomId)?.naam ?? id;

  // klik op een afdeling (zelfde handeling als "Openen" bij het rondlopen)
  const select = (r: RoomDef) => selectRoom(r, mode);
  const coach = ROOMS.find((x) => x.id === 'coach')!;
  const busyRoom = (id: RoomId) => members.some((m) => m.room === id && (m.status === 'werkt' || m.status === 'bezig'));
  // boven (kantine en gamekamer): de borden, de pijplijn en de alarmlichten van beneden zijn weg
  const floor = useFloor((s) => s.floor);
  const ground = floor === 0;
  // een afdeling openen (bv. via de knoppen) brengt je terug naar beneden
  useEffect(() => { if (focus && useFloor.getState().floor === 1 && !useWorld.getState().walk) useFloor.getState().setFloor(0); }, [focus]);

  return (
    <>
      <color attach="background" args={['#060a1c']} />
      <fog attach="fog" args={['#0a0f2a', 180, 480]} />
      <PerspectiveCamera makeDefault fov={FOV} near={0.5} far={400} position={[0, 60, 45]} />
      <CameraRig mode={mode} />
      <WalkController mode={mode} />
      <FpsProbe />
      <Environment resolution={128} frames={1}>
        <Lightformer form="ring" intensity={2} color="#FF7A24" scale={14} position={[-18, 8, -10]} />
        <Lightformer form="ring" intensity={2} color="#20D9FF" scale={14} position={[18, 8, -10]} />
        <Lightformer form="rect" intensity={1.5} color="#A855F7" scale={[30, 6, 1]} position={[0, 12, -30]} />
        <Lightformer form="rect" intensity={1} color="#ffffff" scale={[20, 20, 1]} position={[0, 30, 0]} rotation-x={Math.PI / 2} />
      </Environment>
      <Sky baked={!!office} />
      <pointLight position={[-30, 12, 6]} color="#FF7A24" intensity={55} distance={80} decay={1.4} />
      <pointLight position={[30, 12, 6]} color="#398CFF" intensity={55} distance={80} decay={1.4} />
      <GlansLicht />

      {!office && (<>
      {/* grondplaat: spiegelende vloer met oranje rand */}
      <mesh position={[0, -0.6, 0]} receiveShadow><cylinderGeometry args={[R_BASE, R_BASE + 0.4, 1.2, 8, 1]} /><meshStandardMaterial color="#0a0f24" roughness={0.35} metalness={0.6} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, 0.005, 0]}>
        <circleGeometry args={[R_BASE - 0.2, 8]} />
        <MeshReflectorMaterial blur={[300, 80]} resolution={512} mixBlur={1} mixStrength={18} roughness={0.75} depthScale={1} minDepthThreshold={0.4} maxDepthThreshold={1.4} color="#0d1330" metalness={0.6} mirror={0.6} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, 0.02, 0]}><ringGeometry args={[R_BASE - 0.35, R_BASE - 0.15, 8]} /><meshBasicMaterial color="#FF7A24" toneMapped={false} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 8]} position={[0, -1.15, 0]}><ringGeometry args={[R_BASE + 0.2, R_BASE + 0.6, 8]} /><meshBasicMaterial color="#FF7A24" toneMapped={false} /></mesh>
      {/* lichtlijnen in de gang */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}><ringGeometry args={[R_IN - 0.42, R_IN - 0.34, 96]} /><meshBasicMaterial color="#398CFF" toneMapped={false} /></mesh>

      </>)}
      {office && <BakedOffice model={office} screens={screens} dash={dash} lit={(id) => focus === id || hover === id} />}
      {office && <PostIts screens={office.screens} />}
      <Reception screens={screens} baked={!!office} walk={walk} lit={focus === 'coach' || hover === 'coach'} onSelect={() => select(coach)} />
      {!office && <Entrance />}
      {ground && ROOMS.filter((r) => r.slot >= 0).map((r) => {
        const st = statusOf(per[r.id]);
        return (
          <Wing key={r.id} r={r} baked={office} walk={walk} screens={screens} busy={busyRoom(r.id)} lit={focus === r.id || hover === r.id} alert={mode !== 'studio' && (st === 'wacht' || st === 'probleem') ? st : null}
            onHover={(h) => setHover(h ? r.id : null)} onSelect={() => select(r)} />
        );
      })}
      <Crew members={members} seats={seats} chairs={office?.chairs} handoffs={mode === 'studio' ? [] : handoffs} roomName={roomName}
        onHoverRoom={(id) => setHover((id as RoomId) ?? null)} />
      {mode !== 'studio' && ground && <Pipeline videos={live.videos ?? []} onPick={(id) => select(roomById(id)!)} />}
      {mode !== 'studio' && <Upstairs />}
      {mode !== 'studio' && <Plafond />}
      {mode !== 'studio' && <CastProps members={members} />}
      <City />
      <Drone />
      {mode !== 'studio' && ground && <VoiceProps />}
      <Confetti />
      {mode !== 'studio' && ground && <Beacon alarms={alarms} />}
      <Snow />
      <Disco />
      <EffectComposer ref={fxRef} multisampling={lvl <= 0 ? 0 : lvl === 1 ? 2 : 4}>
        {/* zachtere neon (punt 33): minder gloed, pas boven een hogere drempel */}
        <Bloom intensity={office ? 0.22 : 0.34} luminanceThreshold={office ? 1.25 : 1.0} luminanceSmoothing={0.2} radius={0.4} mipmapBlur />
        <Vignette eskil={false} offset={0.4} darkness={0.22} />
      </EffectComposer>
    </>
  );
}

export default function NeonOffice({ mode }: { mode: WorldMode }) {
  const quality = useWorld((s) => s.quality);
  const perf = useWorld((s) => s.perf); const setPerf = useWorld((s) => s.setPerf);
  const setFocus = useWorld((s) => s.setFocus);
  const auto = quality === 'auto';
  return (
    <Canvas shadows dpr={dprFor(quality, PERF_DPR[auto ? perf : 2])} gl={{ antialias: true, powerPreference: 'high-performance', toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.15 }}
      onPointerMissed={(e) => { if (mode === 'home' && !useWorld.getState().walk && (e.target as HTMLElement)?.tagName === 'CANVAS') setFocus(null); }}>
      {/* soepel op elke computer (punt 74): de beeldsnelheid wordt gemeten tegen de verversing van het scherm (tot 144 Hz).
          Zakt hij onder ~55 fps, dan een stap lichter (minder pixels en minder randafvlakking); loopt hij ruim, dan een stap mooier. */}
      {auto && <PerformanceMonitor ms={400} iterations={8} threshold={0.75} flipflops={4}
        bounds={(hz) => [Math.min(55, hz * 0.85), Math.min(hz, 144) * 0.95]}
        onDecline={() => setPerf(useWorld.getState().perf - 1)} onIncline={() => setPerf(useWorld.getState().perf + 1)} />}
      <PasMaat />
      <Scene mode={mode} />
    </Canvas>
  );
}
