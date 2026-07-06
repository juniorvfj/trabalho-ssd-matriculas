"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Disciplina — modelo SIGAA.

Consultas sobre SIGAA_DISCIPLINA, SIGAA_UNIDADE e SIGAA_PREREQ, reproduzindo as
junções do arquivo de referência SIGAA-API.sql do professor. As cargas horárias
são armazenadas como Numeric; convertemos para int nas respostas por conveniência.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas import DisciplinaCreate, PrerequisitoCreate
from ..infrastructure.orm_models import Disciplina, DisciplinaPrerequisito


async def search_disciplinas(
    db: AsyncSession,
    nome: Optional[str],
    modalidade: Optional[str],
    unidade: Optional[str],
    offset: int,
    count: int,
) -> tuple[list[Disciplina], int]:
    """Pesquisa disciplinas por nome/modalidade/unidade, com paginação."""
    filtros = []
    if nome:
        filtros.append(Disciplina.nome.ilike(f"%{nome}%"))
    if modalidade:
        filtros.append(Disciplina.modalidade == modalidade)
    if unidade:
        filtros.append(Disciplina.unidade == unidade)

    total = (await db.execute(select(func.count()).select_from(Disciplina).where(*filtros))).scalar_one()
    result = await db.execute(
        select(Disciplina).where(*filtros).order_by(Disciplina.nome).offset(offset).limit(count)
    )
    return list(result.scalars().all()), total


async def get_disciplina_by_id(db: AsyncSession, disciplina_id: str) -> Disciplina:
    """Busca uma disciplina pelo código (PK)."""
    disciplina = (
        await db.execute(select(Disciplina).where(Disciplina.id == disciplina_id))
    ).scalar_one_or_none()
    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disciplina '{disciplina_id}' não encontrada",
        )
    return disciplina


async def get_prerequisitos(db: AsyncSession, disciplina_id: str) -> list[Disciplina]:
    """Retorna as disciplinas que são pré-requisito da disciplina informada (SIGAA_PREREQ)."""
    result = await db.execute(
        select(Disciplina)
        .join(DisciplinaPrerequisito, DisciplinaPrerequisito.disciplina_requerido == Disciplina.id)
        .where(DisciplinaPrerequisito.disciplina_requer == disciplina_id)
    )
    return list(result.scalars().all())


async def create_disciplina(db: AsyncSession, disciplina_in: DisciplinaCreate) -> Disciplina:
    """Cria uma nova disciplina, validando integridade (código único, unidade válida)."""
    db_disciplina = Disciplina(**disciplina_in.model_dump())
    db.add(db_disciplina)
    try:
        await db.commit()
        await db.refresh(db_disciplina)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar a disciplina. Verifique o código e a unidade informada.",
        )
    return db_disciplina


async def add_prerequisito(
    db: AsyncSession, disciplina_id: str, prereq_in: PrerequisitoCreate
) -> DisciplinaPrerequisito:
    """Vincula uma disciplina como pré-requisito de outra (SIGAA_PREREQ)."""
    vinculo = DisciplinaPrerequisito(
        disciplina_requer=disciplina_id,
        disciplina_requerido=prereq_in.disciplina_requerido,
    )
    db.add(vinculo)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível vincular o pré-requisito. Verifique se as disciplinas existem.",
        )
    return vinculo
