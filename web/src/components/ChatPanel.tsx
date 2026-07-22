import { useEffect, useRef, useState } from 'react'
import { Send, Loader2, Sparkles, ChevronDown, ChevronRight } from 'lucide-react'

type LogEntry = { t: number; agent: string; msg: string; level: 'info' | 'ok' | 'warn' | 'err' }

export default function ChatPanel({ onSend, running, logs }: { onSend: (d: string) => void; running: boolean; logs: LogEntry[] }) {
  const [input, setInput] = useState('')
  const [showLogs, setShowLogs] = useState(false)
  const logEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [logs, showLogs])

  const submit = () => {
    if (!input.trim() || running) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <div className="w-[420px] shrink-0 border-r border-ink-700 bg-ink-900 flex flex-col min-h-0">
      {/* Prompt area */}
      <div className="p-4 border-b border-ink-700">
        <label className="flex items-center gap-2 text-xs text-ink-400 mb-2">
          <Sparkles size={13} className="text-brand-400" />
          صف مشروعك
        </label>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit() }}
          disabled={running}
          placeholder="مثال: صفحة هبوط لشركة ناشئة مع 3 خدمات ونموذج تواصل"
          className="w-full h-24 resize-none bg-ink-850 border border-ink-700 rounded-lg p-3 text-sm text-ink-100 placeholder-ink-500 focus-ring outline-none disabled:opacity-50"
        />
        <div className="flex items-center justify-between mt-2">
          <span className="text-[10px] text-ink-500">⌘/Ctrl + Enter للإرسال</span>
          <button
            onClick={submit}
            disabled={running || !input.trim()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-500 hover:bg-brand-400 disabled:bg-ink-800 disabled:text-ink-500 text-ink-950 text-xs font-semibold transition-colors"
          >
            {running ? <Loader2 size={13} className="animate-spin-slow" /> : <Send size={13} />}
            {running ? 'جارٍ البناء…' : 'ابنِ الآن'}
          </button>
        </div>
      </div>

      {/* Collapsible activity log — collapsed by default to avoid flooding */}
      <div className="flex-1 flex flex-col min-h-0">
        <button
          onClick={() => setShowLogs(s => !s)}
          className="flex items-center gap-1.5 px-4 py-2 text-[11px] text-ink-400 hover:text-ink-200 border-b border-ink-700 no-select"
        >
          {showLogs ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          سجل النشاط
          <span className="text-ink-600">({logs.length})</span>
        </button>
        {showLogs && (
          <div className="flex-1 overflow-y-auto px-4 py-2 font-mono text-[11px] space-y-1">
            {logs.length === 0 ? (
              <p className="text-ink-600 py-4 text-center">لا يوجد نشاط بعد</p>
            ) : logs.map((l, i) => (
              <div key={i} className="flex gap-2 animate-fade-in">
                <span className="text-ink-600 shrink-0">{new Date(l.t).toLocaleTimeString('en-GB', { hour12: false })}</span>
                <span className={`shrink-0 font-semibold ${levelColor(l.level)}`}>[{l.agent}]</span>
                <span className="text-ink-300">{l.msg}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        )}
        {!showLogs && (
          <div className="flex-1 flex items-center justify-center text-center px-6">
            <div className="text-ink-500 text-xs">
              <Sparkles size={20} className="mx-auto mb-2 text-brand-400/60" />
              اكتب وصف مشروعك واضغط «ابنِ الآن».
              <br />النتائج تظهر كمؤشرات مضغوطة في الأعلى.
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function levelColor(level: LogEntry['level']) {
  return {
    info: 'text-brand-300',
    ok:   'text-emerald-400',
    warn: 'text-amber-400',
    err:  'text-rose-400',
  }[level]
}
