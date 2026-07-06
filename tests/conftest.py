"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Configuração do Pytest (Fixtures e Banco de Testes) — modelo SIGAA.

Cria um banco SQLite temporário por teste, gera as tabelas a partir do metadata
(Base.metadata) e carrega a massa de dados de referência do professor usando o
mesmo carregador do seed (scripts/seed.py). Assim os testes rodam de forma portável,
sem exigir um PostgreSQL, exercitando exatamente os dados do professor.
"""
import os
import tempfile
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Garante que a app e o engine usem SQLite antes de importar módulos que criam engine
os.environ.setdefault("ENVIRONMENT", "test")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from scripts.seed import DB_DIR, DML_FILES, _extract_inserts  # noqa: E402


async def _carregar_dados_professor(conn) -> None:
    """Carrega os INSERTs do professor (ordem de FK) via SQL bruto."""
    for nome in DML_FILES:
        for stmt in _extract_inserts(DB_DIR / nome):
            await conn.exec_driver_sql(stmt)


@pytest_asyncio.fixture
async def engine():
    fd, caminho = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    eng = create_async_engine(f"sqlite+aiosqlite:///{caminho}", echo=False, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _carregar_dados_professor(conn)
    yield eng
    await eng.dispose()
    os.remove(caminho)


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de banco de dados limpa para cada teste."""
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP assíncrono com a sessão de testes injetada em get_db."""
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()
