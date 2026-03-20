const API_BASE = '/api'

export const api = {
  async getStats() {
    const res = await fetch(`${API_BASE}/stats`)
    if (!res.ok) throw new Error('Failed to fetch stats')
    return res.json()
  },

  async getCourses() {
    const res = await fetch(`${API_BASE}/courses`)
    if (!res.ok) throw new Error('Failed to fetch courses')
    return res.json()
  },

  async createCourse(data: { title: string; description: string; fee: number; image_url?: string }) {
    const res = await fetch(`${API_BASE}/courses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create course')
    return res.json()
  },

  async updateCourse(id: string, data: { title?: string; description?: string; fee?: number; image_url?: string }) {
    const res = await fetch(`${API_BASE}/courses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to update course')
    return res.json()
  },

  async deleteCourse(id: string) {
    const res = await fetch(`${API_BASE}/courses/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete course')
    return res.json()
  },

  async getRegistrations(status?: string) {
    const url = status ? `${API_BASE}/registrations?status=${status}` : `${API_BASE}/registrations`
    console.log(url);
    const res = await fetch(url)
    if (!res.ok) throw new Error('Failed to fetch registrations')
    return res.json()
  },

  async approveRegistration(id: string) {
    const res = await fetch(`${API_BASE}/registrations/${id}/approve`, { method: 'PUT' })
    if (!res.ok) throw new Error('Failed to approve registration')
    return res.json()
  },

  async rejectRegistration(id: string) {
    const res = await fetch(`${API_BASE}/registrations/${id}/reject`, { method: 'PUT' })
    if (!res.ok) throw new Error('Failed to reject registration')
    return res.json()
  },

  async getConfig() {
    const res = await fetch(`${API_BASE}/config/upi`)
    if (!res.ok) throw new Error('Failed to fetch config')
    return res.json()
  },

  async updateConfig(value: string) {
    const res = await fetch(`${API_BASE}/config/upi`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value }),
    })
    if (!res.ok) throw new Error('Failed to update config')
    return res.json()
  },
}
