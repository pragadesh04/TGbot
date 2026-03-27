import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit2, Trash2, Image, Clock, Calendar, Lock, Unlock, AlertTriangle } from 'lucide-react'
import { GlassCard } from '../components/GlassCard'
import { GlassModal } from '../components/GlassModal'
import { api } from '../lib/api'

const formatHours = (hours: number): string => {
  if (!hours) return ''
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  if (h === 0) return `${m} Minutes`
  if (m === 0) return `${h} Hour${h > 1 ? 's' : ''}`
  return `${h} Hour${h > 1 ? 's' : ''} ${m} Minutes`
}

export const Courses: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCourse, setEditingCourse] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data: courses, isLoading } = useQuery({
    queryKey: ['courses'],
    queryFn: api.getCourses,
  })

  const createMutation = useMutation({
    mutationFn: api.createCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setIsModalOpen(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.updateCourse(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setIsModalOpen(false)
      setEditingCourse(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: api.deleteCourse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
    },
    onError: (error) => {
      alert('Failed to delete course. Please try again.')
      console.error(error)
    },
  })

  const toggleRegistrationMutation = useMutation({
    mutationFn: api.toggleCourseRegistration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
    },
    onError: (error) => {
      alert('Failed to toggle registration. Please try again.')
      console.error(error)
    },
  })

  const handleEdit = (course: any) => {
    setEditingCourse(course)
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold dark:text-white">Courses</h1>
        <button
          onClick={() => {
            setEditingCourse(null)
            setIsModalOpen(true)
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Course
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-64 rounded-3xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses?.map((course: any) => (
            <GlassCard key={course._id} hover className="overflow-hidden">
              <div className="relative">
                <img
                  src={course.image_url}
                  alt={course.title}
                  className="w-full h-40 object-cover rounded-2xl mb-4"
                />
                <span className={`absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-medium ${
                  course.course_type === 'live' 
                    ? 'bg-red-500 text-white' 
                    : 'bg-blue-500 text-white'
                }`}>
                  {course.course_type === 'live' ? '🔴 Live' : '📼 Recorded'}
                </span>
                <span className={`absolute top-2 left-2 px-3 py-1 rounded-full text-xs font-medium ${
                  course.registration_open === false
                    ? 'bg-red-500 text-white'
                    : 'bg-green-500 text-white'
                }`}>
                  {course.registration_open === false ? '🔒 Closed' : '🔓 Open'}
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2 dark:text-white">{course.title}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                {course.description}
              </p>
              
              {course.course_type === 'live' && (
                <div className="flex items-center gap-2 mb-3 text-sm text-gray-500 dark:text-gray-400">
                  <Calendar className="w-4 h-4" />
                  <span>{course.start_date || 'TBD'}</span>
                  <span>•</span>
                  <span>{course.start_time || 'TBD'}</span>
                  {course.sessions && (
                    <>
                      <span>•</span>
                      <span>{course.sessions} sessions</span>
                    </>
                  )}
                  {course.duration && (
                    <>
                      <span>•</span>
                      <Clock className="w-4 h-4" />
                      <span>{formatHours(course.duration)} each</span>
                    </>
                  )}
                </div>
              )}
              
              <div className="flex items-center justify-between mb-4">
                <span className="text-2xl font-bold text-primary">₹{course.fee}</span>
                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                  {course.registration_count} enrolled
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => toggleRegistrationMutation.mutate(course.id)}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl transition-colors ${
                    course.registration_open === false
                      ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40'
                      : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40'
                  }`}
                >
                  {course.registration_open === false ? <Unlock className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                  {course.registration_open === false ? 'Open' : 'Close'}
                </button>
                <button
                  onClick={() => handleEdit(course)}
                  className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-white dark:bg-black/50 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-primary/10 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(course.id)}
                  className="p-2 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      <CourseModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingCourse(null)
        }}
        course={editingCourse}
        onSubmit={(data) => {
          if (editingCourse) {
            updateMutation.mutate({ id: editingCourse._id, data })
          } else {
            createMutation.mutate(data)
          }
        }}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />
    </div>
  )
}

interface CourseModalProps {
  isOpen: boolean
  onClose: () => void
  course: any
  onSubmit: (data: any) => void
  isLoading: boolean
}

const CourseModal: React.FC<CourseModalProps> = ({ isOpen, onClose, course, onSubmit, isLoading }) => {
  const [title, setTitle] = useState(course?.title || '')
  const [description, setDescription] = useState(course?.description || '')
  const [fee, setFee] = useState(course?.fee?.toString() || '0')
  const [imageUrl, setImageUrl] = useState(course?.image_url || '')
  const [courseType, setCourseType] = useState(course?.course_type || 'recorded')
  const [startDate, setStartDate] = useState(course?.start_date || '')
  const [startTime, setStartTime] = useState(course?.start_time || '')
  const [sessions, setSessions] = useState(course?.sessions?.toString() || '')
  const [duration, setDuration] = useState(course?.duration?.toString() || '')

  useEffect(() => {
    setTitle(course?.title || '')
    setDescription(course?.description || '')
    setFee(course?.fee?.toString() || '0')
    setImageUrl(course?.image_url || '')
    setCourseType(course?.course_type || 'recorded')
    setStartDate(course?.start_date || '')
    setStartTime(course?.start_time || '')
    setSessions(course?.sessions?.toString() || '')
    setDuration(course?.duration?.toString() || '')
  }, [course])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      title,
      description,
      fee: parseFloat(fee),
      image_url: imageUrl || undefined,
      course_type: courseType,
      start_date: courseType === 'live' ? startDate || undefined : undefined,
      start_time: courseType === 'live' ? startTime || undefined : undefined,
      sessions: courseType === 'live' && sessions ? parseInt(sessions) : undefined,
      duration: courseType === 'live' && duration ? parseFloat(duration) : undefined,
    })
  }

  return (
    <GlassModal
      isOpen={isOpen}
      onClose={onClose}
      title={course ? 'Edit Course' : 'Add Course'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Course Type
          </label>
          <select
            value={courseType}
            onChange={(e) => setCourseType(e.target.value)}
            className="input-field"
          >
            <option value="recorded">📼 Recorded</option>
            <option value="live">🔴 Live</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field resize-none"
            rows={3}
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Fee (₹)
          </label>
          <input
            type="number"
            value={fee}
            onChange={(e) => setFee(e.target.value)}
            className="input-field"
            min="0"
            step="0.01"
            required
          />
        </div>

        {courseType === 'live' && (
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Time
              </label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sessions (count)
              </label>
              <input
                type="number"
                value={sessions}
                onChange={(e) => setSessions(e.target.value)}
                className="input-field"
                min="1"
                placeholder="e.g., 3"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Duration (hours)
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="input-field"
                min="0"
                step="0.5"
                placeholder="e.g., 1.5"
              />
            </div>
          </div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Image URL (optional)
          </label>
          <div className="relative">
            <Image className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://..."
              className="input-field pl-10"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to use auto-generated placeholder
          </p>
        </div>
        
        <div className="flex gap-3 pt-4">
          <button type="button" onClick={onClose} className="flex-1 btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={isLoading} className="flex-1 btn-primary">
            {isLoading ? 'Saving...' : course ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </GlassModal>
  )
}
