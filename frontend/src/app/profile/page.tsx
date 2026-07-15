'use client'
import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { User, Mail, Calendar, Shield } from 'lucide-react'

async function getCurrentUser() {
  const token = localStorage.getItem('access_token')
  if (!token) throw new Error('Not authenticated')
  
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
    { headers: { Authorization: `Bearer ${token}` } }
  )
  if (!response.ok) throw new Error('Failed to fetch user')
  return response.json()
}

export default function ProfilePage() {
  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
  })

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
  })

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        email: user.email || '',
      })
    }
  }, [user])

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white">Profile</h1>
              <p className="text-slate text-sm mt-1">Manage your account information</p>
            </div>

            {isLoading ? (
              <div className="animate-pulse">
                <div className="card p-6 space-y-4">
                  <div className="h-8 bg-panel-hover rounded w-1/3" />
                  <div className="h-10 bg-panel-hover rounded" />
                </div>
              </div>
            ) : user ? (
              <>
                {/* Profile Overview */}
                <div className="card p-6">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-16 h-16 rounded-full bg-blue/20 border-2 border-blue flex items-center justify-center">
                      <User className="w-8 h-8 text-blue" />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-white">{user.full_name || 'User'}</h2>
                      <p className="text-sm text-slate">{user.username}</p>
                      <div className="flex items-center gap-1 mt-2 text-xs text-emerald">
                        <Shield className="w-3 h-3" />
                        {user.is_verified ? 'Verified' : 'Unverified'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Account Details */}
                <div className="card p-6">
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Account Details</h3>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-panel-hover rounded">
                      <Mail className="w-5 h-5 text-slate" />
                      <div>
                        <p className="text-xs text-slate uppercase tracking-wider">Email</p>
                        <p className="text-white font-medium">{user.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 bg-panel-hover rounded">
                      <Calendar className="w-5 h-5 text-slate" />
                      <div>
                        <p className="text-xs text-slate uppercase tracking-wider">Member Since</p>
                        <p className="text-white font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Edit Profile */}
                <div className="card p-6">
                  <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Edit Profile</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-white block mb-2">Full Name</label>
                      <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-white block mb-2">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        disabled
                        className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm opacity-50"
                      />
                      <p className="text-xs text-slate mt-1">Email cannot be changed</p>
                    </div>
                    <button className="btn-primary">Save Changes</button>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className="card p-6 border border-danger/30 bg-danger/5">
                  <h3 className="text-sm font-semibold text-danger uppercase tracking-wider mb-4">Danger Zone</h3>
                  <button className="btn-danger text-sm">Delete Account</button>
                  <p className="text-xs text-slate mt-3">This action cannot be undone</p>
                </div>
              </>
            ) : null}
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
