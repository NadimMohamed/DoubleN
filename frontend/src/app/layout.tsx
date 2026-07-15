'use client'
import type { ReactNode } from 'react'
import './globals.css'
import { Providers } from './providers'
import { useAuthInit } from '@/hooks/useAuthInit'

export const metadata = {
  title: { default: 'Double N Trading', template: '%s | Double N Trading' },
  description: 'Real-time cryptocurrency trading platform with live Binance data',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0A1628',
}

function AuthInitWrapper({ children }: { children: ReactNode }) {
  useAuthInit()
  return <>{children}</>
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-navy text-white antialiased font-inter">
        <Providers>
          <AuthInitWrapper>{children}</AuthInitWrapper>
        </Providers>
      </body>
    </html>
  )
}
