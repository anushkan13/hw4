// Session state for the whole app.
//
// The backend returns an HMAC-signed token on login/signup; we keep it in
// localStorage so a refresh or a new tab stays signed in, and re-validate it against
// /api/auth/me on load. The plain password is only ever a form field value -- it is
// sent once over the request body and never stored anywhere on the client.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { API_BASE } from './api'

export interface User {
  id: number
  first_name: string
  last_name: string
  name: string
  email: string
  created_at: string | null
}

export interface SignupInput {
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
}

const TOKEN_KEY = 'campus-customs-token'

interface AuthValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (input: SignupInput) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

/** POST helper that turns a FastAPI error body into a readable message. */
async function postJSON<T>(path: string, body: unknown): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error(
      'Could not reach the Campus Customs backend. Start it with: ' +
        'uvicorn backend.main:app --port 8000',
    )
  }
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data?.detail
    if (typeof detail === 'string') throw new Error(detail)
    // 422 from pydantic comes back as a list of field errors.
    if (Array.isArray(detail) && detail[0]?.msg) {
      throw new Error(String(detail[0].msg).replace(/^Value error, /, ''))
    }
    throw new Error(`Request failed (${res.status})`)
  }
  return data as T
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Restore a session from a stored token on first load.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    let active = true
    fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error('expired'))))
      .then((data) => active && setUser(data.user))
      .catch(() => {
        // Expired, tampered with, or the backend is down: drop it and stay signed out.
        localStorage.removeItem(TOKEN_KEY)
      })
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  const accept = useCallback((data: { user: User; token: string }) => {
    localStorage.setItem(TOKEN_KEY, data.token)
    setUser(data.user)
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      accept(await postJSON('/api/auth/login', { email, password }))
    },
    [accept],
  )

  const signup = useCallback(
    async (input: SignupInput) => {
      accept(
        await postJSON('/api/auth/signup', {
          first_name: input.firstName,
          last_name: input.lastName,
          email: input.email,
          password: input.password,
          confirm_password: input.confirmPassword,
        }),
      )
    },
    [accept],
  )

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
    // Tokens are stateless, so this call is courtesy only; ignore failures.
    void fetch(`${API_BASE}/api/auth/logout`, { method: 'POST' }).catch(() => {})
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, signup, logout }),
    [user, loading, login, signup, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
