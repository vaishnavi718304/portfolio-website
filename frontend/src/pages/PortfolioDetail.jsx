import { useAuth } from 'react-oidc-context'
import { useState, useEffect } from 'react'
import {
  getPortfolio,
  getPortfolioTransactions,
  buyStock,
  sellStock,
  grantAccess,
  revokeAccess,
} from '../api/client'

export default function PortfolioDetail({ portfolioId, onBack }) {
  const auth = useAuth()
  const token = auth.user?.id_token
  const username =
    auth.user?.profile?.['cognito:username'] ||
    auth.user?.profile?.email ||
    auth.user?.profile?.sub

  const [portfolio, setPortfolio] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('holdings')
  const [showBuy, setShowBuy] = useState(false)
  const [showSell, setShowSell] = useState(null)

  const fetchAll = async () => {
    try {
      setLoading(true)
      setError('')
      const [p, t] = await Promise.all([
        getPortfolio(token, portfolioId),
        getPortfolioTransactions(token, portfolioId),
      ])
      setPortfolio(p)
      setTransactions(t)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [portfolioId])

  if (loading) return <div className="loading">Loading portfolio...</div>
  if (error) return <div className="error-msg">{error}</div>
  if (!portfolio) return null

  const holdings = portfolio.investments || []
  const isOwner = portfolio.owner === username
  const accessGrants = portfolio.access_grants || []

  const tabs = ['holdings', 'transactions']
  if (isOwner) tabs.push('access')

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button className="btn btn-ghost" style={{ padding: '6px 12px' }} onClick={onBack}>
          ← Back
        </button>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700 }}>{portfolio.name}</h1>
          <p style={{ color: 'var(--text2)', fontSize: 13 }}>
            {portfolio.description}
            <span style={{ marginLeft: 10, color: 'var(--accent)', fontSize: 12 }}>
              Owner: {portfolio.owner}
            </span>
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: 'none',
              border: 'none',
              padding: '8px 16px',
              color: activeTab === tab ? 'var(--accent)' : 'var(--text2)',
              fontWeight: activeTab === tab ? 600 : 400,
              borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
              fontSize: 14,
              textTransform: 'capitalize',
              marginBottom: -1,
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'holdings' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
            <button className="btn btn-green" onClick={() => setShowBuy(true)}>
              + Buy
            </button>
          </div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            {holdings.length === 0 ? (
              <div className="empty">No holdings yet. Place a buy order to get started.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Quantity</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map(h => (
                    <tr key={h.id}>
                      <td className="mono" style={{ fontWeight: 600, color: 'var(--accent)' }}>
                        {h.ticker}
                      </td>
                      <td className="mono">{h.quantity}</td>
                      <td>
                        <button
                          className="btn btn-red"
                          style={{ padding: '5px 12px', fontSize: 13 }}
                          onClick={() => setShowSell(h)}
                        >
                          Sell
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {transactions.length === 0 ? (
            <div className="empty">No transactions yet.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Type</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(t => (
                  <tr key={t.transaction_id}>
                    <td className="mono" style={{ fontWeight: 600, color: 'var(--accent)' }}>
                      {t.ticker}
                    </td>
                    <td>
                      <span className={`badge badge-${t.transaction_type.toLowerCase()}`}>
                        {t.transaction_type}
                      </span>
                    </td>
                    <td className="mono">{t.quantity}</td>
                    <td className="mono">${Number(t.price).toFixed(2)}</td>
                    <td style={{ color: 'var(--text2)', fontSize: 13 }}>
                      {new Date(t.date_time).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'access' && isOwner && (
        <AccessTab
          token={token}
          portfolioId={portfolioId}
          accessGrants={accessGrants}
          onRefresh={fetchAll}
        />
      )}

      {showBuy && (
        <BuyModal
          token={token}
          portfolioId={portfolioId}
          onClose={() => setShowBuy(false)}
          onDone={() => { setShowBuy(false); fetchAll() }}
        />
      )}

      {showSell && (
        <SellModal
          token={token}
          portfolioId={portfolioId}
          holding={showSell}
          onClose={() => setShowSell(null)}
          onDone={() => { setShowSell(null); fetchAll() }}
        />
      )}
    </div>
  )
}

function AccessTab({ token, portfolioId, accessGrants, onRefresh }) {
  const [username, setUsername] = useState('')
  const [role, setRole] = useState('viewer')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGrant = async () => {
    if (!username.trim()) { setError('Username is required.'); return }
    try {
      setLoading(true)
      setError('')
      await grantAccess(token, portfolioId, username.trim(), role)
      setSuccess(`Access granted to ${username} as ${role}`)
      setUsername('')
      onRefresh()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRevoke = async (u) => {
    if (!window.confirm(`Revoke access for ${u}?`)) return
    try {
      await revokeAccess(token, portfolioId, u)
      onRefresh()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="section-title">Grant Access</div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label>Username</label>
            <input
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="e.g. testuser"
            />
          </div>
          <div style={{ width: 140 }}>
            <label>Role</label>
            <select value={role} onChange={e => setRole(e.target.value)}>
              <option value="viewer">Viewer</option>
              <option value="manager">Manager</option>
            </select>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGrant}
            disabled={loading}
          >
            Grant
          </button>
        </div>
        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <span className="section-title" style={{ margin: 0 }}>Current Access</span>
        </div>
        {accessGrants.length === 0 ? (
          <div className="empty">No access grants yet.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {accessGrants.map(a => (
                <tr key={a.username}>
                  <td className="mono">{a.username}</td>
                  <td>
                    <span className="badge" style={{
                      background: a.role === 'manager' ? 'rgba(79,142,247,0.15)' : 'rgba(139,144,167,0.15)',
                      color: a.role === 'manager' ? 'var(--accent)' : 'var(--text2)',
                    }}>
                      {a.role}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '5px 12px', fontSize: 13 }}
                      onClick={() => handleRevoke(a.username)}
                    >
                      Revoke
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function BuyModal({ token, portfolioId, onClose, onDone }) {
  const [ticker, setTicker] = useState('')
  const [quantity, setQuantity] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleBuy = async () => {
    if (!ticker.trim() || !quantity) { setError('Ticker and quantity are required.'); return }
    const qty = parseInt(quantity, 10)
    if (isNaN(qty) || qty <= 0) { setError('Quantity must be a whole number greater than 0.'); return }
    try {
      setLoading(true)
      setError('')
      await buyStock(token, portfolioId, ticker.trim().toUpperCase(), qty)
      setSuccess(`Successfully bought ${qty} shares of ${ticker.toUpperCase()}`)
      setTimeout(onDone, 1200)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-title">Place Buy Order</div>
        <div className="form-group">
          <label>Ticker Symbol</label>
          <input
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g. AAPL"
            maxLength={10}
          />
        </div>
        <div className="form-group">
          <label>Quantity (whole numbers only)</label>
          <input
            type="number"
            value={quantity}
            onChange={e => setQuantity(e.target.value)}
            placeholder="e.g. 10"
            min="1"
            step="1"
          />
        </div>
        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-green" onClick={handleBuy} disabled={loading}>
            {loading ? 'Placing order...' : 'Buy'}
          </button>
        </div>
      </div>
    </div>
  )
}

function SellModal({ token, portfolioId, holding, onClose, onDone }) {
  const [quantity, setQuantity] = useState('')
  const [salePrice, setSalePrice] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSell = async () => {
    if (!quantity || !salePrice) { setError('Quantity and sale price are required.'); return }
    const qty = parseInt(quantity, 10)
    if (isNaN(qty) || qty <= 0) { setError('Quantity must be a whole number greater than 0.'); return }
    if (qty > holding.quantity) { setError(`You only have ${holding.quantity} shares.`); return }
    if (Number(salePrice) <= 0) { setError('Sale price must be greater than 0.'); return }
    try {
      setLoading(true)
      setError('')
      await sellStock(token, portfolioId, holding.ticker, qty, Number(salePrice))
      setSuccess(`Successfully sold ${qty} shares of ${holding.ticker}`)
      setTimeout(onDone, 1200)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-title">
          Sell {holding.ticker}
          <span style={{ color: 'var(--text2)', fontWeight: 400, fontSize: 14, marginLeft: 8 }}>
            ({holding.quantity} available)
          </span>
        </div>
        <div className="form-group">
          <label>Quantity to Sell (whole numbers only)</label>
          <input
            type="number"
            value={quantity}
            onChange={e => setQuantity(e.target.value)}
            placeholder={`Max ${holding.quantity}`}
            min="1"
            max={holding.quantity}
            step="1"
          />
        </div>
        <div className="form-group">
          <label>Sale Price per Share ($)</label>
          <input
            type="number"
            value={salePrice}
            onChange={e => setSalePrice(e.target.value)}
            placeholder="e.g. 150.00"
            min="0.01"
            step="0.01"
          />
        </div>
        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-red" onClick={handleSell} disabled={loading}>
            {loading ? 'Selling...' : 'Sell'}
          </button>
        </div>
      </div>
    </div>
  )
}