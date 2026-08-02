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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search])

  useEffect(() => {
    if (!token) return
    getFoodCategories(token)
      .then(setCategories)
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced, category, skip])

  if (!token) return null

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const currentPage = Math.floor(skip / PAGE_SIZE) + 1

  const goToPage = (page: number) => {
    setSkip((page - 1) * PAGE_SIZE)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const pickCategory = (c: string) => {
    setCategory(c === category ? '' : c)
    setSkip(0)
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-10 sm:px-6">
      <div>
        <h1 className="font-display text-3xl font-bold sm:text-4xl">Food database</h1>
        <p className="mt-1 font-mono text-sm text-clay">
          {total.toLocaleString()} Indian foods · ICMR-NIN composition
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="relative">
          <svg
            aria-hidden
            className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-clay"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setSkip(0) }}
            placeholder="Search foods… e.g. dal, paneer, roti"
            className="w-full rounded-2xl border border-rim bg-cream py-3 pl-11 pr-4 text-sm text-ink placeholder:text-clay/60 focus:border-saffron"
          />
        </div>

        {categories.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <CategoryChip active={category === ''} onClick={() => pickCategory('')}>
              All
            </CategoryChip>
            {categories.map(c => (
              <CategoryChip key={c} active={category === c} onClick={() => pickCategory(c)}>
                {c}
              </CategoryChip>
            ))}
          </div>
        )}
      </div>

      {error && (
        <p className="rounded-xl border border-chilli/30 bg-chilli-soft px-4 py-2.5 text-sm text-chilli">
          {error}
        </p>
      )}

      {loading ? (
        <p className="py-20 text-center text-clay">Loading the pantry…</p>
      ) : items.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-rim bg-cream py-20 text-center">
          <p className="font-display text-xl font-semibold">No foods match</p>
          <p className="mt-1 font-mono text-sm text-clay">
            Try another dish or clear the category filter.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-3xl border border-rim bg-cream">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-paper text-left font-mono text-[11px] uppercase tracking-wider text-clay">
                <tr>
                  <th className="px-5 py-3 font-semibold">Food</th>
                  <th className="px-5 py-3 text-right font-semibold">Cal</th>
                  <th className="px-5 py-3 text-right font-semibold">Protein</th>
                  <th className="px-5 py-3 text-right font-semibold">Carbs</th>
                  <th className="px-5 py-3 text-right font-semibold">Fat</th>
                  <th className="px-5 py-3 text-right font-semibold">Fiber</th>
                  <th className="px-5 py-3 text-right font-semibold">Iron</th>
                  <th className="px-5 py-3 text-right font-semibold">Calcium</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id} className="border-t border-rim transition-colors hover:bg-paper">
                    <td className="px-5 py-3">
                      <p className="font-medium">{item.name}</p>
                      {item.category && (
                        <span className="mt-0.5 inline-block rounded-full bg-leaf-soft px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-leaf-deep">
                          {item.category}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.energy_kcal)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.protein_g)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.carbs_g)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.fat_g)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.fiber_g)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.iron_mg)}</td>
                    <td className="px-5 py-3 text-right font-mono">{fmt(item.calcium_mg)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {total > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3 font-mono text-sm">
          <span className="text-clay">
            Page {currentPage} of {totalPages} · {total.toLocaleString()} foods
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
              className="cursor-pointer rounded-full border border-rim bg-cream px-4 py-2 text-sm font-semibold transition-colors hover:border-saffron hover:text-saffron-deep disabled:cursor-not-allowed disabled:opacity-40"
            >
              ← Prev
            </button>
            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="cursor-pointer rounded-full border border-rim bg-cream px-4 py-2 text-sm font-semibold transition-colors hover:border-saffron hover:text-saffron-deep disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function CategoryChip({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className={`cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors ${
        active
          ? 'bg-leaf text-white shadow-sm'
          : 'border border-rim bg-cream text-clay hover:border-leaf hover:text-leaf-deep'
      }`}
    >
      {children}
    </button>
  )
}

function fmt(v: number | null): string {
  return v == null || v === 0 ? '—' : v >= 10 ? Math.round(v).toString() : v.toFixed(1)
}
