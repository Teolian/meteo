import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'

interface PressureDataPoint {
  time: string
  mslp_hpa?: number
  dP6_hpa?: number
  dP12_hpa?: number
  dP24_hpa?: number
}

interface PressureChartProps {
  data: PressureDataPoint[]
  showDeltas?: boolean
}

export function PressureChart({ data, showDeltas = false }: PressureChartProps) {
  // Format time for display
  const formatTime = (time: string) => {
    const date = new Date(time)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  // Format data for display
  const chartData = data.map(point => ({
    time: formatTime(point.time),
    fullTime: point.time,
    'MSLP (hPa)': point.mslp_hpa ? Math.round(point.mslp_hpa * 10) / 10 : null,
    'ΔP 6h': point.dP6_hpa ? Math.round(point.dP6_hpa * 10) / 10 : null,
    'ΔP 12h': point.dP12_hpa ? Math.round(point.dP12_hpa * 10) / 10 : null,
    'ΔP 24h': point.dP24_hpa ? Math.round(point.dP24_hpa * 10) / 10 : null,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Давление (MSLP) {showDeltas && '+ Тренды ΔP'}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis
              yAxisId="pressure"
              tick={{ fontSize: 12 }}
              label={{ value: 'hPa', angle: -90, position: 'insideLeft' }}
            />
            {showDeltas && (
              <YAxis
                yAxisId="delta"
                orientation="right"
                tick={{ fontSize: 12 }}
                label={{ value: 'ΔP (hPa)', angle: 90, position: 'insideRight' }}
              />
            )}
            <Tooltip />
            <Legend />
            <Line
              yAxisId="pressure"
              type="monotone"
              dataKey="MSLP (hPa)"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
            />
            {showDeltas && (
              <>
                <Line
                  yAxisId="delta"
                  type="monotone"
                  dataKey="ΔP 6h"
                  stroke="#22c55e"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                />
                <Line
                  yAxisId="delta"
                  type="monotone"
                  dataKey="ΔP 12h"
                  stroke="#f59e0b"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                />
                <Line
                  yAxisId="delta"
                  type="monotone"
                  dataKey="ΔP 24h"
                  stroke="#ef4444"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
