"""
Módulo de Banco de Dados (Core)

Responsável por estabelecer a conexão da aplicação com o banco de dados utilizando
o SQLAlchemy de forma totalmente assíncrona. A comunicação assíncrona não bloqueia 
a thread principal, permitindo maior escalabilidade na API.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Engine: O "motor" de conexão com o BD.
# echo=True faz com que o SQLAlchemy imprima as queries SQL no console (útil em dev).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
)

# AsyncSessionLocal: Fábrica de sessões (Transactions) com o banco de dados.
# autocommit e autoflush estão False para forçarmos o controle explícito da transação.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Base: Classe base declarativa do SQLAlchemy. Todos os nossos modelos ORM vão herdar dela.
Base = declarative_base()

async def get_db():
    """
    Dependency Injection (Injeção de Dependência) do FastAPI.
    Esta função gera uma nova sessão com o banco de dados a cada requisição HTTP 
    que a utilize, e fecha a sessão automaticamente após a requisição acabar (usando yield).
    """
    async with AsyncSessionLocal() as session:
        yield session
