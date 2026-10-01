import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/auth.js'
import Notice from '../components/Notice.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(form.email, form.password)
      navigate(location.state?.from || '/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="page page--form">
      <h1>Log in</h1>
      <form className="form" onSubmit={submit} noValidate>
        <Notice tone="error">{error}</Notice>
        <label>
          Email
          <input name="email" type="email" autoComplete="email" value={form.email} onChange={update} required />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={update}
            required
          />
        </label>
        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      <p className="form-footer">
        New here? <Link to="/register">Create an account</Link>
      </p>
    </section>
  )
}
