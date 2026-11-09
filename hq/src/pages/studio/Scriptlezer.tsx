/**
 * SCRIPTLEZER MET TIJDLIJN (verbeterlijst punt 53). Het script per scène met de tijden, de hook (eerste 5 seconden)
 * gemarkeerd, een controle of de abonneeroproep rond 60% zit, en de vaste regels uit het script.
 * Het script zelf blijft Engels; de uitleg eromheen is Nederlands.
 */
import { useEffect, useState } from 'react';
import { RefreshCw, FileText } from 'lucide-react';
import { useLive } from '../../services/live';
import { leesBestand } from '../../services/kennis';
import { leesScript, sNaarTijd, tijdNaarS, type ScriptInfo } from '../../services/studio';
import { openBestand } from '../../components/shared/BestandViewer';
import { Md } from '../../components/shared/Md';
import { KLEUR } from '../../lib/status';

type Stand = { fase: 'laden' } | { fase: 'ok'; info: ScriptInfo } | { fase: 'fout'; tekst: string };
const KLEUREN = ['#3db8ff', '#a78bfa', '#3ddc97', '#ff8a3d', '#f472b6', '#facc15'];

function Check({ ok, tekst }: { ok: boolean | null; tekst: React.ReactNode }) {
  const k = ok == null ? KLEUR.stil : ok ? KLEUR.klaar : KLEUR.wacht;
  return <li className="flex items-start gap-2 text-[13px] text-slate-200"><span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: k }} />{tekst}</li>;
}

export default function Scriptlezer() {
  const videos = useLive((s) => s.data.videos).filter((v) => v.script);
  const [nr, setNr] = useState<number | null>(null);
  const v = videos.find((x) => x.nr === nr) ?? videos[videos.length - 1];
  const [st, setSt] = useState<Stand>({ fase: 'laden' });
  const [open, setOpen] = useState<number | null>(null);
  useEffect(() => {
    if (!v?.script) return;
    let weg = false; setSt({ fase: 'laden' }); setOpen(null);
    void leesBestand(v.script).then((r) => {
      if (weg) return;
      if (r.kind === 'tekst') setSt({ fase: 'ok', info: leesScript(r.tekst) });
      else setSt({ fase: 'fout', tekst: r.kind === 'geen-toegang' ? 'Deze pagina kan de projectbestanden hier niet lezen. Open het HQ in claude.ai.' : r.kind === 'ontbreekt' ? 'Het script staat niet (meer) op de plek die status.json noemt.' : 'Het script kon nu niet gelezen worden.' });
    });
    return () => { weg = true; };
  }, [v?.script]);
  if (!videos.length) return <div className="panel p-4 text-[14px] text-slate-400">Er is nog geen video met een script.</div>;
  const info = st.fase === 'ok' ? st.info : null;
  const doel = /(\d{1,2}:\d{2})/.exec(v.lengte ?? '')?.[1];
  const abo = info?.abonnee.filter((a) => info.totaal && a.tijd / info.totaal < 0.9) ?? [];
  const aboPct = abo.length && info?.totaal ? Math.round((abo[0].tijd / info.totaal) * 100) : null;
  return (
    <div className="grid min-w-0 gap-3 [&>*]:min-w-0">
      <section className="panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap gap-1.5">{videos.map((x) => (
            <button key={x.nr} onClick={() => setNr(x.nr)} className={`rounded-lg px-3 py-1.5 text-[13px] font-semibold ${x.nr === v.nr ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>Video {x.nr} · {x.werktitel}</button>
          ))}</div>
          <button className="btn-ghost !py-1 text-[13px]" onClick={() => openBestand(v.script)}><FileText size={13} />Heel script openen</button>
        </div>
        {st.fase === 'laden' && <div className="mt-3 text-[14px] text-slate-400"><RefreshCw size={14} className="mr-1 inline animate-spin" />Script laden…</div>}
        {st.fase === 'fout' && <div className="mt-3 text-[14px] text-slate-400">{st.tekst}</div>}
        {info && (info.scenes.length ? (<>
          <div className="mt-3 flex items-baseline justify-between text-[13px] text-slate-400"><span>Tijdlijn: {info.scenes.length} scènes, {sNaarTijd(info.totaal)}{doel ? ` (doel ${doel})` : ''}</span><span>klik op een scène</span></div>
          <div className="relative mt-1 h-10 overflow-hidden rounded-lg bg-white/5">
            {info.scenes.map((s, i) => (
              <button key={i} onClick={() => setOpen(i)} title={`${sNaarTijd(s.start)}-${sNaarTijd(s.eind)} ${s.kop}`}
                className={`absolute top-0 h-full border-r border-[#070b1a] transition hover:brightness-125 ${open === i ? 'ring-2 ring-white' : ''}`}
                style={{ left: `${(s.start / info.totaal) * 100}%`, width: `${Math.max(0.4, ((s.eind - s.start) / info.totaal) * 100)}%`, background: KLEUREN[i % KLEUREN.length], opacity: 0.75 }} />
            ))}
            <div className="pointer-events-none absolute inset-y-0 left-0 border-2 border-orange-300" style={{ width: `${(5 / info.totaal) * 100}%`, minWidth: 4 }} title="hook: eerste 5 seconden" />
            {abo.map((a, i) => <div key={i} className="pointer-events-none absolute inset-y-0 w-0.5 bg-white" style={{ left: `${(a.tijd / info.totaal) * 100}%` }} />)}
            <div className="pointer-events-none absolute inset-y-0 w-px border-l border-dashed border-white/40" style={{ left: '60%' }} />
          </div>
          <div className="mt-1 flex flex-wrap gap-3 text-[12px] text-slate-400"><span><span className="mr-1 inline-block h-2.5 w-2.5 border-2 border-orange-300" />hook (0-5 s)</span><span><span className="mr-1 inline-block h-2.5 w-0.5 bg-white" />abonneeroproep</span><span>stippellijn = 60%</span></div>
          <ul className="mt-3 space-y-1">
            <Check ok={!!info.hook} tekst={<>Hook in de eerste 5 seconden: {info.hook ? <i className="text-white">{info.hook}</i> : 'geen gesproken zin gevonden in de eerste scène.'}</>} />
            <Check ok={aboPct != null ? aboPct >= 45 && aboPct <= 75 : false} tekst={aboPct != null ? <>Abonneeroproep op ongeveer {sNaarTijd(abo[0].tijd)} ({aboPct}% van de video){aboPct >= 45 && aboPct <= 75 ? ', goed rond 60%.' : '. Het doel is rond 60%.'}</> : 'Geen abonneeroproep gevonden vóór het einde. Het doel is rond 60% van de video.'} />
            <Check ok={doel ? Math.abs(info.totaal - tijdNaarS(doel)) <= 60 : null} tekst={doel ? <>Lengte volgens het script {sNaarTijd(info.totaal)}, doel {doel}.</> : <>Lengte volgens het script {sNaarTijd(info.totaal)}.</>} />
            <Check ok={info.scenes.every((s) => s.eind - s.start <= 90)} tekst={(() => { const l = info.scenes.reduce((m, s) => (s.eind - s.start > m.eind - m.start ? s : m)); return <>Langste scène: {l.kop} ({sNaarTijd(l.eind - l.start)}).</>; })()} />
          </ul>
        </>) : <div className="mt-3 text-[14px] text-slate-400">In dit script staan geen scènes met tijden (zoals "Scène 1 (0:00-0:09)"). Open het hele script hierboven.</div>)}
      </section>

      {info && open != null && info.scenes[open] && (
        <section className="panel p-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <span className="font-display text-[17px] font-bold text-white">{info.scenes[open].kop}</span>
            <span className="text-[13px] text-slate-400">{sNaarTijd(info.scenes[open].start)} - {sNaarTijd(info.scenes[open].eind)}{info.scenes[open].start < 5 ? ' · bevat de hook' : ''}</span>
          </div>
          <div className="mt-2 flex gap-2">
            <button className="btn-ghost !py-1 text-[13px]" disabled={open === 0} onClick={() => setOpen(open - 1)}>← Vorige</button>
            <button className="btn-ghost !py-1 text-[13px]" disabled={open >= info.scenes.length - 1} onClick={() => setOpen(open + 1)}>Volgende →</button>
          </div>
          <div className="mt-2 max-h-[60vh] overflow-y-auto"><Md text={info.scenes[open].tekst} compact /></div>
        </section>
      )}

      {info && (
        <section className="panel p-4">
          <div className="mb-2 font-display text-[17px] font-bold text-white">Alle scènes</div>
          <ol className="space-y-1">{info.scenes.map((s, i) => (
            <li key={i}><button onClick={() => setOpen(i)} className="flex w-full items-baseline gap-3 rounded-lg px-2 py-1.5 text-left hover:bg-white/5">
              <span className="w-24 shrink-0 font-mono text-[12px] text-slate-400">{sNaarTijd(s.start)}-{sNaarTijd(s.eind)}</span>
              <span className="min-w-0 flex-1"><span className="text-[14px] text-white">{s.kop}</span>{s.vo[0] && <span className="block truncate text-[12px] italic text-slate-400">{s.vo[0]}</span>}</span>
            </button></li>
          ))}</ol>
        </section>
      )}

      {info?.regels && (
        <details className="panel p-4">
          <summary className="cursor-pointer font-display text-[17px] font-bold text-white">Vaste regels in dit script</summary>
          <div className="mt-2"><Md text={info.regels} compact /></div>
        </details>
      )}
    </div>
  );
}
