# ❄️ Ice Fishing Bite Index MVP

Private web application for ice fishing weather forecast and bite index, focused on Central Russia waterbodies.

## 🎯 Features

- **Weather Forecast**: Hourly weather data from Open-Meteo and MET Norway
- **Bite Index**: AI-calculated fishing bite index (0-100) based on weather patterns
- **Signal Detection**: Automatic detection of weather fronts and stable fishing windows
- **Interactive Map**: Leaflet-based map with waterbody selection
- **Responsive Charts**: Recharts visualizations for MSLP, wind, temperature, precipitation, and snow
- **Mobile-First**: PWA-ready with offline support and mobile-optimized UI
- **Dark/Light Themes**: CSS variable-based theming

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **SQLModel** + SQLite for data persistence
- **httpx** for async HTTP requests
- Weather providers: Open-Meteo (no key), MET Norway (requires User-Agent), optional OpenWeather
- In-memory and file-based caching

### Frontend
- **React 18** + **Vite**
- **TypeScript**
- **Tailwind CSS** + shadcn/ui components
- **Recharts** for data visualization
- **Leaflet** + **React-Leaflet** for maps
- **Vite PWA** for offline support

### DevOps
- **Docker** + **docker-compose** for backend
- **Vercel**-ready frontend deployment

## 📦 Project Structure

```
meteo/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, database, cache
│   │   ├── models/        # SQLModel & Pydantic schemas
│   │   ├── services/      # Weather providers, calculators
│   │   └── tests/         # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── seed_waterbodies.json
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Main pages
│   │   ├── services/      # API client
│   │   └── utils/         # Utilities
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Docker** + **docker-compose** (for backend)
- **Node.js 18+** + **npm** (for frontend)
- **Python 3.11+** (optional, for local backend development)

### 1. Clone and Setup

```bash
cd meteo
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# REQUIRED: MET Norway User-Agent
METNO_USER_AGENT=YourApp/0.1 (contact: your-email@example.com)

# Optional: OpenWeather API key (if using OpenWeather provider)
OPENWEATHER_KEY=your_key_here

# Timezone
TZ=Europe/Moscow
```

### 3. Start Backend (Docker)

```bash
# Build and start backend
docker-compose up -d

# Check logs
docker-compose logs -f api

# Backend will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Seed Database

```bash
# Enter backend container
docker exec -it meteo-api bash

# Run seed script
python seed_db.py

# Exit container
exit
```

### 5. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend will be available at http://localhost:5173
```

## 🔧 Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see above)

# Seed database
python seed_db.py

# Run development server
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🧪 Running Tests

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📚 API Endpoints

### Forecast
```
GET /api/forecast?lat=56.0&lon=37.0&hours=120&provider=open-meteo
```

### Signals (Pressure Trends)
```
GET /api/signals?lat=56.0&lon=37.0&hours=120&window=6,12,24
```

### Bite Index
```
GET /api/bite-index?lat=56.0&lon=37.0&hours=120&species=pike,perch
```

### Waterbodies (CRUD)
```
GET /api/waterbodies
GET /api/waterbodies/{id}
POST /api/waterbodies
PATCH /api/waterbodies/{id}
DELETE /api/waterbodies/{id}
```

Full API documentation: `http://localhost:8000/docs`

## 🌍 Weather Data Sources

### Open-Meteo
- **No API key required**
- Ensemble models: ECMWF, GFS, ICON
- Hourly data: MSLP, temperature, wind, precipitation, snow depth
- Historical data available for validation

### MET Norway (Locationforecast 2.0)
- **Requires User-Agent header** (configured in `.env`)
- High-quality European forecasts
- Respects their fair-use policy

### OpenWeather One Call 3.0 (Optional)
- Requires API key
- Free tier: 1000 calls/day
- Used as fallback/validation

## 🎨 Design System

- **Typography**: Inter font family
- **Colors**: CSS variables for light/dark themes
- **Border Radius**: lg=10px, xl=14px, 2xl=20px
- **Mobile-First**: Optimized for 360px+ screens
- **Accessibility**: WCAG AA compliant, keyboard navigation

## 📱 PWA Features

- Service worker with stale-while-revalidate caching
- Offline access to latest forecast
- App manifest for installation
- Respects OSM tile usage policy (no bulk caching)

## 🗃️ Database Schema

- `waterbodies`: Reservoir/lake metadata
- `forecast_hourly`: Cached weather forecast data
- `signals`: Calculated pressure trends and flags
- `metrics`: Bite index calculations

## 🔍 Bite Index Algorithm (v0)

The bite index is calculated using weighted factors:

- **Pressure Stability** (35%): Low |ΔP/12h| = better fishing
- **Front Signals** (25%): Pre-front drop = short feeding window; active front = poor
- **Wind** (15%): Low wind preferred
- **Cloud Cover** (10%): Moderate clouds optimal
- **Snow/Precipitation** (10%): Light snow OK, heavy storm bad
- **Species Preference** (5%): Species-specific adjustments

**Output**: Score 0-100 with explanations and confidence level

## 🚢 Deployment

### Backend (Render/Fly.io/VPS)

```bash
# Build Docker image
docker build -t meteo-api ./backend

# Run container
docker run -p 8000:8000 --env-file .env meteo-api
```

### Frontend (Vercel)

```bash
cd frontend

# Build
npm run build

# Deploy to Vercel
# Connect Git repository or use Vercel CLI
vercel --prod
```

## 📋 Plan Adherence Checklist

- [x] Monorepo structure (backend/, frontend/)
- [x] Backend: FastAPI with Open-Meteo, MET Norway, (OpenWeather optional)
- [x] Backend: `/api/forecast`, `/api/signals`, `/api/bite-index`, `/api/waterbodies`
- [x] Backend: SQLite database with SQLModel
- [x] Backend: Caching layer (memory + file)
- [x] Backend: Signal calculations (ΔP, front detection, stable windows)
- [x] Backend: Bite index v0 with species profiles
- [x] Backend: Unit tests for signal math
- [x] Frontend: React + Vite + TypeScript
- [x] Frontend: Leaflet map with OSM tiles
- [x] Frontend: Recharts for weather visualization
- [x] Frontend: Weather/Map, Analytics, Help pages
- [x] Frontend: Mobile-first responsive design
- [x] Frontend: PWA support
- [x] Docker + docker-compose for backend
- [x] Seed data: 7 CFO reservoirs/lakes
- [x] .env.example with configuration
- [x] README with setup instructions

## 🔒 Security & Privacy

- No API keys hardcoded
- MET Norway User-Agent requirement enforced
- Private deployment (1-5 users)
- CORS configured for frontend origin
- Environment variables for sensitive data

## 📝 License

Private project for personal use.

## 🙏 Acknowledgments

- **Weather Data**: Open-Meteo, MET Norway
- **Maps**: © OpenStreetMap contributors
- **Theory**: Based on empirical ice fishing observations and meteorological principles

## 🐛 Known Limitations (MVP)

- No user authentication (private deployment assumed)
- No historical data tracking yet
- Meteostat integration pending
- Provider comparison not fully implemented
- Export to CSV pending
- Species weight editing in UI pending

## 🔮 Future Roadmap

- ML-based bite index refinement
- Historical data analysis
- Custom species/waterbody profiles
- Mobile app (React Native)
- Push notifications for optimal conditions
- Social features (reports from anglers)

---

**Version**: 0.1.0 (MVP)
**Last Updated**: 2025-11-12
