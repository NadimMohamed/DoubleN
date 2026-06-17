'use client'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { authApi, tokenStorage, getErrorMessage } from '@/lib/api'

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
          tokenStorage.set(tokens.access_token, tokens.refresh_token)
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
          tokenStorage.set(tokens.access_token, tokens.refresh_token)
          const user = await authApi.me()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (e) {
          set({ error: getErrorMessage(e), isLoading: false })
          throw e
        }
      },

      logout: () => {
        tokenStorage.clear()
        set({ user: null, isAuthenticated: false, error: null })
      },

      fetchMe: async () => {
        const token = tokenStorage.getAccess()
        if (!token) return
        try {
          const user = await authApi.me()
          set({ user, isAuthenticated: true })
        } catch {
          tokenStorage.clear()
          set({ user: null, isAuthenticated: false })
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
