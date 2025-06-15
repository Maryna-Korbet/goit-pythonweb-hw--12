from unittest.mock import Mock, patch
import sys
import os

import pytest
from sqlalchemy import select

from src.entity.models import User
from tests.conftest import TestingSessionLocal
from main import app

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# user data ==================================
user_data = {
    "username": "leapold",
    "email": "leapold@gmail.com",
    "password": "1234567890"
}

# auxiliary functions ================================
def patch_email(monkeypatch):
    """Mock email service."""
    mock_send_email = Mock()
    monkeypatch.setattr(
        "src.services.email_services.send_email", 
        mock_send_email
        )

def login_user(client):
    """Login and return response with tokens."""
    return client.post(
        "/api/auth/login/",
        data={
            "username": user_data["username"], 
            "password": user_data["password"]
        }
    )

def get_tokens(client):
    """Login and return access and refresh tokens."""
    response = login_user(client)
    data = response.json()
    return data["access_token"], data["refresh_token"]

# tests================================
def test_register(client, monkeypatch):
    """Test register user."""
    patch_email(monkeypatch)

    response = client.post("/api/auth/register/", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_register_username(client, monkeypatch):
    """Test register user with same username."""
    patch_email(monkeypatch)
    user_copy = user_data.copy()
    user_copy["email"] = "kot_leapold@gmail.com"

    response = client.post("/api/auth/register/", json=user_copy)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "User already exists"

def test_repeat_register_email(client, monkeypatch):
    """Test register user with same email."""
    patch_email(monkeypatch)
    user_copy = user_data.copy()
    user_copy["username"] = "kot_leapold"

    response = client.post("/api/auth/register/", json=user_copy)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Email already exists"

async def test_not_confirmed_login(client):
    """Test login without email confirmation."""
    response = await login_user(client)
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Email not confirmed"

@pytest.mark.asyncio
async def test_login(client):
    """Test successful login after confirming email."""
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = await login_user(client)  
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_wrong_password_login(client):
    """Test login with wrong password."""
    response = client.post(
        "/api/auth/login/",
        data={"username": user_data["username"], "password": "wrong_password"}
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Incorrect username or password"

def test_wrong_username_login(client):
    """Test login with wrong username."""
    response = client.post(
        "/api/auth/login/",
        data={"username": "unknown", "password": user_data["password"]}
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Wrong username or password"

def test_validation_error_login(client):
    """Test missing username field causes validation error."""
    response = client.post(
        "/api/auth/login/", 
        data={"password": user_data["password"]}
        )
    assert response.status_code == 422, response.text
    assert "detail" in response.json()

def test_refresh_token(client):
    """Test refresh token endpoint."""
    _, refresh_token = get_tokens(client)

    response = client.post(
        "/api/auth/refresh/", 
        json={"refresh_token": refresh_token}
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != refresh_token

async def test_logout(client):
    """Test logout and token blacklisting."""
    with patch("src.services.auth_services.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        redis_mock.setex.return_value = True

        access_token, refresh_token = get_tokens(client)

        response = await client.post(
            "/api/auth/logout/",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 204, response.text
