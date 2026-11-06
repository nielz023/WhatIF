/**
 * AFKEUREN (niels 6 nov 14:07: "Ik wil ook dat er een kopje komt, een rood kopje met afkeuren.")
 * Een rode knop naast elke Goedkeuren van een taak die op niels wacht. Een klik opent een klein venster met een
 * vak voor de reden (mag leeg blijven); Afkeuren stuurt dat als echte opdracht naar Claude.
 * Het venster staat één keer in App.tsx en heeft een eigen store: de kaart met de knop (ActCard) wordt bij elke
 * verversing opnieuw gemaakt, het venster blijft dan gewoon staan.
 */
import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ThumbsDown, X } from 'lucide-react';
import { create } from 'zustand';
import { order } from '../../services/real';
import { useGame } from '../../store/useGame';

export interface AfkeurTaak { title: string; id?: string }
interface A {
  open: AfkeurTaak | null;
  /** wat niels al typte, per taak: na Annuleren (of per ongeluk Esc) staat het er bij een volgende klik nog */
  concept: Record<string, string>;
}
export const useAfkeuren = create<A>(() => ({ open: null, concept: {} }));
const sleutel = (t: AfkeurTaak) => t.id || t.title;
/** de knop waarmee het venster openging: daar komt de focus na het sluiten terug */
let opener: HTMLElement | null = null;
/** opent het venster voor één taak; id is de thread (cmsg_...), als die er is */
export function openAfkeuren(t: AfkeurTaak) {
  const cur = useAfkeuren.getState().open;
  if (cur && sleutel(cur) === sleutel(t)) return; // staat al open: niets wissen
  opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  useAfkeuren.setState({ open: { title: t.title, id: t.id || undefined } });
}

/** de opdracht voor Claude: 'Afgekeurd: taak "X" (thread cmsg_...). Reden: ...' (zonder thread-deel als er geen id is) */
export function afkeurOpdracht(t: AfkeurTaak, reden: string) {
  const r = reden.trim() || 'geen reden gegeven';
  return `Afgekeurd: taak "${t.title}"${t.id ? ` (thread ${t.id})` : ''}. Reden: ${r}${/[.!?]$/.test(r) ? '' : '.'}`;
}

/** de rode stijl van Afkeuren; even groot als de knop ernaast (geef die zijn tekstmaat mee via className) */
export const ROOD = 'btn border border-rose-500 bg-rose-600 text-white hover:bg-rose-500';
export function AfkeurKnop({ title, id, className = '' }: AfkeurTaak & { className?: string }) {
  return <button type="button" className={`${ROOD} ${className}`} onClick={() => openAfkeuren({ title, id })}>Afkeuren</button>;
}

const MAC = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/i.test(navigator.platform || navigator.userAgent);

export default function AfkeurenVenster() {
  const open = useAfkeuren((s) => s.open);
  const toast = useGame((s) => s.toast);
  const [reden, setReden] = useState('');
  const redenRef = useRef(reden); redenRef.current = reden;
  const doos = useRef<HTMLDivElement>(null);
  const taak = open ? sleutel(open) : null;

  // bij openen: een eerder concept voor deze taak terugzetten (de cursor staat er via autoFocus meteen in)
  useEffect(() => { if (taak) setReden(useAfkeuren.getState().concept[taak] ?? ''); }, [taak]);

  const sluit = (verstuurd: boolean) => {
    const o = useAfkeuren.getState().open; if (!o) return;
    const k = sleutel(o); const tekst = redenRef.current;
    useAfkeuren.setState((s) => {
      const concept = { ...s.concept };
      if (verstuurd || !tekst.trim()) delete concept[k]; else concept[k] = tekst;
      return { open: null, concept };
    });
    const el = opener; opener = null;
    if (el && document.contains(el)) el.focus();
  };
  const bevestig = () => {
    const o = useAfkeuren.getState().open; if (!o) return;
    order(afkeurOpdracht(o, redenRef.current), toast);
    sluit(true);
  };
  const acties = useRef({ sluit, bevestig }); acties.current = { sluit, bevestig };

  // Esc annuleert, Ctrl/Cmd+Enter keurt af. Net als het gesprekspaneel in de capture-fase met stopPropagation,
  // zodat de app-brede Esc in App.tsx niet ook nog naar Home gaat. Tab blijft binnen het venster.
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (!useAfkeuren.getState().open) return;
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); acties.current.sluit(false); return; }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); e.stopPropagation(); acties.current.bevestig(); return; }
      if (e.key === 'Tab' && doos.current) {
        const f = [...doos.current.querySelectorAll<HTMLElement>('button, textarea')].filter((x) => !x.hasAttribute('disabled'));
        if (!f.length) return;
        const i = f.indexOf(document.activeElement as HTMLElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && (i === -1 || i === f.length - 1)) { e.preventDefault(); f[0].focus(); }
      }
    };
    window.addEventListener('keydown', k, true);
    return () => window.removeEventListener('keydown', k, true);
  }, []);

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[85] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onMouseDown={(e) => { if (e.target === e.currentTarget) sluit(false); }}>
          <motion.div ref={doos} id="dm-afkeuren" role="dialog" aria-modal="true" aria-labelledby="dm-afkeuren-titel"
            className="panel w-full max-w-[460px] border-rose-500/40 p-5 shadow-[0_24px_70px_rgba(0,0,0,.6),0_0_30px_rgba(225,29,72,.18)]"
            initial={{ y: 18, scale: 0.97 }} animate={{ y: 0, scale: 1 }} exit={{ y: 12, opacity: 0 }} transition={{ duration: 0.18 }}>
            <div className="flex items-start gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-rose-600/20 text-rose-300"><ThumbsDown size={16} /></span>
              <h2 id="dm-afkeuren-titel" className="min-w-0 flex-1 break-words pt-0.5 font-display text-[18px] font-bold leading-snug text-white">Afkeuren: {open.title}</h2>
              <button type="button" className="rounded-lg p-1 text-slate-400 hover:bg-white/5 hover:text-white" onClick={() => sluit(false)} aria-label="Sluiten"><X size={18} /></button>
            </div>
            {/* autoFocus: React zet de cursor er direct bij het tonen in, ook als de pagina het druk heeft met het 3D-kantoor */}
            <textarea autoFocus className="input mt-4 min-h-[104px] resize-y text-[14px] leading-relaxed" value={reden} maxLength={2000} onChange={(e) => setReden(e.target.value)}
              placeholder="Wat moet er anders? (mag leeg blijven)" aria-label="Wat moet er anders? (mag leeg blijven)" />
            <div className="mt-1.5 text-[12px] text-slate-500">Claude krijgt dit als opdracht en past de taak aan. {MAC ? '⌘' : 'Ctrl'} + Enter keurt af, Esc annuleert.</div>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" className="btn-ghost" onClick={() => sluit(false)}>Annuleren</button>
              <button type="button" className={ROOD} onClick={bevestig}>Afkeuren</button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
