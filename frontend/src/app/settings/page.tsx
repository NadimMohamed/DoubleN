'use client'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { Sliders } from 'lucide-react'

export default function SettingsPage() {
  const [theme, setTheme] = useState<'dark' | 'light' | 'auto'>('dark')
  const [refreshInterval, setRefreshInterval] = useState(10)
  const [defaultInterval, setDefaultInterval] = useState('1h')
  const [notifications, setNotifications] = useState({
    priceAlerts: true,
    signalAlerts: true,
    trendAlerts: true,
    errorAlerts: true,
  })

  useEffect(() => {
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      const settings = JSON.parse(saved)
      setTheme(settings.theme)
      setRefreshInterval(settings.refreshInterval)
      setDefaultInterval(settings.defaultInterval)
      setNotifications(settings.notifications)
    }
  }, [])

  const saveSettings = () => {
    const settings = { theme, refreshInterval, defaultInterval, notifications }
    localStorage.setItem('userSettings', JSON.stringify(settings))
    toast.success('Settings saved')
  }

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-4">

            {/* Header */}
            <div className="mb-4">
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5 text-blue" />
                Settings
              </h1>
              <p className="text-sm text-slate mt-0.5">
                Manage your appearance, notifications, and account preferences
              </p>
            </div>

            <div className="max-w-2xl space-y-4">

              {/* Theme Settings */}
              <div className="card p-4">
                <h3 className="font-semibold text-white mb-3">Appearance</h3>
                <div className="space-y-2">
                  {(['dark', 'light', 'auto'] as const).map((t) => (
                    <label key={t} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={theme === t}
                        onChange={() => setTheme(t)}
                        className="w-4 h-4"
                      />
                      <span className="text-sm capitalize text-slate">{t} mode</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Notification Preferences */}
              <div className="card p-4">
                <h3 className="font-semibold text-white mb-3">Notifications</h3>
                <div className="space-y-3">
                  {[
                    { key: 'priceAlerts', label: 'Price Alerts' },
                    { key: 'signalAlerts', label: 'Trading Signals' },
                    { key: 'trendAlerts', label: 'Trend Changes' },
                    { key: 'errorAlerts', label: 'Error Notifications' },
                  ].map(({ key, label }) => (
                    <label key={key} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications[key as keyof typeof notifications]}
                        onChange={(e) => setNotifications({
                          ...notifications,
                          [key]: e.target.checked
                        })}
                        className="w-4 h-4"
                      />
                      <span className="text-sm text-slate">{label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Preferences */}
              <div className="card p-4">
                <h3 className="font-semibold text-white mb-3">Preferences</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-slate uppercase tracking-wider block mb-2">
                      Default Chart Interval
                    </label>
                    <select
                      value={defaultInterval}
                      onChange={(e) => setDefaultInterval(e.target.value)}
                      className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-sm text-white"
                    >
                      <option>1m</option>
                      <option>5m</option>
                      <option>15m</option>
                      <option>1h</option>
                      <option>4h</option>
                      <option>1d</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-slate uppercase tracking-wider block mb-2">
                      Data Refresh Interval (seconds)
                    </label>
                    <input
                      type="number"
                      min="5"
                      max="300"
                      value={refreshInterval}
                      onChange={(e) => setRefreshInterval(Number(e.target.value))}
                      className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-sm text-white"
                    />
                  </div>
                </div>
              </div>

              {/* Security */}
              <div className="card p-4">
                <h3 className="font-semibold text-white mb-3">Security</h3>
                <div className="space-y-3">
                  <button className="btn-secondary w-full text-sm">
                    Logout All Sessions
                  </button>
                  <button className="btn-secondary w-full text-sm">
                    Change Password
                  </button>
                </div>
              </div>

              {/* Save Button */}
              <button
                onClick={saveSettings}
                className="btn-primary w-full py-3 font-semibold"
              >
                Save Settings
              </button>

            </div>

          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
