interface ThaliSegment {
  percent: number
  color: string
}

interface ThaliRingProps {
  segments: ThaliSegment[]
  centerLabel: string
  centerValue: string
  centerUnit?: string
  size?: number
  hole?: number
  className?: string
}

export default function ThaliRing({
  segments,
  centerLabel,
  centerValue,
  centerUnit,
  size = 190,
  hole = 0.42,
  className = '',
}: ThaliRingProps) {
  const active = segments.filter(s => s.percent > 0)
  const total = active.reduce((sum, s) => sum + s.percent, 0)
  const normalized =
    total > 0
      ? active.map(s => (s.percent / total) * 100)
      : active.map(() => 0)

  let acc = 0
  const stops = normalized
    .map((p, i) => {
      const start = acc
      acc += p
      return `${active[i].color} ${start}% ${acc}%`
    })
    .join(', ')
  const background = active.length
    ? `conic-gradient(${stops})`
    : 'var(--color-rim)'

  const inner = size * hole

  return (
    <div
      className={`relative rounded-full ${className}`}
      style={{
        width: size,
        height: size,
        background,
        boxShadow:
          'inset 0 0 0 1px rgba(34,26,18,0.08), 0 12px 30px -12px rgba(34,26,18,0.35)',
      }}
    >
      <div
        className="absolute rounded-full bg-paper flex flex-col items-center justify-center text-center"
        style={{
          inset: (size - inner) / 2,
          boxShadow: '0 0 0 1px rgba(34,26,18,0.06)',
        }}
      >
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-clay">
          {centerLabel}
        </span>
        <span className="font-display font-bold text-ink leading-none mt-1" style={{ fontSize: size * 0.16 }}>
          {centerValue}
        </span>
        {centerUnit && (
          <span className="font-mono text-[11px] text-clay mt-0.5">{centerUnit}</span>
        )}
      </div>
    </div>
  )
}
