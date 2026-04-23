from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import PeriodoLetivo, Turma
from ..api.schemas import PeriodoLetivoCreate, TurmaCreate

async def list_periodos_letivos(db: AsyncSession) -> List[PeriodoLetivo]:
    result = await db.execute(select(PeriodoLetivo))
    return result.scalars().all()

async def create_periodo_letivo(db: AsyncSession, periodo_in: PeriodoLetivoCreate) -> PeriodoLetivo:
    db_periodo = PeriodoLetivo(**periodo_in.model_dump())
    db.add(db_periodo)
    try:
        await db.commit()
        await db.refresh(db_periodo)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o período letivo. Verifique se o código já existe."
        )
    return db_periodo

async def list_turmas(db: AsyncSession) -> List[Turma]:
    result = await db.execute(select(Turma))
    return result.scalars().all()

async def create_turma(db: AsyncSession, turma_in: TurmaCreate) -> Turma:
    db_turma = Turma(**turma_in.model_dump())
    db.add(db_turma)
    try:
        await db.commit()
        await db.refresh(db_turma)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a turma. Verifique se a disciplina e o período letivo existem."
        )
    return db_turma
