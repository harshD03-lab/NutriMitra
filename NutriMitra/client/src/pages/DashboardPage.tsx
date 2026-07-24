import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe } from '../api'

interface UserProfile {
  id: number
  email: string
  name: string
  age: number | null
  gender: string | null
  height_cm: number | null
  weight_kg: number | null
  activity_level: string | null
  diet_type: string | null
  medical_conditions: string | null
}

export default function DashboardPage() {
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) { nav('/'); return }
    getMe(token)
      .then(setUser)
      .catch(() => { localStorage.clear(); nav('/') })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-center py-20 text-gray-500">Loading...</p>
  if (!user) return null

  const updateField = async (field: string, value: string | number | null) => {
    setUser({ ...user, [field]: value })
    setMessage('Profile updated (UI only for now)')
    setTimeout(() => setMessage(''), 3000)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Welcome, {user.name}</h1>
      {message && <p className="text-emerald-600 text-sm">{message}</p>}

      <section className="bg-white rounded-xl shadow-sm border p-5 space-y-4">
        <h2 className="text-lg font-semibold">Your Profile</h2>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Age" value={user.age} onChange={v => updateField('age', v ? Number(v) : null)} />
          <Field label="Gender" value={user.gender} onChange={v => updateField('gender', v)} placeholder="male/female" />
          <Field label="Height (cm)" value={user.height_cm} onChange={v => updateField('height_cm', v ? Number(v) : null)} />
          <Field label="Weight (kg)" value={user.weight_kg} onChange={v => updateField('weight_kg', v ? Number(v) : null)} />
          <Field label="Activity" value={user.activity_level} onChange={v => updateField('activity_level', v)} placeholder="sedentary/light/moderate/active/very_active" />
          <Field label="Diet Type" value={user.diet_type} onChange={v => updateField('diet_type', v)} placeholder="balanced/low-carb/high-protein" />
          <div className="col-span-2">
            <label className="block text-xs text-gray-500 mb-1">Medical Conditions</label>
            <input
              value={user.medical_conditions || ''}
              onChange={e => updateField('medical_conditions', e.target.value || null)}
              placeholder="e.g. diabetes, hypertension"
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>
      </section>

      {user.age && user.gender && user.height_cm && user.weight_kg && user.activity_level && (
        <NutrientTargetsCard profile={user} />
      )}
    </div>
  )
}

function Field({ label, value, onChange, placeholder }: {
  label: string
  value: string | number | null
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <input
        value={value ?? ''}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border rounded-lg px-3 py-2 text-sm"
      />
    </div>
  )
}

function NutriTargetsCard({ profile }: { profile: UserProfile }) {
  const bmr = profile.gender?.toLowerCase() === 'male'
    ? 10 * (profile.weight_kg ?? 0) + 6.25 * (profile.height_cm ?? 0) - 5 * (profile.age ?? 0) + 5
    : 10 * (profile.weight_kg ?? 0) + 6.25 * (profile.height_cm ?? 0) - 5 * (profile.age ?? 0) - 161

  const mult: Record<string, number> = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, very_active: 1.9 }
  const tdee = bmr * (mult[profile.activity_level ?? ''] || 1.2)

  return (
    <section className="bg-white rounded-xl shadow-sm border p-5">
      <h2 className="text-lg font-semibold mb-3">Your Daily Nutrition Targets</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <NutriBox label="Calories" value={`${Math.round(tdee)}`} unit="kcal" color="emerald" />
        <NutriBox label="Protein" value={`${Math.round(tdee * 0.2 / 4)}`} unit="g" color="blue" />
        <NutriBox label="Carbs" value={`${Math.round(tdee * 0.55 / 4)}`} unit="g" color="amber" />
        <NutriBox label="Fat" value={`${Math.round(tdee * 0.25 / 9)}`} unit="g" color="rose" />
      </div>
    </section>
  )
}

function NutriBox({ label, value, unit, color }: { label: string; value: string; unit: string; color: string }) {
  const colors: Record<string, string> = {
    emerald: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    amber: 'bg-amber-50 border-amber-200 text-amber-800',
    rose: 'bg-rose-50 border-rose-200 text-rose-800',
  }
  return (
    <div className={`rounded-lg border p-3 text-center ${colors[color]}`}>
      <p className="text-xs font-medium uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs">{unit}</p>
    </div>
  )
}
