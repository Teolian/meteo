import { Routes, Route } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { WeatherPage } from './pages/WeatherPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { HelpPage } from './pages/HelpPage'

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<WeatherPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </AppShell>
  )
}

export default App
