import { Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { Courses } from './pages/Courses'
import { Registrations } from './pages/Registrations'
import { Settings } from './pages/Settings'
import { useThemeStore } from './store/themeStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      retry: 1,
    },
  },
})

function App() {
  const { isDark } = useThemeStore()

  return (
    <QueryClientProvider client={queryClient}>
      <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
        <div className="flex min-h-screen bg-white dark:bg-black transition-colors duration-300">
          <Sidebar />
          <main className="flex-1 p-8 bg-gradient-to-br from-white to-pink-50 dark:from-black dark:to-gray-900">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/courses" element={<Courses />} />
              <Route path="/registrations" element={<Registrations />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App
