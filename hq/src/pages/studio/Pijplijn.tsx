/**
 * VIDEOPIJPLIJN ALS BEDIENINGSPANEEL (verbeterlijst punt 8).
 * Per video alle stappen van idee tot upload, met hun stand, de bestanden die erbij horen en één knop
 * "Volgende stap starten" die een opdracht klaarzet voor Claude. De stand komt uit status.json (videos[].steps);
 * stappen die daar niet in staan (kwaliteitscheck, thumbnail) leiden we af en dat staat er dan ook bij.
 */
import { ExternalLink, FileText, Image as Beeld, Play } from 'lucide-react';
import { useLive, type Output } from '../../services/live';
import { openOpdracht } from '../../services/real';
import { openBestand } from '../../components/shared/BestandViewer';
import { threadUrl, type RealVideo } from '../../data/driftmark';
import { KLEUR, type Soort } from '../../lib/status';
import Blok from '../../components/shared/Blok';

type Stap = { naam: string; bron: string[]; zoek: RegExp; uitleg: string };
const STAPPEN: Stap[] = [
  { naam: 'Idee', bron: ['Idee', 'Verloop'], zoek: /verloop|idee/i, uitleg: 'onderwerp, verloop en twist' },
  { naam: 'Script', bron: ['Script'], zoek: /script|hook/i, uitleg: 'het Engelse script per scène' },
  { naam: 'Stemmen', bron: ['Stemmen'], zoek: /stem|audio|regels\.tsv|voice/i, uitleg: 'ElevenLabs, alle regels' },
  { naam: 'Cast', bron: ['Cast'], zoek: /cast/i, uitleg: 'figuren in Blender' },
  { naam: 'Sets', bron: ['Sets'], zoek: /\bsets?\b|decor/i, uitleg: 'decors in Blender' },
  { naam: 'Animatie', bron: ['Animatie'], zoek: /anim/i, uitleg: 'alle scènes animeren' },
  { naam: 'Kwaliteitscheck', bron: ['Kwaliteitscheck', 'Check'], zoek: /stillscheck|kwaliteit|controle/i, uitleg: 'stills en scènes nakijken vóór de render' },
  { naam: 'Render', bron: ['Render'], zoek: /render/i, uitleg: 'renderen op je pc' },
  { naam: 'Montage', bron: ['Montage'], zoek: /montage|eindversie|edit/i, uitleg: 'eindmontage op -14 LUFS' },
  { naam: 'Thumbnail', bron: ['Thumbnail'], zoek: /thumb/i, uitleg: 'thumbnail kiezen' },
  { naam: 'Upload', bron: ['Upload-tekst', 'Upload', 'Online'], zoek: /upload|youtube/i, uitleg: 'titel, beschrijving en online zetten' },
];
type Stand = { soort: Soort; tekst: string; afgeleid?: boolean };

function standen(v: RealVideo, outs: Output[]): Stand[] {
  const vind = (labels: string[]) => v.steps.filter((s) => labels.includes(s.label));
  const ruw = STAPPEN.map((st): Stand | null => {
    const s = vind(st.bron);
    if (st.naam === 'Thumbnail' && !s.length) return outs.some((o) => /thumb/i.test(o.path)) ? { soort: 'klaar', tekst: 'gekozen', afgeleid: true } : null;
    if (!s.length) return null;
    if (s.every((x) => x.done)) return { soort: 'klaar', tekst: 'klaar' };
    if (s.some((x) => x.active || x.done)) return { soort: 'bezig', tekst: 'bezig' };
    return { soort: 'stil', tekst: 'nog niet' };
  });
  // stap zonder gegevens: klaar als een latere stap al klaar is, anders onbekend
  return ruw.map((r, i) => r ?? (ruw.slice(i + 1).some((x) => x?.soort === 'klaar' || x?.soort === 'bezig') ? { soort: 'klaar', tekst: 'klaar', afgeleid: true } : { soort: 'stil', tekst: 'geen gegevens', afgeleid: true }));
}

export default function Pijplijn({ v }: { v: RealVideo }) {
  const outs = (useLive((s) => s.data.outputs)?.[String(v.nr)] ?? []).filter((o): o is Output => !!o && typeof o === 'object' && typeof o.path === 'string' && !o.path.endsWith('/'));
  const activity = useLive((s) => s.data.activity);
  const st = standen(v, outs);
  const volgende = st.findIndex((s) => s.soort !== 'klaar');
  const bezig = st.findIndex((s) => s.soort === 'bezig');
  const online = v.status === 'Online';
  const thread = activity.find((a) => a.video === v.nr && a.state === 'working')?.id ?? v.threads[v.threads.length - 1]?.id;
  const files = (stap: Stap) => {
    const l = outs.filter((o) => stap.zoek.test(o.name));
    if (stap.naam === 'Script' && v.script && !l.some((o) => o.path === v.script)) l.unshift({ name: 'Script', path: v.script, kind: 'file' });
    return l.slice(0, 4);
  };
  const start = () => {
    const s = STAPPEN[bezig >= 0 ? bezig : volgende];
    if (!s) return;
    openOpdracht({
      titel: `Video ${v.nr}: ${s.naam}`, thread,
      text: bezig >= 0
        ? `Video ${v.nr} (${v.werktitel}): hoe staat de stap "${s.naam}" (${s.uitleg})? Werk hem af en start daarna de volgende stap. Zet de stand in status.json.`
        : `Video ${v.nr} (${v.werktitel}): start de volgende stap "${s.naam}" (${s.uitleg}). Zet de stand in status.json.`,
    });
  };
  return (
    <Blok naam={`Pijplijn video ${v.nr}`}>
      <section className="panel p-4">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="text-[13px] font-bold uppercase tracking-wider text-slate-400">Video {v.nr} · {v.werktitel}</div>
            <div className="font-display text-[17px] font-bold leading-snug text-white">{v.title}</div>
            <div className="text-[13px] text-slate-400">{v.status}{v.lengte ? ` · ${v.lengte}` : ''}</div>
          </div>
          {!online && volgende >= 0 && (
            <button className="btn-primary shrink-0 text-[13px]" onClick={start}><Play size={13} />{bezig >= 0 ? `${STAPPEN[bezig].naam} afmaken` : 'Volgende stap starten'}</button>
          )}
        </div>
        <ol className="mt-3 grid gap-1.5 sm:grid-cols-2">
          {STAPPEN.map((s, i) => {
            const k = KLEUR[st[i].soort];
            const f = files(s);
            return (
              <li key={s.naam} className={`rounded-xl px-3 py-2 ${i === (bezig >= 0 ? bezig : volgende) && !online ? 'bg-white/[.07] ring-1 ring-orange-400/40' : 'bg-white/[.03]'}`}>
                <div className="flex items-center justify-between gap-2">
                  <span className="flex min-w-0 items-center gap-2 text-[14px] font-semibold text-white">
                    <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${st[i].soort === 'bezig' ? 'animate-pulse' : ''}`} style={{ background: k }} />{i + 1}. {s.naam}
                  </span>
                  <span className="shrink-0 text-[12px]" style={{ color: k }} title={st[i].afgeleid ? 'Niet apart bijgehouden; afgeleid uit de andere stappen' : undefined}>{st[i].tekst}{st[i].afgeleid && st[i].tekst !== 'geen gegevens' ? ' (afgeleid)' : ''}</span>
                </div>
                {f.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {f.map((o) => (
                      <button key={o.path} onClick={() => openBestand(o.path)} className="inline-flex max-w-full items-center gap-1 truncate rounded-md bg-white/5 px-1.5 py-0.5 text-[12px] text-sky-300 hover:text-white" title={o.path}>
                        {o.kind === 'image' ? <Beeld size={11} /> : <FileText size={11} />}<span className="truncate">{o.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </li>
            );
          })}
        </ol>
        <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-white/5 pt-2 text-[13px]">
          {v.youtube && <a href={v.youtube} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sky-300 hover:text-white">Op YouTube<ExternalLink size={11} /></a>}
          {v.threads.map((t) => <a key={t.id} href={threadUrl(t.id)} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sky-300 hover:text-white">{t.title}<ExternalLink size={11} /></a>)}
          {v.folder && <span className="text-slate-500">map: {v.folder}</span>}
        </div>
      </section>
    </Blok>
  );
}
