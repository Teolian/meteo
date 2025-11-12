# План приложения «Зимний клёв» (MVP)

## Цель
Непубличный веб-сервис для 1–5 пользователей (ЦФО), который:
- показывает **текущую погоду** и **почасовой прогноз на несколько дней** по выбранным водоёмам;
- визуализирует ключевые параметры (давление MSLP, ΔP/Δt, ветер, t, облачность, снег/осадки, снежный покров);
- рассчитывает **сигналы фронтальности** и **черновой индекс клёва**;
- даёт страницу с расширенной аналитикой для самостоятельного анализа.

---

## 1. Страницы и UX

### 1.1 Главная «Погода/Карта»
- **Верхняя панель:** выбор водоёма (селектор + поиск), дата/час, таймзона `Europe/Moscow`.
- **Карта (Leaflet):** точки водохранилищ/озёр ЦФО; клик → фокус на водоём; атрибуция OSM обязательна. Для личного пользования можно OSM-тайлы, но соблюдаем политику (не bulk-download, корректная атрибуция). citeturn1search1turn0search9turn0search14
- **Карточка «Сейчас»:** температура, давление MSLP, ветер/порыв, облачность, видимость, тип осадков (снег/дождь), снежный покров, «confidence score» прогноза.
- **Графики (почасовые):**
  - Давление MSLP (линия) + подграфик **ΔP/6h, ΔP/12h, ΔP/24h**.
  - Ветер (линия скорости + стрелки направления) и порывы.
  - Температура воздуха 2 м.
  - Осадки (снег/дождь) и **облачность**.
  - **Снежный покров** (если доступен).
  — Библиотека: **Recharts** (React-friendly). citeturn1search2turn1search8
- **Сигналы/флаги:**
  - `front_like`: быстрый спад/рост давления + сдвиг ветра + рост облачности/осадков.
  - `stable_window`: слабая |ΔP| и ветер ≤ порога за 12–48 ч.
- **Индекс клёва v0:** взвешенная формула (см. §4.3), показывается как шкала + текстовая подсказка.

### 1.2 «Аналитика»
- **Сравнение провайдеров** (по MSLP/ветру/осадкам) для выбранного водоёма: серия графиков «ансамбль моделей».
- **Калибровка/ошибка**: сравнение прогноза ↔ фактические наблюдения Meteostat (MAE за неделю).
- **Редактор правил вида/водоёма**: веса для щуки/судака/окуня/белой рыбы (ручная правка коэффициентов индекса).
- **Экспорт CSV** выбранного диапазона + текущие «сигналы».

### 1.3 Справка (микро-FAQ)
- что означают графики и «сигналы»; краткая памятка по зимнему клёву.

---

## 2. Источники данных (MVP)

- **Open-Meteo** — прогноз без ключа: почасовой MSLP/поверхностное давление, t2m, ветер/порывы, осадки (в т.ч. снег), облачность, **snow_depth**; есть Historical API. citeturn0search0turn0search5turn0search15  
- **MET Norway (met.no, Locationforecast 2.0)** — прогноз с `User-Agent` (иначе 403). Есть поле `air_pressure_at_sea_level`, t, ветер, осадки и др. citeturn0search11turn0search16  
- **OpenWeather One Call 3.0** — fallback/валидация; free tier **1000 calls/day** (по подписке «One Call by Call»). citeturn0search3turn0search8  
- **Meteostat** — исторические **почасовые наблюдения** по станциям/точкам (t, давление, ветер, осадки и др.) для валидации/калибровки. citeturn0search2turn0search7  
- **Карта:** Leaflet + OSM тайлы (для MVP) с соблюдением Tile Usage Policy. Для роста — провайдер вроде MapTiler. citeturn1search1turn0search9

---

## 3. Технологии и деплой

- **Frontend:** React + Vite, Recharts, Leaflet. Деплой статики на **Vercel** (прямое руководство по React). citeturn1search12turn1search15  
- **Backend:** **FastAPI** (Python). Интеграции с Open-Meteo/met.no/OpenWeather, кэширование, расчёт сигналов. Фоновые задачи через `BackgroundTasks`/APScheduler; для долгоживущих задач — вынести в воркер (позже). citeturn1search0  
- **БД:** MVP — SQLite (файловая, простая). Опционально: PostgreSQL (+Timescale) на рост.  
- **Контейнеризация:** Docker для backend; локальный запуск через `docker-compose`.  
- **Развёртывание backend:** любой контейнер-хост (Render/Fly/VM). Фронт — Vercel; фронт обращается к backend по HTTPS.

---

## 4. API (контракты backend)

База: `FastAPI`, все ответы `application/json`, `tz=Europe/Moscow` по умолчанию.

### 4.1 `/api/forecast`
**GET** параметры:  
`lat`, `lon` (обяз.), `hours=120`, `provider=["open-meteo","metno","openweather"]` (список), `include=["mslp","t2m","wind","gust","cloud","precip","snowfall","snow_depth","visibility"]`.

**Ответ (схема):**
```json
{
  "meta": { "lat": 56.0, "lon": 37.0, "timezone": "Europe/Moscow", "providers": ["open-meteo","metno"] },
  "hourly": [
    {
      "time": "2025-11-12T12:00:00+03:00",
      "mslp_hpa": 1007.6,
      "surface_pressure_hpa": 1006.9,
      "t2m_c": -7.3,
      "wind10_mps": 4.2,
      "wind_dir_deg": 210,
      "gust_mps": 7.8,
      "cloud_pct": 85,
      "precip_mm": 0.3,
      "snowfall_mm": 0.3,
      "snow_depth_cm": 18.0,
      "visibility_km": 9.5,
      "provider": "open-meteo"
    }
  ]
}
```
> Примечание: переменные соответствуют документированным полям Open-Meteo (`pressure_msl`, `snow_depth`, и т.д.) и мет.no (`air_pressure_at_sea_level`). citeturn0search0turn0search15turn0search11

### 4.2 `/api/signals`
**GET** параметры: `lat`, `lon`, `hours=120`, `window=[6,12,24]`, `thresholds` (опц.).

**Логика (внутри backend):**
- расчёт **ΔP/Δt** для окон 6/12/24 ч;
- детекция `front_like` (|ΔP| выше порога + сдвиг ветра ≥ X° за 6–12 ч + рост облачности/осадков);
- маркировка `stable_window` (|ΔP| ниже порога и ветер ≤ порога N часов подряд).

**Ответ (схема):**
```json
{
  "trend": { "dP6_hpa": -3.2, "dP12_hpa": -5.1, "dP24_hpa": -7.8 },
  "flags": [
    {"time": "2025-11-12T18:00:00+03:00", "front_like": true, "reason": ["dP12<-4", "wind_shift>45", "cloud+precip↑"]},
    {"time": "2025-11-14T12:00:00+03:00", "stable_window": true}
  ]
}
```

### 4.3 `/api/bite-index`
**GET** параметры: `lat`, `lon`, `hours=120`, `species=["pike","walleye","perch","bream"]`.

**Формула v0 (эвристика):**
```
score = w_stab * S_stab(ΔP) 
      + w_pref * S_pref(species, T, time_of_day)
      + w_wind * S_wind(скорость, сдвиг, порывы)
      + w_cloud * S_cloud(облачность)
      + w_snow * S_snow(снег, снежный покров)
      + w_front * S_front(front_like)
```
- `S_stab(ΔP)` — максимум при |ΔP/12h| низком;  
- `S_front` — бонус за «префронт» (плавное падение, окно короткое), штраф за «фронт сейчас»;  
- `S_pref` — корректировка по виду (например, щука ↑ при плавном падении, судак терпимее к морозу/высокому давлению и ночи).  
- Возвращаем `score ∈ [0,100]` + пояснение факторов.

**Ответ (схема):**
```json
{
  "meta": {"species": ["pike","perch"]},
  "hourly": [
    {"time":"2025-11-12T15:00:00+03:00","score":62,"explain":["stable pressure","low wind"]},
    {"time":"2025-11-12T18:00:00+03:00","score":74,"explain":["pre-front drop","cloud↑","light snow"]}
  ],
  "confidence": "medium"
}
```

### 4.4 `/api/waterbodies`
- CRUD для локального списка озёр/водохранилищ (название, координаты, регион, тип).  
- MVP: JSON-файл/таблица `waterbodies`.

---

## 5. Схема данных

### 5.1 Таблицы (SQL)
- `waterbodies(id, name, lat, lon, region, type)`  
- `forecast_hourly(id, wb_id, time, provider, mslp_hpa, t2m_c, wind10_mps, wind_dir_deg, gust_mps, cloud_pct, precip_mm, snowfall_mm, snow_depth_cm, visibility_km, created_at)`  
- `signals(id, wb_id, time, dP6, dP12, dP24, front_like, stable_window, created_at)`  
- `metrics(id, wb_id, time, score, species_mask, confidence, explain_json, created_at)`  
- `obs_hourly(id, wb_id, station_id, time, mslp_hpa, t2m_c, wind10_mps, precip_mm, created_at)` — из Meteostat (для калибровки). citeturn0search2

### 5.2 Кэш
- In-memory (`lru_cache`) на 5–15 мин + дисковый кэш на 1–3 ч для одного водоёма/часа.

---

## 6. Интеграции (детали)

### 6.1 Open-Meteo (без ключа)
- Пример эндпоинта:  
  `https://api.open-meteo.com/v1/forecast?latitude=56.0&longitude=37.0&hourly=pressure_msl,temperature_2m,wind_speed_10m,wind_direction_10m,gusts_10m,cloud_cover,precipitation,snowfall,snow_depth,visibility&timezone=Europe%2FMoscow`  
- Также **Historical Weather API** для валидации (reanalysis). citeturn0search0turn0search5

### 6.2 MET Norway (Locationforecast 2.0)
- Требуется **кастомный `User-Agent`**, иначе 403.  
- Поля включают `air_pressure_at_sea_level`, t, ветер, осадки, облачность.  
- Базовая документация и FAQ. citeturn0search11turn0search16

### 6.3 OpenWeather (One Call 3.0)
- Free tier 1000 calls/day в плане **One Call by Call**; текущая/почасовая/дневная + алерты. citeturn0search3turn0search18

### 6.4 Meteostat
- **Hourly Station/Point** API для фактических наблюдений; лимиты окна и задержки (данные приходят с лагом ~2–3 ч). citeturn0search2turn0search7

### 6.5 Карта/тайлы
- **Leaflet** (Quick Start) + **OSM Tile Usage Policy**: атрибуция, запрет bulk-загрузки. Для роста — перейти на MapTiler/др. провайдера с ключом. citeturn1search1turn0search9

---

## 7. Стек и пакеты

**Frontend**
- React + Vite  
- `recharts` (графики) citeturn1search2  
- `leaflet` (карта) citeturn1search1

**Backend**
- FastAPI + httpx/requests  
- APScheduler / FastAPI BackgroundTasks citeturn1search0  
- SQLite (SQLModel/SQLAlchemy)  
- Pydantic для схем

**DevOps**
- Dockerfile (backend), docker-compose для локали  
- Vercel (frontend) — гайд деплоя React, CDN кеш. citeturn1search12turn1search15

---

## 8. Конфигурация и секреты

`.env` (backend):
```
OPENWEATHER_KEY=...
METNO_USER_AGENT="MyIceFishingApp/0.1 (contact: you@example.com)"
TZ=Europe/Moscow
```
> Open-Meteo не требует ключа. met.no требует корректный `User-Agent`. citeturn0search11

---

## 9. Сценарии обновления данных

- **Инкрементальное обновление** каждые 60–120 мин: тянем 48–120 ч вперёд, обновляем `forecast_hourly`.
- После загрузки: рассчитываем `signals` и `bite-index` для окна.
- Ночной джоб: подтягиваем **Meteostat** за прошедшие сутки, считаем простую калибровку смещения (bias) по давлению/ветру. citeturn0search7

---

## 10. Индекс клёва v0 (детализация)

### 10.1 Признаки
- `ΔP6/12/24`, `wind_speed/shift/gust`, `cloud_pct`, `precip/snowfall`, `snow_depth`, `t2m`.  
- Сигналы: `front_like`, `stable_window`.  
- Время суток (сумерки/день/ночь) — модификатор.

### 10.2 Весовые коэффициенты (по умолчанию)
- `w_stab=0.35`, `w_front=0.25`, `w_wind=0.15`, `w_cloud=0.10`, `w_snow=0.10`, `w_pref=0.05`.  
- Видовые пресеты: `pike`, `walleye`, `perch`, `bream` (редактируемые в UI).

### 10.3 Confidence score
- функция консенсуса провайдеров (разброс MSLP), величины |ΔP| (буря → ниже), горизонта прогноза (дальше → ниже).

---

## 11. Карта и водоёмы ЦФО

- Таблица `waterbodies` с координатами и тегами.  
- Leaflet слой точек + попапы: «быстрый взгляд» (MSLP, ΔP/12h, ветер, краткий прогноз на 48 ч). citeturn1search1  
- Фильтр: «только водохранилища» / «реки/озёра» / «избранные».

---

## 12. Docker и локальный запуск

`docker-compose.yml` (эскиз):
```yaml
services:
  api:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
    volumes: ["./backend:/app"]
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    environment:
      - VITE_API_URL=http://localhost:8000
```

---

## 13. Деплой

- **Frontend (Vercel):** подключить Git, `npm run build`, публикация; CDN-кеш для статики. citeturn1search18turn1search15  
- **Backend:** Render/Fly/VM c Docker-образом; домен `api.example.com`.  
- CORS: разрешить фронтовый домен Vercel.

---

## 14. Мини-бэклог (последовательность работ)

1) База фронта: карта Leaflet + выбор водоёма + графики Recharts (MSLP/ΔP/ветер/t/облачность/осадки/снег). citeturn1search1turn1search2  
2) Backend: `/api/forecast` (Open-Meteo), кэш. citeturn0search0  
3) Signals: `/api/signals` (ΔP/флаги), отрисовка «сигналов» на таймлайне.
4) Индекс клёва v0: `/api/bite-index` + UI.
5) История/валидация: Meteostat, страница «Аналитика» (MAE/калибровка). citeturn0search2  
6) Подключить met.no как второй провайдер; добавить сравнение моделей. citeturn0search11  
7) Экспорт CSV, избранные водоёмы, настройки видов.
8) Fallback OpenWeather (при лимитах/деградации). citeturn0search3

---

## 15. Дорожная карта (после MVP)

- **Байт-коррекция / ансамблевый блендинг** по провайдерам; простая ML-модель (XGBoost) для `score` с обучением на ваших логах клёва + Meteostat.  
- **Карта «градиента давления»** (5–9 точек вокруг водоёма) → тепловая карта «фронтальности».  
- **Персональные профили видов/водоёмов** (подбор веса по вашим наблюдениям).  
- **Мобильный PWA**, оффлайн-кэш слоёв (только не тайлы — соблюдать политику OSM). citeturn0search9
