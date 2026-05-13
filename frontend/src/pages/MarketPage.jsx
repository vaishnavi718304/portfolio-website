import { useAuth } from 'react-oidc-context'
import { useState } from 'react'
import { getSecurity } from '../api/client'

export default function MarketPage() {
  const auth = useAuth()
  const token = auth.user?.id_token

  const [ticker, setTicker] = useState('')
  const [quote, setQuote] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async () => {
    if (!ticker.trim()) { setError('Enter a ticker symbol.'); return }
    try {
      setLoading(true)
      setError('')
      setQuote(null)
      const data = await getSecurity(token, ticker.trim().toUpperCase())
      setQuote(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Market Lookup</h1>
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            placeholder="Enter ticker e.g. AAPL"
            maxLength={10}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            style={{ flex: 1 }}
          />
          <button
            className="btn btn-primary"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {error && <div className="error-msg">{error}</div>}
      </div>

      {quote && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>
                {quote.ticker}
              </div>
              <div style={{ color: 'var(--text2)', fontSize: 14 }}>{quote.issuer}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 32, fontWeight: 700, color: 'var(--green)' }}>
                ${Number(quote.price).toFixed(2)}
              </div>
              <div style={{ color: 'var(--text2)', fontSize: 12 }}>Last updated: {quote.date}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}