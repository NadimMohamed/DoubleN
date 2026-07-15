'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Bell, CheckCircle, AlertCircle, Info, Trash2, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'

interface Notification {
  id: string
  type: string
  title: string
  message: string
  symbol?: string
  is_read: boolean
  created_at: string
  expires_at?: string
}

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data, refetch, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/notifications', {
        params: { limit: 20, offset: 0 }
      })
      return res.data
    },
    refetchInterval: 30000,
    staleTime: 10000,
  })

  const { mutate: markAsRead } = useMutation({
    mutationFn: async (ids: string[]) => {
      await axios.post('/api/v1/notifications/mark-as-read', {
        notification_ids: ids
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const { mutate: clearOld } = useMutation({
    mutationFn: async () => {
      await axios.post('/api/v1/notifications/clear', {
        older_than_days: 30
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const getIcon = (type: string) => {
    switch (type) {
      case 'price_alert':
      case 'trend_alert':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      case 'signal_alert':
        return <CheckCircle className="w-4 h-4 text-emerald" />
      case 'error_alert':
        return <AlertCircle className="w-4 h-4 text-danger" />
      default:
        return <Info className="w-4 h-4 text-blue" />
    }
  }

  const unread = data?.unread_count || 0

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 hover:bg-panel-hover rounded-lg transition-colors"
        title="Notifications"
      >
        <Bell className="w-5 h-5 text-slate" />
        {unread > 0 && (
          <span className="absolute top-0 right-0 w-2 h-2 bg-danger rounded-full animate-pulse" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-12 w-96 card p-4 max-h-[600px] overflow-y-auto z-50 shadow-lg border border-panel-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">Notifications</h3>
              {unread > 0 && (
                <p className="text-xs text-slate">{unread} unread</p>
              )}
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-panel-hover rounded"
            >
              <X className="w-4 h-4 text-slate" />
            </button>
          </div>

          {isLoading ? (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => (
                <div key={i} className="animate-pulse h-16 bg-panel-hover rounded" />
              ))}
            </div>
          ) : data?.notifications?.length === 0 ? (
            <div className="text-center py-8">
              <Bell className="w-8 h-8 text-slate/30 mx-auto mb-2" />
              <p className="text-sm text-slate">No notifications yet</p>
            </div>
          ) : (
            <>
              <div className="space-y-2 mb-4">
                {data.notifications.map((notif: Notification) => (
                  <div
                    key={notif.id}
                    className={cn(
                      'p-3 rounded-lg text-sm border transition-colors',
                      notif.is_read
                        ? 'bg-panel-hover border-panel-border'
                        : 'bg-blue/10 border-blue/30'
                    )}
                  >
                    <div className="flex items-start gap-2">
                      {getIcon(notif.type)}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white">{notif.title}</p>
                        <p className="text-xs text-slate mt-0.5 break-words">
                          {notif.message}
                        </p>
                        {notif.symbol && (
                          <p className="text-xs text-blue mt-1">
                            {notif.symbol}
                          </p>
                        )}
                      </div>
                      {!notif.is_read && (
                        <button
                          onClick={() => markAsRead([notif.id])}
                          className="p-1 hover:bg-blue/20 rounded flex-shrink-0"
                          title="Mark as read"
                        >
                          <CheckCircle className="w-4 h-4 text-blue" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {data?.total > data?.notifications?.length && (
                <p className="text-xs text-slate text-center mb-3">
                  Showing {data.notifications.length} of {data.total}
                </p>
              )}

              <div className="flex gap-2 pt-3 border-t border-panel-border">
                <button
                  onClick={() => refetch()}
                  className="btn-secondary text-xs flex-1 px-3 py-1.5"
                >
                  <RefreshCw className="w-3 h-3" />
                  Refresh
                </button>
                <button
                  onClick={() => clearOld()}
                  className="btn-secondary text-xs flex-1 px-3 py-1.5"
                >
                  <Trash2 className="w-3 h-3" />
                  Clear Old
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
