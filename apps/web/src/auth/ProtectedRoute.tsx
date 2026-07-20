import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function ProtectedRoute() {
  const { token, loading } = useAuth()
  if (loading) {
    return (
      <div className="grid min-h-screen place-items-center text-[var(--muted)]">
        Loading…
      </div>
    )
  }
  if (!token) return <Navigate to="/login" replace />
  return <Outlet />
}
