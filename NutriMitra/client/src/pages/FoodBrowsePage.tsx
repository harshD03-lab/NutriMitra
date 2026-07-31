import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getFoods, getFoodCategories } from '../api'
import type { FoodItem } from '../api'

const PAGE_SIZE = 20

export default function FoodBrowsePage() {
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [search, setSearch] = useState('')
  const [debounced, setDebounced] = useState('')
  const [category, setCategory] = useState('')
  const [categories, setCategories] = useState<string[]>([])
  const [items, setItems] = useState<FoodItem[]>([])
  const [total, setTotal] = useState(0)
  const [skip, setSkip] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { nav('/'); return }
    const t = setTimeout(() => setDebounced(search), 300)
    return () => clearTimeout(t)
  }, [search])

  useEffect(() => {
    if (!token) return
    getFoodCategories(token)
      .then(setCategories)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!token) return
    setLoading(true)
    setError('')
    const params: Record<string, string | number> = { skip, limit: PAGE_SIZE }
    if (debounced) params.q = debounced
    if (category) params.category = category
    getFoods(token, params)
      .then(res => { setItems(res.items); setTotal(res.total) })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : 'Failed to load foods'))
      .finally(() => setLoading(false))
  }, [debounced, category, skip])

  if (!token) return null

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const currentPage = Math.floor(skip / PAGE_SIZE) + 1

  const goToPage = (page: number) => {
    setSkip((page - 1) * PAGE_SIZE)
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Food Database</h1>
        <p className="text-sm text-gray-500 mt-1">{total.toLocaleString()} foods available</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <input
          value={search}
          onChange={e => { setSearch(e.target.value); setSkip(0) }}
          placeholder="Search foods... e.g. dal, paneer, roti"
          className="flex-1 border rounded-lg px-3 py-2 text-sm"
        />
        <select
          value={category}
          onChange={e => { setCategory(e.target.value); setSkip(0) }}
          className="border rounded-lg px-3 py-2 text-sm bg-white"
        >
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {loading ? (
        <p className="text-center py-10 text-gray-500">Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-center py-10 text-gray-500">No foods match your search.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              <tr>
                <th className="px-3 py-2 font-medium">Food</th>
                <th className="px-3 py-2 font-medium text-right">Cal</th>
                <th className="px-3 py-2 font-medium text-right">Protein</th>
                <th className="px-3 py-2 font-medium text-right">Carbs</th>
                <th className="px-3 py-2 font-medium text-right">Fat</th>
                <th className="px-3 py-2 font-medium text-right">Fiber</th>
                <th className="px-3 py-2 font-medium text-right">Iron (mg)</th>
                <th className="px-3 py-2 font-medium text-right">Calcium (mg)</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id} className="border-t hover:bg-gray-50">
                  <td className="px-3 py-2">
                    <p className="font-medium">{item.name}</p>
                    {item.category && <p className="text-xs text-gray-500">{item.category}</p>}
                  </td>
                  <td className="px-3 py-2 text-right">{fmt(item.energy_kcal)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.protein_g)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.carbs_g)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.fat_g)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.fiber_g)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.iron_mg)}</td>
                  <td className="px-3 py-2 text-right">{fmt(item.calcium_mg)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > 0 && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">
            Page {currentPage} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
              className="px-3 py-1.5 rounded-lg border text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Previous
            </button>
            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 rounded-lg border text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function fmt(v: number | null): string {
  return v == null || v === 0 ? '—' : v >= 10 ? Math.round(v).toString() : v.toFixed(1)
}
