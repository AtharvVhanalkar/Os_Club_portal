import { Link } from 'react-router-dom'
import { formatDay, formatTimeRange, MODE_LABELS, seatsLabel } from '../utils/format.js'

/**
 * Sessions drawn as a commit history: one line, one node per session.
 * Sessions you've registered for get a filled node.
 */
export default function SessionTimeline({ sessions }) {
  return (
    <ol className="timeline">
      {sessions.map((session) => (
        <li key={session.id} className={`timeline__item${session.has_rsvped ? ' is-going' : ''}`}>
          <span className="timeline__node" aria-hidden="true" />
          <div className="timeline__when">
            <span className="timeline__day">{formatDay(session.starts_at)}</span>
            <span className="timeline__time">{formatTimeRange(session.starts_at, session.ends_at)}</span>
          </div>
          <div className="timeline__body">
            <h3 className="timeline__title">
              <Link to={`/sessions/${session.id}`}>{session.title}</Link>
            </h3>
            <p className="timeline__meta">
              <span>{MODE_LABELS[session.mode]}</span>
              {session.location && <span>{session.location}</span>}
              <span>{seatsLabel(session)}</span>
              {session.has_rsvped && <span className="tag tag--going">You're going</span>}
            </p>
          </div>
        </li>
      ))}
    </ol>
  )
}
