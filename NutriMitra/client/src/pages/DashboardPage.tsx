import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, getRecommendations, getPlans, getPlan, deletePlan } from '../api'
import type { UserProfile, RecommendationResponse, MealPlan, MealItem, PlanSummary, SavedPlan } from '../api'
import ThaliRing from '../components/ThaliRing'

const MACRO_COLORS = {
  protein: 'var(--color-leaf)',
  carbs: 'var(--color-saffron)',
  fat: 'var(--color-chilli)',
}

export default function DashboardPage() {
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [plan, setPlan] = useState<RecommendationResponse | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [savedPlans, setSavedPlans] = useState<PlanSummary[]>([])
  const [viewingPlan, setViewingPlan] = useState<SavedPlan | null>(null)

  const loadHistory = (t: string) => {
    getPlans(t)
      .then(setSavedPlans)
      .catch(() => {})
  }

  useEffect(() => {
    if (!token) { nav('/'); return }
    getMe(token)
      .then(u => { setUser(u); loadHistory(token) })
      .catch(() => { localStorage.clear(); nav('/') })
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (loading) return <p className="py-24 text-center text-clay">Loading your plan…</p>
  if (!user) return null

  const updateField = (field: string, value: string | number | null) => {
    setUser({ ...user, [field]: value })
    setMessage('Profile updated — refresh targets with a new plan')
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
      setViewingPlan(null)
      loadHistory(token)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate plan')
    } finally {
      setGenerating(false)
    }
  }

  const openSavedPlan = async (planId: number) => {
    if (!token) return
    try {
      const saved = await getPlan(token, planId)
      setViewingPlan(saved)
      setPlan(null)
      setError('')
    } catch {
      setError('Failed to load saved plan')
    }
  }

  const removeSavedPlan = async (planId: number) => {
    if (!token) return
    try {
      await deletePlan(token, planId)
      setSavedPlans(p => p.filter(x => x.id !== planId))
      if (viewingPlan?.id === planId) setViewingPlan(null)
    } catch {
      setError('Failed to delete plan')
    }
  }

  const canGenerate = Boolean(user.age && user.gender && user.height_cm && user.weight_kg && user.activity_level)
  const shownPlan = viewingPlan
    ? {
        meal_plan: viewingPlan.meal_plan,
        total_calories: viewingPlan.total_calories ?? 0,
        total_protein: viewingPlan.total_protein ?? 0,
        total_carbs: viewingPlan.total_carbs ?? 0,
        total_fat: viewingPlan.total_fat ?? 0,
        explanation: null,
      } as RecommendationResponse
    : plan

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-10 sm:px-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-clay">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
          <h1 className="mt-1 font-display text-3xl font-bold sm:text-4xl">
            Welcome, {user.name.split(' ')[0]}
          </h1>
        </div>
        <button
          onClick={generatePlan}
          disabled={!canGenerate || generating}
          className="cursor-pointer rounded-full bg-saffron px-6 py-3 font-semibold text-white shadow-md shadow-saffron/30 transition-all hover:bg-saffron-deep hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-40"
        >
          {generating ? 'Planning…' : 'Generate my plan'}
        </button>
      </header>

      {message && (
        <p className="rounded-xl border border-leaf/30 bg-leaf-soft px-4 py-2.5 text-sm text-leaf-deep">
          {message}
        </p>
      )}

      {canGenerate && <TargetsCard user={user} />}

      <ProfileCard user={user} updateField={updateField} />

      <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-2xl font-bold">Your meal plan</h2>
          {!canGenerate && (
            <p className="font-mono text-xs text-clay">
              Fill in age, gender, height, weight and activity to build one.
            </p>
          )}
        </div>

        {error && (
          <p className="mt-4 rounded-xl border border-chilli/30 bg-chilli-soft px-4 py-2.5 text-sm text-chilli">
            {error}
          </p>
        )}

        {shownPlan && (
          <div className="mt-6 animate-pop">
            {viewingPlan && (
              <p className="mb-4 text-sm text-clay">
                Viewing a saved plan from {formatDate(viewingPlan.created_at)}{' '}
                <button
                  onClick={() => { setViewingPlan(null); setPlan(null) }}
                  className="ml-1 cursor-pointer font-semibold text-saffron-deep hover:underline"
                >
                  Clear
                </button>
              </p>
            )}
            <MealPlanView plan={shownPlan} />
          </div>
        )}
      </section>

      <HistorySection
        plans={savedPlans}
        onOpen={openSavedPlan}
        onDelete={removeSavedPlan}
      />
    </div>
  )
}

function formatDate(iso: string | null) {
  if (!iso) return 'Unknown date'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? iso : d.toLocaleString()
}

function TargetsCard({ user }: { user: UserProfile }) {
  const bmr = user.gender?.toLowerCase() === 'male'
    ? 10 * (user.weight_kg ?? 0) + 6.25 * (user.height_cm ?? 0) - 5 * (user.age ?? 0) + 5
    : 10 * (user.weight_kg ?? 0) + 6.25 * (user.height_cm ?? 0) - 5 * (user.age ?? 0) - 161

  const mult: Record<string, number> = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, very_active: 1.9 }
  const tdee = bmr * (mult[user.activity_level ?? ''] || 1.2)
  const protein = (tdee * 0.2) / 4
  const carbs = (tdee * 0.55) / 4
  const fat = (tdee * 0.25) / 9

  const calories = protein * 4 + carbs * 4 + fat * 9
  const segments = [
    { percent: ((protein * 4) / calories) * 100, color: MACRO_COLORS.protein },
    { percent: ((carbs * 4) / calories) * 100, color: MACRO_COLORS.carbs },
    { percent: ((fat * 9) / calories) * 100, color: MACRO_COLORS.fat },
  ]

  return (
    <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
      <h2 className="font-display text-2xl font-bold">Today's targets</h2>
      <p className="mt-1 font-mono text-xs text-clay">
        What your body needs today, based on your profile
      </p>
      <div className="mt-6 flex flex-wrap items-center gap-10">
        <ThaliRing
          size={200}
          hole={0.46}
          centerLabel="Target"
          centerValue={`${Math.round(tdee)}`}
          centerUnit="kcal"
          segments={segments}
        />
        <div className="grid flex-1 grid-cols-2 gap-4 sm:grid-cols-3">
          <NutriStat label="Protein" value={`${Math.round(protein)}`} unit="g" color="text-leaf" dot={MACRO_COLORS.protein} />
          <NutriStat label="Carbs" value={`${Math.round(carbs)}`} unit="g" color="text-saffron-deep" dot={MACRO_COLORS.carbs} />
          <NutriStat label="Fat" value={`${Math.round(fat)}`} unit="g" color="text-chilli" dot={MACRO_COLORS.fat} />
        </div>
      </div>
    </section>
  )
}

function ProfileCard({
  user,
  updateField,
}: {
  user: UserProfile
  updateField: (field: string, value: string | number | null) => void
}) {
  const inputClass =
    'w-full rounded-xl border border-rim bg-paper px-3.5 py-2.5 text-sm text-ink focus:border-saffron'

  return (
    <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
      <h2 className="font-display text-2xl font-bold">Your profile</h2>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Field label="Age" value={user.age} onChange={v => updateField('age', v ? Number(v) : null)} />
        <div>
          <FieldLabel>Gender</FieldLabel>
          <select
            value={user.gender ?? ''}
            onChange={e => updateField('gender', e.target.value || null)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">Select…</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <Field label="Height (cm)" value={user.height_cm} onChange={v => updateField('height_cm', v ? Number(v) : null)} />
        <Field label="Weight (kg)" value={user.weight_kg} onChange={v => updateField('weight_kg', v ? Number(v) : null)} />
        <div>
          <FieldLabel>Activity level</FieldLabel>
          <select
            value={user.activity_level ?? ''}
            onChange={e => updateField('activity_level', e.target.value || null)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">Select…</option>
            <option value="sedentary">Sedentary</option>
            <option value="light">Light</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
            <option value="very_active">Very active</option>
          </select>
        </div>
        <div>
          <FieldLabel>Diet type</FieldLabel>
          <select
            value={user.diet_type ?? ''}
            onChange={e => updateField('diet_type', e.target.value || null)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">Select…</option>
            <option value="balanced">Balanced</option>
            <option value="low-carb">Low-carb</option>
            <option value="high-protein">High-protein</option>
          </select>
        </div>
        <div className="sm:col-span-2 lg:col-span-3">
          <FieldLabel>Medical conditions</FieldLabel>
          <input
            value={user.medical_conditions || ''}
            onChange={e => updateField('medical_conditions', e.target.value || null)}
            placeholder="e.g. diabetes, hypertension"
            className={inputClass}
          />
          <p className="mt-1.5 font-mono text-[11px] text-clay">
            Foods clashing with these are hard-filtered out of every plan.
          </p>
        </div>
      </div>
    </section>
  )
}

function Field({ label, value, onChange }: {
  label: string
  value: string | number | null
  onChange: (v: string) => void
}) {
  return (
    <div>
      <FieldLabel>{label}</FieldLabel>
      <input
        value={value ?? ''}
        onChange={e => onChange(e.target.value)}
        className="w-full rounded-xl border border-rim bg-paper px-3.5 py-2.5 text-sm text-ink focus:border-saffron"
      />
    </div>
  )
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="mb-1.5 block font-mono text-[11px] font-semibold uppercase tracking-widest text-clay">
      {children}
    </label>
  )
}

function NutriStat({ label, value, unit, color, dot }: {
  label: string
  value: string
  unit: string
  color: string
  dot: string
}) {
  return (
    <div className="rounded-2xl border border-rim bg-paper p-4">
      <div className="flex items-center gap-2">
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: dot }} />
        <p className="font-mono text-[11px] font-semibold uppercase tracking-widest text-clay">
          {label}
        </p>
      </div>
      <p className={`mt-2 font-display text-3xl font-bold ${color}`}>
        {value}
        <span className="ml-1 text-sm font-medium text-clay">{unit}</span>
      </p>
    </div>
  )
}

function MealPlanView({ plan }: { plan: RecommendationResponse }) {
  const proteinCal = plan.total_protein * 4
  const carbCal = plan.total_carbs * 4
  const fatCal = plan.total_fat * 9
  const cal = Math.max(plan.total_calories, proteinCal + carbCal + fatCal)

  const segments = [
    { percent: (proteinCal / cal) * 100, color: MACRO_COLORS.protein },
    { percent: (carbCal / cal) * 100, color: MACRO_COLORS.carbs },
    { percent: (fatCal / cal) * 100, color: MACRO_COLORS.fat },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-10">
        <ThaliRing
          size={160}
          hole={0.46}
          centerLabel="Plan"
          centerValue={`${Math.round(plan.total_calories)}`}
          centerUnit="kcal"
          segments={segments}
        />
        <ul className="space-y-2">
          <LegendRow dot={MACRO_COLORS.protein} label="Protein" value={`${plan.total_protein.toFixed(1)} g`} />
          <LegendRow dot={MACRO_COLORS.carbs} label="Carbs" value={`${plan.total_carbs.toFixed(1)} g`} />
          <LegendRow dot={MACRO_COLORS.fat} label="Fat" value={`${plan.total_fat.toFixed(1)} g`} />
        </ul>
      </div>

      {plan.meal_plan.map(slot => (
        <MealSlotCard key={slot.meal} slot={slot} />
      ))}

      {plan.explanation && (
        <div className="rounded-2xl border border-rim bg-paper p-5">
          <p className="font-mono text-[11px] font-semibold uppercase tracking-widest text-clay">
            Why these foods?
          </p>
          <ul className="mt-3 space-y-1.5">
            {plan.explanation.split('|').map((line, i) => (
              <li key={i} className="flex gap-2 text-sm text-ink">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-saffron" />
                {line.trim()}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function LegendRow({ dot, label, value }: { dot: string; label: string; value: string }) {
  return (
    <li className="flex items-center gap-2.5 text-sm">
      <span className="h-3 w-3 rounded-full" style={{ background: dot }} />
      <span className="text-clay">{label}</span>
      <span className="font-mono font-semibold text-ink">{value}</span>
    </li>
  )
}

function MealSlotCard({ slot }: { slot: MealPlan }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-rim">
      <div className="flex items-center justify-between bg-paper px-5 py-3">
        <h3 className="font-display text-base font-bold text-saffron-deep">
          {slot.meal}
        </h3>
        <span className="font-mono text-xs text-clay">
          {slot.items.reduce((s, i) => s + i.calories, 0).toFixed(0)} kcal
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left font-mono text-[11px] uppercase tracking-wider text-clay">
            <tr>
              <th className="px-5 py-2.5 font-semibold">Food</th>
              <th className="px-5 py-2.5 text-right font-semibold">Cal</th>
              <th className="px-5 py-2.5 text-right font-semibold">Protein</th>
              <th className="px-5 py-2.5 text-right font-semibold">Carbs</th>
              <th className="px-5 py-2.5 text-right font-semibold">Fat</th>
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
    <tr className="border-t border-rim transition-colors hover:bg-paper">
      <td className="px-5 py-3">
        <p className="font-medium">{item.food_name}</p>
        <p className="font-mono text-xs text-clay">{item.serving_size}</p>
      </td>
      <td className="px-5 py-3 text-right font-mono">{Math.round(item.calories)}</td>
      <td className="px-5 py-3 text-right font-mono">{item.protein_g.toFixed(1)}</td>
      <td className="px-5 py-3 text-right font-mono">{item.carbs_g.toFixed(1)}</td>
      <td className="px-5 py-3 text-right font-mono">{item.fat_g.toFixed(1)}</td>
    </tr>
  )
}

function HistorySection({
  plans,
  onOpen,
  onDelete,
}: {
  plans: PlanSummary[]
  onOpen: (id: number) => void
  onDelete: (id: number) => void
}) {
  return (
    <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
      <h2 className="font-display text-2xl font-bold">Plan history</h2>
      {plans.length === 0 ? (
        <p className="mt-3 font-mono text-sm text-clay">
          No saved plans yet — build one and it lands here.
        </p>
      ) : (
        <ul className="mt-4 divide-y divide-rim">
          {plans.map(p => (
            <li key={p.id} className="flex flex-wrap items-center justify-between gap-3 py-3.5">
              <div className="flex items-center gap-4">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-saffron-soft font-display text-sm font-bold text-saffron-deep">
                  {p.item_count}
                </span>
                <div>
                  <p className="font-semibold">{formatDate(p.created_at)}</p>
                  <p className="font-mono text-xs text-clay">
                    {p.total_calories ?? 0} kcal · P {p.total_protein ?? 0} · C {p.total_carbs ?? 0} · F {p.total_fat ?? 0}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => onOpen(p.id)}
                  className="cursor-pointer rounded-full bg-saffron px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-saffron-deep"
                >
                  View
                </button>
                <button
                  onClick={() => onDelete(p.id)}
                  className="cursor-pointer rounded-full border border-chilli/30 px-4 py-1.5 text-sm font-medium text-chilli transition-colors hover:bg-chilli-soft"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
