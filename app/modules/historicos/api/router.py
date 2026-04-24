"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Histórico Acadêmico
Descrição: Expõe os endpoints REST para consulta e inserção de registros
no histórico acadêmico dos alunos. O endpoint GET por aluno_id é a
principal fonte de dados para o serviço verificarElegibilidade.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import HistoricoAcademicoCreate, HistoricoAcademicoResponse
from ..application.services import get_historico_by_aluno, create_historico, list_all_historicos

# Todas as rotas de Histórico exigem autenticação JWT
router = APIRouter(tags=["Histórico Acadêmico"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[HistoricoAcademicoResponse])
async def get_all_historicos(db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os registros de histórico acadêmico do sistema.
    Útil para visão administrativa geral.
    """
    return await list_all_historicos(db)


@router.get("/{aluno_id}", response_model=List[HistoricoAcademicoResponse])
async def get_historico_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    """
    Recupera o histórico acadêmico completo de um aluno específico.

    Retorna a lista de todas as disciplinas cursadas, com status (APROVADO,
    REPROVADO, TRANCADO, CURSANDO) e nota final. Este endpoint é a base
    de consulta do serviço 'verificarElegibilidade'.
    """
    return await get_historico_by_aluno(db, aluno_id)


@router.post("/", response_model=HistoricoAcademicoResponse, status_code=status.HTTP_201_CREATED)
async def post_historico(historico: HistoricoAcademicoCreate, db: AsyncSession = Depends(get_db)):
    """
    Insere um novo registro no histórico acadêmico de um aluno.

    Validações automáticas pelo Pydantic:
    - nota_final deve estar entre 0.0 e 10.0
    - status deve ser um dos valores do Enum (APROVADO, REPROVADO, TRANCADO, CURSANDO)
    """
    return await create_historico(db, historico)
