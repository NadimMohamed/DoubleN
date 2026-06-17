import type { Metadata, Viewport } from 'next'
import './globals.css'
import { Providers } from './providers'

export const metadata: Metadata = {
  title: { default: 'Double N Trading', template: '%s | Double N Trading' },
  description: 'Real-time cryptocurrency trading platform with live Binance data',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0A1628',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-navy text-white antialiased font-inter">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
