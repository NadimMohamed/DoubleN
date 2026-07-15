'use client'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'

const PUBLIC_ROUTES = ['/auth/login', '/auth/register', '/']

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Wait for hydration
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy">
        <div className="w-8 h-8 border-2 border-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  // Waiting for auth state to initialize (should be fast due to layout-level init)
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy">
        <div className="w-8 h-8 border-2 border-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  // Not authenticated and not on public route
  if (!isAuthenticated && !PUBLIC_ROUTES.includes(pathname)) {
    router.replace('/auth/login')
    return null
  }

  return <>{children}</>
}
