const BASE = '/api/tasks'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data))
  return data
}

export const api = {
  list: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.status) qs.set('status', params.status)
    if (params.priority) qs.set('priority', params.priority)
    const query = qs.toString() ? `?${qs}` : ''
    return request(`/${query}`)
  },

  listPage: (url) => fetch(url).then((r) => r.json()),

  create: (body) =>
    request('/', { method: 'POST', body: JSON.stringify(body) }),

  update: (id, body) =>
    request(`/${id}/`, { method: 'PATCH', body: JSON.stringify(body) }),

  remove: (id) => request(`/${id}/`, { method: 'DELETE' }),

  transition: (id, direction) =>
    request(`/${id}/transition/`, {
      method: 'POST',
      body: JSON.stringify({ direction }),
    }),
}
