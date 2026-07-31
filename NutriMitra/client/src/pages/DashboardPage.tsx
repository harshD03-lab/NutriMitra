import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, getRecommendations } from '../api'
import type { UserProfile, RecommendationResponse, MealPlan, MealItem } from '../api'

export default function DashboardPage() {
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [plan, setPlan] = useState<RecommendationResponse | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { nav('/'); return }
    getMe(token)
      .then(setUser)
      .catch(() => { localStorage.clear(); nav('/') })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-center py-20 text-gray-500">Loading...</p>
  if (!user) return null

  const updateField = (field: string, value: string | number | null) => {
    setUser({ ...user, [field]: value })
    setMessage('Profile updated (UI only for now)')
    setPlan(null)
    setTimeout(() => setMessage(''), 3000)
  }

  const generatePlan = async () => {
    if (!token) return
    setGenerating(true)
    setError('')
    try {
      const profile = {
        age: user.age,
        gender: user.gender,
        height_cm: user.height_cm,
        weight_kg: user.weight_kg,
        activity_level: user.activity_level,
        diet_type: user.diet_type,
        medical_conditions: user.medical_conditions,
      }
      const data = await getRecommendations(token, profile)
      setPlan(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate plan')
    } finally {
      setGenerating(false)
    }
  }

  const canGenerate = Boolean(user.age && user.gender && user.height_cm && user.weight_kg && user.activity_level)

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

      {canGenerate && <NutrientTargetsCard profile={user} />}

      <section className="bg-white rounded-xl shadow-sm border p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">AI Meal Plan</h2>
          <button
            onClick={generatePlan}
            disabled={!canGenerate || generating}
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {generating ? 'Generating...' : 'Generate Meal Plan'}
          </button>
        </div>
        {!canGenerate && (
          <p className="text-xs text-gray-500 mt-2">Fill in age, gender, height, weight and activity to generate a plan.</p>
        )}
        {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
        {plan && <MealPlanView plan={plan} />}
      </section>
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

function NutrientTargetsCard({ profile }: { profile: UserProfile }) {
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

function MealPlanView({ plan }: { plan: RecommendationResponse }) {
  return (
    <div className="mt-5 space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <NutriBox label="Total Calories" value={`${Math.round(plan.total_calories)}`} unit="kcal" color="emerald" />
        <NutriBox label="Protein" value={`${Math.round(plan.total_protein)}`} unit="g" color="blue" />
        <NutriBox label="Carbs" value={`${Math.round(plan.total_carbs)}`} unit="g" color="amber" />
        <NutriBox label="Fat" value={`${Math.round(plan.total_fat)}`} unit="g" color="rose" />
      </div>

      {plan.meal_plan.map(slot => (
        <MealSlot key={slot.meal} slot={slot} />
      ))}

      {plan.explanation && (
        <div className="bg-gray-50 rounded-lg border p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-2">Why these foods?</p>
          <div className="space-y-1">
            {plan.explanation.split('|').map((line, i) => (
              <p key={i} className="text-sm text-gray-700">{line.trim()}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function MealSlot({ slot }: { slot: MealPlan }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-emerald-700 uppercase tracking-wide mb-2">{slot.meal}</h3>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-3 py-2 font-medium">Food</th>
              <th className="px-3 py-2 font-medium text-right">Cal</th>
              <th className="px-3 py-2 font-medium text-right">Protein</th>
              <th className="px-3 py-2 font-medium text-right">Carbs</th>
              <th className="px-3 py-2 font-medium text-right">Fat</th>
            </tr>
          </thead>
          <tbody>
            {slot.items.map((item, i) => (
              <FoodRow key={i} item={item} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function FoodRow({ item }: { item: MealItem }) {
  return (
    <tr className="border-t">
      <td className="px-3 py-2">
        <p className="font-medium">{item.food_name}</p>
        <p className="text-xs text-gray-500">{item.serving_size}</p>
      </td>
      <td className="px-3 py-2 text-right">{Math.round(item.calories)}</td>
      <td className="px-3 py-2 text-right">{item.protein_g.toFixed(1)}</td>
      <td className="px-3 py-2 text-right">{item.carbs_g.toFixed(1)}</td>
      <td className="px-3 py-2 text-right">{item.fat_g.toFixed(1)}</td>
    </tr>
  )
}
