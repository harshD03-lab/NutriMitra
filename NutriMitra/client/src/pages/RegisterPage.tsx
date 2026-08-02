import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register, login } from '../api'
import ThaliRing from '../components/ThaliRing'

const HERO_CHIPS = [
  { label: 'Dal', top: '6%', left: '2%', delay: '0s' },
  { label: 'Roti', top: '18%', left: '78%', delay: '0.8s' },
  { label: 'Paneer', top: '66%', left: '4%', delay: '1.4s' },
  { label: 'Idli', top: '74%', left: '74%', delay: '2s' },
  { label: 'Chai', top: '40%', left: '92%', delay: '0.4s' },
]

export default function RegisterPage() {
  const nav = useNavigate()
  const [tab, setTab] = useState<'login' | 'register'>('register')
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      if (tab === 'register') {
        await register(form)
        await loginFn()
      } else {
        await loginFn()
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  const loginFn = async () => {
    const data = await login({ email: form.email, password: form.password })
    localStorage.setItem('token', data.access_token)
    nav('/dashboard')
  }

  const token = localStorage.getItem('token')
  if (token) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-24 text-center">
        <p className="font-display text-2xl font-semibold">
          You're logged in, {form.name || 'friend'}.
        </p>
        <a
          href="/dashboard"
          className="mt-4 inline-block rounded-full bg-saffron px-6 py-2.5 font-semibold text-white shadow-sm transition-colors hover:bg-saffron-deep"
        >
          Go to Dashboard
        </a>
      </div>
    )
  }

  const inputClass =
    'w-full rounded-xl border border-rim bg-cream px-3.5 py-2.5 text-sm text-ink placeholder:text-clay/60 transition focus:border-saffron'

  return (
    <div className="animate-fade-up">
      {/* Hero + Auth */}
      <section className="mx-auto grid max-w-6xl gap-12 px-4 py-12 sm:px-6 lg:grid-cols-[1.15fr_1fr] lg:items-center lg:py-20">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-saffron/40 bg-saffron-soft px-3.5 py-1 font-mono text-[11px] font-semibold uppercase tracking-widest text-saffron-deep">
            <span className="h-1.5 w-1.5 rounded-full bg-saffron" />
            ICMR-NIN data · 1,000+ Indian foods
          </span>

          <h1 className="mt-6 font-display text-4xl font-bold leading-[1.08] sm:text-5xl lg:text-6xl">
            Your daily thali,
            <br />
            tuned to{' '}
            <span className="relative text-saffron-deep">
              your body
              <span
                aria-hidden
                className="absolute inset-x-0 -bottom-1 h-3 -rotate-1 rounded-full bg-saffron-soft"
              />
            </span>
          </h1>

          <p className="mt-6 max-w-lg text-lg leading-relaxed text-clay">
            NutriMitra reads your age, activity and health conditions, then a
            kNN engine picks real Indian foods that fit your calorie and
            macro targets. No guesswork — just a plan that tastes like home.
          </p>

          <div className="mt-8 grid max-w-md grid-cols-3 gap-4">
            <HeroStat value="1,014" label="foods in the pantry" />
            <HeroStat value="3" label="diet styles" />
            <HeroStat value="0" label="guesswork" />
          </div>

          {/* Thali graphic */}
          <div className="relative mt-12 hidden h-64 w-64 lg:block">
            <div className="absolute inset-0 animate-spin-slower">
              <ThaliRing
                size={256}
                hole={0.5}
                centerLabel="Foods"
                centerValue="1,014"
                centerUnit="ICMR-NIN"
                segments={[
                  { percent: 34, color: 'var(--color-leaf)' },
                  { percent: 40, color: 'var(--color-saffron)' },
                  { percent: 26, color: 'var(--color-chilli)' },
                ]}
              />
            </div>
            {HERO_CHIPS.map(chip => (
              <span
                key={chip.label}
                className="absolute animate-float rounded-full border border-rim bg-cream px-3 py-1.5 font-mono text-xs font-semibold text-ink shadow-sm"
                style={{ top: chip.top, left: chip.left, animationDelay: chip.delay }}
              >
                {chip.label}
              </span>
            ))}
          </div>
        </div>

        {/* Auth card */}
        <div className="mx-auto w-full max-w-md rounded-3xl border border-rim bg-cream p-6 shadow-[0_24px_60px_-24px_rgba(34,26,18,0.25)] sm:p-8">
          <div className="flex rounded-full border border-rim bg-paper p-1">
            {(['register', 'login'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => {
                  setTab(mode)
                  setError('')
                }}
                className={`flex-1 cursor-pointer rounded-full py-2 text-sm font-semibold transition-colors ${
                  tab === mode
                    ? 'bg-saffron text-white shadow-sm'
                    : 'text-clay hover:text-ink'
                }`}
              >
                {mode === 'register' ? 'Create account' : 'Sign in'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {tab === 'register' && (
              <div>
                <Label htmlFor="name">Name</Label>
                <input
                  id="name"
                  required
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  className={inputClass}
                  placeholder="Riya Sharma"
                />
              </div>
            )}
            <div>
              <Label htmlFor="email">Email</Label>
              <input
                id="email"
                type="email"
                required
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className={inputClass}
                placeholder="you@example.com"
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <input
                id="password"
                type="password"
                required
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                className={inputClass}
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="rounded-xl border border-chilli/30 bg-chilli-soft px-3.5 py-2.5 text-sm text-chilli">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="w-full cursor-pointer rounded-xl bg-saffron py-3 font-semibold text-white shadow-sm transition-colors hover:bg-saffron-deep"
            >
              {tab === 'register' ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <p className="mt-5 text-center font-mono text-[11px] text-clay">
            Your profile stays yours. Plans save to your history automatically.
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="border-y border-rim bg-cream">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 py-14 sm:px-6 md:grid-cols-3">
          <FeatureCard
            icon="◎"
            title="A real Indian pantry"
            body="1,014 foods from the ICMR-NIN composition database — dal, roti, paneer, idli and everything between."
          />
          <FeatureCard
            icon="✚"
            title="A safety-first filter"
            body="Hard-blocks foods that clash with diabetes, hypertension, PCOS, kidney or heart conditions."
          />
          <FeatureCard
            icon="◉"
            title="kNN, not guesswork"
            body="A nearest-neighbours engine matches foods to your calorie, protein, carb and fat targets."
          />
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center font-display text-3xl font-bold">
          From your body to a thali in four steps
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Tell us about you', 'Age, gender, height, weight, activity — and any conditions we should avoid.'],
            ['Set your targets', 'BMR via Mifflin-St Jeor, then TDEE and macro split for your diet type.'],
            ['AI builds the plan', 'kNN scores real foods and assembles a day of meals that hits your numbers.'],
            ['Save it for later', 'Every plan lands in your history. Reload or regenerate anytime.'],
          ].map(([title, body], i) => (
            <div
              key={title}
              className="relative rounded-2xl border border-rim bg-cream p-6"
            >
              <span className="font-mono text-xs font-bold text-saffron-deep">
                0{i + 1}
              </span>
              <h3 className="mt-3 font-display text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-clay">{body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function Label({ htmlFor, children }: { htmlFor: string; children: React.ReactNode }) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1.5 block font-mono text-[11px] font-semibold uppercase tracking-widest text-clay"
    >
      {children}
    </label>
  )
}

function HeroStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <p className="font-display text-3xl font-bold text-ink">{value}</p>
      <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-clay">
        {label}
      </p>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  body,
}: {
  icon: string
  title: string
  body: string
}) {
  return (
    <div className="rounded-2xl border border-rim bg-paper p-6 transition-transform duration-300 hover:-translate-y-1">
      <span className="grid h-11 w-11 place-items-center rounded-xl bg-saffron-soft text-xl text-saffron-deep">
        {icon}
      </span>
      <h3 className="mt-4 font-display text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-clay">{body}</p>
    </div>
  )
}
