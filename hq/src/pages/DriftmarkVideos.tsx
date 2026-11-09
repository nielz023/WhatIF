/** Metrolijn (7 haltes van idee tot online) en de uploadkalender (met planning en verzetten, verbeterlijst punt 12). */
import { useState } from 'react';
import { useLive } from '../services/live';
import { order } from '../services/real';
import { useGame } from '../store/useGame';
type Step = { label: string; done?: boolean; active?: boolean };
const HALTES: { naam: string; stappen: string[]; uitleg: string }[] = [
  { naam: 'Idee', stappen: ['Idee', 'Verloop'], uitleg: 'Onderwerp kiezen en het verloop met de twist' },
  { naam: 'Script', stappen: ['Script', 'Stemmen'], uitleg: 'Script schrijven en de stemmen maken in ElevenLabs' },
  { naam: 'Cast', stappen: ['Cast', 'Sets'], uitleg: 'Figuren en decors bouwen in Blender' },
  { naam: 'Animatie', stappen: ['Animatie'], uitleg: 'Alle scènes animeren, met kwaliteitscheck per scène' },
  { naam: 'Render', stappen: ['Render'], uitleg: 'Scènes renderen op je pc' },
  { naam: 'Montage', stappen: ['Montage', 'Upload-tekst', 'Shorts'], uitleg: 'Eindmontage (-14 LUFS), titel, beschrijving, thumbnail en shorts' },
  { naam: 'Online', stappen: ['Online'], uitleg: 'Jij zet hem op YouTube' },
];

export function MetroLine({ steps }: { steps: Step[] }) {
  const st = HALTES.map((h) => {
    const s = steps.filter((x) => h.stappen.includes(x.label));
    const done = s.length > 0 && s.every((x) => x.done);
    const active = !done && s.some((x) => x.active || x.done);
    return { ...h, done, active };
  });
  return (
    <div className="mt-4 overflow-x-auto pb-1">
      <div className="relative flex min-w-[330px] items-start justify-between">
        <div className="absolute left-[7%] right-[7%] top-[11px] h-[3px] rounded-full bg-white/10" />
        <div className="absolute left-[7%] top-[11px] h-[3px] rounded-full bg-gradient-to-r from-sky-400 to-orange-400" style={{ width: `${(Math.max(0, st.reduce((m, h, i) => (h.done || h.active ? i : m), 0)) / (st.length - 1)) * 86}%` }} />
        {st.map((h) => (
          <div key={h.naam} className="relative z-10 flex w-[14%] flex-col items-center text-center" title={h.uitleg}>
            <span className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-[12px] font-bold ${h.done ? 'border-emerald-400 bg-emerald-400 text-[#070b1a]' : h.active ? 'animate-pulse border-orange-400 bg-orange-500/30 text-white shadow-[0_0_14px_#ff8a3d]' : 'border-white/20 bg-[#0f1630] text-slate-500'}`}>{h.done ? '✓' : ''}</span>
            <span className={`mt-1 text-[12px] font-semibold leading-tight ${h.active ? 'text-orange-300' : h.done ? 'text-slate-200' : 'text-slate-500'}`}>{h.naam}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

type YV = { id?: string; title: string; type?: string; status?: string; datum?: string; tijd?: string; views?: number; url?: string };

/** Verzetten = een opdracht aan Claude (de planning in YouTube Studio zet Claude of niels zelf om). */
function Verzet({ wat, nu }: { wat: string; nu?: string }) {
  const [open, setOpen] = useState(false);
  const [d, setD] = useState(nu ?? ''); const [t, setT] = useState('16:15');
  const toast = useGame((s) => s.toast);
  if (!open) return <button type="button" className="shrink-0 rounded-md bg-white/5 px-2 py-1 text-[12px] text-sky-300 hover:text-white" onClick={(e) => { e.preventDefault(); setOpen(true); }}>{nu ? 'Verzetten' : 'Inplannen'}</button>;
  return (
    <span className="flex shrink-0 flex-wrap items-center gap-1" onClick={(e) => e.preventDefault()}>
      <input type="date" value={d} onChange={(e) => setD(e.target.value)} className="rounded-md border border-white/10 bg-black/40 px-1.5 py-0.5 text-[12px] text-white" aria-label="Nieuwe datum" />
      <input type="time" value={t} onChange={(e) => setT(e.target.value)} className="rounded-md border border-white/10 bg-black/40 px-1.5 py-0.5 text-[12px] text-white" aria-label="Tijd" />
      <button type="button" className="rounded-md bg-orange-500 px-2 py-0.5 text-[12px] font-semibold text-white disabled:opacity-40" disabled={!d}
        onClick={() => { order(`Planning: ${nu ? 'verzet' : 'plan'} "${wat}"${nu ? ` (nu ${nu})` : ''} naar ${new Date(d + 'T12:00:00').toLocaleDateString('nl-NL', { weekday: 'long', day: 'numeric', month: 'long' })} om ${t}. Pas de planning in YouTube Studio aan (of zeg wat ik moet doen) en werk status.json bij.`, toast, { doel: 'Publicatie' }); setOpen(false); }}>Doorgeven</button>
      <button type="button" className="text-[12px] text-slate-400 hover:text-white" onClick={() => setOpen(false)}>Annuleren</button>
    </span>
  );
}

export function UploadCalendar({ vids }: { vids: YV[] }) {
  const prod = useLive((s) => s.data.videos);
  const today = new Date().toISOString().slice(0, 10);
  const list = vids.filter((v) => v.datum).sort((a, b) => b.datum!.localeCompare(a.datum!));
  const gepland = list.filter((v) => (v.status && v.status !== 'public') || v.datum! > today).reverse();
  // lange video's die klaar zijn of bijna, maar nog niet op YouTube staan
  const klaarVoorUpload = prod.filter((p) => p.status !== 'Online');
  const planning = (
    <section className="panel mb-3 p-4">
      <div className="mb-2 font-display text-[18px] font-bold text-white">Wat gaat er online</div>
      {gepland.length ? <ul className="space-y-1.5">{gepland.map((v) => (
        <li key={v.id ?? v.title} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-white/[.04] px-3 py-2">
          <span className="min-w-0 truncate text-[14px] text-slate-100"><span className="mr-2 text-[13px] text-orange-300">{new Date(v.datum + 'T12:00:00').toLocaleDateString('nl-NL', { weekday: 'short', day: 'numeric', month: 'short' })}{v.tijd ? ` ${v.tijd}` : (v.status ?? '').match(/\d{1,2}:\d{2}/)?.[0] ? ` ${(v.status ?? '').match(/\d{1,2}:\d{2}/)![0]}` : ''}</span>{v.type === 'long' ? '🎬 lang' : '📱 short'} · {v.title}</span>
          <Verzet wat={v.title} nu={v.datum} />
        </li>
      ))}</ul> : <p className="text-[14px] text-slate-400">Er staat niets ingepland op YouTube.</p>}
      {klaarVoorUpload.length > 0 && (<>
        <div className="mb-1 mt-3 text-[13px] font-semibold text-slate-300">Nog niet ingepland</div>
        <ul className="space-y-1.5">{klaarVoorUpload.map((p) => (
          <li key={p.nr} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-white/[.03] px-3 py-2">
            <span className="min-w-0 text-[14px] text-slate-200">🎬 Video {p.nr} · {p.werktitel} <span className="text-[12px] text-slate-500">({p.status})</span></span>
            <Verzet wat={`video ${p.nr} (${p.title})`} />
          </li>
        ))}</ul>
      </>)}
      <p className="mt-2 text-[12px] text-slate-500">Verzetten of inplannen gaat als opdracht naar Claude. Het ritme uit je kanaalplan: één lange video per week, met shorts ertussen.</p>
    </section>
  );
  if (!list.length) return <>{planning}<div className="panel p-4 text-[15px] text-slate-400">Nog geen uploads bekend. Zodra de cijfers binnen zijn, staan ze hier.</div></>;
  // groepeer per week (maandag)
  const monday = (d: string) => { const t = new Date(d + 'T12:00:00'); const day = (t.getDay() + 6) % 7; t.setDate(t.getDate() - day); return t.toISOString().slice(0, 10); };
  const weeks = [...new Set(list.map((v) => monday(v.datum!)))];
  return (
    <div className="grid gap-3">
      {planning}
      {weeks.map((w) => {
        const items = list.filter((v) => monday(v.datum!) === w);
        const long = items.filter((v) => v.type === 'long');
        return (
          <section key={w} className="panel p-4">
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-display text-[17px] font-bold text-white">Week van {new Date(w + 'T12:00:00').toLocaleDateString('nl-NL', { day: 'numeric', month: 'long' })}</span>
              <span className="text-[13px]" style={{ color: long.length ? '#94a3b8' : '#ff8a3d' }}>{long.length ? `🎬 ${long.length} lange video` : '⚠ geen lange video deze week'} · 📱 {items.length - long.length} shorts</span>
            </div>
            <ul className="space-y-1.5">{items.map((v) => {
              const planned = (v.status && v.status !== 'public') || v.datum! > today;
              return (
                <li key={v.id ?? v.title}>
                  <a href={v.url} target="_blank" rel="noreferrer" className="flex items-center justify-between gap-3 rounded-xl bg-white/[.04] px-3 py-2 hover:bg-white/[.08]">
                    <span className="flex min-w-0 items-center gap-2"><span className="w-14 shrink-0 text-[13px] text-slate-400">{new Date(v.datum + 'T12:00:00').toLocaleDateString('nl-NL', { weekday: 'short', day: 'numeric' })}</span><span className="truncate text-[14px] text-slate-100">{v.type === 'long' ? '🎬' : '📱'} {v.title}</span></span>
                    <span className={`shrink-0 text-[13px] font-semibold ${planned ? 'text-orange-300' : 'text-slate-300'}`}>{planned ? 'ingepland' : `${Number(v.views ?? 0).toLocaleString('nl-NL')} weergaven`}</span>
                  </a>
                </li>
              );
            })}</ul>
          </section>
        );
      })}
    </div>
  );
}
