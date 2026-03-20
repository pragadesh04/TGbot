import { useQuery } from '@tanstack/react-query'
import { GlassCard } from '../components/GlassCard'
import { StatsCards } from '../components/StatsCards'
import { api } from '../lib/api'
import { Users } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: api.getStats,
    refetchInterval: 30000,
  })

  const { data: courses } = useQuery({
    queryKey: ['courses'],
    queryFn: api.getCourses,
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8 dark:text-white">Dashboard</h1>
      
      {stats && <StatsCards stats={stats} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Popular Courses</h2>
          <div className="space-y-3">
            {courses?.slice(0, 5).map((course: any) => (
              <div key={course._id} className="flex items-center justify-between p-3 rounded-xl bg-white/30 dark:bg-black/30">
                <div className="flex items-center gap-3">
                  <img
                    src={course.image_url}
                    alt={course.title}
                    className="w-12 h-12 rounded-lg object-cover"
                  />
                  <div>
                    <p className="font-medium dark:text-white">{course.title}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">₹{course.fee}</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                  {course.registration_count} enrolled
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <a href="/courses" className="p-4 rounded-xl bg-primary text-white text-center font-medium hover:shadow-lg transition-all">
              Manage Courses
            </a>
            <a href="/registrations" className="p-4 rounded-xl bg-dark text-white text-center font-medium dark:bg-transparent dark:border-2 dark:border-primary dark:text-primary hover:shadow-lg transition-all">
              View Registrations
            </a>
            <a href="/settings" className="p-4 rounded-xl bg-white text-dark border border-gray-200 dark:bg-transparent dark:border dark:border-gray-700 dark:text-white text-center font-medium hover:shadow-lg transition-all">
              Settings
            </a>
            <div className="p-4 rounded-xl bg-white/30 dark:bg-black/30 text-center">
              <Users className="w-6 h-6 mx-auto mb-2 text-primary" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {stats?.total || 0} Total Users
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
