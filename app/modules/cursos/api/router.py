"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Cursos
Descrição: Define as rotas (endpoints REST) da entidade Curso, aplicando
as regras de contratos (Schemas Pydantic) para garantir validação de entrada/saída.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schemas import CursoCreate, CursoResponse, CursoUpdate
from ..application.services import get_curso_by_id, list_cursos, create_curso
from app.api.deps import get_current_user

# Define o agrupador de rotas e impõe o requisito de autenticação (get_current_user)
router = APIRouter(tags=["Cursos"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[CursoResponse])
async def get_all_cursos(db: AsyncSession = Depends(get_db)):
    """
    Lista todos os cursos disponíveis.
    Retorna uma lista padronizada conforme o CursoResponse (Modelo Canônico).
    """
    return await list_cursos(db)

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def post_curso(curso: CursoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cadastra um novo curso.
    Valida a carga útil da requisição pelo esquema CursoCreate.
    Retorna status 201 (Created) se houver sucesso.
    """
    return await create_curso(db, curso)

@router.get("/{id}", response_model=CursoResponse)
async def get_curso(id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca os detalhes de um curso específico pelo seu ID.
    Lança erro 404 (Not Found) se o curso não for encontrado na base.
    """
    return await get_curso_by_id(db, id)
