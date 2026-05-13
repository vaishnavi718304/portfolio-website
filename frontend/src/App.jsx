import { useAuth } from 'react-oidc-context'
import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import PortfolioDetail from './pages/PortfolioDetail'
import MarketPage from './pages/MarketPage'
import UserManagementPage from './pages/UserManagementPage'
import Navbar from './components/Navbar'

export default function App() {
  const auth = useAuth()
  const [currentPortfolioId, setCurrentPortfolioId] = useState(null)
  const [currentPage, setCurrentPage] = useState('dashboard')

  const username =
    auth.user?.profile?.['cognito:username'] ||
    auth.user?.profile?.email ||
    auth.user?.profile?.sub

  const isAdmin = username === 'admin'

  if (auth.isLoading) {
    return <div className="loading">Loading...</div>
  }

  if (auth.error) {
    return (
      <div className="loading" style={{ flexDirection: 'column', gap: 12 }}>
        <span>Authentication error: {auth.error.message}</span>
        <button className="btn btn-primary" onClick={() => auth.signinRedirect()}>
          Try Again
        </button>
      </div>
    )
  }

  if (!auth.isAuthenticated) {
    return <LoginPage />
  }

  const handleHome = () => {
    setCurrentPage('dashboard')
    setCurrentPortfolioId(null)
  }

  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar
        onHome={handleHome}
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        isAdmin={isAdmin}
      />
      <main style={{ maxWidth: 1000, margin: '0 auto', padding: '32px 20px' }}>
        {currentPage === 'dashboard' && !currentPortfolioId && (
          <Dashboard onSelectPortfolio={(id) => {
            setCurrentPortfolioId(id)
            setCurrentPage('portfolio')
          }} />
        )}
        {currentPage === 'portfolio' && currentPortfolioId && (
          <PortfolioDetail
            portfolioId={currentPortfolioId}
            onBack={handleHome}
          />
        )}
        {currentPage === 'market' && <MarketPage />}
        {currentPage === 'users' && isAdmin && <UserManagementPage />}
        {currentPage === 'users' && !isAdmin && (
          <div className="card empty">
            Access denied. Admin only.
          </div>
        )}
      </main>
    </div>
  )
}