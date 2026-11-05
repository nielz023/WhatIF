import { useRef, useState } from 'react';
import { Download, Upload, RotateCcw, CloudUpload, CloudDownload } from 'lucide-react';
import { useGame } from '../store/useGame';
import { PageHeader } from '../components/ui';
import { YouTubeDataAdapter } from '../services/adapters';
import { SupabaseAdapter } from '../services/persistence/storage';
import type { GameData } from '../store/state';
import type { IntegrationSettings } from '../types';
import { useTools } from '../services/tools';
import { useLive } from '../services/live';
import { useDb } from '../services/db';
import { useReal } from '../services/real';

type St = 'connected' | 'stub' | 'not_configured';
const LABEL: Record<St, string> = { connected: 'verbonden', stub: 'deels', not_configured: 'niet verbonden' };
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
function useRealConnections() {
  const tools = useTools((x) => x.tools);
  const live = useLive();
  const db = useDb();
  const avail = useReal((x) => x.avail);
  const ok = (k: string): St => (tools[k]?.status === 'ok' ? 'connected' : tools[k]?.status === 'laden' ? 'stub' : 'not_configured');
  const vqc = (tools.vidiqch?.data as Any)?.channels ?? [];
  const drift = vqc.find((c: Any) => /drift/i.test(c.title ?? ''));
  const hf = tools.higgsfield?.data as Any;
  const el = (tools.elevenlabs?.data as Any)?.flows ?? [];
  const bl = live.data.blender;
  const yt = live.data.youtube;
  return [
    { id: 'claude', name: 'Claude (opdrachten)', purpose: 'Denkwerk, scripts, animatie', status: (avail === 'available' ? 'connected' : avail === 'laden' ? 'stub' : 'not_configured') as St, note: avail === 'available' ? 'Echt: wat je in de HQ typt of klikt, voert Claude uit in je project.' : 'Claude luistert nu niet mee; opdrachten wachten in de wachtrij.' },
    { id: 'youtube', name: 'YouTube (via vidIQ)', purpose: 'Kanaalstatistieken lezen', status: (drift ? 'connected' : ok('vidiqch') === 'connected' ? 'stub' : ok('vidiqch')) as St, note: drift ? `Driftmark: ${Number(drift.subscriberCount).toLocaleString('nl-NL')} abonnees, ${Number(drift.viewCount).toLocaleString('nl-NL')} weergaven, ${drift.videoCount} video's. Uploaden doe je zelf in Studio.` : yt?.subscribers != null ? `Laatst bekend: ${yt.subscribers} abonnees (via Claude).` : 'vidIQ wordt nog geladen.' },
    { id: 'threads', name: 'Claude-threads', purpose: 'Wie werkt waaraan', status: (live.source === 'live' ? 'connected' : 'stub') as St, note: live.source === 'live' ? `${live.data.activity.length} threads live uit de projectbestanden, ververst elke minuut.` : 'Laatst bekende stand; live bestand nog niet gelezen.' },
    { id: 'voice', name: 'Stemmen (ElevenLabs v4)', purpose: 'Voice-overs', status: ok('elevenlabs'), note: ok('elevenlabs') === 'connected' ? `Verbonden, ${el.length} recente flows. Claude maakt de stemmen.` : 'ElevenLabs is nog niet bereikbaar vanaf deze pagina; Claude gebruikt hem wel.' },
    { id: 'image', name: 'Beelden (Higgsfield)', purpose: 'Thumbnails en upgrades', status: ok('higgsfield'), note: ok('higgsfield') === 'connected' ? `Verbonden, ${hf?.credits ?? 0} credits (${hf?.subscription_plan_type ?? 'gratis'}). Ook als add-on in Blender.` : 'Higgsfield is nog niet bereikbaar vanaf deze pagina.' },
    { id: 'video', name: 'Blender op je pc', purpose: 'Animatie en renders', status: (bl ? 'connected' : 'stub') as St, note: bl ? `${bl.stand} (bijgewerkt ${bl.bijgewerkt})` : 'Draait via Remote Control op je pc; de animatie-thread zet de stand hier neer.' },
    { id: 'db', name: 'Database (ingebouwd)', purpose: 'Cijfergeschiedenis, logboek, reserve-kopie', status: (db.ready ? 'connected' : db.offline ? 'stub' : 'stub') as St, note: db.ready ? `${db.stats.length} meetpunten, laatste ronde ${db.engine?.lastRun ? new Date(db.engine.lastRun).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam' }) : 'nog niet'}.` : 'Nog niet bereikbaar.' },
    { id: 'files', name: 'Projectbestanden', purpose: 'Opslag van alles', status: (live.source === 'live' ? 'connected' : 'stub') as St, note: 'Scripts, cast, sets en renders staan in de projectbestanden. Je spelvoortgang staat in deze browser.' },
  ];
}

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
  const [ytId, setYtId] = useState('UCJhUg9hdXlhRRc7GBU_nRgg');
  const vqTools = useTools((x) => x.tools);
  const liveYt = useLive((x) => x.data.youtube);
  const [ytOut, setYtOut] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const ov = useRealConnections();
  const set = (k: keyof IntegrationSettings, v: string) => setF({ ...f, [k]: v });
  const supa = new SupabaseAdapter(s.settings.supabaseUrl, s.settings.supabaseAnonKey);

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Settings" subtitle="Integrations, data and simulation." />
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">Echte koppelingen</div>
          <div className="space-y-2">
            {ov.map((i) => (
              <div key={i.id} className="rounded-xl bg-white/[.03] p-3">
                <div className="flex items-center justify-between gap-2"><span className="font-semibold text-white">{i.name}</span><span className={`chip ${STATUS[i.status]}`}>{LABEL[i.status]}</span></div>
                <div className="text-[13px] text-slate-400">{i.purpose} — {i.note}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[13px] text-slate-500">Uploaden naar YouTube gebeurt nooit automatisch: dat doe je zelf in YouTube Studio.</p>
        </div>

        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">API credentials</div>
          <p className="mb-3 rounded-lg bg-amber-500/10 p-2.5 text-[13px] text-amber-200">Keys are stored only in this browser's local storage and sent directly to the provider you choose. Use restricted keys and never share your save file if it contains keys.</p>
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
          <div className="mb-2 text-xs text-slate-400">Geen API-sleutel nodig: zonder sleutel haalt de HQ je cijfers via vidIQ. De ID van Driftmark staat al ingevuld.</div>
          <div className="flex gap-2">
            <input className="input" value={ytId} onChange={(e) => setYtId(e.target.value)} placeholder="Channel ID, e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw" />
            <button className="btn-ghost" disabled={!ytId} onClick={async () => {
              const fmt = (a: number, b: number, c: number, bron: string) => `${Number(a).toLocaleString('nl-NL')} abonnees · ${Number(b).toLocaleString('nl-NL')} weergaven · ${c} video's (${bron})`;
              if (!s.settings.youtubeApiKey) {
                const ch = ((vqTools.vidiqch?.data as Any)?.channels ?? []).find((c: Any) => c.id === ytId || c.channelId === ytId || /drift/i.test(c.title ?? ''));
                if (ch) { setYtOut(fmt(ch.subscriberCount, ch.viewCount, ch.videoCount, 'live via vidIQ')); return; }
                if (liveYt?.subscribers != null) { setYtOut(fmt(liveYt.subscribers, liveYt.views ?? 0, liveYt.videoCount ?? 0, 'laatste ronde van Claude')); return; }
                setYtOut('vidIQ is nog aan het laden. Probeer het over een paar seconden opnieuw.'); return;
              }
              try { const r = await new YouTubeDataAdapter(s.settings.youtubeApiKey).fetchChannelStats(ytId); setYtOut(fmt(r.subscribers, r.views, r.videos, 'YouTube Data API')); }
              catch (e) { setYtOut(`⚠️ ${(e as Error).message}`); }
            }}>Fetch</button>
          </div>
          {ytOut && <div className="mt-2 text-sm text-slate-300">{ytOut}</div>}
        </div>

        <div className="panel p-5">
          <div className="mb-3 font-semibold text-white">Save data</div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-ghost text-[13px]" onClick={() => {
              const data = snapshot();
              data.settings = { ...data.settings, anthropicKey: '', openaiKey: '', youtubeApiKey: '', threadsToken: '', elevenLabsKey: '', supabaseAnonKey: '' };
              const url = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'application/json' }));
              const a = document.createElement('a'); a.href = url; a.download = `faceless-hq-save-day${Math.floor(s.tick / 24)}.json`; a.click(); URL.revokeObjectURL(url);
            }}><Download size={14} />Export save (keys stripped)</button>
            <button className="btn-ghost text-[13px]" onClick={() => fileRef.current?.click()}><Upload size={14} />Import save</button>
            <input ref={fileRef} type="file" accept="application/json" className="hidden" onChange={async (e) => {
              const file = e.target.files?.[0]; if (!file) return;
              try {
                const data = JSON.parse(await file.text()) as GameData;
                if (!data.agents || !data.channels) throw new Error('Not a valid save file');
                s.askConfirm({ title: 'Import save?', body: 'Your current progress will be replaced by the imported save.', confirmLabel: 'Replace progress', danger: true, onConfirm: () => { s.importSave({ ...data, settings: { ...data.settings, ...s.settings } }); s.toast('Save imported.', 'success'); } });
              } catch (err) { s.toast(`Importeren mislukt: ${(err as Error).message}`, 'warning'); }
              e.target.value = '';
            }} />
            <button className="btn-ghost text-[13px]" disabled={!supa.isConfigured()} onClick={async () => { try { await supa.save('default', snapshot()); s.toast('Saved to Supabase.', 'success'); } catch (e) { s.toast((e as Error).message, 'warning'); } }}><CloudUpload size={14} />Save to Supabase</button>
            <button className="btn-ghost text-[13px]" disabled={!supa.isConfigured()} onClick={async () => { try { const d = await supa.load('default'); if (d) { s.importSave(d as GameData); s.toast('Loaded from Supabase.', 'success'); } else s.toast('No cloud save found.', 'warning'); } catch (e) { s.toast((e as Error).message, 'warning'); } }}><CloudDownload size={14} />Load from Supabase</button>
          </div>
          <p className="mt-2 text-[13px] text-slate-500">Progress autosaves to this browser. Supabase requires the table in <code>supabase/schema.sql</code>.</p>
          <div className="mt-5 border-t border-hq-line/60 pt-4">
            <div className="mb-2 text-sm font-semibold text-rose-300">Danger zone</div>
            <button className="btn-danger text-[13px]" onClick={() => s.askConfirm({ title: 'Reset the whole company?', body: 'All progress, agents, channels and history will be permanently replaced with a fresh demo company. This cannot be undone.', confirmLabel: 'Reset everything', danger: true, onConfirm: () => { s.resetGame(); s.toast('Company reset to demo state.', 'info'); } })}><RotateCcw size={14} />Reset game</button>
          </div>
        </div>
      </div>
    </div>
  );
}
