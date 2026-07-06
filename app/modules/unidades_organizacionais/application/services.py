"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Unidade Organizacional — modelo SIGAA.

Consultas e criação sobre a tabela SIGAA_UNIDADE (código natural de 3 caracteres).
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.unidades_organizacionais.api.schemas import UnidadeOrganizacionalCreate
from app.modules.unidades_organizacionais.infrastructure.orm_models import UnidadeOrganizacional


async def search_unidades(
    db: AsyncSession, nome: Optional[str], offset: int, count: int
) -> tuple[list[UnidadeOrganizacional], int]:
    """Pesquisa unidades por nome (parcial) com paginação; retorna (página, total)."""
    filtros = []
    if nome:
        filtros.append(UnidadeOrganizacional.nome.ilike(f"%{nome}%"))

    total = (
        await db.execute(select(func.count()).select_from(UnidadeOrganizacional).where(*filtros))
    ).scalar_one()
    result = await db.execute(
        select(UnidadeOrganizacional)
        .where(*filtros)
        .order_by(UnidadeOrganizacional.nome)
        .offset(offset)
        .limit(count)
    )
    return list(result.scalars().all()), total


async def get_unidade_by_id(db: AsyncSession, unidade_id: str) -> UnidadeOrganizacional:
    """Busca uma unidade organizacional pelo seu código (PK)."""
    unidade = (
        await db.execute(select(UnidadeOrganizacional).where(UnidadeOrganizacional.id == unidade_id))
    ).scalar_one_or_none()
    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unidade organizacional '{unidade_id}' não encontrada.",
        )
    return unidade


async def create_unidade(db: AsyncSession, unidade_in: UnidadeOrganizacionalCreate) -> UnidadeOrganizacional:
    """Cria uma nova unidade organizacional (SIGAA_UNIDADE)."""
    db_unidade = UnidadeOrganizacional(id=unidade_in.id, nome=unidade_in.nome)
    db.add(db_unidade)
    try:
        await db.commit()
        await db.refresh(db_unidade)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a unidade. Verifique se o código já existe.",
        )
    return db_unidade
