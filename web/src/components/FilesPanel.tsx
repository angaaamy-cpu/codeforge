import { useEffect, useState } from 'react'
import { FileCode, Upload, Download, Trash2, X, Github, Loader2, FolderArchive } from 'lucide-react'
import { listFiles, upsertFile, deleteFile, downloadFile, downloadProjectZip, importFromGitHub, fetchGitHubFile } from '@/lib/storage'
import type { ProjectFile } from '@/lib/supabase'

type Props = { projectId: string | null; onClose: () => void }

export default function FilesPanel({ projectId, onClose }: Props) {
  const [files, setFiles] = useState<ProjectFile[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [ghUrl, setGhUrl] = useState('')
  const [ghImporting, setGhImporting] = useState(false)

  useEffect(() => {
    if (!projectId) return
    listFiles(projectId).then(setFiles).catch(e => setErr(e.message))
  }, [projectId])

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = Array.from(e.target.files ?? [])
    if (!projectId || list.length === 0) return
    setBusy(true); setErr(null)
    try {
      for (const f of list) {
        const content = await f.text()
        const saved = await upsertFile(projectId, f.name, content, 'uploaded')
        setFiles(prev => {
          const idx = prev.findIndex(x => x.path === f.name)
          if (idx >= 0) { const c = [...prev]; c[idx] = saved; return c }
          return [...prev, saved]
        })
      }
    } catch (e: any) { setErr(e.message) }
    setBusy(false)
  }

  const onGitHubImport = async () => {
    if (!projectId || !ghUrl.trim()) return
    setGhImporting(true); setErr(null)
    try {
      const remote = await importFromGitHub(ghUrl.trim())
      let added = 0
      for (const r of remote.slice(0, 50)) {
        try {
          const content = await fetchGitHubFile(r.downloadUrl)
          await upsertFile(projectId, r.path, content, 'imported')
          added++
        } catch { /* skip individual failures */ }
      }
      setErr(`تم استيراد ${added} ملف من ${remote.length} متاح`)
      const fresh = await listFiles(projectId)
      setFiles(fresh)
    } catch (e: any) { setErr(e.message) }
    setGhImporting(false)
  }

  const remove = async (id: string, path: string) => {
    await deleteFile(id)
    setFiles(prev => prev.filter(x => x.id !== id))
  }

  const dl = (f: ProjectFile) => downloadFile(f.path, f.content)
  const dlZip = async () => {
    if (!projectId) return
    setBusy(true)
    try { await downloadProjectZip(projectId, 'project') }
    catch (e: any) { setErr(e.message) }
    setBusy(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-ink-900 border border-ink-700 rounded-2xl shadow-2xl flex flex-col max-h-[80vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-ink-700">
          <h2 className="font-semibold text-ink-100 flex items-center gap-2">
            <FileCode size={16} className="text-brand-400" /> الملفات
          </h2>
          <button onClick={onClose} className="text-ink-400 hover:text-ink-200"><X size={18} /></button>
        </div>

        <div className="p-5 overflow-y-auto flex-1 space-y-4">
          {/* Actions */}
          <div className="grid grid-cols-2 gap-2">
            <label className="flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-ink-850 border border-ink-700 hover:border-brand-400 cursor-pointer text-xs text-ink-200">
              {busy ? <Loader2 size={14} className="animate-spin-slow" /> : <Upload size={14} />}
              رفع ملفات
              <input type="file" multiple className="hidden" onChange={onUpload} />
            </label>
            <button
              onClick={dlZip}
              disabled={busy || files.length === 0}
              className="flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-ink-850 border border-ink-700 hover:border-brand-400 text-xs text-ink-200 disabled:opacity-50"
            >
              <FolderArchive size={14} /> تنزيل الكل (zip)
            </button>
          </div>

          {/* GitHub import */}
          <div className="bg-ink-850 border border-ink-700 rounded-lg p-3">
            <p className="text-xs text-ink-300 mb-2 flex items-center gap-1.5"><Github size={13} /> استيراد من مستودع GitHub عام</p>
            <div className="flex gap-2">
              <input
                value={ghUrl} onChange={e => setGhUrl(e.target.value)}
                placeholder="https://github.com/owner/repo"
                className="flex-1 bg-ink-900 border border-ink-700 rounded-md px-2 py-1.5 text-xs text-ink-100 focus-ring outline-none"
              />
              <button
                onClick={onGitHubImport}
                disabled={ghImporting || !ghUrl.trim()}
                className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-brand-500 hover:bg-brand-400 disabled:bg-ink-800 text-ink-950 text-xs font-semibold"
              >
                {ghImporting ? <Loader2 size={13} className="animate-spin-slow" /> : <Github size={13} />} استيراد
              </button>
            </div>
          </div>

          {err && <p className="text-xs text-amber-400 bg-amber-500/10 rounded-md px-3 py-2">{err}</p>}

          {/* File list */}
          <ul className="space-y-1">
            {files.length === 0 && <li className="text-xs text-ink-500 text-center py-6">لا توجد ملفات بعد</li>}
            {files.map(f => (
              <li key={f.id} className="group flex items-center gap-2 bg-ink-850 border border-ink-700 rounded-lg px-3 py-2">
                <FileCode size={13} className="text-brand-400/80 shrink-0" />
                <span className="text-xs font-mono text-ink-200 flex-1 truncate">{f.path}</span>
                <span className="text-[10px] text-ink-500">{(f.size / 1024).toFixed(1)}K</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${f.source === 'uploaded' ? 'bg-emerald-500/10 text-emerald-400' : f.source === 'imported' ? 'bg-amber-500/10 text-amber-400' : 'bg-ink-700 text-ink-400'}`}>{f.source}</span>
                <button onClick={() => dl(f)} className="text-ink-500 hover:text-brand-300"><Download size={12} /></button>
                <button onClick={() => remove(f.id, f.path)} className="text-ink-500 hover:text-rose-400 opacity-0 group-hover:opacity-100"><Trash2 size={12} /></button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
