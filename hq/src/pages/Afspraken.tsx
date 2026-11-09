/**
 * VASTE AFSPRAKEN, BESLUITENLOGBOEK EN VERSIES (verbeterlijst punten 15, 46 en 48).
 * - Afspraken: de regels van niels uit het projectgeheugen (notities van de soort "Afspraak"), met per regel
 *   "Aanpassen": dat wordt een opdracht die Claude in het projectgeheugen opslaat.
 * - Besluiten: elke regel uit het geheugenoverzicht met een datum, op één tijdlijn (nieuwste bovenaan).
 * - Versies: twee versies van een script of document naast elkaar, met wat er veranderd is gemarkeerd.
 */
import { useEffect, useMemo, useState } from 'react';
import { PenLine, Plus, GitCompare } from 'lucide-react';
import { useKennis, bezoekKennis, openKennis, leesBestand, type Bestand } from '../services/kennis';
import { openOpdracht } from '../services/real';
import { Md } from '../components/shared/Md';

/* ---------------- 15: vaste afspraken ---------------- */
export function Afspraken() {
  const g = useKennis((s) => s.geheugen);
  useEffect(() => { void bezoekKennis(); }, []);
  const regels = (g.data?.notities ?? []).filter((n) => n.soort === 'feedback').sort((a, b) => a.titel.localeCompare(b.titel, 'nl'));
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <p className="min-w-0 flex-1 text-[14px] text-slate-400">Je vaste regels voor elke video. Wil je iets veranderen? Klik op Aanpassen: Claude past het aan in het projectgeheugen en elke thread houdt zich er daarna aan.</p>
        <button className="btn-primary text-[13px]" onClick={() => openOpdracht({ doel: 'Algemeen', text: 'Nieuwe vaste afspraak voor elke video, sla op in het projectgeheugen: ', titel: 'Nieuwe vaste afspraak' })}><Plus size={14} />Nieuwe afspraak</button>
      </div>
      {g.fase === 'laden' && !g.data && <div className="panel p-5 text-center text-[14px] text-slate-400">Laden…</div>}
      {g.data && !regels.length && <div className="panel p-5 text-center text-[14px] text-slate-400">Nog geen vaste afspraken gevonden.</div>}
      {!g.data && g.fase !== 'laden' && <div className="panel p-5 text-center text-[14px] text-slate-400">Het projectgeheugen is hier niet te lezen. Open het HQ in claude.ai.</div>}
      <div className="grid gap-3 md:grid-cols-2">
        {regels.map((n) => (
          <div key={n.naam} className="panel flex flex-col p-4">
            <div className="font-display text-[16px] font-bold text-white">{n.titel}</div>
            <div className="mt-1 line-clamp-4 flex-1 text-[13px] text-slate-300">{n.beschrijving || n.tekst.slice(0, 240)}</div>
            <div className="mt-3 flex gap-2">
              <button className="btn-ghost !py-1 text-[12px]" onClick={() => openKennis({ tab: 'geheugen', notitie: n.naam })}>Lezen</button>
              <button className="btn-ghost !py-1 text-[12px]" onClick={() => openOpdracht({ doel: 'Algemeen', text: `Pas de vaste afspraak "${n.titel}" (${n.bestand}) aan in het projectgeheugen: `, titel: `Afspraak aanpassen: ${n.titel}` })}><PenLine size={12} />Aanpassen</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------------- 46: besluitenlogboek ---------------- */
const MAAND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
export function besluitenUit(index: string) {
  const uit: { datum: string; wie?: string; tekst: string }[] = [];
  for (const r of index.split('\n')) {
    const regel = r.replace(/^[-*]\s+/, '').trim();
    const m = regel.match(/(20\d\d)-(\d\d)-(\d\d)/);
    if (!m || regel.length < 20) continue;
    const kop = regel.match(/^([A-ZÀ-Ü0-9 '-]{3,}(?:\([^)]*\))?)\s*:/);
    const wie = /niels/i.test(regel.slice(0, 80)) ? 'niels' : undefined;
    const tekst = regel.replace(/^\[[^\]]+\]\([^)]+\):\s*/, '').trim();
    uit.push({ datum: `${m[1]}-${m[2]}-${m[3]}`, wie, tekst: kop ? tekst : tekst });
  }
  return uit.sort((a, b) => b.datum.localeCompare(a.datum));
}
export function Besluiten() {
  const g = useKennis((s) => s.geheugen);
  useEffect(() => { void bezoekKennis(); }, []);
  const lijst = useMemo(() => besluitenUit(g.data?.index ?? ''), [g.data?.index]);
  if (!g.data) return <div className="panel p-5 text-center text-[14px] text-slate-400">{g.fase === 'laden' ? 'Laden…' : 'Het projectgeheugen is hier niet te lezen. Open het HQ in claude.ai.'}</div>;
  let vorige = '';
  return (
    <div className="panel p-4">
      <p className="mb-3 text-[14px] text-slate-400">Alle beslissingen over stijl, stemmen, regels en titels op één tijdlijn, met de datum en waarom. Ze komen uit het projectgeheugen en worden vanzelf bijgewerkt.</p>
      {!lijst.length && <div className="text-[14px] text-slate-500">Nog geen beslissingen met een datum gevonden.</div>}
      <ol className="relative space-y-2 border-l border-white/10 pl-4">
        {lijst.map((b, i) => {
          const [j, mm, d] = b.datum.split('-');
          const kop = b.datum !== vorige; vorige = b.datum;
          return (
            <li key={i} className="relative">
              {kop && <span className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full bg-orange-400" />}
              {kop && <div className="text-[12px] font-bold uppercase tracking-wider text-orange-300">{Number(d)} {MAAND[Number(mm) - 1]} {j}</div>}
              <div className="rounded-xl bg-white/[.03] px-3 py-2 text-[13px] text-slate-200"><Md text={b.tekst} compact /></div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

/* ---------------- 48: versies van scripts en documenten ---------------- */
const basis = (p: string) => p.replace(/[_-]v\d+(\.\d+)*(?=\.\w+$)/i, '').replace(/\.\w+$/, '');
export function versieGroepen(bestanden: Bestand[]) {
  const per = new Map<string, Bestand[]>();
  for (const b of bestanden) { if (!/\.(md|txt)$/i.test(b.path)) continue; const k = basis(b.path); per.set(k, [...(per.get(k) ?? []), b]); }
  return [...per.entries()].filter(([, l]) => l.length > 1 && l.some((b) => /[_-]v\d/i.test(b.path))).map(([k, l]) => ({ k, l: l.sort((a, b) => a.path.localeCompare(b.path, 'nl', { numeric: true })) }));
}
/** regel-diff (LCS), genoeg voor scripts van een paar honderd regels */
export function verschil(a: string[], b: string[]) {
  const n = a.length, m = b.length;
  if (n * m > 4_000_000) return null;
  const t = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) t[i][j] = a[i] === b[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
  const uit: { s: ' ' | '-' | '+'; r: string }[] = [];
  let i = 0, j = 0;
  while (i < n && j < m) { if (a[i] === b[j]) { uit.push({ s: ' ', r: a[i] }); i++; j++; } else if (t[i + 1][j] >= t[i][j + 1]) uit.push({ s: '-', r: a[i++] }); else uit.push({ s: '+', r: b[j++] }); }
  while (i < n) uit.push({ s: '-', r: a[i++] }); while (j < m) uit.push({ s: '+', r: b[j++] });
  return uit;
}
export function Versies() {
  const d = useKennis((s) => s.documenten);
  useEffect(() => { void bezoekKennis(); }, []);
  const groepen = useMemo(() => versieGroepen(d.data?.bestanden ?? []), [d.data]);
  const [k, setK] = useState<string | null>(null);
  const gr = groepen.find((x) => x.k === k) ?? groepen[0];
  const [ab, setAb] = useState<[string, string] | null>(null);
  useEffect(() => { if (gr) setAb([gr.l[gr.l.length - 2].path, gr.l[gr.l.length - 1].path]); }, [gr?.k]); // eslint-disable-line react-hooks/exhaustive-deps
  const [tekst, setTekst] = useState<[string, string] | null>(null);
  const [alleen, setAlleen] = useState(true);
  useEffect(() => {
    if (!ab) return; setTekst(null); let weg = false;
    void Promise.all(ab.map((p) => leesBestand(p))).then(([x, y]) => { if (!weg) setTekst([x.kind === 'tekst' ? x.tekst : '', y.kind === 'tekst' ? y.tekst : '']); });
    return () => { weg = true; };
  }, [ab]);
  const diff = useMemo(() => (tekst ? verschil(tekst[0].split('\n'), tekst[1].split('\n')) : null), [tekst]);
  if (!d.data) return <div className="panel p-5 text-center text-[14px] text-slate-400">{d.fase === 'laden' ? 'Laden…' : 'De documenten zijn hier niet te lezen. Open het HQ in claude.ai.'}</div>;
  if (!groepen.length) return <div className="panel p-5 text-center text-[14px] text-slate-400">Er zijn nog geen documenten met meerdere versies (zoals script_v1.0 en script_v1.1).</div>;
  const telPlus = diff?.filter((x) => x.s === '+').length ?? 0; const telMin = diff?.filter((x) => x.s === '-').length ?? 0;
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-[13px]">
        <GitCompare size={15} className="text-orange-300" />
        <select className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-white" value={gr?.k} onChange={(e) => setK(e.target.value)} aria-label="Document">{groepen.map((x) => <option key={x.k} value={x.k}>{x.k.split('/').slice(-2).join('/')}</option>)}</select>
        {ab && gr && (<>
          <select className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-white" value={ab[0]} onChange={(e) => setAb([e.target.value, ab[1]])} aria-label="Oude versie">{gr.l.map((b) => <option key={b.path} value={b.path}>{b.name}</option>)}</select>
          <span className="text-slate-500">→</span>
          <select className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-white" value={ab[1]} onChange={(e) => setAb([ab[0], e.target.value])} aria-label="Nieuwe versie">{gr.l.map((b) => <option key={b.path} value={b.path}>{b.name}</option>)}</select>
        </>)}
        <label className="ml-auto flex items-center gap-1.5 text-slate-300"><input type="checkbox" checked={alleen} onChange={(e) => setAlleen(e.target.checked)} className="accent-orange-400" />Alleen wat veranderd is</label>
      </div>
      {!diff ? <div className="panel p-5 text-center text-[14px] text-slate-400">{tekst ? 'Deze documenten zijn te groot om te vergelijken.' : 'Laden…'}</div> : (
        <div className="panel overflow-hidden">
          <div className="border-b border-white/10 px-4 py-2 text-[13px] text-slate-400"><span className="text-emerald-300">+{telPlus} regels erbij</span> · <span className="text-rose-300">−{telMin} regels weg</span></div>
          <div className="max-h-[65vh] overflow-y-auto font-mono text-[12px] leading-relaxed">
            {diff.map((x, i) => {
              if (alleen && x.s === ' ' && !diff.slice(Math.max(0, i - 2), i + 3).some((y) => y.s !== ' ')) return null;
              return <div key={i} className={`whitespace-pre-wrap break-words px-4 ${x.s === '+' ? 'bg-emerald-500/10 text-emerald-200' : x.s === '-' ? 'bg-rose-500/10 text-rose-200 line-through decoration-rose-400/40' : 'text-slate-400'}`}>{x.s === ' ' ? '  ' : `${x.s} `}{x.r || ' '}</div>;
            })}
          </div>
        </div>
      )}
    </div>
  );
}
