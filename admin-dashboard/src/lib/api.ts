const API_BASE = '/api'

const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout = 10000) => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  
  try {
    const res = await fetch(url, { ...options, signal: controller.signal })
    return res
  } finally {
    clearTimeout(timeoutId)
  }
}

export const api = {
  async getStats() {
    const res = await fetchWithTimeout(`${API_BASE}/stats`)
    if (!res.ok) throw new Error('Failed to fetch stats')
    return res.json()
  },

  async getCourses() {
    const res = await fetchWithTimeout(`${API_BASE}/courses`)
    if (!res.ok) throw new Error('Failed to fetch courses')
    return res.json()
  },

  async createCourse(data: { title: string; description: string; fee: number; image_url?: string }) {
    const res = await fetchWithTimeout(`${API_BASE}/courses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create course')
    return res.json()
  },

  async updateCourse(id: string, data: { title?: string; description?: string; fee?: number; image_url?: string }) {
    const res = await fetchWithTimeout(`${API_BASE}/courses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to update course')
    return res.json()
  },

  async deleteCourse(id: string) {
    const res = await fetchWithTimeout(`${API_BASE}/courses/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete course')
    return res.json()
  },

  async toggleCourseRegistration(id: string) {
    const res = await fetchWithTimeout(`${API_BASE}/courses/${id}/toggle-registration`, { method: 'PUT' })  
    if (!res.ok) throw new Error('Failed to toggle registration')
    return res.json()
  },

  async getRegistrations(status?: string, course?: string, sortBy?: string, order?: string) {
    let url = `${API_BASE}/registrations`
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (course) params.append('course', course)
    if (sortBy) params.append('sort_by', sortBy)
    if (order) params.append('order', order)
    const queryString = params.toString()
    if (queryString) url += `?${queryString}`
    const res = await fetchWithTimeout(url)
    if (!res.ok) throw new Error('Failed to fetch registrations')
    return res.json()
  },

  async approveRegistration(id: string) {
    const res = await fetchWithTimeout(`${API_BASE}/registrations/${id}/approve`, { method: 'PUT' })
    if (!res.ok) throw new Error('Failed to approve registration')
    return res.json()
  },

  async rejectRegistration(id: string, reason?: string) {
    const url = reason 
      ? `${API_BASE}/registrations/${id}/reject?reason=${encodeURIComponent(reason)}`
      : `${API_BASE}/registrations/${id}/reject`
    const res = await fetchWithTimeout(url, { method: 'PUT' })
    if (!res.ok) throw new Error('Failed to reject registration')
    return res.json()
  },

  async getConfig() {
    const res = await fetchWithTimeout(`${API_BASE}/config/upi`)
    if (!res.ok) throw new Error('Failed to fetch config')
    return res.json()
  },

  async updateConfig(value: string) {
    const res = await fetchWithTimeout(`${API_BASE}/config/upi`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value }),
    })
    if (!res.ok) throw new Error('Failed to update config')
    return res.json()
  },
}
