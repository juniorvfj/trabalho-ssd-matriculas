"""
Módulo de Serviços (Application Layer) para Unidades Organizacionais

Contém a lógica de negócio e orquestração do CRUD de Unidades Organizacionais.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional

from app.modules.unidades_organizacionais.infrastructure.orm_models import UnidadeOrganizacional
from app.modules.unidades_organizacionais.api.schemas import UnidadeOrganizacionalCreate


async def create_unidade(db: AsyncSession, unidade_in: UnidadeOrganizacionalCreate) -> UnidadeOrganizacional:
    """Cria uma nova unidade organizacional."""
    db_unidade = UnidadeOrganizacional(**unidade_in.model_dump())
    db.add(db_unidade)
    try:
        await db.commit()
        await db.refresh(db_unidade)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a unidade organizacional. Verifique se o código já existe."
        )
    return db_unidade


async def list_all_unidades(db: AsyncSession) -> List[UnidadeOrganizacional]:
    """Retorna todas as unidades organizacionais cadastradas."""
    result = await db.execute(select(UnidadeOrganizacional))
    return result.scalars().all()


async def get_unidade_by_id(db: AsyncSession, unidade_id: int) -> Optional[UnidadeOrganizacional]:
    """Busca uma unidade organizacional pelo seu ID."""
    result = await db.execute(select(UnidadeOrganizacional).where(UnidadeOrganizacional.id == unidade_id))
    unidade = result.scalar_one_or_none()
    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unidade organizacional com id={unidade_id} não encontrada."
        )
    return unidade
