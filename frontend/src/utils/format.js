const dayFormatter = new Intl.DateTimeFormat('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
const longDayFormatter = new Intl.DateTimeFormat('en-IN', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})
const timeFormatter = new Intl.DateTimeFormat('en-IN', { hour: 'numeric', minute: '2-digit' })

export const formatDay = (iso) => dayFormatter.format(new Date(iso))
export const formatLongDay = (iso) => longDayFormatter.format(new Date(iso))
export const formatTime = (iso) => timeFormatter.format(new Date(iso))
export const formatTimeRange = (start, end) => `${formatTime(start)} to ${formatTime(end)}`

export const MODE_LABELS = {
  online: 'Online',
  in_person: 'In person',
  hybrid: 'Hybrid',
}

export function seatsLabel(session) {
  if (session.seats_left === null) return `${session.rsvp_count} going`
  if (session.seats_left === 0) return 'Full'
  return `${session.seats_left - 1} of ${session.capacity} seats left`
}

// <input type="datetime-local"> works with "YYYY-MM-DDTHH:mm" in local time.
export function toLocalInputValue(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

export const fromLocalInputValue = (value) => (value ? new Date(value).toISOString() : null)
