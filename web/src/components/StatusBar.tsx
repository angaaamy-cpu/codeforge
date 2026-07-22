import type { Project, StepStatus } from '@/lib/supabase'
import { Activity, Clock, FileCode, CheckCircle2 } from 'lucide-react'

export default function StatusBar({ running, steps, active }: { running: boolean; steps: StepStatus[]; active: Project | null }) {
  const done = steps.filter(s => s.state === 'done').length
  const total = steps.length
  const elapsed = steps.reduce((acc, s) => acc + (s.duration_ms ?? 0), 0)

  return (
    <footer className="h-7 shrink-0 glass border-t border-ink-700 flex items-center px-3 gap-4 text-[11px] text-ink-400 no-select">
      <div className="flex items-center gap-1.5">
        <span className={`w-1.5 h-1.5 rounded-full ${running ? 'bg-amber-400 animate-pulse-soft' : 'bg-emerald-400'}`} />
        {running ? 'يعمل' : 'جاهز'}
      </div>
      {active && (
        <>
          <Sep />
          <span className="flex items-center gap-1"><FileCode size={11} /> {active.file_count} ملف</span>
          <Sep />
          <span className="flex items-center gap-1"><CheckCircle2 size={11} /> {done}/{total} خطوة</span>
          <Sep />
          <span className="flex items-center gap-1"><Clock size={11} /> {(elapsed / 1000).toFixed(2)}ث</span>
        </>
      )}
      <div className="flex-1" />
      <span className="flex items-center gap-1.5"><Activity size={11} className="text-brand-400" /> CodeForge v1.0</span>
    </footer>
  )
}

const Sep = () => <span className="text-ink-700">·</span>
