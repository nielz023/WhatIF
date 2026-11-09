import { Component, lazy, Suspense, useEffect, useMemo, useState, type ReactNode } from 'react';
import { hasWebGL, reducedMotion, useWorld } from './useWorld';
import { useOfficeLoad } from './loadState';
import type { WorldMode } from './NeonOffice';
import WalkHud, { FloorButton } from './WalkHud';

/* Sneller openen (verbeterlijst punt 68): het 3D-kantoor (three.js, ~1,3 MB code en ~15 MB modellen) laadt pas
 * als niels het kantoor of de studio opent. Gewone pagina's staan er dan binnen een paar seconden. Daarna blijft het
 * kantoor staan bij paginawissels. Als de pagina even stil is, halen we alvast de code (niet de modellen) op. */
const laadOffice = () => import('./NeonOffice');
/* praten met de figuurtjes en de games horen bij het kantoor: zelfde moment laden */
const TalkLayer = lazy(() => import('./TalkPanel'));
const NeonOffice = lazy(laadOffice);
let voorgeladen = false;
function voorladen() {
  if (voorgeladen) return; voorgeladen = true;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ric = (window as any).requestIdleCallback as ((f: () => void, o?: { timeout: number }) => number) | undefined;
  const go = () => void laadOffice().catch(() => { voorgeladen = false; });
  if (ric) ric(go, { timeout: 8000 }); else setTimeout(go, 1000);
}
/** zodra het kantoor één keer nodig is, blijft het gemount */
function useOfficeNodig(mode: WorldMode) {
  const walk = useWorld((s) => s.walk);
  const [nodig, setNodig] = useState(mode !== 'panel' || walk);
  useEffect(() => { if (mode !== 'panel' || walk) setNodig(true); }, [mode, walk]);
  useEffect(() => {
    if (nodig) return;
    const t = setTimeout(voorladen, 20000); // na 20 s rust alvast de code ophalen
    return () => clearTimeout(t);
  }, [nodig]);
  return nodig;
}

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
  const nodig = useOfficeNodig(mode);
  if (!gl) return <Fallback text="Dit apparaat ondersteunt geen 3D (WebGL). Je ziet de HQ zonder kantoor; alle functies werken." />;
  return (
    <div className="absolute inset-0 z-0">
      {/* nachtlucht achter de pagina's; het kantoor tekent eroverheen zodra het geladen is */}
      <div className="dm-world-fallback absolute inset-0" />
      {nodig && (
        <Boundary>
          <Suspense fallback={null}>
            <NeonOffice mode={mode} />
          </Suspense>
        </Boundary>
      )}
      {nodig && <LoadingScreen />}
      {/* lichte waas als er een paneel open is, zodat de tekst leesbaar blijft */}
      <div className={`pointer-events-none absolute inset-0 transition-opacity duration-700 ${mode === 'panel' ? 'opacity-100' : 'opacity-0'}`}
        style={{ background: 'radial-gradient(ellipse at center, rgba(5,8,22,.5) 0%, rgba(5,8,22,.25) 75%)' }} />
      {/* rondlopen: vizier, hint, vraag bij een afdeling en joystick */}
      <WalkHud />
      {/* knopje rechts in het midden: naar de bovenverdieping en terug */}
      <FloorButton />
      {/* praten met de figuurtjes en zelf gamen in de game room */}
      {nodig && <Suspense fallback={null}><TalkLayer /></Suspense>}
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
      <img src="./merk/logo.webp" alt="" width={72} height={72} className="dm-logo mb-4 h-[72px] w-[72px] rounded-2xl" />
      <img src="./merk/woordmerk.webp" alt="Driftmark" width={240} height={43} className="dm-woordmerk h-[43px] w-[240px]" />
      <div className="mt-1 text-[11px] font-bold uppercase tracking-[.4em] text-[#7fb3ff]">3D-kantoor</div>
      <div className="mt-6 h-2 w-[min(70vw,320px)] overflow-hidden rounded-full bg-white/10 shadow-[inset_0_1px_2px_rgba(0,0,0,.5)]"><div className="h-full rounded-full bg-gradient-to-r from-[#FF7A24] to-[#398CFF] shadow-[0_0_14px_rgba(255,122,36,.55)] transition-[width] duration-300" style={{ width: `${Math.max(3, Math.round(p * 100))}%` }} /></div>
      <div className="mt-2 text-[13px] text-slate-400">{stap} <span className="tabular-nums">{Math.round(p * 100)}%</span></div>
      <div className="mt-6 max-w-[min(86vw,420px)] text-center text-[12px] text-slate-500">{tip}</div>
    </div>
  );
}
