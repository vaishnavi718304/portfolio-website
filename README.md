# Portfolio Management Application

Full-stack investment portfolio management app with Flask backend and React frontend.

## Project Structure

```
portfolio-website/
├── app/                  # Flask backend
│   ├── auth/             # JWT authentication (Cognito)
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # API route blueprints
│   ├── schemas/          # Pydantic request validation
│   └── service/          # Business logic layer
├── tests/                # pytest test suite
├── frontend/             # React frontend (Assignment 5)
│   └── src/
│       ├── api/          # Backend API client
│       ├── components/   # Shared UI components
│       └── pages/        # Page-level components
├── .env.example          # Required environment variables
└── requirements.txt
```

## Backend Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
```
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/portfolio_db
ALPHA_VANTAGE_API_KEY=your_key
COGNITO_REGION=us-east-2
COGNITO_USER_POOL_ID=us-east-2_XXXXXXXXX
COGNITO_APP_CLIENT_ID=your_client_id
COGNITO_DOMAIN=https://your-domain.auth.us-east-2.amazoncognito.com
```

### 3. Run the backend
```bash
flask run
# Runs on http://localhost:5000
```

### 4. Run tests
```bash
pytest --cov=app tests/
```

## Frontend Setup

### 1. Install dependencies
```bash
cd frontend
npm install
```

### 2. Run the frontend
```bash
npm run dev
# Runs on http://localhost:5173
```

## AWS Cognito Setup

1. Create a User Pool in AWS Cognito (us-east-2)
2. Create an App Client (SPA type)
3. Set Callback URL: `http://localhost:5173/callback`
4. Set Logout URL: `http://localhost:5173`
5. Enable scopes: `openid`, `email`
6. Copy User Pool ID and Client ID to your `.env`

## Features

- **Authentication**: OIDC Authorization Code Flow via AWS Cognito Hosted UI
- **Portfolios**: View, create, and delete portfolios
- **Holdings**: View current investment positions per portfolio
- **Trading**: Place buy and sell orders (partial and full liquidation)
- **Transactions**: Full transaction history per portfolio
