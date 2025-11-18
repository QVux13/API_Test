"""
Test authentication endpoints (register, login)
"""
import pytest


class TestRegister:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "test123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "test123"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "test123"
        })
        
        assert response.status_code == 422
    
    def test_register_weak_password(self, client):
        """Test registration with weak password (< 6 chars)"""
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "123"
        })
        
        assert response.status_code == 422
    
    def test_register_password_no_letters(self, client):
        """Test registration with password without letters"""
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "123456"
        })
        
        assert response.status_code == 400
        assert "letter" in response.json()["detail"].lower()
    
    def test_register_password_no_numbers(self, client):
        """Test registration with password without numbers"""
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "testtest"
        })
        
        assert response.status_code == 400
        assert "number" in response.json()["detail"].lower()


class TestLogin:
    """Test user login"""
    
    def test_login_success(self, client, test_user_data, test_user):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/api/v1/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "test123"
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Test login without required fields"""
        response = client.post("/api/v1/auth/login", data={
            "username": ""
        })
        
        assert response.status_code == 422


class TestTokenValidation:
    """Test JWT token validation"""
    
    def test_access_with_valid_token(self, client, auth_headers):
        """Test accessing protected route with valid token"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
    
    def test_access_without_token(self, client):
        """Test accessing protected route without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client):
        """Test accessing protected route with invalid token"""
        response = client.get("/api/v1/users/me", headers={
            "Authorization": "Bearer invalid-token"
        })
        assert response.status_code == 401


class TestAuthFlow:
    """Test complete authentication flow"""
    
    def test_register_login_access_flow(self, client):
        """Test complete flow: register -> login -> access"""
        # Register
        user_data = {"email": "flow@example.com", "password": "flow123"}
        reg_resp = client.post("/api/v1/auth/register", json=user_data)
        assert reg_resp.status_code == 200
        
        # Login
        login_resp = client.post("/api/v1/auth/login", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        
        # Access protected resource
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = client.get("/api/v1/users/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == user_data["email"]
    
    def test_multiple_users_isolation(self, client, auth_headers, second_auth_headers, test_user_data, second_user_data):
        """Test that users are isolated from each other"""
        # Get user 1 info
        resp1 = client.get("/api/v1/users/me", headers=auth_headers)
        user1 = resp1.json()
        
        # Get user 2 info
        resp2 = client.get("/api/v1/users/me", headers=second_auth_headers)
        user2 = resp2.json()
        
        # Should be different users
        assert user1["email"] == test_user_data["email"]
        assert user2["email"] == second_user_data["email"]
        assert user1["id"] != user2["id"]