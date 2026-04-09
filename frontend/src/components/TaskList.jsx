import TaskCard from './TaskCard'

export default function TaskList({ tasks, pagination, onUpdate, onDelete, onTransition, onPage }) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-icon">&#128203;</span>
        <p>No hay tareas</p>
        <span className="empty-hint">Crea una nueva tarea para empezar</span>
      </div>
    )
  }

  return (
    <div>
      <div className="task-grid">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onTransition={onTransition}
          />
        ))}
      </div>

      {(pagination.next || pagination.previous) && (
        <div className="pagination">
          <button
            className="btn btn-secondary"
            disabled={!pagination.previous}
            onClick={() => onPage(pagination.previous)}
          >
            &#8592; Anterior
          </button>
          <button
            className="btn btn-secondary"
            disabled={!pagination.next}
            onClick={() => onPage(pagination.next)}
          >
            Siguiente &#8594;
          </button>
        </div>
      )}
    </div>
  )
}
