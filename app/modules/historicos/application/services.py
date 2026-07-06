"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Histórico Acadêmico — modelo SIGAA.

Consultas sobre SIGAA_RL_ALUNO_CURSO_DISCIPLINA, unindo com SIGAA_RL_ALUNO_CURSO
(para chegar à matrícula do aluno) e com SIGAA_DISCIPLINA (para dados da disciplina).
Fornece também a base para a verificação de elegibilidade (disciplinas aprovadas).
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alunos.infrastructure.orm_models import Aluno, AlunoCurso
from app.modules.disciplinas.infrastructure.orm_models import Disciplina
from ..api.schemas import HistoricoDisciplinaCreate
from ..infrastructure.orm_models import HistoricoDisciplina

# Menções consideradas de aprovação no SIGAA (SS=Superior, MS=Médio Superior, MM=Médio)
MENCOES_APROVACAO = {"SS", "MS", "MM"}


async def get_historico_by_aluno(
    db: AsyncSession,
    matricula: str,
    periodo_letivo: Optional[str] = None,
    disciplina: Optional[str] = None,
) -> list[tuple[HistoricoDisciplina, Disciplina]]:
    """
    Retorna as disciplinas cursadas por um aluno (todas as suas linhas de histórico),
    opcionalmente filtrando por período letivo e/ou disciplina.
    """
    # Garante que o aluno existe
    if not (await db.execute(select(Aluno).where(Aluno.matricula == matricula))).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Aluno '{matricula}' não encontrado"
        )

    filtros = [AlunoCurso.aluno == matricula]
    if periodo_letivo:
        filtros.append(HistoricoDisciplina.periodo_letivo == periodo_letivo)
    if disciplina:
        filtros.append(HistoricoDisciplina.disciplina == disciplina)

    result = await db.execute(
        select(HistoricoDisciplina, Disciplina)
        .join(AlunoCurso, AlunoCurso.id == HistoricoDisciplina.aluno_curso)
        .join(Disciplina, Disciplina.id == HistoricoDisciplina.disciplina)
        .where(*filtros)
        .order_by(HistoricoDisciplina.periodo_letivo)
    )
    return list(result.all())


async def disciplinas_aprovadas(db: AsyncSession, matricula: str) -> set[str]:
    """Retorna o conjunto de códigos de disciplina já aprovadas pelo aluno."""
    result = await db.execute(
        select(HistoricoDisciplina.disciplina)
        .join(AlunoCurso, AlunoCurso.id == HistoricoDisciplina.aluno_curso)
        .where(AlunoCurso.aluno == matricula, HistoricoDisciplina.mencao.in_(MENCOES_APROVACAO))
    )
    return {row[0] for row in result.all()}


async def add_disciplina_ao_historico(
    db: AsyncSession, historico_in: HistoricoDisciplinaCreate
) -> HistoricoDisciplina:
    """Lança uma disciplina cursada no histórico (SIGAA_RL_ALUNO_CURSO_DISCIPLINA)."""
    registro = HistoricoDisciplina(**historico_in.model_dump())
    db.add(registro)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível lançar a disciplina no histórico. Verifique vínculo/disciplina/período.",
        )
    return registro
