import axios from "axios"
import { OpenAPI } from "../client"
import { useAuthStore } from "../store/auth"

OpenAPI.BASE = import.meta.env.VITE_API_URL || ""
OpenAPI.WITH_CREDENTIALS = true
OpenAPI.TOKEN = async () => {
  try {
    const authStore = useAuthStore()
    return authStore.accessToken || ""
  } catch (e) {
    return ""
  }
}

let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/refresh") &&
      localStorage.getItem("was_logged_in") === 'true'
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return axios(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const authStore = useAuthStore()
        const success = await authStore.refresh()
        if (success) {
          const newToken = authStore.accessToken
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return axios(originalRequest)
        } else {
          throw new Error("Refresh failed")
        }
      } catch (refreshError) {
        const authStore = useAuthStore()
        processQueue(refreshError, null)
        authStore.logout()
        window.location.href = "/login"
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)
