import { Loader2, Monitor, Smartphone, RefreshCw, Globe } from 'lucide-react'
import { useState } from 'react'

export default function PreviewPanel({ html, running, hasProject }: { html: string | null; running: boolean; hasProject: boolean }) {
  const [device, setDevice] = useState<'desktop' | 'mobile'>('desktop')
  const [reloadKey, setReloadKey] = useState(0)

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-ink-850">
      {/* Preview toolbar */}
      <div className="h-9 shrink-0 border-b border-ink-700 flex items-center px-3 gap-2 no-select">
        <div className="flex items-center gap-1.5 text-[11px] text-ink-400">
          <Globe size={12} className="text-brand-400" />
          المعاينة
        </div>
        <div className="flex-1" />
        {html && (
          <>
            <div className="flex items-center bg-ink-800 rounded-md p-0.5">
              <button
                onClick={() => setDevice('desktop')}
                className={`p-1 rounded ${device === 'desktop' ? 'bg-ink-700 text-brand-300' : 'text-ink-500 hover:text-ink-300'}`}
              ><Monitor size={12} /></button>
              <button
                onClick={() => setDevice('mobile')}
                className={`p-1 rounded ${device === 'mobile' ? 'bg-ink-700 text-brand-300' : 'text-ink-500 hover:text-ink-300'}`}
              ><Smartphone size={12} /></button>
            </div>
            <button
              onClick={() => setReloadKey(k => k + 1)}
              className="p-1 rounded text-ink-500 hover:text-ink-300 hover:bg-ink-800"
            ><RefreshCw size={12} /></button>
          </>
        )}
      </div>

      {/* Preview body */}
      <div className="flex-1 flex items-center justify-center overflow-hidden p-4 grid-bg">
        {running && !html ? (
          <div className="flex flex-col items-center gap-3 text-ink-400">
            <Loader2 size={28} className="animate-spin-slow text-brand-400" />
            <p className="text-xs">جارٍ بناء المعاينة…</p>
          </div>
        ) : html ? (
          <div
            className="bg-white rounded-lg shadow-2xl overflow-hidden transition-all duration-300"
            style={{ width: device === 'desktop' ? '100%' : '390px', height: '100%', maxHeight: '100%' }}
          >
            <iframe
              key={reloadKey}
              srcDoc={html}
              title="preview"
              className="w-full h-full border-0"
              sandbox="allow-scripts"
            />
          </div>
        ) : (
          <div className="text-center text-ink-500">
            <div className="w-16 h-16 mx-auto mb-3 rounded-2xl bg-ink-800 flex items-center justify-center">
              <Monitor size={28} className="text-ink-600" />
            </div>
            <p className="text-sm">{hasProject ? 'المعاينة ستظهر هنا عند اكتمال البناء' : 'المعاينة تظهر هنا بعد البناء'}</p>
          </div>
        )}
      </div>
    </div>
  )
}
