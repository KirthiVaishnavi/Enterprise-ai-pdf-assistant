const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
import { getToken, removeToken } from "../auth/storage"

async function apiRequest(
  path: string,
  options?: RequestInit
) {
    const token= getToken()
    const response = await fetch(`${API_BASE_URL}${path}`,{ 
        ...options,
        headers:{
            ...options?.headers,
            ...(token? {Authorization: `Bearer ${token}` } : {}),
        },
    })

    if (!response.ok) {
        if (response.status === 401) {
            removeToken()
            window.location.href = '/login'
            return
        }
        throw new Error(`API request failed: ${response.status}`)
    }

  return response.json()
}

export default apiRequest