"""
Módulo de Rotas (API Layer) para Unidades Organizacionais

Endpoints RESTful para operações CRUD de Unidades Organizacionais.
"""
from fastapi import APIRouter, Depends, status
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

router = APIRouter(prefix="/unidades-organizacionais", tags=["Unidades Organizacionais"])


@router.get("/", response_model=List[UnidadeOrganizacionalResponse], summary="Listar todas as unidades organizacionais")
async def list_unidades(db: AsyncSession = Depends(get_db)):
    """Retorna a lista completa de unidades organizacionais (departamentos, institutos)."""
    return await list_all_unidades(db)


@router.post("/", response_model=UnidadeOrganizacionalResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar nova unidade organizacional")
async def create_new_unidade(unidade_in: UnidadeOrganizacionalCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra uma nova unidade organizacional no sistema."""
    return await create_unidade(db, unidade_in)


@router.get("/{unidade_id}", response_model=UnidadeOrganizacionalResponse, summary="Buscar unidade organizacional por ID")
async def get_unidade(unidade_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de uma unidade organizacional específica pelo seu ID."""
    return await get_unidade_by_id(db, unidade_id)
