import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, verify_token
from app.auth.password_reset_service import PasswordResetService


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, db_session: Session):
        """Test creating a new user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpassword")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_online is False
        assert user.created_at is not None
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestAuthenticationEndpoints:
    """Test authentication API endpoints"""
    
    def test_user_registration(self, client: TestClient):
        """Test user registration endpoint"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert data["is_online"] is False
    
    def test_duplicate_email_registration(self, client: TestClient):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        user_data["username"] = "user2"
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_duplicate_username_registration(self, client: TestClient):
        """Test registration with duplicate username"""
        user_data1 = {
            "email": "user1@example.com",
            "username": "sameusername",
            "password": "password123"
        }
        user_data2 = {
            "email": "user2@example.com",
            "username": "sameusername",
            "password": "password123"
        }
        
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data1)
        assert response1.status_code == 201
        
        # Second registration with same username should fail
        response2 = client.post("/api/v1/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Username already taken" in response2.json()["detail"]
    
    def test_user_login(self, client: TestClient):
        """Test user login endpoint"""
        # First register a user
        user_data = {
            "email": "logintest@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "email": "logintest@example.com",
            "password": "loginpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client: TestClient):
        """Test getting current user profile"""
        # Register and login
        user_data = {
            "email": "profile@example.com",
            "username": "profileuser",
            "password": "profilepassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "profile@example.com",
            "password": "profilepassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
    
    def test_logout(self, client: TestClient):
        """Test user logout"""
        # Register and login
        user_data = {
            "email": "logout@example.com",
            "username": "logoutuser",
            "password": "logoutpassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "logout@example.com",
            "password": "logoutpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]


class TestJWTTokens:
    """Test JWT token functionality"""
    
    def test_token_refresh(self, client: TestClient):
        """Test token refresh endpoint"""
        # Register and login
        user_data = {
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "refreshpassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": "refresh@example.com",
            "password": "refreshpassword123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_token_refresh(self, client: TestClient):
        """Test refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    def test_token_verification(self):
        """Test JWT token verification"""
        # This tests the verify_token function directly
        from app.core.security import create_access_token
        
        token_data = {"sub": "123"}
        token = create_access_token(token_data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        
        # Test invalid token
        invalid_payload = verify_token("invalid_token")
        assert invalid_payload is None


class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_password_reset_request(self, client: TestClient):
        """Test password reset request"""
        # Register a user first
        user_data = {
            "email": "reset@example.com",
            "username": "resetuser",
            "password": "oldpassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Request password reset
        reset_request = {"email": "reset@example.com"}
        response = client.post("/api/v1/auth/password-reset", json=reset_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data  # In production, this would be sent via email
        assert "message" in data
    
    def test_password_reset_nonexistent_email(self, client: TestClient):
        """Test password reset for nonexistent email"""
        reset_request = {"email": "nonexistent@example.com"}
        response = client.post("/api/v1/auth/password-reset", json=reset_request)
        assert response.status_code == 200  # Don't reveal if email exists
        
        data = response.json()
        assert "message" in data
    
    def test_password_reset_confirm(self, client: TestClient, db_session: Session):
        """Test password reset confirmation"""
        # Register a user
        user_data = {
            "email": "confirm@example.com",
            "username": "confirmuser",
            "password": "oldpassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Request password reset
        reset_request = {"email": "confirm@example.com"}
        reset_response = client.post("/api/v1/auth/password-reset", json=reset_request)
        token = reset_response.json()["token"]
        
        # Confirm password reset
        confirm_data = {
            "token": token,
            "new_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/password-reset-confirm", json=confirm_data)
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]
        
        # Test login with new password
        login_data = {
            "email": "confirm@example.com",
            "password": "newpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
    
    def test_password_reset_invalid_token(self, client: TestClient):
        """Test password reset with invalid token"""
        confirm_data = {
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
        response = client.post("/api/v1/auth/password-reset-confirm", json=confirm_data)
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]
    
    def test_password_reset_service(self, db_session: Session):
        """Test PasswordResetService directly"""
        # Create a user
        user = User(
            email="service@example.com",
            username="serviceuser",
            hashed_password=get_password_hash("oldpassword")
        )
        db_session.add(user)
        db_session.commit()
        
        # Test password reset service
        service = PasswordResetService(db_session)
        
        # Create reset token
        token = service.create_reset_token("service@example.com")
        assert token is not None
        assert len(token) == 32
        
        # Verify token
        verified_user = service.verify_reset_token(token)
        assert verified_user is not None
        assert verified_user.email == "service@example.com"
        
        # Reset password
        success = service.reset_password(token, "newpassword")
        assert success is True
        
        # Verify token is now invalid
        verified_user_after = service.verify_reset_token(token)
        assert verified_user_after is None