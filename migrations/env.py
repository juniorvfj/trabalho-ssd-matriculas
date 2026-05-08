"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
Disciplina: Segurança em Sistemas Distribuídos — UnB
Professor: Ricardo Staciarini Puttini

Módulo de Configuração do Alembic (migrations/env.py)

Este arquivo é executado pelo Alembic quando rodamos 'alembic upgrade head' ou
'alembic revision --autogenerate'. Ele conecta o Alembic ao nosso banco de dados
PostgreSQL de forma assíncrona (usando asyncpg) e aponta para os metadados de
todos os nossos modelos ORM (Base.metadata).

IMPORTANTE:
  - Todos os modelos ORM DEVEM ser importados aqui para que o Alembic enxergue
    as tabelas ao gerar migrações automáticas (--autogenerate).
  - A URL do banco é lida de app.core.config.settings (que carrega o .env).
  - Utilizamos NullPool para migrations, pois não precisamos de pool de conexões
    durante a execução de scripts de migração.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ═══════════════════════════════════════════════════════════════════════════════
# Importação da configuração e dos modelos ORM
# ═══════════════════════════════════════════════════════════════════════════════
# A importação de cada modelo garante que o SQLAlchemy registre a tabela
# no Base.metadata, permitindo que o Alembic detecte mudanças no schema.
from app.core.config import settings
from app.core.database import Base

# Modelos de Entidade — cada import registra uma tabela no metadata
from app.modules.usuarios.infrastructure.orm_models import Usuario
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.disciplinas.infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from app.modules.turmas.infrastructure.orm_models import PeriodoLetivo, Turma
from app.modules.historicos.infrastructure.orm_models import HistoricoAcademico
from app.modules.matriculas.infrastructure.orm_models import SolicitacaoMatricula, Matricula, AuditoriaProcessamento
from app.modules.docentes.infrastructure.orm_models import Docente, TurmaDocente
from app.modules.unidades_organizacionais.infrastructure.orm_models import UnidadeOrganizacional

# ═══════════════════════════════════════════════════════════════════════════════
# Configuração do Alembic
# ═══════════════════════════════════════════════════════════════════════════════

# Objeto de configuração do Alembic (lê alembic.ini)
config = context.config

# Sobrescreve a URL do banco no alembic.ini com a URL do nosso .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configura os loggers do Python a partir do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados do SQLAlchemy contendo todas as tabelas registradas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Executa migrations no modo 'offline' (sem conexão com o banco).

    Gera os comandos SQL como texto, útil para review de DDL antes de aplicar.
    Usado com: alembic upgrade head --sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Executa as migrations usando uma conexão síncrona fornecida pelo wrapper assíncrono."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Cria a engine assíncrona e executa as migrations.

    Usa NullPool (sem pooling) pois migrations são operações de curta duração
    e não precisam de um pool de conexões persistente.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Executa migrations no modo 'online' (conectado ao banco).

    Este é o modo padrão usado por 'alembic upgrade head'.
    """
    asyncio.run(run_async_migrations())


# Seleciona o modo de execução (offline ou online)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
