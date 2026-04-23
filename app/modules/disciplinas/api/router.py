"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Disciplinas
Descrição: Gerencia os endpoints das disciplinas, incluindo a definição
de pré-requisitos, créditos e carga horária.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import DisciplinaCreate, DisciplinaResponse, DisciplinaUpdate
from ..application.services import get_disciplina_by_id, list_disciplinas, create_disciplina

router = APIRouter(tags=["Disciplinas"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[DisciplinaResponse])
async def get_all_disciplinas(db: AsyncSession = Depends(get_db)):
    """
    Retorna a lista completa de disciplinas cadastradas na base.
    """
    return await list_disciplinas(db)

@router.post("/", response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def post_disciplina(disciplina: DisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria uma nova disciplina. 
    Lança erro caso o ID do curso vinculado seja inválido ou código já exista.
    """
    return await create_disciplina(db, disciplina)

@router.get("/{id}", response_model=DisciplinaResponse)
async def get_disciplina(id: int, db: AsyncSession = Depends(get_db)):
    """
    Recupera as informações detalhadas de uma disciplina pelo seu ID.
    """
    return await get_disciplina_by_id(db, id)
