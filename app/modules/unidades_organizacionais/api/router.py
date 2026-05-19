"""
Módulo de Rotas (API Layer) para Unidades Organizacionais

Endpoints RESTful para operações CRUD de Unidades Organizacionais.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.modules.unidades_organizacionais.api.schemas import (
    UnidadeOrganizacionalCreate,
    UnidadeOrganizacionalResponse,
)
from app.modules.unidades_organizacionais.application.services import (
    create_unidade,
    list_all_unidades,
    get_unidade_by_id,
)

router = APIRouter(tags=["Unidades Organizacionais"])


@router.get("/", summary="Listar todas as unidades organizacionais")
async def list_unidades(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """Retorna a lista completa de unidades organizacionais (departamentos, institutos)."""
    unidades = await list_all_unidades(db)
    
    total = len(unidades)
    paginated = unidades[_offset : _offset + _count]

    items = [
        {
            "resourceType": "UnidadeOrganizacional",
            "id": str(u.id),
            "codigo": u.codigo,
            "nome": u.nome,
            "ativo": u.ativo
        }
        for u in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/UnidadeOrganizacional?_offset={_offset}&_count={_count}",
            "next": f"/api/UnidadeOrganizacional?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/UnidadeOrganizacional?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }


@router.post("/", response_model=UnidadeOrganizacionalResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar nova unidade organizacional")
async def create_new_unidade(unidade_in: UnidadeOrganizacionalCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra uma nova unidade organizacional no sistema."""
    return await create_unidade(db, unidade_in)


@router.get("/{unidade_id}", summary="Buscar unidade organizacional por ID")
async def get_unidade(unidade_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de uma unidade organizacional específica pelo seu ID."""
    u = await get_unidade_by_id(db, unidade_id)
    return {
        "resourceType": "UnidadeOrganizacional",
        "id": str(u.id),
        "codigo": u.codigo,
        "nome": u.nome,
        "ativo": u.ativo
    }
