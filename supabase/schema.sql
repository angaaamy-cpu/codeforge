-- CodeForge Database Schema
-- Run this in your Supabase project → SQL Editor

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ─── Projects ────────────────────────────────────────────────────────────────
create table if not exists projects (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  title        text not null,
  description  text not null default '',
  status       text not null default 'building' check (status in ('building', 'done', 'error')),
  steps        jsonb not null default '[]',
  file_count   integer not null default 0,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

alter table projects enable row level security;
create policy "Users see own projects" on projects for all using (auth.uid() = user_id);

-- ─── Files ───────────────────────────────────────────────────────────────────
create table if not exists files (
  id           uuid primary key default gen_random_uuid(),
  project_id   uuid not null references projects(id) on delete cascade,
  user_id      uuid not null references auth.users(id) on delete cascade,
  path         text not null,
  content      text not null default '',
  size         integer not null default 0,
  source       text not null default 'generated',
  created_at   timestamptz not null default now(),
  unique (project_id, path)
);

alter table files enable row level security;
create policy "Users see own files" on files for all using (auth.uid() = user_id);

-- ─── Secrets / Variables / Links ─────────────────────────────────────────────
create table if not exists secrets (
  id           uuid primary key default gen_random_uuid(),
  project_id   uuid not null references projects(id) on delete cascade,
  kind         text not null default 'secret' check (kind in ('secret', 'variable', 'link')),
  key          text not null,
  value        text not null default '',
  created_at   timestamptz not null default now()
);

alter table secrets enable row level security;
create policy "Users see own secrets" on secrets for all using (
  exists (select 1 from projects p where p.id = project_id and p.user_id = auth.uid())
);

-- ─── Agent Memory ─────────────────────────────────────────────────────────────
create table if not exists agent_memory (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  agent        text not null,
  context      text not null,
  tags         text[] not null default '{}',
  created_at   timestamptz not null default now()
);

alter table agent_memory enable row level security;
create policy "Users see own agent memory" on agent_memory for all using (auth.uid() = user_id);

-- ─── Indexes ─────────────────────────────────────────────────────────────────
create index if not exists projects_user_id_idx on projects(user_id);
create index if not exists files_project_id_idx on files(project_id);
create index if not exists secrets_project_id_idx on secrets(project_id);
create index if not exists agent_memory_user_agent_idx on agent_memory(user_id, agent);
