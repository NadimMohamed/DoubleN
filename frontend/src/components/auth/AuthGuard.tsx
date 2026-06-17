'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, fetchMe } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    fetchMe().then(() => {
      if (!useAuthStore.getState().isAuthenticated) {
        router.replace('/auth/login')
      }
    })
  }, [fetchMe, router])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy">
        <div className="w-8 h-8 border-2 border-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return <>{children}</>
}
