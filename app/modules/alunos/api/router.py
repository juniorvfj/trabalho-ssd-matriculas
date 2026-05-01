"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Alunos
Descrição: Exposição dos serviços REST para a entidade Aluno. 
Define os contratos de API utilizando schemas de entrada (AlunoCreate) e saída (AlunoResponse).
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schemas import AlunoCreate, AlunoResponse, AlunoUpdate
from ..application.services import get_aluno_by_id, list_alunos, create_aluno
from app.api.deps import get_current_user, RoleChecker
from app.modules.usuarios.infrastructure.orm_models import RoleEnum

# Requisito de segurança: todas as rotas de Alunos exigem token JWT válido
router = APIRouter(tags=["Alunos"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=List[AlunoResponse], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.COORDENACAO, RoleEnum.PROCESSAMENTO, RoleEnum.CONSULTA]))])
async def get_all_alunos(db: AsyncSession = Depends(get_db)):
    """
    Recupera a listagem de todos os alunos cadastrados no sistema.
    """
    return await list_alunos(db)

@router.post("/", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.COORDENACAO]))])
async def post_aluno(aluno: AlunoCreate, db: AsyncSession = Depends(get_db)):
    """
    Insere um novo aluno no banco de dados.
    A validação (ex: limites de caracteres e formato de e-mail) ocorre automaticamente 
    no modelo AlunoCreate antes da execução da função.
    """
    return await create_aluno(db, aluno)

@router.get("/{id}", response_model=AlunoResponse, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.COORDENACAO, RoleEnum.PROCESSAMENTO, RoleEnum.CONSULTA]))])
async def get_aluno(id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca os dados de um aluno específico pelo seu identificador (ID).
    Caso não exista, um erro HTTP 404 será retornado.
    """
    return await get_aluno_by_id(db, id)
