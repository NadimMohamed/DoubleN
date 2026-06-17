# Double N Trading — Phase 1

Real-time cryptocurrency trading platform with live Binance market data.

## Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy (async) |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Charts** | lightweight-charts (OHLCV from Binance klines) |
| **Real-time** | WebSocket → Binance streams → frontend |
| **Auth** | JWT (access + refresh tokens), bcrypt passwords |
| **Deployment** | Docker Compose / Railway |

## Phase 1 Features

- ✅ User registration and login with JWT auth
- ✅ Live BTCUSDT, ETHUSDT, LTCUSDT, SOLUSDT prices from Binance
- ✅ Real-time price streaming via WebSocket
- ✅ Interactive OHLCV candlestick chart (lightweight-charts)
- ✅ Watchlist — add/remove up to 20 symbols with live prices
- ✅ Auto token refresh on expiry
- ✅ Protected routes

## Quick Start

### Option 1: Docker Compose (recommended)

```bash
# 1. Clone and configure
git clone <repo>
cd double-n-trading
cp .env.example .env

# 2. Edit .env — set SECRET_KEY and POSTGRES_PASSWORD
#    Generate a secret key:
make gen-secret

# 3. Start everything
make up

# 4. Run migrations (first time only)
make migrate
```

Open http://localhost:3000 — register an account and start using the app.

### Option 2: Local development (without Docker)

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit as needed
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `.env.example` to `.env` and set:

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | 64-char random string for JWT signing |
| `POSTGRES_PASSWORD` | ✅ | PostgreSQL password |
| `BINANCE_API_KEY` | ❌ | Not needed for Phase 1 (public endpoints only) |
| `BINANCE_API_SECRET` | ❌ | Not needed for Phase 1 |

## API Reference

Base URL: `http://localhost:8000/api/v1`
Interactive docs: `http://localhost:8000/api/docs`

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | — | Create account |
| POST | `/auth/login` | — | Login, receive JWT tokens |
| POST | `/auth/refresh` | — | Refresh access token |
| GET | `/auth/me` | ✅ | Get current user |

### Market Data (live from Binance)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/market/ticker/{symbol}` | — | 24h ticker |
| GET | `/market/tickers?symbols=BTCUSDT,ETHUSDT` | — | Multiple tickers |
| GET | `/market/klines/{symbol}?interval=1h` | — | OHLCV candles |
| GET | `/market/orderbook/{symbol}` | — | Order book |
| GET | `/market/symbols` | — | Supported symbols |

### Watchlist

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/watchlist` | ✅ | Get watchlist with live prices |
| POST | `/watchlist` | ✅ | Add symbol |
| DELETE | `/watchlist/{id}` | ✅ | Remove symbol |

### WebSocket

```
ws://localhost:8000/ws/ticker/{symbol}
```
Sends real-time price updates from Binance miniTicker stream.

## Running Tests

```bash
make test           # All tests
make test-unit      # Unit tests only
make test-cov       # With coverage report
```

## Deployment on Railway

1. Create a Railway project
2. Add services: PostgreSQL plugin + Redis plugin
3. Deploy backend:
   - Root directory: `backend/`
   - Build: `Dockerfile`
   - Start: `sh -c 'alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT'`
4. Set environment variables from `.env.example`
5. Deploy frontend:
   - Root directory: `frontend/`
   - Build: `npm run build`
   - Start: `npm start`
   - Set `NEXT_PUBLIC_API_URL` to your backend Railway URL

## Project Structure

```
double-n-trading/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # auth.py, market.py, watchlist.py
│   │   ├── core/               # config.py, security.py
│   │   ├── db/                 # session.py
│   │   ├── models/             # user.py, watchlist.py
│   │   ├── schemas/            # auth.py, market.py
│   │   ├── services/           # auth.py, binance.py, watchlist.py
│   │   ├── websockets/         # manager.py, routes.py
│   │   └── main.py
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Unit + integration tests
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/                # Next.js App Router pages
│       ├── components/         # React components
│       ├── hooks/              # useTickerStream (WebSocket)
│       ├── lib/                # api.ts, utils.ts
│       ├── store/              # authStore (Zustand)
│       └── types/              # TypeScript types
├── nginx/nginx.conf
├── docker-compose.yml
├── Makefile
└── .env.example
```
