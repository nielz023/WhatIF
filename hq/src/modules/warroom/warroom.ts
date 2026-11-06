import type { WarIssueType, WarRecommendation } from '../../types';
import { uid } from '../../lib/util';

export const ISSUE_META: Record<WarIssueType, { label: string; icon: string; color: string }> = {
  declining_views: { label: 'Declining Views', icon: '📉', color: '#f43f5e' },
  low_ctr: { label: 'Low CTR', icon: '🖱️', color: '#f59e0b' },
  poor_retention: { label: 'Poor Retention', icon: '⏱️', color: '#a855f7' },
  production_delays: { label: 'Production Delays', icon: '🐢', color: '#3b82f6' },
  falling_revenue: { label: 'Falling Revenue', icon: '💶', color: '#ef4444' },
};

export function buildAnalysis(type: WarIssueType, channelName: string): { analysis: string[]; recs: WarRecommendation[] } {
  const r = (title: string, detail: string, cost: number, effect: WarRecommendation['effect'], magnitude: number): WarRecommendation => ({ id: uid('rec'), title, detail, cost, effect, magnitude });
  switch (type) {
    case 'low_ctr':
      return {
        analysis: [
          `Prestatie-analist: de CTR van ${channelName} ligt de laatste 7 dagen onder de 4,5% van de niche.`,
          `CTR-specialist: thumbnails hebben te veel tekst; uitschieters gebruiken 1 blikvanger en max. 3 woorden.`,
          `CEO-agent: vertoningen zijn goed, de verpakking is het probleem, niet het onderwerp.`,
        ],
        recs: [
          r('Thumbnails opnieuw ontwerpen', 'CTR-specialist en thumbnailontwerper maken een nieuwe stijlgids.', 400, 'ctr', 1.2),
          r('Titels A/B testen', 'Elke upload krijgt 3 titelvarianten, na 48 uur wisselen.', 150, 'ctr', 0.6),
        ],
      };
    case 'poor_retention':
      return {
        analysis: [
          `Prestatie-analist: de kijkduur van ${channelName} zakt hard na de eerste 45 seconden.`,
          `Hook-specialist: intro’s geven te lang uitleg voor de spanning begint.`,
          `Montagechef: het tempo zakt in deel 2, minder verrassingen dan de concurrentie.`,
        ],
        recs: [
          r('Hooks herschrijven', 'Spanning binnen 5 seconden. Creatief team trainen.', 300, 'retention', 6),
          r('Montage met meer verrassingen', 'Shots max 6 s, elke 60-90 s een nieuw probleem.', 500, 'retention', 9),
        ],
      };
    case 'declining_views':
      return {
        analysis: [
          `Prestatie-analist: de weergaven van ${channelName} dalen ten opzichte van vorige week.`,
          `Niche-analist: de laatste uploads leken te veel op elkaar.`,
          `Uploadmanager: we halen het uploadschema niet.`,
        ],
        recs: [
          r('Vaker uploaden', '+1 video per week; productie voorrang geven.', 250, 'schedule', 1),
          r('Nieuwe onderwerpen zoeken', 'Concurrentie-analist zoekt 10 nieuwe uitschieters.', 350, 'ctr', 0.8),
        ],
      };
    case 'production_delays':
      return {
        analysis: [
          `CEO-agent: meerdere projecten zijn over hun deadline.`,
          `Montagechef: de montage is de flessenhals, taken wachten op een animator.`,
          `Uploadmanager: door de vertraging schuiven de volgende uploads op.`,
        ],
        recs: [
          r('Tijdelijke freelance animator', 'Freelancer versnelt de productie 14 dagen.', 600, 'speed', 0.25),
          r('Week overwerk', 'Iets minder moraal, sneller klaar.', 200, 'speed', 0.12),
        ],
      };
    case 'falling_revenue':
      return {
        analysis: [
          `Financieel manager: minder inkomsten dan vorige periode, terwijl de kosten stegen.`,
          `Prestatie-analist: meer onderwerpen met een lage RPM.`,
          `CEO-agent: kies onderwerpen met hogere RPM en video’s langer dan 8 minuten.`,
        ],
        recs: [
          r('Onderwerpen met hogere RPM', 'Kies wetenschap- en techhoeken.', 300, 'rpm', 0.8),
          r('Advertenties halverwege', 'Video’s langer dan 8 min met natuurlijke pauzes.', 150, 'rpm', 0.4),
        ],
      };
  }
}
