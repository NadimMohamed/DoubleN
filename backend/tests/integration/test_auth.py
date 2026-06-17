import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass1",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "hashed_password" not in data
        assert "id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "differentuser",
            "password": "SecurePass1",
        })
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower()

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "different@example.com",
            "username": "testuser",
            "password": "SecurePass1",
        })
        assert resp.status_code == 409
        assert "username" in resp.json()["detail"].lower()

    async def test_register_weak_password(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "username": "weakpass",
            "password": "weak",
        })
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "someuser",
            "password": "SecurePass1",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword1",
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "ghost@example.com",
            "password": "TestPass123",
        })
        assert resp.status_code == 401

    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "TEST@EXAMPLE.COM",
            "password": "TestPass123",
        })
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetMe:
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    async def test_get_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 403  # No auth header → 403

    async def test_get_me_invalid_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me",
                                headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestRefreshToken:
    async def test_refresh_success(self, client: AsyncClient, test_user):
        # First login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        refresh_token = login_resp.json()["refresh_token"]

        # Refresh
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["access_token"] != login_resp.json()["access_token"]

    async def test_refresh_with_access_token_fails(self, client: AsyncClient, test_user):
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        access_token = login_resp.json()["access_token"]

        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": access_token  # wrong type
        })
        assert resp.status_code == 401
