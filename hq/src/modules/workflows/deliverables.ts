import type { Channel, Project, StageId } from '../../types';
import { pick, randInt } from '../../lib/util';

/**
 * LOCAL SIMULATION deliverable generator.
 * Produces structured, plausible placeholder outputs for each stage.
 * When an LLM adapter is configured, agents can generate real text via the Agent panel instead.
 */
export function simulateDeliverable(stage: StageId, project: Project, channel: Channel | undefined, quality: number): string {
  const t = project.topic;
  const niche = channel?.niche ?? 'general';
  const q = Math.round(quality);
  switch (stage) {
    case 'research':
      return [
        `RESEARCH BRIEF — ${t}`,
        `• Niche: ${niche} · Est. search demand: ${randInt(12, 90)}k/mo`,
        `• Top competitor outliers: ${randInt(3, 9)} videos > 5× channel average`,
        `• Audience questions: "Why ${t.toLowerCase()}?", "Is it true that…", "What happens next?"`,
        `• Gap: few videos cover this with a narrative structure under 15 min`,
        `• Confidence score: ${q}/100`,
      ].join('\n');
    case 'topic':
      return [
        `TOPIC SHORTLIST`,
        `1. ${t} ✅ selected`,
        `2. The hidden history behind ${t.split(' ').slice(-2).join(' ')}`,
        `3. ${pick(['5 myths', '7 facts', 'The truth'])} about ${niche}`,
        `Selection rationale: highest demand/competition ratio, evergreen potential.`,
      ].join('\n');
    case 'titles':
      return [
        `TITLE OPTIONS`,
        `A) ${project.title}`,
        `B) Nobody Talks About ${t}`,
        `C) ${t} — The Full Story`,
        `HOOK (0:00–0:20): "In ${randInt(1990, 2024)}, something happened that changed ${niche} forever — and almost nobody noticed."`,
        `Predicted CTR uplift vs. baseline: +${(q / 40).toFixed(1)}%`,
      ].join('\n');
    case 'script':
      return [
        `SCRIPT v${project.rejections + 1} — ${project.title}`,
        `[HOOK] Open loop + stakes (0:00–0:30)`,
        `[ACT 1] Context and the central question (0:30–3:00)`,
        `[ACT 2] Three escalating revelations with b-roll cues (3:00–8:30)`,
        `[ACT 3] Payoff, twist and takeaway (8:30–11:00)`,
        `[CTA] Soft subscribe + next video tease`,
        `Word count: ${randInt(1500, 2100)} · Est. runtime ${randInt(10, 14)} min`,
      ].join('\n');
    case 'factcheck':
      return [
        `FACT-CHECK REPORT`,
        `Claims checked: ${randInt(14, 30)} · Sources cited: ${randInt(6, 15)}`,
        q >= 55 ? `Result: PASS — no critical inaccuracies.` : `Result: ISSUES — ${randInt(2, 5)} claims need stronger sources.`,
      ].join('\n');
    case 'voice':
      return `VOICE-OVER (simulated)\nVoice profile: ${pick(['Deep documentary', 'Warm storyteller', 'Calm narrator'])}\nDuration: ${randInt(10, 14)}:${String(randInt(0, 59)).padStart(2, '0')} · Loudness −14 LUFS\nNo audio file generated — voice adapter not connected.`;
    case 'editing':
      return `EDITED CUT (simulated)\nClips: ${randInt(120, 260)} · Cuts/min: ${randInt(8, 18)} · Music beds: ${randInt(2, 4)}\nRender: 4K/30 · Retention-pacing score ${q}/100\nNo video file generated — video adapter not connected.`;
    case 'thumbnail':
      return `THUMBNAIL VARIANTS (simulated)\nA: Big face-less object + 3-word text\nB: Contrast split before/after\nC: Map + red arrow\nPredicted CTR: ${(3 + q / 20).toFixed(1)}%`;
    case 'qc':
      return [
        `QC CHECKLIST`,
        `☑ Audio levels  ☑ Captions  ☑ Copyright check  ☑ Policy check`,
        q >= 55 ? `Verdict: READY for CEO approval` : `Verdict: SEND BACK — pacing dips at ${randInt(3, 8)}:${String(randInt(0, 59)).padStart(2, '0')}`,
      ].join('\n');
    case 'approval':
      return `APPROVAL MEMO\nOverall quality: ${q}/100\nRecommendation: ${q >= 65 ? 'Approve and publish' : 'Approve with caution'}`;
    case 'publishing':
      return `UPLOAD PACKAGE\nTitle: ${project.title}\nTags: ${niche.toLowerCase()}, ${t.toLowerCase().split(' ').slice(0, 3).join(', ')}\nChapters: 5 · End screen: yes\nDestination: LOCAL SIMULATION (YouTube adapter not connected)`;
  }
}

const TOPICS: Record<string, string[]> = {
  'what if': ['What IF You Could Teleport?', 'What IF You Could Fly 30 km High?', 'What IF You Were Invisible?', 'What IF You Could Rewind 10 Seconds?', 'What IF You Got 2x SMALLER Every Day?', 'What IF You Got 2x BIGGER Every Day?', 'What IF You Never Slept Again?', 'What IF You Could Hear Every Thought?', 'What IF Earth Spun 10x Faster?', 'What IF Gravity Stopped for 1 Second?', 'What IF The Moon Was 2x Closer?', 'What IF The Sun Vanished for 1 Minute?', 'What IF You Could Never Die?', 'What IF You Got 1 Year Younger Every Day?', 'What IF Everyone Disappeared?', 'What IF You Could Stop Time?'],
  default: ['The Lost City Under the Ocean', 'Why Nobody Can Explain This Signal', 'The Richest Empire You Never Heard Of', 'The Engineering Behind Impossible Bridges', 'How One Mistake Changed History'],
  history: ['The Fall of the Bronze Age', 'The Spy Who Fooled Two Empires', 'Inside the Library of Alexandria', 'The Forgotten Pirate Republic'],
  finance: ['How Index Funds Really Work', 'The Hidden Cost of Buy Now Pay Later', 'Why Billionaires Borrow Instead of Sell', 'The 4% Rule Explained'],
  science: ['What Happens Inside a Black Hole', 'The Deepest Hole Ever Dug', 'Why Time Moves Slower in Space', 'The Animal That Never Dies'],
  mystery: ['The Unsolved Case of Flight 19', 'The Village That Vanished', 'The Signal From Deep Space', 'The Ship Found With No Crew'],
};

export function suggestTopic(niche: string): string {
  const k = niche.toLowerCase();
  const key = Object.keys(TOPICS).find((t) => k.includes(t)) ?? 'default';
  return pick(TOPICS[key]);
}
