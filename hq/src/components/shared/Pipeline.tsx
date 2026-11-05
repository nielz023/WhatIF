import { Check } from 'lucide-react';
import type { Project } from '../../types';
import { PIPELINE, stageIndex } from '../../modules/workflows/pipeline';
import { deptById } from '../../modules/departments/departments';

/** Horizontal stepper showing a project's position in the 11-stage pipeline. */
export default function PipelineStepper({ project, small }: { project: Project; small?: boolean }) {
  const cur = project.status === 'Published' ? PIPELINE.length : stageIndex(project.stage);
  return (
    <div className="flex items-center gap-0.5 overflow-x-auto pb-1">
      {PIPELINE.map((s, i) => {
        const done = i < cur;
        const active = i === cur;
        const color = deptById(s.department).color;
        return (
          <div key={s.id} className="flex items-center gap-0.5" title={`${s.label}${project.stageQuality[s.id] != null ? ` · Q${project.stageQuality[s.id]}` : ''}`}>
            <div
              className={`flex items-center justify-center rounded-full font-bold ${small ? 'h-4 w-4 text-[8px]' : 'h-6 w-6 text-[12px]'} ${active ? 'animate-pulse text-white' : done ? 'text-slate-900' : 'text-slate-500'}`}
              style={{ background: done ? color : active ? `${color}55` : '#1e2547', boxShadow: active ? `0 0 12px ${color}` : undefined, border: active ? `1px solid ${color}` : undefined }}
            >
              {done ? <Check size={small ? 9 : 12} /> : i + 1}
            </div>
            {!small && active && <span className="mx-1 whitespace-nowrap text-[13px] font-semibold" style={{ color }}>{s.label}</span>}
            {i < PIPELINE.length - 1 && <div className={`${small ? 'w-1.5' : 'w-3'} h-[2px]`} style={{ background: done ? color : '#1e2547' }} />}
          </div>
        );
      })}
    </div>
  );
}
