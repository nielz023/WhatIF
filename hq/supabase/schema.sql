-- FACELESS YOUTUBE HQ — Supabase schema
-- Phase 1: whole-save JSON document (used by SupabaseAdapter in src/services/persistence/storage.ts)
create table if not exists public.game_saves (
  id text primary key,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

-- Phase 2 (normalised tables, ready for migration from the JSON save)
create table if not exists public.channels (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  name text not null, niche text, audience text, subscribers int default 0, views bigint default 0,
  revenue numeric default 0, rpm numeric default 0, upload_schedule text, monetized boolean default false
);
create table if not exists public.agents (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  name text not null, role text not null, department text not null, level int default 1, xp int default 0,
  performance int default 70, instructions text, personality text, skills jsonb default '{}'::jsonb, channel_ids text[] default '{}'
);
create table if not exists public.projects (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  channel_id text references public.channels(id), title text not null, stage text not null, status text not null,
  priority text, created_tick int, deadline_tick int, stage_quality jsonb default '{}'::jsonb
);
create table if not exists public.tasks (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  project_id text references public.projects(id), agent_id text references public.agents(id),
  title text not null, description text, stage text, priority text, status text not null, progress numeric default 0,
  deadline_tick int, dependencies text[] default '{}', comments jsonb default '[]'::jsonb, documents jsonb default '[]'::jsonb, result text
);
create table if not exists public.thread_posts (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  author_id text, department text, kind text, content text, tick int, likes text[] default '{}', comments jsonb default '[]'::jsonb
);
create table if not exists public.ledger (
  id text primary key, save_id text references public.game_saves(id) on delete cascade,
  day int, channel_id text, category text, amount numeric, note text
);

-- Enable RLS and add policies appropriate for your auth model before going to production.
alter table public.game_saves enable row level security;
