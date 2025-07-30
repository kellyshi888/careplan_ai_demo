"""
Tests for authentication functionality
"""
import pytest
from app.auth.service import AuthenticationService

def test_auth_service_initialization():
    """Test that AuthenticationService initializes correctly"""
    auth_service = AuthenticationService()
    assert auth_service is not None
    assert auth_service.secret_key is not None
    assert auth_service.algorithm == "HS256"

def test_password_hashing():
    """Test password hashing functionality"""
    auth_service = AuthenticationService()
    password = "test_password"
    hashed = auth_service.password_context.hash(password)
    
    assert hashed != password
    assert auth_service.password_context.verify(password, hashed)
    assert not auth_service.password_context.verify("wrong_password", hashed)

def test_sample_users_loaded():
    """Test that sample users are loaded correctly"""
    auth_service = AuthenticationService()
    
    # Check that some users are loaded
    assert len(auth_service._users) > 0
    assert len(auth_service._email_to_user_id) > 0
    
    # Check for specific test users
    assert "admin@hospital.com" in auth_service._email_to_user_id
    assert "dr.garcia@hospital.com" in auth_service._email_to_user_id