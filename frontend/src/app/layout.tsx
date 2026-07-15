import type { ReactNode } from 'react'
import './globals.css'
import { Providers } from './providers'
import AuthWrapper from './auth-wrapper'

export const metadata = {
  title: { default: 'Double N Trading', template: '%s | Double N Trading' },
  description: 'Real-time cryptocurrency trading platform with live Binance data',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0A1628',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-navy text-white antialiased font-inter">
        <Providers>
          <AuthWrapper>{children}</AuthWrapper>
        </Providers>
      </body>
    </html>
  )
}
