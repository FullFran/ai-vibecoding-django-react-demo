export default function FilterBar({ statusFilter, priorityFilter, onStatus, onPriority }) {
  const statuses = [
    { value: '', label: 'Todas' },
    { value: 'TODO', label: 'Por hacer' },
    { value: 'IN_PROGRESS', label: 'En curso' },
    { value: 'DONE', label: 'Hecho' },
  ]

  const priorities = [
    { value: '', label: 'Todas' },
    { value: 'low', label: 'Baja' },
    { value: 'medium', label: 'Media' },
    { value: 'high', label: 'Alta' },
  ]

  return (
    <div className="filter-bar">
      <div className="tab-group">
        {statuses.map((s) => (
          <button
            key={s.value}
            className={`tab-btn${statusFilter === s.value ? ' active' : ''}`}
            onClick={() => onStatus(s.value)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="priority-group">
        <span className="filter-label">Prioridad:</span>
        {priorities.map((p) => (
          <button
            key={p.value}
            className={`pill-btn${priorityFilter === p.value ? ' active' : ''}`}
            onClick={() => onPriority(p.value)}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  )
}
