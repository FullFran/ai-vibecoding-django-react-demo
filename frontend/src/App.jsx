import { useState, useEffect, useCallback } from 'react'
import { api } from './api'
import FilterBar from './components/FilterBar'
import TaskList from './components/TaskList'
import TaskForm from './components/TaskForm'
import './App.css'

export default function App() {
  const [tasks, setTasks] = useState([])
  const [pagination, setPagination] = useState({ count: 0, next: null, previous: null })
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)

  const loadTasks = useCallback(async (params) => {
    setLoading(true)
    setError('')
    try {
      const data = await api.list(params)
      setTasks(data.results ?? data)
      setPagination({ count: data.count, next: data.next, previous: data.previous })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTasks({ status: statusFilter, priority: priorityFilter })
  }, [statusFilter, priorityFilter, loadTasks])

  async function handleCreate(body) {
    try {
      await api.create(body)
      setShowForm(false)
      loadTasks({ status: statusFilter, priority: priorityFilter })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleUpdate(id, body) {
    try {
      await api.update(id, body)
      loadTasks({ status: statusFilter, priority: priorityFilter })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(id) {
    try {
      await api.remove(id)
      loadTasks({ status: statusFilter, priority: priorityFilter })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleTransition(id, direction) {
    try {
      await api.transition(id, direction)
      loadTasks({ status: statusFilter, priority: priorityFilter })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handlePage(url) {
    setLoading(true)
    setError('')
    try {
      const data = await api.listPage(url)
      setTasks(data.results ?? data)
      setPagination({ count: data.count, next: data.next, previous: data.previous })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <span className="brand-icon">&#9776;</span>
            <h1>AITasks</h1>
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
            {showForm ? '&#10005; Cancelar' : '+ Nueva tarea'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {showForm && (
          <div className="create-panel">
            <h2 className="panel-title">Nueva tarea</h2>
            <TaskForm
              onSubmit={handleCreate}
              onCancel={() => setShowForm(false)}
              submitLabel="Crear tarea"
            />
          </div>
        )}

        <FilterBar
          statusFilter={statusFilter}
          priorityFilter={priorityFilter}
          onStatus={setStatusFilter}
          onPriority={setPriorityFilter}
        />

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button className="dismiss" onClick={() => setError('')}>
              &#10005;
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading">Cargando tareas&hellip;</div>
        ) : (
          <TaskList
            tasks={tasks}
            pagination={pagination}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onTransition={handleTransition}
            onPage={handlePage}
          />
        )}

        {!loading && (
          <p className="task-count">
            {pagination.count !== undefined ? `${pagination.count} tarea(s) en total` : ''}
          </p>
        )}
      </main>
    </div>
  )
}
