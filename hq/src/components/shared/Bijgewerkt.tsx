import { RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { useLive } from '../../services/live';

const geleden = (iso?: string | number | null) => {
  const t = typeof iso === 'number' ? iso : Date.parse(iso ?? '');
  if (!t || isNaN(t)) return null;
  const m = Math.max(0, Math.round((Date.now() - t) / 60000));
  const tijd = new Date(t).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' });
  return m < 1 ? `net (${tijd})` : m < 60 ? `${m} min geleden (${tijd})` : m < 48 * 60 ? `${Math.round(m / 60)} uur geleden (${tijd})` : tijd;
};

/**
 * "Bijgewerkt om ..." met de bron en een ververs-knopje (verbeterlijst punten 22, 40 en 72).
 * Zonder `at` neemt hij de tijd van de live stand.
 */
export default function Bijgewerkt({ at, bron, className = '' }: { at?: string | number | null; bron?: string; className?: string }) {
  const live = useLive();
  const [bezig, setBezig] = useState(false);
  const wanneer = geleden(at ?? live.data.updated);
  const offline = live.source === 'fout' || live.source === 'geen-toegang';
  return (
    <span className={`inline-flex flex-wrap items-center gap-1.5 text-[12px] text-slate-500 ${className}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${offline ? 'bg-amber-400' : 'bg-emerald-400'}`} />
      {offline ? 'Laatst bekende stand' : 'Bijgewerkt'} {wanneer ?? 'onbekend'}{bron ? ` · ${bron}` : ''}
      <button onClick={async () => { setBezig(true); try { await live.refresh(); } finally { setBezig(false); } }} className="inline-flex items-center gap-1 rounded px-1 text-sky-300 hover:text-white" title="Nu verversen" aria-label="Nu verversen">
        <RefreshCw size={11} className={bezig ? 'animate-spin' : ''} />
      </button>
    </span>
  );
}
