import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'

interface WindDataPoint {
  time: string
  wind10_mps?: number
  wind_dir_deg?: number
  gust_mps?: number
}

interface WindChartProps {
  data: WindDataPoint[]
}

export function WindChart({ data }: WindChartProps) {
  const formatTime = (time: string) => {
    const date = new Date(time)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const chartData = data.map(point => ({
    time: formatTime(point.time),
    'Скорость (м/с)': point.wind10_mps ? Math.round(point.wind10_mps * 10) / 10 : null,
    'Порывы (м/с)': point.gust_mps ? Math.round(point.gust_mps * 10) / 10 : null,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Ветер</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              label={{ value: 'м/с', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Скорость (м/с)"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Порывы (м/с)"
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
