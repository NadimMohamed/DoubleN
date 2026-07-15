'use client'
import type { ReactNode } from 'react'
import { useAuthInit } from '@/hooks/useAuthInit'

export default function AuthWrapper({ children }: { children: ReactNode }) {
  useAuthInit()
  return <>{children}</>
}
