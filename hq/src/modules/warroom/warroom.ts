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
          `Performance Analyst: CTR on ${channelName} is below the 4.5% niche benchmark over the last 7 days.`,
          `CTR Specialist: Thumbnails use too much text; competitor outliers use 1 focal object + ≤3 words.`,
          `CEO Agent: Impressions are healthy — the packaging, not the topic, is the bottleneck.`,
        ],
        recs: [
          r('Thumbnail redesign sprint', 'CTR Specialist + Thumbnail Designer redo packaging style guide.', 400, 'ctr', 1.2),
          r('Title A/B testing protocol', 'Every upload ships with 3 title variants rotated after 48h.', 150, 'ctr', 0.6),
        ],
      };
    case 'poor_retention':
      return {
        analysis: [
          `Performance Analyst: Average view duration on ${channelName} drops sharply after the first 45 seconds.`,
          `Hook Specialist: Intros spend too long on context before the open loop.`,
          `Editing Supervisor: Pacing dips in act 2 — fewer pattern interrupts than competitors.`,
        ],
        recs: [
          r('Hook rewrite framework', 'Hooks must deliver stakes in < 15s. Train Creative team.', 300, 'retention', 6),
          r('Pattern-interrupt editing pass', 'Add b-roll / zoom every 6–8s in act 2.', 500, 'retention', 9),
        ],
      };
    case 'declining_views':
      return {
        analysis: [
          `Performance Analyst: 7-day views on ${channelName} are trending down vs. the previous week.`,
          `Niche Analyst: Topic fatigue — the last uploads covered overlapping subjects.`,
          `Upload Manager: Upload cadence slipped below the promised schedule.`,
        ],
        recs: [
          r('Increase upload cadence', 'Raise schedule by +1 video/week; prioritise production queue.', 250, 'schedule', 1),
          r('Fresh topic cluster research', 'Competitor Analyst maps 10 new outlier topics.', 350, 'ctr', 0.8),
        ],
      };
    case 'production_delays':
      return {
        analysis: [
          `CEO Agent: Several projects are past their deadline.`,
          `Editing Supervisor: The edit bay is the bottleneck — tasks wait for a free editor.`,
          `Financial Manager: Delays cost an estimated 12% of monthly revenue potential.`,
        ],
        recs: [
          r('Hire freelance editor (temporary)', 'One-off freelancer boosts production speed for 14 days.', 600, 'speed', 0.25),
          r('Overtime week', 'Small morale cost, faster throughput.', 200, 'speed', 0.12),
        ],
      };
    case 'falling_revenue':
      return {
        analysis: [
          `Financial Manager: Revenue is down vs. the previous period while expenses grew.`,
          `Performance Analyst: Mix shifted toward lower-RPM topics.`,
          `CEO Agent: Prioritise high-RPM sub-topics and longer videos for mid-rolls.`,
        ],
        recs: [
          r('High-RPM topic pivot', 'Steer topics toward finance/tech-adjacent angles.', 300, 'rpm', 0.8),
          r('Mid-roll optimisation', 'Videos > 8 min with natural ad breaks.', 150, 'rpm', 0.4),
        ],
      };
  }
}
