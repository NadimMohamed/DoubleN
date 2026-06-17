'use client'
import { Bell } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export function Topbar() {
  const { user } = useAuthStore()
  return (
    <header className="h-14 bg-panel-card border-b border-panel-border flex items-center px-4 gap-4 flex-shrink-0">
      <div className="flex items-center gap-2 flex-1">
        <div className="flex items-center gap-1.5 bg-emerald/10 border border-emerald/20 rounded-full px-3 py-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse" />
          <span className="text-xs font-medium text-emerald">Live</span>
        </div>
        <span className="text-xs text-slate hidden sm:block">Binance market data</span>
      </div>
      <div className="flex items-center gap-2">
        <button className="relative w-8 h-8 flex items-center justify-center rounded-lg hover:bg-panel-hover text-slate hover:text-white transition-colors">
          <Bell className="w-4 h-4" />
        </button>
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue to-emerald flex items-center justify-center text-xs font-bold text-white">
          {user?.username?.[0]?.toUpperCase() ?? 'U'}
        </div>
      </div>
    </header>
  )
}
