import type { GameData } from '../../store/state';
import { dayOf, fmtDate, monthKey } from '../../lib/util';
import { PIPELINE } from '../workflows/pipeline';

type D = Pick<GameData, 'channels' | 'stats' | 'ledger' | 'videos' | 'projects' | 'agents' | 'tasks' | 'tick'>;

export function kpis(d: D) {
  const views = d.channels.reduce((s, c) => s + c.views, 0);
  const subs = d.channels.reduce((s, c) => s + c.subscribers, 0);
  const revenue = d.ledger.filter((l) => l.amount > 0 && l.category === 'Ad Revenue').reduce((s, l) => s + l.amount, 0);
  const expenses = -d.ledger.filter((l) => l.amount < 0).reduce((s, l) => s + l.amount, 0);
  const recent = d.stats.filter((s) => s.day > dayOf(d.tick) - 8 && s.ctr > 0);
  const ctr = recent.length ? recent.reduce((s, x) => s + x.ctr, 0) / recent.length : 0;
  const avd = recent.length ? recent.reduce((s, x) => s + x.avd, 0) / recent.length : 0;
  const monetViews = d.stats.filter((s) => s.revenue > 0).reduce((s, x) => s + x.views, 0);
  const rpm = monetViews ? (d.stats.reduce((s, x) => s + x.revenue, 0) / monetViews) * 1000 : d.channels.reduce((s, c) => s + c.rpm, 0) / Math.max(1, d.channels.length);
  return {
    views, subs, revenue, expenses, profit: revenue - expenses, ctr, avd, rpm,
    activeAgents: d.agents.filter((a) => a.state === 'working' || a.state === 'meeting').length,
    activeProjects: d.projects.filter((p) => p.status === 'Active' || p.status.startsWith('Awaiting')).length,
    pendingApprovals: d.projects.filter((p) => p.status === 'Awaiting Approval' || p.status === 'Awaiting Publish').length + d.tasks.filter((t) => t.kind === 'manual' && t.status === 'Review').length,
  };
}

export function dailySeries(d: D, channelId: string | null, days = 30) {
  const today = dayOf(d.tick);
  const out: { day: number; label: string; views: number; subs: number; revenue: number; expenses: number; ctr: number; avd: number }[] = [];
  for (let day = Math.max(0, today - days); day < today; day++) {
    const st = d.stats.filter((s) => s.day === day && (!channelId || s.channelId === channelId));
    const exp = -d.ledger.filter((l) => l.day === day && l.amount < 0 && (!channelId || l.channelId === channelId || l.channelId === null)).reduce((s, l) => s + l.amount, 0);
    const withCtr = st.filter((s) => s.ctr > 0);
    out.push({
      day, label: fmtDate(day).slice(0, 6),
      views: st.reduce((s, x) => s + x.views, 0),
      subs: st.reduce((s, x) => s + x.subs, 0),
      revenue: +st.reduce((s, x) => s + x.revenue, 0).toFixed(2),
      expenses: +exp.toFixed(2),
      ctr: withCtr.length ? +(withCtr.reduce((s, x) => s + x.ctr, 0) / withCtr.length).toFixed(2) : 0,
      avd: withCtr.length ? +(withCtr.reduce((s, x) => s + x.avd, 0) / withCtr.length).toFixed(1) : 0,
    });
  }
  return out;
}

export function productionStats(d: D) {
  return PIPELINE.map((s) => {
    const done = d.tasks.filter((t) => t.stage === s.id && t.status === 'Completed');
    const q = done.filter((t) => t.quality != null);
    return {
      stage: s.label,
      completed: done.length,
      active: d.tasks.filter((t) => t.stage === s.id && ['Assigned', 'In Progress', 'Review', 'Pending'].includes(t.status)).length,
      rejected: d.tasks.filter((t) => t.stage === s.id && t.status === 'Rejected').length,
      quality: q.length ? Math.round(q.reduce((a, t) => a + (t.quality ?? 0), 0) / q.length) : 0,
    };
  });
}

export function months(d: Pick<GameData, 'ledger'>) {
  return Array.from(new Set(d.ledger.map((l) => monthKey(l.day)))).sort();
}

export function financeSummary(d: Pick<GameData, 'ledger' | 'videos' | 'projects'>, channelId: string | null, month: string | null) {
  const rows = d.ledger.filter((l) => (!channelId || l.channelId === channelId || (l.channelId === null && !channelId)) && (!month || monthKey(l.day) === month));
  const byCat: Record<string, number> = {};
  rows.forEach((r) => (byCat[r.category] = (byCat[r.category] ?? 0) + r.amount));
  const income = rows.filter((r) => r.amount > 0).reduce((s, r) => s + r.amount, 0);
  const expenses = -rows.filter((r) => r.amount < 0).reduce((s, r) => s + r.amount, 0);
  const profit = income - expenses;
  const margin = income ? (profit / income) * 100 : 0;
  const roi = expenses ? (profit / expenses) * 100 : 0;
  // break-even: days of average daily income needed to cover cumulative expense
  const days = new Set(rows.map((r) => r.day)).size || 1;
  const dailyIncome = income / days;
  const dailyExpense = expenses / days;
  const breakEven = dailyIncome > dailyExpense ? 'Reached / profitable' : dailyIncome > 0 ? `Needs ${(dailyExpense / dailyIncome).toFixed(1)}× current income` : 'No revenue yet';
  return { rows, byCat, income, expenses, profit, margin, roi, breakEven, dailyIncome, dailyExpense };
}
