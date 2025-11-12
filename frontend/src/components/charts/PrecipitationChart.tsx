import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'

interface PrecipitationDataPoint {
  time: string
  precip_mm?: number
  snowfall_mm?: number
  cloud_pct?: number
  snow_depth_cm?: number
}

interface PrecipitationChartProps {
  data: PrecipitationDataPoint[]
  showSnowDepth?: boolean
}

export function PrecipitationChart({ data, showSnowDepth = false }: PrecipitationChartProps) {
  const formatTime = (time: string) => {
    const date = new Date(time)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const chartData = data.map(point => ({
    time: formatTime(point.time),
    'Облачность (%)': point.cloud_pct ?? null,
    'Дождь (мм)': point.precip_mm ? Math.round(point.precip_mm * 10) / 10 : null,
    'Снег (мм)': point.snowfall_mm ? Math.round(point.snowfall_mm * 10) / 10 : null,
    'Снежный покров (см)': point.snow_depth_cm ? Math.round(point.snow_depth_cm * 10) / 10 : null,
  }))

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Облачность и осадки</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="cloud"
                tick={{ fontSize: 12 }}
                label={{ value: '%', angle: -90, position: 'insideLeft' }}
              />
              <YAxis
                yAxisId="precip"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{ value: 'мм', angle: 90, position: 'insideRight' }}
              />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="cloud"
                type="monotone"
                dataKey="Облачность (%)"
                stroke="#94a3b8"
                strokeWidth={2}
                dot={false}
              />
              <Bar
                yAxisId="precip"
                dataKey="Дождь (мм)"
                fill="#3b82f6"
                opacity={0.6}
              />
              <Bar
                yAxisId="precip"
                dataKey="Снег (мм)"
                fill="#60a5fa"
                opacity={0.8}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {showSnowDepth && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-lg">Снежный покров</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 12 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  label={{ value: 'см', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Снежный покров (см)"
                  stroke="#60a5fa"
                  strokeWidth={2}
                  fill="#60a5fa"
                  fillOpacity={0.2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </>
  )
}
