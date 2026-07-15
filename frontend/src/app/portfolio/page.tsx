'use client'
import { AuthGuard } from '@/components/auth/AuthGuard'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { PortfolioStats } from '@/components/portfolio/PortfolioStats'
import { AssetAllocationChart } from '@/components/portfolio/AssetAllocation'
import { TradingStats } from '@/components/portfolio/TradingStats'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { PortfolioStats as PortfolioStatsType, AssetAllocation } from '@/types/portfolio'
import { BarChart3 } from 'lucide-react'

export default function PortfolioPage() {
  const { data: stats } = useQuery({
    queryKey: ['portfolio-stats'],
    queryFn: async () => {
      const res = await api.get('/trading/statistics')
      return res.data as PortfolioStatsType
    },
    refetchInterval: 30000,
  })

  const { data: assets = [] } = useQuery({
    queryKey: ['asset-allocation'],
    queryFn: async () => {
      const res = await api.get('/trading/asset-allocation')
      return res.data as AssetAllocation[]
    },
  })

  if (!stats) return <div>Loading...</div>

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-navy">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2 mb-2">
                <BarChart3 className="w-6 h-6" />
                Portfolio Dashboard
              </h1>
              <p className="text-slate">Track your trading performance and portfolio allocation</p>
            </div>

            <PortfolioStats stats={stats} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <AssetAllocationChart assets={assets} />
              </div>
              <div>
                <TradingStats stats={stats} />
              </div>
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  )
}
