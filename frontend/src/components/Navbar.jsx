import { useAuth } from 'react-oidc-context'
import { useState, useEffect } from 'react'
import { getUser } from '../api/client'

const COGNITO_DOMAIN = 'https://us-east-26f1g1ljxl.auth.us-east-2.amazoncognito.com'
const CLIENT_ID = '6prs9bt050s9t9moplarlcaho3'
const LOGOUT_URI = 'http://localhost:5173'

export default function Navbar({ onHome, currentPage, onNavigate, isAdmin }) {
  const auth = useAuth()
  const token = auth.user?.id_token
  const [balance, setBalance] = useState(null)

  const username =
    auth.user?.profile?.['cognito:username'] ||
    auth.user?.profile?.email ||
    auth.user?.profile?.sub ||
    'User'

  useEffect(() => {
    if (token && username) {
      const fetchBalance = () => {
        getUser(token, username)
          .then(u => setBalance(u.balance))
          .catch(() => {})
      }
      fetchBalance()
      const interval = setInterval(fetchBalance, 5000)
      return () => clearInterval(interval)
    }
  }, [token, username])

  const handleLogout = () => {
    auth.removeUser()
    window.location.href = `${COGNITO_DOMAIN}/logout?client_id=${CLIENT_ID}&logout_uri=${encodeURIComponent(LOGOUT_URI)}`
  }

  const navLinks = [
    { key: 'dashboard', label: 'Portfolios' },
    { key: 'market', label: 'Market' },
    ...(isAdmin ? [{ key: 'users', label: 'Users' }] : []),
  ]

  return (
    <nav style={{
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      padding: '0 24px',
      height: 56,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        <button
          onClick={onHome}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text)',
            fontSize: 16,
            fontWeight: 700,
            letterSpacing: '-0.02em',
            cursor: 'pointer',
            fontFamily: 'var(--mono)',
          }}
        >
          ◈ Portfolio Manager
        </button>

        <div style={{ display: 'flex', gap: 4 }}>
          {navLinks.map(link => (
            <button
              key={link.key}
              onClick={() => onNavigate(link.key)}
              style={{
                border: 'none',
                padding: '6px 12px',
                borderRadius: 6,
                color: currentPage === link.key ? 'var(--accent)' : 'var(--text2)',
                fontWeight: currentPage === link.key ? 600 : 400,
                fontSize: 14,
                cursor: 'pointer',
                background: currentPage === link.key ? 'rgba(79,142,247,0.1)' : 'none',
              }}
            >
              {link.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        {balance !== null && (
          <div style={{
            background: 'var(--surface2)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '4px 12px',
            fontSize: 13,
            fontFamily: 'var(--mono)',
            color: 'var(--green)',
          }}>
            ${Number(balance).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        )}
        <span style={{ color: 'var(--text2)', fontSize: 13 }}>
          {username}
        </span>
        <button className="btn btn-ghost" style={{ padding: '6px 14px' }} onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </nav>
  )
}