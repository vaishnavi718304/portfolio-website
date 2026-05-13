const BASE_URL = 'http://localhost:5001'

async function request(path, options = {}, token) {
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    const message = data?.detail || data?.error || `Request failed (${res.status})`
    throw new Error(message)
  }

  return data
}

// Portfolios
export const getPortfolios = (token) =>
  request('/portfolios/', {}, token)

export const createPortfolio = (token, username, name, description) =>
  request('/portfolios/', {
    method: 'POST',
    body: JSON.stringify({ username, name, description }),
  }, token)

export const deletePortfolio = (token, portfolioId) =>
  request(`/portfolios/${portfolioId}`, { method: 'DELETE' }, token)

export const getPortfolio = (token, portfolioId) =>
  request(`/portfolios/${portfolioId}`, {}, token)

// Transactions
export const getPortfolioTransactions = (token, portfolioId) =>
  request(`/portfolios/${portfolioId}/transactions`, {}, token)

// Trades
export const buyStock = (token, portfolioId, ticker, quantity) =>
  request('/trades/buy', {
    method: 'POST',
    body: JSON.stringify({ portfolio_id: portfolioId, ticker, quantity }),
  }, token)

export const sellStock = (token, portfolioId, ticker, quantity, salePrice) =>
  request('/trades/sell', {
    method: 'POST',
    body: JSON.stringify({
      portfolio_id: portfolioId,
      ticker,
      quantity,
      sale_price: salePrice,
    }),
  }, token)

// Users
export const getUser = (token, username) =>
  request(`/users/${username}`, {}, token)

export const getAllUsers = (token) =>
  request('/users/', {}, token)

export const createUser = (token, username, password, firstname, lastname, balance) =>
  request('/users/', {
    method: 'POST',
    body: JSON.stringify({ username, password, firstname, lastname, balance }),
  }, token)

export const deleteUser = (token, username) =>
  request(`/users/${username}`, { method: 'DELETE' }, token)

export const updateBalance = (token, username, new_balance) =>
  request('/users/update-balance', {
    method: 'PUT',
    body: JSON.stringify({ username, new_balance }),
  }, token)

export const getUserTransactions = (token, username) =>
  request(`/users/${username}/transactions`, {}, token)

// Securities
export const getSecurity = (token, ticker) =>
  request(`/securities/${ticker}`, {}, token)

// Portfolio Access
export const grantAccess = (token, portfolioId, username, role) =>
  request(`/portfolios/${portfolioId}/access`, {
    method: 'POST',
    body: JSON.stringify({ username, role }),
  }, token)

export const revokeAccess = (token, portfolioId, username) =>
  request(`/portfolios/${portfolioId}/access/${username}`, {
    method: 'DELETE',
  }, token)