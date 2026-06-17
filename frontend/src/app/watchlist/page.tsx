'use client'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { watchlistApi } from '@/lib/api'
import { formatPrice, formatPct, formatVolume, SUPPORTED_SYMBOLS, SYMBOL_DISPLAY } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { Plus, Trash2, TrendingUp, TrendingDown, Star, RefreshCw } from 'lucide-react'
import type { WatchlistItem } from '@/types'

function AddSymbolModal({ onClose }: { onClose: () => void }) {
  const [selected, setSelected] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { mutate: addSymbol, isPending } = useMutation({
    mutationFn: (symbol: string) => watchlistApi.addSymbol(symbol),
    onSuccess: (item) => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      toast.success(`${item.symbol} added to watchlist`)
      onClose()
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Failed to add symbol'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="card w-full max-w-sm p-5 animate-fade-in">
        <h3 className="text-base font-semibold text-white mb-4">Add Symbol to Watchlist</h3>

        <div className="grid grid-cols-3 gap-2 mb-5 max-h-64 overflow-y-auto">
          {SUPPORTED_SYMBOLS.map((sym) => {
            const info = SYMBOL_DISPLAY[sym] ?? { icon: '?', name: sym }
            return (
              <button key={sym} onClick={() => setSelected(sym)}
                className={cn(
                  'flex flex-col items-center gap-1 p-3 rounded-lg border text-xs transition-all',
                  selected === sym
                    ? 'border-blue bg-blue/10 text-white'
                    : 'border-panel-border text-slate hover:border-blue/40 hover:text-white',
                )}>
                <span className="text-lg">{info.icon}</span>
                <span className="font-medium">{sym.replace('USDT', '')}</span>
              </button>
            )
          })}
        </div>

        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button
            disabled={!selected || isPending}
            onClick={() => selected && addSymbol(selected)}
            className="btn-primary flex-1">
            {isPending
              ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              : <><Plus className="w-4 h-4" /> Add</>
            }
          </button>
        </div>
      </div>
    </div>
  )
}

function WatchlistRow({ item, onRemove }: { item: WatchlistItem; onRemove: (id: string) => void }) {
  const up = (item.price_change_pct_24h ?? 0) >= 0
  const info = SYMBOL_DISPLAY[item.symbol] ?? { icon: '?', name: item.symbol }

  return (
    <div className="flex items-center px-4 py-3 border-b border-panel-border/50 hover:bg-panel-hover transition-colors group">
      {/* Symbol */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className="w-9 h-9 rounded-xl bg-blue/10 flex items-center justify-center text-blue font-bold text-sm flex-shrink-0">
          {info.icon}
        </div>
        <div>
          <div className="text-sm font-semibold text-white">{item.symbol.replace('USDT', '/USDT')}</div>
          <div className="text-xs text-slate">{info.name}</div>
        </div>
      </div>

      {/* Price */}
      <div className="w-32 text-right hidden sm:block">
        <div className="text-sm font-bold text-white tabular-nums">
          {item.price !== null ? formatPrice(item.price) : <span className="text-slate text-xs">Loading…</span>}
        </div>
      </div>

      {/* 24h change */}
      <div className="w-24 text-right hidden sm:block">
        {item.price_change_pct_24h !== null ? (
          <div className={cn('inline-flex items-center gap-0.5 text-xs font-semibold',
            up ? 'text-emerald' : 'text-danger')}>
            {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {formatPct(item.price_change_pct_24h)}
          </div>
        ) : <span className="text-slate text-xs">—</span>}
      </div>

      {/* 24h High */}
      <div className="w-28 text-right hidden lg:block">
        <div className="text-xs text-emerald tabular-nums">{item.high_24h ? formatPrice(item.high_24h) : '—'}</div>
      </div>

      {/* 24h Low */}
      <div className="w-28 text-right hidden lg:block">
        <div className="text-xs text-danger tabular-nums">{item.low_24h ? formatPrice(item.low_24h) : '—'}</div>
      </div>

      {/* Volume */}
      <div className="w-28 text-right hidden xl:block">
        <div className="text-xs text-slate">{item.quote_volume_24h ? formatVolume(item.quote_volume_24h) : '—'}</div>
      </div>

      {/* Remove */}
      <div className="w-10 flex justify-end">
        <button onClick={() => onRemove(item.id)}
          className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate hover:text-danger hover:bg-danger/10 transition-all">
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

export default function WatchlistPage() {
  const [showAdd, setShowAdd] = useState(false)
  const queryClient = useQueryClient()

  const { data: items, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['watchlist'],
    queryFn: watchlistApi.getWatchlist,
    refetchInterval: 15_000,
    staleTime: 10_000,
  })

  const { mutate: removeItem } = useMutation({
    mutationFn: (id: string) => watchlistApi.removeSymbol(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      toast.success('Removed from watchlist')
    },
    onError: () => toast.error('Failed to remove item'),
  })

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-4">

            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400" />
                  Watchlist
                </h1>
                <p className="text-sm text-slate mt-0.5">
                  {items?.length ?? 0} symbols · Live prices from Binance
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => refetch()}
                  className={cn('btn-secondary px-3 py-2 text-xs', isFetching && 'opacity-60')}>
                  <RefreshCw className={cn('w-3.5 h-3.5', isFetching && 'animate-spin')} />
                  <span className="hidden sm:block">Refresh</span>
                </button>
                <button onClick={() => setShowAdd(true)} className="btn-primary px-3 py-2 text-xs">
                  <Plus className="w-3.5 h-3.5" />
                  Add Symbol
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="card overflow-hidden">
              {/* Column headers */}
              <div className="flex items-center px-4 py-2.5 border-b border-panel-border bg-navy-50/30">
                <div className="flex-1 text-xs font-semibold text-slate uppercase tracking-wider">Symbol</div>
                <div className="w-32 text-right text-xs font-semibold text-slate uppercase tracking-wider hidden sm:block">Price</div>
                <div className="w-24 text-right text-xs font-semibold text-slate uppercase tracking-wider hidden sm:block">24h %</div>
                <div className="w-28 text-right text-xs font-semibold text-slate uppercase tracking-wider hidden lg:block">24h High</div>
                <div className="w-28 text-right text-xs font-semibold text-slate uppercase tracking-wider hidden lg:block">24h Low</div>
                <div className="w-28 text-right text-xs font-semibold text-slate uppercase tracking-wider hidden xl:block">Volume</div>
                <div className="w-10" />
              </div>

              {isLoading ? (
                <div className="p-8 text-center">
                  <div className="w-6 h-6 border-2 border-blue border-t-transparent rounded-full animate-spin mx-auto" />
                </div>
              ) : items?.length === 0 ? (
                <div className="p-12 text-center">
                  <Star className="w-10 h-10 text-slate/30 mx-auto mb-3" />
                  <p className="text-slate font-medium">Your watchlist is empty</p>
                  <p className="text-slate/60 text-sm mt-1">Add symbols to track live prices</p>
                  <button onClick={() => setShowAdd(true)} className="btn-primary px-5 py-2 text-sm mt-4 mx-auto">
                    <Plus className="w-4 h-4" /> Add Symbol
                  </button>
                </div>
              ) : (
                items?.map((item) => (
                  <WatchlistRow key={item.id} item={item} onRemove={removeItem} />
                ))
              )}
            </div>

          </main>
        </div>
      </div>

      {showAdd && <AddSymbolModal onClose={() => setShowAdd(false)} />}
    </AuthGuard>
  )
}
