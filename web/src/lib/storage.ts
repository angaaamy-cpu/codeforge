import { supabase, type ProjectFile, type Secret } from './supabase'

// ─── Files ────────────────────────────────────────────────────────────────────

export async function listFiles(projectId: string): Promise<ProjectFile[]> {
  const { data, error } = await supabase
    .from('files')
    .select('*')
    .eq('project_id', projectId)
    .order('path', { ascending: true })

  if (error) throw new Error(error.message)
  return (data ?? []) as ProjectFile[]
}

export async function getFile(fileId: string): Promise<ProjectFile | null> {
  const { data, error } = await supabase
    .from('files')
    .select('*')
    .eq('id', fileId)
    .single()

  if (error) return null
  return data as ProjectFile
}

// ─── Secrets ──────────────────────────────────────────────────────────────────

export async function listSecrets(projectId: string): Promise<Secret[]> {
  const { data, error } = await supabase
    .from('secrets')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: false })

  if (error) throw new Error(error.message)
  return (data ?? []) as Secret[]
}

export async function addSecret(
  projectId: string,
  kind: Secret['kind'],
  key: string,
  value: string,
): Promise<Secret> {
  const { data, error } = await supabase
    .from('secrets')
    .insert({ project_id: projectId, kind, key, value })
    .select()
    .single()

  if (error) throw new Error(error.message)
  return data as Secret
}

export async function deleteSecret(id: string): Promise<void> {
  const { error } = await supabase.from('secrets').delete().eq('id', id)
  if (error) throw new Error(error.message)
}
