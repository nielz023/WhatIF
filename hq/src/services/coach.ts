/**
 * COACH SERVICE (CEO Coach, blueprint v2.0).
 * - systeemprompt (Deel 10) + vaste Driftmark-regels
 * - kennisbank: public/kennis.json (gemaakt door automation/kennis.py), zoeken op woorden
 * - coachgeheugen in de database: coach/geheugen (blijvend), coach/briefing (per dag),
 *   coach/doelen, besluit/* (beslissingen), coach/gesprek (laatste gesprek)
 * - gesprekken via de sample-capability; antwoorden kunnen ACTIE:/BESLISSING:/ONTHOUD:-regels bevatten
 * De coach voert zelf niets uit: een actie wordt pas een echte opdracht als niels op de knop drukt.
 */
import { create } from 'zustand';
import type { Live } from './live';
import type { StatRow } from './db';

/* ---------- typen ---------- */
export interface Fragment { doc: string; taal: string; hoofdstuk: string; onderwerp: string; tekst: string }
export interface Kennis { gemaakt?: string; bronnen: { doc: string; taal: string; soort: 'cursus' | 'driftmark'; fragmenten: number }[]; fragmenten: Fragment[] }
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

KENNIS: de YouTube A-Z Guide (cursus) is de primaire kennisbron zodra die in de kennisbank staat. Gebruik je een fragment, noem dan kort de bron tussen haakjes, bijv. (bron: Lessen video 1). Staat iets niet in de cursus of fragmenten, zeg dan dat het jouw eigen advies is en geen cursusadvies.

BEVOEGDHEDEN:
- Niveau 1 (zelf): vragen beantwoorden, analyseren, rapporten, strategie voorstellen, problemen signaleren.
- Niveau 2 (interne actie, niels drukt op de knop): taak voor een Claude-thread, onderzoek starten, rapport opslaan. Zet zo'n voorstel op een eigen regel: "ACTIE: <korte opdracht voor Claude>".
- Niveau 3 (CEO-goedkeuring verplicht): YouTube-publicatie, externe publicatie, grote uitgaven, budget, nieuwe abonnementen, grote strategiewijziging, onomkeerbare acties. Zet dat op een eigen regel: "BESLISSING: <vraag aan de CEO>".
- Iets blijvends over niels of het bedrijf geleerd (doel, voorkeur, besluit, les)? Zet het op een eigen regel: "ONTHOUD: <vak>: <zin>" met vak = profiel, kanaal, strategie, beslissingen of lessen. Gewone gesprekspraat NIET onthouden.
Claim NOOIT dat iets is uitgevoerd: jij adviseert, de knop of de CEO zet het in gang, en een agent-resultaat controleer je pas als het in de gegevens staat.

EINDDOEL: maak de CEO elke dag beter in het leiden van zijn YouTube-bedrijf. Claude denkt mee. De agents voeren uit. De CEO beslist.`;

/* ---------- kennisbank ---------- */
let kennisP: Promise<Kennis> | null = null;
export function laadKennis(): Promise<Kennis> {
  if (!kennisP) kennisP = fetch('./kennis.json').then((r) => (r.ok ? r.json() : { bronnen: [], fragmenten: [] })).catch(() => ({ bronnen: [], fragmenten: [] }));
  return kennisP;
}
const STOP = new Set('de het een en van in op te is dat je ik wat hoe voor met mijn niet er aan als ook bij of naar zijn maar om dan nog wel kan the a of to and is in for you how what'.split(' '));
const woorden = (t: string) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9]+/).filter((w) => w.length > 2 && !STOP.has(w));
export function zoek(k: Kennis, vraag: string, n = 4): Fragment[] {
  const q = woorden(vraag);
  if (!q.length) return [];
  const scores = k.fragmenten.map((f) => {
    const hay = woorden(`${f.hoofdstuk} ${f.onderwerp} ${f.tekst}`);
    const set = new Map<string, number>(); hay.forEach((w) => set.set(w, (set.get(w) ?? 0) + 1));
    let s = 0;
    for (const w of q) { for (const [h, c] of set) if (h === w) s += 3 + Math.min(c, 4); else if (h.startsWith(w.slice(0, 5)) && w.length > 4) s += 1; }
    if (f.onderwerp && q.some((w) => f.onderwerp.includes(w))) s += 4;
    return { f, s: s * (f.doc.toLowerCase().includes('guide') ? 1.3 : 1) };
  });
  return scores.filter((x) => x.s > 3).sort((a, b) => b.s - a.s).slice(0, n).map((x) => x.f);
}
export const fragmentTekst = (fs: Fragment[]) => fs.length ? fs.map((f, i) => `[${i + 1}] bron: ${f.doc} (${f.taal.toUpperCase()}), ${f.hoofdstuk}\n${f.tekst.slice(0, 900)}`).join('\n\n') : '(geen passende fragmenten gevonden)';

/* ---------- bedrijfsgegevens als tekst ---------- */
export function bedrijf(d: Live, stats: StatRow[], g: Geheugen, doelen: Doel[]): string {
  const v = d.videos.map((x) => `- Video ${x.nr} "${x.title}": ${x.status}; stap nu: ${x.steps.find((s) => s.active)?.label ?? (x.steps.every((s) => s.done) ? 'alles klaar' : '?')}${x.notes?.length ? ` (${x.notes.slice(-2).join('; ').slice(0, 160)})` : ''}`).join('\n');
  const a = d.activity.map((x) => `- [${x.state}] ${x.title}: ${x.doing ?? ''} (laatst ${x.last})`).join('\n');
  const yt = (d.youtube?.videos ?? []).slice(0, 18).map((x) => `- ${x.type === 'long' ? 'LANG' : 'short'} "${x.title}" ${x.datum ?? x.date ?? ''}${x.status ? ' ' + x.status : ''}: ${x.views ?? 0} views`).join('\n');
  const st = stats.length > 1 ? `Abonnees ${stats[0].subscribers} → ${stats[stats.length - 1].subscribers}, weergaven ${stats[0].views} → ${stats[stats.length - 1].views} (meting ${stats[0].at.slice(0, 16)} tot ${stats[stats.length - 1].at.slice(0, 16)}).` : 'Nog geen cijfergeschiedenis.';
  const kosten = (d.costs ?? []).slice(0, 10).map((c) => `- ${c.datum} ${c.wat}: ${c.bedrag != null ? '€' + c.bedrag : c.credits ?? '?'}${c.notitie ? ' (' + c.notitie + ')' : ''}`).join('\n') || '- (geen kosten geregistreerd)';
  const mem = (Object.keys(VAK) as (keyof typeof VAK)[]).map((k) => `${VAK[k]}:\n${(g[k] ?? []).map((x) => '- ' + x).join('\n') || '- (leeg)'}`).join('\n');
  const dl = doelen.length ? doelen.map((x) => `- ${x.klaar ? '[gehaald] ' : ''}${x.tekst}${x.doel ? ` (doel ${x.doel} ${x.meet})` : ''}${x.deadline ? ` vóór ${x.deadline}` : ''}`).join('\n') : '- (nog geen doelen ingesteld)';
  const bl = d.blender ? `Blender op pc: ${d.blender.stand} (bijgewerkt ${d.blender.bijgewerkt})` : '';
  return `=== ECHTE BEDRIJFSGEGEVENS (stand ${d.updated}) ===
KANAAL: Driftmark, ${d.youtube?.subscribers ?? '?'} abonnees, ${d.youtube?.views ?? '?'} weergaven, ${d.youtube?.videoCount ?? '?'} video's. ${st}
Retentie video 1: gem. kijkduur 6:40 (26%), 2/3 weg in eerste minuut. CTR, impressies en RPM zijn NIET beschikbaar in het HQ.
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
  void laadKennis().then((k) => useCoach.setState({ kennis: k }));
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
  const fr = zoek(k, laatste + ' ' + (geschiedenis[geschiedenis.length - 3]?.content ?? ''));
  const cursus = k.bronnen.some((b) => b.soort === 'cursus') ? 'De cursus staat in de kennisbank.' : 'LET OP: de YouTube A-Z Guide (cursus) is nog NIET geüpload; je hebt alleen Driftmark-documenten. Zeg dat als iemand cursusadvies vraagt.';
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
