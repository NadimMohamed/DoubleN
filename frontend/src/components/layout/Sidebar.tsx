'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Star, LogOut, TrendingUp, Sliders, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/watchlist', label: 'Watchlist',  icon: Star },
  { href: '/trading',   label: 'Trading',    icon: TrendingUp },
  { href: '/settings',  label: 'Settings',   icon: Sliders },
  { href: '/profile',   label: 'Profile',    icon: User },
]

export function Sidebar() {
  const pathname = usePathname()
  const { logout, user } = useAuthStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/auth/login')
  }

  return (
    <aside className="w-56 bg-panel-card border-r border-panel-border flex flex-col h-screen flex-shrink-0">
      {/* Logo */}
      <div className="h-14 flex items-center gap-3 px-4 border-b border-panel-border">
        <svg width="28" height="28" viewBox="0 0 48 48" fill="none">
          <path d="M4 36V12L14 28V12" stroke="#0364D1" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M18 36V12L28 28V12" stroke="#0364D1" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M30 28L38 12L46 28" stroke="#00C48C" strokeWidth="3" strokeLinecap="round"/>
          <path d="M33 18L38 9L43 18" stroke="#00C48C" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <div>
          <div className="font-bold text-sm leading-none">DOUBLE N</div>
          <div className="text-[9px] text-slate tracking-[0.15em]">TRADING</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link key={href} href={href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                active
                  ? 'bg-blue/15 text-white border-r-2 border-blue -mr-3 pr-2.5'
                  : 'text-slate hover:text-white hover:bg-panel-hover',
              )}>
              <Icon className={cn('w-4 h-4 flex-shrink-0', active && 'text-blue')} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User + logout */}
      <div className="border-t border-panel-border p-3">
        {user && (
          <div className="flex items-center gap-2 px-3 py-2 mb-1">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue to-emerald flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
              {user.username[0].toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate">@{user.username}</p>
              <p className="text-[10px] text-slate truncate">{user.email}</p>
            </div>
          </div>
        )}
        <button onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate hover:text-danger hover:bg-danger/10 transition-colors">
          <LogOut className="w-4 h-4 flex-shrink-0" />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
