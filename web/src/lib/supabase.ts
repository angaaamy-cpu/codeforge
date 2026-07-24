import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('[CodeForge] VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY is not set. Create a .env file from .env.example.')
}

export const supabase = createClient(supabaseUrl ?? '', supabaseAnonKey ?? '')

// ─── Types ────────────────────────────────────────────────────────────────────

export type StepStatus = {
  key: string
  label: string
  detail?: string
  agent?: string
  state: 'pending' | 'running' | 'done' | 'error'
  duration_ms?: number
}

export type Project = {
  id: string
  title: string
  description: string
  status: 'building' | 'done' | 'error'
  steps: StepStatus[]
  file_count: number
  user_id: string
  created_at: string
  updated_at: string
}

export type ProjectFile = {
  id: string
  project_id: string
  user_id: string
  path: string
  content: string
  size: number
  source: string
  created_at: string
}

export type Secret = {
  id: string
  project_id: string
  kind: 'secret' | 'variable' | 'link'
  key: string
  value: string
  created_at: string
}

export type AgentMemory = {
  id: string
  user_id: string
  agent: string
  context: string
  tags: string[]
  created_at: string
}
