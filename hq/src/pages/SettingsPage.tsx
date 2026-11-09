import { useState } from 'react';
import { PageHeader } from '../components/ui';
import { useWorld } from '../world/useWorld';
import Geluid from '../components/shared/Geluid';
import { prefs, setPref, type Prefs } from '../lib/prefs';
import { useTools } from '../services/tools';
import { useLive } from '../services/live';
import { useDb } from '../services/db';
import { useReal } from '../services/real';

type St = 'connected' | 'stub' | 'not_configured';
const LABEL: Record<St, string> = { connected: 'verbonden', stub: 'deels', not_configured: 'niet verbonden' };
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
function useRealConnections() {
  const tools = useTools((x) => x.tools);
  const live = useLive();
  const db = useDb();
  const avail = useReal((x) => x.avail);
  const ok = (k: string): St => (tools[k]?.status === 'ok' ? 'connected' : tools[k]?.status === 'laden' ? 'stub' : 'not_configured');
  const vqc = (tools.vidiqch?.data as Any)?.channels ?? [];
  const drift = vqc.find((c: Any) => /drift/i.test(c.title ?? ''));
  const hf = tools.higgsfield?.data as Any;
  const el = (tools.elevenlabs?.data as Any)?.flows ?? [];
  const bl = live.data.blender;
  const yt = live.data.youtube;
  return [
    { id: 'claude', name: 'Claude (opdrachten)', purpose: 'Denkwerk, scripts, animatie', status: (avail === 'available' ? 'connected' : avail === 'laden' ? 'stub' : 'not_configured') as St, note: avail === 'available' ? 'Echt: wat je in de HQ typt of klikt, voert Claude uit in je project.' : 'Claude luistert nu niet mee; opdrachten wachten in de wachtrij.' },
    { id: 'youtube', name: 'YouTube (via vidIQ)', purpose: 'Kanaalstatistieken lezen', status: (drift ? 'connected' : ok('vidiqch') === 'connected' ? 'stub' : ok('vidiqch')) as St, note: drift ? `Driftmark: ${Number(drift.subscriberCount).toLocaleString('nl-NL')} abonnees, ${Number(drift.viewCount).toLocaleString('nl-NL')} weergaven, ${drift.videoCount} video's. Uploaden doe je zelf in Studio.` : yt?.subscribers != null ? `Laatst bekend: ${yt.subscribers} abonnees (via Claude).` : 'vidIQ wordt nog geladen.' },
    { id: 'threads', name: 'Claude-threads', purpose: 'Wie werkt waaraan', status: (live.source === 'live' ? 'connected' : 'stub') as St, note: live.source === 'live' ? `${live.data.activity.length} threads live uit de projectbestanden, ververst elke minuut.` : 'Laatst bekende stand; live bestand nog niet gelezen.' },
    { id: 'voice', name: 'Stemmen (ElevenLabs v4)', purpose: 'Voice-overs', status: ok('elevenlabs'), note: ok('elevenlabs') === 'connected' ? `Verbonden, ${el.length} recente flows. Claude maakt de stemmen.` : 'ElevenLabs is nog niet bereikbaar vanaf deze pagina; Claude gebruikt hem wel.' },
    { id: 'image', name: 'Beelden (Higgsfield)', purpose: 'Thumbnails en upgrades', status: ok('higgsfield'), note: ok('higgsfield') === 'connected' ? `Verbonden, ${hf?.credits ?? 0} credits (${hf?.subscription_plan_type ?? 'gratis'}). Ook als add-on in Blender.` : 'Higgsfield is nog niet bereikbaar vanaf deze pagina.' },
    { id: 'video', name: 'Blender op je pc', purpose: 'Animatie en renders', status: (bl ? 'connected' : 'stub') as St, note: bl ? `${bl.stand} (bijgewerkt ${bl.bijgewerkt})` : 'Draait via Remote Control op je pc; de animatie-thread zet de stand hier neer.' },
    { id: 'db', name: 'Database (ingebouwd)', purpose: 'Cijfergeschiedenis, logboek, reserve-kopie', status: (db.ready ? 'connected' : db.offline ? 'stub' : 'stub') as St, note: db.ready ? `${db.stats.length} meetpunten, laatste ronde ${db.engine?.lastRun ? new Date(db.engine.lastRun).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam' }) : 'nog niet'}.` : 'Nog niet bereikbaar.' },
    { id: 'files', name: 'Projectbestanden', purpose: 'Opslag van alles', status: (live.source === 'live' ? 'connected' : 'stub') as St, note: 'Scripts, cast, sets en renders staan in de projectbestanden. Je instellingen staan alleen in deze browser.' },
  ];
}

const STATUS = {
  connected: 'bg-emerald-500/15 text-emerald-300',
  simulation: 'bg-cyan-500/15 text-cyan-300',
  stub: 'bg-amber-500/15 text-amber-300',
  not_configured: 'bg-slate-600/30 text-slate-400',
};

function Rij({ titel, uitleg, children }: { titel: string; uitleg: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl bg-white/[.03] p-3">
      <div className="min-w-0"><div className="text-[14px] font-semibold text-white">{titel}</div><div className="text-[12px] text-slate-400">{uitleg}</div></div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

function Seg<T extends string>({ value, opts, set }: { value: T; opts: [T, string][]; set: (v: T) => void }) {
  return (
    <div className="grid grid-flow-col gap-1 rounded-lg bg-black/30 p-1">
      {opts.map(([v, l]) => <button key={v} onClick={() => set(v)} className={`rounded-md px-2 py-1 text-[12px] font-semibold ${value === v ? 'bg-white/15 text-white' : 'text-slate-400 hover:text-white'}`}>{l}</button>)}
    </div>
  );
}

function Aan({ on, set }: { on: boolean; set: (v: boolean) => void }) {
  return <button onClick={() => set(!on)} className={`rounded-full px-3 py-1 text-[12px] font-bold ${on ? 'bg-emerald-500/20 text-emerald-300' : 'bg-white/10 text-slate-400'}`}>{on ? 'Aan' : 'Uit'}</button>;
}

/** Instellingen die echt iets doen (verbeterlijst punt 73). De oude spel-instellingen (API-sleutels, Supabase, opslaan/laden, reset) zijn weg (punt 38). */
export default function SettingsPage() {
  const ov = useRealConnections();
  const { theme, setTheme, focusMode, setFocusMode, quality, setQuality } = useWorld();
  const [p, setP] = useState<Prefs>(prefs());
  const zet = <K extends keyof Prefs>(k: K, v: Prefs[K]) => { setPref(k, v); setP(prefs()); };

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Instellingen" subtitle="Geluid, beeld, meldingen en koppelingen. Alles wordt alleen in deze browser bewaard." />
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="panel space-y-2 p-5">
          <div className="mb-1 font-semibold text-white">Geluid en beeld</div>
          <Rij titel="Geluid" uitleg="Eén schuif voor klikjes, meldingen en het kantoorgeluid. Links: dempen."><div className="w-56"><Geluid breed /></div></Rij>
          <Rij titel="3D-kwaliteit" uitleg="Auto past zich aan je computer aan. 4K is het scherpst, Snel het soepelst."><Seg value={quality} set={setQuality} opts={[['snel', 'Snel'], ['auto', 'Auto'], ['4k', '4K']]} /></Rij>
          <Rij titel="Licht in het kantoor" uitleg="Klok volgt de echte tijd."><Seg value={theme} set={setTheme} opts={[['auto', 'Klok'], ['dag', 'Dag'], ['nacht', 'Nacht']]} /></Rij>
          <Rij titel="Focusmodus" uitleg="Kantoor gedimd, alleen wat op jou wacht."><Aan on={focusMode} set={setFocusMode} /></Rij>
          <Rij titel="Minder beweging" uitleg="Geen inschuivende kaarten en optellende cijfers."><Aan on={p.minderBeweging} set={(v) => zet('minderBeweging', v)} /></Rij>
          <Rij titel="3D-kantoor op de telefoon" uitleg="Uit: op een klein scherm laadt het 3D-kantoor pas als je erom vraagt."><Aan on={p.telefoon3d} set={(v) => zet('telefoon3d', v)} /></Rij>
        </div>
        <div className="panel space-y-2 p-5">
          <div className="mb-1 font-semibold text-white">Meldingen</div>
          <Rij titel="Meldingen in het HQ" uitleg="Een melding rechtsboven als een taak klaar is of op jou wacht."><Aan on={p.meldingen} set={(v) => zet('meldingen', v)} /></Rij>
          <Rij titel="Geluid bij een melding" uitleg="Zacht belletje als er een antwoord of melding binnenkomt."><Aan on={p.meldingGeluid} set={(v) => zet('meldingGeluid', v)} /></Rij>
          <p className="pt-1 text-[12px] text-slate-500">Pushmeldingen op je telefoon komen via de Claude-app; die kan het HQ zelf niet sturen.</p>
        </div>
        <div className="panel p-5 xl:col-span-2">
          <div className="mb-3 font-semibold text-white">Echte koppelingen</div>
          <div className="grid gap-2 md:grid-cols-2">
            {ov.map((i) => (
              <div key={i.id} className="rounded-xl bg-white/[.03] p-3">
                <div className="flex items-center justify-between gap-2"><span className="font-semibold text-white">{i.name}</span><span className={`chip ${STATUS[i.status]}`}>{LABEL[i.status]}</span></div>
                <div className="text-[13px] text-slate-400">{i.purpose}: {i.note}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[13px] text-slate-500">Uploaden naar YouTube gebeurt nooit automatisch: dat doe je zelf in YouTube Studio. Het HQ zet alles voor je klaar.</p>
        </div>
      </div>
    </div>
  );
}
