/**
 * EIGEN LINK PER PAGINA, GESPREK EN BESTAND (verbeterlijst punt 23) en de zoeksneltoets / (punt 19).
 * De stand staat in het adres achter # (bv. #/videos, #/gesprek/cmsg_..., #/bestand/videos/geen-regels/script.md),
 * zodat de terugknop van de browser werkt en een adres met # het HQ meteen op die plek opent.
 * Let op: binnen claude.ai draait het HQ in een kader; daar werkt terug wel, maar het adres in de adresbalk
 * van claude.ai verandert niet mee.
 */
import { useGame } from '../store/useGame';
import { useGesprek, openGesprek } from '../components/shared/Gesprek';
import { useBestand, openBestand } from '../components/shared/BestandViewer';
import { openKennis, useKennisNav } from '../services/kennis';
import type { PageId } from '../types';

let bezigMetHerstel = false;
function huidig(): string {
  const g = useGesprek.getState().open; const b = useBestand.getState().pad; const p = useGame.getState().page;
  if (b) return `#/bestand/${b}`;
  if (g) return g.kind === 'project' ? '#/projectchat' : `#/gesprek/${g.thread ?? ''}`;
  if (p === 'kennis') return `#/kennis/${useKennisNav.getState().tab}`;
  return `#/${p}`;
}
function herstel(h: string) {
  bezigMetHerstel = true;
  try {
    const [, soort, ...rest] = decodeURIComponent(h.replace(/^#/, '')).split('/');
    const r = rest.join('/');
    if (soort === 'bestand' && r) { openBestand(r); return; }
    useBestand.setState({ pad: null });
    if (soort === 'gesprek' && r) { openGesprek({ kind: 'thread', thread: r, title: 'Gesprek' }); return; }
    if (soort === 'projectchat') { openGesprek({ kind: 'project', title: 'Projectchat' }); return; }
    useGesprek.getState().show(null);
    if (soort === 'kennis') { openKennis(r ? { tab: r as never } : {}); return; }
    if (soort) useGame.getState().setPage(soort as PageId);
  } catch { /* onbekend adres: laten staan */ } finally { setTimeout(() => { bezigMetHerstel = false; }, 0); }
}
function schrijf() {
  if (bezigMetHerstel) return;
  const h = huidig();
  if (h !== location.hash) { try { history.pushState(null, '', h); } catch { /* kader zonder history */ } }
}

export function startRoute() {
  if (location.hash.length > 2) herstel(location.hash);
  useGame.subscribe((s, p) => { if (s.page !== p.page) schrijf(); });
  useGesprek.subscribe((s, p) => { if (s.open !== p.open) schrijf(); });
  useBestand.subscribe((s, p) => { if (s.pad !== p.pad) schrijf(); });
  useKennisNav.subscribe((s, p) => { if (s.tab !== p.tab) schrijf(); });
  window.addEventListener('popstate', () => herstel(location.hash || '#/overzicht'));
  window.addEventListener('keydown', (e) => {
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
    if ((e.target as HTMLElement)?.closest('input,textarea,select,[contenteditable]')) return;
    e.preventDefault(); zoek();
  });
}

/** de zoekbalk door alles (Kennis › Zoeken), met de cursor meteen in het veld */
export function zoek() {
  openKennis({ tab: 'zoeken' });
  setTimeout(() => (document.querySelector('#kennis-zoek, [type=search]') as HTMLInputElement | null)?.focus(), 120);
}
