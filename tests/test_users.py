"""
Test user management endpoints
"""
import pytest


class TestGetCurrentUser:
    """Test GET /users/me endpoint"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user_data):
        """Test getting current user info"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # No sensitive data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_get_current_user_different_users(self, client, auth_headers, second_auth_headers, test_user_data, second_user_data):
        """Test that different tokens return different users"""
        resp1 = client.get("/api/v1/users/me", headers=auth_headers)
        resp2 = client.get("/api/v1/users/me", headers=second_auth_headers)
        
        user1 = resp1.json()
        user2 = resp2.json()
        
        assert user1["id"] != user2["id"]
        assert user1["email"] == test_user_data["email"]
        assert user2["email"] == second_user_data["email"]


class TestGetUserById:
    """Test GET /users/{user_id} endpoint"""
    
    def test_get_user_by_id_success(self, client, auth_headers):
        """Test getting user by ID"""
        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = me_resp.json()["id"]
        
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_user_not_found(self, client, auth_headers):
        """Test getting non-existent user"""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateUser:
    """Test PUT /users/me endpoint"""
    
    def test_update_user_success(self, client, auth_headers):
        """Test updating current user's full name"""
        response = client.put(
            "/api/v1/users/me",
            params={"full_name": "New Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["full_name"] == "New Name"
    
    def test_update_user_unauthorized(self, client):
        """Test updating user without authentication"""
        response = client.put(
            "/api/v1/users/me",
            params={"full_name": "Name"}
        )
        assert response.status_code == 401


class TestDeleteUser:
    """Test DELETE /users/me endpoint"""
    
    def test_delete_user_success(self, client, auth_headers):
        """Test deleting current user account"""
        response = client.delete("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify user can't access anymore
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 401
    
    def test_delete_user_unauthorized(self, client):
        """Test deleting user without authentication"""
        response = client.delete("/api/v1/users/me")
        assert response.status_code == 401