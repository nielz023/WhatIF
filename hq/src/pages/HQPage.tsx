import { Component, lazy, Suspense, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import { useGame } from '../store/useGame';
import { Avatar, DemoBadge } from '../components/ui';
import PipelineStepper from '../components/shared/Pipeline';
import { stageById } from '../modules/workflows/pipeline';
import { deptById } from '../modules/departments/departments';
import { relTime } from '../lib/util';

const OfficeScene = lazy(() => import('../components/office/OfficeScene'));

class OfficeBoundary extends Component<{ children: ReactNode }, { err: boolean }> {
  state = { err: false };
  static getDerivedStateFromError() { return { err: true }; }
  componentDidCatch(e: unknown) { console.warn('[HQ] 3D-kantoor fout', e); }
  render() {
    return this.state.err
      ? <div className="flex h-full items-center justify-center p-6 text-center text-slate-400">Het 3D-kantoor kon niet laden op dit apparaat. De rest van het HQ werkt gewoon.</div>
      : this.props.children;
  }
}

export default function HQPage() {
  const s = useGame();
  const active = s.projects.filter((p) => p.status !== 'Published' && p.status !== 'Cancelled').slice(0, 5);
  const approvals = s.projects.filter((p) => p.status === 'Awaiting Approval' || p.status === 'Awaiting Publish');
  const feed = s.posts.slice(0, 4);
  const counts = { working: s.agents.filter((a) => a.state === 'working').length, meeting: s.agents.filter((a) => a.state === 'meeting').length, idle: s.agents.filter((a) => a.state === 'idle').length };

  return (
    <div className="relative h-full w-full">
      <OfficeBoundary>
        <Suspense fallback={<div className="flex h-full items-center justify-center text-slate-400">Kantoor wordt gebouwd…</div>}>
          <OfficeScene />
        </Suspense>
      </OfficeBoundary>

      {/* title */}
      <div className="pointer-events-none absolute left-4 top-3 select-none">
        <div className="font-display text-2xl font-bold tracking-tight text-white drop-shadow-[0_0_20px_rgba(99,102,241,.6)] md:text-3xl">DRIFTMARK <span className="text-gradient">STUDIO</span></div>
        <div className="mt-1 flex items-center gap-2 text-[13px] text-slate-400">
          <span><span className="text-emerald-400">●</span> {counts.working} working</span>
          <span><span className="text-sky-400">●</span> {counts.meeting} in meetings</span>
          <span><span className="text-slate-400">●</span> {counts.idle} idle</span>
          {s.demoMode && <DemoBadge />}
        </div>
        <div className="mt-1 text-[13px] text-slate-500">Click a room to open its dashboard · click an employee for their profile · drag to rotate, scroll to zoom</div>
      </div>

      {/* pipeline panel */}
      <motion.div initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} className="panel absolute bottom-20 left-3 hidden w-[330px] p-3 lg:block">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-[13px] font-bold uppercase tracking-wider text-slate-300">Production pipeline</span>
          <button className="text-[13px] text-sky-300 hover:text-white" onClick={() => s.setPage('projects')}>All projects →</button>
        </div>
        <div className="space-y-2">
          {active.length === 0 && <div className="text-[13px] text-slate-500">No active projects. Start a new video!</div>}
          {active.map((p) => {
            const st = stageById(p.stage);
            return (
              <button key={p.id} onClick={() => s.selectProject(p.id)} className="w-full rounded-xl bg-white/[.03] p-2 text-left hover:bg-white/[.07]">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-[13px] font-semibold text-white">{p.title}</span>
                  <span className="shrink-0 text-[12px]" style={{ color: deptById(st.department).color }}>{p.status === 'Active' ? st.label : p.status}</span>
                </div>
                <div className="mt-1.5"><PipelineStepper project={p} small /></div>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* approvals + feed */}
      {!s.selectedDept && !s.selectedAgentId && !s.selectedProjectId && (
        <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} className="absolute right-3 top-3 hidden w-[310px] space-y-3 xl:block">
          {approvals.length > 0 && (
            <div className="panel border-amber-400/40 p-3">
              <div className="mb-2 text-[13px] font-bold uppercase tracking-wider text-amber-300">⏳ Waiting for you ({approvals.length})</div>
              {approvals.slice(0, 3).map((p) => (
                <button key={p.id} onClick={() => s.selectProject(p.id)} className="mb-1.5 flex w-full items-center justify-between rounded-lg bg-amber-500/10 px-2.5 py-1.5 text-left text-[13px] hover:bg-amber-500/20">
                  <span className="truncate text-white">{p.title}</span><span className="ml-2 shrink-0 text-amber-300">{p.status === 'Awaiting Approval' ? 'Approve' : 'Publish'}</span>
                </button>
              ))}
            </div>
          )}
          <div className="panel p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-[13px] font-bold uppercase tracking-wider text-slate-300">Live on Threads</span>
              <button className="text-[13px] text-sky-300 hover:text-white" onClick={() => s.setPage('threads')}>Open →</button>
            </div>
            <div className="space-y-2.5">
              {feed.map((p) => {
                const a = s.agents.find((x) => x.id === p.authorId);
                return (
                  <div key={p.id} className="flex gap-2">
                    <Avatar agent={a} size={26} />
                    <div className="min-w-0">
                      <div className="text-[13px]"><span className="font-semibold text-white">{a?.name ?? 'CEO'}</span> <span className="text-slate-500">· {relTime(p.tick, s.tick)}</span></div>
                      <div className="line-clamp-2 text-[13px] text-slate-300">{p.content}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
