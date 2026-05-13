import { useAuth } from 'react-oidc-context'
import { useState, useEffect } from 'react'
import { getPortfolios, createPortfolio, deletePortfolio } from '../api/client'

export default function Dashboard({ onSelectPortfolio }) {
  const auth = useAuth()
  const token = auth.user?.id_token
  const username =
    auth.user?.profile?.['cognito:username'] ||
    auth.user?.profile?.email ||
    auth.user?.profile?.sub

  const [portfolios, setPortfolios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const fetchPortfolios = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getPortfolios(token)
      setPortfolios(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchPortfolios() }, [])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this portfolio? It must have no holdings.')) return
    try {
      await deletePortfolio(token, id)
      setPortfolios(p => p.filter(x => x.id !== id))
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 className="page-title" style={{ margin: 0 }}>My Portfolios</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          + New Portfolio
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {loading ? (
        <div className="loading">Loading portfolios...</div>
      ) : portfolios.length === 0 ? (
        <div className="card empty">
          No portfolios yet. Create your first one!
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {portfolios.map(p => (
            <div
              key={p.id}
              className="card"
              style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              onClick={() => onSelectPortfolio(p.id)}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>{p.name}</div>
                <div style={{ color: 'var(--text2)', fontSize: 13 }}>{p.description}</div>
              </div>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <span style={{ color: 'var(--text2)', fontSize: 12, fontFamily: 'var(--mono)' }}>
                  #{p.id}
                </span>
                {p.owner === username && (
                  <button
                    className="btn btn-danger"
                    style={{ padding: '6px 12px', fontSize: 13 }}
                    onClick={(e) => handleDelete(p.id, e)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreatePortfolioModal
          username={username}
          token={token}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); fetchPortfolios() }}
        />
      )}
    </div>
  )
}

function CreatePortfolioModal({ username, token, onClose, onCreated }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!name.trim() || !description.trim()) {
      setError('Name and description are required.')
      return
    }
    try {
      setLoading(true)
      setError('')
      await createPortfolio(token, username, name.trim(), description.trim())
      onCreated()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-title">New Portfolio</div>
        <div className="form-group">
          <label>Name</label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. Tech Growth"
            maxLength={30}
          />
        </div>
        <div className="form-group">
          <label>Description</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="What's this portfolio for?"
            maxLength={500}
            rows={3}
            style={{ resize: 'vertical' }}
          />
        </div>
        {error && <div className="error-msg">{error}</div>}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating...' : 'Create Portfolio'}
          </button>
        </div>
      </div>
    </div>
  )
}
