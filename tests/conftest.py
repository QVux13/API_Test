"""
Test configuration and fixtures
Provides test database, client, and authenticated users
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from main import app

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Reuse same connection for all tests
)

# Create SessionLocal for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database for each test
    
    Yields:
        Session: Database session
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create test client with overridden database dependency
    
    Args:
        db_session: Test database session
    
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user credentials"""
    return {
        "email": "test@example.com",
        "password": "test123"
    }


@pytest.fixture
def test_user(client, test_user_data):
    """
    Create a test user and return user data
    
    Args:
        client: Test client
        test_user_data: User credentials
    
    Returns:
        dict: Created user data
    """
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def auth_headers(client, test_user_data, test_user):
    """
    Get authentication headers with Bearer token
    
    Args:
        client: Test client
        test_user_data: User credentials
        test_user: Created user
    
    Returns:
        dict: Headers with Authorization token
    """
    # Login to get token
    response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_data():
    """Second test user credentials"""
    return {
        "email": "user2@example.com",
        "password": "user2pass"
    }


@pytest.fixture
def second_user(client, second_user_data):
    """Create second test user"""
    response = client.post("/api/v1/auth/register", json=second_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def second_auth_headers(client, second_user_data, second_user):
    """Get auth headers for second user"""
    response = client.post("/api/v1/auth/login", data={
        "username": second_user_data["email"],
        "password": second_user_data["password"]
    })
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }