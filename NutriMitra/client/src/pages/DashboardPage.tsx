import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getMe,
  getRecommendations,
  getPlans,
  getPlan,
  deletePlan,
  updateProfile,
} from '../api'
import type {
  UserProfile,
  RecommendationResponse,
  MealPlan,
  MealItem,
  PlanSummary,
  SavedPlan,
  ProfileUpdate,
} from '../api'
import {
  ACTIVITY_LEVELS,
  DIET_TYPES,
  GENDERS,
  estimateTargets,
  validateProfile,
} from '../nutrition'
import ThaliRing from '../components/ThaliRing'

const MACRO_COLORS = {
  protein: 'var(--color-leaf)',
  carbs: 'var(--color-saffron)',
  fat: 'var(--color-chilli)',
}

const MEAL_LABELS: Record<string, string> = {
  Breakfast: 'Breakfast',
  Lunch: 'Lunch',
  Dinner: 'Dinner',
  Snacks: 'Healthy snacks',
}

export default function DashboardPage() {
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [warning, setWarning] = useState('')
  const [plan, setPlan] = useState<RecommendationResponse | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [validation, setValidation] = useState('')
  const [savedPlans, setSavedPlans] = useState<PlanSummary[]>([])
  const [viewingPlan, setViewingPlan] = useState<SavedPlan | null>(null)
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const loadHistory = useCallback(
    (t: string) => {
      getPlans(t)
        .then(setSavedPlans)
        .catch(() => {})
    },
    [],
  )

  useEffect(() => {
    if (!token) {
      nav('/')
      return
    }
    getMe(token)
      .then(u => {
        setUser(u)
        loadHistory(token)
      })
      .catch(() => {
        localStorage.clear()
        nav('/')
      })
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(
    () => () => {
      if (saveTimer.current) clearTimeout(saveTimer.current)
    },
    [],
  )

  if (loading) return <p className="py-24 text-center text-clay">Loading your plan…</p>
  if (!user) return null

  const profilePayload = (): ProfileUpdate => ({
    age: user.age,
    gender: user.gender,
    height_cm: user.height_cm,
    weight_kg: user.weight_kg,
    activity_level: user.activity_level,
    diet_type: user.diet_type,
    medical_conditions: user.medical_conditions,
    allergies: user.allergies,
  })

  /** Save the profile. Returns false when the server rejected the update. */
  const persistProfile = async (draft: ProfileUpdate): Promise<boolean> => {
    if (!token) return false
    try {
      const updated = await updateProfile(token, draft)
      setUser(prev => (prev ? { ...prev, ...updated } : prev))
      return true
    } catch {
      return false
    }
  }

  const updateField = (field: string, value: string | number | null) => {
    setUser(prev => (prev ? { ...prev, [field]: value } : prev))
    setPlan(null)
    setValidation('')
    setMessage('Profile updated — generate a new plan to refresh your targets')
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      void persistProfile({ [field]: value } as ProfileUpdate)
    }, 600)
  }

  const generatePlan = async () => {
    if (!token || !user) return
    if (generating) return // never send a second request while one is running

    const check = validateProfile(user)
    if (!check.ok) {
      setValidation(check.message)
      setError('')
      return
    }
    setValidation('')
    setError('')
    setWarning('')
    setGenerating(true)

    try {
      if (saveTimer.current) {
        clearTimeout(saveTimer.current)
        saveTimer.current = null
      }
      const saved = await persistProfile(profilePayload())
      if (!saved) {
        setWarning(
          'Your profile could not be saved to the server, so the plan below was built from what is on screen.',
        )
      }

      const data = await getRecommendations(token, profilePayload() as Record<string, unknown>)
      setPlan(data)
      setViewingPlan(null)
      loadHistory(token)
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not generate a meal plan. Please try again.',
      )
    } finally {
      // The button becomes available again so the user can retry.
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
      setValidation('')
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

  const shownPlan: RecommendationResponse | null = viewingPlan
    ? {
        meal_plan: viewingPlan.meal_plan,
        total_calories: viewingPlan.total_calories ?? 0,
        total_protein: viewingPlan.total_protein ?? 0,
        total_carbs: viewingPlan.total_carbs ?? 0,
        total_fat: viewingPlan.total_fat ?? 0,
        target_calories: estimateTargets(user).calories,
        target_protein_g: estimateTargets(user).protein_g,
        target_carbs_g: estimateTargets(user).carbs_g,
        target_fat_g: estimateTargets(user).fat_g,
        explanation: null,
      }
    : plan

  const profileCheck = validateProfile(user)

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-10 sm:px-6 relative pb-24">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-clay">
            {new Date().toLocaleDateString(undefined, {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
            })}
          </p>
          <h1 className="mt-1 font-display text-3xl font-bold sm:text-4xl">
            Welcome, {user.name.split(' ')[0]}
          </h1>
        </div>
      </header>

      {message && (
        <p className="rounded-xl border border-leaf/30 bg-leaf-soft px-4 py-2.5 text-sm text-leaf-deep">
          {message}
        </p>
      )}

      <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
        <TargetsCard user={user} />
      </section>

      <ProfileCard user={user} updateField={updateField} />

      {/* The button is always visible - a missing profile is reported with a
          validation message instead of hiding the action. */}
      <div className="flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={generatePlan}
          disabled={generating}
          aria-busy={generating}
          className="w-full cursor-pointer rounded-full bg-saffron px-6 py-3 font-semibold text-white shadow-lg shadow-saffron/30 transition-all hover:bg-saffron-deep hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
        >
          {generating ? 'Planning…' : 'Generate My Meal Plan'}
        </button>
        {generating && (
          <p className="font-mono text-xs text-clay">
            Building your plan from the nutrition dataset…
          </p>
        )}
        {validation && (
          <p
            role="alert"
            className="w-full rounded-xl border border-chilli/30 bg-chilli-soft px-4 py-2.5 text-sm text-chilli"
          >
            {validation}
          </p>
        )}
        {warning && (
          <p
            role="status"
            className="w-full rounded-xl border border-saffron/40 bg-saffron-soft px-4 py-2.5 text-sm text-saffron-deep"
          >
            {warning}
          </p>
        )}
      </div>

      <section className="rounded-3xl border border-rim bg-cream p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-2xl font-bold">Your meal plan</h2>
          {!profileCheck.ok && (
            <p className="font-mono text-xs text-clay">
              Fill in age, gender, height, weight, activity and diet to build one.
            </p>
          )}
        </div>

        {error && (
          <p
            role="alert"
            className="mt-4 rounded-xl border border-chilli/30 bg-chilli-soft px-4 py-2.5 text-sm text-chilli"
          >
            {error}
          </p>
        )}

        {shownPlan ? (
          <div className="mt-6 animate-pop">
            {viewingPlan && (
              <p className="mb-4 text-sm text-clay">
                Viewing a saved plan from {formatDate(viewingPlan.created_at)}{' '}
                <button
                  type="button"
                  onClick={() => {
                    setViewingPlan(null)
                    setPlan(null)
                  }}
                  className="ml-1 cursor-pointer font-semibold text-saffron-deep hover:underline"
                >
                  Clear
                </button>
              </p>
            )}
            <MealPlanView plan={shownPlan} />
          </div>
        ) : (
          !error &&
          !generating && (
            <p className="mt-4 font-mono text-sm text-clay">
              No plan yet — press{' '}
              <span className="font-semibold text-saffron-deep">Generate My Meal Plan</span>{' '}
              and your personalised day appears here.
            </p>
          )
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
  const targets = estimateTargets(user)
  const proteinCal = targets.protein_g * 4
  const carbCal = targets.carbs_g * 4
  const fatCal = targets.fat_g * 9
  const calories = proteinCal + carbCal + fatCal

  const segments = [
    { percent: calories > 0 ? (proteinCal / calories) * 100 : 0, color: MACRO_COLORS.protein },
    { percent: calories > 0 ? (carbCal / calories) * 100 : 0, color: MACRO_COLORS.carbs },
    { percent: calories > 0 ? (fatCal / calories) * 100 : 0, color: MACRO_COLORS.fat },
  ]

  return (
    <section>
      <h2 className="font-display text-2xl font-bold">Today's targets</h2>
      <p className="mt-1 font-mono text-xs text-clay">
        What your body needs today, based on your profile
      </p>
      <div className="mt-6 flex flex-wrap items-center gap-10">
        <ThaliRing
          size={200}
          hole={0.46}
          centerLabel="Target"
          centerValue={`${Math.round(targets.calories)}`}
          centerUnit="kcal"
          segments={segments}
        />
        <div className="grid flex-1 grid-cols-2 gap-4 sm:grid-cols-3">
          <NutriStat
            label="Protein"
            value={`${Math.round(targets.protein_g)}`}
            unit="g"
            color="text-leaf"
            dot={MACRO_COLORS.protein}
          />
          <NutriStat
            label="Carbs"
            value={`${Math.round(targets.carbs_g)}`}
            unit="g"
            color="text-saffron-deep"
            dot={MACRO_COLORS.carbs}
          />
          <NutriStat
            label="Fat"
            value={`${Math.round(targets.fat_g)}`}
            unit="g"
            color="text-chilli"
            dot={MACRO_COLORS.fat}
          />
        </div>
      </div>
      <p className="mt-4 font-mono text-[11px] text-clay">
        Estimated with the Mifflin-St Jeor equation and your activity level. It is a
        guide, not a medical requirement.
      </p>
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
        <Field
          label="Age"
          value={user.age}
          onChange={v => updateField('age', v ? Number(v) : null)}
        />
        <div>
          <FieldLabel>Gender</FieldLabel>
          <select
            value={user.gender ?? ''}
            onChange={e => updateField('gender', e.target.value || null)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">Select…</option>
            {GENDERS.map(g => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
        </div>
        <Field
          label="Height (cm)"
          value={user.height_cm}
          onChange={v => updateField('height_cm', v ? Number(v) : null)}
        />
        <Field
          label="Weight (kg)"
          value={user.weight_kg}
          onChange={v => updateField('weight_kg', v ? Number(v) : null)}
        />
        <div>
          <FieldLabel>Activity level</FieldLabel>
          <select
            value={user.activity_level ?? ''}
            onChange={e => updateField('activity_level', e.target.value || null)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">Select…</option>
            {ACTIVITY_LEVELS.map(level => (
              <option key={level.value} value={level.value}>
                {level.label}
              </option>
            ))}
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
            {DIET_TYPES.map(diet => (
              <option key={diet.value} value={diet.value}>
                {diet.label}
              </option>
            ))}
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
            Foods clashing with these are hard-filtered out of every plan. General
            guidance only — always follow your own doctor's advice.
          </p>
        </div>
        <div className="sm:col-span-2 lg:col-span-3">
          <FieldLabel>Allergies / foods to avoid</FieldLabel>
          <input
            value={user.allergies || ''}
            onChange={e => updateField('allergies', e.target.value || null)}
            placeholder="e.g. peanut, milk, egg"
            className={inputClass}
          />
          <p className="mt-1.5 font-mono text-[11px] text-clay">
            Matching dishes are removed from your plan. The dataset has no full
            ingredient list, so always double-check a dish before eating it.
          </p>
        </div>
      </div>
    </section>
  )
}

function Field({
  label,
  value,
  onChange,
}: {
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

function NutriStat({
  label,
  value,
  unit,
  color,
  dot,
}: {
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

/** Describes how the generated meals relate to the estimated target. */
function coverageNote(actual: number, target: number) {
  if (!target || target <= 0) return ''
  const percent = Math.round((actual / target) * 100)
  if (actual === 0) return 'No calories were calculated for this plan.'
  if (percent >= 90 && percent <= 110) {
    return `The generated meals provide ${Math.round(actual)} kcal — right around your estimated target of ${Math.round(target)} kcal.`
  }
  if (percent < 90) {
    return `The generated meals provide ${Math.round(actual)} kcal — about ${percent}% of your estimated target of ${Math.round(target)} kcal. Add a little more to close the gap.`
  }
  return `The generated meals provide ${Math.round(actual)} kcal — about ${percent}% of your estimated target of ${Math.round(target)} kcal. Trim a portion or a snack to come closer.`
}

function MealPlanView({ plan }: { plan: RecommendationResponse }) {
  const proteinCal = plan.total_protein * 4
  const carbCal = plan.total_carbs * 4
  const fatCal = plan.total_fat * 9
  const cal = Math.max(plan.total_calories, proteinCal + carbCal + fatCal)

  const segments = [
    { percent: cal > 0 ? (proteinCal / cal) * 100 : 0, color: MACRO_COLORS.protein },
    { percent: cal > 0 ? (carbCal / cal) * 100 : 0, color: MACRO_COLORS.carbs },
    { percent: cal > 0 ? (fatCal / cal) * 100 : 0, color: MACRO_COLORS.fat },
  ]

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-rim bg-paper p-5">
        <p className="font-mono text-[11px] font-semibold uppercase tracking-widest text-clay">
          Daily nutrition summary
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-10">
          <ThaliRing
            size={160}
            hole={0.46}
            centerLabel="Meals"
            centerValue={`${Math.round(plan.total_calories)}`}
            centerUnit="kcal"
            segments={segments}
          />
          <div className="grid flex-1 grid-cols-2 gap-4 sm:grid-cols-3">
            <NutriStat
              label="Daily target"
              value={`${Math.round(plan.target_calories)}`}
              unit="kcal"
              color="text-ink"
              dot="var(--color-clay)"
            />
            <NutriStat
              label="Meals give"
              value={`${Math.round(plan.total_calories)}`}
              unit="kcal"
              color="text-saffron-deep"
              dot="var(--color-saffron)"
            />
            <NutriStat
              label="Protein"
              value={`${plan.total_protein.toFixed(1)}`}
              unit="g"
              color="text-leaf"
              dot={MACRO_COLORS.protein}
            />
            <NutriStat
              label="Carbs"
              value={`${plan.total_carbs.toFixed(1)}`}
              unit="g"
              color="text-saffron-deep"
              dot={MACRO_COLORS.carbs}
            />
            <NutriStat
              label="Fat"
              value={`${plan.total_fat.toFixed(1)}`}
              unit="g"
              color="text-chilli"
              dot={MACRO_COLORS.fat}
            />
          </div>
        </div>
        <p className="mt-4 font-mono text-[11px] text-clay">
          {coverageNote(plan.total_calories, plan.target_calories)}
        </p>
        {plan.target_calories > 0 && (
          <p className="mt-1 font-mono text-[11px] text-clay">
            Target macros: {plan.target_protein_g} g protein · {plan.target_carbs_g} g
            carbs · {plan.target_fat_g} g fat.
          </p>
        )}
      </div>

      {plan.meal_plan.map(slot => (
        <MealSlotCard key={slot.meal} slot={slot} />
      ))}

      <div className="rounded-2xl border border-rim bg-paper p-5">
        <p className="font-mono text-[11px] font-semibold uppercase tracking-widest text-clay">
          Daily totals from the foods above
        </p>
        <div className="mt-3 flex flex-wrap gap-x-8 gap-y-2 font-mono text-sm text-ink">
          <span>
            <span className="text-clay">Calories</span> {plan.total_calories.toFixed(1)} kcal
          </span>
          <span>
            <span className="text-clay">Protein</span> {plan.total_protein.toFixed(1)} g
          </span>
          <span>
            <span className="text-clay">Carbs</span> {plan.total_carbs.toFixed(1)} g
          </span>
          <span>
            <span className="text-clay">Fat</span> {plan.total_fat.toFixed(1)} g
          </span>
        </div>
      </div>

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

function MealSlotCard({ slot }: { slot: MealPlan }) {
  const totals = slot.totals ?? {
    calories: slot.items.reduce((s, i) => s + i.calories, 0),
    protein_g: slot.items.reduce((s, i) => s + i.protein_g, 0),
    carbs_g: slot.items.reduce((s, i) => s + i.carbs_g, 0),
    fat_g: slot.items.reduce((s, i) => s + i.fat_g, 0),
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-rim">
      <div className="flex items-center justify-between bg-paper px-5 py-3">
        <h3 className="font-display text-base font-bold text-saffron-deep">
          {MEAL_LABELS[slot.meal] ?? slot.meal}
        </h3>
        <span className="font-mono text-xs text-clay">
          {totals.calories.toFixed(0)} kcal · P {totals.protein_g.toFixed(1)} g · C{' '}
          {totals.carbs_g.toFixed(1)} g · F {totals.fat_g.toFixed(1)} g
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
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
              <FoodRow key={`${item.food_name}-${i}`} item={item} />
            ))}
            <tr className="border-t-2 border-rim bg-paper font-mono text-xs">
              <td className="px-5 py-2.5 font-semibold uppercase tracking-wider text-clay">
                Meal total
              </td>
              <td className="px-5 py-2.5 text-right font-semibold">
                {totals.calories.toFixed(0)}
              </td>
              <td className="px-5 py-2.5 text-right font-semibold">
                {totals.protein_g.toFixed(1)}
              </td>
              <td className="px-5 py-2.5 text-right font-semibold">
                {totals.carbs_g.toFixed(1)}
              </td>
              <td className="px-5 py-2.5 text-right font-semibold">
                {totals.fat_g.toFixed(1)}
              </td>
            </tr>
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
            <li
              key={p.id}
              className="flex flex-wrap items-center justify-between gap-3 py-3.5"
            >
              <div className="flex items-center gap-4">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-saffron-soft font-display text-sm font-bold text-saffron-deep">
                  {p.item_count}
                </span>
                <div>
                  <p className="font-semibold">{formatDate(p.created_at)}</p>
                  <p className="font-mono text-xs text-clay">
                    {p.total_calories ?? 0} kcal · P {p.total_protein ?? 0} · C{' '}
                    {p.total_carbs ?? 0} · F {p.total_fat ?? 0}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => onOpen(p.id)}
                  className="cursor-pointer rounded-full bg-saffron px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-saffron-deep"
                >
                  View
                </button>
                <button
                  type="button"
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
