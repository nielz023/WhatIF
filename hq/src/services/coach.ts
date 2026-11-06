/**
 * COACH SERVICE (CEO Coach, blueprint v2.0).
 * - systeemprompt (Deel 10) + vaste Driftmark-regels
 * - kennisbank: driftmark-hq/kennis/kennis.json uit de projectbestanden (v35: cursus, werkwijze, het hele
 *   projectgeheugen, alle threads en alle documenten), met public/kennis.json als ingebouwde reserve; zoeken op woorden
 * - coachgeheugen in de database: coach/geheugen (blijvend), coach/briefing (per dag),
 *   coach/doelen, besluit/* (beslissingen), coach/gesprek (laatste gesprek)
 * - gesprekken via de sample-capability; antwoorden kunnen ACTIE:/BESLISSING:/ONTHOUD:-regels bevatten
 * De coach voert zelf niets uit: een actie wordt pas een echte opdracht als niels op de knop drukt.
 */
import { create } from 'zustand';
import type { Live } from './live';
import type { StatRow } from './db';
import { leesJson } from './threads';

/* ---------- typen ---------- */
export type FragmentSoort = 'cursus' | 'driftmark' | 'geheugen' | 'document' | 'gesprek';
/** waar een fragment vandaan komt: een geheugennotitie (id = naam, of MEMORY voor het overzicht), een gesprek
 *  (id = thread-id of "projectchat", msg = het bericht) of een document (id = pad in de projectbestanden) */
export interface Bron { type: 'geheugen' | 'gesprek' | 'document'; id: string; msg?: string; at?: string }
export interface Fragment { doc: string; soort?: FragmentSoort; taal: string; hoofdstuk: string; onderwerp: string; tekst: string; bron?: Bron }
export interface Kennis {
  gemaakt?: string; bronnen: { doc: string; taal: string; soort: FragmentSoort; fragmenten: number }[]; fragmenten: Fragment[];
  /** bestanden: de volledige kennis uit de projectbestanden; ingebouwd: de reserve in de pagina (cursus en werkwijze) */
  uit?: 'bestanden' | 'ingebouwd';
  /** bij de reserve: waarom het volledige bestand niet gelezen kon worden (not_found, geen-files, not_granted, ...) */
  waarom?: string;
}
export interface Geheugen { profiel: string[]; kanaal: string[]; strategie: string[]; beslissingen: string[]; lessen: string[]; bijgewerkt?: string }
export interface Actie { prioriteit: 'hoog' | 'middel' | 'laag'; omschrijving: string; reden: string; resultaat: string; wie: string; niveau?: 1 | 2 | 3 }
export interface Briefing { datum: string; gemaakt: string; samenvatting: string; kanaal: string[]; productie: string[]; agents: string[]; financien: string[]; problemen: string[]; kansen: string[]; acties: Actie[] }
export interface Doel { id: string; tekst: string; meet?: 'abonnees' | 'weergaven' | 'videos' | 'vrij'; doel?: number; deadline?: string; klaar?: boolean }
export interface Besluit { id: string; at: string; vraag: string; waarom?: string; bron: 'coach' | 'taak'; status: 'open' | 'goedgekeurd' | 'afgewezen'; opdracht?: string; besloten?: string }
export interface Rapport { id: string; soort: 'week' | 'maand' | 'advies'; at: string; tekst: string }
export type Msg = { role: 'user' | 'assistant'; content: string };

export const LEEG: Geheugen = { profiel: [], kanaal: [], strategie: [], beslissingen: [], lessen: [] };
export const VAK: Record<keyof Omit<Geheugen, 'bijgewerkt'>, string> = { profiel: 'Over jou', kanaal: 'Kanaalprofiel', strategie: 'Strategie en doelen', beslissingen: 'Beslissingen', lessen: 'Lessen' };

/** Startgeheugen uit wat al bekend is (alleen als de database nog leeg is). */
export const START_GEHEUGEN: Geheugen = {
  profiel: ['niels, tiener, Nederlands. Praat altijd Nederlands met hem; scripts zelf zijn Engels.', 'Wil niet om toestemming gevraagd worden voor gewone stappen: gewoon doen.', 'Wil direct een melding als iets mislukt of stilvalt.', 'Uploaden naar YouTube doet niels zelf.'],
  kanaal: ['Driftmark (@driftmark3d): faceless 3D "What IF"-video\'s met één naamloos hoofdpersonage en zijn gezin.', 'Format: lange video ~12-18 min per week + teaser-shorts (staand, 30-45 s) met cliffhanger en link naar de lange video.', 'Stijl: glans-look (vinyl-speelgoed), voorbeeldkanaal IFOLOGY. Stem via ElevenLabs, alles in Blender (UE5 voor grote buitenshots).'],
  strategie: ['Elke week één lange video, shorts sturen kijkers naar de lange video.', 'Onderwerpen met escalatie: eerst leuk, dan indrukwekkend, dan gevaarlijk, dan een twist.'],
  beslissingen: ['Video 2 niet meer aanpassen (1 nov).', 'Niet verwijzen naar de volgende video aan het eind (4 nov).', 'Renderen in 30 fps; niels maakt er 60 fps van in CapCut.'],
  lessen: ['Video 1: 2/3 van de kijkers weg in de eerste minuut. Hook binnen 5 s, geen uitleg in de eerste minuut.', 'Shorts doen 1,2-1,8K views, lange video\'s blijven achter: de brug van short naar lange video is het grootste groeipunt.', 'Veelgemaakte fouten in animatie: clipping, uitgerekte armen, zwevende props, open sets. Check vóór elke render.'],
};

/* ---------- systeemprompt (Deel 10 van de blueprint) ---------- */
export const SYSTEEM = `Je bent Claude, de CEO Coach van Driftmark HQ: de persoonlijke YouTube Business Coach, strategisch adviseur en rechterhand van niels, de eigenaar (CEO) van het YouTube-kanaal Driftmark.

MISSIE: help de CEO Driftmark uit te bouwen tot een professioneel, efficiënt en winstgevend YouTube-productiebedrijf: betere beslissingen, sterke strategie, betere video's, efficiëntere productie, AI-agents (de Claude-threads) goed aansturen, kosten beheersen, groeikansen zien.

GEDRAG: denk als een ervaren ondernemer. Direct, eerlijk, kritisch en oplossingsgericht. Geef niet automatisch gelijk; is een idee niet verstandig, zeg dat met de reden en een beter alternatief. Noem je een probleem, geef dan altijd een oplossing. Standaard kort en praktisch (max ~150 woorden), alleen uitgebreid als daarom gevraagd wordt. Antwoord ALTIJD in het Nederlands; niels is een tiener, dus helder en zonder vakjargon zonder uitleg.

BESLISPROCES: 1) begrijp het doel, 2) gebruik de bedrijfsgegevens hieronder, 3) gebruik de kennisfragmenten hieronder, 4) analyseer, 5) noem problemen en kansen, 6) geef de beste aanbeveling, 7) concrete vervolgstappen. Maak onderscheid tussen FEIT (staat in de gegevens), AANNAME, VERWACHTING en ADVIES. Verzin NOOIT cijfers, statistieken, kosten of resultaten: staat iets niet in de gegevens, zeg dat het ontbreekt. Gegevens uit "het spel" (Studio, speelgeld, spelcijfers) zijn NIET echt; gebruik alleen de echte gegevens.

KENNIS: de cursus van niels, het Faceless YouTube Handboek (Faceless Education, NL), is de primaire kennisbron. Vaste richtwaarden uit de cursus: CTR 5%+ minimaal, 10%+ geweldig, 15%+ uitstekend (evergreen); AVD <30% werk nodig, 30-40% oké, 40-50% goed, 50%+ geweldig; 1 like per 100 views, 1 abonnee per 100-200 kijkers; video's 10-15 min met 50%+ AVD; YPP = 1.000 abonnees + 4.000 kijkuren in 12 maanden; titel max 100 tekens, elk woord met hoofdletter; thumbnail max 3 elementen, fel en contrastrijk; testfase 5 video's, dan beslissen; één van de eerste 5-10 video's met 1K+ views → maak 3-5 video's over dat onderwerp vanuit een andere hoek. Gebruik je een fragment, noem dan kort de bron tussen haakjes, bijv. (bron: Lessen video 1). De kennisbank bevat nu ook het volledige projectgeheugen (alle vaste regels en lessen), alle threads met het hele gesprek en alle documenten; noem die net zo, bijv. (bron: Geheugen: Cursus regels) of (bron: Thread: Animeer video 3: geen regels meer). Staat iets niet in de cursus of fragmenten, zeg dan dat het jouw eigen advies is en geen cursusadvies.

BEVOEGDHEDEN:
- Niveau 1 (zelf): vragen beantwoorden, analyseren, rapporten, strategie voorstellen, problemen signaleren.
- Niveau 2 (interne actie, niels drukt op de knop): taak voor een Claude-thread, onderzoek starten, rapport opslaan. Zet zo'n voorstel op een eigen regel: "ACTIE: <korte opdracht voor Claude>".
- Niveau 3 (CEO-goedkeuring verplicht): YouTube-publicatie, externe publicatie, grote uitgaven, budget, nieuwe abonnementen, grote strategiewijziging, onomkeerbare acties. Zet dat op een eigen regel: "BESLISSING: <vraag aan de CEO>".
- Iets blijvends over niels of het bedrijf geleerd (doel, voorkeur, besluit, les)? Zet het op een eigen regel: "ONTHOUD: <vak>: <zin>" met vak = profiel, kanaal, strategie, beslissingen of lessen. Gewone gesprekspraat NIET onthouden.
Claim NOOIT dat iets is uitgevoerd: jij adviseert, de knop of de CEO zet het in gang, en een agent-resultaat controleer je pas als het in de gegevens staat.

EINDDOEL: maak de CEO elke dag beter in het leiden van zijn YouTube-bedrijf. Claude denkt mee. De agents voeren uit. De CEO beslist.`;

/* ---------- kennisbank ---------- */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
const KENNIS_PAD = 'driftmark-hq/kennis/kennis.json';
const SOORTEN = new Set<string>(['cursus', 'driftmark', 'geheugen', 'document', 'gesprek']);
const BRONTYPES = new Set<string>(['geheugen', 'gesprek', 'document']);
const tekstOf = (x: unknown) => (typeof x === 'string' ? x : '');
/** Leest een kennisbestand; kapotte stukjes vallen weg. null: geen kennisbestand. */
function leesKennis(j: Any, uit: Kennis['uit'], waarom?: string): Kennis | null {
  if (!j || typeof j !== 'object' || !Array.isArray(j.fragmenten)) return null;
  const fragmenten: Fragment[] = [];
  for (const f of j.fragmenten) {
    if (!f || typeof f !== 'object' || typeof f.tekst !== 'string' || !f.tekst.trim()) continue;
    const b = f.bron;
    const bron: Bron | undefined = b && typeof b === 'object' && BRONTYPES.has(b.type) && typeof b.id === 'string' && b.id.trim()
      ? { type: b.type, id: b.id.trim(), ...(typeof b.msg === 'string' && b.msg ? { msg: b.msg } : {}), ...(typeof b.at === 'string' ? { at: b.at } : {}) } : undefined;
    fragmenten.push({
      doc: tekstOf(f.doc).trim() || 'Onbekend', soort: SOORTEN.has(f.soort) ? f.soort : undefined, taal: tekstOf(f.taal) || 'nl',
      hoofdstuk: tekstOf(f.hoofdstuk), onderwerp: tekstOf(f.onderwerp), tekst: f.tekst, ...(bron ? { bron } : {}),
    });
  }
  const bronnen = (Array.isArray(j.bronnen) ? j.bronnen : []).filter((x: Any) => x && typeof x.doc === 'string')
    .map((x: Any) => ({ doc: x.doc, taal: tekstOf(x.taal) || 'nl', soort: (SOORTEN.has(x.soort) ? x.soort : 'driftmark') as FragmentSoort, fragmenten: Number.isFinite(x.fragmenten) ? Number(x.fragmenten) : 0 }));
  return { gemaakt: tekstOf(j.gemaakt) || undefined, bronnen, fragmenten, uit, ...(waarom ? { waarom } : {}) };
}
let kennisP: Promise<Kennis> | null = null;
/** wanneer de ingebouwde reserve geladen werd omdat het volledige bestand er (nog) niet was; 0 = niet */
let reserveSinds = 0;
/**
 * De kennisbank, pas geladen als de coach of Kennis › Zoeken hem nodig heeft (het bestand is ruim 1,5 MB).
 * Eerst het volledige bestand uit de projectbestanden; lukt dat niet, dan de ingebouwde ./kennis.json. Na zo'n
 * reserve wordt het volledige bestand na 5 minuten opnieuw geprobeerd (het komt elk uur).
 */
export function laadKennis(): Promise<Kennis> {
  if (kennisP && reserveSinds && Date.now() - reserveSinds > 5 * 60000) { kennisP = null; reserveSinds = 0; }
  if (!kennisP) {
    kennisP = (async () => {
      let r = await leesJson(KENNIS_PAD).catch(() => ({ ok: false as const, code: 'unavailable' }));
      // net veranderd, even te druk of half geschreven: nog één keer
      if (!r.ok && ['changed', 'rate_limited', 'kapot'].includes(r.code)) { await new Promise((ok) => setTimeout(ok, 2500)); r = await leesJson(KENNIS_PAD).catch(() => ({ ok: false as const, code: 'unavailable' })); }
      let k = r.ok ? leesKennis(r.data, 'bestanden') : null;
      if (!k) {
        const code = r.ok ? 'vorm' : r.code;
        const j = await fetch('./kennis.json').then((x) => (x.ok ? x.json() : null)).catch(() => null);
        k = leesKennis(j, 'ingebouwd', code) ?? { bronnen: [], fragmenten: [], uit: 'ingebouwd', waarom: code };
        // geen projectbestanden in deze weergave of geen toestemming: niet blijven proberen
        if (code !== 'geen-files' && code !== 'not_granted') reserveSinds = Date.now();
      }
      useCoach.setState({ kennis: k });
      return k;
    })();
  }
  return kennisP;
}
const STOP = new Set('de het een en van in op te is dat je ik wat hoe voor met mijn niet er aan als ook bij of naar zijn maar om dan nog wel kan the a of to and is in for you how what'.split(' '));
const woorden = (t: string) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9]+/).filter((w) => w.length > 2 && !STOP.has(w));
/** de woorden van elk fragment, één keer geteld en daarna bewaard (de kennisbank heeft bijna 2000 stukjes) */
const woordCache = new WeakMap<Fragment, Map<string, number>>();
function woordenVan(f: Fragment) {
  let m = woordCache.get(f);
  if (!m) { m = new Map(); for (const w of woorden(`${f.hoofdstuk} ${f.onderwerp} ${f.tekst}`)) m.set(w, (m.get(w) ?? 0) + 1); woordCache.set(f, m); }
  return m;
}
/** vaste regels en de cursus wegen zwaarder dan losse gespreksberichten */
const GEWICHT: Partial<Record<FragmentSoort, number>> = { cursus: 1.4, geheugen: 1.3, gesprek: 0.9 };
export function zoek(k: Kennis, vraag: string, n = 4): Fragment[] {
  const q = [...new Set(woorden(vraag))];
  if (!q.length) return [];
  const scores = k.fragmenten.map((f) => {
    const set = woordenVan(f);
    let s = 0;
    for (const w of q) {
      const c = set.get(w); if (c) s += 3 + Math.min(c, 4);
      if (w.length > 4) { const p = w.slice(0, 5); for (const h of set.keys()) if (h !== w && h.startsWith(p)) s += 1; }
    }
    if (f.onderwerp && q.some((w) => f.onderwerp.includes(w))) s += 4;
    return { f, s: s * (GEWICHT[f.soort ?? 'driftmark'] ?? 1) };
  });
  return scores.filter((x) => x.s > 3).sort((a, b) => b.s - a.s).slice(0, n).map((x) => x.f);
}
const SOORT_LABEL: Record<FragmentSoort, string> = { cursus: 'CURSUS', driftmark: 'Driftmark', geheugen: 'GEHEUGEN', document: 'DOCUMENT', gesprek: 'GESPREK' };
export const fragmentTekst = (fs: Fragment[]) => fs.length ? fs.map((f, i) => `[${i + 1}] ${SOORT_LABEL[f.soort ?? 'driftmark']} · bron: ${f.doc} (${f.taal.toUpperCase()}), ${f.hoofdstuk}\n${f.tekst.slice(0, 900)}`).join('\n\n') : '(geen passende fragmenten gevonden)';

/* ---------- bedrijfsgegevens als tekst ---------- */
export function bedrijf(d: Live, stats: StatRow[], g: Geheugen, doelen: Doel[]): string {
  const v = d.videos.map((x) => `- Video ${x.nr} "${x.title}": ${x.status}; stap nu: ${x.steps.find((s) => s.active)?.label ?? (x.steps.every((s) => s.done) ? 'alles klaar' : '?')}${x.notes?.length ? ` (${x.notes.slice(-2).join('; ').slice(0, 160)})` : ''}`).join('\n');
  const a = d.activity.map((x) => `- [${x.state}] ${x.title}: ${x.doing ?? ''} (laatst ${x.last})`).join('\n');
  const mmss = (x?: number) => (x == null ? '' : `${Math.floor(x / 60)}:${String(Math.round(x % 60)).padStart(2, '0')}`);
  const yt = (d.youtube?.videos ?? []).slice(0, 24).map((x) => `- ${x.type === 'long' ? 'LANG' : 'short'} "${x.title}" ${x.datum ?? x.date ?? ''}${x.status && x.status !== 'public' ? ' ' + x.status : ''}: ${x.views ?? 0} views, ${x.likes ?? '?'} likes${x.comments != null ? `, ${x.comments} reacties` : ''}${x.avd != null ? `, gem. kijkduur ${mmss(x.avd)} (${x.avp}% bekeken)` : ''}${x.subs != null ? `, +${x.subs} abonnees` : ''}`).join('\n');
  const longs = (d.youtube?.videos ?? []).filter((x) => x.type === 'long' && x.avd != null);
  const ret = longs.length ? `Kijkduur lange video's (vidIQ, ververst ${d.youtube?.vidiqAt?.slice(0, 16) ?? '?'}): ${longs.map((x) => `"${x.title.slice(0, 40)}" ${mmss(x.avd)} (${x.avp}%)`).join('; ')}. Video 1: 2/3 van de kijkers weg in de eerste minuut (Studio-screenshot 1 nov).` : 'Kijkduur per video: nog niet opgehaald.';
  const st = stats.length > 1 ? `Abonnees ${stats[0].subscribers} → ${stats[stats.length - 1].subscribers}, weergaven ${stats[0].views} → ${stats[stats.length - 1].views} (meting ${stats[0].at.slice(0, 16)} tot ${stats[stats.length - 1].at.slice(0, 16)}).` : 'Nog geen cijfergeschiedenis.';
  const kosten = (d.costs ?? []).slice(0, 10).map((c) => `- ${c.datum} ${c.wat}: ${c.bedrag != null ? '€' + c.bedrag : c.credits ?? '?'}${c.notitie ? ' (' + c.notitie + ')' : ''}`).join('\n') || '- (geen kosten geregistreerd)';
  const mem = (Object.keys(VAK) as (keyof typeof VAK)[]).map((k) => `${VAK[k]}:\n${(g[k] ?? []).map((x) => '- ' + x).join('\n') || '- (leeg)'}`).join('\n');
  const dl = doelen.length ? doelen.map((x) => `- ${x.klaar ? '[gehaald] ' : ''}${x.tekst}${x.doel ? ` (doel ${x.doel} ${x.meet})` : ''}${x.deadline ? ` vóór ${x.deadline}` : ''}`).join('\n') : '- (nog geen doelen ingesteld)';
  const bl = d.blender ? `Blender op pc: ${d.blender.stand} (bijgewerkt ${d.blender.bijgewerkt})` : '';
  return `=== ECHTE BEDRIJFSGEGEVENS (stand ${d.updated}) ===
KANAAL: Driftmark, ${d.youtube?.subscribers ?? '?'} abonnees, ${d.youtube?.views ?? '?'} weergaven, ${d.youtube?.videoCount ?? '?'} video's. ${st}
${ret} CTR, impressies en RPM zijn NIET beschikbaar in het HQ (alleen in YouTube Studio).
VIDEO'S IN PRODUCTIE:\n${v}
AGENTS (Claude-threads):\n${a}
${bl}
YOUTUBE (laatste uploads):\n${yt}
KOSTEN:\n${kosten}
DOELEN:\n${dl}
=== COACHGEHEUGEN ===\n${mem}`;
}

/* ---------- regels uit een antwoord halen ---------- */
export function parse(t: string) {
  const acties = [...t.matchAll(/^\s*ACTIE:\s*(.+)$/gim)].map((m) => m[1].trim());
  const besluiten = [...t.matchAll(/^\s*BESLISSING:\s*(.+)$/gim)].map((m) => m[1].trim());
  const onthoud = [...t.matchAll(/^\s*ONTHOUD:\s*(profiel|kanaal|strategie|beslissingen|lessen)\s*:\s*(.+)$/gim)].map((m) => ({ vak: m[1].toLowerCase() as keyof typeof VAK, tekst: m[2].trim() }));
  const schoon = t.replace(/^\s*(ACTIE|BESLISSING|ONTHOUD|OPDRACHT):.*$/gim, '').trim();
  const opdracht = t.match(/^\s*OPDRACHT:\s*(.+)$/im)?.[1]?.trim();
  if (opdracht) acties.push(opdracht);
  return { schoon, acties, besluiten, onthoud };
}

/* ---------- capabilities ---------- */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let sampleFn: any = null; let dbRef: any = null;
interface CS {
  klaar: boolean; kanVragen: boolean | null; dbOk: boolean;
  kennis: Kennis | null; geheugen: Geheugen; briefing: Briefing | null; doelen: Doel[]; besluiten: Besluit[]; rapporten: Rapport[]; gesprek: Msg[];
}
export const useCoach = create<CS>(() => ({ klaar: false, kanVragen: null, dbOk: false, kennis: null, geheugen: LEEG, briefing: null, doelen: [], besluiten: [], rapporten: [], gesprek: [] }));

let gestart = false;
export async function startCoach() {
  if (gestart) return; gestart = true;
  // de kennisbank (ruim 1,5 MB) laadt pas als de coach hem nodig heeft: bij een vraag, de briefing of Kennis
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const c = (window as any).claude;
  if (!c?.use) { useCoach.setState({ kanVragen: false, klaar: true }); return; }
  c.use('sample').then((s: unknown) => { sampleFn = s; useCoach.setState({ kanVragen: !!s }); }).catch(() => useCoach.setState({ kanVragen: false }));
  try { dbRef = await c.use('db'); } catch { dbRef = null; }
  if (!dbRef) { useCoach.setState({ klaar: true }); return; }
  const t = setTimeout(() => useCoach.setState({ klaar: true }), 10000);
  const fout = (e: unknown) => { clearTimeout(t); console.warn('[coach] db', e); useCoach.setState({ klaar: true }); };
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.doc('coach/geheugen').onSnapshot((d: any) => { clearTimeout(t); useCoach.setState({ geheugen: d.exists ? { ...LEEG, ...d.data() } : START_GEHEUGEN, dbOk: true, klaar: true }); }, fout);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.doc('coach/briefing').onSnapshot((d: any) => useCoach.setState({ briefing: d.exists ? (d.data() as Briefing) : null }), fout);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.doc('coach/doelen').onSnapshot((d: any) => useCoach.setState({ doelen: d.exists ? ((d.data().lijst ?? []) as Doel[]) : [] }), fout);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.doc('coach/gesprek').onSnapshot((d: any) => { if (d.exists && !useCoach.getState().gesprek.length) useCoach.setState({ gesprek: (d.data().msgs ?? []) as Msg[] }); }, fout);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.collection('besluit').orderBy('at', 'desc').limit(40).onSnapshot((s: any) => useCoach.setState({ besluiten: s.docs.map((x: any) => x.data() as Besluit) }), fout);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dbRef.collection('rapport').orderBy('at', 'desc').limit(20).onSnapshot((s: any) => useCoach.setState({ rapporten: s.docs.map((x: any) => x.data() as Rapport) }), fout);
  } catch (e) { fout(e); }
}

async function schrijf(pad: string, data: unknown) {
  if (!dbRef) throw new Error('Database niet beschikbaar (alleen op de gepubliceerde pagina).');
  await dbRef.doc(pad).set(data);
}
export async function bewaarGeheugen(g: Geheugen) { useCoach.setState({ geheugen: g }); await schrijf('coach/geheugen', { ...g, bijgewerkt: new Date().toISOString() }); }
export async function onthoud(vak: keyof typeof VAK, tekst: string) {
  const g = useCoach.getState().geheugen; if ((g[vak] ?? []).includes(tekst)) return;
  await bewaarGeheugen({ ...g, [vak]: [...(g[vak] ?? []), tekst] });
}
export async function bewaarDoelen(lijst: Doel[]) { useCoach.setState({ doelen: lijst }); await schrijf('coach/doelen', { lijst }); }
export async function nieuwBesluit(vraag: string, bron: Besluit['bron'], waarom?: string, opdracht?: string) {
  const id = `${Date.now()}`; const b: Besluit = { id, at: new Date().toISOString(), vraag, bron, status: 'open', ...(waarom ? { waarom } : {}), ...(opdracht ? { opdracht } : {}) };
  await schrijf(`besluit/${id}`, b); return b;
}
export async function zetBesluit(b: Besluit, status: Besluit['status']) { await schrijf(`besluit/${b.id}`, { ...b, status, besloten: new Date().toISOString() }); }
export async function bewaarGesprek(msgs: Msg[]) { useCoach.setState({ gesprek: msgs }); if (dbRef) { try { await dbRef.doc('coach/gesprek').set({ msgs: msgs.slice(-30) }); } catch { /* geen schrijfrecht */ } } }

function foutTekst(e: unknown) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const code = (e as any)?.code;
  return code === 'not_granted' ? 'Ik mag nog geen vragen beantwoorden. Sta het toe als claude.ai erom vraagt.' : code === 'rate_limited' ? 'Even rustig aan, probeer het zo nog eens.' : 'Dat lukte nu niet. Probeer het zo nog een keer.';
}

/** Stelt een vraag aan de coach met systeemprompt, bedrijfsgegevens en kennisfragmenten. */
export async function vraag(geschiedenis: Msg[], data: Live, stats: StatRow[], onText: (t: string) => void, opts: { lang?: boolean } = {}): Promise<{ tekst: string; bronnen: Fragment[] }> {
  if (!sampleFn) return { tekst: 'Vragen stellen werkt alleen op de gepubliceerde pagina in claude.ai.', bronnen: [] };
  const s = useCoach.getState();
  const k = s.kennis ?? await laadKennis();
  const laatste = geschiedenis[geschiedenis.length - 1]?.content ?? '';
  const fr = zoek(k, laatste + ' ' + (geschiedenis[geschiedenis.length - 3]?.content ?? ''), k.uit === 'bestanden' ? 6 : 4);
  const cursus = k.bronnen.some((b) => b.soort === 'cursus') ? 'De cursus staat in de kennisbank.' : 'LET OP: de cursus staat niet in de kennisbank; je hebt alleen Driftmark-documenten. Zeg dat als iemand cursusadvies vraagt.';
  const kop = `${SYSTEEM}\n\n${bedrijf(data, stats, s.geheugen, s.doelen)}\n\n=== KENNISFRAGMENTEN ===\n${cursus}\n${fragmentTekst(fr)}\n\nDatum nu: ${new Date().toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam' })}.`;
  const msgs: Msg[] = geschiedenis.slice(-12);
  const input: Msg[] = [{ role: 'user', content: `${kop}\n\n--- Bericht van de CEO ---\n${msgs[0].content}` }, ...msgs.slice(1)];
  try {
    const r = await sampleFn(input.length === 1 ? input[0].content : input, { cache: false, modelTier: opts.lang ? 'default' : 'quick', onText: ({ text }: { text: string }) => onText(text) });
    return { tekst: r.text, bronnen: fr };
  } catch (e) { return { tekst: foutTekst(e), bronnen: [] }; }
}

/** Dagelijkse CEO-briefing + actieplan (max 5), opgeslagen in coach/briefing. */
export async function maakBriefing(data: Live, stats: StatRow[]): Promise<Briefing | string> {
  if (!sampleFn) return 'De briefing maken werkt alleen op de gepubliceerde pagina in claude.ai.';
  const s = useCoach.getState();
  const k = s.kennis ?? await laadKennis();
  const fr = zoek(k, 'retentie hook groei shorts kwaliteit fouten', 4);
  const prompt = `${SYSTEEM}\n\n${bedrijf(data, stats, s.geheugen, s.doelen)}\n\n=== KENNIS ===\n${fragmentTekst(fr)}\n\nMaak de DAILY CEO BRIEFING voor vandaag (${new Date().toLocaleDateString('nl-NL', { timeZone: 'Europe/Amsterdam' })}). Alleen feiten uit de gegevens; ontbreekt iets (bv. CTR, API-kosten), zeg dat het ontbreekt. Korte zinnen, Nederlands.
Geef ALLEEN JSON in deze vorm:
{"samenvatting":"1-2 zinnen: hoe staat Driftmark ervoor","kanaal":["..."],"productie":["lopend / klaar / vastgelopen"],"agents":["welke threads bezig, wachten of aandacht nodig"],"financien":["..."],"problemen":["probleem + oplossing"],"kansen":["..."],"acties":[{"prioriteit":"hoog|middel|laag","omschrijving":"wat","reden":"waarom","resultaat":"verwacht resultaat","wie":"niels of Claude (welke thread)","niveau":1|2|3}]}
Maximaal 5 acties, belangrijkste eerst. niveau 2 = Claude kan het doen na een klik, niveau 3 = CEO-besluit nodig.`;
  try {
    const j = await sampleFn.json(prompt, { cache: false, modelTier: 'default' });
    const b: Briefing = { datum: new Date().toISOString().slice(0, 10), gemaakt: new Date().toISOString(), samenvatting: String(j.samenvatting ?? ''), kanaal: j.kanaal ?? [], productie: j.productie ?? [], agents: j.agents ?? [], financien: j.financien ?? [], problemen: j.problemen ?? [], kansen: j.kansen ?? [], acties: (j.acties ?? []).slice(0, 5) };
    useCoach.setState({ briefing: b });
    try { await schrijf('coach/briefing', b); } catch { /* alleen lokaal */ }
    return b;
  } catch (e) { return foutTekst(e); }
}

/** Week-, maand- of strategierapport (tekst), opgeslagen in rapport/*. */
export async function maakRapport(soort: Rapport['soort'], data: Live, stats: StatRow[]): Promise<Rapport | string> {
  if (!sampleFn) return 'Rapporten maken werkt alleen op de gepubliceerde pagina in claude.ai.';
  const s = useCoach.getState();
  const opdracht = soort === 'week'
    ? 'Maak de WEEKLY BUSINESS REVIEW met kopjes: 1 Kanaalgroei, 2 Videoprestaties, 3 Productiekwaliteit, 4 Productiesnelheid, 5 Kosten, 6 Agentprestaties, 7 Problemen, 8 Nieuwe kansen, 9 Aanbevelingen voor volgende week.'
    : soort === 'maand'
      ? 'Maak de MONTHLY STRATEGY REVIEW: doelstellingen, financiële prestaties, kanaalgroei, contentstrategie, productiecapaciteit, rendement, mogelijkheden om op te schalen. Sluit af met: strategie VOORTZETTEN, AANPASSEN of UITBREIDEN, met reden.'
      : 'Geef STRATEGISCH ADVIES: de 3 belangrijkste strategische aanbevelingen voor Driftmark nu, elk met reden, risico en eerste stap.';
  const prompt = `${SYSTEEM}\n\n${bedrijf(data, stats, s.geheugen, s.doelen)}\n\n${opdracht}\nGebruik markdown-kopjes (##) en korte opsommingen. Max 450 woorden. Alleen echte cijfers; ontbreekt iets, zeg het.`;
  try {
    const r = await sampleFn(prompt, { cache: false, modelTier: 'default' });
    const rap: Rapport = { id: `${Date.now()}`, soort, at: new Date().toISOString(), tekst: r.text };
    try { await schrijf(`rapport/${rap.id}`, rap); } catch { useCoach.setState({ rapporten: [rap, ...useCoach.getState().rapporten] }); }
    return rap;
  } catch (e) { return foutTekst(e); }
}
