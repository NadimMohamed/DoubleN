'use client'
import React, { useState } from 'react'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { Bell, Lock, Eye, Zap, Moon } from 'lucide-react'

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    signals: true,
    priceAlerts: true,
    news: false,
    email: true,
  })

  const [theme, setTheme] = useState('dark')
  const [refreshInterval, setRefreshInterval] = useState('5000')

  const handleNotificationChange = (key: string) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white">Settings</h1>
              <p className="text-slate text-sm mt-1">Manage your preferences and configuration</p>
            </div>

            {/* Notifications */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bell className="w-5 h-5 text-blue" />
                <h2 className="text-lg font-semibold text-white">Notifications</h2>
              </div>
              <div className="space-y-3">
                {[
                  { key: 'signals', label: 'Trading Signals', desc: 'Get notified of BUY/SELL signals' },
                  { key: 'priceAlerts', label: 'Price Alerts', desc: 'Alert when price reaches target' },
                  { key: 'news', label: 'Market News', desc: 'Breaking news and market updates' },
                  { key: 'email', label: 'Email Notifications', desc: 'Receive alerts via email' },
                ].map(({ key, label, desc }) => (
                  <div key={key} className="flex items-center justify-between p-3 bg-panel-hover rounded">
                    <div>
                      <p className="text-sm font-medium text-white">{label}</p>
                      <p className="text-xs text-slate mt-1">{desc}</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange(key)}
                      className={`relative w-12 h-6 rounded-full transition-colors ${
                        notifications[key as keyof typeof notifications] ? 'bg-blue' : 'bg-panel-border'
                      }`}
                    >
                      <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        notifications[key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Display Settings */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Eye className="w-5 h-5 text-blue" />
                <h2 className="text-lg font-semibold text-white">Display</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-white block mb-2">Theme</label>
                  <select
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>
              </div>
            </div>

            {/* API Settings */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-5 h-5 text-blue" />
                <h2 className="text-lg font-semibold text-white">API & Performance</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-white block mb-2">Data Refresh Interval (ms)</label>
                  <select
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(e.target.value)}
                    className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
                  >
                    <option value="3000">3 seconds (fast, more data usage)</option>
                    <option value="5000">5 seconds (standard)</option>
                    <option value="10000">10 seconds (slow, less data usage)</option>
                    <option value="30000">30 seconds (very slow)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Security */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Lock className="w-5 h-5 text-blue" />
                <h2 className="text-lg font-semibold text-white">Security</h2>
              </div>
              <button className="btn-secondary text-sm">Change Password</button>
              <p className="text-xs text-slate mt-3">Last password change: 30 days ago</p>
            </div>

            {/* Save Button */}
            <div className="flex gap-3">
              <button className="btn-primary">Save Settings</button>
              <button className="btn-secondary">Reset to Defaults</button>
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
