#!/usr/bin/env python3
"""
DoubleN Trading Platform - Comprehensive API Test Suite
Tests all endpoints and demonstrates platform capabilities.
"""

import httpx
import json
import asyncio
from datetime import datetime

API_URL = "https://doublen-production.up.railway.app/api/v1"
TEST_EMAIL = f"test_{datetime.now().timestamp()}@example.com"
TEST_USERNAME = f"testuser_{int(datetime.now().timestamp())}"
TEST_PASSWORD = "TestPassword123!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def log_section(msg):
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}{msg}{Colors.END}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.END}\n")

async def test_auth():
    """Test authentication endpoints."""
    log_section("Testing Authentication")
    
    async with httpx.AsyncClient() as client:
        # Register
        log_info(f"Registering user: {TEST_EMAIL}")
        resp = await client.post(
            f"{API_URL}/auth/register",
            json={
                "email": TEST_EMAIL,
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
                "full_name": "Test User"
            }
        )
        if resp.status_code == 201:
            log_success("User registration successful")
            user_data = resp.json()
        else:
            log_error(f"Registration failed: {resp.status_code} - {resp.text}")
            return None
        
        # Login
        log_info("Testing login...")
        resp = await client.post(
            f"{API_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if resp.status_code == 200:
            log_success("Login successful")
            tokens = resp.json()
            access_token = tokens["access_token"]
        else:
            log_error(f"Login failed: {resp.status_code}")
            return None
        
        # Get current user
        log_info("Testing GET /auth/me...")
        resp = await client.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if resp.status_code == 200:
            log_success("Get current user successful")
        else:
            log_error(f"Get user failed: {resp.status_code}")
        
        return access_token

async def test_market_data(client):
    """Test market data endpoints."""
    log_section("Testing Market Data")
    
    # Get symbols
    log_info("Fetching supported symbols...")
    resp = await client.get(f"{API_URL}/market/symbols")
    if resp.status_code == 200:
        symbols = resp.json()["symbols"]
        log_success(f"Got {len(symbols)} supported symbols")
    else:
        log_error(f"Failed to get symbols: {resp.status_code}")
        return
    
    # Get ticker
    log_info("Fetching BTCUSDT ticker...")
    resp = await client.get(f"{API_URL}/market/ticker/BTCUSDT")
    if resp.status_code == 200:
        ticker = resp.json()
        log_success(f"BTC Price: ${ticker['price']}, Change: {ticker['price_change_pct']}%")
    else:
        log_error(f"Failed to get ticker: {resp.status_code}")
    
    # Get multiple tickers
    log_info("Fetching multiple tickers...")
    resp = await client.get(f"{API_URL}/market/tickers?symbols=BTCUSDT,ETHUSDT,SOLUSDT")
    if resp.status_code == 200:
        tickers = resp.json()
        log_success(f"Got {len(tickers)} tickers")
    else:
        log_error(f"Failed to get tickers: {resp.status_code}")
    
    # Get klines
    log_info("Fetching BTCUSDT klines (1h, 50 candles)...")
    resp = await client.get(f"{API_URL}/market/klines/BTCUSDT?interval=1h&limit=50")
    if resp.status_code == 200:
        klines = resp.json()
        log_success(f"Got {len(klines)} candles")
        if klines:
            latest = klines[-1]
            log_info(f"Latest candle: O={latest['open']} H={latest['high']} L={latest['low']} C={latest['close']}")
    else:
        log_error(f"Failed to get klines: {resp.status_code}")
    
    # Get orderbook
    log_info("Fetching BTCUSDT orderbook...")
    resp = await client.get(f"{API_URL}/market/orderbook/BTCUSDT?limit=10")
    if resp.status_code == 200:
        ob = resp.json()
        log_success(f"Got orderbook: {len(ob['bids'])} bids, {len(ob['asks'])} asks")
    else:
        log_error(f"Failed to get orderbook: {resp.status_code}")

async def test_trading_analysis(client):
    """Test trading analysis endpoints."""
    log_section("Testing Trading Analysis")
    
    # Quick trend
    log_info("Testing trend detection for BTCUSDT...")
    resp = await client.get(f"{API_URL}/trading/trend/BTCUSDT?interval=1h")
    if resp.status_code == 200:
        trend = resp.json()
        log_success(f"Trend: {trend['direction'].upper()} (strength: {trend['strength']:.1f}/100)")
    else:
        log_error(f"Failed to get trend: {resp.status_code}")
    
    # Support/Resistance
    log_info("Testing support/resistance for BTCUSDT...")
    resp = await client.get(f"{API_URL}/trading/support-resistance/BTCUSDT?interval=1h&period=20")
    if resp.status_code == 200:
        sr = resp.json()
        if sr['support'] and sr['resistance']:
            log_success(f"Support: ${sr['support']}, Resistance: ${sr['resistance']}, Pivot: ${sr['pivot']}")
        else:
            log_error("Support/Resistance returned None values")
    else:
        log_error(f"Failed to get S/R: {resp.status_code}")
    
    # Full analysis
    log_info("Testing full AI trading analysis for BTCUSDT...")
    resp = await client.get(
        f"{API_URL}/trading/analysis/BTCUSDT?interval=1h&lookback=100&account_balance=10000"
    )
    if resp.status_code == 200:
        analysis = resp.json()
        log_success("Full analysis received")
        log_info(f"  Signal: {analysis['signal']['signal'].upper()}")
        log_info(f"  Confidence: {analysis['signal']['confidence']}%")
        log_info(f"  Reasoning: {analysis['signal']['reasoning']}")
        log_info(f"  Stop Loss: ${analysis['risk_management']['stop_loss']}")
        log_info(f"  Take Profit (2x): ${analysis['risk_management']['take_profit_2x']}")
        log_info(f"  Take Profit (3x): ${analysis['risk_management']['take_profit_3x']}")
    else:
        log_error(f"Failed to get analysis: {resp.status_code} - {resp.text}")

async def test_watchlist(client, token):
    """Test watchlist endpoints."""
    log_section("Testing Watchlist")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add to watchlist
    log_info("Adding BTCUSDT to watchlist...")
    resp = await client.post(
        f"{API_URL}/watchlist",
        json={"symbol": "BTCUSDT"},
        headers=headers
    )
    if resp.status_code == 201:
        item = resp.json()
        log_success("Added to watchlist")
        item_id = item["id"]
    else:
        log_error(f"Failed to add: {resp.status_code}")
        return
    
    # Get watchlist
    log_info("Fetching watchlist...")
    resp = await client.get(f"{API_URL}/watchlist", headers=headers)
    if resp.status_code == 200:
        items = resp.json()
        log_success(f"Watchlist has {len(items)} items")
        for item in items:
            log_info(f"  - {item['symbol']}: ${item.get('price', 'N/A')}")
    else:
        log_error(f"Failed to get watchlist: {resp.status_code}")
    
    # Remove from watchlist
    log_info("Removing from watchlist...")
    resp = await client.delete(f"{API_URL}/watchlist/{item_id}", headers=headers)
    if resp.status_code == 204:
        log_success("Removed from watchlist")
    else:
        log_error(f"Failed to remove: {resp.status_code}")

async def test_health(client):
    """Test health check."""
    log_section("Testing Health Check")
    
    resp = await client.get("https://doublen-production.up.railway.app/health")
    if resp.status_code == 200:
        health = resp.json()
        log_success(f"API Status: {health['status']}")
        log_info(f"  Binance: {health['binance']}")
        log_info(f"  Version: {health['version']}")
        log_info(f"  Environment: {health['env']}")
    else:
        log_error(f"Health check failed: {resp.status_code}")

async def main():
    """Run all tests."""
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════════╗")
    print(f"║  DoubleN Trading Platform - API Test Suite                  ║")
    print(f"║  Testing against: {API_URL.replace('https://', '').replace('/api/v1', ''):<36}║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    async with httpx.AsyncClient() as client:
        # Test health first
        await test_health(client)
        
        # Test auth and get token
        token = await test_auth()
        if not token:
            log_error("Authentication failed, cannot continue tests")
            return
        
        # Test market data
        await test_market_data(client)
        
        # Test trading analysis
        await test_trading_analysis(client)
        
        # Test watchlist
        await test_watchlist(client, token)
    
    print(f"\n{Colors.GREEN}✓ All tests completed!{Colors.END}\n")

if __name__ == "__main__":
    asyncio.run(main())
