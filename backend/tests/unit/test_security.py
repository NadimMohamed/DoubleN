import pytest
from datetime import timedelta
from jose import JWTError

from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("MyPassword1")
        assert hashed != "MyPassword1"
        assert len(hashed) > 30

    def test_verify_correct_password(self):
        hashed = hash_password("MyPassword1")
        assert verify_password("MyPassword1", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("MyPassword1")
        assert verify_password("WrongPass", hashed) is False

    def test_same_password_different_hashes(self):
        """bcrypt generates unique salts each time."""
        h1 = hash_password("Same1Password")
        h2 = hash_password("Same1Password")
        assert h1 != h2
        # But both verify correctly
        assert verify_password("Same1Password", h1) is True
        assert verify_password("Same1Password", h2) is True


class TestJWT:
    def test_access_token_roundtrip(self):
        token, expires_at = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"
        assert payload["exp"] == expires_at

    def test_access_token_returns_expiry(self):
        token, expires_at = create_access_token("user-123")
        assert isinstance(expires_at, int)
        assert expires_at > 0

    def test_refresh_token_type(self):
        token, expires_at = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user-456"
        assert payload["exp"] == expires_at

    def test_decode_invalid_token_raises(self):
        with pytest.raises(JWTError):
            decode_token("not.a.valid.token")

    def test_decode_tampered_token_raises(self):
        token, _ = create_access_token("user-789")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_token(tampered)
