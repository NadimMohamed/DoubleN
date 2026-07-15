'use client'
import { useState } from 'react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { Settings as SettingsIcon, Bell, Palette, Clock, Lock } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    emailAlerts: true,
    tradingSignals: true,
    watchlistUpdates: true,
    darkMode: true,
    refreshInterval: 15,
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    if (settings.newPassword && settings.newPassword !== settings.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    localStorage.setItem('appSettings', JSON.stringify(settings))
    toast.success('Settings saved successfully')
  }

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <SettingsIcon className="w-6 h-6" />
                Settings
              </h1>
              <p className="text-slate text-sm mt-1">Manage your preferences and account settings</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="card p-6 lg:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                  <Bell className="w-5 h-5 text-blue" />
                  <h2 className="text-lg font-semibold text-white">Notifications</h2>
                </div>
                <div className="space-y-4">
                  {[
                    { key: 'emailAlerts', label: 'Price Alerts', desc: 'Get notified of large price movements' },
                    { key: 'tradingSignals', label: 'Trading Signals', desc: 'Receive alerts for new trading signals' },
                    { key: 'watchlistUpdates', label: 'Watchlist Updates', desc: 'Updates on your monitored symbols' },
                  ].map(({ key, label, desc }) => (
                    <label key={key} className="flex items-start gap-3 cursor-pointer hover:bg-panel-hover p-2 rounded">
                      <input
                        type="checkbox"
                        checked={settings[key as keyof typeof settings] as boolean}
                        onChange={(e) => handleChange(key, e.target.checked)}
                        className="mt-1 w-4 h-4 cursor-pointer"
                      />
                      <div>
                        <div className="text-sm font-medium text-white">{label}</div>
                        <div className="text-xs text-slate">{desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="card p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Palette className="w-5 h-5 text-blue" />
                    <h3 className="font-semibold text-white">Display</h3>
                  </div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.darkMode}
                      onChange={(e) => handleChange('darkMode', e.target.checked)}
                      className="w-4 h-4 cursor-pointer"
                    />
                    <span className="text-sm text-slate">Dark Mode</span>
                  </label>
                </div>

                <div className="card p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-blue" />
                    <h3 className="font-semibold text-white">Data Refresh</h3>
                  </div>
                  <div className="space-y-3">
                    <input
                      type="range"
                      min="5"
                      max="60"
                      step="5"
                      value={settings.refreshInterval}
                      onChange={(e) => handleChange('refreshInterval', parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-xs text-slate text-center">
                      Every {settings.refreshInterval} seconds
                    </div>
                  </div>
                </div>
              </div>

              <div className="card p-6 lg:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                  <Lock className="w-5 h-5 text-blue" />
                  <h2 className="text-lg font-semibold text-white">Security</h2>
                </div>
                <div className="space-y-4">
                  {[
                    { key: 'currentPassword', label: 'Current Password', type: 'password' },
                    { key: 'newPassword', label: 'New Password', type: 'password' },
                    { key: 'confirmPassword', label: 'Confirm Password', type: 'password' },
                  ].map(({ key, label, type }) => (
                    <div key={key}>
                      <label className="text-xs text-slate uppercase tracking-wider block mb-2">{label}</label>
                      <input
                        type={type}
                        value={settings[key as keyof typeof settings] as string}
                        onChange={(e) => handleChange(key, e.target.value)}
                        placeholder={`Enter ${label.toLowerCase()}`}
                        className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm focus:border-blue focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-3 flex justify-end">
                <button
                  onClick={handleSave}
                  className="btn-primary px-6 py-2"
                >
                  Save Settings
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
