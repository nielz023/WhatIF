/**
 * CURSUS IN HET HQ: de regels uit het Faceless YouTube Handboek (Faceless Education),
 * toegepast op de echte stand van Driftmark.
 * - CursusMeter      (Kanaal): richtwaarden van de cursus naast je echte cijfers
 * - TitelTester      (Video's): scoort een titel op de titelregels van de cursus
 * - CursusCheck      (Video's): per video de cursuschecklist (script, thumbnail, upload), opgeslagen in de database
 * - CursusStappen    (Werkwijze): het productieproces + upload-checklist van de cursus
 * - cursusTip()      (Home/coach): een tip uit de cursus die past bij de stand
 */
import { useEffect, useState } from 'react';
import { GraduationCap, Check } from 'lucide-react';
import { useLive } from '../services/live';
import { useDb } from '../services/db';

const BRON = 'Cursus: Faceless YouTube Handboek';

function Bar({ pct, color = '#ff8a3d' }: { pct: number; color?: string }) {
  return <div className="h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full" style={{ width: `${Math.max(2, Math.min(100, pct))}%`, background: color }} /></div>;
}
const OORDEEL: Record<string, [string, string]> = { goed: ['goed', 'text-green-300'], oké: ['oké', 'text-sky-300'], werk: ['werk nodig', 'text-orange-300'], onbekend: ['nog onbekend', 'text-slate-400'] };

/* ---------- Kanaal: cursusmeter ---------- */
export function CursusMeter() {
  const yt = useLive((s) => s.data.youtube);
  const stats = useDb((s) => s.stats);
  const vids = (yt?.videos ?? []).filter((v) => (v.status ?? 'public') === 'public');
  const longs = vids.filter((v) => v.type === 'long');
  const subs = yt?.subscribers ?? 0;
  const views = yt?.views ?? 0;
  const perSub = subs ? Math.round(views / subs) : 0;
  const best = [...vids].sort((a, b) => (b.views ?? 0) - (a.views ?? 0))[0];
  const bestLong = [...longs].sort((a, b) => (b.views ?? 0) - (a.views ?? 0))[0];
  const rows: { naam: string; doel: string; nu: string; oordeel: keyof typeof OORDEEL; tip: string; pct?: number }[] = [
    { naam: 'Gemiddeld bekeken (AVD)', doel: '40%+ goed, 50%+ geweldig', nu: 'Video 1: 26% (6:40)', oordeel: 'werk', tip: 'Onder 30% = het script moet beter. Bij video 1 zat het lek in de eerste minuut.', pct: 26 / 50 * 100 },
    { naam: 'Abonnees per kijker', doel: '1 per 100-200 weergaven', nu: perSub ? `1 per ${perSub.toLocaleString('nl-NL')}` : '?', oordeel: perSub && perSub <= 200 ? 'goed' : perSub && perSub <= 300 ? 'oké' : 'werk', tip: 'Vraag rond 60% van de video om te abonneren, plus een korte outro met één oproep en een eindscherm.', pct: perSub ? (150 / perSub) * 100 : 0 },
    { naam: 'Een 1K-video in de eerste 5-10', doel: 'minstens één', nu: best ? `${best.type === 'short' ? 'Short' : 'Lang'}: ${(best.views ?? 0).toLocaleString('nl-NL')} (${best.title.slice(0, 32)}…)` : '?', oordeel: (bestLong?.views ?? 0) >= 1000 ? 'goed' : (best?.views ?? 0) >= 1000 ? 'oké' : 'werk', tip: 'Haalt een video 1K+, maak dan 3-5 video\'s over dat onderwerp vanuit een andere hoek. Je beste short gaat over teleporteren.', pct: Math.min(100, ((bestLong?.views ?? 0) / 1000) * 100) },
    { naam: 'Videolengte', doel: '10-15 min', nu: 'Video 2: 12:56 · video 4: ~12 min', oordeel: 'goed', tip: 'Minstens zo lang als de concurrent, maar 10 min met 70% is beter dan 20 min met 30%.', pct: 100 },
    { naam: 'YouTube Partner Programma', doel: '1.000 abonnees + 4.000 kijkuren', nu: `${subs} abonnees · kijkuren onbekend`, oordeel: 'onbekend', tip: 'Shorts-weergaven tellen niet mee voor de 4.000 kijkuren: lange video\'s wel. Maak alvast een AdSense-account aan.', pct: (subs / 1000) * 100 },
    { naam: 'CTR (klikken ÷ vertoningen)', doel: '5%+ (evergreen), 10%+ geweldig', nu: 'niet zichtbaar in het HQ', oordeel: 'onbekend', tip: 'Kijk 48 uur na een upload in Studio. Lage CTR en weinig uit Aanbevolen? Vervang de thumbnail.' },
    { naam: 'Testfase', doel: '5 video\'s, dan beslissen', nu: `${longs.length} van 5 lange video's online`, oordeel: longs.length >= 5 ? 'goed' : 'oké', tip: 'Na 5 video\'s: goed = 3-5 nieuwe in die richting; matig = eerst CTR en AVD omhoog; slecht = niche, thumbnail, hook en doelgroep herzien.', pct: (longs.length / 5) * 100 },
  ];
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-1 flex items-center gap-2 font-display text-[18px] font-bold text-white"><GraduationCap size={18} className="text-orange-300" />Cursusmeter</div>
      <div className="mb-3 text-[13px] text-slate-400">De richtwaarden uit je cursus naast je echte cijfers{stats.length ? '' : ''}. Alleen wat er staat is gemeten; de rest zie jij in YouTube Studio.</div>
      <div className="grid gap-2 md:grid-cols-2">
        {rows.map((r) => (
          <div key={r.naam} className="rounded-xl bg-white/[.04] p-3">
            <div className="flex items-baseline justify-between gap-2"><span className="font-semibold text-white">{r.naam}</span><span className={`shrink-0 text-[13px] font-bold ${OORDEEL[r.oordeel][1]}`}>{OORDEEL[r.oordeel][0]}</span></div>
            <div className="text-[13px] text-slate-300">Nu: {r.nu} · doel: {r.doel}</div>
            {r.pct != null && <div className="mt-1.5"><Bar pct={r.pct} color={r.oordeel === 'goed' ? '#3ddc97' : r.oordeel === 'werk' ? '#ff8a3d' : '#3db8ff'} /></div>}
            <div className="mt-1.5 text-[13px] text-slate-400">💡 {r.tip}</div>
          </div>
        ))}
      </div>
      <div className="mt-2 text-[12px] text-slate-500">{BRON}, hoofdstuk 3, 9 en 10.</div>
    </section>
  );
}

/* ---------- Video's: titeltester ---------- */
const KERN = ['what if', 'how', 'why', 'actually', 'really', 'explained', 'paradox', 'every day', 'forever', 'never', 'only', 'last'];
export function scoreTitel(t: string) {
  const s = t.trim();
  const woorden = s.split(/\s+/).filter(Boolean);
  const klein = woorden.filter((w) => /^[a-z]/.test(w) && !['a', 'an', 'the', 'of', 'to', 'in', 'on', 'for', 'and', 'or', 'at', 'by'].includes(w));
  const checks = [
    { ok: s.length > 0 && s.length <= 100, tekst: `Max 100 tekens (nu ${s.length})` },
    { ok: s.length >= 25 && s.length <= 70, tekst: 'Kort genoeg om op mobiel helemaal te lezen (25-70 tekens)' },
    { ok: /^what if/i.test(s), tekst: 'Begint met "What If" (titelstructuur voor animatie)' },
    { ok: /\d/.test(s), tekst: 'Bevat een getal (10x, Day 1, 1,000…)' },
    { ok: klein.length === 0, tekst: klein.length ? `Elk woord met hoofdletter (mist: ${klein.slice(0, 4).join(', ')})` : 'Elk woord met hoofdletter' },
    { ok: /\b[A-Z]{3,}\b/.test(s.replace(/^WHAT IF/i, '')), tekst: 'Eén woord in HOOFDLETTERS voor de lading (STRONGER, NO RULES)' },
    { ok: KERN.some((k) => s.toLowerCase().includes(k)), tekst: 'Kernwoord uit de cursus (What If, How, Why, Actually, Really…)' },
    { ok: /\?$|\)$/.test(s), tekst: 'Eindigt als vraag of met een duidelijke afsluiting' },
  ];
  const score = Math.round((checks.filter((c) => c.ok).length / checks.length) * 100);
  return { score, checks };
}
export function TitelTester() {
  const vids = useLive((s) => s.data.videos);
  const [t, setT] = useState(() => vids.find((v) => v.status !== 'Online')?.title ?? '');
  const r = scoreTitel(t);
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-1 flex items-center gap-2 font-display text-[18px] font-bold text-white"><GraduationCap size={18} className="text-orange-300" />Titeltester</div>
      <div className="mb-2 text-[13px] text-slate-400">Typ een titel. Hij wordt gescoord op de titelregels uit je cursus (hoofdstuk 5). Een hoge score is geen garantie, de inhoud moet de titel waarmaken.</div>
      <input className="input w-full text-[15px]" value={t} onChange={(e) => setT(e.target.value)} placeholder="What IF You Could Never Die?" aria-label="Titel" />
      <div className="mt-3 flex items-center gap-3"><div className="font-display text-3xl font-bold" style={{ color: r.score >= 75 ? '#3ddc97' : r.score >= 50 ? '#3db8ff' : '#ff8a3d' }}>{r.score}</div><div className="flex-1"><Bar pct={r.score} color={r.score >= 75 ? '#3ddc97' : r.score >= 50 ? '#3db8ff' : '#ff8a3d'} /></div></div>
      <div className="mt-2 grid gap-1 sm:grid-cols-2">{r.checks.map((c) => <div key={c.tekst} className={`text-[13px] ${c.ok ? 'text-green-300' : 'text-slate-400'}`}>{c.ok ? '✓' : '○'} {c.tekst}</div>)}</div>
      <div className="mt-2 flex flex-wrap gap-1.5 text-[12px]">{vids.map((v) => <button key={v.nr} onClick={() => setT(v.title)} className="rounded-full bg-white/5 px-2.5 py-1 text-slate-300 hover:bg-white/10">Video {v.nr}</button>)}</div>
    </section>
  );
}

/* ---------- Video's: cursuscheck per video ---------- */
export const CHECK: { fase: string; items: { id: string; tekst: string }[] }[] = [
  { fase: 'Idee', items: [
    { id: 'idee-bewijs', tekst: 'Onderwerp heeft bewijs: lijkt op een outlier (bij ons of IFOLOGY) of op je beste short' },
    { id: 'idee-comments', tekst: 'Comments van top 3-video\'s gelezen: wat vragen kijkers?' },
  ] },
  { fase: 'Script', items: [
    { id: 'hook-titel', tekst: 'De titel komt in andere woorden terug in de eerste zin' },
    { id: 'hook-10s', tekst: 'Binnen 10 s weet de kijker wat hij krijgt; geen opwarming' },
    { id: 'hook-reden', tekst: 'Reden om te blijven: belofte, vraag of cliffhanger' },
    { id: 'script-minuut', tekst: 'Elke minuut een voorproefje of nieuw probleem (pattern breaks)' },
    { id: 'script-abo', tekst: 'Abonneeroproep rond 60% van de video' },
    { id: 'script-outro', tekst: 'Outro max 20 woorden, één abonneeroproep' },
    { id: 'script-feiten', tekst: 'Elke "This part is real" met 2 betrouwbare bronnen gecheckt' },
    { id: 'script-hardop', tekst: 'Klinkt natuurlijk hardop: korte zinnen, geen jargon' },
  ] },
  { fase: 'Thumbnail', items: [
    { id: 'thumb-3', tekst: 'Max 3 elementen: gezicht met emotie, tekst, beeld' },
    { id: 'thumb-contrast', tekst: 'Fel en veel contrast, valt op in donkere modus' },
    { id: 'thumb-mobiel', tekst: 'Tekst groot en leesbaar op mobiel' },
    { id: 'thumb-spanning', tekst: 'Spanning tussen titel en thumbnail' },
    { id: 'thumb-tech', tekst: '1280×720, max 2 MB' },
  ] },
  { fase: 'Upload', items: [
    { id: 'up-titel', tekst: 'Titel max 100 tekens, elk woord hoofdletter, trefwoord erin' },
    { id: 'up-beschr', tekst: 'Eerste 157 tekens van de beschrijving: onderwerp + trefwoord' },
    { id: 'up-tijd', tekst: 'Tijdstempels (hoofdstukken) in de beschrijving' },
    { id: 'up-hashtags', tekst: 'Max 3 hashtags = je eerste 3 tags' },
    { id: 'up-links', tekst: 'Links naar je andere video\'s (sessietijd)' },
    { id: 'up-reactie', tekst: 'Vastgezette reactie met een vraag of link' },
    { id: 'up-eind', tekst: 'Eindscherm en kaarten naar de volgende video' },
    { id: 'up-test', tekst: '"Test & compare" met 3 thumbnails aan' },
    { id: 'up-ai', tekst: 'AI-label alleen als er AI-muziek of realistische AI-beelden in zitten' },
    { id: 'up-plan', tekst: 'Ingepland binnen 24 uur (snellere advertentiecheck)' },
  ] },
  { fase: 'Na 48 uur', items: [
    { id: 'na-ctr', tekst: 'CTR bekeken (doel 5%+); laag en weinig Aanbevolen → thumbnail vervangen' },
    { id: 'na-avd', tekst: 'AVD bekeken (doel 40%+); waar haken kijkers af?' },
    { id: 'na-bron', tekst: 'Verkeersbronnen bekeken (Browse/Aanbevolen = YouTube pusht je)' },
    { id: 'na-reageer', tekst: 'Op elke comment gereageerd' },
  ] },
];
const TOTAAL = CHECK.reduce((a, f) => a + f.items.length, 0);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let dbP: Promise<any> | null = null;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getDb = () => (dbP ??= (async () => { try { const c = (window as any).claude; return c?.use ? await c.use('db') : null; } catch { return null; } })());

export function CursusCheck() {
  const vids = useLive((s) => s.data.videos);
  const [nr, setNr] = useState(() => vids.find((v) => v.status !== 'Online')?.nr ?? vids[vids.length - 1]?.nr ?? 1);
  const [vink, setVink] = useState<Record<string, boolean>>({});
  const [opgeslagen, setOpgeslagen] = useState<boolean | null>(null);
  useEffect(() => {
    let uit: (() => void) | undefined; let on = true;
    const key = `cursus-check-${nr}`;
    try { setVink(JSON.parse(localStorage.getItem(key) || '{}')); } catch { setVink({}); }
    void getDb().then((db) => {
      if (!db || !on) { setOpgeslagen(false); return; }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      uit = db.doc(`check/video${nr}`).onSnapshot((d: any) => { if (d.exists) setVink(d.data().vink ?? {}); setOpgeslagen(true); }, () => setOpgeslagen(false));
    });
    return () => { on = false; uit?.(); };
  }, [nr]);
  const zet = (id: string) => {
    const nieuw = { ...vink, [id]: !vink[id] };
    setVink(nieuw);
    try { localStorage.setItem(`cursus-check-${nr}`, JSON.stringify(nieuw)); } catch { /* */ }
    void getDb().then((db) => db?.doc(`check/video${nr}`).set({ vink: nieuw, at: new Date().toISOString() }).catch(() => setOpgeslagen(false)));
  };
  const gedaan = Object.values(vink).filter(Boolean).length;
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-1 flex flex-wrap items-center gap-2 font-display text-[18px] font-bold text-white"><GraduationCap size={18} className="text-orange-300" />Cursuscheck
        <span className="ml-auto flex gap-1.5">{vids.map((v) => <button key={v.nr} onClick={() => setNr(v.nr)} className={`rounded-full px-3 py-1 text-[13px] font-semibold ${nr === v.nr ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300'}`}>Video {v.nr}</button>)}</span>
      </div>
      <div className="mb-2 text-[13px] text-slate-400">Alles wat de cursus vraagt, van idee tot 48 uur na de upload. Claude vinkt aan wat hij doet; jij vinkt de upload-stappen aan. {opgeslagen ? 'Opgeslagen in de database.' : opgeslagen === false ? 'Alleen in deze browser bewaard.' : ''}</div>
      <div className="mb-3 flex items-center gap-3"><div className="flex-1"><Bar pct={(gedaan / TOTAAL) * 100} color="#3ddc97" /></div><span className="shrink-0 text-[13px] text-slate-300">{gedaan}/{TOTAAL}</span></div>
      <div className="grid gap-3 md:grid-cols-2">
        {CHECK.map((f) => (
          <div key={f.fase}>
            <div className="mb-1 text-[12px] font-bold uppercase tracking-wider text-orange-300">{f.fase}</div>
            {f.items.map((i) => (
              <button key={i.id} onClick={() => zet(i.id)} className="flex w-full items-start gap-2 rounded-lg px-1.5 py-1 text-left text-[14px] hover:bg-white/5">
                <span className={`mt-0.5 flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded border ${vink[i.id] ? 'border-green-400 bg-green-500/30 text-green-200' : 'border-slate-500'}`}>{vink[i.id] && <Check size={13} />}</span>
                <span className={vink[i.id] ? 'text-slate-400 line-through' : 'text-slate-200'}>{i.tekst}</span>
              </button>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ---------- Werkwijze: cursusstappen ---------- */
export function CursusStappen() {
  const STAP = [
    ['Nicheonderzoek', 'Kanalen jonger dan 6 maanden met 100K+-video\'s en <50K abonnees = ruimte. Bij ons: IFOLOGY en What IF-animatie.'],
    ['Niche en strategie', 'Format animatie/AI storytelling: origineel, geen claimrisico, hoge retentie. Wekelijks één lange video + shorts.'],
    ['Onderwerp', 'Bouw uit op wat al 1K+ haalde (teleport, tijd/snelheid, lichaam verandert). Lees comments: "maak ook X" is goud.'],
    ['Script', '10-15 min (~150 woorden per minuut). Titel in de eerste zin, binnen 10 s duidelijk, elke minuut een voorproefje, abonneeroproep rond 60%, outro max 20 woorden, 2 bronnen per feit.'],
    ['Voice-over', 'Toon van de niche: verhalend, mysterieus, jeugdig. Onze vaste ElevenLabs-stem.'],
    ['Video editen', 'In Blender (en UE5). Shots 3-4 s, stem centraal, -14 LUFS.'],
    ['Thumbnail', 'Max 3 elementen, fel, contrast, gezicht met emotie, spanning met de titel, 1280×720. Altijd 3 varianten om te testen.'],
    ['Uploaden', 'Beschrijving (157 tekens boven de vouw, tijdstempels, links, 3 hashtags), vastgezette reactie, eindscherm, binnen 24 uur inplannen. Dit doet niels zelf.'],
  ];
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-1 flex items-center gap-2 font-display text-[18px] font-bold text-white"><GraduationCap size={18} className="text-orange-300" />De 8 stappen uit je cursus, voor Driftmark</div>
      <div className="grid gap-2 md:grid-cols-2">{STAP.map(([t, x], i) => (
        <div key={t} className="flex gap-3 rounded-xl bg-white/[.03] p-3"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-orange-500/30 text-sm font-bold text-white">{i + 1}</span><div><div className="text-[14px] font-semibold text-white">{t}</div><div className="text-[13px] text-slate-400">{x}</div></div></div>
      ))}</div>
      <div className="mt-3 rounded-xl border border-orange-400/30 bg-orange-500/5 p-3 text-[13px] text-slate-300"><b className="text-orange-200">De vriendentest:</b> zou je deze video trots laten zien aan vrienden, familie of een kritische buitenstaander? Nee? Dan niet uploaden. · <b className="text-orange-200">Mindset:</b> goed genoeg → publiceer → analyseer → verbeter. Groei is niet lineair; denk in 6-12 maanden.</div>
      <div className="mt-2 text-[12px] text-slate-500">{BRON}, hoofdstuk 2-8.</div>
    </section>
  );
}

/* ---------- Home: een cursustip die past bij de stand ---------- */
const TIPS = [
  'Vraag rond 60% van je video om te abonneren, niet alleen aan het eind.',
  'Herhaal de titel in andere woorden in je eerste zin.',
  'Een thumbnail met max 3 elementen: gezicht met emotie, tekst, beeld.',
  'Kijk 48 uur na een upload naar CTR (doel 5%+) en AVD (doel 40%+).',
  'Link je andere video\'s in de beschrijving: dat verhoogt de sessietijd.',
  'Haalde een video 1K+? Maak er 3-5 over hetzelfde onderwerp vanuit een andere hoek.',
  'Goed genoeg → publiceer → analyseer → verbeter. Niet te lang perfectioneren.',
  'Maak nu al een AdSense-account aan, dan ben je klaar als je in het YPP komt.',
  'Elk feit in je script met 2 betrouwbare bronnen checken.',
  'Max 3 hashtags in de beschrijving, en maak die ook je eerste 3 tags.',
];
export function CursusTip() {
  const [i] = useState(() => Math.floor((Date.now() / 864e5)) % TIPS.length);
  return (
    <div className="flex items-start gap-3 rounded-2xl border border-orange-400/30 bg-orange-500/[.06] p-3">
      <GraduationCap size={20} className="mt-0.5 shrink-0 text-orange-300" />
      <div><div className="text-[12px] font-bold uppercase tracking-wider text-orange-300">Cursustip van vandaag</div><div className="text-[14px] text-slate-100">{TIPS[i]}</div></div>
    </div>
  );
}
