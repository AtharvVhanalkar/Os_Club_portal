import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../../api/client.js'
import Loading from '../../components/Loading.jsx'
import Notice from '../../components/Notice.jsx'
import { formatLongDay, formatTimeRange, MODE_LABELS } from '../../utils/format.js'

export default function ManageSession() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [attendees, setAttendees] = useState([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([api.getSession(id), api.attendees(id)])
      .then(([sessionData, attendeeData]) => {
        if (!active) return
        setSession(sessionData)
        setAttendees(attendeeData)
      })
      .catch((err) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [id])

  const run = async (label, task) => {
    setBusy(label)
    setError('')
    setMessage('')
    try {
      await task()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy('')
    }
  }

  const createLink = () =>
    run('link', async () => {
      setSession(await api.createMeetLink(id, Boolean(session.meet_link)))
      setMessage('Meeting link is ready.')
    })

  const sendInvites = () =>
    run('invites', async () => {
      const result = await api.sendInvites(id)
      setSession(result.session)
      setMessage(`Sent ${result.sent} invite${result.sent === 1 ? '' : 's'}.`)
    })

  const remove = () => {
    if (!window.confirm(`Delete "${session.title}"? Registrations will be removed too.`)) return
    run('delete', async () => {
      await api.deleteSession(id)
      navigate('/organize')
    })
  }

  if (!session && !error) return <Loading />
  if (!session) return <Notice tone="error">{error}</Notice>

  const needsLink = session.mode !== 'in_person'

  return (
    <section className="page">
      <Link to="/organize" className="back-link">Back to dashboard</Link>
      <div className="section-head">
        <h1>{session.title}</h1>
        <div className="actions">
          <Link to={`/sessions/${session.id}`} className="button button--ghost">View public page</Link>
          <Link to={`/organize/${session.id}/edit`} className="button button--ghost">Edit</Link>
        </div>
      </div>
      <p className="muted">
        {formatLongDay(session.starts_at)}, {formatTimeRange(session.starts_at, session.ends_at)}.{' '}
        {MODE_LABELS[session.mode]}
        {session.location && ` at ${session.location}`}.
      </p>

      <Notice tone="error">{error}</Notice>
      <Notice tone="success">{message}</Notice>

      <div className="manage-grid">
        <div className="panel">
          <h2>Invitations</h2>
          {needsLink && (
            <>
              <p className="panel__label">Meeting link</p>
              {session.meet_link ? (
                <p className="meet-link">
                  <a href={session.meet_link} target="_blank" rel="noreferrer">{session.meet_link}</a>
                </p>
              ) : (
                <p className="muted">No link yet. One is created automatically when you send invites.</p>
              )}
              <button type="button" className="button button--ghost" onClick={createLink} disabled={Boolean(busy)}>
                {busy === 'link' ? 'Creating…' : session.meet_link ? 'Create a new link' : 'Create meeting link'}
              </button>
            </>
          )}

          <p className="panel__label">Email</p>
          <p className="muted">
            {session.invites_sent_at
              ? `Last sent ${new Date(session.invites_sent_at).toLocaleString('en-IN')}.`
              : 'Invites have not been sent yet.'}
          </p>
          <button
            type="button"
            className="button"
            onClick={sendInvites}
            disabled={Boolean(busy) || attendees.length === 0}
          >
            {busy === 'invites'
              ? 'Sending…'
              : `Send invites to ${attendees.length} ${attendees.length === 1 ? 'person' : 'people'}`}
          </button>
        </div>

        <div className="panel">
          <h2>
            Registered <span className="count">{attendees.length}</span>
          </h2>
          {attendees.length === 0 ? (
            <p className="muted">Nobody has registered yet. Share the session page to get the word out.</p>
          ) : (
            <ul className="attendees">
              {attendees.map(({ id: rsvpId, user }) => (
                <li key={rsvpId}>
                  <span>{[user.first_name, user.last_name].filter(Boolean).join(' ') || 'Member'}</span>
                  <span className="muted">{user.email}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="danger-zone">
        <button type="button" className="link-button link-button--danger" onClick={remove} disabled={Boolean(busy)}>
          Delete this session
        </button>
      </div>
    </section>
  )
}
