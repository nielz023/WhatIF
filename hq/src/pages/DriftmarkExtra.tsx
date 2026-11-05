import { useEffect, useState } from 'react';
import { ExternalLink, Cpu, Coins, MessageSquareReply, Image as ImageIcon, Download } from 'lucide-react';
import { useTools, findNum } from '../services/tools';
import { useLive, readFile, downloadFile, type Output } from '../services/live';

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
  const el = tools.elevenlabs, vq = tools.vidiq, vqc = tools.vidiqch, hf = tools.higgsfield, gh = tools.github, nl = tools.nexlev;
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
        <Card title="GitHub (scripts)" status={gh.status}>
          {gh.status === 'ok' ? ((gh.data as Any) ?? []).slice(0, 3).map((c: Any) => (
            <a key={c.sha} href={c.html_url} target="_blank" rel="noreferrer" className="block truncate text-indigo-300 hover:text-white">{new Date(c.commit?.author?.date).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' })} · {String(c.commit?.message ?? '').split('\n')[0]}</a>
          )) : <div>{err(gh)}</div>}
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
