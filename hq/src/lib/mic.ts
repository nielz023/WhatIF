/**
 * Microfoon in elk tekstvak: één globale module, zodat geen enkel veld zelf iets hoeft te doen.
 * - Elk geschikt veld krijgt klasse `dm-mic` (icoon via CSS, zie het einde van index.css).
 * - Klik op het icoon (rechter ~34 px, bij een textarea het vak rechtsboven) of Alt+M = inspreken aan/uit.
 * - Werkt de spraakherkenning van de browser niet (geen API, geen toestemming, 'network' in de app),
 *   dan houden we de focus in het veld en tonen we hoe de dicteerfunctie van het systeem werkt.
 * - Een veld uitzetten: `data-geen-mic` op het veld of op een ouder.
 */
import { useGame } from '../store/useGame';

type Veld = HTMLInputElement | HTMLTextAreaElement;

const SELECTOR = 'textarea, input:not([type]), input[type=text], input[type=search]';
const ZONE = 34;
const MIN_B = 110;
const MIN_H = 26;

let gestart = false;
let rec: SpeechRecognitionLike | null = null;
let actief: Veld | null = null;
let laatsteHint = 0;
let cursorVeld: Veld | null = null;

interface SpeechRecognitionLike {
  lang: string; interimResults: boolean; continuous: boolean;
  onresult: ((e: { resultIndex: number; results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }> }) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void; stop(): void; abort(): void;
}

const isVeld = (el: unknown): el is Veld => el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement;

function geschikt(el: Element): el is Veld {
  if (!isVeld(el) || !el.matches(SELECTOR)) return false;
  if (el.readOnly || el.disabled || el.closest('[data-geen-mic]')) return false;
  return el.offsetWidth >= MIN_B && el.offsetHeight >= MIN_H;
}

function scan() {
  document.querySelectorAll<Veld>(SELECTOR).forEach((el) => {
    const ok = geschikt(el);
    if (ok !== el.classList.contains('dm-mic')) el.classList.toggle('dm-mic', ok);
  });
}

let scanGepland = false;
function planScan() {
  if (scanGepland) return;
  scanGepland = true;
  requestAnimationFrame(() => { scanGepland = false; scan(); });
}

function inZone(el: Veld, x: number, y: number) {
  const r = el.getBoundingClientRect();
  if (x < r.right - ZONE || x > r.right || y < r.top || y > r.bottom) return false;
  return el instanceof HTMLTextAreaElement ? y <= r.top + ZONE : true;
}

/** React ziet de wijziging alleen via de native setter plus een input-event. */
function zetWaarde(el: Veld, v: string, caret: number) {
  const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value')?.set?.call(el, v);
  el.dispatchEvent(new Event('input', { bubbles: true }));
  try { el.setSelectionRange(caret, caret); } catch { /* sommige types kennen geen selectie */ }
}

function plaats(el: Veld, voor: string, na: string, gesproken: string) {
  const t = gesproken.replace(/\s+/g, ' ').trim();
  const sep1 = t && voor && !/\s$/.test(voor) ? ' ' : '';
  const sep2 = t && na && !/^[\s.,!?;:]/.test(na) ? ' ' : '';
  const begin = voor + sep1 + t;
  zetWaarde(el, begin + sep2 + na, begin.length);
}

function platformTip() {
  const ua = navigator.userAgent || '';
  const touchMac = /Mac/.test(ua) && navigator.maxTouchPoints > 1;
  if (/Android|iPhone|iPad|iPod|Mobile/i.test(ua) || touchMac) return 'Tik op de microfoon van je toetsenbord';
  if (/Win/i.test(ua)) return 'Druk op Windows-toets + H om in te spreken';
  if (/Mac/i.test(ua)) return 'Druk twee keer op Fn (Dicteren) om in te spreken';
  return 'Gebruik de dicteerfunctie van je computer om in te spreken';
}

function hint(el: Veld | null, reden: string) {
  if (el) el.focus();
  const nu = Date.now();
  if (nu - laatsteHint < 60000) return;
  laatsteHint = nu;
  const begin =
    reden === 'not-allowed' || reden === 'service-not-allowed' ? 'De microfoon mag hier niet aan.'
      : reden === 'audio-capture' ? 'Ik vind geen microfoon.'
        : 'Inspreken via de browser lukt hier niet.';
  useGame.getState().toast(`${begin} ${platformTip()}; dat werkt in elk tekstvak.`, 'info');
}

/** Zacht stoppen laat de laatste eindtekst nog binnenkomen; hard stoppen (abort) negeert alles wat nog komt. */
function stop(hard = false) {
  const r = rec;
  const el = actief;
  rec = null; actief = null;
  el?.classList.remove('dm-mic-aan');
  if (!r) return;
  if (hard) { r.onresult = null; r.onerror = null; r.onend = null; }
  try { if (hard) r.abort(); else r.stop(); } catch { /* al gestopt */ }
}

function start(el: Veld) {
  stop();
  const W = window as unknown as { SpeechRecognition?: new () => SpeechRecognitionLike; webkitSpeechRecognition?: new () => SpeechRecognitionLike };
  const SR = W.SpeechRecognition || W.webkitSpeechRecognition;
  if (document.activeElement !== el) el.focus();
  if (!SR) { hint(el, 'geen-api'); return; }
  let r: SpeechRecognitionLike;
  try { r = new SR(); } catch { hint(el, 'geen-api'); return; }
  r.lang = 'nl-NL'; r.interimResults = true; r.continuous = true;
  const a = el.selectionStart ?? el.value.length;
  const b = el.selectionEnd ?? a;
  const voor = el.value.slice(0, a);
  const na = el.value.slice(b);
  rec = r; actief = el;
  el.classList.add('dm-mic-aan');
  // Alle resultaten van deze sessie opnieuw samenvoegen: tussentekst wordt zo vanzelf vervangen door de eindtekst.
  r.onresult = (e) => {
    let tekst = '';
    for (let i = 0; i < e.results.length; i++) tekst += ' ' + (e.results[i][0]?.transcript ?? '');
    plaats(el, voor, na, tekst);
  };
  r.onerror = (e) => {
    const fout = e?.error || '';
    if (rec === r) stop(true);
    if (fout !== 'no-speech' && fout !== 'aborted') hint(el, fout);
  };
  r.onend = () => { if (rec === r) stop(); };
  try { r.start(); } catch { stop(true); hint(el, 'geen-api'); }
}

function wissel(el: Veld) {
  if (actief === el) stop(); else start(el);
}

/** Eén keer starten vanuit de opstart van de app. */
export function startMic() {
  if (gestart || typeof document === 'undefined') return;
  gestart = true;
  scan();
  new MutationObserver(planScan).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style', 'hidden', 'disabled', 'readonly', 'data-geen-mic'] });
  setInterval(scan, 2500);
  window.addEventListener('resize', planScan);
  document.addEventListener('focusin', planScan);

  // Klik op het icoon: mousedown afvangen, zodat de focus en het tekstpunt blijven staan.
  document.addEventListener('mousedown', (e) => {
    const el = e.target;
    if (e.button !== 0 || !isVeld(el) || !el.classList.contains('dm-mic') || !inZone(el, e.clientX, e.clientY)) return;
    e.preventDefault();
    e.stopPropagation();
    wissel(el);
  }, true);

  // Handje boven het icoon.
  document.addEventListener('mousemove', (e) => {
    const el = e.target;
    const op = isVeld(el) && el.classList.contains('dm-mic') && inZone(el, e.clientX, e.clientY) ? el : null;
    if (cursorVeld && cursorVeld !== op) cursorVeld.style.cursor = '';
    if (op) op.style.cursor = 'pointer';
    cursorVeld = op;
  }, { passive: true });

  window.addEventListener('keydown', (e) => {
    if (e.altKey && !e.ctrlKey && !e.metaKey && (e.code === 'KeyM' || e.key.toLowerCase() === 'm')) {
      const el = document.activeElement;
      if (el && isVeld(el) && geschikt(el)) { e.preventDefault(); e.stopPropagation(); wissel(el); }
      return;
    }
    if (!actief) return;
    if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); stop(); return; }
    // Zelf typen in het opnemende veld: inspreken stoppen, zodat we de getypte tekst niet overschrijven.
    if (e.target === actief && !['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) stop(true);
  }, true);

  document.addEventListener('focusout', (e) => { if (actief && e.target === actief) stop(); }, true);
}
