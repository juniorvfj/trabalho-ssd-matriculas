"""
Módulo de Serviços de Turmas (Application Layer)

As funções deste arquivo inserem e consultam períodos letivos e turmas no banco.
A lógica de matrícula de alunos na turma fica no módulo de matrículas (se houver), 
mas aqui cuidamos da entidade Turma em si.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import PeriodoLetivo, Turma
from ..api.schemas import PeriodoLetivoCreate, TurmaCreate

async def list_periodos_letivos(db: AsyncSession) -> List[PeriodoLetivo]:
    """Recupera todos os períodos letivos já cadastrados (ex: 2025.1, 2025.2)."""
    result = await db.execute(select(PeriodoLetivo))
    return result.scalars().all()

async def create_periodo_letivo(db: AsyncSession, periodo_in: PeriodoLetivoCreate) -> PeriodoLetivo:
    """Cria um novo semestre letivo no sistema."""
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
    """Lista todas as turmas de todas as disciplinas."""
    result = await db.execute(select(Turma))
    return result.scalars().all()

async def create_turma(db: AsyncSession, turma_in: TurmaCreate) -> Turma:
    """Cria uma turma para uma dada disciplina num determinado período letivo."""
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
