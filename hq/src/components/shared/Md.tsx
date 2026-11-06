/**
 * MARKDOWN ALS REACT-ELEMENTEN, nooit als HTML: alle tekst is data (geheugen, gesprekken, scripts, coachantwoorden).
 * Kent: koppen, alinea's, lijsten (ook ingesprongen en genummerd, met vinkjes), tabellen, citaten, codeblokken,
 * scheidingslijnen, **vet**, *schuin*, ~~doorgehaald~~, `code`, links en losse https-adressen.
 * Links: alleen http(s) gaat naar buiten (nieuw tabblad, rel="noreferrer"). Intern zijn #cmsg_... (een thread of
 * bericht), [[naam]] en naam.md (een geheugennotitie) en /mnt/project-files/... (een projectbestand); die handelt
 * de aanroeper af met onLink. Zonder onLink, of bij elk ander soort link, blijft het gewone tekst.
 * hl: zoekwoorden (zie lib/vouw.ts) die gemarkeerd worden.
 */
import { useMemo, type ReactNode } from 'react';
import { treffers, veiligPad, vouw } from '../../lib/tekst';

export type MdLink =
  | { soort: 'thread'; id: string; label: string }
  | { soort: 'notitie'; naam: string; label: string }
  | { soort: 'bestand'; pad: string; label: string };

interface Ctx { hl?: string[]; onLink?: (l: MdLink) => void; compact?: boolean }


function linkVan(doel: string, label: string): { web: string } | { intern: MdLink } | null {
  const t = doel.trim();
  if (/^https?:\/\/[^\s]+$/i.test(t)) return { web: t };
  const cm = /^#(cmsg_[A-Za-z0-9_-]{6,160})$/.exec(t);
  if (cm) return { intern: { soort: 'thread', id: cm[1], label } };
  const mnt = /^\/mnt\/project-files\/(.+)$/.exec(t);
  if (mnt) { let p = mnt[1]; try { p = decodeURIComponent(p); } catch { /* laten zoals het is */ } return veiligPad(p) ? { intern: { soort: 'bestand', pad: p, label } } : null; }
  const md = /^(?:\.\/)?([A-Za-z0-9_.-]{1,120})\.md$/.exec(t);
  if (md) return { intern: { soort: 'notitie', naam: md[1], label } };
  return null;
}

/** tekst met de zoekwoorden gemarkeerd */
function markeer(t: string, ctx: Ctx, k: string): ReactNode {
  if (!ctx.hl?.length || !t) return t;
  const hits = treffers(vouw(t), ctx.hl);
  if (!hits.length) return t;
  const uit: ReactNode[] = []; let i = 0;
  hits.forEach(([a, b], n) => {
    if (a > i) uit.push(t.slice(i, a));
    uit.push(<mark key={`${k}h${n}`} data-hl="" className="rounded-sm bg-amber-300/30 px-px text-amber-50">{t.slice(a, b)}</mark>);
    i = b;
  });
  if (i < t.length) uit.push(t.slice(i));
  return uit;
}

const LINKKLASSE = 'text-sky-300 underline decoration-sky-300/40 underline-offset-2 [overflow-wrap:anywhere] hover:text-white';
// `code` · [[notitie|label]] · [label](doel) · **vet** · __vet__ · ~~weg~~ · *schuin* · losse https-adressen
const INLINE = /(`+)([^`\n]+?)\1|\[\[([^\]|\n]{1,120})(?:\|([^\]\n]{1,200}))?\]\]|\[([^\]\n]{1,300})\]\(([^()\s]{1,800})(?:\s+"[^"\n]*")?\)|\*\*([^*\n]+?)\*\*|__([^_\n]+?)__|~~([^~\n]+?)~~|\*([^*\s][^*\n]*?)\*|(https?:\/\/[^\s<>()[\]]+)/g;
const WOORD = /[\p{L}\p{N}_*]/u;

function inline(text: string, ctx: Ctx, k: string, diep = 0, link = true): ReactNode[] {
  const uit: ReactNode[] = [];
  let last = 0; let n = 0;
  const re = new RegExp(INLINE.source, 'g');
  const tekst = (a: number, b: number) => { if (b > a) uit.push(<span key={`${k}t${n++}`}>{markeer(text.slice(a, b), ctx, `${k}t${n}`)}</span>); };
  const binnen = (s: string) => (diep < 3 ? inline(s, ctx, `${k}i${n}`, diep + 1, link) : [markeer(s, ctx, `${k}i${n}`)]);
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    const start = m.index; let eind = start + m[0].length;
    let node: ReactNode = null;
    if (m[2] != null) node = <code key={`${k}c${n}`} className="rounded bg-white/[.08] px-1 py-px font-mono text-[.92em] text-orange-100 [overflow-wrap:anywhere]">{markeer(m[2], ctx, `${k}c${n}`)}</code>;
    else if (m[3] != null) {
      const naam = m[3].trim(); const label = (m[4] ?? m[3]).trim();
      node = link && ctx.onLink
        ? <button key={`${k}w${n}`} type="button" className={`${LINKKLASSE} inline text-left`} onClick={() => ctx.onLink?.({ soort: 'notitie', naam, label })}>{markeer(label, ctx, `${k}w${n}`)}</button>
        : <span key={`${k}w${n}`} className="text-sky-200">{markeer(label, ctx, `${k}w${n}`)}</span>;
    } else if (m[5] != null) {
      const l = linkVan(m[6], m[5]);
      const label = link ? inline(m[5], ctx, `${k}l${n}`, diep + 1, false) : [markeer(m[5], ctx, `${k}l${n}`)];
      if (l && 'web' in l && link) node = <a key={`${k}a${n}`} href={l.web} target="_blank" rel="noreferrer" className={LINKKLASSE}>{label}</a>;
      else if (l && 'intern' in l && link && ctx.onLink) { const doel = l.intern; node = <button key={`${k}b${n}`} type="button" className={`${LINKKLASSE} inline text-left`} onClick={() => ctx.onLink?.(doel)}>{label}</button>; }
      else node = <span key={`${k}s${n}`} className="text-sky-200">{label}</span>;
    } else if (m[7] != null || m[8] != null) node = <strong key={`${k}v${n}`} className="font-semibold text-white">{binnen(m[7] ?? m[8])}</strong>;
    else if (m[9] != null) node = <del key={`${k}d${n}`} className="text-slate-400">{binnen(m[9])}</del>;
    else if (m[10] != null) {
      // *schuin* alleen tussen woorden, niet in iets als 2*3*4 of **
      const voor = start > 0 ? text[start - 1] : ' '; const na = text[eind] ?? ' ';
      if (WOORD.test(voor) || WOORD.test(na) || /\s$/.test(m[10])) { re.lastIndex = start + 1; continue; }
      node = <em key={`${k}e${n}`} className="italic">{binnen(m[10])}</em>;
    } else if (m[11] != null) {
      // losse link: leestekens aan het eind horen bij de zin
      let url = m[11]; const rest = /[.,;:!?'")\]]+$/.exec(url);
      if (rest) { url = url.slice(0, -rest[0].length); eind -= rest[0].length; re.lastIndex = eind; }
      node = link ? <a key={`${k}u${n}`} href={url} target="_blank" rel="noreferrer" className={LINKKLASSE}>{markeer(url, ctx, `${k}u${n}`)}</a> : <span key={`${k}u${n}`}>{markeer(url, ctx, `${k}u${n}`)}</span>;
    }
    tekst(last, start);
    uit.push(node); n++;
    last = eind;
  }
  tekst(last, text.length);
  return uit;
}

/* ---------- blokken ---------- */
type Item = { diep: number; nr?: string; vink?: boolean; tekst: string };
type Blok =
  | { t: 'kop'; n: number; tekst: string }
  | { t: 'p'; regels: string[] }
  | { t: 'lijst'; items: Item[] }
  | { t: 'tabel'; kop: string[]; rijen: string[][]; uitlijn: ('left' | 'center' | 'right')[] }
  | { t: 'citaat'; tekst: string }
  | { t: 'code'; tekst: string }
  | { t: 'lijn' };

const FENCE = /^\s{0,3}(```|~~~)/;
const KOP = /^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$/;
const LIJN = /^\s{0,3}([-*_])(\s*\1){2,}\s*$/;
const LIJST = /^(\s*)([-*•+]|\d{1,3}[.)])\s+(?:\[([ xX])\]\s+)?(.*)$/;
const SCHEIDING = /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/;
const CITAAT = /^\s{0,3}>/;
const isTabel = (L: string[], i: number) => L[i].includes('|') && i + 1 < L.length && L[i + 1].includes('|') && L[i + 1].includes('-') && SCHEIDING.test(L[i + 1]);
const blokBegin = (L: string[], i: number) => FENCE.test(L[i]) || KOP.test(L[i]) || LIJN.test(L[i]) || CITAAT.test(L[i]) || LIJST.test(L[i]) || isTabel(L, i);
const cellen = (x: string) => x.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());

function blokken(text: string): Blok[] {
  const L = text.replace(/\r\n?/g, '\n').split('\n');
  const uit: Blok[] = [];
  let i = 0;
  while (i < L.length) {
    const l = L[i];
    if (!l.trim()) { i++; continue; }
    const f = FENCE.exec(l);
    if (f) {
      const r: string[] = []; i++;
      while (i < L.length && !L[i].trim().startsWith(f[1])) { r.push(L[i]); i++; }
      i++; uit.push({ t: 'code', tekst: r.join('\n') }); continue;
    }
    const h = KOP.exec(l);
    if (h) { uit.push({ t: 'kop', n: h[1].length, tekst: h[2] }); i++; continue; }
    if (LIJN.test(l)) { uit.push({ t: 'lijn' }); i++; continue; }
    if (isTabel(L, i)) {
      const kop = cellen(l);
      const uitlijn = cellen(L[i + 1]).map((c) => (c.startsWith(':') && c.endsWith(':') ? 'center' : c.endsWith(':') ? 'right' : 'left') as 'left' | 'center' | 'right');
      i += 2; const rijen: string[][] = [];
      while (i < L.length && L[i].trim() && L[i].includes('|')) { rijen.push(cellen(L[i])); i++; }
      uit.push({ t: 'tabel', kop, rijen, uitlijn }); continue;
    }
    if (CITAAT.test(l)) {
      const r: string[] = [];
      while (i < L.length && CITAAT.test(L[i])) { r.push(L[i].replace(/^\s{0,3}>\s?/, '')); i++; }
      uit.push({ t: 'citaat', tekst: r.join('\n') }); continue;
    }
    if (LIJST.test(l)) {
      const items: Item[] = [];
      while (i < L.length) {
        const m = LIJST.exec(L[i]);
        if (m) {
          const insp = m[1].replace(/\t/g, '    ').length;
          items.push({ diep: Math.min(4, Math.floor(insp / 2)), nr: /\d/.test(m[2]) ? m[2] : undefined, vink: m[3] ? m[3] !== ' ' : undefined, tekst: m[4] });
          i++; continue;
        }
        // vervolgregel van het vorige item (ingesprongen)
        if (L[i].trim() && /^\s{2,}\S/.test(L[i]) && !blokBegin(L, i)) { items[items.length - 1].tekst += '\n' + L[i].trim(); i++; continue; }
        break;
      }
      uit.push({ t: 'lijst', items }); continue;
    }
    const r: string[] = [l]; i++;
    while (i < L.length && L[i].trim() && !blokBegin(L, i)) { r.push(L[i]); i++; }
    uit.push({ t: 'p', regels: r });
  }
  return uit;
}

function Regels({ regels, ctx, k }: { regels: string[]; ctx: Ctx; k: string }) {
  return <>{regels.map((r, j) => <span key={j}>{j > 0 && <br />}{inline(r, ctx, `${k}r${j}`)}</span>)}</>;
}

function Blokken({ lijst, ctx, k }: { lijst: Blok[]; ctx: Ctx; k: string }) {
  const c = ctx.compact;
  return (
    <>
      {lijst.map((b, i) => {
        const key = `${k}${i}`;
        switch (b.t) {
          case 'kop': return (
            <div key={key} role="heading" aria-level={Math.min(6, b.n + 1)} className={c ? 'pt-1 font-semibold text-white' : b.n <= 2 ? 'pt-2 font-display text-[16px] font-bold text-orange-200' : b.n === 3 ? 'pt-1.5 font-display text-[15px] font-bold text-white' : 'pt-1 font-semibold text-slate-100'}>
              {inline(b.tekst, ctx, key)}
            </div>
          );
          case 'p': return <p key={key}><Regels regels={b.regels} ctx={ctx} k={key} /></p>;
          case 'lijst': return (
            <div key={key} className={c ? 'space-y-0.5' : 'space-y-1'}>
              {b.items.map((it, j) => (
                <div key={j} className="flex gap-2" style={it.diep ? { paddingLeft: it.diep * 16 } : undefined}>
                  <span className={`shrink-0 ${it.nr ? 'min-w-[1.2em] tabular-nums text-orange-300' : 'text-orange-400'}`} aria-hidden>{it.vink != null ? (it.vink ? '☑' : '☐') : it.nr ?? (it.diep ? '◦' : '•')}</span>
                  <span className="min-w-0 flex-1"><Regels regels={it.tekst.split('\n')} ctx={ctx} k={`${key}-${j}`} /></span>
                </div>
              ))}
            </div>
          );
          case 'tabel': return (
            <div key={key} className="overflow-x-auto rounded-lg border border-white/10">
              <table className="min-w-full border-collapse text-[.93em]">
                <thead><tr className="bg-white/[.05]">{b.kop.map((x, j) => <th key={j} style={{ textAlign: b.uitlijn[j] ?? 'left' }} className="border-b border-white/10 px-2.5 py-1.5 font-semibold text-white">{inline(x, ctx, `${key}k${j}`)}</th>)}</tr></thead>
                <tbody>{b.rijen.map((r, j) => <tr key={j} className="border-t border-white/[.06] align-top">{b.kop.map((_, x) => <td key={x} style={{ textAlign: b.uitlijn[x] ?? 'left' }} className="px-2.5 py-1.5">{inline(r[x] ?? '', ctx, `${key}r${j}c${x}`)}</td>)}</tr>)}</tbody>
              </table>
            </div>
          );
          case 'citaat': return <div key={key} className="space-y-1 border-l-2 border-orange-400/50 pl-3 text-slate-300"><Blokken lijst={blokken(b.tekst)} ctx={ctx} k={`${key}q`} /></div>;
          case 'code': return <pre key={key} className="overflow-x-auto whitespace-pre rounded-lg bg-black/30 p-3 font-mono text-[12.5px] leading-relaxed text-slate-200"><code>{markeer(b.tekst, ctx, key)}</code></pre>;
          case 'lijn': return <hr key={key} className="border-white/10" />;
        }
        return null;
      })}
    </>
  );
}

/** Markdown (of gewone tekst) netjes weergegeven. Data: wordt nooit door de automatische vertaling (lib/nl.ts) gehaald. */
export function Md({ text, hl, onLink, compact, className = '' }: { text: string; hl?: string[]; onLink?: (l: MdLink) => void; compact?: boolean; className?: string }) {
  const lijst = useMemo(() => blokken(text ?? ''), [text]);
  const ctx: Ctx = { hl, onLink, compact };
  return <div translate="no" className={`${compact ? 'space-y-1' : 'space-y-1.5'} break-words ${className}`}><Blokken lijst={lijst} ctx={ctx} k="b" /></div>;
}
