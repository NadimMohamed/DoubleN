import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { TokenResponse, LoginRequest, RegisterRequest, User, TickerPrice, KlineData, OrderBook, WatchlistItem } from '@/types'

// Falls back to the production backend URL (matching next.config.js) so the
// app still works if NEXT_PUBLIC_API_URL isn't set at build time in Railway.
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://doublen-production.up.railway.app'

// ── Axios instance ────────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Token storage ─────────────────────────────────────────────────────────────
const TOKEN_KEY = 'dnt_access_token'
const REFRESH_KEY = 'dnt_refresh_token'
const DEFAULT_COOKIE_MAX_AGE = 86400 // 24h fallback if we can't read the token's exp claim

// Reads the `exp` claim off a JWT (if present) so the cookie's max-age
// matches the token's actual expiry instead of an arbitrary constant.
function getTokenMaxAge(token: string): number {
  try {
    const [, payloadSegment] = token.split('.')
    if (!payloadSegment) return DEFAULT_COOKIE_MAX_AGE

    const payload = JSON.parse(atob(payloadSegment.replace(/-/g, '+').replace(/_/g, '/')))
    if (typeof payload?.exp === 'number') {
      const secondsRemaining = Math.floor(payload.exp - Date.now() / 1000)
      return secondsRemaining > 0 ? secondsRemaining : 0
    }
    return DEFAULT_COOKIE_MAX_AGE
  } catch {
    return DEFAULT_COOKIE_MAX_AGE
  }
}

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null
  const match = document.cookie.split(';').find((c) => c.trim().startsWith(`${name}=`))
  if (!match) return null
  const value = match.split('=')[1]?.trim()
  return value || null
}

export const tokenStorage = {
  getAccess: () => {
    if (typeof window === 'undefined') return null
    // Try cookie first (server/middleware relies on it), fall back to localStorage.
    return getCookie(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY)
  },
  getRefresh: () => {
    if (typeof window === 'undefined') return null
    return getCookie(REFRESH_KEY) || localStorage.getItem(REFRESH_KEY)
  },
  set: (access: string, refresh: string) => {
    if (typeof window === 'undefined') return
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
    // Also persist tokens as cookies so the Next.js middleware
    // (which runs on the server and has no access to localStorage) can
    // verify the session before rendering protected routes like /dashboard.
    if (typeof document !== 'undefined') {
      const maxAge = getTokenMaxAge(access)
      const secure = process.env.NODE_ENV === 'production' ? '; Secure' : ''
      document.cookie = `${TOKEN_KEY}=${access}; path=/; max-age=${maxAge}; SameSite=Lax${secure}`
      document.cookie = `${REFRESH_KEY}=${refresh}; path=/; max-age=2592000; SameSite=Lax${secure}`
    }
  },
  clear: () => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    if (typeof document !== 'undefined') {
      const secure = process.env.NODE_ENV === 'production' ? '; Secure' : ''
      document.cookie = `${TOKEN_KEY}=; path=/; max-age=0; SameSite=Lax${secure}`
      document.cookie = `${REFRESH_KEY}=; path=/; max-age=0; SameSite=Lax${secure}`
    }
  },
}

// ── Request interceptor — attach Bearer token ─────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccess()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor — auto refresh on 401 ────────────────────────────────
let isRefreshing = false
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token!)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
      }

      original._retry = true
      isRefreshing = true

      const refreshToken = tokenStorage.getRefresh()
      if (!refreshToken) {
        tokenStorage.clear()
        window.location.href = '/auth/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post<TokenResponse>(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })
        tokenStorage.set(data.access_token, data.refresh_token)
        processQueue(null, data.access_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch (refreshError) {
        processQueue(refreshError, null)
        tokenStorage.clear()
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

// ── Auth API ──────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: RegisterRequest) =>
    api.post<User>('/auth/register', data).then((r) => r.data),

  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/auth/login', data).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>('/auth/refresh', { refresh_token }).then((r) => r.data),
}

// ── Market API ────────────────────────────────────────────────────────────────
export const marketApi = {
  getTicker: (symbol: string) =>
    api.get<TickerPrice>(`/market/ticker/${symbol}`).then((r) => r.data),

  getTickers: (symbols: string[]) =>
    api.get<TickerPrice[]>('/market/tickers', { params: { symbols: symbols.join(',') } }).then((r) => r.data),

  getKlines: (symbol: string, interval = '1h', limit = 200) =>
    api.get<KlineData[]>(`/market/klines/${symbol}`, { params: { interval, limit } }).then((r) => r.data),

  getOrderBook: (symbol: string, limit = 20) =>
    api.get<OrderBook>(`/market/orderbook/${symbol}`, { params: { limit } }).then((r) => r.data),

  getSupportedSymbols: () =>
    api.get<{ symbols: string[] }>('/market/symbols').then((r) => r.data),
}

// ── Watchlist API ─────────────────────────────────────────────────────────────
export const watchlistApi = {
  getWatchlist: () => api.get<WatchlistItem[]>('/watchlist').then((r) => r.data),

  addSymbol: (symbol: string) =>
    api.post<WatchlistItem>('/watchlist', { symbol }).then((r) => r.data),

  removeSymbol: (itemId: string) =>
    api.delete(`/watchlist/${itemId}`).then((r) => r.data),
}

// ── Error helper ──────────────────────────────────────────────────────────────
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((e) => e.msg).join(', ')
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'An unexpected error occurred'
}
