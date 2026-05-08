"""
Módulo de Serviços (Application Layer) para Docentes

Contém a lógica de negócio e orquestração do CRUD de Docentes
e vinculação de docentes a turmas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional

from app.modules.docentes.infrastructure.orm_models import Docente, TurmaDocente
from app.modules.docentes.api.schemas import DocenteCreate, TurmaDocenteCreate


async def create_docente(db: AsyncSession, docente_in: DocenteCreate) -> Docente:
    """Cria um novo docente no sistema."""
    db_docente = Docente(**docente_in.model_dump())
    db.add(db_docente)
    try:
        await db.commit()
        await db.refresh(db_docente)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o docente. Verifique se a matrícula já existe."
        )
    return db_docente


async def list_all_docentes(db: AsyncSession) -> List[Docente]:
    """Retorna todos os docentes cadastrados."""
    result = await db.execute(select(Docente))
    return result.scalars().all()


async def get_docente_by_id(db: AsyncSession, docente_id: int) -> Optional[Docente]:
    """Busca um docente pelo seu ID."""
    result = await db.execute(select(Docente).where(Docente.id == docente_id))
    docente = result.scalar_one_or_none()
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente com id={docente_id} não encontrado."
        )
    return docente


async def vincular_docente_turma(db: AsyncSession, vinculo_in: TurmaDocenteCreate) -> TurmaDocente:
    """Vincula um docente a uma turma (relação N:M)."""
    # Verificar se o vínculo já existe
    result = await db.execute(
        select(TurmaDocente).where(
            TurmaDocente.turma_id == vinculo_in.turma_id,
            TurmaDocente.docente_id == vinculo_in.docente_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este docente já está vinculado a esta turma."
        )

    db_vinculo = TurmaDocente(**vinculo_in.model_dump())
    db.add(db_vinculo)
    try:
        await db.commit()
        await db.refresh(db_vinculo)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível vincular o docente à turma. Verifique os IDs."
        )
    return db_vinculo


async def listar_docentes_turma(db: AsyncSession, turma_id: int) -> List[TurmaDocente]:
    """Lista todos os docentes vinculados a uma turma."""
    result = await db.execute(
        select(TurmaDocente).where(TurmaDocente.turma_id == turma_id)
    )
    return result.scalars().all()
