# Double N Trading API Documentation

## Base URL
```
https://api.doublen.app/api/v1
```

## Authentication
All protected endpoints require:
```
Authorization: Bearer <access_token>
```

## Market Data Endpoints

### GET /market/ticker/{symbol}
Get 24h ticker data
```
curl https://api.doublen.app/api/v1/market/ticker/BTCUSDT
```
Response:
```json
{
  "symbol": "BTCUSDT",
  "price": 45000.00,
  "price_change": 500.00,
  "price_change_pct": 1.12,
  "high_24h": 45800.00,
  "low_24h": 44200.00,
  "volume": 12345.6789,
  "quote_volume": 555555555.55,
  "open_price": 44500.00,
  "last_updated": "2024-01-01T00:00:00Z",
  "data_source": "binance"
}
```

### GET /market/klines/{symbol}
Get OHLCV candlestick data
```
curl "https://api.doublen.app/api/v1/market/klines/BTCUSDT?interval=1h&limit=100"
```

### GET /analysis/{symbol}
Get AI trading analysis with signal
```
curl https://api.doublen.app/api/v1/analysis/BTCUSDT
```
Response:
```json
{
  "symbol": "BTCUSDT",
  "current_price": 45000.00,
  "signal": {
    "signal": "buy",
    "confidence": 82,
    "reasoning": "RSI oversold | MACD bullish"
  },
  "trend": {
    "direction": "bullish",
    "strength": 75
  },
  "support_resistance": {
    "support": 44200.00,
    "resistance": 45800.00
  },
  "indicators": {
    "rsi": 28.5,
    "macd": 0.0045,
    "macd_signal": 0.0040,
    "ema_12": 44950.00,
    "ema_26": 44850.00,
    "atr": 350.00
  }
}
```

## Notification Endpoints

### POST /notifications
Create a notification (auth required)
```
curl -X POST https://api.doublen.app/api/v1/notifications \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "price_alert",
    "title": "Price Alert: BTC",
    "message": "Bitcoin price crossed $45,000",
    "symbol": "BTCUSDT"
  }'
```

### GET /notifications
Get user notifications (auth required)
```
curl https://api.doublen.app/api/v1/notifications \
  -H "Authorization: Bearer <token>"
```

### POST /notifications/mark-as-read
Mark notifications as read
```
curl -X POST https://api.doublen.app/api/v1/notifications/mark-as-read \
  -H "Authorization: Bearer <token>" \
  -d '{"notification_ids": ["id1", "id2"]}'
```

## Error Responses

All errors follow a standard format:
```json
{
  "detail": "Error message",
  "request_id": "unique-request-id"
}
```

Status codes:
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 503: Service unavailable (Binance/CoinGecko down)

## Rate Limiting

- 60 requests per minute per IP
- Headers:
  - `X-RateLimit-Limit: 60`
  - `X-RateLimit-Remaining: 59`
  - `X-RateLimit-Reset: 1234567890`

## Examples

### Get Bitcoin price
```bash
curl https://api.doublen.app/api/v1/market/ticker/BTCUSDT | jq .price
```

### Get AI trading signal
```bash
curl https://api.doublen.app/api/v1/analysis/ETHUSDT | jq '.signal.signal'
```

### Subscribe to price alerts
```bash
curl -X POST https://api.doublen.app/api/v1/notifications \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "price_alert",
    "title": "Alert",
    "message": "BTC crossed $45k",
    "symbol": "BTCUSDT"
  }'
```
