'use client'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { usePositions, useOpenPosition, useClosePosition } from '@/hooks/usePositions'
import { PositionsTable } from '@/components/trading/PositionsTable'
import { OpenPositionForm } from '@/components/trading/OpenPositionForm'
import { toast } from 'sonner'
import { TrendingUp } from 'lucide-react'

export default function PositionsPage() {
  const { data: positions = [], isLoading } = usePositions()
  const openPosition = useOpenPosition()
  const closePosition = useClosePosition()

  const totalUnrealizedPnL = positions.reduce((sum, p) => sum + p.unrealized_pnl, 0)
  const winningPositions = positions.filter(p => p.unrealized_pnl > 0).length

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2 mb-2">
                <TrendingUp className="w-6 h-6" />
                Positions
              </h1>
              <p className="text-slate">Manage your open trading positions</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="card p-4">
                <div className="text-xs text-slate uppercase tracking-wider mb-1">Open Positions</div>
                <div className="text-2xl font-bold text-white">{positions.length}</div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-slate uppercase tracking-wider mb-1">Unrealized PnL</div>
                <div className={`text-2xl font-bold ${totalUnrealizedPnL >= 0 ? 'text-emerald' : 'text-danger'}`}>
                  ${totalUnrealizedPnL.toFixed(2)}
                </div>
              </div>
              <div className="card p-4">
                <div className="text-xs text-slate uppercase tracking-wider mb-1">Winning Positions</div>
                <div className="text-2xl font-bold text-emerald">{winningPositions}/{positions.length}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <PositionsTable
                  positions={positions}
                  onClose={async (positionId, exitPrice) => {
                    try {
                      await closePosition.mutateAsync({ positionId, exitPrice })
                      toast.success('Position closed')
                    } catch (error) {
                      toast.error('Failed to close position')
                    }
                  }}
                  isLoading={isLoading}
                />
              </div>

              <div>
                <OpenPositionForm
                  onSubmit={async (data) => {
                    try {
                      await openPosition.mutateAsync(data)
                      toast.success('Position opened')
                    } catch (error) {
                      toast.error('Failed to open position')
                    }
                  }}
                  isLoading={openPosition.isPending}
                  symbols={['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']}
                />
              </div>
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
