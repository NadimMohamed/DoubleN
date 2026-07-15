'use client'
import { useEffect, useRef, useState, useCallback } from 'react'
import type { WsTickerMessage } from '@/types'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

interface UseTickerStreamOptions {
  symbol: string
  enabled?: boolean
}

interface TickerState {
  price: number | null
  open: number | null
  high: number | null
  low: number | null
  volume: number | null
  isConnected: boolean
  lastUpdated: number | null
}

export function useTickerStream({ symbol, enabled = true }: UseTickerStreamOptions): TickerState {
  const [state, setState] = useState<TickerState>({
    price: null, open: null, high: null, low: null,
    volume: null, isConnected: false, lastUpdated: null,
  })
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const backoffRef = useRef(1000)
  const mountedRef = useRef(true)
  // Batch updates using requestAnimationFrame for better performance
  const rafRef = useRef<number | null>(null)
  const pendingStateRef = useRef<Partial<TickerState> | null>(null)

  const connect = useCallback(() => {
    if (!enabled || !mountedRef.current) return

    // Get JWT token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

    if (!token) {
      console.warn('WebSocket: no auth token available, cannot connect')
      return
    }

    // Build URL with token parameter
    const url = new URL(`${WS_URL}/ws/ticker/${symbol.toUpperCase()}`)
    url.searchParams.append('token', token)

    const ws = new WebSocket(url.toString())
    wsRef.current = ws

    ws.onopen = () => {
      if (!mountedRef.current) return
      backoffRef.current = 1000
      setState((s) => ({ ...s, isConnected: true }))
    }

    ws.onmessage = (event) => {
      if (!mountedRef.current) return
      try {
        const msg: WsTickerMessage = JSON.parse(event.data)
        if (msg.type === 'ticker') {
          // Batch updates with RAF
          pendingStateRef.current = {
            price: msg.price,
            open: msg.open,
            high: msg.high,
            low: msg.low,
            volume: msg.volume,
            isConnected: true,
            lastUpdated: msg.timestamp,
          }

          if (rafRef.current === null) {
            rafRef.current = requestAnimationFrame(() => {
              if (pendingStateRef.current) {
                setState((s) => ({ ...s, ...pendingStateRef.current }))
              }
              rafRef.current = null
            })
          }
        }
      } catch {}
    }

    ws.onclose = (event) => {
      if (!mountedRef.current) return
      setState((s) => ({ ...s, isConnected: false }))

      // Check for auth failure (1008 = policy violation) — don't reconnect
      if (event.code === 1008) {
        console.warn('WebSocket auth failed:', event.reason)
        return
      }

      // Exponential backoff, cap at 10s (reduced from 30s)
      reconnectTimer.current = setTimeout(() => {
        if (mountedRef.current) {
          backoffRef.current = Math.min(backoffRef.current * 2, 10000)
          connect()
        }
      }, backoffRef.current)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [symbol, enabled])

  useEffect(() => {
    mountedRef.current = true
    if (enabled) connect()
    return () => {
      mountedRef.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null
        wsRef.current.close()
      }
    }
  }, [connect, enabled])

  return state
}

// ── Multi-symbol hook — subscribes to multiple tickers via polling ─────────────
// Uses REST API polling as a fallback when individual WS connections are expensive
export function useMultiTickerPoll(
  symbols: string[],
  intervalMs = 5000,
  enabled = true
) {
  const [prices, setPrices] = useState<Record<string, number>>({})
  const [changes, setChanges] = useState<Record<string, number>>({})

  useEffect(() => {
    if (!enabled || symbols.length === 0) return

    const fetchPrices = async () => {
      try {
        const { marketApi } = await import('@/lib/api')
        const tickers = await marketApi.getTickers(symbols)
        const priceMap: Record<string, number> = {}
        const changeMap: Record<string, number> = {}
        tickers.forEach((t) => {
          priceMap[t.symbol] = t.price
          changeMap[t.symbol] = t.price_change_pct
        })
        setPrices(priceMap)
        setChanges(changeMap)
      } catch {}
    }

    fetchPrices()
    const timer = setInterval(fetchPrices, intervalMs)
    return () => clearInterval(timer)
  }, [symbols.join(','), intervalMs, enabled])

  return { prices, changes }
}
