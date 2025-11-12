import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

export function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Аналитика</h1>
        <p className="text-muted-foreground">Сравнение провайдеров и настройка индекса</p>
      </div>

      {/* Provider Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Сравнение провайдеров</CardTitle>
          <CardDescription>
            Ансамбль моделей: Open-Meteo, MET Norway
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-semibold">Open-Meteo</p>
                <p className="text-sm text-muted-foreground">
                  ECMWF, GFS, ICON - ансамбль моделей
                </p>
              </div>
              <Badge variant="success">Активен</Badge>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-semibold">MET Norway</p>
                <p className="text-sm text-muted-foreground">
                  Locationforecast 2.0
                </p>
              </div>
              <Badge variant="success">Активен</Badge>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-semibold">OpenWeather</p>
                <p className="text-sm text-muted-foreground">
                  One Call 3.0 (опционально)
                </p>
              </div>
              <Badge variant="secondary">Не настроен</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calibration */}
      <Card>
        <CardHeader>
          <CardTitle>Калибровка</CardTitle>
          <CardDescription>
            Точность прогноза vs фактические наблюдения
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p>Калибровка на основе Meteostat будет доступна после накопления данных</p>
            <p className="text-sm mt-2">Требуется минимум 7 дней наблюдений</p>
          </div>
        </CardContent>
      </Card>

      {/* Species Weights Editor */}
      <Card>
        <CardHeader>
          <CardTitle>Настройка индекса клёва</CardTitle>
          <CardDescription>
            Весовые коэффициенты для разных видов рыб
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Pike */}
            <div>
              <h4 className="font-semibold mb-3">Щука</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Стабильность давления:</span>
                  <span>0.30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Фронт (префронт):</span>
                  <span>0.35 ↑</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ветер:</span>
                  <span>0.15</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Облачность:</span>
                  <span>0.10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Осадки:</span>
                  <span>0.10</span>
                </div>
              </div>
            </div>

            {/* Perch */}
            <div>
              <h4 className="font-semibold mb-3">Окунь</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Стабильность давления:</span>
                  <span>0.40 ↑</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Фронт:</span>
                  <span>0.20</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ветер:</span>
                  <span>0.20 ↑</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                * Коэффициенты можно будет редактировать в следующих версиях
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export */}
      <Card>
        <CardHeader>
          <CardTitle>Экспорт данных</CardTitle>
          <CardDescription>
            Выгрузка прогноза и сигналов в CSV
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4 text-muted-foreground">
            <p>Функция экспорта будет доступна в следующих версиях</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
