import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/auth.js'
import SessionTimeline from '../components/SessionTimeline.jsx'
import Loading from '../components/Loading.jsx'
import Notice from '../components/Notice.jsx'

export default function Home() {
  const { user } = useAuth()
  const [when, setWhen] = useState('upcoming')
  const [result, setResult] = useState({ key: null, sessions: null, error: '' })
  const key = `${when}:${user?.id ?? 'guest'}`

  useEffect(() => {
    let active = true
    api
      .listSessions(when)
      .then((sessions) => active && setResult({ key, sessions, error: '' }))
      .catch((err) => active && setResult({ key, sessions: null, error: err.message }))
    return () => {
      active = false
    }
  }, [when, key])

  // Results from a previous filter are ignored until the new ones arrive.
  const current = result.key === key ? result : { sessions: null, error: '' }
  const { sessions, error } = current

  return (
    <>
      <section className="hero">
        <h1 className="hero__title">Learn open source by shipping it.</h1>
        <p className="hero__lede">
          Talks, workshops and hack nights run by students who contribute to real projects. Register for a
          session and we'll send the details and the meeting link to your inbox.
        </p>
        {!user && (
          <div className="hero__actions">
            <Link to="/register" className="button">Join the club</Link>
            <Link to="/login" className="button button--ghost">I already have an account</Link>
          </div>
        )}
      </section>

      <section className="page" aria-labelledby="sessions-heading">
        <div className="section-head">
          <h2 id="sessions-heading">{when === 'upcoming' ? 'Upcoming sessions' : 'Past sessions'}</h2>
          <div className="segmented" role="group" aria-label="Show sessions">
            <button type="button" aria-pressed={when === 'upcoming'} onClick={() => setWhen('upcoming')}>
              Upcoming
            </button>
            <button type="button" aria-pressed={when === 'past'} onClick={() => setWhen('past')}>
              Past
            </button>
          </div>
        </div>

        <Notice tone="error">{error}</Notice>
        {!sessions && !error && <Loading label="Loading sessions" />}
        {sessions && sessions.length === 0 && (
          <div className="empty">
            <p>
              {when === 'upcoming'
                ? 'No sessions are scheduled yet. Check back soon, or ask an organizer to host one.'
                : 'No past sessions yet.'}
            </p>
            {user?.is_organizer && when === 'upcoming' && (
              <Link to="/organize/new" className="button">Schedule a session</Link>
            )}
          </div>
        )}
        {sessions && sessions.length > 0 && <SessionTimeline sessions={sessions} />}
      </section>
    </>
  )
}
