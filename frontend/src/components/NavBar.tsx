import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import Bulldog from './Bulldog'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'nav-link active' : 'nav-link'

export default function NavBar() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <div className="container">
        <NavLink to="/" className="brand">
          <span className="brand-mark">
            <Bulldog size={30} accent="var(--gold)" />
          </span>
          <span>
            <span className="brand-name">CAMPUS CUSTOMS</span>
            <span className="brand-tag">Official Yale Apparel</span>
          </span>
        </NavLink>

        <nav className="nav-links">
          <NavLink to="/" className={linkClass} end>
            Home
          </NavLink>
          <NavLink to="/products" className={linkClass}>
            Products
          </NavLink>
          <NavLink to="/about" className={linkClass}>
            About Us
          </NavLink>
          <span className="nav-divider" />

          {/* While the stored token is being checked, show nothing rather than
              flashing "Log In" at someone who is already signed in. */}
          {loading ? null : user ? (
            <>
              <span className="nav-greeting">
                <Bulldog size={20} accent="var(--gold-bright)" title="" />
                Hello, {user.first_name}
              </span>
              <button type="button" className="nav-link nav-logout" onClick={handleLogout}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Log In
              </NavLink>
              <NavLink to="/create-account" className="nav-cta">
                Create Account
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
