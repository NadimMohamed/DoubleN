"""Rate limiting middleware using Redis."""
import redis
from fastapi import Request, HTTPException, status
import structlog
from app.core.config import settings

log = structlog.get_logger(__name__)

class RateLimiter:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.limit_per_minute = settings.RATE_LIMIT_PER_MINUTE

    def get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request."""
        # Prioritize authenticated user ID
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.id}"
        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limit."""
        client_id = self.get_client_id(request)
        key = f"rate_limit:{client_id}"

        try:
            current = self.redis_client.incr(key)
            if current == 1:
                # First request in this window, set expiry
                self.redis_client.expire(key, 60)

            if current > self.limit_per_minute:
                log.warning(
                    "rate_limit.exceeded",
                    client_id=client_id,
                    current=current,
                    limit=self.limit_per_minute
                )
                return False

            return True
        except Exception as e:
            # If Redis is down, allow request (fail open)
            log.warning("rate_limit.redis_error", error=str(e))
            return True

# Global rate limiter instance
rate_limiter = None

def init_rate_limiter():
    """Initialize rate limiter."""
    global rate_limiter
    try:
        rate_limiter = RateLimiter(settings.REDIS_URL)
        log.info("rate_limiter.initialized")
    except Exception as e:
        log.error("rate_limiter.init_failed", error=str(e))

async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limiting."""
    if not rate_limiter:
        return await call_next(request)

    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Max 60 requests per minute."
        )

    return await call_next(request)
