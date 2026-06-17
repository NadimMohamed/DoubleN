import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-navy flex flex-col items-center justify-center gap-4 p-4">
      <div className="text-6xl font-black text-blue/20">404</div>
      <h1 className="text-xl font-bold text-white">Page not found</h1>
      <p className="text-slate text-sm text-center max-w-xs">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link href="/dashboard"
        className="mt-2 px-5 py-2.5 bg-blue hover:bg-blue-light text-white text-sm font-semibold rounded-lg transition-colors">
        Go to Dashboard
      </Link>
    </div>
  )
}
