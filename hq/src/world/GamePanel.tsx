/**
 * Het spelscherm van de game room (niels 2026-11-09: "je kan zelf ook gamen in de rondloopmodus"). Opent als je bij een
 * gamekast, racesimulator, de airhockeytafel of de grijpmachine op E drukt (of op de knop tikt). De spellen zelf staan in
 * games.ts; hier: het canvas, de toetsen, muis en vinger, knoppen voor aanraken, highscores en Esc om te stoppen.
 */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronLeft, ChevronRight, ChevronUp, Circle, RotateCcw, Trophy, X } from 'lucide-react';
import { usePlay, stopSpel, score, type GameId } from './play';
import { GAMES, type Game, type Input } from './games';
import { useWalk } from './walkState';
import { reducedMotion } from './useWorld';

type Btn = 'l' | 'r' | 'u' | 'd' | 'a';
const KEYMAP: Record<string, Btn> = { ArrowLeft: 'l', KeyA: 'l', ArrowRight: 'r', KeyD: 'r', ArrowUp: 'u', KeyW: 'u', ArrowDown: 'd', KeyS: 'd', Space: 'a', Enter: 'a' };
const ICON: Record<Btn, typeof ChevronLeft> = { l: ChevronLeft, r: ChevronRight, u: ChevronUp, d: ChevronDown, a: Circle };

export default function GameLayer() {
  const open = usePlay((s) => s.open);
  if (!open) return null;
  return <Spel key={open} id={open} />;
}

function Spel({ id }: { id: GameId }) {
  const def = GAMES[id];
  const best = usePlay((s) => s.best[id] ?? 0);
  const touch = useWalk((s) => s.touch);
  const cv = useRef<HTMLCanvasElement>(null);
  const game = useRef<Game>(null as unknown as Game); if (!game.current) game.current = def.make();
  const held = useRef(new Set<Btn>()); const hit = useRef(new Set<Btn>());
  const ptr = useRef({ x: null as number | null, y: null as number | null, down: false, hit: false });
  const [ronde, setRonde] = useState(0);
  const [eind, setEind] = useState<{ score: number; record: boolean } | null>(null);
  const [live, setLive] = useState({ score: 0, info: '' });

  const opnieuw = () => { game.current = def.make(); held.current.clear(); hit.current.clear(); setEind(null); setRonde((r) => r + 1); };

  // toetsen: vangen vóór het rondlopen (anders loop je mee) en Esc sluit
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); stopSpel(); return; }
      const b = KEYMAP[e.code];
      if (e.code === 'KeyE' || e.code === 'KeyQ' || b) { e.preventDefault(); e.stopImmediatePropagation(); }
      if (!b) return;
      if (eind && (b === 'a') && !e.repeat) { opnieuw(); return; }
      if (!e.repeat) hit.current.add(b);
      held.current.add(b); if (b !== 'a') ptr.current.x = ptr.current.y = null; // toetsen nemen het over van de muis
    };
    const up = (e: KeyboardEvent) => { const b = KEYMAP[e.code]; if (b) { held.current.delete(b); e.stopImmediatePropagation(); } };
    window.addEventListener('keydown', down, true); window.addEventListener('keyup', up, true);
    return () => { window.removeEventListener('keydown', down, true); window.removeEventListener('keyup', up, true); };
  }, [eind]); // eslint-disable-line react-hooks/exhaustive-deps

  // de spellus
  useEffect(() => {
    const c = cv.current; if (!c) return;
    const g0 = game.current; c.width = g0.w * 2; c.height = g0.h * 2;
    const g = c.getContext('2d'); if (!g) return;
    let raf = 0, last = performance.now(), t = 0, shown = 0, klaar = false;
    const frame = (now: number) => {
      raf = requestAnimationFrame(frame);
      const dt = Math.min(0.05, (now - last) / 1000); last = now; if (document.hidden) return;
      const gm = game.current; t += dt;
      if (!gm.over) {
        const k: Input = {
          l: held.current.has('l'), r: held.current.has('r'), u: held.current.has('u'), d: held.current.has('d'), a: held.current.has('a'),
          lHit: hit.current.has('l'), rHit: hit.current.has('r'), uHit: hit.current.has('u'), dHit: hit.current.has('d'), aHit: hit.current.has('a'),
          px: ptr.current.x, py: ptr.current.y, pDown: ptr.current.down, pHit: ptr.current.hit,
        };
        hit.current.clear(); ptr.current.hit = false;
        gm.step(dt, k);
      }
      g.setTransform(2, 0, 0, 2, 0, 0); g.save(); gm.draw(g, t); g.restore();
      if (gm.over && !klaar) { klaar = true; const rec = score(id, gm.score); setEind({ score: gm.score, record: rec && gm.score > 0 }); }
      if (now - shown > 200) { shown = now; setLive({ score: gm.score, info: gm.info }); }
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [ronde, id]);

  // muis en vinger op het canvas (in spelcoördinaten)
  const zet = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const r = e.currentTarget.getBoundingClientRect(); const gm = game.current;
    ptr.current.x = ((e.clientX - r.left) / r.width) * gm.w; ptr.current.y = ((e.clientY - r.top) / r.height) * gm.h;
  };
  const g0 = game.current; const ratio = g0.w / g0.h;
  const knop = (b: Btn) => ({
    onPointerDown: (e: React.PointerEvent) => { e.preventDefault(); held.current.add(b); hit.current.add(b); ptr.current.x = ptr.current.y = null; if (eind && b === 'a') opnieuw(); },
    onPointerUp: () => held.current.delete(b), onPointerLeave: () => held.current.delete(b), onPointerCancel: () => held.current.delete(b),
  });
  const rm = reducedMotion();
  return (
    <div className="pointer-events-auto absolute inset-x-0 bottom-0 top-[64px] z-40 flex items-center justify-center bg-[#03050f]/70 p-2 backdrop-blur-sm" role="dialog" aria-label={`Spel ${def.naam}`} id="dm-spel">
      <motion.div initial={{ opacity: 0, scale: rm ? 1 : 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: rm ? 0 : 0.2 }}
        className="flex max-h-full w-[min(96vw,560px)] flex-col rounded-2xl border bg-[#0b1130]/95 p-3 shadow-2xl" style={{ borderColor: `${def.kleur}99`, boxShadow: `0 0 40px ${def.kleur}40` }}>
        <div className="mb-2 flex items-center gap-3">
          <div className="min-w-0 flex-1">
            <div className="font-display text-[18px] font-black tracking-wide" style={{ color: def.kleur }}>{def.naam}</div>
            <div className="text-[12px] leading-snug text-slate-400">{def.uitleg}</div>
          </div>
          <div className="flex items-center gap-1.5 rounded-lg bg-white/5 px-2 py-1 text-[12px] font-semibold text-slate-200" title="Jouw beste score in deze browser"><Trophy size={14} className="text-[#FACC15]" /> {best}</div>
          <button onClick={stopSpel} aria-label="Spel sluiten (Esc)" title="Sluiten (Esc)" className="rounded-lg p-1.5 text-slate-300 hover:bg-white/10 hover:text-white"><X size={20} /></button>
        </div>
        <div className="relative mx-auto" style={{ width: `min(100%, calc((100dvh - ${touch ? 330 : 250}px) * ${ratio}))`, aspectRatio: `${g0.w} / ${g0.h}` }}>
          <canvas ref={cv} className="block h-full w-full touch-none select-none rounded-xl" style={{ imageRendering: 'auto' }}
            onPointerMove={zet} onPointerDown={(e) => { zet(e); ptr.current.down = true; ptr.current.hit = true; try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* */ } }}
            onPointerUp={() => { ptr.current.down = false; }} onPointerCancel={() => { ptr.current.down = false; }}
            onPointerLeave={(e) => { if (e.pointerType === 'mouse' && id !== 'hockey') { ptr.current.x = ptr.current.y = null; } }} />
          {eind && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-xl bg-[#03050f]/75 text-center">
              <div className="text-[13px] font-semibold uppercase tracking-widest text-slate-400">Afgelopen</div>
              <div className="font-display text-[40px] font-black text-white">{eind.score}</div>
              {eind.record && <div className="rounded-full bg-[#FACC15]/20 px-3 py-1 text-[13px] font-bold text-[#FACC15]">Nieuw record!</div>}
              <div className="flex gap-2">
                <button onClick={opnieuw} autoFocus className="flex items-center gap-2 rounded-xl px-4 py-2 text-[14px] font-bold text-white" style={{ background: `${def.kleur}55`, boxShadow: `inset 0 0 0 1px ${def.kleur}` }}><RotateCcw size={16} /> Nog een keer{!touch && <span className="rounded border border-white/25 px-1 font-mono text-[11px]">spatie</span>}</button>
                <button onClick={stopSpel} className="rounded-xl bg-white/10 px-4 py-2 text-[14px] font-semibold text-slate-200 hover:bg-white/20">Stoppen{!touch && <span className="ml-2 rounded border border-white/25 px-1 font-mono text-[11px]">Esc</span>}</button>
              </div>
            </div>
          )}
        </div>
        <div className="mt-2 flex items-center justify-between text-[12px] text-slate-400">
          <span>Score <b className="text-white">{live.score}</b>{live.info && <span className="ml-2">{live.info}</span>}</span>
          {!touch && <span>Esc: stoppen</span>}
        </div>
        {touch && (
          <div className="mt-2 flex justify-center gap-2">
            {def.knoppen.map((b) => { const I = ICON[b]; return <button key={b} {...knop(b)} aria-label={b} className="flex h-14 w-16 touch-none select-none items-center justify-center rounded-2xl border border-white/20 bg-white/10 text-white active:bg-white/25"><I size={26} /></button>; })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
