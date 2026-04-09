import { useState } from 'react'

export default function TaskForm({ initial = {}, onSubmit, onCancel, submitLabel = 'Crear' }) {
  const [form, setForm] = useState({
    title: initial.title || '',
    description: initial.description || '',
    priority: initial.priority || 'medium',
    due_date: initial.due_date || '',
    tags: Array.isArray(initial.tags) ? initial.tags.join(', ') : '',
  })
  const [error, setError] = useState('')

  function set(field, val) {
    setForm((f) => ({ ...f, [field]: val }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!form.title.trim()) {
      setError('El título es obligatorio')
      return
    }
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      priority: form.priority,
    }
    if (form.due_date) payload.due_date = form.due_date
    if (form.tags.trim()) {
      payload.tags = form.tags.split(',').map((t) => t.trim()).filter(Boolean)
    }
    onSubmit(payload)
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      {error && <p className="form-error">{error}</p>}

      <div className="form-group">
        <label>Título *</label>
        <input
          type="text"
          value={form.title}
          onChange={(e) => set('title', e.target.value)}
          placeholder="Nombre de la tarea"
          autoFocus
        />
      </div>

      <div className="form-group">
        <label>Descripción</label>
        <textarea
          value={form.description}
          onChange={(e) => set('description', e.target.value)}
          placeholder="Descripción opcional"
          rows={3}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Prioridad</label>
          <select value={form.priority} onChange={(e) => set('priority', e.target.value)}>
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>

        <div className="form-group">
          <label>Fecha límite</label>
          <input
            type="date"
            value={form.due_date}
            onChange={(e) => set('due_date', e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Etiquetas (separadas por coma)</label>
        <input
          type="text"
          value={form.tags}
          onChange={(e) => set('tags', e.target.value)}
          placeholder="bug, frontend, urgente"
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          {submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancelar
          </button>
        )}
      </div>
    </form>
  )
}
