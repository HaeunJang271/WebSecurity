import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = '/api/v1'

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const { refreshToken, setTokens, logout } = useAuthStore.getState()
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          setTokens(access_token, refresh_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          logout()
        }
      } else {
        logout()
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: async (data: { email: string; username: string; password: string; full_name?: string }) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },
  
  login: async (data: { email: string; password: string }) => {
    const response = await api.post('/auth/login', data)
    return response.data
  },
  
  me: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

// Scan API
export const scanAPI = {
  create: async (data: { target_url: string; scan_type?: string; scan_depth?: number }) => {
    const response = await api.post('/scans', data)
    return response.data
  },
  
  list: async (params?: { page?: number; page_size?: number; status?: string }) => {
    const response = await api.get('/scans', { params })
    return response.data
  },
  
  get: async (id: number) => {
    const response = await api.get(`/scans/${id}`)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/scans/${id}`)
  },
  
  cancel: async (id: number) => {
    const response = await api.post(`/scans/${id}/cancel`)
    return response.data
  },
}

// Vulnerability API
export const vulnerabilityAPI = {
  getByScan: async (scanId: number, params?: { severity?: string; vuln_type?: string }) => {
    const response = await api.get(`/vulnerabilities/scan/${scanId}`, { params })
    return response.data
  },
  
  get: async (id: number) => {
    const response = await api.get(`/vulnerabilities/${id}`)
    return response.data
  },
  
  markFalsePositive: async (id: number, isFalsePositive: boolean) => {
    const response = await api.patch(`/vulnerabilities/${id}/false-positive`, null, {
      params: { is_false_positive: isFalsePositive },
    })
    return response.data
  },
}

// Report API
export const reportAPI = {
  downloadPDF: async (scanId: number) => {
    const response = await api.get(`/reports/${scanId}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },
  
  downloadHTML: async (scanId: number) => {
    const response = await api.get(`/reports/${scanId}/html`, {
      responseType: 'blob',
    })
    return response.data
  },
}

