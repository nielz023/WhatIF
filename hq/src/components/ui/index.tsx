import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
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
  'In Progress': 'bg-indigo-500/15 text-indigo-300 ring-indigo-400/30',
  Review: 'bg-amber-500/15 text-amber-300 ring-amber-400/30',
  Approved: 'bg-teal-500/15 text-teal-300 ring-teal-400/30',
  Rejected: 'bg-rose-500/15 text-rose-300 ring-rose-400/30',
  Completed: 'bg-emerald-500/15 text-emerald-300 ring-emerald-400/30',
};
export function StatusBadge({ status }: { status: TaskStatus | string }) {
  const cls = STATUS_STYLE[status as TaskStatus] ?? 'bg-slate-500/15 text-slate-300 ring-slate-400/30';
  return <span className={`chip ring-1 ${cls}`}>{status}</span>;
}

const PRIO: Record<Priority, string> = {
  Low: 'text-slate-400 bg-slate-500/10', Medium: 'text-sky-300 bg-sky-500/10', High: 'text-orange-300 bg-orange-500/10', Critical: 'text-rose-300 bg-rose-500/15',
};
export const PriorityBadge = ({ p }: { p: Priority }) => <span className={`chip ${PRIO[p]}`}>{p}</span>;

export const StateDot = ({ state }: { state: Agent['state'] }) => {
  const c = { working: 'bg-emerald-400', meeting: 'bg-sky-400', idle: 'bg-slate-400', training: 'bg-purple-400' }[state];
  return <span className="inline-flex items-center gap-1.5 text-xs capitalize text-slate-300"><span className={`h-2 w-2 rounded-full ${c} shadow-[0_0_8px_currentColor]`} />{state}</span>;
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
    <button onClick={onClick} disabled={!onClick} className="panel group relative overflow-hidden p-4 text-left transition enabled:hover:-translate-y-0.5 enabled:hover:border-indigo-400/50 disabled:cursor-default">
      <div className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full opacity-25 blur-2xl" style={{ background: color }} />
      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        {label}
        {icon && <span style={{ color }}>{icon}</span>}
      </div>
      <div className="mt-1.5 font-display text-2xl font-bold text-white">{value}</div>
      {sub && <div className="mt-0.5 text-xs text-slate-400">{sub}</div>}
    </button>
  );
}

export function Modal({ open, onClose, title, children, width = 560, footer }: { open: boolean; onClose: () => void; title: ReactNode; children: ReactNode; width?: number; footer?: ReactNode }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={onClose}>
          <motion.div
            className="panel flex max-h-[90vh] w-full flex-col border-indigo-500/30"
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
          className="panel fixed bottom-20 right-3 top-[76px] z-[60] flex flex-col rounded-2xl border-indigo-500/30"
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

export const DemoBadge = ({ label = 'DEMO DATA' }: { label?: string }) => (
  <span className="chip bg-amber-500/15 text-[10px] tracking-wider text-amber-300 ring-1 ring-amber-400/30">{label}</span>
);

export const SimBadge = () => (
  <span className="chip bg-cyan-500/10 text-[10px] tracking-wider text-cyan-300 ring-1 ring-cyan-400/30">LOCAL SIMULATION</span>
);

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight text-white md:text-3xl">{title}</h1>
        {subtitle && <div className="mt-1 text-sm text-slate-400">{subtitle}</div>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export const RoleLabel = ({ agent }: { agent: Agent }) => <span className="text-xs text-slate-400">{roleById(agent.role).title}</span>;

export function Empty({ children }: { children: ReactNode }) {
  return <div className="rounded-xl border border-dashed border-hq-line p-6 text-center text-sm text-slate-500">{children}</div>;
}

export function Tabs<T extends string>({ value, onChange, items }: { value: T; onChange: (v: T) => void; items: { id: T; label: ReactNode }[] }) {
  return (
    <div className="inline-flex flex-wrap gap-1 rounded-xl border border-hq-line bg-hq-bg/60 p-1">
      {items.map((i) => (
        <button key={i.id} onClick={() => onChange(i.id)} className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${value === i.id ? 'bg-indigo-500/25 text-white shadow-neon' : 'text-slate-400 hover:text-white'}`}>
          {i.label}
        </button>
      ))}
    </div>
  );
}
