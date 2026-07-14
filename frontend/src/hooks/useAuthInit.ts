'use client'
import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { tokenStorage } from '@/lib/api'

export function useAuthInit() {
  const { fetchMe, user } = useAuthStore()
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    const init = async () => {
      // Restore session from stored tokens if they exist
      await fetchMe()
      setIsInitialized(true)
    }
    init()
  }, [fetchMe])

  return isInitialized || !!user
}
