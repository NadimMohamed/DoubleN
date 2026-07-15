export interface WebSocketMessage {
  type: 'ticker' | 'notification' | 'position'
  symbol?: string
  price?: number
  price_change_pct?: number
  high_24h?: number
  low_24h?: number
  volume?: number
  timestamp?: string
  [key: string]: any
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private listeners: Map<string, Set<(data: WebSocketMessage) => void>> = new Map()

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.url = baseUrl.replace(/^http/, 'ws')
  }

  connect(symbol: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.url}/api/v1/ws/market/${symbol.toUpperCase()}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log(`WebSocket connected to ${symbol}`)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          const data: WebSocketMessage = JSON.parse(event.data)
          this.emit(data.symbol || 'general', data)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.attemptReconnect(symbol)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private attemptReconnect(symbol: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts), 30000)
      console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`)
      setTimeout(() => this.connect(symbol).catch(console.error), delay)
    }
  }

  subscribe(symbol: string, callback: (data: WebSocketMessage) => void) {
    if (!this.listeners.has(symbol)) {
      this.listeners.set(symbol, new Set())
    }
    this.listeners.get(symbol)!.add(callback)
  }

  unsubscribe(symbol: string, callback: (data: WebSocketMessage) => void) {
    this.listeners.get(symbol)?.delete(callback)
  }

  private emit(symbol: string, data: WebSocketMessage) {
    this.listeners.get(symbol)?.forEach(callback => callback(data))
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new WebSocketClient()
