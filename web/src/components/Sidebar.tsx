import { useState } from 'react'
import { Folder, FileCode, ChevronRight, ChevronDown, History, Trash2, Plus, Layers } from 'lucide-react'
import type { Project } from '@/lib/supabase'

type Props = {
  projects: Project[]
  activeId: string | null
  onSelect: (p: Project) => void
  onDelete: (id: string) => void
  files: { path: string; size: number; lang?: string }[]
}

export default function Sidebar({ projects, activeId, onSelect, onDelete, files }: Props) {
  const [tab, setTab] = useState<'files' | 'history'>('files')
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ root: true })

  // Build tree from file paths
  const tree = buildTree(files.map(f => ({ path: f.path, size: f.size, lang: f.lang ?? 'txt' })))

  return (
    <aside className="w-64 shrink-0 bg-ink-900 border-r border-ink-700 flex flex-col no-select">
      {/* Tabs */}
      <div className="flex border-b border-ink-700 text-xs">
        <button
          onClick={() => setTab('files')}
          className={`flex-1 py-2.5 flex items-center justify-center gap-1.5 transition-colors ${tab === 'files' ? 'text-brand-300 border-b-2 border-brand-400 bg-ink-850' : 'text-ink-400 hover:text-ink-200'}`}
        >
          <Layers size={14} /> الملفات
        </button>
        <button
          onClick={() => setTab('history')}
          className={`flex-1 py-2.5 flex items-center justify-center gap-1.5 transition-colors ${tab === 'history' ? 'text-brand-300 border-b-2 border-brand-400 bg-ink-850' : 'text-ink-400 hover:text-ink-200'}`}
        >
          <History size={14} /> السجل
        </button>
      </div>

      {tab === 'files' ? (
        <div className="flex-1 overflow-y-auto py-2 text-sm">
          <p className="px-3 py-1.5 text-[10px] uppercase tracking-wider text-ink-500 font-semibold">المشروع الحالي</p>
          {files.length === 0 ? (
            <p className="px-3 py-6 text-center text-ink-500 text-xs">لا يوجد مشروع نشط</p>
          ) : (
            <TreeView node={tree} expanded={expanded} setExpanded={setExpanded} depth={0} />
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <div className="px-3 py-2 flex items-center justify-between">
            <p className="text-[10px] uppercase tracking-wider text-ink-500 font-semibold">المشاريع السابقة</p>
            <span className="text-[10px] text-ink-500">{projects.length}</span>
          </div>
          {projects.length === 0 ? (
            <p className="px-3 py-6 text-center text-ink-500 text-xs">لا يوجد سجل بعد</p>
          ) : (
            <ul className="space-y-1 px-2">
              {projects.map(p => (
                <li key={p.id}>
                  <div
                    onClick={() => onSelect(p)}
                    className={`group flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-colors ${activeId === p.id ? 'bg-ink-800 text-ink-100' : 'hover:bg-ink-850 text-ink-300'}`}
                  >
                    <StatusDot status={p.status} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium truncate">{p.title}</p>
                      <p className="text-[10px] text-ink-500 truncate">{p.description}</p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); onDelete(p.id) }}
                      className="opacity-0 group-hover:opacity-100 text-ink-500 hover:text-rose-400 transition-all"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </aside>
  )
}

function StatusDot({ status }: { status: string }) {
  const map: Record<string, string> = {
    planning: 'bg-ink-500',
    building: 'bg-amber-400 animate-pulse-soft',
    completed: 'bg-emerald-400',
    failed: 'bg-rose-400',
  }
  return <span className={`w-2 h-2 rounded-full shrink-0 ${map[status] ?? 'bg-ink-500'}`} />
}

type TreeNode = { name: string; path: string; children: TreeNode[]; isFile: boolean; size?: number }

function buildTree(files: { path: string; size: number; lang: string }[]): TreeNode {
  const root: TreeNode = { name: 'project', path: '', children: [], isFile: false }
  for (const f of files) {
    const parts = f.path.split('/')
    let cur = root
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]
      const isFile = i === parts.length - 1
      let child = cur.children.find(c => c.name === part)
      if (!child) {
        child = { name: part, path: parts.slice(0, i + 1).join('/'), children: [], isFile, size: isFile ? f.size : undefined }
        cur.children.push(child)
      }
      cur = child
    }
  }
  // sort: dirs first, then files, alpha
  function sort(n: TreeNode) {
    n.children.sort((a, b) => a.isFile === b.isFile ? a.name.localeCompare(b.name) : a.isFile ? 1 : -1)
    n.children.forEach(sort)
  }
  sort(root)
  return root
}

function TreeView({ node, expanded, setExpanded, depth }: { node: TreeNode; expanded: Record<string, boolean>; setExpanded: (r: Record<string, boolean>) => void; depth: number }) {
  return (
    <ul className={depth === 0 ? '' : 'ml-3 border-r border-ink-800'}>
      {node.children.map(child => (
        <li key={child.path}>
          {child.isFile ? (
            <div className="flex items-center gap-2 px-2 py-1 rounded hover:bg-ink-850 cursor-pointer text-ink-300" style={{ paddingRight: depth * 12 + 8 }}>
              <FileCode size={13} className="text-brand-400/70 shrink-0" />
              <span className="text-xs truncate">{child.name}</span>
              <span className="ml-auto text-[10px] text-ink-600">{formatSize(child.size ?? 0)}</span>
            </div>
          ) : (
            <>
              <div
                onClick={() => setExpanded({ ...expanded, [child.path]: !expanded[child.path] })}
                className="flex items-center gap-1 px-2 py-1 rounded hover:bg-ink-850 cursor-pointer text-ink-200"
                style={{ paddingRight: depth * 12 + 8 }}
              >
                {expanded[child.path] ? <ChevronDown size={13} className="text-ink-500" /> : <ChevronRight size={13} className="text-ink-500" />}
                <Folder size={13} className="text-amber-400/80 shrink-0" />
                <span className="text-xs font-medium">{child.name}</span>
              </div>
              {expanded[child.path] && <TreeView node={child} expanded={expanded} setExpanded={setExpanded} depth={depth + 1} />}
            </>
          )}
        </li>
      ))}
    </ul>
  )
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`
  return `${(bytes / 1024).toFixed(1)}K`
}
