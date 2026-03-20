import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit2, Trash2, Image } from 'lucide-react'
import { GlassCard } from '../components/GlassCard'
import { GlassModal } from '../components/GlassModal'
import { api } from '../lib/api'

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
  })

  const handleEdit = (course: any) => {
    setEditingCourse(course)
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this course?')) {
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
              <img
                src={course.image_url}
                alt={course.title}
                className="w-full h-40 object-cover rounded-2xl mb-4"
              />
              <h3 className="text-xl font-semibold mb-2 dark:text-white">{course.title}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                {course.description}
              </p>
              <div className="flex items-center justify-between mb-4">
                <span className="text-2xl font-bold text-primary">₹{course.fee}</span>
                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                  {course.registration_count} enrolled
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(course)}
                  className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl bg-white dark:bg-black/50 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-primary/10 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(course._id)}
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      title,
      description,
      fee: parseFloat(fee),
      image_url: imageUrl || undefined,
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
