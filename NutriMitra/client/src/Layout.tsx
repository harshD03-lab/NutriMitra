import { Outlet, Link } from 'react-router-dom'

export default function Layout() {
  const token = localStorage.getItem('token')
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-emerald-700 text-white px-6 py-3 flex items-center justify-between shadow">
        <Link to="/" className="text-xl font-bold tracking-tight">NutriMitra</Link>
        <nav className="flex gap-4 text-sm">
          {token ? (
            <>
              <Link to="/dashboard" className="hover:underline">Dashboard</Link>
              <button
                onClick={() => { localStorage.clear(); location.href = '/' }}
                className="hover:underline cursor-pointer"
              >
                Logout
              </button>
            </>
          ) : (
            <Link to="/" className="hover:underline">Home</Link>
          )}
        </nav>
      </header>
      <main className="flex-1 px-4 py-8 max-w-3xl mx-auto w-full">
        <Outlet />
      </main>
    </div>
  )
}
