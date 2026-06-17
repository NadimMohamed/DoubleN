import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { TokenResponse, LoginRequest, RegisterRequest, User, TickerPrice, KlineData, OrderBook, WatchlistItem } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ── Axios instance ────────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Token storage ─────────────────────────────────────────────────────────────
const TOKEN_KEY = 'dnt_access_token'
const REFRESH_KEY = 'dnt_refresh_token'

export const tokenStorage = {
  getAccess: () => (typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null),
  getRefresh: () => (typeof window !== 'undefined' ? localStorage.getItem(REFRESH_KEY) : null),
  set: (access: string, refresh: string) => {
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
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
