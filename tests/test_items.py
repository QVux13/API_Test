"""
Test item/task management endpoints
"""
import pytest


class TestCreateItem:
    """Test POST /items/ endpoint"""
    
    def test_create_item_success(self, client, auth_headers):
        """Test creating a new item"""
        response = client.post(
            "/api/v1/items/",
            json={"title": "Test Task", "description": "Description"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Description"
        assert "id" in data
        assert "owner_id" in data
    
    def test_create_item_unauthorized(self, client):
        """Test creating item without authentication"""
        response = client.post("/api/v1/items/", json={"title": "Task"})
        assert response.status_code == 401
    
    def test_create_item_without_description(self, client, auth_headers):
        """Test creating item without optional description"""
        response = client.post(
            "/api/v1/items/",
            json={"title": "Task"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json()["description"] is None
    
    def test_create_item_missing_title(self, client, auth_headers):
        """Test creating item without required title"""
        response = client.post(
            "/api/v1/items/",
            json={"description": "No title"},
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestGetItems:
    """Test GET /items/ endpoint"""
    
    def test_get_items_empty(self, client, auth_headers):
        """Test getting items when none exist"""
        response = client.get("/api/v1/items/", headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json()) == 0
    
    def test_get_items_with_data(self, client, auth_headers):
        """Test getting items after creating some"""
        # Create 3 items
        for i in range(3):
            client.post(
                "/api/v1/items/",
                json={"title": f"Task {i}"},
                headers=auth_headers
            )
        
        response = client.get("/api/v1/items/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_get_items_pagination(self, client, auth_headers):
        """Test pagination with skip and limit"""
        # Create 10 items
        for i in range(10):
            client.post(
                "/api/v1/items/",
                json={"title": f"Task {i}"},
                headers=auth_headers
            )
        
        # Test skip
        response = client.get("/api/v1/items/?skip=5", headers=auth_headers)
        assert len(response.json()) == 5
        
        # Test limit
        response = client.get("/api/v1/items/?limit=3", headers=auth_headers)
        assert len(response.json()) == 3
    
    def test_get_items_user_isolation(self, client, auth_headers, second_auth_headers):
        """Test users can only see their own items"""
        # User 1 creates items
        client.post("/api/v1/items/", json={"title": "User 1 Task"}, headers=auth_headers)
        
        # User 2 creates items
        client.post("/api/v1/items/", json={"title": "User 2 Task"}, headers=second_auth_headers)
        
        # User 1 should only see their items
        resp1 = client.get("/api/v1/items/", headers=auth_headers)
        assert len(resp1.json()) == 1
        assert "User 1" in resp1.json()[0]["title"]
        
        # User 2 should only see their items
        resp2 = client.get("/api/v1/items/", headers=second_auth_headers)
        assert len(resp2.json()) == 1
        assert "User 2" in resp2.json()[0]["title"]
    
    def test_get_items_unauthorized(self, client):
        """Test getting items without authentication"""
        response = client.get("/api/v1/items/")
        assert response.status_code == 401


class TestGetItemById:
    """Test GET /items/{item_id} endpoint"""
    
    def test_get_item_success(self, client, auth_headers):
        """Test getting specific item by ID"""
        # Create item
        create_resp = client.post(
            "/api/v1/items/",
            json={"title": "Test", "description": "Desc"},
            headers=auth_headers
        )
        item_id = create_resp.json()["id"]
        
        # Get item
        response = client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == item_id
    
    def test_get_item_not_found(self, client, auth_headers):
        """Test getting non-existent item"""
        response = client.get("/api/v1/items/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_item_unauthorized_access(self, client, auth_headers, second_auth_headers):
        """Test user cannot access another user's item"""
        # User 1 creates item
        create_resp = client.post(
            "/api/v1/items/",
            json={"title": "User 1 Task"},
            headers=auth_headers
        )
        item_id = create_resp.json()["id"]
        
        # User 2 tries to access
        response = client.get(f"/api/v1/items/{item_id}", headers=second_auth_headers)
        assert response.status_code == 404


class TestUpdateItem:
    """Test PUT /items/{item_id} endpoint"""
    
    def test_update_item_success(self, client, auth_headers):
        """Test updating item"""
        # Create item
        create_resp = client.post(
            "/api/v1/items/",
            json={"title": "Original", "description": "Desc"},
            headers=auth_headers
        )
        item_id = create_resp.json()["id"]
        
        # Update item
        response = client.put(
            f"/api/v1/items/{item_id}",
            json={"title": "Updated", "description": "New Desc"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    def test_update_item_not_found(self, client, auth_headers):
        """Test updating non-existent item"""
        response = client.put(
            "/api/v1/items/99999",
            json={"title": "New"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_update_item_unauthorized(self, client, auth_headers, second_auth_headers):
        """Test updating another user's item"""
        # User 1 creates item
        create_resp = client.post(
            "/api/v1/items/",
            json={"title": "Task"},
            headers=auth_headers
        )
        item_id = create_resp.json()["id"]
        
        # User 2 tries to update
        response = client.put(
            f"/api/v1/items/{item_id}",
            json={"title": "Hacked"},
            headers=second_auth_headers
        )
        assert response.status_code == 404


class TestDeleteItem:
    """Test DELETE /items/{item_id} endpoint"""
    
    def test_delete_item_success(self, client, auth_headers):
        """Test deleting item"""
        # Create item
        create_resp = client.post(
            "/api/v1/items/",
            json={"title": "To Delete"},
            headers=auth_headers
        )
        item_id = create_resp.json()["id"]
        
        # Delete item
        response = client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_item_not_found(self, client, auth_headers):
        """Test deleting non-existent item"""
        response = client.delete("/api/v1/items/99999", headers=auth_headers)
        assert response.status_code == 404