"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Curso — modelo SIGAA.

Consultas sobre SIGAA_CURSO e a tabela associativa SIGAA_RL_CURSO_UNIDADE,
seguindo as mesmas junções do arquivo de referência SIGAA-API.sql do professor.
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BaseAPIException
from app.modules.cursos.api.schemas import CursoCreate
from app.modules.cursos.infrastructure.orm_models import Curso, CursoUnidade
from app.modules.unidades_organizacionais.infrastructure.orm_models import UnidadeOrganizacional


async def search_cursos(
    db: AsyncSession, nome: Optional[str], unidade: Optional[str], offset: int, count: int
) -> tuple[list[Curso], int]:
    """
    Pesquisa cursos por nome (parcial) e/ou unidade organizacional, com paginação.
    A junção com SIGAA_RL_CURSO_UNIDADE reproduz a consulta de busca do professor.
    """
    stmt = select(Curso)
    count_stmt = select(func.count(func.distinct(Curso.id)))
    if unidade:
        stmt = stmt.join(CursoUnidade, CursoUnidade.curso == Curso.id).where(CursoUnidade.unidade == unidade)
        count_stmt = count_stmt.join(CursoUnidade, CursoUnidade.curso == Curso.id).where(CursoUnidade.unidade == unidade)
    if nome:
        stmt = stmt.where(Curso.nome.ilike(f"%{nome}%"))
        count_stmt = count_stmt.where(Curso.nome.ilike(f"%{nome}%"))

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Curso.nome).offset(offset).limit(count))
    return list(result.scalars().all()), total


async def get_curso_by_id(db: AsyncSession, curso_id: str) -> Curso:
    """Retorna o curso pelo código (PK). Dispara 404 caso não exista."""
    curso = (await db.execute(select(Curso).where(Curso.id == curso_id))).scalar_one_or_none()
    if not curso:
        raise BaseAPIException(message="Curso não encontrado", code="CURSO_NOT_FOUND", status_code=404)
    return curso


async def get_unidades_do_curso(db: AsyncSession, curso_id: str) -> list[UnidadeOrganizacional]:
    """Retorna as unidades organizacionais vinculadas a um curso (via SIGAA_RL_CURSO_UNIDADE)."""
    result = await db.execute(
        select(UnidadeOrganizacional)
        .join(CursoUnidade, CursoUnidade.unidade == UnidadeOrganizacional.id)
        .where(CursoUnidade.curso == curso_id)
    )
    return list(result.scalars().all())


async def create_curso(db: AsyncSession, curso_in: CursoCreate) -> Curso:
    """Cria um novo curso, validando unicidade do código."""
    if (await db.execute(select(Curso).where(Curso.id == curso_in.id))).scalar_one_or_none():
        raise BaseAPIException(message="Código de curso já existente", code="CURSO_ALREADY_EXISTS", status_code=400)
    db_obj = Curso(**curso_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
