"""
Módulo de Serviços de Disciplinas (Application Layer)

Concentra todas as regras de negócio para criação e consulta de Disciplinas.
Note que as exceções levantadas aqui serão tratadas globalmente e padronizadas (HTTP 400 ou 404).
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from ..infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from ..api.schemas import DisciplinaCreate, DisciplinaUpdate

async def list_disciplinas(db: AsyncSession) -> List[Disciplina]:
    """Retorna todas as disciplinas armazenadas no banco de dados."""
    result = await db.execute(select(Disciplina))
    return result.scalars().all()

async def get_disciplina_by_id(db: AsyncSession, disciplina_id: int) -> Disciplina:
    """Busca os dados de uma única disciplina através de seu ID."""
    result = await db.execute(select(Disciplina).where(Disciplina.id == disciplina_id))
    disciplina = result.scalars().first()
    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disciplina com id {disciplina_id} não encontrada"
        )
    return disciplina

async def create_disciplina(db: AsyncSession, disciplina_in: DisciplinaCreate) -> Disciplina:
    """
    Função de criação de Disciplinas.
    Utiliza um bloco try/except para capturar falhas de integridade do banco (ex: chave estrangeira
    inválida ou código duplicado). Em caso de falha, faz o 'rollback' da transação.
    """
    # TODO: verificar se curso existe previamente
    db_disciplina = Disciplina(**disciplina_in.model_dump())
    db.add(db_disciplina)
    try:
        # Tenta persistir os dados no disco
        await db.commit()
        await db.refresh(db_disciplina)
    except Exception as e:
        # Desfaz a operação em memória em caso de erro no commit
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a disciplina. Verifique se o código já existe e se o curso_id é válido."
        )
    return db_disciplina
