import httpx
import hmac
import hashlib
import time
from typing import Optional, Dict
from datetime import datetime, timezone
import structlog

log = structlog.get_logger(__name__)

class BingXClient:
    """BingX API client for account management and trading."""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://openapi.bingx.com/openApi/spot"
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                headers={"User-Agent": "DoubleNTrading/1.0"}
            )
        return self._client
    
    def _sign_request(self, method: str, endpoint: str, params: Dict) -> Dict:
        """Sign request for BingX API."""
        timestamp = str(int(time.time() * 1000))
        params['timestamp'] = timestamp
        
        # Sort and create query string
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # Sign
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        return params
    
    async def get_account_balance(self) -> Dict:
        """Get account balance and assets."""
        try:
            params = {}
            signed = self._sign_request("GET", "/v1/user/getBalance", params)
            
            client = await self._get_client()
            r = await client.get(
                f"{self.base_url}/v1/user/getBalance",
                params=signed,
                headers={"X-BX-APIKEY": self.api_key}
            )
            r.raise_for_status()
            data = r.json()
            log.info("bingx.balance_fetched", balance=data.get('balances', []))
            return data
        except Exception as e:
            log.error("bingx.balance_fetch_failed", error=str(e))
            raise
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict:
        """Get all open orders."""
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            signed = self._sign_request("GET", "/v1/openOrders", params)
            
            client = await self._get_client()
            r = await client.get(
                f"{self.base_url}/v1/openOrders",
                params=signed,
                headers={"X-BX-APIKEY": self.api_key}
            )
            r.raise_for_status()
            data = r.json()
            log.info("bingx.open_orders_fetched", count=len(data.get('orders', [])))
            return data
        except Exception as e:
            log.error("bingx.open_orders_fetch_failed", error=str(e))
            raise
    
    async def get_trades(self, symbol: Optional[str] = None, limit: int = 50) -> Dict:
        """Get recent trades."""
        try:
            params = {'limit': limit}
            if symbol:
                params['symbol'] = symbol
            
            signed = self._sign_request("GET", "/v1/myTrades", params)
            
            client = await self._get_client()
            r = await client.get(
                f"{self.base_url}/v1/myTrades",
                params=signed,
                headers={"X-BX-APIKEY": self.api_key}
            )
            r.raise_for_status()
            data = r.json()
            log.info("bingx.trades_fetched", count=len(data.get('trades', [])))
            return data
        except Exception as e:
            log.error("bingx.trades_fetch_failed", error=str(e))
            raise
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
