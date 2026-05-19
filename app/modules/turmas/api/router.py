"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Turmas
Descrição: Contém as operações para criação e listagem de Turmas e Períodos Letivos.
Estes endpoints são cruciais para a Fase 3 do processamento de matrículas.
"""
from fastapi import APIRouter, Depends, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import PeriodoLetivoCreate, PeriodoLetivoResponse, TurmaCreate, TurmaResponse
from ..application.services import list_periodos_letivos, create_periodo_letivo, list_turmas, create_turma

router = APIRouter(tags=["Turmas"], dependencies=[Depends(get_current_user)])

@router.get("/periodos")
async def get_all_periodos(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """
    Lista todos os períodos letivos (semestres acadêmicos).
    """
    periodos = await list_periodos_letivos(db)
    
    total = len(periodos)
    paginated = periodos[_offset : _offset + _count]

    items = [
        {
            "resourceType": "PeriodoLetivo",
            "id": str(p.id),
            "codigo": p.codigo,
            "descricao": p.descricao,
            "ano": p.ano,
            "periodo": p.periodo,
            "dataInicio": str(p.data_inicio),
            "dataFim": str(p.data_fim),
            "ativo": p.ativo
        }
        for p in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Turma/periodos?_offset={_offset}&_count={_count}",
            "next": f"/api/Turma/periodos?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Turma/periodos?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.post("/periodos", response_model=PeriodoLetivoResponse, status_code=status.HTTP_201_CREATED)
async def post_periodo(periodo: PeriodoLetivoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo período letivo, definindo a data de início, fim e código (ex: 2026.1).
    """
    return await create_periodo_letivo(db, periodo)

@router.get("/")
async def get_all_turmas(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """
    Retorna a lista completa de turmas oferecidas.
    """
    turmas = await list_turmas(db)
    
    total = len(turmas)
    paginated = turmas[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Turma",
            "id": str(t.id),
            "disciplina": {
                "resourceType": "Disciplina",
                "id": str(t.disciplina_id)
            },
            "periodoLetivo": {
                "resourceType": "PeriodoLetivo",
                "id": str(t.periodo_letivo_id)
            },
            "codigoTurma": t.codigo_turma,
            "vagasTotais": t.vagas_totais,
            "vagasOcupadas": getattr(t, 'vagas_ocupadas', 0),
            "horarioSerializado": t.horario_serializado,
            "status": t.status,
            "ativa": t.ativa
        }
        for t in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Turma?_offset={_offset}&_count={_count}",
            "next": f"/api/Turma?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Turma?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.post("/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def post_turma(turma: TurmaCreate, db: AsyncSession = Depends(get_db)):
    """
    Abre uma nova turma de uma disciplina em um período letivo específico.
    Define as vagas disponíveis e o horário serializado.
    """
    return await create_turma(db, turma)
