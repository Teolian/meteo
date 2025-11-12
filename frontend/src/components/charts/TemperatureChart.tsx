import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'

interface TemperatureDataPoint {
  time: string
  t2m_c?: number
}

interface TemperatureChartProps {
  data: TemperatureDataPoint[]
}

export function TemperatureChart({ data }: TemperatureChartProps) {
  const formatTime = (time: string) => {
    const date = new Date(time)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const chartData = data.map(point => ({
    time: formatTime(point.time),
    'Температура (°C)': point.t2m_c ? Math.round(point.t2m_c * 10) / 10 : null,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Температура воздуха</CardTitle>
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
              label={{ value: '°C', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="Температура (°C)"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
