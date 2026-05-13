import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


# Configure pytest-asyncio to use function scope
pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture(scope="function")
async def client():
    """Create async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Test GET /health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]


@pytest.mark.asyncio
async def test_system_info(client: AsyncClient):
    """Test GET /api/system/info endpoint."""
    response = await client.get("/api/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "resources" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_api_version(client: AsyncClient):
    """Test GET /api/version endpoint."""
    response = await client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient):
    """Test GET /api/documents endpoint."""
    response = await client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_search_documents(client: AsyncClient):
    """Test POST /api/documents/search endpoint."""
    response = await client.post(
        "/api/documents/search",
        json={"query": "test", "top_k": 5}
    )
    # The search endpoint should work - return 200 with results or 200 with empty results
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
