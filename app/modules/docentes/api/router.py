"""
Módulo de Rotas (API Layer) para Docentes

Endpoints RESTful para operações CRUD de Docentes
e vinculação de docentes a turmas.
"""
from fastapi import APIRouter, Depends, status
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

router = APIRouter(prefix="/docentes", tags=["Docentes"])


@router.get("/", response_model=List[DocenteResponse], summary="Listar todos os docentes")
async def list_docentes(db: AsyncSession = Depends(get_db)):
    """Retorna a lista completa de docentes cadastrados no sistema."""
    return await list_all_docentes(db)


@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo docente")
async def create_new_docente(docente_in: DocenteCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra um novo docente no sistema."""
    return await create_docente(db, docente_in)


@router.get("/{docente_id}", response_model=DocenteResponse, summary="Buscar docente por ID")
async def get_docente(docente_id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de um docente específico pelo seu ID."""
    return await get_docente_by_id(db, docente_id)


@router.post("/turma-docente", response_model=TurmaDocenteResponse, status_code=status.HTTP_201_CREATED, summary="Vincular docente a turma")
async def vincular_docente_a_turma(vinculo_in: TurmaDocenteCreate, db: AsyncSession = Depends(get_db)):
    """Vincula um docente a uma turma (relação N:M do diagrama de entidades)."""
    return await vincular_docente_turma(db, vinculo_in)


@router.get("/turma/{turma_id}/docentes", response_model=List[TurmaDocenteResponse], summary="Listar docentes de uma turma")
async def list_docentes_by_turma(turma_id: int, db: AsyncSession = Depends(get_db)):
    """Lista todos os docentes vinculados a uma turma específica."""
    return await listar_docentes_turma(db, turma_id)
