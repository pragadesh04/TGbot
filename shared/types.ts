export interface Course {
  _id: string
  title: string
  description: string
  fee: number
  image_url: string
  registration_count: number
  created_at: string
  updated_at: string
}

export interface Registration {
  _id: string
  telegram_id: number
  name: string
  address: string
  course_id: string
  course_title: string
  amount: number
  screenshot_url?: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  updated_at: string
}

export interface Stats {
  total: number
  pending: number
  approved: number
  rejected: number
}

export interface Config {
  upi_id: string
}
