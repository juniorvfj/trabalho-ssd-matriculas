"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Histórico Acadêmico
Descrição: Expõe os endpoints REST para o histórico acadêmico consolidado
dos alunos (1:1) e para os itens individuais de disciplinas cursadas.
O endpoint GET por aluno_id é a principal fonte de dados para o serviço
verificarElegibilidade.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import (
    HistoricoAcademicoCreate,
    HistoricoAcademicoResponse,
    HistoricoDisciplinaCreate,
    HistoricoDisciplinaResponse,
)
from ..application.services import (
    get_historico_by_aluno,
    create_historico,
    add_disciplina_to_historico,
    list_all_historicos,
)

# Todas as rotas de Histórico exigem autenticação JWT
router = APIRouter(tags=["Histórico Acadêmico"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[HistoricoAcademicoResponse])
async def get_all_historicos(db: AsyncSession = Depends(get_db)):
    """
    Retorna todos os históricos acadêmicos consolidados do sistema.
    Útil para visão administrativa geral.
    """
    return await list_all_historicos(db)


@router.get("/{aluno_id}", response_model=HistoricoAcademicoResponse)
async def get_historico_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    """
    Recupera o histórico acadêmico consolidado de um aluno específico.

    Retorna o status geral do vínculo (ATIVO, INATIVO, CONCLUIDO),
    carga horária integralizada/pendente e a lista de disciplinas cursadas
    com menção, frequência e status individual.
    """
    return await get_historico_by_aluno(db, aluno_id)


@router.post("/", response_model=HistoricoAcademicoResponse, status_code=status.HTTP_201_CREATED)
async def post_historico(historico: HistoricoAcademicoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria o histórico acadêmico consolidado de um aluno.

    Como a relação é 1:1, cada aluno pode ter no máximo um histórico.
    """
    return await create_historico(db, historico)


@router.post("/{aluno_id}/disciplinas", response_model=HistoricoDisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def post_disciplina_historico(
    aluno_id: int,
    disciplina: HistoricoDisciplinaCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Adiciona um registro de disciplina cursada ao histórico acadêmico de um aluno.

    Validações:
    - O aluno deve ter um histórico acadêmico cadastrado
    - disciplina_id e periodo_letivo_id devem ser válidos
    - status deve ser um dos valores do Enum (APROVADO, REPROVADO, TRANCADO, CURSANDO)
    """
    return await add_disciplina_to_historico(db, aluno_id, disciplina)
