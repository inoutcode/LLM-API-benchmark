import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data.error || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data)
}

// 任务 API
export const taskAPI = {
  getTasks: (params) => api.get('/tasks/', { params }),
  getTask: (id) => api.get(`/tasks/${id}`),
  createTask: (data) => api.post('/tasks/', data),
  updateTask: (id, data) => api.put(`/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/tasks/${id}`),
  runTask: (id) => api.post(`/tasks/${id}/run`),
  stopTask: (id) => api.post(`/tasks/${id}/stop`)
}

// 结果 API
export const resultAPI = {
  getPerfResults: (params) => api.get('/results/perf', { params }),
  getPerfResult: (id) => api.get(`/results/perf/${id}`),
  getPerfResultFile: (id) => api.get(`/results/perf/${id}/file`),
  getPerfChartData: (params) => api.get('/results/perf/chart-data', { params }),
  getPerfModels: () => api.get('/results/perf/models'),
  
  getQualityResults: (params) => api.get('/results/quality', { params }),
  getQualityResult: (id) => api.get(`/results/quality/${id}`),
  getQualityResultFile: (id) => api.get(`/results/quality/${id}/file`),
  getQualityResultRaw: (id) => api.get(`/results/quality/${id}/raw`),
  
  getStatistics: () => api.get('/results/statistics')
}

export default api