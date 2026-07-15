'use client'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { AssetAllocation } from '@/types/portfolio'

interface AssetAllocationProps {
  assets: AssetAllocation[]
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export function AssetAllocationChart({ assets }: AssetAllocationProps) {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-bold text-white mb-4">Asset Allocation</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={assets}
            dataKey="percentage"
            nameKey="symbol"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label
          >
            {assets.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value}%`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {assets.map((asset, i) => (
          <div key={asset.symbol} className="flex justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
              <span className="text-slate">{asset.symbol}</span>
            </div>
            <span className="text-white font-semibold">{asset.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
