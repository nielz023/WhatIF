import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { BarChart3, Clapperboard, LineChart, Sparkles, Layers, LayoutGrid, Home, LayoutDashboard, SquarePlay, MessageSquare } from 'lucide-react';
import { useShallow } from 'zustand/react/shallow';
import { useGame } from '../../store/useGame';
import { useLive, type Activity } from '../../services/live';
import { openGesprek } from '../shared/Gesprek';
import { mainOf } from './Sidebar';
import type { PageId } from '../../types';

/** De zwevende glazen hoofdnavigatie boven het kantoor. */
const ITEMS: { id: PageId; label: string; icon: typeof BarChart3; uitleg: string }[] = [
  { id: 'driftmark', label: 'Overzicht', icon: BarChart3, uitleg: 'Het 3D-kantoor: je hele bedrijf in één blik' },
  { id: 'videos', label: "Video's", icon: Clapperboard, uitleg: 'Elke video van idee tot upload, plus shorts' },
  { id: 'kanaal', label: 'Kanaal', icon: SquarePlay, uitleg: 'Abonnees, weergaven, kijkduur en cursusmeter' },
  { id: 'coach', label: 'Coach', icon: Sparkles, uitleg: 'Je CEO Coach: gesprek, briefing, doelen, beslissingen' },
  { id: 'hq', label: 'Studio', icon: Layers, uitleg: 'Het kantoor beheren: teamleden, projecten, spel' },
  { id: 'meer', label: 'Meer', icon: LayoutGrid, uitleg: 'Taken, werkwijze, cast, gereedschap, koppelingen' },
];

const ago = (iso?: string) => {
  const t = Date.parse(iso ?? ''); if (isNaN(t)) return '';
  const m = Math.max(0, Math.round((Date.now() - t) / 60000));
  return m < 1 ? 'net' : m < 60 ? `${m} min` : m < 48 * 60 ? `${Math.round(m / 60)} uur` : `${Math.round(m / 1440)} dagen`;
};
const wacht = (a: Activity) => a.state === 'blocked' || a.state === 'review_ready';

/** Lijstje onder de knop: waar de meldingen precies voor zijn (niels 2026-11-06: na een halve seconde met de muis erop). */
function WachtLijst({ items, onPick }: { items: Activity[]; onPick: () => void }) {
  const shown = items.slice(0, 6);
  return (
    <motion.div id="dm-wachtlijst" role="tooltip" initial={{ opacity: 0, y: -6, x: '-50%' }} animate={{ opacity: 1, y: 0, x: '-50%' }} exit={{ opacity: 0, y: -6, x: '-50%' }} transition={{ duration: 0.16 }}
      className="absolute left-1/2 top-full z-50 mt-2 w-[360px] rounded-2xl border border-[#FF7A24]/35 bg-[#0b1130]/95 p-2 text-left shadow-[0_18px_50px_rgba(0,0,0,.55),0_0_24px_rgba(255,122,36,.18)] backdrop-blur">
      <div className="px-2 pb-1 pt-0.5 text-[11px] font-bold uppercase tracking-widest text-[#FF9A52]">{items.length} {items.length === 1 ? 'ding wacht' : 'dingen wachten'} op jou</div>
      <ul className="space-y-0.5">
        {shown.map((a) => {
          const klaar = a.state === 'review_ready';
          const wat = a.needs || a.doing || (klaar ? 'Klaar om te bekijken.' : 'Wacht op jouw antwoord.');
          const inner = (<>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: klaar ? '#FACC15' : '#FF9F1C', boxShadow: `0 0 8px ${klaar ? '#FACC15' : '#FF9F1C'}` }} />
              <span className="min-w-0 flex-1 truncate text-[13px] font-semibold text-white">{a.title}</span>
              <span className="shrink-0 text-[11px] text-slate-500">{klaar ? 'bekijken' : 'jouw beurt'}{ago(a.lastIso) && ` · ${ago(a.lastIso)}`}</span>
            </div>
            <div className="mt-0.5 line-clamp-2 pl-4 text-[12px] leading-snug text-slate-300">{wat}</div>
          </>);
          return (
            <li key={a.id || a.session || a.title}>
              {a.session
                ? <button onClick={() => { onPick(); openGesprek({ kind: 'thread', session: a.session!, title: a.title, thread: a.id || undefined }); }} className="group/w block w-full rounded-xl px-2 py-1.5 text-left hover:bg-white/[.07]" title="Hele gesprek openen">{inner}<div className="hidden pl-4 pt-0.5 text-[11px] text-[#7fd8ff] group-hover/w:flex group-hover/w:items-center group-hover/w:gap-1"><MessageSquare size={11} />Gesprek openen</div></button>
                : <div className="rounded-xl px-2 py-1.5">{inner}</div>}
            </li>
          );
        })}
      </ul>
      {items.length > shown.length && <div className="px-2 pt-1 text-[11px] text-slate-500">En nog {items.length - shown.length}. Alles staat in Meer › Alle taken.</div>}
    </motion.div>
  );
}

export default function GlassNav() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const items = useLive(useShallow((s) => s.data.activity.filter(wacht).sort((a, b) => (Date.parse(b.lastIso ?? '') || 0) - (Date.parse(a.lastIso ?? '') || 0))));
  const waiting = items.length;
  const cur = mainOf(page);
  const [open, setOpen] = useState(false);
  const openRef = useRef(false); openRef.current = open;
  const timer = useRef<number | undefined>(undefined);
  const enter = () => { window.clearTimeout(timer.current); if (!openRef.current) timer.current = window.setTimeout(() => setOpen(true), 500); };
  const leave = () => { window.clearTimeout(timer.current); timer.current = window.setTimeout(() => setOpen(false), 220); };
  const close = () => { window.clearTimeout(timer.current); setOpen(false); };
  useEffect(() => () => window.clearTimeout(timer.current), []);
  useEffect(() => { if (!waiting) close(); }, [waiting]);
  return (
    <nav className="pointer-events-auto relative z-40 hidden justify-center px-4 pb-1 pt-2 md:flex" aria-label="Hoofdnavigatie">
      <div className="flex gap-2 lg:gap-3">
        {ITEMS.map(({ id, label, icon: Icon, uitleg }, i) => {
          const active = cur === id;
          const lijst = id === 'driftmark' && waiting > 0;
          return (
            <div key={id} className="relative" style={{ perspective: 900 }} onMouseEnter={lijst ? enter : undefined} onMouseLeave={lijst ? leave : undefined}>
              <button onClick={() => { if (lijst) close(); setPage(id); }} title={lijst ? undefined : uitleg} data-active={active} className="glass-btn group" style={{ ['--ry' as string]: `${(i - 2.5) * -5}deg` }} aria-current={active ? 'page' : undefined}
                aria-describedby={lijst && open ? 'dm-wachtlijst' : undefined} onFocus={lijst ? enter : undefined} onBlur={lijst ? leave : undefined}>
                <Icon size={26} className="glass-btn-ico" />
                <span>{label}</span>
                {lijst && <span className="absolute -right-1.5 -top-1.5 min-w-[20px] rounded-full bg-[#FF7A24] px-1 text-center text-[11px] font-bold text-white shadow-[0_0_10px_#FF7A24]">{waiting}</span>}
              </button>
              <AnimatePresence>{lijst && open && <WachtLijst key="wacht" items={items} onPick={close} />}</AnimatePresence>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

const SIDE: { id: PageId; label: string; icon: typeof Home }[] = [
  { id: 'driftmark', label: 'HQ', icon: Home },
  { id: 'overzicht', label: 'Dagoverzicht', icon: LayoutDashboard },
  { id: 'videos', label: "Video's", icon: Clapperboard },
  { id: 'kanaal', label: 'Kanaal', icon: LineChart },
  { id: 'coach', label: 'Coach', icon: Sparkles },
  { id: 'hq', label: 'Studio', icon: Layers },
  { id: 'meer', label: 'Meer', icon: LayoutGrid },
];

/** Zwevende glazen zijbalk links (zoals op het referentiebeeld), alleen op grote schermen. */
export function GlassSide() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  return (
    <aside className="glass-side pointer-events-auto absolute left-4 top-2 z-30 hidden w-[190px] p-2.5 xl:block" aria-label="Zijbalk">
      {SIDE.map(({ id, label, icon: Icon }) => {
        const active = page === id || (id === 'hq' && mainOf(page) === 'hq');
        return (
          <button key={id} onClick={() => setPage(id)} data-active={active} className="glass-side-btn">
            <Icon size={20} /><span>{label}</span>
          </button>
        );
      })}
    </aside>
  );
}
