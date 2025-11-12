/**
 * API client for backend services
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface Waterbody {
  id: number
  name: string
  lat: number
  lon: number
  region: string
  type: string
}

export interface HourlyForecast {
  time: string
  mslp_hpa?: number
  surface_pressure_hpa?: number
  t2m_c?: number
  wind10_mps?: number
  wind_dir_deg?: number
  gust_mps?: number
  cloud_pct?: number
  precip_mm?: number
  snowfall_mm?: number
  snow_depth_cm?: number
  visibility_km?: number
  provider: string
}

export interface ForecastResponse {
  meta: {
    lat: number
    lon: number
    timezone: string
    providers: string[]
  }
  hourly: HourlyForecast[]
}

export interface SignalFlag {
  time: string
  front_like?: boolean
  stable_window?: boolean
  reason?: string[]
}

export interface SignalsResponse {
  trend: {
    dP6_hpa?: number
    dP12_hpa?: number
    dP24_hpa?: number
  }
  flags: SignalFlag[]
}

export interface BiteIndexHourly {
  time: string
  score: number
  explain: string[]
}

export interface BiteIndexResponse {
  meta: {
    species: string[]
  }
  hourly: BiteIndexHourly[]
  confidence: 'low' | 'medium' | 'high'
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Waterbodies
  async getWaterbodies(region?: string, type?: string): Promise<Waterbody[]> {
    const params = new URLSearchParams()
    if (region) params.append('region', region)
    if (type) params.append('type', type)
    const query = params.toString() ? `?${params.toString()}` : ''
    return this.request<Waterbody[]>(`/waterbodies${query}`)
  }

  async getWaterbody(id: number): Promise<Waterbody> {
    return this.request<Waterbody>(`/waterbodies/${id}`)
  }

  // Forecast
  async getForecast(params: {
    lat: number
    lon: number
    hours?: number
    provider?: string[]
    include?: string[]
  }): Promise<ForecastResponse> {
    const searchParams = new URLSearchParams({
      lat: params.lat.toString(),
      lon: params.lon.toString(),
      hours: (params.hours || 120).toString(),
    })

    if (params.provider) {
      params.provider.forEach(p => searchParams.append('provider', p))
    }
    if (params.include) {
      params.include.forEach(i => searchParams.append('include', i))
    }

    return this.request<ForecastResponse>(`/forecast?${searchParams.toString()}`)
  }

  // Signals
  async getSignals(params: {
    lat: number
    lon: number
    hours?: number
    window?: number[]
  }): Promise<SignalsResponse> {
    const searchParams = new URLSearchParams({
      lat: params.lat.toString(),
      lon: params.lon.toString(),
      hours: (params.hours || 120).toString(),
    })

    if (params.window) {
      params.window.forEach(w => searchParams.append('window', w.toString()))
    }

    return this.request<SignalsResponse>(`/signals?${searchParams.toString()}`)
  }

  // Bite Index
  async getBiteIndex(params: {
    lat: number
    lon: number
    hours?: number
    species?: string[]
  }): Promise<BiteIndexResponse> {
    const searchParams = new URLSearchParams({
      lat: params.lat.toString(),
      lon: params.lon.toString(),
      hours: (params.hours || 120).toString(),
    })

    if (params.species) {
      params.species.forEach(s => searchParams.append('species', s))
    }

    return this.request<BiteIndexResponse>(`/bite-index?${searchParams.toString()}`)
  }
}

export const api = new ApiClient()
