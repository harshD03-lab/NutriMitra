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

export interface FoodItem {
  id: number
  name: string
  category: string | null
  energy_kcal: number | null
  protein_g: number | null
  carbs_g: number | null
  fat_g: number | null
  fiber_g: number | null
  calcium_mg: number | null
  iron_mg: number | null
  vitamin_c_mg: number | null
  vitamin_a_mcg: number | null
  folate_mcg: number | null
  zinc_mg: number | null
  serving_size_g: number | null
  suitable_for: string | null
}

export interface FoodListResponse {
  total: number
  skip: number
  limit: number
  items: FoodItem[]
}

export function getFoods(token: string, params: Record<string, string | number>) {
  const query = new URLSearchParams(params as Record<string, string>).toString()
  return request('GET', `/food/?${query}`, undefined, token) as Promise<FoodListResponse>
}

export function getFoodCategories(token: string) {
  return request('GET', '/food/categories', undefined, token) as Promise<string[]>
}

export interface PlanSummary {
  id: number
  total_calories: number | null
  total_protein: number | null
  total_carbs: number | null
  total_fat: number | null
  item_count: number
  created_at: string | null
}

export interface SavedPlan {
  id: number
  meal_plan: MealPlan[]
  total_calories: number | null
  total_protein: number | null
  total_carbs: number | null
  total_fat: number | null
  created_at: string | null
}

export function getPlans(token: string) {
  return request('GET', '/plans/', undefined, token) as Promise<PlanSummary[]>
}

export function getPlan(token: string, planId: number) {
  return request('GET', `/plans/${planId}`, undefined, token) as Promise<SavedPlan>
}

export function deletePlan(token: string, planId: number) {
  return request('DELETE', `/plans/${planId}`, undefined, token)
}
