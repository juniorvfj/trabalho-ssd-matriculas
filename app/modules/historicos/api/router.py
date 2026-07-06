"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Histórico Acadêmico — modelo SIGAA.

O identificador do histórico é a matrícula do aluno. GET /{id} retorna todas as
disciplinas cursadas; GET /{id}/disciplina permite filtrar por período/disciplina.
É a principal fonte de dados do serviço verificarElegibilidade.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from ..api.schemas import HistoricoDisciplinaCreate, HistoricoDisciplinaResponse
from ..application.services import add_disciplina_ao_historico, get_historico_by_aluno

router = APIRouter(tags=["HistoricoAcademico"])


def _item(hd, disc) -> dict:
    return {
        "resourceType": "HistoricoDisciplina",
        "disciplina": {"resourceType": "Disciplina", "id": disc.id, "nome": disc.nome},
        "periodoLetivo": hd.periodo_letivo,
        "mencao": hd.mencao,
    }


@router.get("/{id}", summary="Histórico do aluno")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """Retorna o histórico (disciplinas cursadas) de um aluno pela matrícula."""
    linhas = await get_historico_by_aluno(db, id)
    items = [_item(hd, disc) for hd, disc in linhas]
    return {
        "resourceType": "HistoricoAcademico",
        "aluno": {"resourceType": "Aluno", "matricula": id},
        "total": len(items),
        "disciplinas": items,
    }


@router.get("/{id}/disciplina", response_model=SearchSet, summary="Pesquisar disciplinas no histórico")
async def search_disciplina(
    id: str,
    db: AsyncSession = Depends(get_db),
    periodoLetivo: Optional[str] = Query(None, description="Filtro por período letivo"),
    disciplina: Optional[str] = Query(None, description="Filtro por código de disciplina"),
):
    """Pesquisa disciplinas do histórico de um aluno, com filtros opcionais (SearchSet)."""
    linhas = await get_historico_by_aluno(db, id, periodoLetivo, disciplina)
    items = [_item(hd, disc) for hd, disc in linhas]
    extra = ""
    if periodoLetivo:
        extra += f"periodoLetivo={periodoLetivo}&"
    if disciplina:
        extra += f"disciplina={disciplina}&"
    return search_set(items, len(items), 0, len(items) or 1, f"/api/HistoricoAcademico/{id}/disciplina", extra)


@router.post("/disciplina", response_model=HistoricoDisciplinaResponse, status_code=status.HTTP_201_CREATED, summary="Lançar disciplina no histórico")
async def post_disciplina(historico_in: HistoricoDisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Lança uma disciplina cursada no histórico (SIGAA_RL_ALUNO_CURSO_DISCIPLINA)."""
    return await add_disciplina_ao_historico(db, historico_in)
