"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Turmas
Descrição: Contém as operações para criação e listagem de Turmas e Períodos Letivos.
Estes endpoints são cruciais para a Fase 3 do processamento de matrículas.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import PeriodoLetivoCreate, PeriodoLetivoResponse, TurmaCreate, TurmaResponse
from ..application.services import list_periodos_letivos, create_periodo_letivo, list_turmas, create_turma

router = APIRouter(tags=["Turmas"], dependencies=[Depends(get_current_user)])

@router.get("/periodos", response_model=List[PeriodoLetivoResponse])
async def get_all_periodos(db: AsyncSession = Depends(get_db)):
    """
    Lista todos os períodos letivos (semestres acadêmicos).
    """
    return await list_periodos_letivos(db)

@router.post("/periodos", response_model=PeriodoLetivoResponse, status_code=status.HTTP_201_CREATED)
async def post_periodo(periodo: PeriodoLetivoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo período letivo, definindo a data de início, fim e código (ex: 2026.1).
    """
    return await create_periodo_letivo(db, periodo)

@router.get("/", response_model=List[TurmaResponse])
async def get_all_turmas(db: AsyncSession = Depends(get_db)):
    """
    Retorna a lista completa de turmas oferecidas.
    """
    return await list_turmas(db)

@router.post("/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def post_turma(turma: TurmaCreate, db: AsyncSession = Depends(get_db)):
    """
    Abre uma nova turma de uma disciplina em um período letivo específico.
    Define as vagas disponíveis e o horário serializado.
    """
    return await create_turma(db, turma)
