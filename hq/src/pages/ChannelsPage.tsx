import { useState } from 'react';
import { Plus, Clapperboard, Pencil, Check } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Avatar, DemoBadge, PageHeader, Progress, StatusBadge } from '../components/ui';
import { ChartPanel, AreaSeries } from '../components/shared/charts';
import { dailySeries } from '../modules/analytics/metrics';
import { DEPARTMENTS } from '../modules/departments/departments';
import { compact, eur } from '../lib/util';

export default function ChannelsPage() {
  const s = useGame();
  const [sel, setSel] = useState(s.channels[0]?.id);
  const [edit, setEdit] = useState(false);
  const c = s.channels.find((x) => x.id === sel) ?? s.channels[0];
  const [form, setForm] = useState({ niche: '', audience: '', perWeek: 1 });
  if (!c) return null;
  const series = dailySeries(s, c.id, 30);
  const projects = s.projects.filter((p) => p.channelId === c.id);
  const agents = s.agents.filter((a) => a.channelIds.includes(c.id));
  const videos = s.videos.filter((v) => v.channelId === c.id).sort((a, b) => b.publishedTick - a.publishedTick);

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="YouTube Channels" subtitle="Simulated channels. Each has its own niche, audience, schedule, projects and dedicated agents." actions={<button className="btn-primary text-xs" onClick={() => s.openModal('newChannel')}><Plus size={14} />New channel</button>} />
      <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {s.channels.map((ch) => (
          <button key={ch.id} onClick={() => { setSel(ch.id); setEdit(false); }} className={`panel relative overflow-hidden p-4 text-left transition hover:-translate-y-0.5 ${sel === ch.id ? 'border-indigo-400/70 shadow-neon' : ''}`}>
            <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full opacity-30 blur-2xl" style={{ background: ch.logo.color }} />
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl text-2xl" style={{ background: `${ch.logo.color}33`, boxShadow: `0 0 0 1px ${ch.logo.color}66` }}>{ch.logo.emoji}</div>
              <div className="min-w-0"><div className="truncate font-semibold text-white">{ch.name}</div><div className="truncate text-xs text-slate-400">{ch.niche}</div></div>
            </div>
            <div className="mt-3 grid grid-cols-3 text-center text-xs">
              <div><div className="font-bold text-white">{compact(ch.subscribers)}</div><div className="text-slate-500">subs</div></div>
              <div><div className="font-bold text-white">{compact(ch.views)}</div><div className="text-slate-500">views</div></div>
              <div><div className="font-bold text-white">{eur(ch.revenue)}</div><div className="text-slate-500">revenue</div></div>
            </div>
            <div className="mt-2 flex items-center gap-2">
              {ch.monetized ? <span className="chip bg-emerald-500/15 text-emerald-300">💸 Monetized</span> : <span className="chip bg-slate-700/40 text-slate-300">{ch.subscribers}/1000 to monetize</span>}
              {ch.isDemo && <DemoBadge label="DEMO" />}
            </div>
            {!ch.monetized && <div className="mt-2"><Progress value={(ch.subscribers / 1000) * 100} h={4} color={ch.logo.color} /></div>}
          </button>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          <ChartPanel title={`${c.name} · last 30 days`}><AreaSeries data={series} keys={[{ key: 'views', color: c.logo.color, name: 'Views' }, { key: 'subs', color: '#22c55e', name: 'New subs' }]} fmt={compact} /></ChartPanel>
          <div className="panel p-4">
            <div className="mb-3 flex items-center justify-between"><div className="text-sm font-semibold text-white">Projects ({projects.length})</div><button className="btn-ghost !py-1 text-xs" onClick={() => s.openModal('newVideo')}><Clapperboard size={13} />New video</button></div>
            <div className="space-y-1.5">
              {projects.length === 0 && <div className="text-sm text-slate-500">No projects yet for this channel.</div>}
              {projects.slice(0, 10).map((p) => (
                <button key={p.id} onClick={() => s.selectProject(p.id)} className="flex w-full items-center justify-between rounded-lg bg-white/[.03] px-3 py-2 text-left text-sm hover:bg-white/[.06]"><span className="truncate text-white">{p.title}</span><StatusBadge status={p.status} /></button>
              ))}
            </div>
          </div>
          <div className="panel p-4">
            <div className="mb-3 text-sm font-semibold text-white">Published videos ({videos.length})</div>
            <table className="w-full text-xs">
              <thead><tr className="text-left uppercase tracking-wider text-slate-500"><th className="pb-2">Title</th><th>Views</th><th>CTR</th><th>AVD</th><th>Revenue</th></tr></thead>
              <tbody>{videos.map((v) => (<tr key={v.id} className="border-t border-hq-line/50 text-slate-300"><td className="max-w-[260px] truncate py-1.5 text-white">{v.title}{v.projectId === 'demo' && <span className="ml-1 text-amber-300/70">(demo)</span>}</td><td>{compact(v.views)}</td><td>{v.ctr}%</td><td>{v.avd}%</td><td>{eur(v.revenue, 2)}</td></tr>))}</tbody>
            </table>
          </div>
        </div>

        <div className="space-y-4">
          <div className="panel p-4">
            <div className="mb-3 flex items-center justify-between">
              <div className="text-sm font-semibold text-white">Channel profile</div>
              {!edit ? <button className="btn-ghost !py-1 text-xs" onClick={() => { setForm({ niche: c.niche, audience: c.audience, perWeek: c.uploadsPerWeek }); setEdit(true); }}><Pencil size={12} />Edit</button>
                : <button className="btn-success !py-1 text-xs" onClick={() => { s.updateChannel(c.id, { niche: form.niche, audience: form.audience, uploadsPerWeek: form.perWeek, uploadSchedule: `${form.perWeek}x / week` }); setEdit(false); s.toast('Channel updated.', 'success'); }}><Check size={12} />Save</button>}
            </div>
            {edit ? (
              <div className="space-y-2">
                <div><label className="label">Niche</label><input className="input" value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} /></div>
                <div><label className="label">Target audience</label><input className="input" value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} /></div>
                <div><label className="label">Uploads / week</label><input className="input" type="number" min={1} value={form.perWeek} onChange={(e) => setForm({ ...form, perWeek: Math.max(1, +e.target.value) })} /></div>
              </div>
            ) : (
              <dl className="space-y-2 text-sm">
                {[['Niche', c.niche], ['Target audience', c.audience], ['Upload schedule', c.uploadSchedule], ['RPM', eur(c.rpm, 2)], ['Subscribers', c.subscribers.toLocaleString()], ['Total views', c.views.toLocaleString()], ['Revenue', eur(c.revenue, 2)]].map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-3"><dt className="text-slate-500">{k}</dt><dd className="text-right text-slate-200">{v}</dd></div>
                ))}
              </dl>
            )}
          </div>
          <div className="panel p-4">
            <div className="mb-2 text-sm font-semibold text-white">Dedicated agents ({agents.length})</div>
            <p className="mb-2 text-xs text-slate-500">Agents not assigned to a specific channel work for all channels.</p>
            <div className="flex flex-wrap gap-2">{agents.map((a) => <button key={a.id} onClick={() => s.selectAgent(a.id)}><Avatar agent={a} size={34} /></button>)}</div>
            <div className="label mt-4">Assign a whole department</div>
            <div className="grid grid-cols-2 gap-1.5">
              {DEPARTMENTS.map((d) => (
                <button key={d.id} className="rounded-lg border border-hq-line px-2 py-1.5 text-left text-xs text-slate-300 hover:border-indigo-400" onClick={() => s.askConfirm({ title: `Dedicate ${d.short} to ${c.name}?`, body: `All ${s.agents.filter((a) => a.department === d.id).length} agents in ${d.name} will only work on ${c.name} projects. Other channels' work in this department will wait.`, confirmLabel: 'Assign department', onConfirm: () => s.assignDeptToChannel(d.id, c.id) })}>
                  {d.icon} {d.short}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
