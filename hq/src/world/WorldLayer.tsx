import { Component, lazy, Suspense, useEffect, useMemo, useState, type ReactNode } from 'react';
import { hasWebGL, reducedMotion } from './useWorld';
import { useOfficeLoad } from './loadState';
import type { WorldMode } from './NeonOffice';
import WalkHud, { FloorButton } from './WalkHud';

const NeonOffice = lazy(() => import('./NeonOffice'));

class Boundary extends Component<{ children: ReactNode }, { err: boolean }> {
  state = { err: false };
  static getDerivedStateFromError() { return { err: true }; }
  componentDidCatch(e: unknown) { useOfficeLoad.setState({ failed: true, done: true }); console.warn('[HQ] 3D-kantoor fout', e); }
  render() { return this.state.err ? <Fallback text="Het 3D-kantoor liep vast op dit apparaat. Alle knoppen en panelen werken gewoon." /> : this.props.children; }
}

function Fallback({ text }: { text: string }) {
  return (
    <div className="dm-world-fallback absolute inset-0">
      <div className="absolute bottom-24 left-1/2 w-[min(90vw,420px)] -translate-x-1/2 rounded-xl border border-white/10 bg-black/40 px-4 py-2 text-center text-[13px] text-slate-300 backdrop-blur">{text}</div>
    </div>
  );
}

/** De blijvende 3D-wereld achter alle schermen. Wordt één keer geladen en blijft staan bij paginawissels. */
export default function WorldLayer({ mode }: { mode: WorldMode }) {
  const gl = useMemo(() => hasWebGL(), []);
  if (!gl) return <Fallback text="Dit apparaat ondersteunt geen 3D (WebGL). Je ziet de HQ zonder kantoor; alle functies werken." />;
  return (
    <div className="absolute inset-0 z-0">
      <Boundary>
        <Suspense fallback={<div className="dm-world-fallback absolute inset-0" />}>
          <NeonOffice mode={mode} />
        </Suspense>
      </Boundary>
      <LoadingScreen />
      {/* lichte waas als er een paneel open is, zodat de tekst leesbaar blijft */}
      <div className={`pointer-events-none absolute inset-0 transition-opacity duration-700 ${mode === 'panel' ? 'opacity-100' : 'opacity-0'}`}
        style={{ background: 'radial-gradient(ellipse at center, rgba(5,8,22,.5) 0%, rgba(5,8,22,.25) 75%)' }} />
      {/* rondlopen: vizier, hint, vraag bij een afdeling en joystick */}
      <WalkHud />
      {/* knopje rechts in het midden: naar de bovenverdieping en terug */}
      <FloorButton />
    </div>
  );
}

const TIPS = ['Tip: houd de scrollknop ingedrukt om rond het kantoor te draaien.', 'Tip: klik op een afdeling voor het team, de taken en het gereedschap.', 'Tip: met het luidsprekertje bovenin kies je dag, nacht of feest.', 'Tip: in elke afdeling kun je praten met de agents.'];
/** Laadscherm met logo en voortgang, tot het 3D-kantoor er staat. */
function LoadingScreen() {
  const { p, stap, done } = useOfficeLoad();
  const [weg, setWeg] = useState(false);
  const [tip] = useState(() => TIPS[Math.floor(Math.random() * TIPS.length)]);
  useEffect(() => { if (!done) return; const t = setTimeout(() => setWeg(true), reducedMotion() ? 0 : 900); return () => clearTimeout(t); }, [done]);
  // nooit langer dan 25 s in beeld (dan toont het HQ gewoon het eenvoudige kantoor)
  useEffect(() => { const t = setTimeout(() => setWeg(true), 25000); return () => clearTimeout(t); }, []);
  if (weg) return null;
  return (
    <div className={`pointer-events-none absolute inset-0 z-30 flex flex-col items-center justify-center bg-[radial-gradient(ellipse_at_center,#101a4a_0%,#060a1c_70%)] transition-opacity duration-700 ${done ? 'opacity-0' : 'opacity-100'}`} role="status" aria-live="polite">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-400 via-orange-500 to-[#ff5f3d] shadow-[0_0_50px_rgba(255,122,36,.55)]"><svg viewBox="0 0 24 24" className="h-7 w-7 fill-white"><path d="M8 5.5v13l11-6.5z" /></svg></div>
      <div className="font-display text-[26px] font-bold tracking-wide text-white">DRIFTMARK <span className="text-[#398CFF]">HQ</span></div>
      <div className="mt-5 h-1.5 w-[min(70vw,320px)] overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-[#FF7A24] to-[#398CFF] transition-[width] duration-300" style={{ width: `${Math.round(p * 100)}%` }} /></div>
      <div className="mt-2 text-[13px] text-slate-400">{stap} {Math.round(p * 100)}%</div>
      <div className="mt-6 max-w-[min(86vw,420px)] text-center text-[12px] text-slate-500">{tip}</div>
    </div>
  );
}
