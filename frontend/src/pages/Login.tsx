import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  // Already signed in (or just finished signing in): nothing to do on this page.
  useEffect(() => {
    if (user) navigate('/products', { replace: true })
  }, [user, navigate])

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await login(email, password)
      // The password state is dropped as soon as the request is done.
      setPassword('')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Welcome Back</h1>
        <p className="auth-sub">Log in to your Campus Customs account.</p>

        <div className="field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@yale.edu"
            required
          />
        </div>

        <div className="field">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button className="btn btn-navy" type="submit" disabled={busy}>
          {busy ? 'Logging in…' : 'Log In'}
        </button>

        {error && (
          <p className="notice notice-error" role="alert">
            {error}
          </p>
        )}

        <p className="auth-foot">
          New to Campus Customs? <Link to="/create-account">Create an account</Link>
        </p>
      </form>
    </div>
  )
}
