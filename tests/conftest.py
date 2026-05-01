"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Configuração do Pytest (Fixtures e Banco de Testes)
Descrição: Prepara o ambiente isolado de testes configurando o banco de dados
(PostgreSQL) sem pooling para evitar gargalos concorrentes e garantindo a correta 
injeção de dependências do Event Loop assíncrono durante os testes das Sprints.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.main import app
from app.core.database import Base, get_db

from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/matricula_test_db"

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Fornece uma sessão de banco de dados limpa para cada teste."""
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Fornece um cliente HTTP (httpx) assíncrono injetando a sessão de testes nas dependências."""
    # Sobrescreve a dependência get_db
    app.dependency_overrides[get_db] = lambda: db_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    
    app.dependency_overrides.clear()
