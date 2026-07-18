import type { StepStatus } from '@/lib/supabase'
import { CheckCircle2, Loader2, Circle, AlertCircle } from 'lucide-react'

export default function StepTracker({ steps, running }: { steps: StepStatus[]; running: boolean }) {
  if (steps.length === 0) {
    return (
      <div className="h-12 shrink-0 border-b border-ink-700 bg-ink-900 flex items-center px-4 text-xs text-ink-500 no-select">
        <span className="flex items-center gap-2">
          <Circle size={12} /> في انتظار وصف المشروع…
        </span>
      </div>
    )
  }

  const done = steps.filter(s => s.state === 'done').length
  const total = steps.length
  const pct = Math.round((done / total) * 100)
  const hasError = steps.some(s => s.state === 'error')

  return (
    <div className="shrink-0 border-b border-ink-700 bg-ink-900 px-4 py-2.5 no-select">
      {/* Progress bar — thin, top */}
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1 h-1 rounded-full bg-ink-800 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${hasError ? 'bg-rose-500' : 'bg-gradient-to-r from-brand-400 to-emerald-400'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className={`text-[11px] font-mono tabular-nums ${hasError ? 'text-rose-400' : 'text-ink-300'}`}>
          {done}/{total} · {pct}%
        </span>
      </div>

      {/* Steps as compact pills — no text flooding */}
      <div className="flex items-center gap-1.5 flex-wrap">
        {steps.map((s, i) => (
          <div
            key={s.key}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] transition-all duration-300 animate-slide-in ${
              s.state === 'done'    ? 'bg-emerald-500/10 text-emerald-400' :
              s.state === 'running' ? 'bg-brand-500/10 text-brand-300 ring-1 ring-brand-400/30' :
              s.state === 'error'   ? 'bg-rose-500/10 text-rose-400' :
              'bg-ink-800 text-ink-500'
            }`}
            title={s.detail}
          >
            {s.state === 'done'    ? <CheckCircle2 size={12} /> :
             s.state === 'running' ? <Loader2 size={12} className="animate-spin-slow" /> :
             s.state === 'error'   ? <AlertCircle size={12} /> :
                                     <Circle size={12} />}
            <span className="font-medium">{s.label}</span>
            {s.state === 'done' && s.duration_ms && (
              <span className="text-[10px] text-ink-500 font-mono">{s.duration_ms}ms</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
