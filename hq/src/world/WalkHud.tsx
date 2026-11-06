/**
 * Schermlaag van RONDLOPEN (de camera zit in Walk.tsx): de knop rechtsboven in de bovenbalk (tijdens het lopen
 * "Stoppen"), een klein vizier, een hintbalk, de vraag "menu openen?" als je een afdeling binnenloopt en op een
 * telefoon een joystick linksonder. Geen three.js hier: dit zit in het hoofdbestand.
 */
import { useEffect, useRef, useState, type ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Footprints, X } from 'lucide-react';
import { useGame } from '../store/useGame';
import { useWorld, reducedMotion } from './useWorld';
import { useOfficeLoad } from './loadState';
import { useWalk, walkInput } from './walkState';
import { roomById, type RoomId } from './rooms';
import { selectRoom } from './select';

/** "Openen": rondlopen stoppen (muis weer los) en het menu van de afdeling openen, precies zoals een klik in Home. */
function openRoom(id: RoomId) {
  const r = roomById(id); if (!r) return;
  try { if (document.pointerLockElement) document.exitPointerLock(); } catch { /* */ }
  useWorld.getState().setWalk(false);
  selectRoom(r, 'home');
}
const stop = () => useWorld.getState().setWalk(false);

/** Knop rechtsboven: zichtbaar als het 3D-kantoor op Home staat. */
export function WalkButton() {
  const page = useGame((s) => s.page);
  const walk = useWorld((s) => s.walk);
  const ready = useWalk((s) => s.ready);
  const loaded = useOfficeLoad((s) => s.done);
  if (page !== 'driftmark' || !ready || !loaded) return null;
  const toggle = () => {
    const w = useWorld.getState();
    // lopen: open lades en meldingen gaan dicht, zodat niets het beeld bedekt
    if (!w.walk) { const g = useGame.getState(); g.setNotifOpen(false); g.selectAgent(null); g.selectProject(null); g.selectDept(null); }
    w.setWalk(!w.walk);
  };
  return (
    <button id="dm-walk" onClick={(e) => { e.currentTarget.blur(); toggle(); }} aria-pressed={walk}
      aria-label={walk ? 'Stoppen met rondlopen' : 'Rondlopen door het kantoor'} title={walk ? 'Stoppen met rondlopen (Esc)' : 'Rondlopen: zelf door het kantoor lopen'}
      className={`inline-flex items-center gap-1.5 rounded-xl border p-2 text-[13px] font-semibold transition xl:px-3 ${walk ? 'border-[#FF7A24]/80 bg-[#FF7A24]/25 text-white shadow-[0_0_16px_rgba(255,122,36,.4)]' : 'border-hq-line/60 bg-hq-panel/60 text-slate-300 hover:text-white'}`}>
      {walk ? <X size={18} /> : <Footprints size={18} />}
      <span className="hidden xl:inline">{walk ? 'Stoppen' : 'Rondlopen'}</span>
    </button>
  );
}

const Key = ({ children }: { children: ReactNode }) => <span className="rounded-md border border-white/20 bg-white/10 px-1.5 py-px font-mono text-[11px] font-bold text-white">{children}</span>;

function Crosshair() {
  return (
    <svg className="absolute left-1/2 top-1/2 -ml-3 -mt-3 h-6 w-6" viewBox="0 0 24 24" aria-hidden style={{ filter: 'drop-shadow(0 0 2px rgba(0,0,0,.9))' }}>
      <circle cx="12" cy="12" r="6.5" fill="none" stroke="rgba(255,255,255,.8)" strokeWidth="1.5" />
      <circle cx="12" cy="12" r="1.6" fill="#FFB070" />
    </svg>
  );
}

function Hint() {
  const touch = useWalk((s) => s.touch); const locked = useWalk((s) => s.locked); const noLock = useWalk((s) => s.noLock);
  if (touch) return (
    <div className="absolute inset-x-0 top-[74px] flex justify-center px-3 md:bottom-5 md:top-auto">
      <div className="holo-mini pointer-events-auto flex items-center gap-3 py-1.5 pl-3 pr-1.5 text-[13px] text-slate-200">
        <span>Linksonder: lopen · veeg: rondkijken</span>
        <button onClick={stop} className="rounded-lg bg-[#FF7A24]/25 px-2.5 py-1 text-[12px] font-bold text-white">Stoppen</button>
      </div>
    </div>
  );
  return (
    <div className="absolute inset-x-0 bottom-5 flex flex-col items-center gap-2 px-3">
      {!locked && !noLock && <div className="holo-mini px-3 py-1 text-[12px] font-semibold text-[#FFD2AE]">Klik in het kantoor om met de muis rond te kijken</div>}
      <div className="holo-mini flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 px-4 py-2 text-[13px] text-slate-200">
        <Key>WASD</Key> of <Key>pijltjes</Key>: lopen <span className="text-slate-500">·</span> <Key>Shift</Key>: sneller <span className="text-slate-500">·</span> {noLock ? 'slepen met de muis' : 'muis'}: rondkijken <span className="text-slate-500">·</span> <Key>Esc</Key>: stoppen
      </div>
    </div>
  );
}

/** Vraag bij het binnenlopen van een afdeling. Enter of E opent het menu, N sluit de vraag. */
function Prompt() {
  const ask = useWalk((s) => s.ask); const touch = useWalk((s) => s.touch);
  const r = roomById(ask);
  useEffect(() => {
    if (!ask) return;
    const k = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.repeat || (e.target as HTMLElement | null)?.closest?.('input,textarea,select,[contenteditable="true"]')) return;
      if (e.key === 'Enter' || e.code === 'KeyE') { e.preventDefault(); openRoom(ask); }
      else if (e.code === 'KeyN') { e.preventDefault(); useWalk.getState().dismiss(); }
    };
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k);
  }, [ask]);
  const rm = reducedMotion();
  return (
    <AnimatePresence>
      {r && (
        <motion.div key={r.id} id="dm-walk-vraag" role="dialog" aria-label={`Menu van ${r.naam} openen?`} className="absolute inset-x-0 bottom-[176px] flex justify-center px-3 md:bottom-[118px]"
          initial={{ opacity: 0, y: rm ? 0 : 14, scale: rm ? 1 : 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: rm ? 0 : 8 }} transition={{ duration: rm ? 0.1 : 0.25 }}>
          <div className="pointer-events-auto w-[min(92vw,420px)] rounded-2xl border bg-[#0b1130]/90 p-4 backdrop-blur" style={{ borderColor: `${r.color}99`, boxShadow: `0 0 30px ${r.color}38, 0 18px 50px rgba(0,0,0,.55)` }}>
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-[22px]" style={{ background: `${r.color}26`, boxShadow: `inset 0 0 0 1px ${r.color}88` }}>{r.icon}</span>
              <div className="min-w-0">
                <div className="text-[15px] font-bold leading-snug text-white">Je loopt de afdeling {r.naam} binnen</div>
                <div className="text-[13px] text-slate-300">Wil je het menu openen?</div>
              </div>
            </div>
            <div className="mt-3 flex gap-2">
              <button onClick={() => openRoom(r.id)} className="flex flex-1 items-center justify-center gap-2 rounded-xl px-3 py-2 text-[14px] font-bold text-white transition hover:brightness-125" style={{ background: `${r.color}40`, boxShadow: `inset 0 0 0 1px ${r.color}aa` }}>
                Openen{!touch && <Key>Enter</Key>}
              </button>
              <button onClick={() => useWalk.getState().dismiss()} className="flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-[14px] font-semibold text-slate-200 transition hover:bg-white/20">
                Nee{!touch && <Key>N</Key>}
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Joystick linksonder (aanraken): hoe verder je hem duwt, hoe harder je loopt. */
function Stick() {
  const touch = useWalk((s) => s.touch);
  const base = useRef<HTMLDivElement>(null); const id = useRef<number | null>(null);
  const [k, setK] = useState<[number, number]>([0, 0]);
  const R = 44;
  const put = (e: React.PointerEvent) => {
    const b = base.current?.getBoundingClientRect(); if (!b) return;
    let x = e.clientX - (b.left + b.width / 2), y = e.clientY - (b.top + b.height / 2);
    const L = Math.hypot(x, y); if (L > R) { x *= R / L; y *= R / L; }
    setK([x, y]); walkInput.jx = x / R; walkInput.jy = -y / R;
  };
  const end = () => { id.current = null; setK([0, 0]); walkInput.jx = walkInput.jy = 0; };
  useEffect(() => () => { walkInput.jx = walkInput.jy = 0; }, []);
  if (!touch) return null;
  return (
    <div ref={base} role="presentation" aria-label="Joystick om te lopen" className="pointer-events-auto absolute left-5 h-[132px] w-[132px] touch-none select-none rounded-full border border-white/25 bg-[#0b1130]/45 backdrop-blur-sm"
      style={{ bottom: 'calc(24px + env(safe-area-inset-bottom))', boxShadow: 'inset 0 0 24px rgba(32,217,255,.15)' }}
      onPointerDown={(e) => { id.current = e.pointerId; e.currentTarget.setPointerCapture(e.pointerId); put(e); }}
      onPointerMove={(e) => { if (id.current === e.pointerId) put(e); }}
      onPointerUp={end} onPointerCancel={end}>
      <div className="absolute left-1/2 top-1/2 h-[56px] w-[56px] rounded-full border border-white/50 bg-white/25 shadow-[0_0_18px_rgba(32,217,255,.4)]"
        style={{ transform: `translate(calc(-50% + ${k[0]}px), calc(-50% + ${k[1]}px))` }} />
    </div>
  );
}

/** Alles boven het beeld tijdens het rondlopen (in WorldLayer, boven het 3D-kantoor). */
export default function WalkHud() {
  const walk = useWorld((s) => s.walk);
  const page = useGame((s) => s.page);
  // vangnet: alleen op Home kun je rondlopen
  useEffect(() => { if (walk && page !== 'driftmark') stop(); }, [walk, page]);
  const rm = reducedMotion();
  return (
    <AnimatePresence>
      {walk && (
        <motion.div key="walk" id="dm-walk-hud" className="pointer-events-none absolute inset-0 z-20"
          initial={{ opacity: 0 }} animate={{ opacity: 1, transition: { duration: rm ? 0 : 0.35, delay: rm ? 0 : 0.9 } }} exit={{ opacity: 0, transition: { duration: rm ? 0 : 0.2 } }}>
          <Crosshair />
          <Hint />
          <Prompt />
          <Stick />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
