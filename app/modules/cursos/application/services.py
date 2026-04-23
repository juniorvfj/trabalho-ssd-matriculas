from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.cursos.infrastructure.orm_models import Curso
from ..api.schemas import CursoCreate, CursoUpdate
from app.core.exceptions import BaseAPIException

async def get_curso_by_id(db: AsyncSession, curso_id: int) -> Curso:
    stmt = select(Curso).where(Curso.id == curso_id)
    result = await db.execute(stmt)
    curso = result.scalar_one_or_none()
    if not curso:
        raise BaseAPIException(message="Curso não encontrado", code="CURSO_NOT_FOUND", status_code=404)
    return curso

async def list_cursos(db: AsyncSession):
    stmt = select(Curso)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_curso(db: AsyncSession, curso_in: CursoCreate) -> Curso:
    # Checar se já existe código
    stmt = select(Curso).where(Curso.codigo == curso_in.codigo)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise BaseAPIException(message="Código de curso já existente", code="CURSO_ALREADY_EXISTS", status_code=400)
    
    db_obj = Curso(**curso_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
