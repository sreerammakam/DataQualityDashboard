import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

export type Dimension = 'completeness' | 'timeliness' | 'validity' | 'accuracy' | 'consistency'

export interface Dataset { id: number; key: string; name: string; description?: string }
export interface DimensionSummary { dimension: Dimension; latest_value?: number | null; latest_at?: string | null }
export interface TimeseriesPoint { recorded_at: string; value: number }
export interface Timeseries { metric_name: string; points: TimeseriesPoint[] }
