import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../../api/client.js'
import Loading from '../../components/Loading.jsx'
import Notice from '../../components/Notice.jsx'
import { fromLocalInputValue, toLocalInputValue } from '../../utils/format.js'

const EMPTY = {
  title: '',
  description: '',
  starts_at: '',
  ends_at: '',
  mode: 'online',
  location: '',
  capacity: '',
}

export default function SessionEditor() {
  const { id } = useParams()
  const isEditing = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(isEditing ? null : EMPTY)
  const [errors, setErrors] = useState({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!isEditing) return
    api
      .getSession(id)
      .then((session) =>
        setForm({
          ...EMPTY,
          ...session,
          starts_at: toLocalInputValue(session.starts_at),
          ends_at: toLocalInputValue(session.ends_at),
          capacity: session.capacity ?? '',
        }),
      )
      .catch((err) => setError(err.message))
  }, [id, isEditing])

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    setErrors({})
    const payload = {
      title: form.title,
      description: form.description,
      mode: form.mode,
      location: form.location,
      starts_at: fromLocalInputValue(form.starts_at),
      ends_at: fromLocalInputValue(form.ends_at),
      capacity: form.capacity === '' ? null : Number(form.capacity),
    }
    try {
      const saved = isEditing ? await api.updateSession(id, payload) : await api.createSession(payload)
      navigate(`/organize/${saved.id}`)
    } catch (err) {
      setErrors(err.fields || {})
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (!form) return error ? <Notice tone="error">{error}</Notice> : <Loading />

  const needsLocation = form.mode !== 'online'

  return (
    <section className="page page--form">
      <Link to={isEditing ? `/organize/${id}` : '/organize'} className="back-link">
        {isEditing ? 'Back to session' : 'Back to dashboard'}
      </Link>
      <h1>{isEditing ? 'Edit session' : 'New session'}</h1>

      <form className="form" onSubmit={submit} noValidate>
        <Notice tone="error">{error}</Notice>

        <label>
          Title
          <input name="title" value={form.title} onChange={update} required maxLength={200} />
          {errors.title && <span className="field-error">{errors.title}</span>}
        </label>

        <label>
          Description
          <textarea name="description" rows={5} value={form.description} onChange={update} />
        </label>

        <div className="form__row">
          <label>
            Starts
            <input name="starts_at" type="datetime-local" value={form.starts_at} onChange={update} required />
            {errors.starts_at && <span className="field-error">{errors.starts_at}</span>}
          </label>
          <label>
            Ends
            <input name="ends_at" type="datetime-local" value={form.ends_at} onChange={update} required />
            {errors.ends_at && <span className="field-error">{errors.ends_at}</span>}
          </label>
        </div>

        <fieldset className="choices">
          <legend>Format</legend>
          {[
            ['online', 'Online'],
            ['in_person', 'In person'],
            ['hybrid', 'Hybrid'],
          ].map(([value, label]) => (
            <label key={value} className="choice">
              <input type="radio" name="mode" value={value} checked={form.mode === value} onChange={update} />
              {label}
            </label>
          ))}
        </fieldset>

        {needsLocation && (
          <label>
            Location
            <input name="location" value={form.location} onChange={update} placeholder="e.g. Seminar Hall, Block A" />
            {errors.location && <span className="field-error">{errors.location}</span>}
          </label>
        )}

        <label>
          Capacity
          <input name="capacity" type="number" min="1" value={form.capacity} onChange={update} />
          <span className="hint">Leave empty for unlimited seats.</span>
          {errors.capacity && <span className="field-error">{errors.capacity}</span>}
        </label>

        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Saving…' : isEditing ? 'Save changes' : 'Create session'}
        </button>
      </form>
    </section>
  )
}
