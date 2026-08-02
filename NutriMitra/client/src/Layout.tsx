import { Outlet, NavLink, Link } from 'react-router-dom'

function LogoMark() {
  return (
    <span className="grid h-9 w-9 place-items-center rounded-full bg-saffron text-paper">
      <span className="grid h-6 w-6 place-items-center rounded-full bg-paper">
        <span className="font-display text-sm font-bold text-saffron-deep">N</span>
      </span>
    </span>
  )
}

export default function Layout() {
  const token = localStorage.getItem('token')

  const navLink = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors ${
      isActive
        ? 'bg-saffron-soft text-saffron-deep'
        : 'text-clay hover:bg-paper hover:text-ink'
    }`

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 border-b border-rim bg-paper/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <Link
            to="/"
            className="flex items-center gap-2.5 font-display text-xl font-bold tracking-tight"
          >
            <LogoMark />
            <span>
              Nutri<span className="text-saffron-deep">Mitra</span>
            </span>
          </Link>
          <nav className="flex items-center gap-2">
            {token ? (
              <>
                <NavLink to="/dashboard" className={navLink}>
                  Dashboard
                </NavLink>
                <NavLink to="/foods" className={navLink}>
                  Foods
                </NavLink>
                <button
                  onClick={() => {
                    localStorage.clear()
                    location.href = '/'
                  }}
                  className="cursor-pointer rounded-full border border-rim px-3.5 py-1.5 text-sm font-medium text-clay transition-colors hover:border-chilli hover:text-chilli"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/"
                className="rounded-full bg-saffron px-4 py-1.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-saffron-deep"
              >
                Get started
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-rim py-6 text-center font-mono text-xs text-clay">
        NutriMitra · built on ICMR-NIN Indian food data
      </footer>
    </div>
  )
}
