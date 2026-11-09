/**
 * Schermlaag van het praten met de figuurtjes (niels 2026-11-09): tijdens het rondlopen "E: praat met …" als er iemand
 * vlak voor je staat, en het gesprek zelf. Typen of inspreken: het tekstvak krijgt vanzelf het microfoontje (lib/mic.ts).
 */
import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Gamepad2, MessageCircle, Send, Volume2, VolumeX, X } from 'lucide-react';
import { useWorld, reducedMotion } from './useWorld';
import { useWalk } from './walkState';
import { useTalk, begin, sluit, stuur, crewIndex } from './talk';
import { useGame } from '../store/useGame';
import { usePlay, speel, stopSpel } from './play';
import GameLayer from './GamePanel';

const typing = (e: KeyboardEvent) => !!(e.target as HTMLElement | null)?.closest?.('input,textarea,select,[contenteditable="true"]');

/** wie of wat er voor je staat: een machine wint als de rand ervan dichterbij is dan het figuurtje (midden) */
function kies(): 'talk' | 'game' | null {
  const t = useTalk.getState().near; const g = usePlay.getState().near;
  // een speler die vlak bij een spel staat (bijv. aan de airhockeytafel) is meestal aan het spelen: het spel gaat iets voor
  if (g && (!t || g.d <= t.d + 0.3)) return 'game';
  return t ? 'talk' : null;
}

function NearPrompt() {
  const near = useTalk((s) => s.near); const open = useTalk((s) => s.open); const touch = useWalk((s) => s.touch);
  const walk = useWorld((s) => s.walk); const pnear = usePlay((s) => s.near); const game = usePlay((s) => s.open);
  const wat = walk && !open && !game ? kies() : null;
  const doel = wat === 'game' ? { key: `g-${pnear!.id}`, naam: pnear!.naam, kleur: pnear!.kleur } : wat === 'talk' ? { key: near!.key, naam: near!.naam, kleur: near!.kleur } : null;
  const doe = () => {
    if (wat === 'game' && pnear) speel(pnear.id);
    else if (near) { const m = crewIndex.members.get(near.key); if (m) begin(m); }
  };
  return (
    <AnimatePresence>
      {doel && (
        <motion.div key={doel.key} className="pointer-events-none absolute inset-x-0 top-[38%] flex justify-center"
          initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
          <button id={wat === 'game' ? 'dm-speel' : 'dm-praat'} onClick={doe}
            className="pointer-events-auto mt-10 flex items-center gap-2 rounded-full border bg-[#0b1130]/85 py-1.5 pl-2 pr-3 text-[13px] font-semibold text-white backdrop-blur"
            style={{ borderColor: `${doel.kleur}aa`, boxShadow: `0 0 18px ${doel.kleur}55` }}>
            {!touch && <span className="rounded-md border border-white/20 bg-white/10 px-1.5 py-px font-mono text-[11px] font-bold">E</span>}
            {wat === 'game'
              ? <><Gamepad2 size={15} style={{ color: doel.kleur }} /> Speel {doel.naam}</>
              : <><MessageCircle size={15} style={{ color: doel.kleur }} /> Praat met {doel.naam}</>}
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Gesprek() {
  const open = useTalk((s) => s.open); const log = useTalk((s) => (open ? s.log[open.key] : undefined)) ?? [];
  const bezig = useTalk((s) => s.bezig); const stem = useTalk((s) => s.stem);
  const [tekst, setTekst] = useState('');
  const lijst = useRef<HTMLDivElement>(null); const veld = useRef<HTMLInputElement>(null);
  useEffect(() => { lijst.current?.scrollTo({ top: 1e6, behavior: reducedMotion() ? 'auto' : 'smooth' }); }, [log]);
  useEffect(() => { if (open) setTimeout(() => veld.current?.focus(), 60); else setTekst(''); }, [open?.key]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); sluit(); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, [open]);
  const verstuur = () => { const t = tekst.trim(); if (!t) return; setTekst(''); void stuur(t); };
  if (!open) return null;
  const { p } = open;
  return (
    <motion.div key={open.key} id="dm-gesprek" role="dialog" aria-label={`Gesprek met ${p.naam}`}
      className="pointer-events-auto absolute bottom-[96px] right-3 top-[84px] flex w-[min(94vw,380px)] flex-col overflow-hidden rounded-2xl border bg-[#0b1130]/92 backdrop-blur md:right-[86px]"
      style={{ borderColor: `${p.kleur}99`, boxShadow: `0 0 30px ${p.kleur}33, 0 18px 50px rgba(0,0,0,.55)` }}
      initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: reducedMotion() ? 0 : 0.22 }}>
      <div className="flex items-center gap-3 border-b border-white/10 px-3 py-2.5">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-[17px] font-black text-white" style={{ background: p.kleur, boxShadow: `0 0 14px ${p.kleur}88` }}>{p.naam[0]}</span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-[15px] font-bold text-white">{p.naam}</div>
          <div className="truncate text-[12px] text-slate-400">{p.rol}</div>
        </div>
        <button onClick={() => useTalk.getState().setStem(!stem)} title={stem ? 'Stem uit' : 'Stem aan'} aria-label={stem ? 'Stem uitzetten' : 'Stem aanzetten'}
          className="rounded-lg p-1.5 text-slate-300 hover:bg-white/10 hover:text-white">{stem ? <Volume2 size={18} /> : <VolumeX size={18} />}</button>
        <button onClick={sluit} title="Sluiten (Esc)" aria-label="Gesprek sluiten" className="rounded-lg p-1.5 text-slate-300 hover:bg-white/10 hover:text-white"><X size={18} /></button>
      </div>
      <div ref={lijst} className="flex-1 space-y-2 overflow-y-auto px-3 py-3">
        {log.map((m, i) => (
          <div key={i} className={`flex ${m.van === 'ik' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-[14px] leading-snug ${m.van === 'ik' ? 'rounded-br-md bg-[#FF7A24]/25 text-white' : 'rounded-bl-md bg-white/8 text-slate-100'}`}
              style={m.van === 'zij' ? { boxShadow: `inset 0 0 0 1px ${p.kleur}55` } : undefined}>{m.tekst}</div>
          </div>
        ))}
      </div>
      <form className="flex items-center gap-2 border-t border-white/10 p-2.5" onSubmit={(e) => { e.preventDefault(); verstuur(); }}>
        <input ref={veld} type="text" value={tekst} onChange={(e) => setTekst(e.target.value)} placeholder={`Zeg iets tegen ${p.naam.toLowerCase()}…`} aria-label={`Bericht aan ${p.naam}`}
          className="min-w-0 flex-1 rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-[14px] text-white placeholder:text-slate-500 focus:border-[#FF7A24]/70 focus:outline-none" />
        <button type="submit" disabled={bezig || !tekst.trim()} aria-label="Versturen" className="rounded-xl bg-[#FF7A24]/80 p-2 text-white transition hover:bg-[#FF7A24] disabled:opacity-40"><Send size={18} /></button>
      </form>
      <div className="px-3 pb-2 text-[11px] text-slate-500">Inspreken: klik op het microfoontje in het tekstvak of druk Alt+M.</div>
    </motion.div>
  );
}

/** in WorldLayer: de vraag "praat met …" of "speel …", het gesprek en het spelscherm */
export default function TalkLayer() {
  const walk = useWorld((s) => s.walk); const page = useGame((s) => s.page);
  // E: praten met wie er voor je staat
  useEffect(() => {
    if (!walk) return;
    const k = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.repeat || typing(e) || e.code !== 'KeyE') return;
      const t = useTalk.getState(); const p = usePlay.getState(); if (t.open || p.open) return;
      const wat = kies(); if (!wat) return;
      if (wat === 'game' && p.near) { e.preventDefault(); e.stopImmediatePropagation(); speel(p.near.id); return; }
      const m = t.near && crewIndex.members.get(t.near.key); if (!m) return;
      e.preventDefault(); e.stopImmediatePropagation(); begin(m);
    };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, [walk]);
  // weg van Home of klaar met lopen: gesprek dicht
  useEffect(() => { if (page !== 'driftmark') sluit(); if ((page !== 'driftmark' || !walk) && usePlay.getState().open) stopSpel(); }, [page, walk]);
  return (
    <div className="pointer-events-none absolute inset-0 z-30">
      <NearPrompt />
      <AnimatePresence>{<Gesprek />}</AnimatePresence>
      <GameLayer />
    </div>
  );
}
