const BASE = '/v1'

async function request(method: string, path: string, body?: unknown, token?: string) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export function register(data: { email: string; password: string; name: string }) {
  return request('POST', '/auth/register', data)
}

export function login(data: { email: string; password: string }) {
  return request('POST', '/auth/login', data)
}

export function getMe(token: string) {
  return request('GET', '/users/me', undefined, token)
}

export interface UserProfile {
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

export interface MealItem {
  food_name: string
  serving_size: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface MealPlan {
  meal: string
  items: MealItem[]
}

export interface RecommendationResponse {
  meal_plan: MealPlan[]
  total_calories: number
  total_protein: number
  total_carbs: number
  total_fat: number
  explanation: string | null
}

export function getRecommendations(token: string, profile: Record<string, unknown>) {
  return request('POST', '/recommendations/', profile, token) as Promise<RecommendationResponse>
}
