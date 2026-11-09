/**
 * RENDERS LIVE VOLGEN (verbeterlijst punt 10).
 * Per video: scènes klaar van totaal, verwachte eindtijd, vrije schijfruimte, het laatst gerenderde beeld
 * (als er een pad bekend is) en een rode melding bij een crash of als het te lang stil is.
 * Bronnen: het blender-veld in status.json en wat de renderthreads melden (activity[].doing).
 * Staat iets er niet in, dan zegt de pagina dat; er wordt niets geschat.
 */
import { AlertTriangle, MessageSquare } from 'lucide-react';
import { useLive } from '../../services/live';
import { renderStanden, bronTijd, kortTijd, type RenderStand } from '../../services/studio';
import { openGesprek } from '../../components/shared/Gesprek';
import { openBestand } from '../../components/shared/BestandViewer';
import { openOpdracht } from '../../services/real';
import { KLEUR } from '../../lib/status';
import Bron from '../../components/shared/Bron';
import Blok from '../../components/shared/Blok';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
const ONTBREEKT = 'niet gemeld';

function Kaart({ r }: { r: RenderStand }) {
  const kleur = r.kapot || r.stil ? KLEUR.probleem : r.state === 'working' ? KLEUR.bezig : r.state === 'blocked' || r.state === 'review_ready' ? KLEUR.wacht : KLEUR.stil;
  const pct = r.klaar != null && r.totaal ? Math.round((r.klaar / r.totaal) * 100) : null;
  return (
    <section className="panel p-4" style={{ borderColor: r.kapot || r.stil ? `${KLEUR.probleem}88` : undefined }}>
      {(r.kapot || r.stil) && (
        <div className="mb-2 flex items-start gap-2 rounded-xl px-3 py-2 text-[14px] font-semibold text-white" style={{ background: `${KLEUR.probleem}33` }} role="alert">
          <AlertTriangle size={16} className="mt-0.5 shrink-0" style={{ color: KLEUR.probleem }} />
          {r.kapot ? 'De render is vastgelopen of mislukt. Kijk in het gesprek wat er misging.' : `Sinds ${kortTijd(r.at) ?? 'lange tijd'} geen nieuws van deze render. Misschien staat hij stil.`}
        </div>
      )}
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-display text-[17px] font-bold text-white">{r.video ? `Video ${r.video}` : 'Render'} · {r.titel}</span>
        <span className="flex items-center gap-1.5 text-[13px] font-semibold" style={{ color: kleur }}><span className={`h-2.5 w-2.5 rounded-full ${r.state === 'working' && !r.stil ? 'animate-pulse' : ''}`} style={{ background: kleur }} />{r.kapot ? 'probleem' : r.stil ? 'stil?' : r.state === 'working' ? 'rendert' : 'wacht'}</span>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Cijfer label="Scènes klaar" waarde={r.klaar != null && r.totaal ? `${r.klaar} / ${r.totaal}` : ONTBREEKT} />
        <Cijfer label="Klaar" waarde={pct != null ? `${pct}%` : ONTBREEKT} />
        <Cijfer label="Vrije schijf" waarde={r.vrij ?? ONTBREEKT} />
        <Cijfer label="Laatste melding" waarde={bronTijd(r.at) ?? 'onbekend'} />
      </div>
      {pct != null && <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full" style={{ width: `${pct}%`, background: kleur }} /></div>}
      <div className="mt-2 text-[13px] text-slate-300"><span className="text-slate-500">Verwacht klaar: </span>{r.eind ?? 'de thread heeft nog geen eindtijd gemeld.'}</div>
      <div className="mt-1 text-[13px] text-slate-400">{r.tekst}</div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {r.frame ? <button className="btn-ghost !py-1 text-[13px]" onClick={() => openBestand(r.frame!)}>Laatste beeld bekijken</button> : <span className="text-[12px] text-slate-500">Geen pad naar het laatst gerenderde beeld bekend.</span>}
        {r.thread && <button className="btn-ghost !py-1 text-[13px]" onClick={() => openGesprek({ kind: 'thread', thread: r.thread!, title: r.titel })}><MessageSquare size={13} />Gesprek</button>}
        <button className="btn-ghost !py-1 text-[13px]" onClick={() => openOpdracht({ thread: r.thread, text: `Hoe staat de render van ${r.video ? `video ${r.video}` : r.titel}? Meld scènes klaar/totaal, vrije schijfruimte, verwachte eindtijd en het pad van het laatst gerenderde beeld in status.json.` })}>Stand opvragen</button>
        <Bron bron="thread" at={r.at} relatief className="ml-auto" />
      </div>
    </section>
  );
}

function Cijfer({ label, waarde }: { label: string; waarde: string }) {
  return (
    <div className="rounded-lg bg-white/[.04] px-2.5 py-1.5">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">{label}</div>
      <div className={`font-display text-[17px] font-bold ${waarde === ONTBREEKT ? 'text-slate-500' : 'text-white'}`}>{waarde}</div>
    </div>
  );
}

export default function Renders() {
  const activity = useLive((s) => s.data.activity);
  const blender = useLive((s) => s.data.blender) as Any;
  const lijst = renderStanden(activity);
  const wachtrij = Array.isArray(blender?.wachtrij) ? blender.wachtrij as { naam: string; status: string }[] : typeof blender?.wachtrij === 'string' ? blender.wachtrij : null;
  const frame = typeof blender?.frame === 'string' ? blender.frame : typeof blender?.laatsteBeeld === 'string' ? blender.laatsteBeeld : null;
  return (
    <div className="grid gap-3">
      <Blok naam="Blender op je pc">
        <section className="panel p-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <span className="font-display text-[18px] font-bold text-white">Blender op je pc</span>
            <Bron bron="status.json" at={blender?.bijgewerkt} relatief />
          </div>
          {blender ? (<>
            <p className="mt-1 text-[14px] text-slate-200">{blender.stand || 'Geen stand gemeld.'}</p>
            {wachtrij && (typeof wachtrij === 'string'
              ? <p className="mt-1 text-[13px] text-slate-400"><span className="text-slate-500">Wachtrij: </span>{wachtrij}</p>
              : <ul className="mt-1 space-y-0.5 text-[13px] text-slate-300">{(wachtrij as { naam: string; status: string }[]).map((w) => <li key={w.naam}>• {w.naam} <span className="text-slate-500">({w.status})</span></li>)}</ul>)}
            {frame && <button className="btn-ghost mt-2 !py-1 text-[13px]" onClick={() => openBestand(frame)}>Laatste beeld bekijken</button>}
            {blender.bijgewerkt && Date.now() - Date.parse(blender.bijgewerkt) > 12 * 36e5 && <p className="mt-2 text-[13px]" style={{ color: KLEUR.wacht }}>Deze stand is ouder dan 12 uur. Kijk hieronder wat de threads zelf melden.</p>}
          </>) : <p className="mt-1 text-[14px] text-slate-400">Er staat nog geen renderstand in status.json.</p>}
        </section>
      </Blok>
      {lijst.length ? lijst.map((r) => <Blok key={r.thread ?? r.titel} naam={`Render ${r.titel}`}><Kaart r={r} /></Blok>)
        : <div className="panel p-4 text-[14px] text-slate-400">Er loopt nu geen render volgens de threads. Zodra een thread meldt dat hij rendert, staat hij hier met scènes, schijfruimte en eindtijd.</div>}
      <p className="text-[12px] text-slate-500">Scènes, schijfruimte en eindtijd komen uit wat de renderthread zelf meldt (ongeveer elk uur). Een render die meer dan 3 uur niets meldt, kleurt rood.</p>
    </div>
  );
}
