import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, CloudSnow, BarChart3, HelpCircle } from 'lucide-react'
import { cn } from '@/utils/cn'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Погода', href: '/', icon: CloudSnow },
    { name: 'Аналитика', href: '/analytics', icon: BarChart3 },
    { name: 'Справка', href: '/help', icon: HelpCircle },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 flex flex-1 items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <CloudSnow className="h-6 w-6 text-primary" />
              <span className="hidden font-bold sm:inline-block">
                Зимний клёв
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    'flex items-center space-x-2 transition-colors hover:text-foreground/80',
                    location.pathname === item.href
                      ? 'text-foreground'
                      : 'text-foreground/60'
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              ))}
            </nav>

            {/* Mobile menu button */}
            <button
              type="button"
              className="md:hidden inline-flex items-center justify-center rounded-md p-2 text-foreground hover:bg-accent"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span className="sr-only">Открыть меню</span>
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b bg-background">
          <nav className="container space-y-1 px-4 py-3">
            {navigation.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  'flex items-center space-x-3 rounded-md px-3 py-2 text-sm font-medium',
                  location.pathname === item.href
                    ? 'bg-accent text-accent-foreground'
                    : 'text-foreground/60 hover:bg-accent hover:text-accent-foreground'
                )}
                onClick={() => setMobileMenuOpen(false)}
              >
                <item.icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        </div>
      )}

      {/* Main Content */}
      <main className="container py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-8">
        <div className="container flex flex-col items-center justify-between gap-4 md:flex-row">
          <p className="text-center text-sm text-muted-foreground">
            © 2025 Зимний клёв. Данные: Open-Meteo, MET Norway.
          </p>
        </div>
      </footer>
    </div>
  )
}
