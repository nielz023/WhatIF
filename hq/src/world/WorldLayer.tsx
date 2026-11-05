import { Component, lazy, Suspense, useMemo, type ReactNode } from 'react';
import { hasWebGL } from './useWorld';
import type { WorldMode } from './NeonOffice';

const NeonOffice = lazy(() => import('./NeonOffice'));

class Boundary extends Component<{ children: ReactNode }, { err: boolean }> {
  state = { err: false };
  static getDerivedStateFromError() { return { err: true }; }
  componentDidCatch(e: unknown) { console.warn('[HQ] 3D-kantoor fout', e); }
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
      {/* lichte waas als er een paneel open is, zodat de tekst leesbaar blijft */}
      <div className={`pointer-events-none absolute inset-0 transition-opacity duration-700 ${mode === 'panel' ? 'opacity-100' : 'opacity-0'}`}
        style={{ background: 'radial-gradient(ellipse at center, rgba(5,8,22,.5) 0%, rgba(5,8,22,.25) 75%)' }} />
    </div>
  );
}
