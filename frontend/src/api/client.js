// A tiny wrapper around fetch that talks to the Django API.
const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')
const TOKEN_KEY = 'osc_token'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

export class ApiError extends Error {
  constructor(message, status, fields = {}) {
    super(message)
    this.status = status
    this.fields = fields
  }
}

// DRF returns errors as {detail: "..."} or {field: ["..."]}. Turn both into
// one readable message plus a per-field map for forms.
function parseError(status, body) {
  if (!body || typeof body !== 'object') {
    return new ApiError(`Request failed (${status}).`, status)
  }
  if (typeof body.detail === 'string') {
    return new ApiError(body.detail, status)
  }
  const fields = {}
  for (const [key, value] of Object.entries(body)) {
    fields[key] = Array.isArray(value) ? value.join(' ') : String(value)
  }
  const message = fields.non_field_errors || Object.values(fields)[0] || `Request failed (${status}).`
  return new ApiError(message, status, fields)
}

export async function request(path, { method = 'GET', body } = {}) {
  const headers = { Accept: 'application/json' }
  const token = tokenStore.get()
  if (token) headers.Authorization = `Token ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError('Could not reach the server. Check that the backend is running.', 0)
  }

  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (!response.ok) throw parseError(response.status, data)
  return data
}

export const api = {
  // Auth
  register: (payload) => request('/auth/register/', { method: 'POST', body: payload }),
  login: (payload) => request('/auth/login/', { method: 'POST', body: payload }),
  logout: () => request('/auth/logout/', { method: 'POST' }),
  me: () => request('/auth/me/'),

  // Sessions
  listSessions: (when = 'upcoming') => request(`/sessions/?when=${when}`),
  getSession: (id) => request(`/sessions/${id}/`),
  createSession: (payload) => request('/sessions/', { method: 'POST', body: payload }),
  updateSession: (id, payload) => request(`/sessions/${id}/`, { method: 'PATCH', body: payload }),
  deleteSession: (id) => request(`/sessions/${id}/`, { method: 'DELETE' }),

  // RSVP
  rsvp: (id) => request(`/sessions/${id}/rsvp/`, { method: 'POST' }),
  cancelRsvp: (id) => request(`/sessions/${id}/rsvp/`, { method: 'DELETE' }),

  // Organizer tools
  attendees: (id) => request(`/sessions/${id}/attendees/`),
  createMeetLink: (id, regenerate = false) =>
    request(`/sessions/${id}/meet-link/`, { method: 'POST', body: { regenerate } }),
  sendInvites: (id) => request(`/sessions/${id}/send-invites/`, { method: 'POST' }),
}
