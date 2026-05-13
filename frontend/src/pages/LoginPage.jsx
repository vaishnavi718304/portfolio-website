import { useAuth } from 'react-oidc-context'

export default function LoginPage() {
  const auth = useAuth()

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg)',
    }}>
      <div style={{ textAlign: 'center', maxWidth: 400 }}>
        <div style={{
          fontFamily: 'var(--mono)',
          fontSize: 32,
          fontWeight: 700,
          marginBottom: 8,
          color: 'var(--accent)',
        }}>
          ◈ Portfolio Manager
        </div>
        <p style={{ color: 'var(--text2)', marginBottom: 32, fontSize: 15 }}>
          Manage your investment portfolios
        </p>
        <button
          className="btn btn-primary"
          style={{ padding: '12px 32px', fontSize: 15, width: '100%' }}
          onClick={() => auth.signinRedirect()}
        >
          Sign in with Cognito
        </button>
      </div>
    </div>
  )
}
