/**
 * Service adapters for external integrations.
 *
 * HONESTY RULE: nothing here pretends to be connected. Each adapter reports
 * `status()` truthfully. Only the LLM adapters perform real network calls, and
 * only after the user enters their own API key. Publishing adapters (YouTube,
 * Threads) are intentionally NOT wired to any write endpoint: the game always
 * publishes to the LOCAL SIMULATION and asks for explicit confirmation first.
 */
import type { IntegrationSettings } from '../types';

export type AdapterStatus = 'connected' | 'not_configured' | 'simulation' | 'stub';

export class NotConnectedError extends Error {
  constructor(service: string) {
    super(`${service} is niet gekoppeld. De app draait als simulatie.`);
  }
}

export interface IntegrationInfo {
  id: string;
  name: string;
  purpose: string;
  status: AdapterStatus;
  note: string;
}

// ── LLM (Claude / OpenAI) ─────────────────────────────────────────
export interface LLMAdapter {
  name: string;
  status(): AdapterStatus;
  generate(system: string, prompt: string): Promise<string>;
}

export class ClaudeAdapter implements LLMAdapter {
  name = 'Anthropic Claude';
  constructor(private key: string, private model: string) {}
  status(): AdapterStatus { return this.key ? 'connected' : 'not_configured'; }
  async generate(system: string, prompt: string) {
    if (!this.key) throw new NotConnectedError(this.name);
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': this.key,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({ model: this.model, max_tokens: 800, system, messages: [{ role: 'user', content: prompt }] }),
    });
    if (!res.ok) throw new Error(`Claude API error ${res.status}: ${await res.text()}`);
    const json = (await res.json()) as { content: { type: string; text?: string }[] };
    return json.content.filter((c) => c.type === 'text').map((c) => c.text).join('\n');
  }
}

export class OpenAIAdapter implements LLMAdapter {
  name = 'OpenAI';
  constructor(private key: string, private model: string) {}
  status(): AdapterStatus { return this.key ? 'connected' : 'not_configured'; }
  async generate(system: string, prompt: string) {
    if (!this.key) throw new NotConnectedError(this.name);
    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'content-type': 'application/json', Authorization: `Bearer ${this.key}` },
      body: JSON.stringify({ model: this.model, max_tokens: 800, messages: [{ role: 'system', content: system }, { role: 'user', content: prompt }] }),
    });
    if (!res.ok) throw new Error(`OpenAI API error ${res.status}: ${await res.text()}`);
    const json = (await res.json()) as { choices: { message: { content: string } }[] };
    return json.choices[0]?.message.content ?? '';
  }
}

export class SimulatedLLM implements LLMAdapter {
  name = 'Local Simulation';
  status(): AdapterStatus { return 'simulation'; }
  async generate(_system: string, prompt: string) {
    await new Promise((r) => setTimeout(r, 700));
    return `[SIMULATED OUTPUT — no AI model connected]\n\nBrief received: "${prompt.slice(0, 140)}"\n\n1. Key insight: focus on a single, curiosity-driven question.\n2. Structure: hook → context → 3 escalating reveals → payoff.\n3. Next step: hand off to the next department for review.\n\nConnect Claude or OpenAI in Settings to generate real output.`;
  }
}

export function getLLM(s: IntegrationSettings): LLMAdapter {
  if (s.llmProvider === 'anthropic' && s.anthropicKey) return new ClaudeAdapter(s.anthropicKey, s.anthropicModel);
  if (s.llmProvider === 'openai' && s.openaiKey) return new OpenAIAdapter(s.openaiKey, s.openaiModel);
  return new SimulatedLLM();
}

// ── YouTube Data API ──────────────────────────────────────────────
export interface YouTubeAdapter {
  status(): AdapterStatus;
  /** Read-only public channel statistics via API key. */
  fetchChannelStats(channelId: string): Promise<{ subscribers: number; views: number; videos: number }>;
  /** Upload requires OAuth + explicit user approval. Not implemented on purpose. */
  uploadVideo(): Promise<never>;
}

export class YouTubeDataAdapter implements YouTubeAdapter {
  constructor(private apiKey: string) {}
  status(): AdapterStatus { return this.apiKey ? 'connected' : 'not_configured'; }
  async fetchChannelStats(channelId: string) {
    if (!this.apiKey) throw new NotConnectedError('YouTube Data API');
    const res = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=statistics&id=${encodeURIComponent(channelId)}&key=${this.apiKey}`);
    if (!res.ok) throw new Error(`YouTube API error ${res.status}`);
    const j = (await res.json()) as { items?: { statistics: { subscriberCount: string; viewCount: string; videoCount: string } }[] };
    const st = j.items?.[0]?.statistics;
    if (!st) throw new Error('Kanaal niet gevonden');
    return { subscribers: +st.subscriberCount, views: +st.viewCount, videos: +st.videoCount };
  }
  async uploadVideo(): Promise<never> {
    throw new Error('Uploaden naar YouTube doet niels zelf in Studio.');
  }
}

// ── Threads API ───────────────────────────────────────────────────
export interface ThreadsAdapter {
  status(): AdapterStatus;
  publish(text: string): Promise<never>;
}
export class MetaThreadsAdapter implements ThreadsAdapter {
  constructor(private token: string) {}
  status(): AdapterStatus { return this.token ? 'stub' : 'not_configured'; }
  async publish(_text: string): Promise<never> {
    // Future: POST graph.threads.net/v1.0/{user-id}/threads then /threads_publish — only after explicit user approval.
    throw new NotConnectedError('Threads API');
  }
}

// ── Voice / Image / Video production ──────────────────────────────
export interface MediaAdapter { status(): AdapterStatus; generate(input: string): Promise<never>; }
const stubAdapter = (service: string, configured: boolean): MediaAdapter => ({
  status: () => (configured ? 'stub' : 'not_configured'),
  generate: async () => { throw new NotConnectedError(service); },
});

export function integrationOverview(s: IntegrationSettings): IntegrationInfo[] {
  const llm = getLLM(s);
  return [
    { id: 'llm', name: 'Claude / OpenAI models', purpose: 'Agent reasoning & text deliverables', status: llm.status(), note: llm.status() === 'connected' ? `Gebruikt ${llm.name}, rechtstreeks vanuit je browser met je eigen sleutel.` : 'Agents use the local simulation for text output.' },
    { id: 'youtube', name: 'YouTube Data API', purpose: 'Read channel statistics', status: new YouTubeDataAdapter(s.youtubeApiKey).status(), note: 'Read-only. Uploading is not implemented; publishing is simulated locally.' },
    { id: 'threads', name: 'Threads API', purpose: 'Cross-post internal updates', status: new MetaThreadsAdapter(s.threadsToken).status(), note: 'Adapter interface only. The internal Threads feed is simulated and never posts externally.' },
    { id: 'voice', name: 'Voice generation', purpose: 'AI voice-overs', status: stubAdapter('Voice', !!s.elevenLabsKey).status(), note: 'Interface prepared. Voice-over stage outputs simulated metadata.' },
    { id: 'image', name: 'Image generation', purpose: 'Thumbnails', status: stubAdapter('Image', !!s.imageProvider).status(), note: 'Interface prepared. Thumbnail stage outputs simulated variants.' },
    { id: 'video', name: 'Video production', purpose: 'Rendering & editing', status: 'not_configured', note: 'Interface prepared. Editing stage outputs simulated renders.' },
    { id: 'supabase', name: 'Supabase', purpose: 'Cloud saves', status: s.supabaseUrl && s.supabaseAnonKey ? 'connected' : 'not_configured', note: 'Save data is in local browser storage until you configure Supabase.' },
  ];
}
