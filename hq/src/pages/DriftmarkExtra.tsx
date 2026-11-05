import { useEffect, useState } from 'react';
import { Bot, ExternalLink, Cpu, Coins, MessageSquareReply, Image as ImageIcon, Download } from 'lucide-react';
import { useTools, findNum } from '../services/tools';
import { useLive, readFile, downloadFile, type Output } from '../services/live';
import { useDb, type StatRow } from '../services/db';

const Card = ({ title, status, children }: { title: string; status: string; children: React.ReactNode }) => {
  const c = status === 'ok' ? '#10b981' : status === 'laden' ? '#94a3b8' : '#f59e0b';
  return (
    <div className="rounded-xl bg-white/[.03] p-3">
      <div className="mb-1 flex items-center justify-between gap-2"><span className="text-xs font-semibold text-white">{title}</span><span className="h-2 w-2 rounded-full" style={{ background: c }} title={status} /></div>
      <div className="space-y-0.5 text-[11px] text-slate-400">{children}</div>
    </div>
  );
};
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
const err = (t: { status: string; error?: string }) => t.status === 'laden' ? 'Laden…' : t.status === 'geen' ? 'Alleen op de gepubliceerde pagina in claude.ai.' : `Niet bereikbaar: ${t.error ?? ''}`;

export function ToolsPanel() {
  const { tools, refresh } = useTools();
  const blender = useLive((s) => s.data.blender);
  const el = tools.elevenlabs, vq = tools.vidiq, vqc = tools.vidiqch, hf = tools.higgsfield, nl = tools.nexlev;
  const vqAccount = (vqc.data as Any)?.authenticatedAs as string | undefined;
  const vqHasDrift = ((vqc.data as Any)?.channels ?? []).some((c: Any) => /drift/i.test(c.title ?? ''));
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200"><Cpu size={16} />Gereedschap live</div>
        <button className="text-[11px] text-indigo-300 hover:text-white" onClick={() => void refresh()}>Verversen</button>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        <Card title="Blender (je pc)" status={blender ? 'ok' : 'laden'}>
          {blender ? (<>
            <div className="text-slate-300">{blender.stand}</div>
            {blender.wachtrij.slice(0, 6).map((w) => <div key={w.naam}>• {w.naam} <span className="text-slate-500">· {w.status}</span></div>)}
            <div className="text-slate-500">bijgewerkt {blender.bijgewerkt}</div>
          </>) : <div>Renderwachtrij via Remote Control op je pc. De animatie-thread zet de stand hier neer.</div>}
        </Card>
        <Card title="ElevenLabs (stemmen)" status={el.status}>
          {el.status === 'ok' ? ((el.data as Any)?.flows ?? []).slice(0, 4).map((f: Any) => (
            <div key={f.flow_id} className="flex justify-between gap-2"><a className="truncate text-indigo-300 hover:text-white" href={f.url} target="_blank" rel="noreferrer">{f.name}</a><span className="shrink-0 text-slate-500">{f.node_count} nodes</span></div>
          )) : <div>{err(el)}</div>}
        </Card>
        <Card title="vidIQ" status={vq.status === 'ok' && !vqHasDrift ? 'fout' : vq.status}>
          {vq.status === 'ok' ? (<>
            <div>Credits: <span className="text-white">{(vq.data as Any)?.totalCredits ?? '?'}</span> · vernieuwt {new Date((vq.data as Any)?.renewableResetsAt).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}</div>
            {vqAccount && <div>Account: {vqAccount}</div>}
            {((vqc.data as Any)?.channels ?? []).filter((c: Any) => /drift/i.test(c.title ?? '')).map((c: Any) => (
              <div key={c.channelId} className="text-emerald-300">Driftmark gekoppeld · {Number(c.subscriberCount).toLocaleString('nl-NL')} abonnees · {Number(c.viewCount).toLocaleString('nl-NL')} weergaven · {c.videoCount} video's</div>
            ))}
            {!vqHasDrift && vqc.status === 'ok' && <div className="text-amber-300">Driftmark hangt niet aan dit vidIQ-account. Koppel vidIQ opnieuw met het Google-account van Driftmark.</div>}
          </>) : <div>{err(vq)}</div>}
        </Card>
        <Card title="Higgsfield" status={hf.status}>
          {hf.status === 'ok' ? <div>Credits: <span className="text-white">{(hf.data as Any)?.credits ?? '?'}</span> · abonnement {(hf.data as Any)?.subscription_plan_type ?? '?'}</div> : <div>{err(hf)}</div>}
          <div>Ook als add-on in Blender op je pc.</div>
        </Card>
        <Card title="NexLev (kanaal Driftmark)" status={nl.status}>
          {nl.status === 'ok' ? (<>
            <div>Abonnees: <span className="text-white">{findNum(nl.data, /subscriber/i)?.toLocaleString('nl-NL') ?? '?'}</span></div>
            <div>Weergaven: <span className="text-white">{findNum(nl.data, /view/i)?.toLocaleString('nl-NL') ?? '?'}</span></div>
            <div>Video's: <span className="text-white">{findNum(nl.data, /video/i) ?? '?'}</span></div>
          </>) : <div>{nl.status === 'fout' ? 'Weeklimiet van het gratis plan op; weer beschikbaar vanaf 7 nov 14:03.' : err(nl)}</div>}
        </Card>
      </div>
    </section>
  );
}

export function CostsPanel() {
  const costs = useLive((s) => s.data.costs) ?? [];
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200"><Coins size={16} />Kosten</div>
      {costs.length === 0 ? <div className="text-xs text-slate-500">Nog geen kosten genoteerd.</div> : (
        <div className="overflow-x-auto"><table className="w-full text-left text-[11px]"><thead className="text-slate-500"><tr><th className="py-1 pr-2">Datum</th><th className="pr-2">Wat</th><th className="pr-2">Credits</th><th>Bedrag</th></tr></thead>
          <tbody>{costs.map((c, i) => <tr key={i} className="border-t border-white/5 text-slate-300"><td className="py-1 pr-2">{c.datum}</td><td className="pr-2">{c.wat}{c.notitie ? <span className="text-slate-500"> · {c.notitie}</span> : null}</td><td className="pr-2">{c.credits ?? '—'}</td><td>{typeof c.bedrag === 'number' ? `€ ${c.bedrag.toFixed(2).replace('.', ',')}` : 'onbekend'}</td></tr>)}</tbody></table></div>
      )}
    </section>
  );
}

export function RepliesPanel() {
  const replies = useLive((s) => s.data.replies) ?? [];
  if (!replies.length) return null;
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200"><MessageSquareReply size={16} />Antwoorden op je opdrachten</div>
      <ul className="space-y-2">{replies.slice(0, 8).map((r, i) => (
        <li key={i} className="rounded-lg bg-white/[.03] p-2.5 text-[11px]"><div className="text-slate-500">{r.at} · jij: <span className="text-slate-300">{r.opdracht}</span></div><div className="mt-0.5 text-slate-200">{r.antwoord}</div></li>
      ))}</ul>
    </section>
  );
}

function Thumb({ o }: { o: Output }) {
  const [url, setUrl] = useState<string | null>(null);
  const [fail, setFail] = useState(false);
  useEffect(() => {
    let u: string | null = null;
    if (o.kind === 'image') readFile(o.path).then((b) => { u = URL.createObjectURL(new Blob([b as BlobPart])); setUrl(u); }).catch(() => setFail(true));
    return () => { if (u) URL.revokeObjectURL(u); };
  }, [o.path, o.kind]);
  return (
    <div className="overflow-hidden rounded-lg border border-white/5 bg-black/20">
      {o.kind === 'image' && url && <img src={url} alt={o.name} className="aspect-video w-full object-cover" />}
      {o.kind === 'image' && !url && <div className="flex aspect-video items-center justify-center text-[10px] text-slate-500">{fail ? 'Preview niet te laden' : <ImageIcon size={16} />}</div>}
      <div className="flex items-center justify-between gap-1 px-2 py-1 text-[10px]"><span className="truncate text-slate-300">{o.name}</span><button className="shrink-0 text-indigo-300 hover:text-white" title="Downloaden" onClick={() => void downloadFile(o.path)}><Download size={12} /></button></div>
    </div>
  );
}

export function Outputs({ nr }: { nr: number }) {
  const outs = useLive((s) => s.data.outputs?.[String(nr)]) ?? [];
  if (!outs.length) return null;
  return <div className="mt-2 grid grid-cols-2 gap-1.5">{outs.slice(0, 6).map((o) => <Thumb key={o.path} o={o} />)}</div>;
}

export { ExternalLink };

/* ---------- Automatisering: routine, controles, cijfergeschiedenis en logboek ---------- */
function Spark({ rows, k, color, label }: { rows: StatRow[]; k: 'subscribers' | 'views'; color: string; label: string }) {
  const pts = rows.filter((r) => typeof r[k] === 'number');
  const last = pts[pts.length - 1]?.[k];
  const first = pts[0]?.[k];
  const W = 240, H = 56;
  let d = '';
  if (pts.length > 1) {
    const vals = pts.map((r) => r[k] as number);
    const min = Math.min(...vals), max = Math.max(...vals), span = max - min || 1;
    d = vals.map((v, i) => `${i ? 'L' : 'M'}${((i / (vals.length - 1)) * W).toFixed(1)},${(H - 4 - ((v - min) / span) * (H - 8)).toFixed(1)}`).join(' ');
  }
  const diff = last != null && first != null ? last - first : null;
  return (
    <div className="min-w-0 rounded-xl bg-white/[.03] p-3">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-[11px] uppercase tracking-wider text-slate-400">{label}</span>
        {diff != null && pts.length > 1 && <span className="text-xs font-semibold" style={{ color: diff >= 0 ? '#3ddc97' : '#ff4d6d' }}>{diff >= 0 ? '+' : ''}{diff.toLocaleString('nl-NL')}</span>}
      </div>
      <div className="font-display text-2xl font-bold text-white">{last != null ? last.toLocaleString('nl-NL') : '—'}</div>
      {d ? <svg viewBox={`0 0 ${W} ${H}`} className="mt-1 h-14 w-full" preserveAspectRatio="none"><path d={d} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" /></svg>
        : <div className="mt-1 text-[11px] text-slate-500">De grafiek groeit vanzelf: elk uur komt er een meetpunt bij.</div>}
      {pts.length > 0 && <div className="text-[10px] text-slate-500">{pts.length} meetpunten sinds {fmt(pts[0].at)}</div>}
    </div>
  );
}
const fmt = (iso?: string) => { if (!iso) return '—'; try { return new Date(iso).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' }); } catch { return iso; } };
const KIND: Record<string, string> = { info: '#3db8ff', waarschuwing: '#ff8a3d', fout: '#ff4d6d' };

export function AutomationPanel() {
  const { ready, offline, stats, log, engine } = useDb();
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200"><Bot size={16} />Automatisering</div>
        <span className="text-[11px] text-slate-400">
          {engine?.lastRun ? <>Laatste ronde {fmt(engine.lastRun)} · volgende {fmt(engine.nextRun)}</> : ready ? 'Wacht op de eerste ronde' : offline ? 'Database nu niet bereikbaar' : 'Laden…'}
        </span>
      </div>
      <p className="mb-3 text-[11px] text-slate-400">Elk uur draait er vanzelf een ronde. Die haalt je kanaalcijfers op, controleert alle taken en meldt het meteen als iets vastloopt. Je hoeft er niets voor te doen.</p>
      <div className="mb-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
        <Spark rows={stats} k="subscribers" color="#ff8a3d" label="Abonnees" />
        <Spark rows={stats} k="views" color="#3db8ff" label="Weergaven" />
      </div>
      {!!engine?.checks?.length && (
        <div className="mb-3 flex flex-wrap gap-1.5">{engine.checks.map((c) => (
          <span key={c.naam} title={c.notitie} className="rounded-full px-2.5 py-1 text-[11px] font-medium" style={{ background: c.ok ? 'rgba(61,220,151,.12)' : 'rgba(255,77,109,.14)', color: c.ok ? '#3ddc97' : '#ff4d6d' }}>{c.ok ? '✓' : '!'} {c.naam}</span>
        ))}</div>
      )}
      {log.length > 0 && (
        <ul className="space-y-1">{log.slice(0, 6).map((l, i) => (
          <li key={i} className="flex gap-2 text-[11px]"><span className="mt-1 h-2 w-2 shrink-0 rounded-full" style={{ background: KIND[l.kind] ?? '#94a3b8' }} /><span className="shrink-0 text-slate-500">{fmt(l.at)}</span><span className="min-w-0 text-slate-300">{l.text}</span></li>
        ))}</ul>
      )}
    </section>
  );
}
