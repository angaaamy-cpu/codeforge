import type { AgentId } from '@/lib/pipeline'
import { AGENTS } from '@/lib/pipeline'
import { Manager, Architect, Developer, QA } from '@/lib/icons'

const ICONS: Record<string, React.ComponentType<{ size?: number; className?: string }>> = { Manager, Architect, Developer, QA }

export default function AgentBar({ running, activeAgent }: { running: boolean; activeAgent: AgentId | null }) {
  return (
    <div className="flex items-center gap-1.5">
      {AGENTS.map(a => {
        const Icon = ICONS[a.icon]
        const isActive = running && activeAgent === a.id
        const isDim = running && activeAgent !== a.id
        return (
          <div
            key={a.id}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md transition-all duration-300 ${
              isActive ? 'bg-ink-800 ring-1 ring-brand-400/40' : isDim ? 'opacity-40' : 'opacity-80'
            }`}
            title={a.name}
          >
            <span className={isActive ? 'animate-pulse-soft' : ''}>
              <Icon size={14} className={`text-${a.color}-400`} />
            </span>
            <span className={`text-[11px] ${isActive ? 'text-ink-100' : 'text-ink-400'}`}>{a.name}</span>
          </div>
        )
      })}
    </div>
  )
}
