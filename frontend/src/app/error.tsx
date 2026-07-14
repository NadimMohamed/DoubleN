'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen bg-navy flex items-center justify-center p-4">
      <div className="card p-6 text-center max-w-sm">
        <h1 className="text-xl font-bold text-danger mb-3">Something went wrong</h1>
        <p className="text-slate text-sm mb-4">{error.message || 'An unexpected error occurred'}</p>
        <button onClick={reset} className="btn-primary w-full py-2">
          Try again
        </button>
      </div>
    </div>
  )
}
