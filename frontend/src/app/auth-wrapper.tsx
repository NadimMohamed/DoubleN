'use client'
import { useEffect } from 'react'
import { sessionManager } from '@/lib/sessionManager'
import { useAuthInit } from '@/hooks/useAuthInit'

export function AuthWrapper({ children }: { children: React.ReactNode }) {
  useAuthInit()

  useEffect(() => {
    // Check token on mount
    sessionManager.refreshTokenIfNeeded()
    
    // Schedule periodic checks
    sessionManager.scheduleNextRefresh()
    
    // Check on visibility change
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        sessionManager.refreshTokenIfNeeded()
      }
    }
    
    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  return <>{children}</>
}

export default AuthWrapper
