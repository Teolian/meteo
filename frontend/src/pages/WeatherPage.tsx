import { useState, useEffect } from 'react'
import { MapPin, Loader2, AlertCircle } from 'lucide-react'
import { api, Waterbody, ForecastResponse, SignalsResponse, BiteIndexResponse } from '@/services/api'
import { WaterbodyMap } from '@/components/WaterbodyMap'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PressureChart } from '@/components/charts/PressureChart'
import { WindChart } from '@/components/charts/WindChart'
import { TemperatureChart } from '@/components/charts/TemperatureChart'
import { PrecipitationChart } from '@/components/charts/PrecipitationChart'
import { BiteIndexChart } from '@/components/charts/BiteIndexChart'

export function WeatherPage() {
  const [waterbodies, setWaterbodies] = useState<Waterbody[]>([])
  const [selectedWaterbody, setSelectedWaterbody] = useState<Waterbody | undefined>()
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [signals, setSignals] = useState<SignalsResponse | null>(null)
  const [biteIndex, setBiteIndex] = useState<BiteIndexResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showMap, setShowMap] = useState(false)

  // Load waterbodies on mount
  useEffect(() => {
    async function loadWaterbodies() {
      try {
        const wbs = await api.getWaterbodies()
        setWaterbodies(wbs)
        if (wbs.length > 0) {
          setSelectedWaterbody(wbs[0])
        }
      } catch (err) {
        setError('Ошибка загрузки водоёмов')
        console.error(err)
      }
    }
    loadWaterbodies()
  }, [])

  // Load forecast when waterbody changes
  useEffect(() => {
    if (!selectedWaterbody) return

    async function loadForecast() {
      setLoading(true)
      setError(null)

      try {
        const [forecastData, signalsData, biteIndexData] = await Promise.all([
          api.getForecast({
            lat: selectedWaterbody!.lat,
            lon: selectedWaterbody!.lon,
            hours: 120,
            provider: ['open-meteo'],
          }),
          api.getSignals({
            lat: selectedWaterbody!.lat,
            lon: selectedWaterbody!.lon,
            hours: 120,
            window: [6, 12, 24],
          }),
          api.getBiteIndex({
            lat: selectedWaterbody!.lat,
            lon: selectedWaterbody!.lon,
            hours: 120,
            species: ['pike', 'perch'],
          }),
        ])

        setForecast(forecastData)
        setSignals(signalsData)
        setBiteIndex(biteIndexData)
      } catch (err) {
        setError('Ошибка загрузки прогноза')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    loadForecast()
  }, [selectedWaterbody])

  // Get current weather (first data point)
  const currentWeather = forecast?.hourly[0]

  // Merge forecast and signals data for charts
  const mergedData = forecast?.hourly.map((point, idx) => {
    const signal = signals?.flags.find(f => f.time === point.time)
    return {
      ...point,
      dP6_hpa: idx > 0 ? signals?.flags[idx]?.front_like ? -5 : 0 : 0, // Simplified
    }
  }) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Погода и клёв</h1>
          <p className="text-muted-foreground">Почасовой прогноз для зимней рыбалки</p>
        </div>

        <Button onClick={() => setShowMap(!showMap)} variant="outline">
          <MapPin className="h-4 w-4 mr-2" />
          {showMap ? 'Скрыть карту' : 'Показать карту'}
        </Button>
      </div>

      {/* Waterbody Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Водоём</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {waterbodies.map((wb) => (
              <Button
                key={wb.id}
                variant={selectedWaterbody?.id === wb.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedWaterbody(wb)}
              >
                {wb.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Map (collapsible) */}
      {showMap && (
        <WaterbodyMap
          waterbodies={waterbodies}
          selectedWaterbody={selectedWaterbody}
          onWaterbodySelect={setSelectedWaterbody}
          className="h-96"
        />
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-3 text-muted-foreground">Загрузка прогноза...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="flex items-center gap-3 p-6">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <span className="text-destructive">{error}</span>
          </CardContent>
        </Card>
      )}

      {/* Current Weather Card */}
      {!loading && currentWeather && (
        <Card>
          <CardHeader>
            <CardTitle>Сейчас</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Температура</p>
                <p className="text-2xl font-bold">{currentWeather.t2m_c?.toFixed(1)}°C</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Давление</p>
                <p className="text-2xl font-bold">{currentWeather.mslp_hpa?.toFixed(1)} hPa</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Ветер</p>
                <p className="text-2xl font-bold">{currentWeather.wind10_mps?.toFixed(1)} м/с</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Облачность</p>
                <p className="text-2xl font-bold">{currentWeather.cloud_pct}%</p>
              </div>
            </div>

            {signals && (
              <div className="mt-4 flex gap-2">
                {signals.flags.filter(f => f.front_like).length > 0 && (
                  <Badge variant="warning">Фронт приближается</Badge>
                )}
                {signals.flags.filter(f => f.stable_window).length > 0 && (
                  <Badge variant="success">Стабильная погода</Badge>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Bite Index */}
      {!loading && biteIndex && (
        <BiteIndexChart data={biteIndex.hourly} confidence={biteIndex.confidence} />
      )}

      {/* Weather Charts */}
      {!loading && forecast && (
        <div className="space-y-6">
          <PressureChart data={forecast.hourly} showDeltas />
          <WindChart data={forecast.hourly} />
          <TemperatureChart data={forecast.hourly} />
          <PrecipitationChart data={forecast.hourly} showSnowDepth />
        </div>
      )}
    </div>
  )
}
