import { AGENTS, type AgentId } from '@/lib/engine'
import { Manager, Architect, Developer, QA, Security, Docs, Researcher } from '@/lib/icons'

const ICONS: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  Manager, Architect, Developer, QA, Security, Docs, Researcher,
}

export default function AgentBar({ running, activeAgent }: { running: boolean; activeAgent: AgentId | null }) {
  return (
    <div className="flex items-center gap-1">
      {AGENTS.map(a => {
        const Icon = ICONS[a.id] ?? Manager
        const isActive = running && activeAgent === a.id
        const isDim = running && activeAgent !== a.id
        return (
          <div
            key={a.id}
            className={`flex items-center gap-1 px-1.5 py-1 rounded-md transition-all duration-300 ${
              isActive ? 'bg-ink-800 ring-1 ring-brand-400/40' : isDim ? 'opacity-40' : 'opacity-80'
            }`}
            title={`${a.name_ar} — ${a.role_ar}`}
          >
            <span className={isActive ? 'animate-pulse-soft' : ''}>
              <Icon size={13} className={`text-${a.color}-400`} />
            </span>
            <span className={`text-[10px] ${isActive ? 'text-ink-100' : 'text-ink-400'}`}>{a.name_ar}</span>
          </div>
        )
      })}
    </div>
  )
}
