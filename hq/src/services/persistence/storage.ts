/**
 * Persistence layer.
 *  - LocalStorage is the default (works offline, no credentials).
 *  - SupabaseAdapter is ready for use once a project URL + anon key are configured
 *    in Settings and the table from `supabase/schema.sql` exists.
 */
import type { StateStorage } from 'zustand/middleware';

export const localStorageAdapter: StateStorage = {
  getItem: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  setItem: (k, v) => { try { localStorage.setItem(k, v); } catch { /* quota / private mode */ } },
  removeItem: (k) => { try { localStorage.removeItem(k); } catch { /* ignore */ } },
};

export interface RemoteSaveAdapter {
  readonly name: string;
  isConfigured(): boolean;
  save(saveId: string, data: unknown): Promise<void>;
  load(saveId: string): Promise<unknown | null>;
}

export class SupabaseAdapter implements RemoteSaveAdapter {
  readonly name = 'Supabase';
  constructor(private url: string, private anonKey: string) {}
  isConfigured() { return !!(this.url && this.anonKey); }
  private headers() {
    return { apikey: this.anonKey, Authorization: `Bearer ${this.anonKey}`, 'Content-Type': 'application/json' };
  }
  async save(saveId: string, data: unknown) {
    if (!this.isConfigured()) throw new Error('Supabase is not configured.');
    const res = await fetch(`${this.url.replace(/\/$/, '')}/rest/v1/game_saves`, {
      method: 'POST',
      headers: { ...this.headers(), Prefer: 'resolution=merge-duplicates' },
      body: JSON.stringify({ id: saveId, data, updated_at: new Date().toISOString() }),
    });
    if (!res.ok) throw new Error(`Supabase save failed: ${res.status} ${await res.text()}`);
  }
  async load(saveId: string) {
    if (!this.isConfigured()) throw new Error('Supabase is not configured.');
    const res = await fetch(`${this.url.replace(/\/$/, '')}/rest/v1/game_saves?id=eq.${encodeURIComponent(saveId)}&select=data`, { headers: this.headers() });
    if (!res.ok) throw new Error(`Supabase load failed: ${res.status}`);
    const rows = (await res.json()) as { data: unknown }[];
    return rows[0]?.data ?? null;
  }
}
