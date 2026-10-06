import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

const MIN_PASSWORD_LENGTH = 8

export default function CreateAccount() {
  const { user, signup } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  // Signup logs you straight in, so leave the form once that happens.
  useEffect(() => {
    if (user) navigate('/products', { replace: true })
  }, [user, navigate])

  const update = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }))

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)

    // Check the match here too so the user gets the message without a round trip;
    // the backend checks it again regardless.
    if (form.password !== form.confirmPassword) {
      setError('The passwords do not match.')
      return
    }

    setBusy(true)
    try {
      await signup(form)
      setForm((prev) => ({ ...prev, password: '', confirmPassword: '' }))
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Join the Pride</h1>
        <p className="auth-sub">Create your Campus Customs account.</p>

        <div className="field-row">
          <div className="field">
            <label htmlFor="first-name">First Name</label>
            <input
              id="first-name"
              autoComplete="given-name"
              value={form.firstName}
              onChange={update('firstName')}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="last-name">Last Name</label>
            <input
              id="last-name"
              autoComplete="family-name"
              value={form.lastName}
              onChange={update('lastName')}
              required
            />
          </div>
        </div>

        <div className="field">
          <label htmlFor="signup-email">Email</label>
          <input
            id="signup-email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={update('email')}
            placeholder="you@yale.edu"
            required
          />
        </div>

        <div className="field">
          <label htmlFor="signup-password">Password</label>
          <input
            id="signup-password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={update('password')}
            minLength={MIN_PASSWORD_LENGTH}
            required
          />
          <span className="field-hint">
            At least {MIN_PASSWORD_LENGTH} characters.
          </span>
        </div>

        <div className="field">
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            value={form.confirmPassword}
            onChange={update('confirmPassword')}
            minLength={MIN_PASSWORD_LENGTH}
            required
          />
        </div>

        <button className="btn btn-navy" type="submit" disabled={busy}>
          {busy ? 'Creating account…' : 'Create Account'}
        </button>

        {error && (
          <p className="notice notice-error" role="alert">
            {error}
          </p>
        )}

        <p className="auth-foot">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}
