import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/auth.js'

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <header className="header">
      <a className="skip-link" href="#main">Skip to content</a>
      <div className="header__inner">
        <Link to="/" className="brand">
          <span className="brand__mark" aria-hidden="true" />
          Open Source Club
        </Link>
        <nav className="nav" aria-label="Main">
          <NavLink to="/" end>Sessions</NavLink>
          <NavLink to="/contributors">Contributors</NavLink>
          {user?.is_organizer && <NavLink to="/organize">Organize</NavLink>}
          {user ? (
            <>
              <span className="nav__user">{user.first_name || user.email}</span>
              <button type="button" className="link-button" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <Link to="/register" className="button button--small">Join the club</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
