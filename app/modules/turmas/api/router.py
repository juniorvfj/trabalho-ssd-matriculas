"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Turma — modelo SIGAA (SIGAA_TURMA + SIGAA_TURMA_HORARIOAULA).

Os antigos endpoints de /periodos foram removidos: no SIGAA o período letivo é um
campo texto na própria turma (ex.: '20182'), não uma entidade. Em seu lugar há os
endpoints de horário de aula (/horarios).
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from .schemas import HorarioAulaCreate, HorarioAulaResponse, TurmaCreate, TurmaResponse
from ..application.services import (
    create_horario,
    create_turma,
    get_turma_by_id,
    list_horarios,
    search_turmas,
)

router = APIRouter(tags=["Turma"])


def _turma_item(t) -> dict:
    return {
        "resourceType": "Turma",
        "id": str(t.id),
        "codigo": t.codigo,
        "periodoLetivo": t.periodo_letivo,
        "disciplina": {"resourceType": "Disciplina", "id": t.disciplina},
        "vagas": int(t.vagas) if t.vagas is not None else None,
        "sede": t.sede,
    }


@router.get("/horarios", response_model=SearchSet, summary="Listar horários de aula")
async def get_all_horarios(db: AsyncSession = Depends(get_db)):
    """Lista os slots de horário de aula (SIGAA_TURMA_HORARIOAULA)."""
    horarios = await list_horarios(db)
    items = [
        {
            "resourceType": "HorarioAula",
            "id": h.id,
            "dia": h.dia,
            "horaInicio": h.hora_inicio,
            "horaFim": h.hora_fim,
        }
        for h in horarios
    ]
    return search_set(items, len(items), 0, len(items) or 1, "/api/Turma/horarios")


@router.post("/horarios", response_model=HorarioAulaResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar horário de aula")
async def post_horario(horario: HorarioAulaCreate, db: AsyncSession = Depends(get_db)):
    """Cria um slot de horário de aula."""
    return await create_horario(db, horario)


@router.get("/", response_model=SearchSet, summary="Pesquisar turmas")
async def get_all_turmas(
    db: AsyncSession = Depends(get_db),
    periodoLetivo: Optional[str] = Query(None, description="Filtro por período letivo (ex.: '20182')"),
    disciplina: Optional[str] = Query(None, description="Filtro por código de disciplina"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa turmas por período letivo e/ou disciplina (SearchSet)."""
    turmas, total = await search_turmas(db, periodoLetivo, disciplina, _offset, _count)
    extra = ""
    if periodoLetivo:
        extra += f"periodoLetivo={periodoLetivo}&"
    if disciplina:
        extra += f"disciplina={disciplina}&"
    return search_set([_turma_item(t) for t in turmas], total, _offset, _count, "/api/Turma", extra)


@router.post("/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar turma")
async def post_turma(turma: TurmaCreate, db: AsyncSession = Depends(get_db)):
    """Abre uma nova turma de uma disciplina num período letivo."""
    return await create_turma(db, turma)


@router.get("/{id}", summary="Buscar turma por ID")
async def get_turma(id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de uma turma pelo seu ID."""
    t = await get_turma_by_id(db, id)
    return _turma_item(t)
