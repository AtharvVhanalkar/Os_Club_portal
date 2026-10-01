import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/auth.js'
import Loading from '../components/Loading.jsx'
import Notice from '../components/Notice.jsx'
import { formatLongDay, formatTimeRange, MODE_LABELS, seatsLabel } from '../utils/format.js'

export default function SessionDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const location = useLocation()
  const [session, setSession] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [now] = useState(() => Date.now())

  useEffect(() => {
    api.getSession(id).then(setSession).catch((err) => setError(err.message))
  }, [id, user])

  const isPast = session && new Date(session.ends_at).getTime() < now
  const isFull = session && session.seats_left === 0

  const toggleRsvp = async () => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      if (session.has_rsvped) {
        setSession(await api.cancelRsvp(id))
        setMessage('Your registration is cancelled.')
      } else {
        setSession(await api.rsvp(id))
        setMessage("You're registered. We'll email you the details before the session.")
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (!session && !error) return <Loading label="Loading session" />
  if (!session) {
    return (
      <section className="page page--narrow">
        <Notice tone="error">{error}</Notice>
        <Link to="/">Back to sessions</Link>
      </section>
    )
  }

  return (
    <article className="page page--narrow session">
      <Link to="/" className="back-link">All sessions</Link>
      <h1>{session.title}</h1>

      <dl className="facts">
        <div>
          <dt>Date</dt>
          <dd>{formatLongDay(session.starts_at)}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>{formatTimeRange(session.starts_at, session.ends_at)}</dd>
        </div>
        <div>
          <dt>Format</dt>
          <dd>{MODE_LABELS[session.mode]}</dd>
        </div>
        {session.location && (
          <div>
            <dt>Location</dt>
            <dd>{session.location}</dd>
          </div>
        )}
        <div>
          <dt>Seats</dt>
          <dd>{seatsLabel(session)}</dd>
        </div>
      </dl>

      {session.description && <p className="session__description">{session.description}</p>}

      <div className="rsvp-box">
        <Notice tone="error">{error}</Notice>
        <Notice tone="success">{message}</Notice>

        {session.meet_link && (
          <p className="meet-link">
            Meeting link: <a href={session.meet_link} target="_blank" rel="noreferrer">{session.meet_link}</a>
          </p>
        )}

        {isPast ? (
          <p className="muted">This session has ended.</p>
        ) : !user ? (
          <p>
            <Link to="/login" state={{ from: location.pathname }} className="button">Log in to register</Link>
          </p>
        ) : session.has_rsvped ? (
          <button type="button" className="button button--ghost" onClick={toggleRsvp} disabled={busy}>
            {busy ? 'Cancelling…' : 'Cancel my registration'}
          </button>
        ) : (
          <button type="button" className="button" onClick={toggleRsvp} disabled={busy || isFull}>
            {isFull ? 'Session is full' : busy ? 'Registering…' : 'Register for this session'}
          </button>
        )}

        {user?.is_organizer && (
          <p>
            <Link to={`/organize/${session.id}`}>Manage this session</Link>
          </p>
        )}
      </div>
    </article>
  )
}
