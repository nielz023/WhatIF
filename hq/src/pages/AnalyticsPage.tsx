import { useMemo, useState } from 'react';
import { Users, FolderKanban, Eye, UserPlus, Euro, Receipt, TrendingUp, MousePointerClick, Timer, Coins, Hourglass } from 'lucide-react';
import { useGame } from '../store/useGame';
import { DemoBadge, PageHeader, StatCard, Tabs } from '../components/ui';
import { ChartPanel, AreaSeries, Bars, LineSeries, CHART_COLORS } from '../components/shared/charts';
import { dailySeries, kpis, productionStats } from '../modules/analytics/metrics';
import { compact, eur, pct } from '../lib/util';

export default function AnalyticsPage() {
  const s = useGame();
  const [range, setRange] = useState<'14' | '30' | '90'>('30');
  const [channel, setChannel] = useState<string>('all');
  const k = kpis(s);
  const series = useMemo(() => dailySeries(s, channel === 'all' ? null : channel, +range), [s.stats, s.ledger, channel, range]); // eslint-disable-line
  const perChannel = useMemo(() => {
    const today = Math.floor(s.tick / 24);
    const days = Array.from({ length: +range }, (_, i) => today - +range + i).filter((d) => d >= 0);
    return days.map((d) => {
      const row: Record<string, number | string> = { label: `D${d}` };
      s.channels.forEach((c) => { row[c.name] = s.stats.find((x) => x.day === d && x.channelId === c.id)?.views ?? 0; });
      return row;
    });
  }, [s.stats, s.channels, range, s.tick]);
  const prod = productionStats(s);
  const channelTable = s.channels.map((c) => {
    const vids = s.videos.filter((v) => v.channelId === c.id);
    return { c, videos: vids.length, ctr: vids.length ? vids.reduce((a, v) => a + v.ctr, 0) / vids.length : 0, avd: vids.length ? vids.reduce((a, v) => a + v.avd, 0) / vids.length : 0 };
  });
  const top = [...s.videos].sort((a, b) => b.views - a.views).slice(0, 6);

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader
        title="CEO Dashboard"
        subtitle={<span className="flex items-center gap-2">Company-wide performance, production and finances {s.demoMode && <DemoBadge label="INCLUDES DEMO DATA" />}</span>}
        actions={<>
          <select className="input !w-auto !py-1.5 text-xs" value={channel} onChange={(e) => setChannel(e.target.value)}>
            <option value="all">All channels</option>
            {s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <Tabs value={range} onChange={setRange} items={[{ id: '14', label: '14d' }, { id: '30', label: '30d' }, { id: '90', label: '90d' }]} />
        </>}
      />
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-6">
        <StatCard label="Active agents" value={`${k.activeAgents}/${s.agents.length}`} icon={<Users size={16} />} color="#22d3ee" onClick={() => s.setPage('agents')} />
        <StatCard label="Active projects" value={k.activeProjects} icon={<FolderKanban size={16} />} color="#a855f7" onClick={() => s.setPage('projects')} />
        <StatCard label="Total views" value={compact(k.views)} icon={<Eye size={16} />} color="#3b82f6" />
        <StatCard label="Subscribers" value={compact(k.subs)} icon={<UserPlus size={16} />} color="#ec4899" onClick={() => s.setPage('channels')} />
        <StatCard label="Revenue" value={eur(k.revenue)} icon={<Euro size={16} />} color="#22c55e" onClick={() => s.setPage('finances')} />
        <StatCard label="Expenses" value={eur(k.expenses)} icon={<Receipt size={16} />} color="#f43f5e" onClick={() => s.setPage('finances')} />
        <StatCard label="Profit" value={<span className={k.profit < 0 ? 'text-rose-400' : 'text-emerald-300'}>{eur(k.profit)}</span>} icon={<TrendingUp size={16} />} color="#22c55e" />
        <StatCard label="CTR (7d)" value={pct(k.ctr)} icon={<MousePointerClick size={16} />} color="#f59e0b" />
        <StatCard label="AVD (7d)" value={pct(k.avd)} sub="avg % viewed" icon={<Timer size={16} />} color="#a855f7" />
        <StatCard label="RPM" value={eur(k.rpm, 2)} icon={<Coins size={16} />} color="#facc15" />
        <StatCard label="Pending approvals" value={k.pendingApprovals} icon={<Hourglass size={16} />} color="#fb923c" onClick={() => s.setPage('projects')} />
        <StatCard label="Reputation" value={`${Math.round(s.company.reputation)}/100`} icon={<TrendingUp size={16} />} color="#6366f1" />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <ChartPanel title="Revenue vs expenses (€ / day)"><AreaSeries data={series} keys={[{ key: 'revenue', color: '#22c55e', name: 'Revenue' }, { key: 'expenses', color: '#f43f5e', name: 'Expenses' }]} fmt={(v) => `€${Math.round(v)}`} /></ChartPanel>
        <ChartPanel title="Views per day"><AreaSeries data={series} keys={[{ key: 'views', color: '#22d3ee', name: 'Views' }]} fmt={compact} /></ChartPanel>
        <ChartPanel title="Channel performance (views/day)"><Bars data={perChannel} x="label" stacked keys={s.channels.map((c, i) => ({ key: c.name, color: c.logo.color || CHART_COLORS[i] }))} fmt={compact} /></ChartPanel>
        <ChartPanel title="CTR & AVD trend (%)"><LineSeries data={series.filter((x) => x.ctr > 0)} keys={[{ key: 'ctr', color: '#f59e0b', name: 'CTR %' }, { key: 'avd', color: '#a855f7', name: 'AVD %' }]} /></ChartPanel>
        <ChartPanel title="Production performance by stage" h={280}><Bars data={prod} x="stage" keys={[{ key: 'completed', color: '#22c55e', name: 'Completed' }, { key: 'active', color: '#6366f1', name: 'Active' }, { key: 'rejected', color: '#f43f5e', name: 'Rejected' }]} /></ChartPanel>
        <ChartPanel title="Average quality by stage" h={280}><Bars data={prod.filter((p) => p.quality > 0)} x="stage" layout="vertical" keys={[{ key: 'quality', color: '#a855f7', name: 'Quality' }]} /></ChartPanel>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <div className="panel p-4">
          <div className="mb-3 text-sm font-semibold text-white">Channels</div>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-[11px] uppercase tracking-wider text-slate-500"><th className="pb-2">Channel</th><th>Subs</th><th>Views</th><th>Videos</th><th>CTR</th><th>AVD</th><th>RPM</th></tr></thead>
            <tbody>
              {channelTable.map(({ c, videos, ctr, avd }) => (
                <tr key={c.id} className="border-t border-hq-line/50 text-slate-300">
                  <td className="py-2 font-semibold text-white">{c.logo.emoji} {c.name}</td><td>{compact(c.subscribers)}</td><td>{compact(c.views)}</td><td>{videos}</td><td>{pct(ctr)}</td><td>{pct(avd)}</td><td>{eur(c.rpm, 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel p-4">
          <div className="mb-3 text-sm font-semibold text-white">Top videos</div>
          <div className="space-y-2">
            {top.map((v, i) => {
              const c = s.channels.find((x) => x.id === v.channelId);
              return (
                <div key={v.id} className="flex items-center gap-3 text-sm">
                  <span className="w-5 text-center font-display font-bold text-slate-500">{i + 1}</span>
                  <span className="flex-1 truncate text-white">{v.title}<span className="ml-2 text-xs text-slate-500">{c?.name}{v.projectId === 'demo' ? ' · demo' : ''}</span></span>
                  <span className="text-xs text-slate-400">{compact(v.views)} views</span>
                  <span className="w-14 text-right text-xs text-amber-300">{v.ctr}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
