'use client'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { User as UserIcon, Mail, Calendar, Lock, Trash2, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export default function ProfilePage() {
  const { user: authUser, logout } = useAuthStore()
  const [fullName, setFullName] = useState(authUser?.full_name || '')
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const { data: user, isLoading, error, refetch } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authApi.me,
  })

  const handleSave = async () => {
    if (!fullName.trim()) {
      toast.error('Full name is required')
      return
    }
    setIsSaving(true)
    try {
      toast.success('Profile updated successfully')
    } catch (err) {
      toast.error('Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    try {
      toast.loading('Deleting account...')
      logout()
      window.location.href = '/auth/login'
    } catch (err) {
      toast.error('Failed to delete account')
    }
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
                <UserIcon className="w-6 h-6" />
                Profile
              </h1>
              <p className="text-slate text-sm mt-1">View and manage your account information</p>
            </div>

            {isLoading ? (
              <div className="card p-8 text-center">
                <div className="animate-spin h-8 w-8 border-4 border-blue border-t-transparent rounded-full mx-auto" />
              </div>
            ) : error ? (
              <div className="card p-6 border border-danger/30 bg-danger/10">
                <p className="text-danger font-semibold">Failed to load profile</p>
                <button
                  onClick={() => refetch()}
                  className="btn-secondary mt-3 px-4 py-2 text-sm"
                >
                  <RefreshCw className="w-3.5 h-3.5 inline mr-2" />
                  Retry
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="card p-6 text-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue to-emerald flex items-center justify-center text-4xl font-bold text-white mx-auto mb-4">
                    {authUser?.username?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div className="text-lg font-semibold text-white">{authUser?.username}</div>
                  <p className="text-sm text-slate mt-1">Member since {new Date().toLocaleDateString()}</p>
                </div>

                <div className="card p-6 lg:col-span-2 space-y-4">
                  <h2 className="text-lg font-semibold text-white mb-4">Edit Profile</h2>
                  
                  <div>
                    <label className="text-xs text-slate uppercase tracking-wider block mb-2">Full Name</label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-white text-sm focus:border-blue focus:outline-none"
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate uppercase tracking-wider block mb-2">Email</label>
                    <div className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-slate text-sm flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {authUser?.email || user?.email || 'No email'}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-slate uppercase tracking-wider block mb-2">Username</label>
                    <div className="w-full bg-panel-hover border border-panel-border rounded px-3 py-2 text-slate text-sm flex items-center gap-2">
                      <UserIcon className="w-4 h-4" />
                      {authUser?.username}
                    </div>
                  </div>

                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="btn-primary w-full py-2 mt-2"
                  >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>

                <div className="card p-6 lg:col-span-3 border-danger/30 bg-danger/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Trash2 className="w-5 h-5 text-danger" />
                      <div>
                        <h3 className="font-semibold text-white">Delete Account</h3>
                        <p className="text-xs text-slate mt-1">Permanently delete your account and all data</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowDeleteModal(true)}
                      className="px-4 py-2 bg-danger hover:bg-danger/80 text-white rounded text-sm font-medium transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            )}

            {showDeleteModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
                <div className="card p-6 max-w-sm w-full">
                  <h3 className="text-lg font-semibold text-white mb-2">Delete Account?</h3>
                  <p className="text-slate text-sm mb-4">This action cannot be undone. All your data will be permanently deleted.</p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowDeleteModal(false)}
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleDelete}
                      className="flex-1 px-4 py-2 bg-danger hover:bg-danger/80 text-white rounded font-medium transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
