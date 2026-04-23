"""
Módulo de Serviços de Cursos (Application Layer)

As funções deste arquivo lidam com a regra de negócio da entidade Curso, isolando
o código de banco de dados do código da web/API.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.cursos.infrastructure.orm_models import Curso
from ..api.schemas import CursoCreate, CursoUpdate
from app.core.exceptions import BaseAPIException

async def get_curso_by_id(db: AsyncSession, curso_id: int) -> Curso:
    """Retorna o curso de acordo com o ID. Dispara uma exceção customizada caso não exista."""
    stmt = select(Curso).where(Curso.id == curso_id)
    result = await db.execute(stmt)
    curso = result.scalar_one_or_none()
    if not curso:
        raise BaseAPIException(message="Curso não encontrado", code="CURSO_NOT_FOUND", status_code=404)
    return curso

async def list_cursos(db: AsyncSession):
    """Lista todos os cursos existentes."""
    stmt = select(Curso)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_curso(db: AsyncSession, curso_in: CursoCreate) -> Curso:
    """
    Cria um novo curso validando regras de negócio cruciais.
    Ex: Não podem haver dois cursos com o mesmo código institucional.
    """
    # Checar se já existe código
    stmt = select(Curso).where(Curso.codigo == curso_in.codigo)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise BaseAPIException(message="Código de curso já existente", code="CURSO_ALREADY_EXISTS", status_code=400)
    
    # Transforma o Schema (Pydantic) num Objeto de BD (SQLAlchemy) e insere
    db_obj = Curso(**curso_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
