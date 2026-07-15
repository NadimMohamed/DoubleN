export default function ProfileLoading() {
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
            <div className="card p-6 h-64 bg-panel-hover rounded" />
            <div className="card p-6 h-64 bg-panel-hover rounded lg:col-span-2" />
          </div>
        </main>
      </div>
    </div>
  )
}
