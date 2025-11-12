
# DESIGN.md — Дизайн‑система и mobile‑first для «Зимний клёв»

## 1) Принципы
- Чистый, долговечный дизайн без AI‑генераторов.
- Mobile‑first: удобно одной рукой.
- Доступность: WCAG AA, видимые фокусы.
- Темы: light/dark через CSS‑переменные.

## 2) Токены
- Типографика: Inter/Ui Sans; 12/14/16/20/24/32/40; `lh=1.5`.
- Радиусы: `lg=10px`, `xl=14px`, `2xl=20px`; тени: `sm/md/lg`.
- Цвета: `--bg/--fg/--muted/--accent/--accent-2/--danger` (+ dark).

## 3) Компоненты (Tailwind + shadcn/ui)
AppShell, Card, Tabs, Button, Input, Select, Switch, Badge, Tooltip, Modal/Drawer, ChartCard, MapPanel, StatusPills.

## 4) Макеты
- Главная: селектор водоёма, карта Leaflet, карточка «Сейчас», графики (MSLP+ΔP, Wind, T2m, Cloud+Precip/Snow, Snow Depth), лента сигналов.
- Аналитика: ансамбль провайдеров, MAE vs Meteostat, редактор весов.
- Справка: пояснения графиков/флагов/индекса.
- Mobile: карта в Drawer; графики по одному столбцу.

## 5) PWA
- `manifest.webmanifest`, сервис‑воркер SW (stale‑while‑revalidate) для App Shell и `/api/*` (не кэшировать OSM‑тайлы надолго).

## 6) Критерии дизайна
- Lighthouse ≥ 90; AXE — без критичных ошибок.
- Читаемость графиков на ширине 360.
- Offline доступ к последнему прогнозу (без тайлов OSM).
