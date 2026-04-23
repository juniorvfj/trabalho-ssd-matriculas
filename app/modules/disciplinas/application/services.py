from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from ..api.schemas import DisciplinaCreate, DisciplinaUpdate

async def list_disciplinas(db: AsyncSession) -> List[Disciplina]:
    result = await db.execute(select(Disciplina))
    return result.scalars().all()

async def get_disciplina_by_id(db: AsyncSession, disciplina_id: int) -> Disciplina:
    result = await db.execute(select(Disciplina).where(Disciplina.id == disciplina_id))
    disciplina = result.scalars().first()
    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disciplina com id {disciplina_id} não encontrada"
        )
    return disciplina

async def create_disciplina(db: AsyncSession, disciplina_in: DisciplinaCreate) -> Disciplina:
    # TODO: verificar se curso existe
    db_disciplina = Disciplina(**disciplina_in.model_dump())
    db.add(db_disciplina)
    try:
        await db.commit()
        await db.refresh(db_disciplina)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a disciplina. Verifique se o código já existe e se o curso_id é válido."
        )
    return db_disciplina
