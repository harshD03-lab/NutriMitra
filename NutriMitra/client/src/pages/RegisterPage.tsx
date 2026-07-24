import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register, login } from '../api'

export default function RegisterPage() {
  const nav = useNavigate()
  const [tab, setTab] = useState<'login' | 'register'>('register')
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      if (tab === 'register') {
        await register(form)
        await loginFn()
      } else {
        await loginFn()
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  const loginFn = async () => {
    const data = await login({ email: form.email, password: form.password })
    localStorage.setItem('token', data.access_token)
    nav('/dashboard')
  }

  const token = localStorage.getItem('token')
  if (token) {
    return (
      <div className="text-center py-20">
        <p className="text-lg mb-4">You're logged in.</p>
        <a href="/dashboard" className="text-emerald-600 underline">Go to Dashboard</a>
      </div>
    )
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <h1 className="text-2xl font-bold text-center mb-6">Welcome to NutriMitra</h1>
      <p className="text-gray-500 text-center mb-6 text-sm">
        Your AI-powered Indian diet planner
      </p>

      <div className="flex mb-6 border rounded-lg overflow-hidden">
        <button
          onClick={() => setTab('register')}
          className={`flex-1 py-2 text-sm font-medium ${tab === 'register' ? 'bg-emerald-600 text-white' : 'bg-white text-gray-600'}`}
        >
          Register
        </button>
        <button
          onClick={() => setTab('login')}
          className={`flex-1 py-2 text-sm font-medium ${tab === 'login' ? 'bg-emerald-600 text-white' : 'bg-white text-gray-600'}`}
        >
          Login
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {tab === 'register' && (
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              required
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email" required
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password" required
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full bg-emerald-600 text-white py-2 rounded-lg font-medium hover:bg-emerald-700 cursor-pointer"
        >
          {tab === 'register' ? 'Create Account' : 'Sign In'}
        </button>
      </form>
    </div>
  )
}
