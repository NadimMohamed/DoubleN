'use client'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types'
import { authApi, tokenStorage, getErrorMessage } from '@/lib/api'

// Refresh this many seconds before the access token actually expires, so we
// proactively rotate tokens instead of waiting for a 401 to trigger it.
const REFRESH_MARGIN_SECONDS = 5 * 60

let refreshTimer: ReturnType<typeof setTimeout> | null = null

function clearScheduledRefresh() {
  if (refreshTimer) {
    clearTimeout(refreshTimer)
    refreshTimer = null
  }
}

// Schedules a silent, proactive token refresh 5 minutes before `expiresAt`
// (a Unix timestamp in seconds). If we're already within that window (or
// past it), the refresh is scheduled to run immediately.
function scheduleTokenRefresh(expiresAt: number | undefined) {
  clearScheduledRefresh()
  if (typeof expiresAt !== 'number') return

  const refreshAtMs = (expiresAt - REFRESH_MARGIN_SECONDS) * 1000
  const delayMs = Math.max(refreshAtMs - Date.now(), 0)

  refreshTimer = setTimeout(async () => {
    const refreshToken = tokenStorage.getRefresh()
    if (!refreshToken) return
    try {
      const tokens = await authApi.refresh(refreshToken)
      tokenStorage.set(tokens.access_token, tokens.refresh_token, tokens.expires_at)
      scheduleTokenRefresh(tokens.expires_at)
    } catch {
      // Let the next authenticated request's 401 handling take over.
    }
  }, delayMs)
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const tokens = await authApi.login(data)
          tokenStorage.set(tokens.access_token, tokens.refresh_token, tokens.expires_at)
          scheduleTokenRefresh(tokens.expires_at)
          const user = await authApi.me()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (e) {
          set({ error: getErrorMessage(e), isLoading: false })
          throw e
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null })
        try {
          await authApi.register(data)
          // Auto-login after registration
          const tokens = await authApi.login({ email: data.email, password: data.password })
          tokenStorage.set(tokens.access_token, tokens.refresh_token, tokens.expires_at)
          scheduleTokenRefresh(tokens.expires_at)
          const user = await authApi.me()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (e) {
          set({ error: getErrorMessage(e), isLoading: false })
          throw e
        }
      },

      logout: () => {
        clearScheduledRefresh()
        tokenStorage.clear()
        set({ user: null, isAuthenticated: false, error: null })
      },

      fetchMe: async () => {
        const token = tokenStorage.getAccess()
        if (!token) {
          set({ user: null, isAuthenticated: false })
          return
        }
        // Ensure a proactive refresh is scheduled even after a page reload,
        // where login()/register() (which normally schedule it) don't run.
        scheduleTokenRefresh(tokenStorage.getExpiresAt() ?? undefined)
        try {
          const user = await authApi.me()
          set({ user, isAuthenticated: true })
        } catch {
          // Access token may have expired — try to refresh before giving up.
          const refreshToken = tokenStorage.getRefresh()
          if (refreshToken) {
            try {
              const newTokens = await authApi.refresh(refreshToken)
              tokenStorage.set(newTokens.access_token, newTokens.refresh_token, newTokens.expires_at)
              scheduleTokenRefresh(newTokens.expires_at)
              const user = await authApi.me()
              set({ user, isAuthenticated: true })
            } catch {
              clearScheduledRefresh()
              tokenStorage.clear()
              set({ user: null, isAuthenticated: false })
            }
          } else {
            clearScheduledRefresh()
            tokenStorage.clear()
            set({ user: null, isAuthenticated: false })
          }
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
