import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { AlertCircle, TrendingDown, TrendingUp, Wind } from 'lucide-react'

export function HelpPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Справка</h1>
        <p className="text-muted-foreground">Как читать графики и использовать индекс клёва</p>
      </div>

      {/* Bite Index */}
      <Card>
        <CardHeader>
          <CardTitle>Индекс клёва</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            Индекс клёва (0-100) рассчитывается на основе метеоусловий и эмпирических
            правил для зимней рыбалки. Учитываются:
          </p>

          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <TrendingDown className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="font-semibold">Стабильность давления (35%)</p>
                <p className="text-sm text-muted-foreground">
                  Слабые изменения давления (|ΔP/12h| &lt; 2 hPa) = хороший клёв
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="font-semibold">Фронты (25%)</p>
                <p className="text-sm text-muted-foreground">
                  Префронт (плавное падение -2..-4 hPa) = короткое окно активности.
                  Резкий фронт = клёв слабый.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Wind className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="font-semibold">Ветер (15%)</p>
                <p className="text-sm text-muted-foreground">
                  Слабый ветер (&lt;3 м/с) лучше, сильный (&gt;8 м/с) хуже
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t">
            <p className="text-sm font-semibold mb-2">Шкала индекса:</p>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <Badge variant="danger">0-40</Badge>
                <span className="text-muted-foreground">Слабый клёв</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="warning">40-70</Badge>
                <span className="text-muted-foreground">Средний клёв</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="success">70-100</Badge>
                <span className="text-muted-foreground">Хороший клёв</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Signals */}
      <Card>
        <CardHeader>
          <CardTitle>Сигналы и флаги</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="warning">Фронт приближается</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Быстрое падение/рост давления (&gt;4 hPa/12h), сдвиг ветра, рост облачности.
              Обычно клёв слабый, но может быть короткое окно перед фронтом.
            </p>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="success">Стабильная погода</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Слабые изменения давления и ветра в течение 12+ часов. Лучшее время для рыбалки.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Pressure Chart */}
      <Card>
        <CardHeader>
          <CardTitle>График давления (MSLP)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p>
            Основной индикатор погодных условий. Показывает атмосферное давление на уровне моря.
          </p>

          <div className="space-y-2 text-sm">
            <div>
              <p className="font-semibold">ΔP/6h, ΔP/12h, ΔP/24h</p>
              <p className="text-muted-foreground">
                Тенденции изменения давления за 6, 12 и 24 часа. Помогают определить фронты.
              </p>
            </div>

            <div className="pt-2">
              <p className="font-semibold">Типичные значения:</p>
              <ul className="list-disc list-inside text-muted-foreground space-y-1">
                <li>1000-1015 hPa: низкое (циклон)</li>
                <li>1015-1025 hPa: нормальное</li>
                <li>1025+ hPa: высокое (антициклон)</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Theory Link */}
      <Card>
        <CardHeader>
          <CardTitle>Теоретическая основа</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Индекс основан на эмпирических наблюдениях рыболовов и метеорологических данных.
            Ключевой принцип: <strong>стабильность важнее абсолютных значений</strong>.
          </p>

          <div className="bg-muted/50 p-4 rounded-lg text-sm space-y-2">
            <p className="font-semibold">Краткая памятка:</p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Стабильное давление → хороший клёв</li>
              <li>Плавное падение (префронт) → короткий всплеск</li>
              <li>Резкий фронт/метель → клёв слабый</li>
              <li>1-2 дня после шторма → постепенное восстановление</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card>
        <CardHeader>
          <CardTitle>О приложении</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-3">
          <p>
            <strong>Версия:</strong> 0.1.0 (MVP)
          </p>
          <p>
            <strong>Данные:</strong> Open-Meteo (ECMWF, GFS, ICON), MET Norway Locationforecast
          </p>
          <p>
            <strong>Карта:</strong> © OpenStreetMap contributors
          </p>
          <p className="text-muted-foreground">
            Прогноз обновляется каждый час. Индекс клёва - экспериментальный,
            используйте как дополнительный инструмент к вашему опыту.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
