import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { useEffect, useRef, useState, type ReactNode } from 'react';
import type { Agent, Priority, TaskStatus } from '../../types';
import { roleById } from '../../modules/agents/roles';

export function Avatar({ agent, size = 36, ring }: { agent?: Agent | null; size?: number; ring?: boolean }) {
  if (!agent) {
    return (
      <div className="flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-600 font-bold text-white" style={{ width: size, height: size, fontSize: size * 0.38 }}>
        👑
      </div>
    );
  }
  const { skin, hair, shirt, initials } = agent.avatar;
  return (
    <div
      className="relative flex shrink-0 items-end justify-center overflow-hidden rounded-full"
      style={{ width: size, height: size, background: `linear-gradient(160deg, ${shirt}55, #0b1024)`, boxShadow: ring ? `0 0 0 2px ${shirt}, 0 0 14px ${shirt}88` : `0 0 0 1px ${shirt}66` }}
      title={agent.name}
    >
      <div className="absolute rounded-full" style={{ width: size * 0.46, height: size * 0.46, top: size * 0.16, background: skin }} />
      <div className="absolute rounded-t-full" style={{ width: size * 0.5, height: size * 0.24, top: size * 0.12, background: hair }} />
      <div className="absolute rounded-t-full" style={{ width: size * 0.78, height: size * 0.34, bottom: -size * 0.04, background: shirt }} />
      <span className="absolute bottom-0 right-0 rounded-full bg-slate-950/80 px-1 text-[8px] font-bold text-white" style={{ fontSize: Math.max(7, size * 0.2) }}>{initials}</span>
    </div>
  );
}

const STATUS_STYLE: Record<TaskStatus, string> = {
  Pending: 'bg-slate-500/15 text-slate-300 ring-slate-400/30',
  Assigned: 'bg-sky-500/15 text-sky-300 ring-sky-400/30',
  'In Progress': 'bg-sky-500/15 text-sky-300 ring-sky-400/30',
  Review: 'bg-amber-500/15 text-amber-300 ring-amber-400/30',
  Approved: 'bg-teal-500/15 text-teal-300 ring-teal-400/30',
  Rejected: 'bg-rose-500/15 text-rose-300 ring-rose-400/30',
  Completed: 'bg-emerald-500/15 text-emerald-300 ring-emerald-400/30',
};
/** Statussen blijven in de logica Engels, maar je ziet ze altijd in het Nederlands (verbeterlijst punt 39). */
export const STATUS_NL: Record<string, string> = {
  Pending: 'Wacht', Assigned: 'Toegewezen', 'In Progress': 'Bezig', Review: 'Controle', Approved: 'Goedgekeurd', Rejected: 'Afgekeurd', Completed: 'Klaar',
  Active: 'Actief', 'Awaiting Approval': 'Wacht op jouw akkoord', 'Awaiting Publish': 'Klaar voor upload', Published: 'Online', Cancelled: 'Gestopt',
};
export function StatusBadge({ status }: { status: TaskStatus | string }) {
  const cls = STATUS_STYLE[status as TaskStatus] ?? 'bg-slate-500/15 text-slate-300 ring-slate-400/30';
  return <span className={`chip ring-1 ${cls}`}>{STATUS_NL[status] ?? status}</span>;
}

const PRIO: Record<Priority, string> = {
  Low: 'text-slate-400 bg-slate-500/10', Medium: 'text-sky-300 bg-sky-500/10', High: 'text-orange-300 bg-orange-500/10', Critical: 'text-rose-300 bg-rose-500/15',
};
const PRIO_NL: Record<Priority, string> = { Low: 'Laag', Medium: 'Normaal', High: 'Hoog', Critical: 'Spoed' };
export const PriorityBadge = ({ p }: { p: Priority }) => <span className={`chip ${PRIO[p]}`}>{PRIO_NL[p] ?? p}</span>;

export const StateDot = ({ state }: { state: Agent['state'] }) => {
  const c = { working: 'bg-emerald-400', meeting: 'bg-sky-400', idle: 'bg-slate-400', training: 'bg-purple-400' }[state];
  return <span className="inline-flex items-center gap-1.5 text-[13px] capitalize text-slate-300"><span className={`h-2 w-2 rounded-full ${c} shadow-[0_0_8px_currentColor]`} />{{ working: 'aan het werk', meeting: 'in overleg', idle: 'vrij', training: 'in training' }[state] ?? state}</span>;
};

export function Progress({ value, color = '#6366f1', h = 6 }: { value: number; color?: string; h?: number }) {
  return (
    <div className="w-full overflow-hidden rounded-full bg-slate-800/80" style={{ height: h }}>
      <motion.div className="h-full rounded-full" style={{ background: `linear-gradient(90deg, ${color}aa, ${color})`, boxShadow: `0 0 10px ${color}88` }} initial={false} animate={{ width: `${Math.max(0, Math.min(100, value))}%` }} transition={{ duration: 0.5 }} />
    </div>
  );
}

export function StatCard({ label, value, sub, icon, color = '#6366f1', onClick }: { label: string; value: ReactNode; sub?: ReactNode; icon?: ReactNode; color?: string; onClick?: () => void }) {
  return (
    <button onClick={onClick} disabled={!onClick} className="panel group relative overflow-hidden p-4 text-left transition enabled:hover:-translate-y-0.5 enabled:hover:border-sky-400/50 disabled:cursor-default">
      <div className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full opacity-25 blur-2xl" style={{ background: color }} />
      <div className="flex items-center justify-between text-[13px] font-semibold uppercase tracking-wider text-slate-400">
        {label}
        {icon && <span style={{ color }}>{icon}</span>}
      </div>
      <div className="getal mt-1.5 text-2xl text-white"><Telt value={value} /></div>
      {sub && <div className="mt-0.5 text-[13px] text-slate-400">{sub}</div>}
    </button>
  );
}

export function Modal({ open, onClose, title, children, width = 560, footer }: { open: boolean; onClose: () => void; title: ReactNode; children: ReactNode; width?: number; footer?: ReactNode }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={onClose}>
          <motion.div
            className="panel flex max-h-[90vh] w-full flex-col border-sky-500/30"
            style={{ maxWidth: width }}
            initial={{ y: 24, scale: 0.97 }} animate={{ y: 0, scale: 1 }} exit={{ y: 16, opacity: 0 }}
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-hq-line/70 px-5 py-4">
              <div className="h-title text-lg">{title}</div>
              <button className="rounded-lg p-1 text-slate-400 hover:bg-white/5 hover:text-white" onClick={onClose} aria-label="Close"><X size={18} /></button>
            </div>
            <div className="overflow-y-auto px-5 py-4">{children}</div>
            {footer && <div className="flex justify-end gap-2 border-t border-hq-line/70 px-5 py-3">{footer}</div>}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function Drawer({ open, onClose, children, width = 520, title }: { open: boolean; onClose: () => void; children: ReactNode; width?: number; title?: ReactNode }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          className="panel fixed bottom-20 right-3 top-[76px] z-[60] flex flex-col rounded-2xl border-sky-500/30"
          style={{ width: `min(${width}px, calc(100vw - 24px))` }}
          initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 40, opacity: 0 }}
          transition={{ type: 'spring', damping: 26, stiffness: 260 }}
        >
          <div className="flex items-center justify-between border-b border-hq-line/70 px-5 py-3">
            <div className="h-title text-base">{title}</div>
            <button className="rounded-lg p-1 text-slate-400 hover:bg-white/5 hover:text-white" onClick={onClose} aria-label="Close"><X size={18} /></button>
          </div>
          <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}

export const DemoBadge = ({ label = 'VOORBEELD' }: { label?: string }) => (
  <span className="chip bg-amber-500/15 text-[12px] tracking-wider text-amber-300 ring-1 ring-amber-400/30">{label}</span>
);

export const SimBadge = () => (
  <span className="chip bg-cyan-500/10 text-[12px] tracking-wider text-cyan-300 ring-1 ring-cyan-400/30">LOCAL SIMULATION</span>
);

/** Paginakop in de huisstijl: titel (kop-1), korte uitleg en knoppen rechts. */
export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        <h1 className="kop-1 text-2xl md:text-3xl">{title}</h1>
        <div className="mt-2 h-[3px] w-12 rounded-full bg-gradient-to-r from-[#FF7A24] to-[#398CFF] shadow-[0_0_12px_rgba(255,122,36,.45)]" />
        {subtitle && <div className="mt-2 max-w-2xl text-sm text-slate-400">{subtitle}</div>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export const RoleLabel = ({ agent }: { agent: Agent }) => <span className="text-[13px] text-slate-400">{roleById(agent.role).title}</span>;

/**
 * Lege plek met uitleg (verbeterlijst punt 31): nooit een leeg vak of een nul, maar wat hier komt en wanneer.
 * `titel` is de korte zin, `children` de uitleg, `actie` een knop om het te vullen.
 */
export function Empty({ children, titel, icon, actie }: { children?: ReactNode; titel?: ReactNode; icon?: ReactNode; actie?: ReactNode }) {
  return (
    <div className="leeg">
      {icon && <div className="mb-1 flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/10 text-sky-300">{icon}</div>}
      {titel && <div className="text-sm font-semibold text-slate-200">{titel}</div>}
      {children && <div className="max-w-md text-[13px] leading-relaxed text-slate-400">{children}</div>}
      {actie && <div className="mt-2">{actie}</div>}
    </div>
  );
}

/** Getal dat zacht optelt (punt 32). Alleen de eerste keer vanaf nul; bij een nieuwe waarde loopt hij kort
 *  van de oude naar de nieuwe stand, zodat er bij verversen niets springt. Tekst die geen getal is blijft zoals hij is.
 *  Bij minder beweging (.dm-rustig) staat het getal er meteen. */
export function Telt({ value, duur = 700 }: { value: ReactNode; duur?: number }) {
  const doel = typeof value === 'number' ? value : typeof value === 'string' ? leesGetal(value) : null;
  const [toon, setToon] = useState<number | null>(() => (doel == null || rustig() ? doel : 0));
  const vanRef = useRef<number>(0);
  useEffect(() => {
    if (doel == null) return;
    const van = toon ?? 0;
    if (rustig() || van === doel) { setToon(doel); return; }
    vanRef.current = van;
    let raf = 0; let t0 = -1;
    const stap = (t: number) => {
      if (t0 < 0) t0 = t; // tijd van het eerste beeld (rAF-tijd kan vóór performance.now() liggen)
      const k = Math.max(0, Math.min(1, (t - t0) / duur)); const e = 1 - Math.pow(1 - k, 3);
      setToon(vanRef.current + (doel - vanRef.current) * e);
      if (k < 1) raf = requestAnimationFrame(stap);
    };
    raf = requestAnimationFrame(stap);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doel]);
  if (doel == null || toon == null || toon === doel) return <>{value}</>;
  if (typeof value === 'string') return <>{zetTerug(value, toon, doel)}</>;
  return <>{String(Math.round(toon))}</>;
}
const rustig = () => { try { return document.documentElement.classList.contains('dm-rustig'); } catch { return true; } };
/** "1.234", "+31", "21,9K" of "66,1%": het getal eruit, anders null */
function leesGetal(s: string): number | null {
  const m = /^([+-]?)(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?([KkMm%]?)$/.exec(s.trim());
  if (!m) return null;
  const n = parseFloat(m[2].replace(/\./g, '') + (m[3] ? '.' + m[3] : ''));
  return m[1] === '-' ? -n : n;
}
function zetTerug(orig: string, n: number, doel: number) {
  if (n === doel) return orig;
  const m = /^([+-]?)(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?([KkMm%]?)$/.exec(orig.trim())!;
  const dec = m[3]?.length ?? 0;
  const txt = Math.abs(n).toLocaleString('nl-NL', { minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: m[2].includes('.') || Math.abs(doel) >= 10000 });
  return `${m[1] === '+' ? '+' : n < 0 ? '-' : ''}${txt}${m[4]}`;
}

export function Tabs<T extends string>({ value, onChange, items }: { value: T; onChange: (v: T) => void; items: { id: T; label: ReactNode }[] }) {
  return (
    <div className="inline-flex flex-wrap gap-1 rounded-xl border border-hq-line bg-hq-bg/60 p-1">
      {items.map((i) => (
        <button key={i.id} onClick={() => onChange(i.id)} className={`rounded-lg px-3 py-1.5 text-[13px] font-semibold transition ${value === i.id ? 'bg-sky-500/25 text-white shadow-neon' : 'text-slate-400 hover:text-white'}`}>
          {i.label}
        </button>
      ))}
    </div>
  );
}
