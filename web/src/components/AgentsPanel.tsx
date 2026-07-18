import { useEffect, useState } from 'react'
import { X, Brain, ExternalLink, Cpu, BookOpen } from 'lucide-react'
import { AGENTS, type AgentId } from '@/lib/engine'
import { supabase, type AgentMemory } from '@/lib/supabase'

type Props = { onClose: () => void; userId: string }

export default function AgentsPanel({ onClose, userId }: Props) {
  const [mem, setMem] = useState<AgentMemory[]>([])
  const [sel, setSel] = useState<AgentId | 'all'>('all')

  useEffect(() => {
    supabase
      .from('agent_memory')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(50)
      .then(({ data }) => setMem((data ?? []) as AgentMemory[]))
  }, [userId])

  const filtered = sel === 'all' ? mem : mem.filter(m => m.agent === sel)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-3xl bg-ink-900 border border-ink-700 rounded-2xl shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-ink-700">
          <h2 className="font-semibold text-ink-100 flex items-center gap-2">
            <Cpu size={16} className="text-brand-400" /> الوكلاء السبعة
          </h2>
          <button onClick={onClose} className="text-ink-400 hover:text-ink-200"><X size={18} /></button>
        </div>

        <div className="p-5 overflow-y-auto flex-1 space-y-5">
          {/* Agents grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {AGENTS.map(a => (
              <div key={a.id} className="bg-ink-850 border border-ink-700 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`w-2.5 h-2.5 rounded-full bg-${a.color}-400`} />
                  <h3 className="font-semibold text-sm text-ink-100">{a.name_ar}</h3>
                  <span className="text-[10px] text-ink-500 font-mono ml-auto">{a.id}</span>
                </div>
                <p className="text-xs text-ink-400 mb-3">{a.role_ar}</p>
                <div className="space-y-1.5">
                  <p className="text-[10px] uppercase tracking-wider text-ink-500 font-semibold">مصادر مفتوحة</p>
                  {a.sources.map(s => (
                    <a key={s.url} href={s.url} target="_blank" rel="noreferrer"
                       className="flex items-center gap-1.5 text-xs text-brand-300 hover:text-brand-200">
                      <ExternalLink size={11} /> {s.name}
                      <span className="text-ink-500">— {s.note}</span>
                    </a>
                  ))}
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {a.handles.map(h => (
                    <span key={h} className="text-[10px] px-1.5 py-0.5 rounded bg-ink-800 text-ink-400 font-mono">{h}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Memory */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Brain size={14} className="text-brand-400" />
              <h3 className="text-sm font-semibold text-ink-100">ذاكرة الوكلاء</h3>
              <select
                value={sel}
                onChange={e => setSel(e.target.value as AgentId | 'all')}
                className="mr-auto bg-ink-850 border border-ink-700 rounded-md px-2 py-1 text-xs text-ink-200 focus-ring outline-none"
              >
                <option value="all">كل الوكلاء</option>
                {AGENTS.map(a => <option key={a.id} value={a.id}>{a.name_ar}</option>)}
              </select>
            </div>

            {filtered.length === 0 ? (
              <p className="text-xs text-ink-500 text-center py-6 flex items-center justify-center gap-2">
                <BookOpen size={13} /> لا توجد ذكريات بعد — تتراكم مع كل مهمة
              </p>
            ) : (
              <ul className="space-y-1.5">
                {filtered.map(m => (
                  <li key={m.id} className="bg-ink-850 border border-ink-700 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${kindColor(m.kind)}`}>{m.kind}</span>
                      <span className="text-[10px] text-ink-500 font-mono">{m.agent}</span>
                      <span className="text-[10px] text-ink-600 ml-auto">{new Date(m.created_at).toLocaleDateString('en-GB')}</span>
                    </div>
                    <p className="text-xs text-ink-300">{m.content}</p>
                    {m.tags?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {m.tags.map(t => <span key={t} className="text-[10px] text-brand-300 font-mono">#{t}</span>)}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function kindColor(k: string) {
  return {
    note: 'bg-ink-700 text-ink-300',
    lesson: 'bg-brand-500/10 text-brand-300',
    error: 'bg-rose-500/10 text-rose-400',
    fix: 'bg-emerald-500/10 text-emerald-400',
    preference: 'bg-amber-500/10 text-amber-400',
  }[k] ?? 'bg-ink-700 text-ink-300'
}
