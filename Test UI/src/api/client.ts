import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL as string | undefined

if (!baseURL) {
  // eslint-disable-next-line no-console
  console.warn(
    'VITE_API_BASE_URL is not set. Create a .env file (see .env.example) pointing at your backend.',
  )
}

export const apiClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 90_000,
})
