'use client'
import { useQuery } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
import axios from 'axios'

export function AISignalBadge({ symbol }: { symbol: string }) {
  const { data: analysis } = useQuery({
    queryKey: ['analysis', symbol],
    queryFn: async () => {
      const res = await axios.get(`/api/v1/analysis/${symbol}`)
      return res.data
    },
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 0,
  })

  if (!analysis) {
    return <span className="text-xs text-slate">--</span>
  }

  const signal = analysis.signal.signal
  const confidence = analysis.signal.confidence
  
  return (
    <div className={cn(
      'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold',
      signal === 'buy' ? 'bg-emerald/20 text-emerald' :
      signal === 'sell' ? 'bg-danger/20 text-danger' :
      'bg-slate/20 text-slate'
    )}>
      <span className="uppercase text-xs">{signal}</span>
      <span className="text-xs opacity-75">{confidence}%</span>
    </div>
  )
}
