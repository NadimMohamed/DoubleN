import hmac
import hashlib
import time
from typing import Optional, Dict, Any
import httpx
import structlog
from app.core.config import settings

log = structlog.get_logger(__name__)

class BingXClient:
    """BingX API client for account management and trading"""
    
    BASE_URL = "https://api-gw-trading.bingx.com"
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=httpx.Timeout(10.0),
                headers={"User-Agent": "DoubleNTrading/1.0"}
            )
        return self._client
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """Sign request parameters with API secret"""
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance and wallet information"""
        timestamp = int(time.time() * 1000)
        params = {
            "timestamp": timestamp,
            "apiKey": self.api_key
        }
        signature = self._sign_request(params)
        
        try:
            client = await self._get_client()
            response = await client.get(
                "/openApi/spot/v1/account/getBalance",
                params={**params, "signature": signature}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error("bingx.get_balance_failed", error=str(e))
            raise
    
    async def get_open_positions(self) -> list:
        """Get all open trading positions"""
        timestamp = int(time.time() * 1000)
        params = {
            "timestamp": timestamp,
            "apiKey": self.api_key
        }
        signature = self._sign_request(params)
        
        try:
            client = await self._get_client()
            response = await client.get(
                "/openApi/spot/v1/trade/openOrders",
                params={**params, "signature": signature}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error("bingx.get_positions_failed", error=str(e))
            raise
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
