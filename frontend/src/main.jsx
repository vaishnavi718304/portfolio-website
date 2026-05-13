import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthProvider } from 'react-oidc-context'
import App from './App'
import './index.css'

const cognitoAuthConfig = {
  authority: 'https://cognito-idp.us-east-2.amazonaws.com/us-east-2_6f1g1Ljxl',
  client_id: '6prs9bt050s9t9moplarlcaho3',
  redirect_uri: 'http://localhost:5173/callback',
  response_type: 'code',
  scope: 'openid email',
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname)
  },
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>
)
