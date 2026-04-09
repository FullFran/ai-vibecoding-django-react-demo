import { useState } from 'react'
import TaskForm from './TaskForm'

const PRIORITY_LABEL = { low: 'Baja', medium: 'Media', high: 'Alta' }
const STATUS_LABEL = { TODO: 'Por hacer', IN_PROGRESS: 'En curso', DONE: 'Hecho' }

export default function TaskCard({ task, onUpdate, onDelete, onTransition }) {
  const [editing, setEditing] = useState(false)
  const [confirming, setConfirming] = useState(false)

  function handleDelete() {
    if (confirming) {
      onDelete(task.id)
    } else {
      setConfirming(true)
    }
  }

  if (editing) {
    return (
      <div className="task-card editing">
        <TaskForm
          initial={task}
          onSubmit={(data) => {
            onUpdate(task.id, data)
            setEditing(false)
          }}
          onCancel={() => setEditing(false)}
          submitLabel="Guardar"
        />
      </div>
    )
  }

  return (
    <div className={`task-card priority-${task.priority}`}>
      <div className="card-header">
        <div className="badges">
          <span className={`badge priority-badge priority-${task.priority}`}>
            {PRIORITY_LABEL[task.priority]}
          </span>
          <span className={`badge status-badge status-${task.status}`}>
            {STATUS_LABEL[task.status]}
          </span>
        </div>
        <div className="card-actions">
          <button
            className="icon-btn"
            title="Retroceder estado"
            onClick={() => onTransition(task.id, 'backward')}
            disabled={task.status === 'TODO'}
          >
            &#8592;
          </button>
          <button
            className="icon-btn"
            title="Avanzar estado"
            onClick={() => onTransition(task.id, 'forward')}
            disabled={task.status === 'DONE'}
          >
            &#8594;
          </button>
          <button className="icon-btn edit-btn" title="Editar" onClick={() => setEditing(true)}>
            &#9998;
          </button>
          <button
            className={`icon-btn delete-btn${confirming ? ' confirming' : ''}`}
            title={confirming ? 'Confirmar eliminación' : 'Eliminar'}
            onClick={handleDelete}
            onBlur={() => setConfirming(false)}
          >
            {confirming ? '✓ Confirmar' : '&#10005;'}
          </button>
        </div>
      </div>

      <h3 className="card-title">{task.title}</h3>

      {task.description && <p className="card-desc">{task.description}</p>}

      <div className="card-meta">
        {task.due_date && (
          <span className="meta-item">
            <span className="meta-icon">&#128197;</span> {task.due_date}
          </span>
        )}
        {task.tags && task.tags.length > 0 && (
          <div className="tags">
            {task.tags.map((t, i) => (
              <span key={i} className="tag">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
