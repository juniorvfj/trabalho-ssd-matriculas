"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Currículo — modelo SIGAA.

Operações sobre SIGAA_CURRICULO, SIGAA_RL_CURRICULO_CURSO e
SIGAA_RL_CURRICULO_DISCIPLINA, reproduzindo as consultas de "Estrutura Curricular"
do arquivo SIGAA-API.sql do professor.
"""
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.curriculos.api.schemas import CurriculoCreate, CurriculoDisciplinaCreate
from app.modules.curriculos.infrastructure.orm_models import (
    Curriculo,
    CurriculoCurso,
    CurriculoDisciplina,
)
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.disciplinas.infrastructure.orm_models import Disciplina


async def search_curriculos(
    db: AsyncSession, curso: Optional[str], offset: int, count: int
) -> tuple[list[Curriculo], int]:
    """Pesquisa currículos, opcionalmente filtrando por curso (via RL), com paginação."""
    stmt = select(Curriculo)
    count_stmt = select(func.count(func.distinct(Curriculo.id)))
    if curso:
        stmt = stmt.join(CurriculoCurso, CurriculoCurso.curriculo == Curriculo.id).where(
            CurriculoCurso.curso == curso
        )
        count_stmt = count_stmt.join(
            CurriculoCurso, CurriculoCurso.curriculo == Curriculo.id
        ).where(CurriculoCurso.curso == curso)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Curriculo.id).offset(offset).limit(count))
    return list(result.scalars().all()), total


async def get_curriculo(db: AsyncSession, curriculo_id: str) -> Curriculo:
    """Busca um currículo pelo código (PK)."""
    curriculo = (await db.execute(select(Curriculo).where(Curriculo.id == curriculo_id))).scalar_one_or_none()
    if not curriculo:
        raise HTTPException(status_code=404, detail="Currículo não encontrado")
    return curriculo


async def get_disciplinas_do_curriculo(db: AsyncSession, curriculo_id: str) -> list[tuple[CurriculoDisciplina, Disciplina]]:
    """Lista as disciplinas de um currículo (SIGAA_RL_CURRICULO_DISCIPLINA + SIGAA_DISCIPLINA)."""
    result = await db.execute(
        select(CurriculoDisciplina, Disciplina)
        .join(Disciplina, Disciplina.id == CurriculoDisciplina.disciplina)
        .where(CurriculoDisciplina.curriculo == curriculo_id)
        .order_by(CurriculoDisciplina.periodo)
    )
    return list(result.all())


async def create_curriculo(db: AsyncSession, curriculo_in: CurriculoCreate) -> Curriculo:
    """Cria um novo currículo e, opcionalmente, o vínculo com um curso."""
    if (await db.execute(select(Curriculo).where(Curriculo.id == curriculo_in.id))).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Código de currículo já existe")
    if curriculo_in.curso and not (
        await db.execute(select(Curso).where(Curso.id == curriculo_in.curso))
    ).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    dados = curriculo_in.model_dump(exclude={"curso"})
    db_curriculo = Curriculo(**dados)
    db.add(db_curriculo)
    if curriculo_in.curso:
        db.add(CurriculoCurso(curriculo=curriculo_in.id, curso=curriculo_in.curso))
    await db.commit()
    await db.refresh(db_curriculo)
    return db_curriculo


async def add_disciplina(
    db: AsyncSession, curriculo_id: str, disc_in: CurriculoDisciplinaCreate
) -> CurriculoDisciplina:
    """Vincula uma disciplina a um currículo (SIGAA_RL_CURRICULO_DISCIPLINA)."""
    await get_curriculo(db, curriculo_id)
    if not (await db.execute(select(Disciplina).where(Disciplina.id == disc_in.disciplina))).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    assoc = CurriculoDisciplina(
        curriculo=curriculo_id,
        disciplina=disc_in.disciplina,
        periodo=disc_in.periodo,
        tipo=disc_in.tipo,
    )
    db.add(assoc)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Disciplina já vinculada a este currículo")
    return assoc
