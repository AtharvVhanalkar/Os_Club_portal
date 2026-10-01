import { useCallback, useEffect, useMemo, useState } from 'react'
import { api, tokenStore } from '../api/client.js'
import { AuthContext } from './auth.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(tokenStore.get()))

  // Restore the logged-in user when the page loads.
  useEffect(() => {
    if (!tokenStore.get()) return
    api
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false))
  }, [])

  const handleAuth = useCallback(({ token, user: nextUser }) => {
    tokenStore.set(token)
    setUser(nextUser)
    return nextUser
  }, [])

  const login = useCallback((email, password) => api.login({ email, password }).then(handleAuth), [handleAuth])
  const register = useCallback((payload) => api.register(payload).then(handleAuth), [handleAuth])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } finally {
      tokenStore.clear()
      setUser(null)
    }
  }, [])

  const value = useMemo(() => ({ user, loading, login, register, logout }), [user, loading, login, register, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
