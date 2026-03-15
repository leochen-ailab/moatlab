import axios, { AxiosError } from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// 创建 axios 实例
const client: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // 60秒超时（分析请求可能较长）
  headers: {
    'Content-Type': 'application/json',
  },
})

// Loading 实例
let loadingInstance: ReturnType<typeof ElLoading.service> | null = null
let requestCount = 0

// 显示 loading
const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)',
    })
  }
  requestCount++
}

// 隐藏 loading
const hideLoading = () => {
  requestCount--
  if (requestCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// 请求拦截器
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 显示 loading（可以通过 config 中的自定义参数控制是否显示）
    if (config.headers && config.headers['X-Show-Loading'] !== 'false') {
      showLoading()
    }
    return config
  },
  (error: AxiosError) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器
client.interceptors.response.use(
  (response: AxiosResponse) => {
    hideLoading()
    return response.data
  },
  (error: AxiosError) => {
    hideLoading()

    // 错误处理
    let message = '请求失败'

    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          message = data?.detail || '请求参数错误'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = data?.detail || '服务器内部错误'
          break
        default:
          message = data?.detail || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      message = '网络连接失败，请检查后端服务是否启动'
    } else {
      // 请求配置出错
      message = error.message || '请求配置错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default client
