import { useEffect, useState, useCallback } from 'react'
import { wsClient, WebSocketMessage } from '@/lib/websocket'

export function useWebSocket(symbol: string) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<WebSocketMessage | null>(null)

  useEffect(() => {
    wsClient.connect(symbol)
      .then(() => setIsConnected(true))
      .catch(console.error)

    const handleMessage = (data: WebSocketMessage) => {
      setLastUpdate(data)
    }

    wsClient.subscribe(symbol, handleMessage)

    return () => {
      wsClient.unsubscribe(symbol, handleMessage)
      wsClient.disconnect()
      setIsConnected(false)
    }
  }, [symbol])

  return { isConnected, lastUpdate }
}
