import { useEffect, useMemo, useState } from 'react'
import { AuthProvider, useAuth } from '@/lib/auth'
import { supabase, type Project, type StepStatus, type ProjectFile } from '@/lib/supabase'
import { PIPELINE, AGENTS, AGENT_MAP, routeTask, recallMemory, storeMemory, type AgentId } from '@/lib/engine'
import { listFiles, upsertFile } from '@/lib/storage'
import AuthScreen from '@/components/AuthScreen'
import Sidebar from '@/components/Sidebar'
import ChatPanel from '@/components/ChatPanel'
import PreviewPanel from '@/components/PreviewPanel'
import AgentBar from '@/components/AgentBar'
import StatusBar from '@/components/StatusBar'
import StepTracker from '@/components/StepTracker'
import SecretsPanel from '@/components/SecretsPanel'
import FilesPanel from '@/components/FilesPanel'
import AgentsPanel from '@/components/AgentsPanel'
import { Key, FolderArchive, Cpu, LogOut } from 'lucide-react'

const rand = (a: number, b: number) => Math.floor(a + Math.random() * (b - a))
const slugify = (s: string) =>
  s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, '').trim().replace(/\s+/g, '_').slice(0, 40) || 'project'

type LogEntry = { t: number; agent: string; msg: string; level: 'info' | 'ok' | 'warn' | 'err' }

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  )
}

function Shell() {
  const { user, loading, signOut } = useAuth()
  if (loading) return <div className="min-h-screen bg-ink-950" />
  if (!user) return <AuthScreen />
  return <Workbench onSignOut={signOut} userId={user.id} />
}

function Workbench({ onSignOut, userId }: { onSignOut: () => void; userId: string }) {
  const [projects, setProjects] = useState<Project[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [steps, setSteps] = useState<StepStatus[]>([])
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [files, setFiles] = useState<ProjectFile[]>([])
  const [previewHtml, setPreviewHtml] = useState<string | null>(null)
  const [panel, setPanel] = useState<'secrets' | 'files' | 'agents' | null>(null)

  const active = useMemo(() => projects.find(p => p.id === activeId) ?? null, [projects, activeId])

  useEffect(() => { loadProjects() }, [])

  async function loadProjects() {
    const { data } = await supabase.from('projects').select('*').order('created_at', { ascending: false }).limit(50)
    if (data) setProjects(data as Project[])
  }

  function pushLog(agent: string, msg: string, level: LogEntry['level'] = 'info') {
    setLogs(l => [...l.slice(-200), { t: Date.now(), agent, msg, level }])
  }

  async function startBuild(description: string) {
    if (!description.trim() || running) return
    setRunning(true); setLogs([])
    const title = slugify(description)
    const initialSteps: StepStatus[] = PIPELINE.map(s => ({ key: s.key, label: s.label, detail: s.detail, agent: s.agent, state: 'pending' }))
    setSteps(initialSteps)

    const { data, error } = await supabase.from('projects').insert({
      title, description, status: 'building', steps: initialSteps, file_count: 0, user_id: userId,
    }).select().single()

    if (error || !data) {
      pushLog('Manager', `فشل إنشاء المشروع: ${error?.message ?? 'unknown'}`, 'err')
      setRunning(false); return
    }
    const project = data as Project
    setActiveId(project.id)
    setProjects(p => [project, ...p])
    pushLog('Manager', `بدء بناء: ${title}`, 'info')

    // Recall memory for this kind of task
    const tags = extractTags(description)
    const recalled = await recallMemory('architect', tags, userId)
    if (recalled.length > 0) {
      pushLog('Architect', `تذكّر ${recalled.length} ذاكرة سابقة`, 'info')
    }

    let currentSteps = [...initialSteps]
    let fileCount = 0

    for (let i = 0; i < PIPELINE.length; i++) {
      const step = PIPELINE[i]
      const agent = AGENT_MAP[step.agent]
      currentSteps = currentSteps.map((s, idx) => idx === i ? { ...s, state: 'running' } : s)
      setSteps([...currentSteps])
      pushLog(agent.name_ar, `${step.label} — جارٍ`, 'info')

      await supabase.from('projects').update({ steps: currentSteps, updated_at: new Date().toISOString() }).eq('id', project.id)
      // record agent run
      const { data: runRow } = await supabase.from('agent_runs').insert({
        project_id: project.id, user_id: userId, agent: step.agent, task: step.label, status: 'running',
      }).select().single()

      const dur = rand(step.dur[0], step.dur[1])
      await new Promise(r => setTimeout(r, dur))

      if (step.key === 'develop') {
        // generate sample files and persist them
        const gen = generateProjectFiles(title)
        for (const f of gen) {
          try { await upsertFile(project.id, f.path, f.content, 'generated') } catch {}
        }
        fileCount = gen.length
        const fresh = await listFiles(project.id)
        setFiles(fresh)
      }

      currentSteps = currentSteps.map((s, idx) => idx === i ? { ...s, state: 'done', duration_ms: dur } : s)
      setSteps([...currentSteps])
      pushLog(agent.name_ar, `${step.label} — اكتمل (${dur}ms)`, 'ok')

      // update run
      if (runRow) {
        await supabase.from('agent_runs').update({ status: 'done', duration_ms: dur, result: step.detail }).eq('id', runRow.id)
      }
      await supabase.from('projects').update({ steps: currentSteps, file_count: fileCount, updated_at: new Date().toISOString() }).eq('id', project.id)

      // store a memory per step (experience accumulation)
      await storeMemory(step.agent, 'note', `${step.label} على «${title}»: ${step.detail}`, tags, userId, project.id, 0.5)
    }

    const finalProject: Project = { ...project, status: 'completed', steps: currentSteps, file_count: fileCount, updated_at: new Date().toISOString() }
    await supabase.from('projects').update({ status: 'completed', steps: currentSteps, file_count: fileCount, updated_at: finalProject.updated_at }).eq('id', project.id)
    setProjects(p => p.map(x => x.id === project.id ? finalProject : x))
    setPreviewHtml(buildPreviewHtml(title))
    pushLog('Manager', 'اكتمل البناء بنجاح', 'ok')
    setRunning(false)
  }

  async function deleteProject(id: string) {
    await supabase.from('projects').delete().eq('id', id)
    setProjects(p => p.filter(x => x.id !== id))
    if (activeId === id) { setActiveId(null); setSteps([]); setPreviewHtml(null); setFiles([]) }
  }

  async function selectProject(p: Project) {
    setActiveId(p.id)
    setSteps(p.steps ?? [])
    setPreviewHtml(p.status === 'completed' ? buildPreviewHtml(p.title) : null)
    setLogs([])
    const f = await listFiles(p.id)
    setFiles(f)
  }

  const currentAgent = (steps.find(s => s.state === 'running')?.agent ?? null) as AgentId | null

  return (
    <div className="h-screen flex flex-col bg-ink-950 text-ink-100 overflow-hidden">
      <header className="h-12 shrink-0 glass border-b border-ink-700 flex items-center px-4 gap-3 no-select">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center font-bold text-ink-950 text-sm">CF</div>
          <span className="font-semibold tracking-tight">CodeForge</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-ink-800 text-ink-400 font-mono">7 agents</span>
        </div>
        <AgentBar running={running} activeAgent={currentAgent} />
        <div className="flex-1" />
        <button onClick={() => setPanel('agents')} className="flex items-center gap-1 px-2 py-1 rounded-md text-ink-400 hover:text-ink-200 hover:bg-ink-800 text-xs"><Cpu size={13} /> الوكلاء</button>
        <button onClick={() => setPanel('secrets')} disabled={!activeId} className="flex items-center gap-1 px-2 py-1 rounded-md text-ink-400 hover:text-ink-200 hover:bg-ink-800 text-xs disabled:opacity-40"><Key size={13} /> الأسرار</button>
        <button onClick={() => setPanel('files')} disabled={!activeId} className="flex items-center gap-1 px-2 py-1 rounded-md text-ink-400 hover:text-ink-200 hover:bg-ink-800 text-xs disabled:opacity-40"><FolderArchive size={13} /> الملفات</button>
        <button onClick={onSignOut} className="flex items-center gap-1 px-2 py-1 rounded-md text-ink-400 hover:text-rose-400 hover:bg-ink-800 text-xs"><LogOut size={13} /> خروج</button>
      </header>

      <div className="flex-1 flex min-h-0">
        <Sidebar projects={projects} activeId={activeId} onSelect={selectProject} onDelete={deleteProject} files={files} />
        <main className="flex-1 flex flex-col min-w-0">
          <StepTracker steps={steps} running={running} />
          <div className="flex-1 flex min-h-0">
            <ChatPanel onSend={startBuild} running={running} logs={logs} />
            <PreviewPanel html={previewHtml} running={running} hasProject={!!active} />
          </div>
        </main>
      </div>

      <StatusBar running={running} steps={steps} active={active} />

      {panel === 'secrets' && <SecretsPanel projectId={activeId} onClose={() => setPanel(null)} />}
      {panel === 'files' && <FilesPanel projectId={activeId} onClose={() => setPanel(null)} />}
      {panel === 'agents' && <AgentsPanel onClose={() => setPanel(null)} userId={userId} />}
    </div>
  )
}

function extractTags(desc: string): string[] {
  const words = desc.toLowerCase().split(/\s+/).filter(w => w.length > 3)
  return Array.from(new Set(words)).slice(0, 5)
}

function generateProjectFiles(title: string): { path: string; content: string }[] {
  return [
    {
      path: 'index.html',
      content: `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>${title}</title><link rel="stylesheet" href="style.css"/></head><body><div class="hero"><h1>${title.replace(/_/g,' ')}</h1><p>مشروع توليد بواسطة CodeForge</p><a class="btn" href="#">ابدأ</a></div><script src="script.js"></script></body></html>`,
    },
    {
      path: 'style.css',
      content: `*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;background:#0a0b0f;color:#eef1f5}.hero{padding:80px 24px;text-align:center}.hero h1{font-size:40px;background:linear-gradient(90deg,#22d3ee,#10b981);-webkit-background-clip:text;color:transparent}.btn{display:inline-block;padding:10px 22px;border-radius:10px;background:linear-gradient(90deg,#22d3ee,#06b6d4);color:#0a0b0f;font-weight:600;text-decoration:none}`,
    },
    { path: 'script.js', content: `console.log('${title} ready');` },
    { path: 'README.md', content: `# ${title}\n\nمشروع تم توليده بواسطة CodeForge.\n` },
  ]
}

function buildPreviewHtml(title: string) {
  return `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>${title}</title>
<style>body{margin:0;font-family:system-ui,sans-serif;background:#0a0b0f;color:#eef1f5}.h{padding:64px 24px;text-align:center}.h h1{font-size:40px;margin:0 0 12px;background:linear-gradient(90deg,#22d3ee,#10b981);-webkit-background-clip:text;color:transparent}.h p{color:#8a93a6;max-width:520px;margin:0 auto 32px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;max-width:960px;margin:0 auto;padding:0 24px 64px}.c{background:#13161d;border:1px solid #252b3a;border-radius:16px;padding:24px}.c h3{margin:0 0 8px;color:#22d3ee;font-size:16px}.c p{margin:0;color:#b4bcc9;font-size:14px;line-height:1.6}.b{display:inline-block;padding:10px 22px;border-radius:10px;background:linear-gradient(90deg,#22d3ee,#06b6d4);color:#0a0b0f;font-weight:600;text-decoration:none}</style></head>
<body><div class="h"><h1>${title.replace(/_/g,' ')}</h1><p>مشروع تم توليده بواسطة CodeForge — منصة بناء المشاريع بالذكاء الاصطناعي.</p><a class="b" href="#">ابدأ الآن</a></div><div class="cards"><div class="c"><h3>سرعة</h3><p>بناء كامل خلال ثوانٍ من وصف نصي بسيط.</p></div><div class="c"><h3>جودة</h3><p>كود نظيف ومنظم مع توثيق وتقارير تلقائية.</p></div><div class="c"><h3>أمان</h3><p>مراجعة أمان تلقائية لكل مشروع قبل التسليم.</p></div></div></body></html>`
}
