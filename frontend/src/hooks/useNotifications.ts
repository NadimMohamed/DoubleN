import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  symbol?: string
  is_read: boolean
  created_at: string
  expires_at?: string
}

export interface NotificationsData {
  notifications: Notification[]
  total: number
  unread_count: number
}

export function useNotifications() {
  return useQuery<NotificationsData>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/notifications', {
        params: { limit: 50, offset: 0 }
      })
      return res.data
    },
    refetchInterval: 30000,
    staleTime: 10000,
  })
}
