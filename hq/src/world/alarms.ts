/**
 * ALARMEN (verbeterpunt 8): wat er mis kan gaan, uit de echte stand.
 * Rood = er is iets vastgelopen of mislukt (crisiskamer gaat knipperen met zwaailicht en sirene).
 * Oranje = let op (renderstatus al lang niet bijgewerkt, schijf bijna vol, taak wacht al lang op jou).
 * Verbeterlijst punt 60: per probleem ook wat er misging, wat Claude deed en wat niels moet doen.
 */
import type { Live } from '../services/live';
import { useDb } from '../services/db';

export interface Alarm {
  level: 'rood' | 'oranje'; text: string; key: string;
  /** wat er misging (uitgebreider dan text) */ mis?: string;
  /** wat Claude (de thread of de automatische ronde) eraan deed, als dat bekend is */ gedaan?: string;
  /** wat niels moet doen */ jij?: string;
  /** thread waar het bij hoort (voor "open het gesprek" en opdrachten) */ thread?: string;
  /** voorstel voor een opdracht aan Claude */ opdracht?: string;
}

const hoursAgo = (iso?: string) => { if (!iso) return Infinity; const t = new Date(iso.length <= 16 ? iso + ':00' : iso).getTime(); return isNaN(t) ? Infinity : (Date.now() - t) / 3.6e6; };

export function alarmsFrom(L: Live): Alarm[] {
  const out: Alarm[] = [];
  for (const a of L.activity ?? []) {
    const id = a.id || a.session || a.title; // live threads die nog niet in status.json staan hebben (nog) geen id
    if (a.state === 'failed') out.push({
      level: 'rood', text: `Taak mislukt: ${a.title}`, key: `f:${id}`, thread: a.id || undefined,
      mis: `De thread "${a.title}" is mislukt${a.last ? ` (laatst actief ${a.last})` : ''}.`,
      gedaan: a.doing ? `Laatste stap van Claude: ${a.doing}` : undefined,
      jij: a.needs ?? 'Lees het gesprek en kies: opnieuw proberen of laten vallen.',
      opdracht: `De thread "${a.title}" is mislukt. Zoek uit waarom, los het op en probeer het opnieuw. Meld wat je hebt gedaan.`,
    });
    const h = hoursAgo(a.lastIso);
    if (a.state === 'blocked' && Number.isFinite(h) && h > 24) out.push({
      level: 'oranje', text: `Wacht al ${Math.round(h)} uur op jou: ${a.title}`, key: `b:${id}`, thread: a.id || undefined,
      mis: `De thread "${a.title}" staat al ${Math.round(h)} uur stil omdat hij op jou wacht.`,
      gedaan: a.doing ? `Claude stopte bij: ${a.doing}` : 'Claude wacht op je antwoord en doet intussen niets aan deze taak.',
      jij: a.needs ?? 'Geef antwoord in het gesprek, dan gaat Claude verder.',
    });
  }
  const b = L.blender;
  if (b) {
    const rendering = (L.videos ?? []).some((v) => v.steps.some((s) => s.active && (s.label === 'Animatie' || s.label === 'Render')));
    const h = hoursAgo(b.bijgewerkt);
    if (rendering && h > 12 && h < 24 * 30) out.push({
      level: 'oranje', text: `Renderstatus al ${Math.round(h)} uur niet bijgewerkt (loopt de render nog?)`, key: 'render-stil',
      mis: `De render op je pc meldde zich ${Math.round(h)} uur geleden voor het laatst: "${b.stand}".`,
      gedaan: 'De automatische ronde kijkt elk uur naar de renderstatus, maar ziet niets veranderen.',
      jij: 'Kijk of je pc aanstaat en Blender nog rendert. Is hij gestopt, start hem opnieuw of geef Claude een opdracht.',
      opdracht: 'De renderstatus is al lang niet bijgewerkt. Controleer of de render op de pc nog loopt en zet hem zo nodig opnieuw in gang.',
    });
    const disk = /schijf\s*([\d.,]+)\s*GB/i.exec(b.stand ?? '')?.[1];
    if (disk) {
      const gb = parseFloat(disk.replace(',', '.'));
      if (gb < 25) out.push({
        level: gb < 8 ? 'rood' : 'oranje', text: `Schijf bijna vol: ${disk} GB vrij (stand van ${b.bijgewerkt?.slice(5, 16).replace('T', ' ')})`, key: 'schijf',
        mis: `Er is nog maar ${disk} GB vrij op de schijf waar gerenderd wordt; bij een volle schijf stopt de render.`,
        jij: 'Ruim oude frames of renders op, of laat Claude voorstellen wat weg kan.',
        opdracht: 'De schijf is bijna vol. Maak een lijst van oude frames en renders die veilig weg kunnen (niets weggooien zonder mijn akkoord).',
      });
    }
  }
  // fouten uit het automatische logboek van de laatste 24 uur
  const e = useDb.getState().log.find((x) => x.kind === 'fout' && hoursAgo(x.at) < 24);
  if (e) out.push({
    level: 'rood', text: `Fout in de automatische ronde: ${e.text}`.slice(0, 120), key: `log:${e.at}`,
    mis: e.text, gedaan: 'De automatische ronde schreef deze fout in het logboek en ging verder met de rest.',
    jij: 'Meestal niets: de volgende ronde probeert het opnieuw. Komt hij terug, geef Claude dan de opdracht hieronder.',
    opdracht: `Er staat een fout in het logboek van de automatische ronde: "${e.text}". Zoek uit wat er misgaat en los het op.`,
  });
  return out;
}

/** Iets echt mis (verbeterlijst punt 60): een rood alarm of een vastgelopen render. Alleen dan staat de crisiskamer in het menu. */
export const ernstig = (alarms: Alarm[]) => alarms.some((a) => a.level === 'rood' || a.key === 'render-stil');
