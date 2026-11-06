/**
 * MUZIEKBALK (niels 2026-11-06: "spotify koppelen, bovenin een muziekbalkje").
 * Leest via je eigen Spotify-koppeling in claude.ai wat er nu speelt (mcp-capability),
 * met hartje om op te slaan. Klik op het plaatje: menu met niels' playlists en de
 * knop om die in Spotify af te spelen. Een ingebouwde Spotify-speler (iframe) blokkeert
 * claude.ai, dus afspelen/pauze/overslaan gebeurt in Spotify zelf.
 */
import { useEffect, useRef, useState } from 'react';
import { ChevronDown, ExternalLink, Heart, Music2 } from 'lucide-react';

const PLAYLISTS = [
  { id: '0lyLOIHumYTLteeaUvt8to', name: 'OG RawStyle' },
  { id: '31kCJwFmA4SYr5bK9sRLpQ', name: 'Gym' },
  { id: '4T1mOmZxc6wqaASVUinELI', name: 'Op repeat' },
  { id: '6kdI3hgDMfYAFDpCW2ZRZw', name: 'Radio Niels' },
];
const KEY = 'dm-spotify-playlist';
function lees(): string | null { try { return localStorage.getItem(KEY); } catch { return null; } }
function bewaar(id: string) { try { localStorage.setItem(KEY, id); } catch { /* geen opslag */ } }

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
  const [open, setOpen] = useState(false);
  const [pl, setPl] = useState<string | null>(() => lees());
  const [geladen, setGeladen] = useState<string | null>(null); // speler pas laden na eerste keer openen
  const box = useRef<HTMLDivElement>(null);
  const kies = (id: string) => { setPl(id); bewaar(id); setGeladen(id); };
  useEffect(() => {
    if (!open) return;
    if (!geladen) setGeladen(pl ?? PLAYLISTS[0].id);
    const weg = (e: MouseEvent) => { if (box.current && !box.current.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('mousedown', weg); document.addEventListener('keydown', esc);
    return () => { document.removeEventListener('mousedown', weg); document.removeEventListener('keydown', esc); };
  }, [open, geladen, pl]);

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

  const save = async () => {
    if (!t?.uri || saved[t.uri]) return;
    try { const mcp = await getMcp(); await mcp.callTool('Spotify', 'save_to_library', { uri: t.uri }); setSaved((s) => ({ ...s, [t.uri!]: true })); } catch { /* stil */ }
  };
  const prog = t?.dur && t.prog != null ? Math.min(1, (t.prog + (t.playing ? Date.now() - t.at : 0)) / t.dur) : null;

  const actief = geladen ?? pl ?? PLAYLISTS[0].id;
  const plNaam = PLAYLISTS.find((x) => x.id === (pl ?? actief))?.name ?? 'Spotify';
  const live = st === 'ok' && t;

  return (
    <div ref={box} className="relative hidden xl:block">
      <div className="glass-stat flex max-w-[320px] items-center gap-2.5 !py-1.5" title="Muziek">
        <button onClick={() => setOpen((o) => !o)} className="group relative shrink-0" aria-label="Playlists en speler openen" title="Playlist kiezen">
          {live && t.img ? <img src={t.img} alt="" onError={(e) => { e.currentTarget.style.display = 'none'; }} className="h-8 w-8 rounded-md object-cover shadow" /> : <span className="grid h-8 w-8 place-items-center rounded-md bg-[#1DB954]/20 text-[#1DB954]"><Music2 size={16} /></span>}
          <span className="absolute -bottom-1 -right-1 grid h-4 w-4 place-items-center rounded-full bg-[#1DB954] text-black opacity-90 group-hover:opacity-100"><ChevronDown size={11} className={open ? 'rotate-180' : ''} /></span>
        </button>
        <div className="min-w-0 flex-1">
          {live ? (
            <a href={t.url} target="_blank" rel="noreferrer" className="block truncate text-[12px] font-semibold text-white hover:underline">{t.title}</a>
          ) : (
            <button onClick={() => setOpen((o) => !o)} className="block max-w-full truncate text-left text-[12px] font-semibold text-white hover:underline">{geladen ? plNaam : 'Kies je muziek'}</button>
          )}
          <div className="truncate text-[11px] text-slate-400">{live ? (t.playing ? '' : '⏸ ') + (t.artist || 'Spotify') : 'Spotify · klik om te kiezen'}</div>
          {live && prog != null && <div className="mt-1 h-[3px] w-full overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#1DB954]" style={{ width: `${prog * 100}%` }} /></div>}
        </div>
        {live && t.uri && (
          <button onClick={save} className={`shrink-0 rounded-lg p-1 ${saved[t.uri] ? 'text-[#1DB954]' : 'text-slate-400 hover:text-white'}`} aria-label="Opslaan in je Spotify-bibliotheek" title={saved[t.uri] ? 'Opgeslagen' : 'Opslaan in je bibliotheek'}>
            <Heart size={16} fill={saved[t.uri] ? 'currentColor' : 'none'} />
          </button>
        )}
      </div>

      {/* menu + speler: blijft staan als het dicht is (onzichtbaar), zodat de muziek doorspeelt */}
      <div className={`absolute right-0 top-full z-[60] mt-2 w-[380px] rounded-2xl border border-white/10 bg-[#0b1226]/95 p-3 shadow-2xl backdrop-blur-xl transition ${open ? 'visible opacity-100' : 'pointer-events-none invisible opacity-0'}`} style={open ? undefined : { transform: 'translateY(-6px)' }}>
        <div className="mb-2 flex items-center justify-between">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Jouw playlists</div>
          <a href={'https://open.spotify.com/playlist/' + actief} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white">Open in Spotify <ExternalLink size={11} /></a>
        </div>
        <div className="mb-3 grid grid-cols-2 gap-1.5">
          {PLAYLISTS.map((x) => (
            <button key={x.id} onClick={() => kies(x.id)} className={`truncate rounded-lg px-2.5 py-1.5 text-left text-[12px] font-semibold transition ${actief === x.id ? 'bg-[#1DB954] text-black' : 'bg-white/5 text-slate-200 hover:bg-white/10'}`}>{x.name}</button>
          ))}
        </div>
        {/* claude.ai laat geen Spotify-speler in de pagina toe (getest 6 nov): afspelen gebeurt in de Spotify-app */}
        {live && (
          <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 p-2.5">
            {t.img ? <img src={t.img} alt="" className="h-16 w-16 rounded-lg object-cover shadow" /> : <span className="grid h-16 w-16 place-items-center rounded-lg bg-[#1DB954]/20 text-[#1DB954]"><Music2 size={24} /></span>}
            <div className="min-w-0">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">{t.playing ? 'Speelt nu' : 'Gepauzeerd'}</div>
              <div className="truncate text-[13px] font-semibold text-white">{t.title}</div>
              <div className="truncate text-[11px] text-slate-400">{t.artist}</div>
            </div>
          </div>
        )}
        <a href={'https://open.spotify.com/playlist/' + actief} target="_blank" rel="noreferrer" onClick={() => setTimeout(() => setOpen(false), 300)} className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#1DB954] px-3 py-2.5 text-[13px] font-bold text-black hover:brightness-110">
          <Music2 size={16} /> Speel {plNaam} in de Spotify-app
        </a>
        <div className="mt-2 text-[10px] leading-snug text-slate-500">claude.ai laat de Spotify-speler niet in HQ toe. Afspelen, pauze en overslaan doe je in de Spotify-app; HQ laat zien wat er speelt, met het plaatje. </div>
      </div>
    </div>
  );
}
