import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../ui/Card'
import { Badge } from '../ui/Badge'

interface BiteIndexDataPoint {
  time: string
  score: number
  explain: string[]
}

interface BiteIndexChartProps {
  data: BiteIndexDataPoint[]
  confidence: 'low' | 'medium' | 'high'
}

const confidenceColors = {
  low: 'warning',
  medium: 'secondary',
  high: 'success',
} as const

const confidenceLabels = {
  low: 'Низкая',
  medium: 'Средняя',
  high: 'Высокая',
}

export function BiteIndexChart({ data, confidence }: BiteIndexChartProps) {
  const formatTime = (time: string) => {
    const date = new Date(time)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const chartData = data.map(point => ({
    time: formatTime(point.time),
    fullTime: point.time,
    'Индекс клёва': point.score,
    explain: point.explain.join(', '),
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-popover border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-sm">{data.time}</p>
          <p className="text-lg font-bold text-primary">
            {data['Индекс клёва']} / 100
          </p>
          <p className="text-xs text-muted-foreground mt-1">{data.explain}</p>
        </div>
      )
    }
    return null
  }

  // Get average score
  const avgScore = Math.round(data.reduce((sum, p) => sum + p.score, 0) / data.length)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Индекс клёва</CardTitle>
            <CardDescription>
              Средний: {avgScore}/100
            </CardDescription>
          </div>
          <Badge variant={confidenceColors[confidence]}>
            Точность: {confidenceLabels[confidence]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="biteGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12 }}
              label={{ value: 'Индекс', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="Индекс клёва"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              fill="url(#biteGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>0-40: Слабо</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span>40-70: Средне</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>70-100: Хорошо</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
