"""
Módulo de Serviços de Histórico Acadêmico (Application Layer)

Contém as regras de negócio para consulta e inserção de registros no histórico.
A função 'get_historico_by_aluno' é particularmente importante: ela é a base
para que o serviço 'verificarElegibilidade' consulte quais disciplinas o aluno
já cursou (e se foi aprovado), determinando se ele pode se matricular em novas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import HistoricoAcademico
from ..api.schemas import HistoricoAcademicoCreate


async def get_historico_by_aluno(db: AsyncSession, aluno_id: int) -> List[HistoricoAcademico]:
    """
    Retorna todos os registros do histórico acadêmico de um aluno específico.

    Essa função é essencial para:
    - Verificar se o aluno já foi aprovado em uma disciplina (elegibilidade)
    - Verificar se o aluno cumpriu os pré-requisitos de outra disciplina
    - Gerar o comprovante acadêmico do aluno
    """
    result = await db.execute(
        select(HistoricoAcademico).where(HistoricoAcademico.aluno_id == aluno_id)
    )
    return result.scalars().all()


async def create_historico(db: AsyncSession, historico_in: HistoricoAcademicoCreate) -> HistoricoAcademico:
    """
    Insere um novo registro no histórico acadêmico.

    Utiliza try/except para tratar falhas de integridade referencial (ex: aluno_id
    ou disciplina_id inexistentes no banco). Em caso de falha, faz rollback.
    """
    db_historico = HistoricoAcademico(**historico_in.model_dump())
    db.add(db_historico)
    try:
        await db.commit()
        await db.refresh(db_historico)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o registro de histórico. Verifique se aluno_id, disciplina_id e periodo_letivo_id são válidos."
        )
    return db_historico


async def list_all_historicos(db: AsyncSession) -> List[HistoricoAcademico]:
    """Retorna todos os registros de histórico acadêmico do sistema."""
    result = await db.execute(select(HistoricoAcademico))
    return result.scalars().all()
