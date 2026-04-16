"""
Pytest configuration and fixtures for FastAPI application testing.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="function")
def client():
    """
    Provides a TestClient instance for testing the FastAPI application.
    The function scope ensures each test gets a fresh client instance.
    """
    return TestClient(app)