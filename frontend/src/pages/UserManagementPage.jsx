import { useAuth } from 'react-oidc-context'
import { useState, useEffect } from 'react'
import {
  getAllUsers,
  createUser,
  deleteUser,
  updateBalance,
  getUserTransactions,
} from '../api/client'

export default function UserManagementPage() {
  const auth = useAuth()
  const token = auth.user?.id_token

  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getAllUsers(token)
      setUsers(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchUsers() }, [])

  const handleDelete = async (username) => {
    if (!window.confirm(`Delete user ${username}? This cannot be undone.`)) return
    try {
      await deleteUser(token, username)
      setUsers(u => u.filter(x => x.username !== username))
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 className="page-title" style={{ margin: 0 }}>User Management</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          + New User
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {loading ? (
        <div className="loading">Loading users...</div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Balance</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.username}>
                  <td className="mono" style={{ fontWeight: 600 }}>{u.username}</td>
                  <td>{u.firstname} {u.lastname}</td>
                  <td className="mono" style={{ color: 'var(--green)' }}>
                    ${Number(u.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button
                        className="btn btn-ghost"
                        style={{ padding: '5px 12px', fontSize: 13 }}
                        onClick={() => setSelectedUser(u)}
                      >
                        View
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '5px 12px', fontSize: 13 }}
                        onClick={() => handleDelete(u.username)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <CreateUserModal
          token={token}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); fetchUsers() }}
        />
      )}

      {selectedUser && (
        <UserDetailModal
          token={token}
          user={selectedUser}
          onClose={() => setSelectedUser(null)}
          onUpdated={() => { setSelectedUser(null); fetchUsers() }}
        />
      )}
    </div>
  )
}

function CreateUserModal({ token, onClose, onCreated }) {
  const [form, setForm] = useState({
    username: '', password: '', firstname: '', lastname: '', balance: 10000,
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!form.username || !form.password || !form.firstname || !form.lastname) {
      setError('All fields are required.')
      return
    }
    try {
      setLoading(true)
      setError('')
      await createUser(token, form.username, form.password, form.firstname, form.lastname, Number(form.balance))
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
        <div className="modal-title">Create New User</div>
        <div className="form-group">
          <label>Username</label>
          <input value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} placeholder="e.g. johndoe" maxLength={30} />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="Password" maxLength={30} />
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>First Name</label>
            <input value={form.firstname} onChange={e => setForm({ ...form, firstname: e.target.value })} maxLength={30} />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Last Name</label>
            <input value={form.lastname} onChange={e => setForm({ ...form, lastname: e.target.value })} maxLength={30} />
          </div>
        </div>
        <div className="form-group">
          <label>Initial Balance ($)</label>
          <input type="number" value={form.balance} onChange={e => setForm({ ...form, balance: e.target.value })} min="0" step="0.01" />
        </div>
        {error && <div className="error-msg">{error}</div>}
        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating...' : 'Create User'}
          </button>
        </div>
      </div>
    </div>
  )
}

function UserDetailModal({ token, user, onClose, onUpdated }) {
  const [newBalance, setNewBalance] = useState(user.balance)
  const [transactions, setTransactions] = useState([])
  const [loadingTx, setLoadingTx] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    getUserTransactions(token, user.username)
      .then(setTransactions)
      .catch(() => setTransactions([]))
      .finally(() => setLoadingTx(false))
  }, [])

  const handleUpdateBalance = async () => {
    if (Number(newBalance) < 0) { setError('Balance cannot be negative.'); return }
    try {
      setError('')
      await updateBalance(token, user.username, Number(newBalance))
      setSuccess('Balance updated successfully!')
      setTimeout(onUpdated, 1000)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal" style={{ maxWidth: 600, maxHeight: '80vh', overflowY: 'auto' }}>
        <div className="modal-title">{user.firstname} {user.lastname} (@{user.username})</div>

        <div className="form-group">
          <label>Update Balance ($)</label>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              type="number"
              value={newBalance}
              onChange={e => setNewBalance(e.target.value)}
              min="0"
              step="0.01"
            />
            <button className="btn btn-primary" onClick={handleUpdateBalance}>
              Update
            </button>
          </div>
        </div>

        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}

        <div style={{ marginTop: 20 }}>
          <div className="section-title">Transaction History</div>
          {loadingTx ? (
            <div className="loading">Loading...</div>
          ) : transactions.length === 0 ? (
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
                    <td className="mono" style={{ color: 'var(--accent)' }}>{t.ticker}</td>
                    <td>
                      <span className={`badge badge-${t.transaction_type.toLowerCase()}`}>
                        {t.transaction_type}
                      </span>
                    </td>
                    <td className="mono">{t.quantity}</td>
                    <td className="mono">${Number(t.price).toFixed(2)}</td>
                    <td style={{ color: 'var(--text2)', fontSize: 12 }}>
                      {new Date(t.date_time).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}