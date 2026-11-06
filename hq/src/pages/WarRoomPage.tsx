import { useState } from 'react';
import { ShieldAlert, Search } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Avatar, Empty, PageHeader, Progress } from '../components/ui';
import { ISSUE_META } from '../modules/warroom/warroom';
import { dailySeries } from '../modules/analytics/metrics';
import { fmtTick } from '../lib/util';
import type { WarIssueType } from '../types';

export default function WarRoomPage() {
  const s = useGame();
  const [type, setType] = useState<WarIssueType>('low_ctr');
  const [channel, setChannel] = useState<string>(s.channels[0]?.id ?? '');
  const series = dailySeries(s, null, 14);
  const wk = (k: 'views') => [series.slice(-7).reduce((a, x) => a + x[k], 0), series.slice(0, 7).reduce((a, x) => a + x[k], 0)];
  const [v1, v0] = wk('views');
  const ctrNow = series.filter((x) => x.ctr).slice(-7);
  const ctr = ctrNow.length ? ctrNow.reduce((a, x) => a + x.ctr, 0) / ctrNow.length : 0;
  const avd = ctrNow.length ? ctrNow.reduce((a, x) => a + x.avd, 0) / ctrNow.length : 0;
  const overdue = s.projects.filter((p) => p.status === 'Active' && p.deadlineTick < s.tick).length;
  const signals: { type: WarIssueType; level: 'ok' | 'warn' | 'bad'; text: string }[] = [
    { type: 'declining_views', level: v0 && v1 < v0 * 0.9 ? 'bad' : v0 && v1 < v0 ? 'warn' : 'ok', text: `Weergaven 7 dagen: ${v1.toLocaleString('nl-NL')} (${v0 ? (((v1 - v0) / v0) * 100).toFixed(0) : '—'}% t.o.v. vorige week)` },
    { type: 'low_ctr', level: ctr < 4 ? 'bad' : ctr < 4.8 ? 'warn' : 'ok', text: `Gem. CTR: ${ctr.toFixed(2)}% (doel 4,5%)` },
    { type: 'poor_retention', level: avd < 38 ? 'bad' : avd < 44 ? 'warn' : 'ok', text: `Gem. kijkduur: ${avd.toFixed(1)}%` },
    { type: 'production_delays', level: overdue >= 2 ? 'bad' : overdue === 1 ? 'warn' : 'ok', text: `${overdue} projecten te laat` },
  ];
  const lvl = { ok: 'text-emerald-300 border-emerald-500/30', warn: 'text-amber-300 border-amber-500/30', bad: 'text-rose-300 border-rose-500/40' };
  // geen inkomsten-check en geen kosten meer: plannen kosten niets en worden nooit tegengehouden (niels 2026-11-06)
  const issues = Object.entries(ISSUE_META).filter(([k]) => k !== 'falling_revenue');
  const cases = s.warCases.filter((w) => w.type !== 'falling_revenue');

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28" style={{ background: 'radial-gradient(900px 500px at 50% 0%, rgba(239,68,68,.10), transparent)' }}>
      <PageHeader title="Crisiskamer" subtitle="Het team zoekt uit waarom iets minder gaat en stelt een plan voor. Er gebeurt niets zonder jouw akkoord." />
      <div className="grid gap-3 md:grid-cols-4">
        {signals.map((sg) => (
          <button key={sg.type} onClick={() => setType(sg.type)} className={`panel border p-3 text-left ${lvl[sg.level]} ${type === sg.type ? 'ring-1 ring-rose-400/60' : ''}`}>
            <div className="text-xl">{ISSUE_META[sg.type].icon}</div>
            <div className="mt-1 text-sm font-semibold text-white">{ISSUE_META[sg.type].label}</div>
            <div className="mt-0.5 text-[13px]">{sg.text}</div>
          </button>
        ))}
      </div>

      <div className="panel mt-4 flex flex-wrap items-end gap-3 border-rose-500/30 p-4">
        <div><label className="label">Probleem</label><select className="input !w-56" value={type} onChange={(e) => setType(e.target.value as WarIssueType)}>{issues.map(([k, m]) => <option key={k} value={k}>{m.icon} {m.label}</option>)}</select></div>
        <div><label className="label">Voor</label><select className="input !w-56" value={channel} onChange={(e) => setChannel(e.target.value)}><option value="">Alle kanalen</option>{s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
        <button className="btn-danger !py-2.5" onClick={() => { s.openWarCase(type, channel || null); s.toast('Crisiskamer bijeengeroepen. De analyse staat er over ongeveer 6 uur.', 'info'); }}><ShieldAlert size={15} />Crisiskamer bijeenroepen</button>
      </div>

      <div className="mt-5 space-y-3">
        {cases.length === 0 && <Empty>Nog geen zaken. Kies hierboven een probleem en roep de crisiskamer bijeen.</Empty>}
        {cases.map((w) => {
          const agents = w.agentIds.map((id) => s.agents.find((a) => a.id === id)).filter(Boolean);
          const pctDone = w.status === 'Investigating' ? Math.min(100, ((s.tick - w.openedTick) / (w.readyTick - w.openedTick)) * 100) : 100;
          return (
            <div key={w.id} className={`panel p-4 ${w.status === 'Ready' ? 'border-rose-400/50 shadow-[0_0_30px_rgba(244,63,94,.15)]' : ''}`}>
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-2xl">{ISSUE_META[w.type].icon}</span>
                <div className="flex-1">
                  <div className="font-semibold text-white">{w.title}</div>
                  <div className="text-[13px] text-slate-400">Geopend {fmtTick(w.openedTick)} · {w.evidence}</div>
                </div>
                <div className="flex -space-x-2">{agents.map((a) => a && <Avatar key={a.id} agent={a} size={28} />)}</div>
                <span className={`chip ${w.status === 'Ready' ? 'bg-rose-500/20 text-rose-200' : w.status === 'Resolved' ? 'bg-emerald-500/15 text-emerald-300' : w.status === 'Dismissed' ? 'bg-slate-600/30 text-slate-400' : 'bg-sky-500/15 text-sky-300'}`}>{w.status}</span>
              </div>
              {w.status === 'Investigating' && <div className="mt-3"><div className="mb-1 flex items-center gap-1.5 text-[13px] text-sky-300"><Search size={12} className="animate-pulse" />Het team verzamelt gegevens…</div><Progress value={pctDone} color="#ef4444" /></div>}
              {w.status !== 'Investigating' && (
                <>
                  <div className="mt-3 space-y-1.5">{w.analysis.map((l, i) => <div key={i} className="rounded-lg bg-white/[.03] px-3 py-1.5 text-sm text-slate-300">{l}</div>)}</div>
                  <div className="mt-3 grid gap-2 md:grid-cols-2">
                    {w.recommendations.map((r) => (
                      <div key={r.id} className={`rounded-xl border p-3 ${w.chosen === r.id ? 'border-emerald-400/60 bg-emerald-500/10' : 'border-hq-line'}`}>
                        <div className="font-semibold text-white">{r.title}</div>
                        <div className="mt-1 text-[13px] text-slate-400">{r.detail}</div>
                        {w.status === 'Ready' && (
                          <button className="btn-success mt-2 !py-1.5 text-[13px]" onClick={() => s.askConfirm({ title: 'Plan goedkeuren?', body: `"${r.title}" gaat als echte opdracht naar Claude.\n\n${r.detail}`, confirmLabel: 'Plan goedkeuren', onConfirm: () => s.approveRecommendation(w.id, r.id) })}>Plan goedkeuren</button>
                        )}
                        {w.chosen === r.id && <div className="mt-2 text-[13px] text-emerald-300">✓ Goedgekeurd door niels</div>}
                      </div>
                    ))}
                  </div>
                  {w.status === 'Ready' && <button className="btn-ghost mt-3 text-[13px]" onClick={() => s.dismissCase(w.id)}>Zaak sluiten</button>}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
