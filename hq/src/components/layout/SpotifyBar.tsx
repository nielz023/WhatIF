/**
 * MUZIEKBALK (niels 2026-11-06: "spotify koppelen, bovenin een muziekbalkje").
 * Leest via je eigen Spotify-koppeling in claude.ai wat er nu speelt (mcp-capability).
 * De koppeling kan niet afspelen/pauzeren/overslaan; wel opslaan in je bibliotheek (hartje).
 */
import { useEffect, useRef, useState } from 'react';
import { Heart, Music2 } from 'lucide-react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let mcpP: Promise<any> | null = null;
function getMcp() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if (!mcpP) mcpP = (async () => { try { const c = (window as any).claude; return c?.use ? await c.use('mcp') : null; } catch { return null; } })();
  return mcpP;
}

interface Track { title: string; artist: string; img?: string; uri?: string; url?: string; playing: boolean; prog?: number; dur?: number; at: number }

/* Het antwoord van Spotify is niet vooraf bekend: zoek de velden op naam. */
function walk(o: unknown, f: (k: string, v: unknown, parent: Record<string, unknown>) => void, d = 0) {
  if (!o || typeof o !== 'object' || d > 6) return;
  for (const [k, v] of Object.entries(o as Record<string, unknown>)) { f(k, v, o as Record<string, unknown>); walk(v, f, d + 1); }
}
function parse(p: unknown): Track | null {
  if (!p || typeof p !== 'object' || Object.keys(p).length === 0) return null;
  let title = '', artist = '', img: string | undefined, uri: string | undefined, url: string | undefined, playing = true, prog: number | undefined, dur: number | undefined;
  const artists: string[] = [];
  walk(p, (k, v, par) => {
    const kl = k.toLowerCase();
    if (typeof v === 'string') {
      if (!uri && /^spotify:(track|episode):/.test(v)) uri = v;
      if (!url && /^https:\/\/open\.spotify\.com\/(track|episode)\//.test(v)) url = v;
      if (!img && /^https:\/\/(i\.scdn\.co|.*\.spotifycdn\.com|mosaic\.scdn\.co)\//.test(v)) img = v;
      if (!title && /^(track_?name|title|song)$/.test(kl)) title = v;
      if (/^artist(_?name)?s?$/.test(kl)) artists.push(v);
    }
    if (Array.isArray(v) && /^artists?$/.test(kl)) v.forEach((a) => { if (typeof a === 'string') artists.push(a); else if (a && typeof a === 'object' && typeof (a as { name?: unknown }).name === 'string') artists.push((a as { name: string }).name); });
    if (typeof v === 'boolean' && /is_?playing|playing/.test(kl)) playing = v;
    if (typeof v === 'number' && /progress/.test(kl)) prog = v;
    if (typeof v === 'number' && /^duration/.test(kl)) dur = v;
  });
  // het eerste "name" is soms de artiest of het album: neem bij voorkeur de naam naast de uri
  walk(p, (_k, v, par) => {
    if (typeof v === 'string' && /^spotify:(track|episode):/.test(v) && typeof par.name === 'string') title = par.name;
  });
  const top = p as Record<string, unknown>;
  if (!title && typeof top.name === 'string') title = top.name;
  if (!title && top.item && typeof (top.item as { name?: unknown }).name === 'string') title = (top.item as { name: string }).name;
  artist = [...new Set(artists)].slice(0, 2).join(', ');
  if (!title) return null;
  if (!url && uri) url = 'https://open.spotify.com/' + uri.split(':')[1] + '/' + uri.split(':')[2];
  return { title, artist, img, uri, url, playing, prog, dur, at: Date.now() };
}

export default function SpotifyBar() {
  const [st, setSt] = useState<'laden' | 'geen' | 'stil' | 'ok' | 'fout'>('laden');
  const [t, setT] = useState<Track | null>(null);
  const [saved, setSaved] = useState<Record<string, boolean>>({});
  const [, tick] = useState(0);
  const busy = useRef(false);

  useEffect(() => {
    let on = true;
    const poll = async () => {
      if (busy.current || document.hidden) return; busy.current = true;
      try {
        const mcp = await getMcp();
        if (!mcp) { if (on) setSt('geen'); return; }
        const r = await mcp.callTool('Spotify', 'get_currently_playing', {}, { cache: { staleTime: 8000, gcTime: 60000 } });
        let p = r?.payload;
        if (p === undefined) { const txt = r?.content?.find((b: { type: string }) => b.type === 'text')?.text; try { p = txt ? JSON.parse(txt) : null; } catch { p = { title: txt }; } }
        const tr = parse(p);
        if (on) { setT(tr); setSt(tr ? 'ok' : 'stil'); }
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const code = (e as any)?.code;
        if (on) setSt(code === 'server_not_connected' || code === 'not_granted' || code === 'forbidden' ? 'geen' : 'fout');
      } finally { busy.current = false; }
    };
    void poll();
    const id = setInterval(poll, 15000);
    const tk = setInterval(() => tick((x) => x + 1), 1000);
    const vis = () => { if (!document.hidden) void poll(); };
    document.addEventListener('visibilitychange', vis);
    return () => { on = false; clearInterval(id); clearInterval(tk); document.removeEventListener('visibilitychange', vis); };
  }, []);

  if (st === 'geen' || st === 'laden') return null;

  const save = async () => {
    if (!t?.uri || saved[t.uri]) return;
    try { const mcp = await getMcp(); await mcp.callTool('Spotify', 'save_to_library', { uri: t.uri }); setSaved((s) => ({ ...s, [t.uri!]: true })); } catch { /* stil */ }
  };
  const prog = t?.dur && t.prog != null ? Math.min(1, (t.prog + (t.playing ? Date.now() - t.at : 0)) / t.dur) : null;

  return (
    <div className="glass-stat hidden max-w-[300px] items-center gap-2.5 !py-1.5 2xl:flex" title="Speelt nu op Spotify">
      {t?.img ? <img src={t.img} alt="" onError={(e) => { e.currentTarget.style.display = "none"; }} className="h-8 w-8 shrink-0 rounded-md object-cover shadow" /> : <span className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-[#1DB954]/20 text-[#1DB954]"><Music2 size={16} /></span>}
      <div className="min-w-0 flex-1">
        {t ? (
          <a href={t.url} target="_blank" rel="noreferrer" className="block truncate text-[12px] font-semibold text-white hover:underline">{t.title}</a>
        ) : <div className="text-[12px] font-semibold text-slate-300">{st === 'fout' ? 'Spotify niet bereikbaar' : 'Spotify: niets aan het afspelen'}</div>}
        {t && <div className="truncate text-[11px] text-slate-400">{t.playing ? '' : '⏸ '}{t.artist || 'Spotify'}</div>}
        {prog != null && <div className="mt-1 h-[3px] w-full overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#1DB954]" style={{ width: `${prog * 100}%` }} /></div>}
      </div>
      {t?.uri && (
        <button onClick={save} className={`shrink-0 rounded-lg p-1 ${saved[t.uri] ? 'text-[#1DB954]' : 'text-slate-400 hover:text-white'}`} aria-label="Opslaan in je Spotify-bibliotheek" title={saved[t.uri] ? 'Opgeslagen' : 'Opslaan in je bibliotheek'}>
          <Heart size={16} fill={saved[t.uri] ? 'currentColor' : 'none'} />
        </button>
      )}
    </div>
  );
}
