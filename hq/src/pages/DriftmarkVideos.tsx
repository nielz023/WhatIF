/** Metrolijn (7 haltes van idee tot online) en de uploadkalender. */
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

type YV = { id?: string; title: string; type?: string; status?: string; datum?: string; views?: number; url?: string };
export function UploadCalendar({ vids }: { vids: YV[] }) {
  const list = vids.filter((v) => v.datum).sort((a, b) => b.datum!.localeCompare(a.datum!));
  if (!list.length) return <div className="panel p-4 text-[15px] text-slate-400">Nog geen uploads bekend. Zodra de cijfers binnen zijn, staan ze hier.</div>;
  const today = new Date().toISOString().slice(0, 10);
  // groepeer per week (maandag)
  const monday = (d: string) => { const t = new Date(d + 'T12:00:00'); const day = (t.getDay() + 6) % 7; t.setDate(t.getDate() - day); return t.toISOString().slice(0, 10); };
  const weeks = [...new Set(list.map((v) => monday(v.datum!)))];
  return (
    <div className="grid gap-3">
      {weeks.map((w) => {
        const items = list.filter((v) => monday(v.datum!) === w);
        const long = items.filter((v) => v.type === 'long');
        return (
          <section key={w} className="panel p-4">
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-display text-[17px] font-bold text-white">Week van {new Date(w + 'T12:00:00').toLocaleDateString('nl-NL', { day: 'numeric', month: 'long' })}</span>
              <span className="text-[13px] text-slate-400">{long.length ? `🎬 ${long.length} lange video` : 'geen lange video'} · 📱 {items.length - long.length} shorts</span>
            </div>
            <ul className="space-y-1.5">{items.map((v) => {
              const planned = (v.status && v.status !== 'public') || v.datum! > today;
              return (
                <li key={v.id ?? v.title}>
                  <a href={v.url} target="_blank" rel="noreferrer" className="flex items-center justify-between gap-3 rounded-xl bg-white/[.04] px-3 py-2 hover:bg-white/[.08]">
                    <span className="flex min-w-0 items-center gap-2"><span className="w-14 shrink-0 text-[13px] text-slate-400">{new Date(v.datum + 'T12:00:00').toLocaleDateString('nl-NL', { weekday: 'short', day: 'numeric' })}</span><span className="truncate text-[14px] text-slate-100">{v.type === 'long' ? '🎬' : '📱'} {v.title}</span></span>
                    <span className={`shrink-0 text-[13px] font-semibold ${planned ? 'text-orange-300' : 'text-slate-300'}`}>{planned ? 'ingepland' : `${Number(v.views ?? 0).toLocaleString('nl-NL')} views`}</span>
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
