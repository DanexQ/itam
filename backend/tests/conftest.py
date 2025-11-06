import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.main import app
from app.core.database import Base, get_session
from pathlib import Path

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

dotenv_path = Path(__file__).with_name(".env.tests")
load_dotenv(dotenv_path)
load_dotenv(".env.tests")
engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_db():
    """
    Tworzy schemat przed testem i usuwa po teście.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client():
    """
    Nadpisuje zależność get_session, żeby użyć testowej sesji,
    i udostępnia AsyncClient z ASGITransport.
    """
    async def override_get_session():
        async with AsyncSessionLocal() as session:
            yield session

    # nadpisujemy zależność FastAPI
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # cleanup override
    app.dependency_overrides.pop(get_session, None)

@pytest_asyncio.fixture
def register_payload():
    return {
        "email": "user@example.com",
        "password": "string123",
        "first_name": "Jan",
        "last_name": "Kowalski",
        "position": "IT Manager",
        "department": "IT"
    }
