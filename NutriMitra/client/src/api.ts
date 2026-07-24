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

export function getRecommendations(token: string, profile: Record<string, unknown>) {
  return request('POST', '/recommendations/', profile, token)
}
