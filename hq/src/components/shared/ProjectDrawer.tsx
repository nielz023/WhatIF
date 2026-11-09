import { useState } from 'react';
import { CheckCircle2, Rocket, Undo2, XCircle } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Drawer, PriorityBadge, StatusBadge } from '../ui';
import PipelineStepper from './Pipeline';
import TaskCard from './TaskCard';
import { PIPELINE, stageById } from '../../modules/workflows/pipeline';
import { projectQuality } from '../../modules/tasks/engine';
import { fmtTick } from '../../lib/util';
import type { StageId } from '../../types';

export default function ProjectDrawer() {
  const s = useGame();
  const p = s.projects.find((x) => x.id === s.selectedProjectId);
  const [rejectTo, setRejectTo] = useState<StageId>('script');
  const [reason, setReason] = useState('');
  if (!p) return <Drawer open={false} onClose={() => s.selectProject(null)}>{null}</Drawer>;
  const ch = s.channels.find((c) => c.id === p.channelId);
  const tasks = p.taskIds.map((id) => s.tasks.find((t) => t.id === id)).filter(Boolean).reverse();
  const video = s.videos.find((v) => v.id === p.videoId);
  const q = projectQuality(p);

  const confirmPublish = () =>
    s.askConfirm({
      title: 'Uploadpakket laten klaarzetten?',
      body: `"${p.title}" gaat naar de upload.\n\nClaude krijgt de opdracht om titel, beschrijving, tags en thumbnail klaar te maken. Het uploaden naar YouTube doe je zelf in Studio.\n\nDit kun je daarna niet meer terugdraaien.`,
      confirmLabel: 'Klaarzetten',
      onConfirm: () => s.publishProject(p.id),
    });

  return (
    <Drawer open onClose={() => s.selectProject(null)} title="Project" width={600}>
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-orange-500/20 text-2xl">🎬</div>
        <div className="min-w-0 flex-1">
          <div className="font-display text-lg font-bold leading-snug text-white">{p.title}</div>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-[13px] text-slate-400">
            <StatusBadge status={p.status} /><PriorityBadge p={p.priority} />
          </div>
        </div>
      </div>
      <div className="mt-4"><PipelineStepper project={p} /></div>
      {/* geen kosten of inkomsten meer: geld speelt in het kantoor geen rol (niels 2026-11-06) */}
      <div className="mt-3 grid grid-cols-2 gap-2 text-center text-[13px]">
        <div className="rounded-xl bg-white/[.03] p-2"><div className="text-slate-500">Keer teruggestuurd</div><div className="font-bold text-white">{p.rejections}</div></div>
        <div className="rounded-xl bg-white/[.03] p-2"><div className="text-slate-500">Taken</div><div className="font-bold text-white">{p.taskIds.length}</div></div>
      </div>

      {p.status === 'Awaiting Approval' && (
        <div className="mt-4 rounded-2xl border border-amber-400/40 bg-amber-500/10 p-4">
          <div className="font-semibold text-amber-200">Wacht op jouw akkoord</div>
          <p className="mt-1 text-[13px] text-amber-100/80">Bekijk wat er hieronder is opgeleverd. Keur goed om naar de upload te gaan, of stuur het terug naar een afdeling met je opmerking.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button className="btn-success text-[13px]" onClick={() => s.approveProject(p.id)}><CheckCircle2 size={14} />Goedkeuren</button>
          </div>
          <div className="mt-3 grid gap-2 sm:grid-cols-[150px_1fr_auto]">
            <select className="input !py-1.5 text-[13px]" value={rejectTo} onChange={(e) => setRejectTo(e.target.value as StageId)}>
              {PIPELINE.filter((x) => !x.manual).map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
            </select>
            <input className="input !py-1.5 text-[13px]" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Wat moet er anders?" />
            <button className="btn-danger text-[13px]" onClick={() => { s.rejectProject(p.id, rejectTo, reason || 'niels wil aanpassingen'); setReason(''); }}><Undo2 size={14} />Terugsturen</button>
          </div>
        </div>
      )}
      {p.status === 'Awaiting Publish' && (
        <div className="mt-4 rounded-2xl border border-cyan-400/40 bg-cyan-500/10 p-4">
          <div className="font-semibold text-cyan-200">Klaar voor upload</div>
          <p className="mt-1 text-[13px] text-cyan-100/80">Claude zet titel, beschrijving, tags en thumbnail klaar. Het uploaden naar YouTube doe je zelf in YouTube Studio.</p>
          <button className="btn-primary mt-3 text-[13px]" onClick={confirmPublish}><Rocket size={14} />Uploadpakket klaarzetten…</button>
        </div>
      )}

      <div className="label mt-5">Taken en opleveringen</div>
      <div className="space-y-2">{tasks.map((t) => t && <TaskCard key={t.id} task={t} />)}</div>

      <div className="label mt-5">Tijdlijn</div>
      <div className="space-y-1 border-l border-hq-line pl-3">
        {[...p.history].reverse().map((h, i) => (
          <div key={i} className="text-[13px]"><span className="text-slate-500">{fmtTick(h.tick)}</span> <span className="text-slate-300">{h.text}</span></div>
        ))}
      </div>

      {!['Published', 'Cancelled'].includes(p.status) && (
        <button className="btn-danger mt-5 text-[13px]" onClick={() => s.askConfirm({ title: 'Project stoppen?', body: `"${p.title}" wordt gestopt en alle open taken worden gesloten. Claude krijgt de opdracht er niet verder aan te werken.`, confirmLabel: 'Stoppen', danger: true, onConfirm: () => s.cancelProject(p.id) })}>
          <XCircle size={14} />Project stoppen
        </button>
      )}
      <p className="mt-3 text-[13px] text-slate-500">Huidige stap: {p.status === 'Published' ? 'Online' : stageById(p.stage).label}</p>
    </Drawer>
  );
}
