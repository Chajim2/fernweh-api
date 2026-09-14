import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_async_session, get_session

@pytest.fixture
async def db_async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def async_session(db_engine):
    async with AsyncSession(db_engine) as s:
        yield s

@pytest.fixture
async def async_client(db_engine):
    async def override():
        async with AsyncSession(db_engine) as s:
            yield s
            
    app.dependency_overrides[get_async_session] = override
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture
async def token(client) -> str:
    user_data = {"username" : "john",
                 "password" : "cena"}

    resp = await client.post("/auth/register", json=user_data)
    assert resp.status_code == 201, f"Failed to register {resp.text}"


    resp = await client.post("/auth/login", data=user_data)
    
    assert resp.status_code == 200, f"Failed to log in {resp.text}"

    return resp.json()['access_token']

@pytest.fixture
async def auth_client(client, token):
    # Inject the token into the client's default headers
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client