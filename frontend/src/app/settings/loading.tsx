export default function SettingsLoading() {
  return (
    <div className="flex h-screen overflow-hidden bg-navy">
      <div className="w-56 bg-panel-card border-r border-panel-border" />
      <div className="flex flex-col flex-1 min-w-0">
        <div className="h-14 border-b border-panel-border" />
        <main className="flex-1 overflow-y-auto p-6 space-y-6 animate-pulse">
          <div className="space-y-2">
            <div className="h-8 w-40 bg-panel-hover rounded" />
            <div className="h-4 w-60 bg-panel-hover rounded" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="card p-6 h-64 bg-panel-hover rounded" />
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}
