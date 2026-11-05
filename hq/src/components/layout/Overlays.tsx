import { AnimatePresence, motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Modal } from '../ui';

export function Toasts() {
  const toasts = useGame((s) => s.toasts);
  const dismiss = useGame((s) => s.dismissToast);
  return (
    <div className="pointer-events-none fixed bottom-24 left-1/2 z-[100] flex -translate-x-1/2 flex-col items-center gap-2">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.button
            key={t.id}
            layout
            initial={{ opacity: 0, y: 12, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8 }}
            onClick={() => dismiss(t.id)}
            className={`pointer-events-auto rounded-xl border px-4 py-2 text-sm font-medium shadow-2xl backdrop-blur-xl ${
              t.kind === 'success' ? 'border-emerald-400/40 bg-emerald-950/80 text-emerald-100' : t.kind === 'warning' ? 'border-amber-400/40 bg-amber-950/80 text-amber-100' : 'border-sky-400/40 bg-sky-950/80 text-sky-100'
            }`}
          >
            {t.text}
          </motion.button>
        ))}
      </AnimatePresence>
    </div>
  );
}

/** Explicit approval dialog for irreversible / external-facing actions. */
export function ConfirmDialog() {
  const c = useGame((s) => s.confirm);
  const close = useGame((s) => s.closeConfirm);
  return (
    <Modal
      open={!!c}
      onClose={close}
      title={<span className="flex items-center gap-2"><AlertTriangle size={18} className={c?.danger ? 'text-rose-400' : 'text-amber-400'} />{c?.title}</span>}
      width={480}
      footer={
        <>
          <button className="btn-ghost" onClick={close}>Cancel</button>
          <button className={c?.danger ? 'btn-danger' : 'btn-primary'} onClick={() => { c?.onConfirm(); close(); }}>{c?.confirmLabel}</button>
        </>
      }
    >
      <p className="whitespace-pre-line text-sm leading-relaxed text-slate-300">{c?.body}</p>
    </Modal>
  );
}
