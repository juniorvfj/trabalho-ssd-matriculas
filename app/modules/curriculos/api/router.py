"""
Módulo de Rotas da API (API Layer) para Currículos.

Define os endpoints expostos publicamente via FastAPI para 
a entidade Currículo e os seus componentes (Disciplinas).
"""
from fastapi import APIRouter, Depends, status
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

@router.get("/", response_model=List[CurriculoResponse])
async def list_curriculos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os currículos com suporte a paginação (skip, limit).
    """
    service = CurriculoService(db)
    return await service.list_curriculos(skip=skip, limit=limit)

@router.get("/{id}", response_model=CurriculoResponse)
async def get_curriculo(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém detalhes de um currículo pelo seu ID (Primary Key).
    """
    service = CurriculoService(db)
    return await service.get_curriculo(id)

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
