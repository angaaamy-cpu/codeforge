// ─── Agent types ─────────────────────────────────────────────────────────────

export type AgentId =
  | 'Manager'
  | 'Architect'
  | 'Developer'
  | 'QA'
  | 'Security'
  | 'Docs'
  | 'Researcher'

export type Agent = {
  id: AgentId
  name_ar: string
  role_ar: string
  color: 'brand' | 'emerald' | 'amber' | 'rose' | 'violet' | 'sky' | 'teal'
  handles: string[]
  sources: { url: string; name: string; note: string }[]
}

// ─── Agents registry ─────────────────────────────────────────────────────────

export const AGENTS: Agent[] = [
  {
    id: 'Manager',
    name_ar: 'المدير',
    role_ar: 'تنسيق المهام وتقسيم المشروع',
    color: 'brand',
    handles: ['planning', 'coordination', 'breakdown'],
    sources: [
      { url: 'https://github.com/joaomdmoura/crewAI', name: 'CrewAI', note: 'إطار عمل الوكلاء المتعددين' },
    ],
  },
  {
    id: 'Researcher',
    name_ar: 'الباحث',
    role_ar: 'البحث عن مراجع وأكواد مشابهة',
    color: 'sky',
    handles: ['search', 'reference', 'inspiration'],
    sources: [
      { url: 'https://github.com', name: 'GitHub', note: 'مستودعات مفتوحة المصدر' },
      { url: 'https://stackoverflow.com', name: 'Stack Overflow', note: 'حلول تقنية' },
    ],
  },
  {
    id: 'Architect',
    name_ar: 'المعماري',
    role_ar: 'تصميم هيكل المشروع والتقنيات',
    color: 'violet',
    handles: ['stack', 'structure', 'design'],
    sources: [
      { url: 'https://12factor.net', name: '12-Factor App', note: 'مبادئ التطبيقات الحديثة' },
    ],
  },
  {
    id: 'Developer',
    name_ar: 'المطور',
    role_ar: 'كتابة الكود وتوليد الملفات',
    color: 'emerald',
    handles: ['coding', 'files', 'implementation'],
    sources: [
      { url: 'https://developer.mozilla.org', name: 'MDN', note: 'مرجع ويب شامل' },
    ],
  },
  {
    id: 'QA',
    name_ar: 'ضمان الجودة',
    role_ar: 'مراجعة الكود واكتشاف الأخطاء',
    color: 'amber',
    handles: ['testing', 'review', 'bugs'],
    sources: [
      { url: 'https://jestjs.io', name: 'Jest', note: 'اختبار JavaScript' },
    ],
  },
  {
    id: 'Security',
    name_ar: 'الأمان',
    role_ar: 'فحص الثغرات الأمنية',
    color: 'rose',
    handles: ['xss', 'injection', 'secrets', 'vulnerabilities'],
    sources: [
      { url: 'https://owasp.org', name: 'OWASP', note: 'دليل أمان التطبيقات' },
    ],
  },
  {
    id: 'Docs',
    name_ar: 'التوثيق',
    role_ar: 'كتابة README والتوثيق التقني',
    color: 'teal',
    handles: ['readme', 'docs', 'comments'],
    sources: [
      { url: 'https://readme.so', name: 'Readme.so', note: 'قوالب توثيق' },
    ],
  },
]

export const AGENT_MAP: Record<AgentId, Agent> = Object.fromEntries(
  AGENTS.map(a => [a.id, a]),
) as Record<AgentId, Agent>

// ─── Pipeline definition ──────────────────────────────────────────────────────

export type PipelineStep = {
  key: string
  label: string
  detail: string
  agent: AgentId
}

export const PIPELINE: PipelineStep[] = [
  { key: 'create',   label: 'إنشاء المشروع',  detail: 'تحليل الوصف وإنشاء مشروع جديد',  agent: 'Manager' },
  { key: 'research', label: 'البحث',           detail: 'البحث عن مراجع وأكواد مشابهة',   agent: 'Researcher' },
  { key: 'plan',     label: 'التخطيط',         detail: 'اختيار التقنيات وتصميم الهيكل',  agent: 'Architect' },
  { key: 'develop',  label: 'التطوير',         detail: 'كتابة الكود وتوليد الملفات',      agent: 'Developer' },
  { key: 'test',     label: 'الاختبار',         detail: 'مراجعة الكود وكشف الأخطاء',     agent: 'QA' },
  { key: 'security', label: 'مراجعة الأمان',    detail: 'فحص الثغرات الأمنية',           agent: 'Security' },
  { key: 'docs',     label: 'التوثيق',         detail: 'كتابة README والتوثيق التقني',   agent: 'Docs' },
]
