import React from 'react'
import { Users, Clock, CheckCircle, XCircle } from 'lucide-react'
import { GlassCard } from './GlassCard'

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <GlassCard hover className="flex items-center gap-4">
    <div
      className="p-4 rounded-2xl"
      style={{ backgroundColor: `${color}20` }}
    >
      {icon}
    </div>
    <div>
      <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
      <p className="text-3xl font-bold dark:text-white">{value}</p>
    </div>
  </GlassCard>
)

interface StatsProps {
  stats: {
    total: number
    pending: number
    approved: number
    rejected: number
  }
}

export const StatsCards: React.FC<StatsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        title="Total Registrations"
        value={stats.total}
        icon={<Users className="w-6 h-6 text-primary" />}
        color="#ff6699"
      />
      <StatCard
        title="Pending"
        value={stats.pending}
        icon={<Clock className="w-6 h-6 text-yellow-500" />}
        color="#eab308"
      />
      <StatCard
        title="Approved"
        value={stats.approved}
        icon={<CheckCircle className="w-6 h-6 text-green-500" />}
        color="#22c55e"
      />
      <StatCard
        title="Rejected"
        value={stats.rejected}
        icon={<XCircle className="w-6 h-6 text-red-500" />}
        color="#ef4444"
      />
    </div>
  )
}
