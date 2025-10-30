"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_merchant_id():
    """Return test merchant ID."""
    return "219c230a-5c4b-43d4-861d-f25979de2e88"


@pytest.fixture
def test_customer_id():
    """Return test customer ID."""
    return "3b415031-7236-425e-bc8f-35c7a5f572ab"


@pytest.fixture
def test_api_key():
    """Return test API key."""
    return "test"
