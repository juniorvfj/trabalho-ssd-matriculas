"""
Módulo de Serviços de Histórico Acadêmico (Application Layer)

Contém as regras de negócio para consulta e inserção de registros no histórico
acadêmico consolidado (HistoricoAcademico) e nos itens individuais de disciplinas
(HistoricoDisciplina).
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import HistoricoAcademico, HistoricoDisciplina
from ..api.schemas import HistoricoAcademicoCreate, HistoricoDisciplinaCreate


async def get_historico_by_aluno(db: AsyncSession, aluno_id: int) -> HistoricoAcademico:
    """
    Retorna o histórico acadêmico consolidado de um aluno específico,
    incluindo a lista de disciplinas cursadas (eager loading).

    Lança 404 se o aluno não possuir histórico cadastrado.
    """
    result = await db.execute(
        select(HistoricoAcademico)
        .options(selectinload(HistoricoAcademico.disciplinas))
        .where(HistoricoAcademico.aluno_id == aluno_id)
    )
    historico = result.scalar_one_or_none()
    if not historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Histórico acadêmico não encontrado para aluno_id={aluno_id}"
        )
    return historico


async def create_historico(db: AsyncSession, historico_in: HistoricoAcademicoCreate) -> HistoricoAcademico:
    """
    Cria um novo histórico acadêmico consolidado para um aluno.

    Valida que o aluno ainda não possui histórico (relação 1:1).
    """
    existing = await db.execute(
        select(HistoricoAcademico).where(HistoricoAcademico.aluno_id == historico_in.aluno_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O aluno_id={historico_in.aluno_id} já possui histórico acadêmico cadastrado."
        )

    db_historico = HistoricoAcademico(**historico_in.model_dump())
    db.add(db_historico)
    try:
        await db.commit()
        await db.refresh(db_historico)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o histórico. Verifique se aluno_id é válido."
        )
    return db_historico


async def add_disciplina_to_historico(
    db: AsyncSession, aluno_id: int, disciplina_in: HistoricoDisciplinaCreate
) -> HistoricoDisciplina:
    """
    Adiciona um registro de disciplina cursada ao histórico acadêmico de um aluno.

    Busca o histórico consolidado do aluno e vincula o novo item.
    """
    result = await db.execute(
        select(HistoricoAcademico).where(HistoricoAcademico.aluno_id == aluno_id)
    )
    historico = result.scalar_one_or_none()
    if not historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Histórico acadêmico não encontrado para aluno_id={aluno_id}. Crie o histórico antes."
        )

    db_disciplina = HistoricoDisciplina(
        historico_academico_id=historico.id,
        **disciplina_in.model_dump()
    )
    db.add(db_disciplina)
    try:
        await db.commit()
        await db.refresh(db_disciplina)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível adicionar a disciplina ao histórico. Verifique disciplina_id e periodo_letivo_id."
        )
    return db_disciplina


async def list_all_historicos(db: AsyncSession) -> List[HistoricoAcademico]:
    """Retorna todos os históricos acadêmicos consolidados do sistema."""
    result = await db.execute(
        select(HistoricoAcademico).options(selectinload(HistoricoAcademico.disciplinas))
    )
    return result.scalars().all()
