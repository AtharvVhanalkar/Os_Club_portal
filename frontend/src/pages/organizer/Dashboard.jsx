import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client.js'
import Loading from '../../components/Loading.jsx'
import Notice from '../../components/Notice.jsx'
import { formatDay, formatTime, MODE_LABELS } from '../../utils/format.js'

export default function Dashboard() {
  const [sessions, setSessions] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listSessions('upcoming').then(setSessions).catch((err) => setError(err.message))
  }, [])

  return (
    <section className="page">
      <div className="section-head">
        <h1>Organize</h1>
        <Link to="/organize/new" className="button">New session</Link>
      </div>

      <Notice tone="error">{error}</Notice>
      {!sessions && !error && <Loading />}
      {sessions && sessions.length === 0 && (
        <div className="empty">
          <p>No upcoming sessions. Schedule one to open registrations.</p>
        </div>
      )}
      {sessions && sessions.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Session</th>
                <th scope="col">When</th>
                <th scope="col">Format</th>
                <th scope="col">Registered</th>
                <th scope="col">Invites</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id}>
                  <td>
                    <Link to={`/organize/${session.id}`}>{session.title}</Link>
                  </td>
                  <td>
                    {formatDay(session.starts_at)}, {formatTime(session.starts_at)}
                  </td>
                  <td>{MODE_LABELS[session.mode]}</td>
                  <td>
                    {session.rsvp_count}
                    {session.capacity !== null && ` / ${session.capacity}`}
                  </td>
                  <td>{session.invites_sent_at ? 'Sent' : 'Not sent'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
