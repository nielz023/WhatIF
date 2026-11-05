import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Heart, MessageCircle, Repeat2, FileText, Send, Info } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Avatar, DemoBadge, PageHeader } from '../components/ui';
import { DEPARTMENTS, deptById } from '../modules/departments/departments';
import { roleById } from '../modules/agents/roles';
import { relTime } from '../lib/util';
import type { ThreadPost } from '../types';

const KIND: Record<ThreadPost['kind'], { label: string; cls: string }> = {
  update: { label: 'Update', cls: 'bg-sky-500/10 text-sky-300' },
  report: { label: 'Report', cls: 'bg-purple-500/10 text-purple-300' },
  handoff: { label: 'Hand-off', cls: 'bg-teal-500/10 text-teal-300' },
  celebration: { label: 'Win', cls: 'bg-amber-500/10 text-amber-300' },
  question: { label: 'Question', cls: 'bg-sky-500/10 text-sky-300' },
  alert: { label: 'Feedback loop', cls: 'bg-rose-500/10 text-rose-300' },
};

export default function ThreadsPage() {
  const s = useGame();
  const [text, setText] = useState('');
  const [filter, setFilter] = useState<string>('all');
  const [openComments, setOpenComments] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const posts = s.posts.filter((p) => filter === 'all' || p.department === filter || (filter === 'reports' && p.kind === 'report'));
  const authorOf = (id: string) => s.agents.find((a) => a.id === id);

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Threads" subtitle={<span className="flex items-center gap-2">Internal company social network <DemoBadge label="INTERNAL · SIMULATED" /></span>} />
      <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
        <div className="mx-auto w-full max-w-2xl">
          <div className="panel mb-4 p-4">
            <div className="flex gap-3">
              <Avatar size={40} />
              <div className="flex-1">
                <textarea className="input min-h-[70px] resize-none" placeholder="Post an update to the whole company…" value={text} onChange={(e) => setText(e.target.value)} maxLength={500} />
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-[13px] text-slate-500">Visible to all agents · never posted externally</span>
                  <button className="btn-primary !py-1.5 text-[13px]" disabled={!text.trim()} onClick={() => { s.createPost(text.trim()); setText(''); }}><Send size={13} />Post</button>
                </div>
              </div>
            </div>
          </div>
          <div className="mb-3 flex flex-wrap gap-1.5">
            {[{ id: 'all', label: 'For you' }, { id: 'reports', label: '📊 Reports' }, ...DEPARTMENTS.map((d) => ({ id: d.id, label: `${d.icon} ${d.short}` }))].map((f) => (
              <button key={f.id} onClick={() => setFilter(f.id)} className={`chip px-3 py-1 ring-1 ${filter === f.id ? 'bg-sky-500/25 text-white ring-sky-400/60' : 'text-slate-400 ring-slate-700'}`}>{f.label}</button>
            ))}
          </div>
          <AnimatePresence initial={false}>
            {posts.slice(0, 60).map((p) => {
              const a = authorOf(p.authorId);
              const d = p.department === 'hq' ? null : deptById(p.department);
              const liked = p.likes.includes('player');
              return (
                <motion.div key={p.id} layout initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="border-b border-hq-line/60 py-4">
                  <div className="flex gap-3">
                    <button onClick={() => a && s.selectAgent(a.id)}><Avatar agent={a} size={42} /></button>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-sm">
                        <span className="font-semibold text-white">{a?.name ?? 'You (CEO)'}</span>
                        <span className="text-[13px] text-slate-500">{a ? roleById(a.role).title : 'Chief Executive'}</span>
                        <span className="text-[13px] text-slate-600">· {relTime(p.tick, s.tick)}</span>
                        {d && <span className="chip text-[12px]" style={{ background: `${d.color}1f`, color: d.color }}>{d.short}</span>}
                        <span className={`chip text-[12px] ${KIND[p.kind].cls}`}>{KIND[p.kind].label}</span>
                        {p.isDemo && <span className="text-[12px] text-amber-300/70">demo</span>}
                      </div>
                      <p className="mt-1 whitespace-pre-line text-[15px] leading-relaxed text-slate-200">{p.content}</p>
                      {p.attachment && (
                        <div className="mt-2 rounded-xl border border-hq-line bg-black/30 p-3">
                          <div className="flex items-center gap-1.5 text-[13px] font-semibold text-purple-300"><FileText size={13} />{p.attachment.title}</div>
                          <pre className="mt-1 max-h-40 overflow-auto whitespace-pre-wrap font-sans text-[13px] text-slate-300">{p.attachment.body}</pre>
                        </div>
                      )}
                      <div className="mt-2 flex items-center gap-5 text-[13px] text-slate-400">
                        <button onClick={() => s.likePost(p.id)} className={`flex items-center gap-1.5 hover:text-rose-400 ${liked ? 'text-rose-400' : ''}`}><Heart size={15} fill={liked ? 'currentColor' : 'none'} />{p.likes.length}</button>
                        <button onClick={() => setOpenComments(openComments === p.id ? null : p.id)} className="flex items-center gap-1.5 hover:text-sky-300"><MessageCircle size={15} />{p.comments.length}</button>
                        <button onClick={() => { s.sharePost(p.id); s.toast('Shared with the whole company.', 'success'); }} className="flex items-center gap-1.5 hover:text-emerald-300"><Repeat2 size={15} />Share</button>
                      </div>
                      {(openComments === p.id || (p.comments.length > 0 && p.comments.length <= 2)) && (
                        <div className="mt-2 space-y-2 border-l border-hq-line pl-3">
                          {p.comments.map((c) => {
                            const ca = authorOf(c.authorId);
                            return <div key={c.id} className="text-[13px]"><span className="font-semibold text-slate-200">{ca?.name ?? 'You (CEO)'}</span> <span className="text-slate-600">{relTime(c.tick, s.tick)}</span><div className="text-slate-300">{c.text}</div></div>;
                          })}
                          {openComments === p.id && (
                            <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (comment.trim()) { s.commentPost(p.id, comment.trim()); setComment(''); } }}>
                              <input className="input !py-1.5 text-[13px]" placeholder="Reply…" value={comment} onChange={(e) => setComment(e.target.value)} />
                              <button className="btn-ghost !py-1 text-[13px]" disabled={!comment.trim()}>Reply</button>
                            </form>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
        <div className="space-y-4">
          <div className="panel p-4">
            <div className="mb-2 text-sm font-semibold text-white">Most active</div>
            {Object.entries(s.posts.reduce<Record<string, number>>((m, p) => ((m[p.authorId] = (m[p.authorId] ?? 0) + 1), m), {}))
              .sort((a, b) => b[1] - a[1]).slice(0, 6).map(([id, n]) => {
                const a = authorOf(id);
                return <button key={id} onClick={() => a && s.selectAgent(a.id)} className="flex w-full items-center gap-2 py-1.5 text-left text-sm"><Avatar agent={a} size={26} /><span className="flex-1 truncate text-slate-200">{a?.name ?? 'You (CEO)'}</span><span className="text-[13px] text-slate-500">{n} posts</span></button>;
              })}
          </div>
          <div className="panel p-4 text-[13px] text-slate-400">
            <div className="mb-1 flex items-center gap-1.5 font-semibold text-slate-200"><Info size={13} />About this feed</div>
            Threads is an internal, simulated feed where agents share updates, hand-offs and reports. A <code className="text-cyan-300">ThreadsAdapter</code> for the real Meta Threads API is prepared in <code className="text-cyan-300">src/services/adapters.ts</code> but is <b>not connected</b> — nothing here is published externally.
          </div>
        </div>
      </div>
    </div>
  );
}
