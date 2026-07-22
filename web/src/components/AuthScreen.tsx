import { useState } from 'react'
import { useAuth } from '@/lib/auth'
import { Loader2, Sparkles } from 'lucide-react'

export default function AuthScreen() {
  const { signIn, signUp } = useAuth()
  const [mode, setMode] = useState<'in' | 'up'>('up')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return
    setBusy(true); setError(null)
    const fn = mode === 'in' ? signIn : signUp
    const { error } = await fn(email, password)
    if (error) setError(error)
    setBusy(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-950 grid-bg p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center font-bold text-ink-950 text-xl">CF</div>
          <h1 className="text-2xl font-bold text-ink-100">CodeForge</h1>
          <p className="text-sm text-ink-400 mt-1">منصة بناء المشاريع بالذكاء الاصطناعي</p>
        </div>

        <div className="glass border border-ink-700 rounded-2xl p-6">
          <div className="flex bg-ink-850 rounded-lg p-1 mb-5">
            <button
              onClick={() => setMode('up')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'up' ? 'bg-brand-500 text-ink-950' : 'text-ink-400 hover:text-ink-200'}`}
            >حساب جديد</button>
            <button
              onClick={() => setMode('in')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${mode === 'in' ? 'bg-brand-500 text-ink-950' : 'text-ink-400 hover:text-ink-200'}`}
            >تسجيل دخول</button>
          </div>

          <form onSubmit={submit} className="space-y-3">
            <div>
              <label className="block text-xs text-ink-400 mb-1">البريد الإلكتروني</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full bg-ink-850 border border-ink-700 rounded-lg px-3 py-2 text-sm text-ink-100 focus-ring outline-none"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-xs text-ink-400 mb-1">كلمة المرور</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full bg-ink-850 border border-ink-700 rounded-lg px-3 py-2 text-sm text-ink-100 focus-ring outline-none"
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-xs text-rose-400 bg-rose-500/10 rounded-md px-3 py-2">{error}</p>}

            <button
              type="submit"
              disabled={busy}
              className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-400 disabled:bg-ink-800 text-ink-950 font-semibold text-sm py-2.5 rounded-lg transition-colors"
            >
              {busy ? <Loader2 size={15} className="animate-spin-slow" /> : <Sparkles size={15} />}
              {mode === 'up' ? 'إنشاء الحساب' : 'دخول'}
            </button>
          </form>

          <p className="text-[10px] text-ink-500 mt-4 text-center">
            بإنشاء حساب تصبح مشاريعك معزولة ومرتبطة بحسابك.
          </p>
        </div>
      </div>
    </div>
  )
}
