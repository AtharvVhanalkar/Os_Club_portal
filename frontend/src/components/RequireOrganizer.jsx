import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/auth.js'
import Loading from './Loading.jsx'

export default function RequireOrganizer() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  if (!user.is_organizer) {
    return (
      <section className="page page--narrow">
        <h1>Organizers only</h1>
        <p>This area is for club organizers. Ask a maintainer if you need access.</p>
      </section>
    )
  }
  return <Outlet />
}
