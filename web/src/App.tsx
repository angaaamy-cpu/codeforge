import { useEffect, useMemo, useState } from 'react'
import { supabase, type Project, type StepStatus } from '@/lib/supabase'
import { PIPELINE_STEPS, STEP_AGENT, STEP_DURATION, SAMPLE_FILES, AGENTS } from '@/lib/pipeline'
import Sidebar from '@/components/Sidebar'
import ChatPanel from '@/components/ChatPanel'
import PreviewPanel from '@/components/PreviewPanel'
import AgentBar from '@/components/AgentBar'
import StatusBar from '@/components/StatusBar'
import StepTracker from '@/components/StepTracker'

const rand = (min: number, max: number) => Math.floor(min + Math.random() * (max - min))
const slugify = (s: string) =>
  s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, '').trim().replace(/\s+/g, '_').slice(0, 40) || 'project'

export default function App() {
  const [projects, setProjects] = useState<Project[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [steps, setSteps] = useState<StepStatus[]>([])
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState<{ t: number; agent: string; msg: string; level: 'info' | 'ok' | 'warn' | 'err' }[]>([])
  const [files] = useState(SAMPLE_FILES)
  const [previewHtml, setPreviewHtml] = useState<string | null>(null)

  const active = useMemo(() => projects.find(p => p.id === activeId) ?? null, [projects, activeId])

  // Load history on mount
  useEffect(() => { loadProjects() }, [])

  async function loadProjects() {
    const { data } = await supabase.from('projects').select('*').order('created_at', { ascending: false }).limit(50)
    if (data) setProjects(data as Project[])
  }

  function pushLog(agent: string, msg: string, level: 'info' | 'ok' | 'warn' | 'err' = 'info') {
    setLogs(l => [...l.slice(-200), { t: Date.now(), agent, msg, level }])
  }

  async function startBuild(description: string) {
    if (!description.trim() || running) return
    setRunning(true)
    setLogs([])
    const title = slugify(description)
    const initialSteps: StepStatus[] = PIPELINE_STEPS.map(s => ({ ...s, state: 'pending' }))
    setSteps(initialSteps)

    // Insert project row
    const { data, error } = await supabase.from('projects').insert({
      title,
      description,
      status: 'building',
      steps: initialSteps,
      file_count: 0,
    }).select().single()

    if (error || !data) {
      pushLog('Manager', `فشل إنشاء المشروع: ${error?.message ?? 'unknown'}`, 'err')
      setRunning(false)
      return
    }
    const project = data as Project
    setActiveId(project.id)
    setProjects(p => [project, ...p])
    pushLog('Manager', `بدء بناء: ${title}`, 'info')

    // Run pipeline steps sequentially with compact status updates
    let currentSteps = [...initialSteps]
    let fileCount = 0
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      const step = PIPELINE_STEPS[i]
      const agentId = STEP_AGENT[step.key]
      const agentName = AGENTS.find(a => a.id === agentId)?.name ?? agentId

      // mark running
      currentSteps = currentSteps.map((s, idx) => idx === i ? { ...s, state: 'running' } : s)
      setSteps([...currentSteps])
      pushLog(agentName, `${step.label} — جارٍ`, 'info')

      // sync to DB (lightweight — only status + current steps)
      await supabase.from('projects').update({ steps: currentSteps, updated_at: new Date().toISOString() }).eq('id', project.id)

      const [lo, hi] = STEP_DURATION[step.key]
      const dur = rand(lo, hi)
      await new Promise(r => setTimeout(r, dur))

      // accumulate files during develop step
      if (step.key === 'develop') fileCount = SAMPLE_FILES.length

      // mark done
      currentSteps = currentSteps.map((s, idx) => idx === i ? { ...s, state: 'done', duration_ms: dur } : s)
      setSteps([...currentSteps])
      pushLog(agentName, `${step.label} — اكتمل (${dur}ms)`, 'ok')
      await supabase.from('projects').update({ steps: currentSteps, file_count: fileCount, updated_at: new Date().toISOString() }).eq('id', project.id)
    }

    // finalize
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
    if (activeId === id) { setActiveId(null); setSteps([]); setPreviewHtml(null) }
  }

  function selectProject(p: Project) {
    setActiveId(p.id)
    setSteps(p.steps ?? [])
    setPreviewHtml(p.status === 'completed' ? buildPreviewHtml(p.title) : null)
    setLogs([])
  }

  return (
    <div className="h-screen flex flex-col bg-ink-950 text-ink-100 overflow-hidden">
      {/* Top bar */}
      <header className="h-12 shrink-0 glass border-b border-ink-700 flex items-center px-4 gap-3 no-select">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center font-bold text-ink-950 text-sm">CF</div>
          <span className="font-semibold tracking-tight">CodeForge</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-ink-800 text-ink-400 font-mono">v1.0</span>
        </div>
        <div className="flex-1" />
        <AgentBar running={running} activeAgent={currentAgent(steps)} />
      </header>

      {/* Main 3-pane layout */}
      <div className="flex-1 flex min-h-0">
        <Sidebar
          projects={projects}
          activeId={activeId}
          onSelect={selectProject}
          onDelete={deleteProject}
          files={files}
        />

        <main className="flex-1 flex flex-col min-w-0">
          {/* Step tracker — compact, always visible, no flooding */}
          <StepTracker steps={steps} running={running} />

          {/* Chat + Preview split */}
          <div className="flex-1 flex min-h-0">
            <ChatPanel onSend={startBuild} running={running} logs={logs} />
            <PreviewPanel html={previewHtml} running={running} hasProject={!!active} />
          </div>
        </main>
      </div>

      <StatusBar running={running} steps={steps} active={active} />
    </div>
  )
}

function currentAgent(steps: StepStatus[]) {
  const running = steps.find(s => s.state === 'running')
  if (!running) return null
  return STEP_AGENT[running.key] ?? null
}

function buildPreviewHtml(title: string) {
  return `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>${title}</title>
<style>
  body{margin:0;font-family:system-ui,sans-serif;background:#0a0b0f;color:#eef1f5}
  .h{padding:64px 24px;text-align:center}
  .h h1{font-size:40px;margin:0 0 12px;background:linear-gradient(90deg,#22d3ee,#10b981);-webkit-background-clip:text;color:transparent}
  .h p{color:#8a93a6;max-width:520px;margin:0 auto 32px}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;max-width:960px;margin:0 auto;padding:0 24px 64px}
  .c{background:#13161d;border:1px solid #252b3a;border-radius:16px;padding:24px}
  .c h3{margin:0 0 8px;color:#22d3ee;font-size:16px}
  .c p{margin:0;color:#b4bcc9;font-size:14px;line-height:1.6}
  .b{display:inline-block;padding:10px 22px;border-radius:10px;background:linear-gradient(90deg,#22d3ee,#06b6d4);color:#0a0b0f;font-weight:600;text-decoration:none}
</style></head>
<body>
  <div class="h">
    <h1>${title.replace(/_/g, ' ')}</h1>
    <p>مشروع تم توليده بواسطة CodeForge — منصة بناء المشاريع بالذكاء الاصطناعي.</p>
    <a class="b" href="#">ابدأ الآن</a>
  </div>
  <div class="cards">
    <div class="c"><h3>سرعة</h3><p>بناء كامل خلال ثوانٍ من وصف نصي بسيط.</p></div>
    <div class="c"><h3>جودة</h3><p>كود نظيف ومنظم مع توثيق وتقارير تلقائية.</p></div>
    <div class="c"><h3>أمان</h3><p>مراجعة أمان تلقائية لكل مشروع قبل التسليم.</p></div>
  </div>
</body></html>`
}
