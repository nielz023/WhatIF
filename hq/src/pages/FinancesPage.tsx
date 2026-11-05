import { useMemo, useState } from 'react';
import { useGame } from '../store/useGame';
import { DemoBadge, PageHeader, StatCard } from '../components/ui';
import { ChartPanel, Donut, Bars } from '../components/shared/charts';
import { financeSummary, months } from '../modules/analytics/metrics';
import { eur, fmtDate, monthKey, pct } from '../lib/util';

export default function FinancesPage() {
  const s = useGame();
  const [channel, setChannel] = useState('all');
  const [month, setMonth] = useState('all');
  const ch = channel === 'all' ? null : channel;
  const mo = month === 'all' ? null : month;
  const f = useMemo(() => financeSummary(s, ch, mo), [s.ledger, ch, mo]); // eslint-disable-line
  const expenseCats = Object.entries(f.byCat).filter(([, v]) => v < 0).map(([name, v]) => ({ name, value: Math.round(-v) }));
  const monthly = months(s).map((m) => {
    const x = financeSummary(s, ch, m);
    return { month: m, income: Math.round(x.income), expenses: Math.round(x.expenses), profit: Math.round(x.profit) };
  });
  const perVideo = s.projects.filter((p) => p.status === 'Published' && (!ch || p.channelId === ch)).map((p) => {
    const v = s.videos.find((x) => x.id === p.videoId);
    return { p, v, roi: p.cost ? (((v?.revenue ?? 0) - p.cost) / p.cost) * 100 : 0 };
  });

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader
        title="Finances"
        subtitle={<span className="flex items-center gap-2">Simulated P&L in EUR {s.demoMode && <DemoBadge label="INCLUDES DEMO DATA" />}</span>}
        actions={<>
          <select className="input !w-auto !py-1.5 text-[13px]" value={channel} onChange={(e) => setChannel(e.target.value)}>
            <option value="all">All channels (incl. company overhead)</option>
            {s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select className="input !w-auto !py-1.5 text-[13px]" value={month} onChange={(e) => setMonth(e.target.value)}>
            <option value="all">All months</option>
            {months(s).map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </>}
      />
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatCard label="Balance" value={eur(s.company.balance)} color="#22c55e" />
        <StatCard label="Revenue" value={eur(f.income)} color="#22c55e" />
        <StatCard label="Expenses" value={eur(f.expenses)} color="#f43f5e" />
        <StatCard label="Profit" value={<span className={f.profit < 0 ? 'text-rose-400' : 'text-emerald-300'}>{eur(f.profit)}</span>} color="#a855f7" />
        <StatCard label="Profit margin" value={pct(f.margin)} sub={`ROI ${pct(f.roi)}`} color="#f59e0b" />
        <StatCard label="Break-even" value={<span className="text-base">{f.breakEven}</span>} sub={`${eur(f.dailyIncome, 2)} erin / ${eur(f.dailyExpense, 2)} eruit per dag`} color="#22d3ee" />
      </div>
      {ch && <p className="mt-2 text-[13px] text-slate-500">Channel view shows only costs and revenue attributed to this channel; salaries, subscriptions and software are company overhead.</p>}

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <ChartPanel title="Monthly P&L"><Bars data={monthly} x="month" keys={[{ key: 'income', color: '#22c55e', name: 'Income' }, { key: 'expenses', color: '#f43f5e', name: 'Expenses' }, { key: 'profit', color: '#a855f7', name: 'Profit' }]} fmt={(v) => `€${v}`} /></ChartPanel>
        <ChartPanel title="Expense breakdown">{expenseCats.length ? <Donut data={expenseCats} fmt={(v) => eur(v)} /> : <div className="text-sm text-slate-500">No expenses in this period.</div>}</ChartPanel>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_1fr]">
        <div className="panel p-4">
          <div className="mb-3 text-sm font-semibold text-white">Categories</div>
          <div className="space-y-1.5 text-sm">
            {['Ad Revenue', 'Rewards', 'Production', 'Freelancers', 'Salaries', 'AI Subscriptions', 'Software', 'Hiring', 'Training', 'Upgrades'].map((cat) => (
              <div key={cat} className="flex justify-between border-b border-hq-line/40 py-1"><span className="text-slate-300">{cat}</span><span className={(f.byCat[cat] ?? 0) < 0 ? 'text-rose-300' : 'text-emerald-300'}>{eur(f.byCat[cat] ?? 0, 2)}</span></div>
            ))}
          </div>
          <div className="mt-4 text-sm font-semibold text-white">Video ROI</div>
          <div className="mt-2 space-y-1 text-[13px]">
            {perVideo.length === 0 && <div className="text-slate-500">Publish a video to track its ROI.</div>}
            {perVideo.map(({ p, v, roi }) => (
              <div key={p.id} className="flex justify-between gap-2"><span className="truncate text-slate-300">{p.title}</span><span className="shrink-0 text-slate-400">cost {eur(p.cost)} · rev {eur(v?.revenue ?? 0, 2)} · <span className={roi < 0 ? 'text-rose-300' : 'text-emerald-300'}>{pct(roi, 0)}</span></span></div>
            ))}
          </div>
        </div>
        <div className="panel p-4">
          <div className="mb-3 text-sm font-semibold text-white">Ledger ({f.rows.length})</div>
          <div className="max-h-[440px] overflow-y-auto">
            <table className="w-full text-[13px]">
              <thead className="sticky top-0 bg-hq-panel"><tr className="text-left uppercase tracking-wider text-slate-500"><th className="py-1.5">Date</th><th>Category</th><th>Note</th><th className="text-right">Amount</th></tr></thead>
              <tbody>
                {[...f.rows].reverse().slice(0, 200).map((r) => (
                  <tr key={r.id} className="border-t border-hq-line/40 text-slate-300">
                    <td className="whitespace-nowrap py-1.5 text-slate-500" title={monthKey(r.day)}>{fmtDate(r.day)}</td>
                    <td>{r.category}</td>
                    <td className="max-w-[220px] truncate">{r.note}</td>
                    <td className={`text-right ${r.amount < 0 ? 'text-rose-300' : 'text-emerald-300'}`}>{eur(r.amount, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
