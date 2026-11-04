import { useRef, useState } from 'react';
import { Download, Upload, RotateCcw, CloudUpload, CloudDownload } from 'lucide-react';
import { useGame } from '../store/useGame';
import { PageHeader } from '../components/ui';
import { integrationOverview, YouTubeDataAdapter } from '../services/adapters';
import { SupabaseAdapter } from '../services/persistence/storage';
import type { GameData } from '../store/state';
import type { IntegrationSettings } from '../types';

const STATUS = {
  connected: 'bg-emerald-500/15 text-emerald-300',
  simulation: 'bg-cyan-500/15 text-cyan-300',
  stub: 'bg-amber-500/15 text-amber-300',
  not_configured: 'bg-slate-600/30 text-slate-400',
};

function snapshot(): GameData {
  const st = useGame.getState() as unknown as Record<string, unknown>;
  const keys: (keyof GameData)[] = ['version', 'tick', 'company', 'agents', 'tasks', 'projects', 'videos', 'channels', 'stats', 'ledger', 'posts', 'notifications', 'achievements', 'missions', 'missionDay', 'upgrades', 'warCases', 'modifiers', 'settings', 'demoMode'];
  return JSON.parse(JSON.stringify(Object.fromEntries(keys.map((k) => [k, st[k]])))) as GameData;
}

export default function SettingsPage() {
  const s = useGame();
  const [f, setF] = useState<IntegrationSettings>({ ...s.settings });
  const [ytId, setYtId] = useState('');
  const [ytOut, setYtOut] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const ov = integrationOverview(s.settings);
  const set = (k: keyof IntegrationSettings, v: string) => setF({ ...f, [k]: v });
  const supa = new SupabaseAdapter(s.settings.supabaseUrl, s.settings.supabaseAnonKey);

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Settings" subtitle="Integrations, data and simulation." />
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">Integration status</div>
          <div className="space-y-2">
            {ov.map((i) => (
              <div key={i.id} className="rounded-xl bg-white/[.03] p-3">
                <div className="flex items-center justify-between gap-2"><span className="font-semibold text-white">{i.name}</span><span className={`chip ${STATUS[i.status]}`}>{i.status.replace('_', ' ')}</span></div>
                <div className="text-xs text-slate-400">{i.purpose} — {i.note}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-slate-500">External publishing (YouTube, Threads) is never performed automatically. Publishing in this game always stays in the local simulation and requires your explicit confirmation.</p>
        </div>

        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">API credentials</div>
          <p className="mb-3 rounded-lg bg-amber-500/10 p-2.5 text-xs text-amber-200">Keys are stored only in this browser's local storage and sent directly to the provider you choose. Use restricted keys and never share your save file if it contains keys.</p>
          <div className="grid gap-3">
            <div>
              <label className="label">Agent AI provider</label>
              <select className="input" value={f.llmProvider} onChange={(e) => set('llmProvider', e.target.value)}>
                <option value="simulation">Local simulation (no API)</option>
                <option value="anthropic">Anthropic Claude</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>
            <div className="grid grid-cols-[1fr_170px] gap-2">
              <div><label className="label">Anthropic API key</label><input className="input" type="password" value={f.anthropicKey} onChange={(e) => set('anthropicKey', e.target.value)} placeholder="sk-ant-…" autoComplete="off" /></div>
              <div><label className="label">Claude model</label><input className="input" value={f.anthropicModel} onChange={(e) => set('anthropicModel', e.target.value)} /></div>
            </div>
            <div className="grid grid-cols-[1fr_170px] gap-2">
              <div><label className="label">OpenAI API key</label><input className="input" type="password" value={f.openaiKey} onChange={(e) => set('openaiKey', e.target.value)} placeholder="sk-…" autoComplete="off" /></div>
              <div><label className="label">OpenAI model</label><input className="input" value={f.openaiModel} onChange={(e) => set('openaiModel', e.target.value)} /></div>
            </div>
            <div><label className="label">YouTube Data API key (read-only stats)</label><input className="input" type="password" value={f.youtubeApiKey} onChange={(e) => set('youtubeApiKey', e.target.value)} autoComplete="off" /></div>
            <div className="grid grid-cols-2 gap-2">
              <div><label className="label">Threads access token</label><input className="input" type="password" value={f.threadsToken} onChange={(e) => set('threadsToken', e.target.value)} autoComplete="off" /></div>
              <div><label className="label">Voice API key</label><input className="input" type="password" value={f.elevenLabsKey} onChange={(e) => set('elevenLabsKey', e.target.value)} autoComplete="off" /></div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div><label className="label">Supabase URL</label><input className="input" value={f.supabaseUrl} onChange={(e) => set('supabaseUrl', e.target.value)} placeholder="https://xyz.supabase.co" /></div>
              <div><label className="label">Supabase anon key</label><input className="input" type="password" value={f.supabaseAnonKey} onChange={(e) => set('supabaseAnonKey', e.target.value)} autoComplete="off" /></div>
            </div>
            <button className="btn-primary" onClick={() => { s.updateSettings(f); s.toast('Settings saved locally.', 'success'); }}>Save settings</button>
          </div>
        </div>

        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">YouTube Data API test (read-only)</div>
          <div className="flex gap-2">
            <input className="input" value={ytId} onChange={(e) => setYtId(e.target.value)} placeholder="Channel ID, e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw" />
            <button className="btn-ghost" disabled={!ytId} onClick={async () => {
              try { const r = await new YouTubeDataAdapter(s.settings.youtubeApiKey).fetchChannelStats(ytId); setYtOut(`Subscribers ${r.subscribers.toLocaleString()} · Views ${r.views.toLocaleString()} · Videos ${r.videos}`); }
              catch (e) { setYtOut(`⚠️ ${(e as Error).message}`); }
            }}>Fetch</button>
          </div>
          {ytOut && <div className="mt-2 text-sm text-slate-300">{ytOut}</div>}
        </div>

        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">Save data</div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-ghost text-xs" onClick={() => {
              const data = snapshot();
              data.settings = { ...data.settings, anthropicKey: '', openaiKey: '', youtubeApiKey: '', threadsToken: '', elevenLabsKey: '', supabaseAnonKey: '' };
              const url = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'application/json' }));
              const a = document.createElement('a'); a.href = url; a.download = `faceless-hq-save-day${Math.floor(s.tick / 24)}.json`; a.click(); URL.revokeObjectURL(url);
            }}><Download size={14} />Export save (keys stripped)</button>
            <button className="btn-ghost text-xs" onClick={() => fileRef.current?.click()}><Upload size={14} />Import save</button>
            <input ref={fileRef} type="file" accept="application/json" className="hidden" onChange={async (e) => {
              const file = e.target.files?.[0]; if (!file) return;
              try {
                const data = JSON.parse(await file.text()) as GameData;
                if (!data.agents || !data.channels) throw new Error('Not a valid save file');
                s.askConfirm({ title: 'Import save?', body: 'Your current progress will be replaced by the imported save.', confirmLabel: 'Replace progress', danger: true, onConfirm: () => { s.importSave({ ...data, settings: { ...data.settings, ...s.settings } }); s.toast('Save imported.', 'success'); } });
              } catch (err) { s.toast(`Import failed: ${(err as Error).message}`, 'warning'); }
              e.target.value = '';
            }} />
            <button className="btn-ghost text-xs" disabled={!supa.isConfigured()} onClick={async () => { try { await supa.save('default', snapshot()); s.toast('Saved to Supabase.', 'success'); } catch (e) { s.toast((e as Error).message, 'warning'); } }}><CloudUpload size={14} />Save to Supabase</button>
            <button className="btn-ghost text-xs" disabled={!supa.isConfigured()} onClick={async () => { try { const d = await supa.load('default'); if (d) { s.importSave(d as GameData); s.toast('Loaded from Supabase.', 'success'); } else s.toast('No cloud save found.', 'warning'); } catch (e) { s.toast((e as Error).message, 'warning'); } }}><CloudDownload size={14} />Load from Supabase</button>
          </div>
          <p className="mt-2 text-xs text-slate-500">Progress autosaves to this browser. Supabase requires the table in <code>supabase/schema.sql</code>.</p>
          <div className="mt-5 border-t border-hq-line/60 pt-4">
            <div className="mb-2 text-sm font-semibold text-rose-300">Danger zone</div>
            <button className="btn-danger text-xs" onClick={() => s.askConfirm({ title: 'Reset the whole company?', body: 'All progress, agents, channels and history will be permanently replaced with a fresh demo company. This cannot be undone.', confirmLabel: 'Reset everything', danger: true, onConfirm: () => { s.resetGame(); s.toast('Company reset to demo state.', 'info'); } })}><RotateCcw size={14} />Reset game</button>
          </div>
        </div>
      </div>
    </div>
  );
}
