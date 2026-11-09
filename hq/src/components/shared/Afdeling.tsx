/**
 * ELKE AFDELING DEZELFDE OPBOUW (verbeterlijst punt 50):
 *   1. wat deze afdeling doet,  2. wat nu loopt,  3. wat op niels wacht,  4. wat klaar is,  5. snelknoppen,
 * daarna het eigen gereedschap van de afdeling (children). Gebruikt door het afdelingspaneel in het 3D-kantoor
 * (world/HomeHud.tsx) en door de afdelingslade in Team (DepartmentDrawer.tsx).
 * Alles komt uit de echte stand (status.json); elke snelknop is een echte opdracht voor Claude.
 */
import { useMemo, type ReactNode } from 'react';
import { CheckCircle2, Clock, ExternalLink, Info, Loader2, MessageSquare, Zap } from 'lucide-react';
import { useLive, type Activity } from '../../services/live';
import { order } from '../../services/real';
import { useGame } from '../../store/useGame';
import { KLEUR } from '../../lib/status';
import { threadUrl } from '../../data/driftmark';
import { threadsPerRoom, type RoomDef, type RoomId } from '../../world/rooms';
import { openGesprek } from './Gesprek';

/** wat elke afdeling doet, in gewone woorden */
export const WAT_DOET: Record<RoomId, string> = {
  onderzoek: 'Zoekt onderwerpen die passen bij de What If-niche, volgt IFOLOGY en andere kanalen en leest de comments.',
  creatief: 'Maakt van een onderwerp een verloop met escalatie en twist, en bedenkt titels en hooks.',
  script: 'Schrijft het script en controleert de eerste 30 seconden (hook) en het tempo.',
  stem: 'Neemt de voice-overs en dialogen op in ElevenLabs en controleert of elke regel klaar is.',
  productie: 'Bouwt cast en sets in Blender, animeert de scènes, controleert de stills en rendert op je pc.',
  thumbnail: 'Ontwerpt de thumbnail en drie varianten voor Test & compare.',
  publicatie: 'Maakt de uploadtekst, plant de upload en de shorts en doet de 48-uurcheck.',
  ceo: 'Volgt je cijfers (weergaven, kijkduur, abonnees), schrijft het weekrapport en zet de koers uit.',
  crisis: 'Komt alleen in actie als er echt iets misgaat: een mislukte taak, een vastgelopen render of een volle schijf.',
  coach: 'Je coach: briefing, doelen, beslissingen en antwoord op elke vraag over je kanaal.',
};

/** snelknoppen per afdeling: elke knop is een echte opdracht */
export const SNEL: Record<RoomId, string[]> = {
  onderzoek: ['Zoek drie nieuwe onderwerpen die nu goed werken in de What If-niche.', 'Haal de nieuwste uploads van IFOLOGY op en zeg wat ik ervan kan leren.', 'Lees de comments van mijn laatste video en vat samen wat kijkers willen.'],
  creatief: ['Bedenk 5 titels voor de volgende video volgens de cursusregels.', 'Maak een verloop met escalatie en twist voor het beste onderwerp van het onderwerpenbord.'],
  script: ['Controleer de hook (eerste 30 seconden) van het script dat nu in productie is.', 'Zoek in het script naar trage stukken in de eerste minuut.'],
  stem: ['Controleer of alle stemregels van de video in productie klaar zijn.', 'Maak een lijst van stemregels die opnieuw moeten.'],
  productie: ['Geef de stand van de renders van de video in productie.', 'Draai de kwaliteitscheck op alle scènes van de video in productie.'],
  thumbnail: ['Maak drie thumbnailvarianten voor de volgende video.', 'Vergelijk mijn laatste twee thumbnails en zeg wat beter kan.'],
  publicatie: ['Maak de uploadtekst (titel, beschrijving, tags, hoofdstukken) voor de volgende video.', 'Plan de shorts van de komende twee weken.'],
  ceo: ['Maak het weekrapport met de drie belangrijkste lessen.', "Vergelijk mijn laatste vijf video's en shorts en noem de grootste verschillen."],
  crisis: ['Controleer of er iets vastloopt of misgaat en los het op.'],
  coach: ['Geef me een briefing: wat is vandaag het belangrijkste?'],
};

const isWacht = (a: Activity) => a.state === 'blocked' || a.state === 'review_ready';
const kleurVan = (a: Activity) => (a.state === 'failed' ? KLEUR.probleem : isWacht(a) ? KLEUR.wacht : a.state === 'working' ? KLEUR.bezig : a.state === 'done' ? KLEUR.klaar : KLEUR.stil);

function Rij({ a }: { a: Activity }) {
  const c = kleurVan(a);
  return (
    <div className="group rounded-lg border border-white/[.06] bg-white/[.025] px-2.5 py-1.5 transition hover:border-white/20">
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: c, boxShadow: `0 0 8px ${c}` }} />
        <span className="min-w-0 flex-1 truncate text-[13px] font-semibold text-white">{a.title}</span>
        {(a.id || a.session) && <button className="shrink-0 rounded-md p-0.5 text-slate-400 hover:bg-white/10 hover:text-white" title="Hele gesprek lezen" aria-label="Hele gesprek lezen" onClick={() => openGesprek({ kind: 'thread', session: a.session, title: a.title, thread: a.id || undefined })}><MessageSquare size={13} /></button>}
        {a.id && <a href={threadUrl(a.id)} target="_blank" rel="noreferrer" title="Openen in Claude" aria-label="Openen in Claude"><ExternalLink size={12} className="shrink-0 text-slate-500 group-hover:text-white" /></a>}
      </div>
      {(a.needs || a.doing || a.last) && <div className="mt-0.5 line-clamp-2 pl-4 text-[12px] text-slate-400">{a.needs && isWacht(a) ? <span style={{ color: '#fed7aa' }}>Jij: {a.needs}</span> : a.doing ?? a.last}</div>}
    </div>
  );
}

function Blok({ titel, kleur, icon, aantal, leeg, children }: { titel: string; kleur: string; icon: ReactNode; aantal?: number; leeg: string; children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-white/[.07] bg-black/20 p-3">
      <div className="mb-1.5 flex items-center gap-1.5 text-[12px] font-bold uppercase tracking-wider" style={{ color: kleur }}>{icon}<span>{titel}</span>{aantal != null && <span className="ml-auto rounded-full px-1.5 text-[11px] normal-case tracking-normal" style={{ background: `${kleur}22` }}>{aantal}</span>}</div>
      {children ?? <div className="text-[12.5px] text-slate-500">{leeg}</div>}
    </div>
  );
}

/** De vaste opbouw van een afdeling. `info` = een paar echte regels over de stand; children = het eigen gereedschap. */
export default function Afdeling({ r, info, children, voor }: { r: RoomDef; info?: string[]; children?: ReactNode; voor?: ReactNode }) {
  const activity = useLive((s) => s.data.activity);
  const toast = useGame((s) => s.toast);
  const list = useMemo(() => threadsPerRoom(activity)[r.id] ?? [], [activity, r.id]);
  const nu = list.filter((a) => a.state === 'working');
  const fout = list.filter((a) => a.state === 'failed');
  const wacht = list.filter(isWacht);
  const klaar = list.filter((a) => a.state === 'done').sort((a, b) => (b.lastIso ?? '').localeCompare(a.lastIso ?? ''));
  return (
    <div className="space-y-3">
      <Blok titel="Wat deze afdeling doet" kleur={r.color} icon={<Info size={13} />} leeg="">
        <div className="text-[13px] leading-snug text-slate-200">{WAT_DOET[r.id]}</div>
        {!!info?.length && <div className="mt-1.5 space-y-0.5 text-[12.5px] text-slate-300">{info.map((x, i) => <div key={i} className="flex gap-2"><span style={{ color: r.color }}>›</span><span className="min-w-0">{x}</span></div>)}</div>}
      </Blok>
      {voor}
      {fout.length > 0 && <Blok titel="Mislukt" kleur={KLEUR.probleem} icon={<Info size={13} />} aantal={fout.length} leeg=""><div className="space-y-1.5">{fout.map((a) => <Rij key={a.id || a.session || a.title} a={a} />)}</div></Blok>}
      <Blok titel="Wacht op jou" kleur={KLEUR.wacht} icon={<Clock size={13} />} aantal={wacht.length} leeg="Niets: deze afdeling heeft nu niets van je nodig.">
        {wacht.length ? <div className="space-y-1.5">{wacht.map((a) => <Rij key={a.id || a.session || a.title} a={a} />)}</div> : undefined}
      </Blok>
      <Blok titel="Loopt nu" kleur={KLEUR.bezig} icon={<Loader2 size={13} />} aantal={nu.length} leeg="Er loopt nu geen taak voor deze afdeling.">
        {nu.length ? <div className="space-y-1.5">{nu.map((a) => <Rij key={a.id || a.session || a.title} a={a} />)}</div> : undefined}
      </Blok>
      <Blok titel="Klaar" kleur={KLEUR.klaar} icon={<CheckCircle2 size={13} />} aantal={klaar.length} leeg="Nog niets afgerond voor deze afdeling.">
        {klaar.length ? (
          <div className="space-y-1.5">
            {klaar.slice(0, 4).map((a) => <Rij key={a.id || a.session || a.title} a={a} />)}
            {klaar.length > 4 && <details className="text-[12px] text-slate-400"><summary className="cursor-pointer hover:text-white">Nog {klaar.length - 4} afgerond</summary><div className="mt-1.5 space-y-1.5">{klaar.slice(4).map((a) => <Rij key={a.id || a.session || a.title} a={a} />)}</div></details>}
          </div>
        ) : undefined}
      </Blok>
      <Blok titel="Snelknoppen" kleur={r.color} icon={<Zap size={13} />} leeg="">
        <div className="flex flex-wrap gap-1.5">
          {SNEL[r.id].map((t) => (
            <button key={t} onClick={() => order(`[Afdeling ${r.naam} · ${r.agent}] ${t}`, toast, { doel: r.naam })} title="Wordt een echte opdracht voor Claude"
              className="rounded-lg border px-2.5 py-1.5 text-left text-[12px] font-semibold text-white transition hover:brightness-125" style={{ borderColor: `${r.color}55`, background: `${r.color}18` }}>{t}</button>
          ))}
        </div>
      </Blok>
      {children}
    </div>
  );
}
