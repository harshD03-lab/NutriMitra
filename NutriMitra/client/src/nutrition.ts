/**
 * Profile validation and energy estimation for the dashboard.
 *
 * The formulas mirror the server side implementation
 * (`app/ml/nutrient_engine.py`) so the numbers shown before a plan is
 * generated match the plan that comes back from the API.
 */

export interface ProfileDraft {
  age: number | null
  gender: string | null
  height_cm: number | null
  weight_kg: number | null
  activity_level: string | null
  diet_type: string | null
  medical_conditions: string | null
  allergies: string | null
}

export interface ProfileValidation {
  ok: boolean
  missing: string[]
  message: string
}

/** Fields that must be filled in before a plan can be generated. */
export const REQUIRED_FIELDS: { key: keyof ProfileDraft; label: string }[] = [
  { key: 'age', label: 'age' },
  { key: 'gender', label: 'gender' },
  { key: 'height_cm', label: 'height' },
  { key: 'weight_kg', label: 'weight' },
  { key: 'activity_level', label: 'activity level' },
  { key: 'diet_type', label: 'diet type' },
]

export const ACTIVITY_LEVELS: { value: string; label: string }[] = [
  { value: 'sedentary', label: 'Sedentary' },
  { value: 'light', label: 'Light' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'active', label: 'Active' },
  { value: 'very_active', label: 'Very active' },
]

export const DIET_TYPES: { value: string; label: string }[] = [
  { value: 'balanced', label: 'Balanced' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'non-vegetarian', label: 'Non-vegetarian' },
  { value: 'low-carb', label: 'Low-carb' },
  { value: 'high-protein', label: 'High-protein' },
]

export const GENDERS: { value: string; label: string }[] = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
]

const ACTIVITY_FACTORS: Record<string, number> = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  very_active: 1.9,
}

const MACRO_SPLITS: Record<string, { protein: number; fat: number; carbs: number }> = {
  'low-carb': { protein: 0.3, fat: 0.4, carbs: 0.3 },
  'high-protein': { protein: 0.35, fat: 0.25, carbs: 0.4 },
}

export interface EstimatedTargets {
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

/**
 * Estimate the daily energy requirement with the Mifflin-St Jeor equation
 * plus a physical activity factor.  The result is an estimate, never a
 * guaranteed requirement.
 */
export function estimateTargets(profile: ProfileDraft): EstimatedTargets {
  const weight = profile.weight_kg ?? 0
  const height = profile.height_cm ?? 0
  const age = profile.age ?? 0
  const bmr =
    profile.gender?.toLowerCase() === 'male'
      ? 10 * weight + 6.25 * height - 5 * age + 5
      : 10 * weight + 6.25 * height - 5 * age - 161
  const tdee = bmr * (ACTIVITY_FACTORS[profile.activity_level ?? ''] ?? 1.2)
  const split = MACRO_SPLITS[profile.diet_type ?? ''] ?? {
    protein: 0.2,
    fat: 0.25,
    carbs: 0.55,
  }
  return {
    calories: Math.round(tdee),
    protein_g: Math.round((tdee * split.protein) / 4),
    carbs_g: Math.round((tdee * split.carbs) / 4),
    fat_g: Math.round((tdee * split.fat) / 9),
  }
}

/** Check that everything needed to build a plan is present. */
export function validateProfile(profile: ProfileDraft): ProfileValidation {
  const missing: string[] = []

  for (const field of REQUIRED_FIELDS) {
    const value = profile[field.key]
    if (value === null || value === undefined || value === '') {
      missing.push(field.label)
      continue
    }
    if (typeof value === 'number' && (!Number.isFinite(value) || value <= 0)) {
      missing.push(field.label)
    }
  }

  if (missing.length === 0) {
    return { ok: true, missing: [], message: '' }
  }

  return {
    ok: false,
    missing,
    message: `Please fill in your ${missing.join(', ')} before generating a meal plan.`,
  }
}
