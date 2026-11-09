/**
 * Nieuw gereedschap per afdeling (verbeterlijst stap 6):
 * Onderzoek: onderwerpenbord met scores en "naar volgende video" (51), nieuwste uploads van concurrenten (45).
 * Creatief: titellab, titel naast de thumbnail zoals op YouTube, pc en telefoon, met de cursusregels (52).
 * Productie: scènebord met stills, status en de kwaliteitscheck van niels per scène (56 en 47).
 * Publicatie: Uploaddag en shortsplanning (57).  CEO: lessen van de maand (58).
 * Alles is echte data of zegt eerlijk dat het er (nog) niet is; elke knop is een echte opdracht voor Claude.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { ArrowRight, Clapperboard, Lightbulb, ListChecks, Send, Users, Wand2 } from 'lucide-react';
import { useLive, filesApi } from '../services/live';
import { order } from '../services/real';
import { laadBeeld } from '../services/kennis';
import { useGame } from '../store/useGame';
import { scoreTitel } from '../pages/Cursus';
import { openBestand } from '../components/shared/BestandViewer';
import { KLEUR } from '../lib/status';
import { useDoc, Sec, Leeg, nl, type Onderwerp } from './deptTools';

/* =================== ONDERZOEK: onderwerpenbord met scores (punt 51) =================== */
interface BordOnderwerp extends Onderwerp { niche?: number; zoekvolume?: number | string; ifology?: number }
const scoreKleur = (n?: number) => (n == null ? KLEUR.stil : n >= 7 ? KLEUR.klaar : n >= 5 ? KLEUR.bezig : KLEUR.wacht);
function Score({ label, v, uitleg }: { label: string; v?: number | string; uitleg: string }) {
  const n = typeof v === 'number' ? v : undefined;
  return (
    <span title={uitleg} className="inline-flex items-center gap-1 rounded-md bg-white/[.05] px-1.5 py-0.5 text-[10.5px]">
      <span className="text-slate-400">{label}</span>
      <b style={{ color: v == null ? KLEUR.stil : n != null ? scoreKleur(n) : '#e2e8f0' }}>{v == null ? 'nog niet' : n != null ? `${n}/10` : v}</b>
    </span>
  );
}
export function OnderwerpenBord() {
  const [doc, , st] = useDoc<{ at?: string; conclusie?: string; top?: BordOnderwerp[]; volgorde?: string }>('bord/onderwerpen');
  const ideas = useLive((s) => s.data.ideas);
  const toast = useGame((s) => s.toast);
  const [alles, setAlles] = useState(false);
  // de lijst van het team (database); anders de ideeënlijst uit status.json, zonder scores
  const lijst: BordOnderwerp[] = doc?.top?.length ? doc.top : ideas.slice(0, 12).map((x, i) => ({ nr: i + 1, titel: x.title.replace(/^\d+\.\s*/, '') }));
  const gescoord = lijst.some((o) => o.niche != null || o.ifology != null || o.zoekvolume != null);
  const naarVolgende = (o: BordOnderwerp) => order(`Zet het onderwerp "${o.titel}" klaar als volgende video: maak er een verloop van (escalatie en twist) en zet het in de planning na de video die nu in productie is.`, toast, { doel: 'Onderzoek' });
  return (
    <Sec title="Onderwerpenbord" icon={<Lightbulb size={13} />} color="#20D9FF" right={doc?.at && <span className="text-[11px] text-slate-500">{new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}</span>}>
      {!lijst.length ? <Leeg>{st === 'laden' ? 'Laden…' : 'Nog geen onderwerpen. Het team zoekt onderwerpen die passen bij de niche.'}</Leeg> : (
        <div className="space-y-1">
          {doc?.conclusie && <div className="mb-1 rounded-lg bg-[#20D9FF]/10 px-2 py-1.5 text-[12px] leading-snug text-cyan-100">💡 {doc.conclusie}</div>}
          {(alles ? lijst : lijst.slice(0, 6)).map((o) => (
            <div key={o.nr + o.titel} className="rounded-lg border border-white/[.06] bg-white/[.02] px-2 py-1.5 text-[12px]">
              <div className="flex items-start gap-2">
                <span className="mt-px w-5 shrink-0 font-bold text-[#20D9FF]">{o.nr}.</span>
                <span className="min-w-0 flex-1 font-semibold text-white">{o.titel}</span>
                <button onClick={() => naarVolgende(o)} className="shrink-0 rounded-md px-1.5 py-0.5 text-[10.5px] font-bold text-white hover:brightness-125" style={{ background: `${KLEUR.bezig}44` }} title="Wordt een echte opdracht voor Claude">Naar volgende video</button>
              </div>
              <div className="mt-1 flex flex-wrap gap-1 pl-7">
                <Score label="Niche" v={o.niche} uitleg="Hoe goed het past bij What If-video's met 3D-animatie" />
                <Score label="Zoekvolume" v={o.zoekvolume} uitleg="Hoe vaak erop gezocht wordt (uit vidIQ of NexLev, als het bekend is)" />
                <Score label="IFOLOGY" v={o.ifology} uitleg="Hoe goed zulke onderwerpen het doen bij IFOLOGY" />
                {o.maak && <span className="rounded-md bg-white/[.05] px-1.5 py-0.5 text-[10.5px] text-slate-300" title="Hoeveel werk in Blender">{o.maak}</span>}
              </div>
              {(o.waarom || o.twist) && <div className="mt-0.5 pl-7 leading-snug text-slate-400">{o.waarom}{o.twist ? ` Twist: ${o.twist}` : ''}</div>}
            </div>
          ))}
          {lijst.length > 6 && <button onClick={() => setAlles(!alles)} className="text-[12px] font-semibold text-[#20D9FF] hover:underline">{alles ? 'Minder tonen' : `Alle ${lijst.length} tonen`}</button>}
          {!gescoord && (
            <div className="mt-1 rounded-lg bg-white/[.04] px-2 py-1.5 text-[11.5px] leading-snug text-slate-300">
              Er zijn nog geen scores bekend, dus ik toon er geen.{' '}
              <button className="font-semibold text-[#20D9FF] hover:underline" onClick={() => order('Geef elk onderwerp op het onderwerpenbord (database bord/onderwerpen) een score van 1 tot 10 voor niche-fit en IFOLOGY-fit, en het zoekvolume uit vidIQ of NexLev als dat bekend is. Zet ze in de velden niche, ifology en zoekvolume.', toast, { doel: 'Onderzoek' })}>Laat Claude ze scoren</button>
            </div>
          )}
          {doc?.volgorde && <div className="mt-1 rounded-lg bg-white/[.04] px-2 py-1.5 text-[12px] leading-snug text-slate-200">🎬 {doc.volgorde}</div>}
        </div>
      )}
    </Sec>
  );
}

/* =================== ONDERZOEK: nieuwste uploads van concurrenten (punt 45) =================== */
interface Upload { kanaal: string; titel: string; url?: string; datum?: string; views?: number }
export function ConcurrentUploads() {
  const [doc, , st] = useDoc<{ at?: string; uploads?: Upload[] }>('concurrenten/uploads');
  const toast = useGame((s) => s.toast);
  const ups = doc?.uploads ?? [];
  const haal = () => order('Haal de nieuwste uploads van IFOLOGY en vergelijkbare What If-kanalen op (titel, datum, weergaven, link) via vidIQ of NexLev, en zet ze in de database onder concurrenten/uploads als { at, uploads: [{ kanaal, titel, url, datum, views }] }. Niet scrapen.', toast, { doel: 'Onderzoek' });
  return (
    <Sec title="Nieuwste uploads van concurrenten" icon={<Users size={13} />} color="#20D9FF" right={doc?.at && <span className="text-[11px] text-slate-500">{new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}</span>}>
      {ups.length ? (
        <div className="space-y-1">
          {ups.slice(0, 8).map((u, i) => (
            <a key={i} href={u.url} target="_blank" rel="noreferrer" className="block rounded-lg px-1.5 py-1 text-[12px] hover:bg-white/5">
              <div className="truncate font-semibold text-white">{u.titel}</div>
              <div className="text-[11px] text-slate-400">{u.kanaal}{u.datum ? ` · ${u.datum}` : ''}{u.views != null ? ` · ${nl(u.views)} weergaven` : ''}</div>
            </a>
          ))}
        </div>
      ) : <Leeg>{st === 'laden' ? 'Laden…' : 'De HQ kan YouTube zelf niet lezen. Claude haalt de nieuwste uploads op met vidIQ of NexLev en zet ze hier neer.'}</Leeg>}
      <button onClick={haal} className="mt-2 inline-flex items-center gap-1 rounded-lg bg-[#20D9FF]/20 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#20D9FF]/35"><Send size={12} />Haal de nieuwste uploads van IFOLOGY op</button>
    </Sec>
  );
}

/* =================== CREATIEF: titellab (punt 52) =================== */
/** een beeld uit de projectbestanden (of ./ uit de pagina zelf) als object-URL */
function useBeeld(path?: string) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!path) { setUrl(null); return; }
    if (path.startsWith('./')) { setUrl(path); return; }
    let on = true; let u: string | null = null;
    laadBeeld(path, 'image/jpeg').then((x) => { u = x; if (on) setUrl(x); else URL.revokeObjectURL(x); }).catch(() => { if (on) setUrl(null); });
    return () => { on = false; if (u) URL.revokeObjectURL(u); };
  }, [path]);
  return url;
}
export function TitelLab() {
  const L = useLive((s) => s.data);
  const toast = useGame((s) => s.toast);
  const bezig = useMemo(() => L.videos.filter((v) => v.status !== 'Online').sort((a, b) => a.nr - b.nr), [L.videos]);
  // thumbnails: die van een video in productie (projectbestand), anders je nieuwste online video's
  const thumbs = useMemo(() => {
    const out: { label: string; path: string }[] = [];
    for (const v of bezig) for (const o of L.outputs?.[String(v.nr)] ?? []) if (o.kind === 'image' && /thumb/i.test(o.path)) out.push({ label: `Video ${v.nr}`, path: o.path });
    for (const y of (L.youtube?.videos ?? []).filter((x) => x.type === 'long' && x.id).sort((a, b) => (b.datum ?? '').localeCompare(a.datum ?? '')).slice(0, 2)) out.push({ label: `Online: ${y.title.slice(0, 18)}…`, path: `./thumbs/${y.id}.jpg` });
    return out;
  }, [L.outputs, L.youtube, bezig]);
  const [ti, setTi] = useState(0);
  const [titel, setTitel] = useState(() => bezig[bezig.length - 1]?.title ?? '');
  const img = useBeeld(thumbs[ti]?.path);
  const r = scoreTitel(titel);
  const kanaal = L.channel?.name ?? 'Driftmark';
  const doelVideo = bezig[bezig.length - 1];
  const Thumb = ({ w }: { w: string }) => (
    <div className={`relative aspect-video shrink-0 overflow-hidden rounded-lg bg-gradient-to-br from-[#1b2660] to-[#3a1d4f] ${w}`}>
      {img ? <img src={img} alt="" className="h-full w-full object-cover" /> : <span className="absolute inset-0 flex items-center justify-center text-[10px] text-slate-400">geen thumbnail</span>}
    </div>
  );
  const kleur = r.score >= 75 ? KLEUR.klaar : r.score >= 50 ? KLEUR.bezig : KLEUR.wacht;
  return (
    <Sec title="Titellab" icon={<Wand2 size={13} />} color="#A855F7" right={<span className="text-[12px] font-bold" style={{ color: kleur }}>{r.score}/100</span>}>
      <input value={titel} onChange={(e) => setTitel(e.target.value)} placeholder="What IF You Could Never Die?" aria-label="Titel"
        className="mb-2 w-full rounded-lg border border-white/10 bg-black/30 px-2 py-1.5 text-[12.5px] text-white placeholder:text-slate-500 focus:border-white/30 focus:outline-none" />
      <div className="mb-2 flex flex-wrap gap-1">
        {bezig.map((v) => <button key={v.nr} onClick={() => setTitel(v.title)} className="rounded-full bg-white/5 px-2 py-0.5 text-[10.5px] text-slate-300 hover:bg-white/10">Titel video {v.nr}</button>)}
        {thumbs.length > 1 && thumbs.map((t, i) => <button key={t.path} onClick={() => setTi(i)} className={`rounded-full px-2 py-0.5 text-[10.5px] font-semibold ${ti === i ? 'bg-[#A855F7]/40 text-white' : 'bg-white/5 text-slate-300'}`}>{t.label}</button>)}
      </div>
      <div className="grid gap-2 sm:grid-cols-[1.4fr_1fr]">
        <div>
          <div className="mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">Pc</div>
          <div className="rounded-lg bg-[#0f0f0f] p-2">
            <Thumb w="w-full" />
            <div className="mt-1.5 flex gap-2"><span className="h-6 w-6 shrink-0 rounded-full bg-gradient-to-br from-orange-400 to-sky-500" />
              <div className="min-w-0"><div className="line-clamp-2 text-[12.5px] font-semibold leading-tight text-[#f1f1f1]">{titel || 'Titel'}</div><div className="mt-0.5 text-[10.5px] text-[#aaa]">{kanaal}</div></div></div>
          </div>
        </div>
        <div>
          <div className="mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">Telefoon</div>
          <div className="rounded-lg bg-[#0f0f0f] p-1.5">
            <div className="flex gap-1.5"><Thumb w="w-[55%]" /><div className="min-w-0 flex-1"><div className="line-clamp-3 text-[10.5px] font-medium leading-tight text-[#f1f1f1]">{titel || 'Titel'}</div><div className="mt-0.5 text-[9px] text-[#aaa]">{kanaal}</div></div></div>
          </div>
          <div className="mt-1 text-[10.5px] leading-snug text-slate-500">{titel.length} tekens; op een telefoon valt na ongeveer 70 tekens de rest weg.</div>
        </div>
      </div>
      <div className="mt-2 space-y-0.5">
        {r.checks.map((c) => <div key={c.tekst} className="flex gap-1.5 text-[11.5px]"><span style={{ color: c.ok ? KLEUR.klaar : KLEUR.probleem }}>{c.ok ? '✓' : '✗'}</span><span className="text-slate-300">{c.tekst}</span></div>)}
      </div>
      <div className="mt-1 text-[10.5px] text-slate-500">De regels komen uit je cursus (titelhoofdstuk). Een hoge score is geen garantie.</div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        <button onClick={() => order(`Maak 5 titels voor video ${doelVideo?.nr ?? 'in productie'} volgens de titelregels uit de cursus (begint met What If, een getal, elk woord met hoofdletter, 25-70 tekens). Mijn huidige idee: "${titel}".`, toast, { doel: 'Creatief' })} className="inline-flex items-center gap-1 rounded-lg bg-[#A855F7]/25 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#A855F7]/40"><Send size={12} />Laat Claude 5 titels maken</button>
        {doelVideo && titel.trim() && titel !== doelVideo.title && <button onClick={() => order(`Gebruik voor video ${doelVideo.nr} de titel "${titel.trim()}" (titellab-score ${r.score}/100) en zet hem in de uploadtekst.`, toast, { doel: 'Creatief' })} className="rounded-lg bg-white/5 px-2.5 py-1 text-[12px] font-semibold text-slate-200 hover:bg-white/10">Deze titel gebruiken</button>}
      </div>
    </Sec>
  );
}

/* =================== PRODUCTIE: scènebord met kwaliteitscheck (punten 56 en 47) =================== */
/** de vaste kwaliteitscheck van niels, per scène */
export const QC: [string, string][] = [
  ['tekst', 'Tekst strak'], ['teller', 'Teller weg bij flashbacks'], ['props', 'Props niet in elkaar of zwevend'], ['sets', 'Sets dicht'],
  ['clipping', 'Geen clipping'], ['bestek', 'Bestek correct'], ['rennen', 'Rennen met gebogen knieën'], ['armen', 'Geen uitgerekte armen'], ['uitloop', 'Scène loopt 0,6 s door'],
];
/** wat status.json per scène mag meegeven (blender.scenes of scenes) */
interface SceneData { id: string; video?: number; gebouwd?: boolean; gecontroleerd?: boolean; gerenderd?: boolean; fouten?: string[]; qc?: Record<string, boolean>; preview?: string }
interface Kaart { id: string; still?: string; preview?: string; fouten: string[]; data?: SceneData }
const sceneId = (name: string) => name.replace(/\.[a-z]+$/i, '').replace(/^d/i, '').toLowerCase();
const sceneSort = (a: string, b: string) => (parseInt(a, 10) - parseInt(b, 10)) || a.localeCompare(b);
/** stills (stillscheck/), previews (preview/) en het rapport van de stills-check uit de map van de video */
function useSceneBoard(folder?: string) {
  const [st, setSt] = useState<{ fase: 'laden' | 'ok' | 'geen' | 'leeg'; kaarten: Kaart[]; rapport?: string }>({ fase: 'laden', kaarten: [] });
  useEffect(() => {
    if (!folder) { setSt({ fase: 'leeg', kaarten: [] }); return; }
    let on = true;
    (async () => {
      const fs = await filesApi(); if (!fs) { if (on) setSt({ fase: 'geen', kaarten: [] }); return; }
      const lijst = async (p: string) => { try { const r = await fs.list({ path: p }); return ((r?.entries ?? []) as { path: string; isDirectory: boolean }[]).filter((e) => !e.isDirectory); } catch { return []; } };
      const base = folder.replace(/\/?$/, '/');
      const [stills, previews] = await Promise.all([lijst(base + 'stillscheck/'), lijst(base + 'preview/')]);
      const per = new Map<string, Kaart>();
      const kaart = (id: string) => { let k = per.get(id); if (!k) { k = { id, fouten: [] }; per.set(id, k); } return k; };
      for (const e of stills) { const n = e.path.split('/').pop() ?? ''; if (/^d\d/i.test(n) && /\.(jpe?g|png|webp)$/i.test(n)) kaart(sceneId(n)).still = e.path; }
      for (const e of previews) { const n = e.path.split('/').pop() ?? ''; const m = /scene_?(\d+[a-z]?\d?)/i.exec(n); if (m && /\.(jpe?g|png|webp)$/i.test(n)) kaart(m[1].toLowerCase()).preview = e.path; }
      // fouten uit het rapport van de stills-check (tabel | Scène | Fout | Oplossing |)
      let rapport: string | undefined;
      const rp = stills.find((e) => /rapport\.md$/i.test(e.path));
      if (rp) {
        rapport = rp.path;
        try {
          const txt = new TextDecoder().decode((await fs.read(rp.path)).bytes);
          for (const regel of txt.split('\n')) {
            const c = regel.split('|').map((x) => x.trim());
            if (c.length < 5 || !c[1] || /^-+$/.test(c[1]) || /^sc[eè]ne$/i.test(c[1]) || c[1].toLowerCase() === 'alle') continue;
            for (const id of c[1].toLowerCase().split(/[,\s]+/).filter(Boolean)) {
              const doel = per.get(id) ?? [...per.values()].find((x) => x.id.replace(/[a-z]\d?$/, '') === id);
              if (doel) doel.fouten.push(`${c[2]} → ${c[3]}`);
            }
          }
        } catch { /* rapport niet te lezen */ }
      }
      if (on) setSt({ fase: per.size ? 'ok' : 'leeg', kaarten: [...per.values()].sort((a, b) => sceneSort(a.id, b.id)), rapport });
    })();
    return () => { on = false; };
  }, [folder]);
  return st;
}
/** still of preview van een scène: pas gelezen als hij in beeld komt */
function SceneThumb({ path }: { path?: string }) {
  const ref = useRef<HTMLDivElement>(null); const [zicht, setZicht] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el || !path || typeof IntersectionObserver === 'undefined') return;
    const io = new IntersectionObserver((e) => { if (e.some((x) => x.isIntersecting)) { setZicht(true); io.disconnect(); } }); io.observe(el);
    return () => io.disconnect();
  }, [path]);
  const url = useBeeld(zicht ? path : undefined);
  return (
    <div ref={ref} className="relative aspect-video overflow-hidden rounded-md bg-[#141a36]">
      {url ? <button className="h-full w-full" onClick={() => path && openBestand(path)} title="Groot bekijken"><img src={url} alt="" className="h-full w-full object-cover" /></button>
        : <span className="absolute inset-0 flex items-center justify-center text-[10px] text-slate-500">{path ? 'laden…' : 'geen beeld'}</span>}
    </div>
  );
}
export function SceneBoard() {
  const L = useLive((s) => s.data);
  const toast = useGame((s) => s.toast);
  const video = L.videos.filter((v) => v.status !== 'Online' && v.steps.some((x) => x.active && /Animatie|Render|Sets|Cast/.test(x.label))).sort((a, b) => b.nr - a.nr)[0];
  const board = useSceneBoard(video?.folder);
  const [open, setOpen] = useState<string | null>(null); const [alles, setAlles] = useState(false);
  if (!video) return <Sec title="Scènebord" icon={<Clapperboard size={13} />} color="#FF4DB8"><Leeg>Er is nu geen video in animatie of render.</Leeg></Sec>;
  const extra = L as unknown as { scenes?: SceneData[]; blender?: { scenes?: SceneData[] } };
  const data = (extra.blender?.scenes ?? extra.scenes ?? []).filter((d) => d && typeof d.id === 'string' && (d.video == null || d.video === video.nr));
  const tekst = `${L.blender?.stand ?? ''} ${L.activity.map((a) => `${a.doing ?? ''} ${a.needs ?? ''}`).join(' ')}`;
  const voortgang = /(\d+)\s+van de\s+(\d+)\s+sc[eè]nes\s+klaar/i.exec(tekst);
  const nu = /\bd(\d+[a-z]?\d?)\s+is\s+bezig/i.exec(tekst)?.[1]?.toLowerCase();
  const kaarten: Kaart[] = board.kaarten.map((k) => ({ ...k, data: data.find((d) => d.id.toLowerCase() === k.id) }));
  for (const d of data) if (!kaarten.some((k) => k.id === d.id.toLowerCase())) kaarten.push({ id: d.id.toLowerCase(), fouten: [], data: d, preview: d.preview });
  kaarten.sort((a, b) => sceneSort(a.id, b.id));
  const qcIngevuld = data.some((d) => d.qc && Object.keys(d.qc).length);
  const Stip = ({ ok, label }: { ok?: boolean; label: string }) => (
    <span className="inline-flex items-center gap-0.5 text-[10px]" title={ok == null ? `${label}: niet bekend` : ok ? label : `nog niet ${label}`}>
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: ok == null ? KLEUR.stil : ok ? KLEUR.klaar : KLEUR.wacht }} /><span className={ok ? 'text-slate-200' : 'text-slate-500'}>{label}</span>
    </span>
  );
  return (
    <Sec title={`Scènebord video ${video.nr}`} icon={<Clapperboard size={13} />} color="#FF4DB8" right={<span className="text-[11px] text-slate-500">{kaarten.length ? `${kaarten.length} scènes` : ''}</span>}>
      {voortgang && (
        <div className="mb-2">
          <div className="mb-0.5 flex justify-between gap-2 text-[11.5px]"><span className="text-slate-300">Render op je pc</span><span className="font-bold" style={{ color: KLEUR.bezig }}>{voortgang[1]} van {voortgang[2]} klaar{nu ? ` · d${nu} is bezig` : ''}</span></div>
          <div className="h-1.5 rounded-full bg-white/10"><div className="h-1.5 rounded-full" style={{ width: `${Math.min(100, (+voortgang[1] / Math.max(1, +voortgang[2])) * 100)}%`, background: KLEUR.bezig }} /></div>
        </div>
      )}
      {board.fase === 'laden' ? <Leeg>Scènes laden…</Leeg> : !kaarten.length ? <Leeg>{board.fase === 'geen' ? 'Open de HQ in claude.ai om de stills en previews uit de projectmap te zien.' : `Nog geen stills of previews gevonden in ${video.folder}stillscheck/ of preview/.`}</Leeg> : (
        <>
          <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-3">
            {(alles ? kaarten : kaarten.slice(0, 9)).map((k) => {
              const d = k.data;
              // gebouwd: er zijn stills van de scène; gecontroleerd: de stills-check heeft er een rapport over; gerenderd: alleen als het bekend is
              const gebouwd = d?.gebouwd ?? (k.still || k.preview ? true : undefined);
              const gecontroleerd = d?.gecontroleerd ?? (board.rapport && k.still ? true : undefined);
              const fouten = [...(d?.fouten ?? []), ...k.fouten];
              const qcBekend = !!d?.qc && Object.keys(d.qc).length > 0;
              const rood = qcBekend ? QC.filter(([q]) => d!.qc![q] === false).length : 0;
              return (
                <div key={k.id} className="rounded-lg border bg-white/[.02] p-1" style={{ borderColor: nu === k.id ? `${KLEUR.bezig}aa` : rood ? `${KLEUR.probleem}88` : 'rgba(255,255,255,.07)' }}>
                  <SceneThumb path={k.preview ?? k.still} />
                  <div className="mt-1 flex items-center justify-between gap-1"><b className="text-[12px] text-white">Scène {k.id}</b>{nu === k.id && <span className="text-[10px] font-bold" style={{ color: KLEUR.bezig }}>rendert nu</span>}</div>
                  <div className="flex flex-wrap gap-x-1.5"><Stip ok={gebouwd} label="gebouwd" /><Stip ok={gecontroleerd} label="gecontroleerd" /><Stip ok={d?.gerenderd} label="gerenderd" /></div>
                  <button onClick={() => setOpen(open === k.id ? null : k.id)} aria-expanded={open === k.id} className="mt-0.5 flex w-full items-center gap-1 text-left text-[10.5px] text-slate-400 hover:text-white">
                    <span className="flex gap-px">{QC.map(([q]) => { const v = d?.qc?.[q]; return <span key={q} className="h-2 w-1.5 rounded-sm" style={{ background: v == null ? '#334155' : v ? KLEUR.klaar : KLEUR.probleem }} />; })}</span>
                    <span>{qcBekend ? (rood ? `${rood} rood` : 'alles groen') : 'geen data'}</span>
                    {fouten.length > 0 && <span className="ml-auto font-semibold" style={{ color: KLEUR.wacht }}>{fouten.length} fout{fouten.length > 1 ? 'en' : ''}</span>}
                  </button>
                  {open === k.id && (
                    <div className="mt-1 space-y-0.5 border-t border-white/10 pt-1">
                      {QC.map(([q, label]) => { const v = d?.qc?.[q]; return <div key={q} className="flex gap-1 text-[10.5px]"><span style={{ color: v == null ? KLEUR.stil : v ? KLEUR.klaar : KLEUR.probleem }}>{v == null ? '○' : v ? '✓' : '✗'}</span><span className="text-slate-300">{label}</span></div>; })}
                      {fouten.map((f, i) => <div key={i} className="text-[10.5px] leading-snug text-orange-200">• {f}</div>)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          {kaarten.length > 9 && <button onClick={() => setAlles(!alles)} className="mt-1.5 text-[12px] font-semibold text-[#FF4DB8] hover:underline">{alles ? 'Minder tonen' : `Alle ${kaarten.length} scènes tonen`}</button>}
        </>
      )}
      {!qcIngevuld && (
        <div className="mt-2 rounded-lg bg-white/[.04] px-2 py-1.5 text-[11.5px] leading-snug text-slate-300">
          Jouw kwaliteitscheck per scène (tekst strak, teller, props, sets, clipping, bestek, rennen, armen, 0,6 s uitloop) is nog niet ingevuld. Grijs betekent: geen data.{' '}
          <button className="font-semibold text-[#FF4DB8] hover:underline" onClick={() => order(`Vul voor video ${video.nr} per scène de kwaliteitscheck in (${QC.map(([, l]) => l.toLowerCase()).join(', ')}) en zet hem in status.json onder blender.scenes: [{ id, video, gebouwd, gecontroleerd, gerenderd, fouten, qc: { ${QC.map(([q]) => q).join(', ')} } }].`, toast, { doel: 'Productie' })}>Laat Claude hem invullen</button>
        </div>
      )}
      {board.rapport && <button onClick={() => openBestand(board.rapport!)} className="mt-1.5 block text-[11.5px] font-semibold text-sky-300 hover:underline">Rapport van de stills-check lezen</button>}
    </Sec>
  );
}

/* =================== PUBLICATIE: uploaddag en shortsplanning (punt 57) =================== */
export function openUploaddag() {
  try { localStorage.setItem('driftmark-view-videos-v34', 'upload'); } catch { /* */ }
  useGame.getState().setPage('videos');
  setTimeout(() => window.dispatchEvent(new CustomEvent('dm-view', { detail: { mode: 'videos', view: 'upload' } })), 60);
}
export function PublicatieBlok() {
  const L = useLive((s) => s.data);
  const toast = useGame((s) => s.toast);
  const shorts = (L.youtube?.videos ?? []).filter((v) => v.type === 'short');
  const online = shorts.filter((v) => (v.status ?? 'public') === 'public');
  const gepland = shorts.filter((v) => v.status && v.status !== 'public');
  const klaar = L.videos.filter((v) => v.status !== 'Online' && /upload/i.test(v.status));
  return (
    <>
      <Sec title="Uploaddag" icon={<ListChecks size={13} />} color="#398CFF">
        <div className="text-[12px] leading-snug text-slate-300">{klaar.length ? klaar.map((v) => `Video ${v.nr} (${v.werktitel}): ${v.status}`).join(' · ') : 'Titel, beschrijving, tags en thumbnail klaar om in YouTube Studio te plakken, met een afvinklijst.'}</div>
        <button onClick={openUploaddag} className="mt-2 inline-flex items-center gap-1 rounded-lg bg-[#398CFF]/25 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#398CFF]/40"><ArrowRight size={12} />Uploaddag openen</button>
      </Sec>
      <Sec title="Shortsplanning" icon={<Clapperboard size={13} />} color="#398CFF" right={<span className="text-[11px] text-slate-500">{online.length} online</span>}>
        {!L.shorts.length ? <Leeg>Nog geen shorts bekend.</Leeg> : (
          <div className="space-y-1.5">
            {L.shorts.map((g) => {
              const c = /klaar|online/i.test(g.status) ? KLEUR.klaar : /niet gestart/i.test(g.status) ? KLEUR.stil : KLEUR.bezig;
              return (
                <div key={g.title} className="text-[12px]">
                  <div className="flex items-center gap-2"><span className="h-2 w-2 shrink-0 rounded-full" style={{ background: c }} /><span className="min-w-0 flex-1 truncate font-semibold text-white">{g.title}</span><span className="shrink-0 text-[11px]" style={{ color: c }}>{g.status}</span></div>
                  <div className="truncate pl-4 text-[11px] text-slate-400">{(g.items ?? []).join(' · ')}</div>
                </div>
              );
            })}
            {gepland.length > 0 && <div className="text-[11.5px] text-slate-300">Ingepland op YouTube: {gepland.map((v) => `${v.title}${v.datum ? ` (${v.datum})` : ''}`).join(' · ')}</div>}
          </div>
        )}
        <button onClick={() => order('Maak een planning voor de shorts van de komende twee weken: welke short op welke dag en tijd, met de link naar de bijbehorende lange video.', toast, { doel: 'Publicatie' })} className="mt-2 inline-flex items-center gap-1 rounded-lg bg-[#398CFF]/20 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#398CFF]/35"><Send size={12} />Plan de shorts</button>
      </Sec>
    </>
  );
}

/* =================== CEO: lessen van de maand (punt 58) =================== */
export function LessenVanDeMaand() {
  const L = useLive((s) => s.data);
  const eigen = (L as unknown as { lessen?: ({ titel?: string; tekst?: string } | string)[] }).lessen;
  const afgeleid = useMemo(() => {
    const maand = Date.now() - 31 * 864e5;
    const vids = (L.youtube?.videos ?? []).filter((v) => { const t = Date.parse(v.date ?? v.datum ?? ''); return !isNaN(t) && t >= maand; });
    const shorts = vids.filter((v) => v.type === 'short' && v.views != null).sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
    const longs = vids.filter((v) => v.type === 'long' && v.views != null).sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
    const out: string[] = [];
    if (shorts.length >= 2) out.push(`Je beste short van de maand, "${shorts[0].title}", haalde ${nl(shorts[0].views)} weergaven; de minste ${nl(shorts[shorts.length - 1].views)}. Kijk wat die hook anders doet.`);
    const sv = shorts.reduce((a, v) => a + (v.views ?? 0), 0); const lv = longs.reduce((a, v) => a + (v.views ?? 0), 0);
    if (shorts.length && longs.length) out.push(`Shorts brachten deze maand ${nl(sv)} weergaven, lange video's ${nl(lv)}. ${sv > lv ? 'Laat elke short duidelijk naar de lange video verwijzen.' : "De lange video's dragen het kanaal."}`);
    const avp = longs.filter((v) => v.avp != null).sort((a, b) => (b.avp ?? 0) - (a.avp ?? 0));
    if (avp.length >= 2) out.push(`"${avp[0].title}" werd het langst bekeken (gemiddeld ${Math.round(avp[0].avp!)}%), "${avp[avp.length - 1].title}" het kortst (${Math.round(avp[avp.length - 1].avp!)}%).`);
    else if (longs[0]) out.push(`Je best bekeken lange video van de maand is "${longs[0].title}" met ${nl(longs[0].views)} weergaven.`);
    return out.slice(0, 3);
  }, [L]);
  const lijst = eigen?.length ? eigen.slice(0, 3).map((x) => (typeof x === 'string' ? x : [x.titel, x.tekst].filter(Boolean).join(': '))) : afgeleid;
  return (
    <Sec title="Lessen van de maand" icon={<Lightbulb size={13} />} color="#FACC15" right={<span className="text-[11px] text-slate-500">{eigen?.length ? 'van Claude' : lijst.length ? 'uit je cijfers' : ''}</span>}>
      {!lijst.length ? <Leeg>Nog te weinig cijfers van deze maand. De lessen komen met het weekrapport op maandag.</Leeg> : (
        <ol className="space-y-1 text-[12px] leading-snug text-slate-200">{lijst.map((l, i) => <li key={i} className="flex gap-2"><b className="text-[#FACC15]">{i + 1}.</b><span>{l}</span></li>)}</ol>
      )}
      {!eigen?.length && lijst.length > 0 && <div className="mt-1 text-[10.5px] text-slate-500">Berekend uit je YouTube-cijfers van de laatste 31 dagen; de uitgebreide lessen komen met het weekrapport.</div>}
    </Sec>
  );
}
