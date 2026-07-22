import { useEffect, useState } from 'react'
import { Key, Link as LinkIcon, Variable, Plus, Trash2, X, Eye, EyeOff, ShieldAlert } from 'lucide-react'
import { listSecrets, addSecret, deleteSecret } from '@/lib/storage'
import type { Secret } from '@/lib/supabase'

type Props = { projectId: string | null; onClose: () => void }

export default function SecretsPanel({ projectId, onClose }: Props) {
  const [items, setItems] = useState<Secret[]>([])
  const [kind, setKind] = useState<Secret['kind']>('secret')
  const [key, setKey] = useState('')
  const [value, setValue] = useState('')
  const [reveal, setReveal] = useState<Record<string, boolean>>({})
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    listSecrets(projectId).then(setItems).catch(e => setErr(e.message))
  }, [projectId])

  const add = async () => {
    if (!projectId || !key.trim()) return
    try {
      const s = await addSecret(projectId, kind, key.trim(), value)
      setItems(i => [...i, s]); setKey(''); setValue('')
    } catch (e: any) { setErr(e.message) }
  }

  const remove = async (id: string) => {
    await deleteSecret(id); setItems(i => i.filter(x => x.id !== id))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-ink-900 border border-ink-700 rounded-2xl shadow-2xl flex flex-col max-h-[80vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-ink-700">
          <h2 className="font-semibold text-ink-100 flex items-center gap-2">
            <Key size={16} className="text-brand-400" /> الأسرار والمتغيرات والروابط
          </h2>
          <button onClick={onClose} className="text-ink-400 hover:text-ink-200"><X size={18} /></button>
        </div>

        <div className="px-5 py-3 bg-amber-500/10 border-b border-amber-500/20 text-[11px] text-amber-300 flex items-center gap-2">
          <ShieldAlert size={13} /> تُخزَّن القيم كما هي في قاعدة البيانات. لا تضع مفاتيح إنتاج حساسة دون تشفير.
        </div>

        <div className="p-5 overflow-y-auto flex-1">
          {/* Add form */}
          <div className="space-y-2 mb-5">
            <div className="flex gap-2">
              <select
                value={kind}
                onChange={e => setKind(e.target.value as Secret['kind'])}
                className="bg-ink-850 border border-ink-700 rounded-lg px-2 py-2 text-xs text-ink-100 focus-ring outline-none"
              >
                <option value="secret">سر</option>
                <option value="variable">متغير</option>
                <option value="link">رابط</option>
              </select>
              <input
                value={key} onChange={e => setKey(e.target.value)}
                placeholder="المفتاح (مثال: OPENAI_API_KEY)"
                className="flex-1 bg-ink-850 border border-ink-700 rounded-lg px-3 py-2 text-xs text-ink-100 focus-ring outline-none"
              />
            </div>
            <div className="flex gap-2">
              <input
                value={value} onChange={e => setValue(e.target.value)}
                placeholder="القيمة"
                className="flex-1 bg-ink-850 border border-ink-700 rounded-lg px-3 py-2 text-xs text-ink-100 focus-ring outline-none"
              />
              <button onClick={add} className="flex items-center gap-1 px-3 py-2 rounded-lg bg-brand-500 hover:bg-brand-400 text-ink-950 text-xs font-semibold">
                <Plus size={13} /> إضافة
              </button>
            </div>
          </div>

          {err && <p className="text-xs text-rose-400 mb-3">{err}</p>}

          {/* List */}
          <ul className="space-y-1.5">
            {items.length === 0 && <li className="text-xs text-ink-500 text-center py-6">لا توجد عناصر بعد</li>}
            {items.map(s => (
              <li key={s.id} className="group flex items-center gap-2 bg-ink-850 border border-ink-700 rounded-lg px-3 py-2">
                {s.kind === 'secret' ? <Key size={13} className="text-rose-400/80" /> :
                 s.kind === 'link' ? <LinkIcon size={13} className="text-brand-400/80" /> :
                 <Variable size={13} className="text-amber-400/80" />}
                <span className="text-xs font-mono text-ink-200 shrink-0">{s.key}</span>
                <span className="text-ink-600">=</span>
                <span className="text-xs font-mono text-ink-400 flex-1 truncate">
                  {s.kind === 'secret' && !reveal[s.id] ? '•'.repeat(Math.min(s.value.length, 20)) : s.value}
                </span>
                {s.kind === 'secret' && (
                  <button onClick={() => setReveal(r => ({ ...r, [s.id]: !r[s.id] }))} className="text-ink-500 hover:text-ink-300">
                    {reveal[s.id] ? <EyeOff size={12} /> : <Eye size={12} />}
                  </button>
                )}
                <button onClick={() => remove(s.id)} className="text-ink-500 hover:text-rose-400 opacity-0 group-hover:opacity-100">
                  <Trash2 size={12} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
