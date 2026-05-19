"""
Módulo de Rotas (API Layer) para Docentes

Endpoints RESTful para operações CRUD de Docentes
e vinculação de docentes a turmas.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.modules.docentes.api.schemas import (
    DocenteCreate,
    DocenteResponse,
    TurmaDocenteCreate,
    TurmaDocenteResponse,
)
from app.modules.docentes.application.services import (
    create_docente,
    list_all_docentes,
    get_docente_by_id,
    vincular_docente_turma,
    listar_docentes_turma,
)

router = APIRouter(tags=["Docentes"])


@router.get("/", summary="Listar todos os docentes")
async def list_docentes(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """Retorna a lista completa de docentes cadastrados no sistema."""
    docentes = await list_all_docentes(db)
    
    total = len(docentes)
    paginated = docentes[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Docente",
            "id": str(d.id),
            "matricula": d.matricula,
            "nome": d.nome,
            "ativo": d.ativo
        }
        for d in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Docente?_offset={_offset}&_count={_count}",
            "next": f"/api/Docente?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Docente?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }


@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo docente")
async def create_new_docente(docente_in: DocenteCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra um novo docente no sistema."""
    return await create_docente(db, docente_in)


@router.get("/{docente_id}", summary="Buscar docente por ID")
async def get_docente(docente_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de um docente específico pelo seu ID."""
    d = await get_docente_by_id(db, docente_id)
    return {
        "resourceType": "Docente",
        "id": str(d.id),
        "matricula": d.matricula,
        "nome": d.nome,
        "ativo": d.ativo
    }


@router.post("/turma-docente", response_model=TurmaDocenteResponse, status_code=status.HTTP_201_CREATED, summary="Vincular docente a turma")
async def vincular_docente_a_turma(vinculo_in: TurmaDocenteCreate, db: AsyncSession = Depends(get_db)):
    """Vincula um docente a uma turma (relação N:M do diagrama de entidades)."""
    return await vincular_docente_turma(db, vinculo_in)


@router.get("/turma/{turma_id}/docentes", response_model=List[TurmaDocenteResponse], summary="Listar docentes de uma turma")
async def list_docentes_by_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    """Lista todos os docentes vinculados a uma turma específica."""
    return await listar_docentes_turma(db, turma_id)
