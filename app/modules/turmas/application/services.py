"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Turma — modelo SIGAA.

Operações sobre SIGAA_TURMA e SIGAA_TURMA_HORARIOAULA. O período letivo é um
campo texto (ex.: '20182'), não uma entidade.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas import HorarioAulaCreate, TurmaCreate
from ..infrastructure.orm_models import HorarioAula, Turma


async def search_turmas(
    db: AsyncSession,
    periodo_letivo: Optional[str],
    disciplina: Optional[str],
    offset: int,
    count: int,
) -> tuple[list[Turma], int]:
    """Pesquisa turmas por período letivo e/ou disciplina, com paginação."""
    filtros = []
    if periodo_letivo:
        filtros.append(Turma.periodo_letivo == periodo_letivo)
    if disciplina:
        filtros.append(Turma.disciplina == disciplina)

    total = (await db.execute(select(func.count()).select_from(Turma).where(*filtros))).scalar_one()
    result = await db.execute(select(Turma).where(*filtros).order_by(Turma.id).offset(offset).limit(count))
    return list(result.scalars().all()), total


async def get_turma_by_id(db: AsyncSession, turma_id: int) -> Turma:
    """Busca uma turma pelo ID."""
    turma = (await db.execute(select(Turma).where(Turma.id == turma_id))).scalar_one_or_none()
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Turma {turma_id} não encontrada")
    return turma


async def create_turma(db: AsyncSession, turma_in: TurmaCreate) -> Turma:
    """Cria uma turma para uma disciplina num período letivo."""
    db_turma = Turma(**turma_in.model_dump())
    db.add(db_turma)
    try:
        await db.commit()
        await db.refresh(db_turma)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a turma. Verifique a disciplina e a unicidade (código+período+disciplina).",
        )
    return db_turma


async def list_horarios(db: AsyncSession) -> list[HorarioAula]:
    """Lista os slots de horário de aula (SIGAA_TURMA_HORARIOAULA)."""
    result = await db.execute(select(HorarioAula).order_by(HorarioAula.id))
    return list(result.scalars().all())


async def create_horario(db: AsyncSession, horario_in: HorarioAulaCreate) -> HorarioAula:
    """Cria um slot de horário de aula."""
    db_horario = HorarioAula(**horario_in.model_dump())
    db.add(db_horario)
    try:
        await db.commit()
        await db.refresh(db_horario)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o horário. Verifique se o código já existe.",
        )
    return db_horario
