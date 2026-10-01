import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/auth.js'
import Notice from '../components/Notice.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    setErrors({})
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setErrors(err.fields || {})
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="page page--form">
      <h1>Join the club</h1>
      <p className="muted">Create an account to register for sessions.</p>
      <form className="form" onSubmit={submit} noValidate>
        <Notice tone="error">{error}</Notice>
        <div className="form__row">
          <label>
            First name
            <input name="first_name" autoComplete="given-name" value={form.first_name} onChange={update} required />
          </label>
          <label>
            Last name
            <input name="last_name" autoComplete="family-name" value={form.last_name} onChange={update} />
          </label>
        </div>
        <label>
          College email
          <input name="email" type="email" autoComplete="email" value={form.email} onChange={update} required />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={update}
            required
          />
          <span className="hint">At least 8 characters. Avoid common passwords.</span>
          {errors.password && <span className="field-error">{errors.password}</span>}
        </label>
        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="form-footer">
        Already a member? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
