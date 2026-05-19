"""
Módulo de Rotas da API (API Layer) para Currículos.

Define os endpoints expostos publicamente via FastAPI para 
a entidade Currículo e os seus componentes (Disciplinas).
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.modules.curriculos.application.services import CurriculoService
from app.modules.curriculos.api.schemas import (
    CurriculoCreate, CurriculoResponse,
    CurriculoDisciplinaCreate, CurriculoDisciplinaResponse
)
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=CurriculoResponse, status_code=status.HTTP_201_CREATED)
async def create_curriculo(
    curriculo_in: CurriculoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cria um novo currículo.
    
    Requer:
    - O curso (`curso_id`) e o período letivo (`periodo_letivo_vigor_id`) devem existir.
    - O `codigo` deve ser único.
    """
    service = CurriculoService(db)
    return await service.create_curriculo(curriculo_in)

@router.get("/")
async def list_curriculos(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os currículos com suporte a paginação.
    """
    service = CurriculoService(db)
    curriculos = await service.list_curriculos(skip=0, limit=1000)
    
    total = len(curriculos)
    paginated = curriculos[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Curriculo",
            "id": str(c.id),
            "codigo": c.codigo,
            "status": c.status,
            "dataValidade": str(c.data_validade) if c.data_validade else None,
            "curso": {
                "resourceType": "Curso",
                "id": str(c.curso_id)
            },
            "periodoLetivo": {
                "resourceType": "PeriodoLetivo",
                "id": str(c.periodo_letivo_vigor_id)
            }
        }
        for c in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Curriculo?_offset={_offset}&_count={_count}",
            "next": f"/api/Curriculo?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Curriculo?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.get("/{id}")
async def get_curriculo(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém detalhes de um currículo pelo seu ID (Primary Key).
    """
    service = CurriculoService(db)
    c = await service.get_curriculo(id)
    return {
        "resourceType": "Curriculo",
        "id": str(c.id),
        "codigo": c.codigo,
        "status": c.status,
        "dataValidade": str(c.data_validade) if c.data_validade else None,
        "curso": {
            "resourceType": "Curso",
            "id": str(c.curso_id)
        },
        "periodoLetivo": {
            "resourceType": "PeriodoLetivo",
            "id": str(c.periodo_letivo_vigor_id)
        }
    }

@router.post("/{id}/disciplinas", response_model=CurriculoDisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def add_disciplina_to_curriculo(
    id: int,
    disc_in: CurriculoDisciplinaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Adiciona uma disciplina como componente a um currículo.
    
    A entidade `CurriculoDisciplina` registra a relação N:M com
    atributos adicionais (tipo e nível da disciplina naquele currículo).
    """
    service = CurriculoService(db)
    return await service.add_disciplina(id, disc_in)
