# Double N Trading - Deployment Guide

## Architecture Overview

### Backend (FastAPI)
- Python 3.12, async SQLAlchemy
- Market data from Binance REST API + CoinGecko fallback
- Technical analysis engine (TA calculations)
- AI signal generation service
- PostgreSQL for persistence
- Redis for ticker caching

### Frontend (Next.js 14)
- React 18, TypeScript
- Real-time market updates via React Query
- Session management with proactive token refresh
- Error boundaries for graceful failure handling
- Responsive Tailwind CSS design

### Database (PostgreSQL)
- User authentication & profiles
- Watchlist items
- Notifications with auto-expiry
- Proper indexing on frequently-queried fields

## Deployment Steps

### 1. Environment Setup
```bash
# Backend environment variables
SECRET_KEY=<64-char random string>
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>
REDIS_URL=redis://<host>:6379/0
BINANCE_BASE_URL=https://api.binance.com
USE_COINGECKO_FALLBACK=true
REQUIRE_LIVE_DATA=true
```

### 2. Database Migration
```bash
# SSH into backend service
cd /app
alembic upgrade head
```

This creates:
- users table
- watchlist_items table
- **notifications table** (NEW)

### 3. Deploy Services
```bash
# Backend
docker build -f backend/Dockerfile -t doublen-backend:latest backend/
docker run -p 8000:8000 doublen-backend:latest

# Frontend
npm run build
npm start
```

### 4. Verification
```bash
# Check health
curl https://api.doublen.app/health

# Test API
curl https://api.doublen.app/api/docs

# Verify notifications
curl -H "Authorization: Bearer <token>" https://api.doublen.app/api/v1/notifications
```

## Features Checklist

### Real Data Sources
- ✅ Binance REST API (primary)
- ✅ CoinGecko (fallback)
- ✅ Error on both fail (never mock data)

### Technical Analysis
- ✅ SMA (Simple Moving Average)
- ✅ RSI (Relative Strength Index)
- ✅ MACD (Moving Average Convergence Divergence)
- ✅ EMA (Exponential Moving Average 12/26)
- ✅ ATR (Average True Range)
- ✅ Support/Resistance levels

### AI Trading Signals
- ✅ BUY/SELL/NEUTRAL determination
- ✅ Confidence scoring (0-95%)
- ✅ Reasoning explanation
- ✅ Trend analysis (bullish/bearish/neutral)

### Notifications
- ✅ 8 alert types
- ✅ Database persistence
- ✅ Auto-expiry (24h default)
- ✅ Mark as read
- ✅ Clear old notifications
- ✅ Unread count

### Frontend
- ✅ Real-time market data
- ✅ Dashboard with analysis card
- ✅ Trading page with risk calculator
- ✅ Watchlist with AI signals
- ✅ Notification center
- ✅ Settings page
- ✅ Session persistence
- ✅ Error boundaries

## Performance Optimizations

- Redis caching (2s in-memory, 5s in Redis)
- React Query stale-while-revalidate
- Request deduplication
- Proper HTTP caching headers
- Error boundary for render errors
- Token refresh 5 min before expiry

## Monitoring

Check deployment status:
```bash
# Railway Dashboard
https://railway.com/project/<project-id>

# Health check
GET /health

# API docs
GET /api/docs

# Logs
tail -f deployment.log
```

## Troubleshooting

### Build Fails
- Check Docker/base image
- Verify requirements.txt syntax
- Ensure SECRET_KEY is set

### Deploy Fails
- Check DATABASE_URL format
- Verify Redis connectivity
- Review build logs for errors

### API Errors (503)
- Binance and CoinGecko both down
- Check internet connectivity
- Review service logs

## Future Enhancements

- Phase 12: BingX exchange integration
- Phase 13: Position analyzer
- Phase 14: Advanced chart features (timeframes, indicators)
- Phase 15: Trading workstation (4-panel layout)
