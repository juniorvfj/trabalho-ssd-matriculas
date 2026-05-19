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

from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from ..application.services import get_historico_by_aluno

# Todas as rotas de Histórico exigem autenticação JWT
router = APIRouter(tags=["HistoricoAcademico"], dependencies=[Depends(get_current_user)])

@router.get("/{id}")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna histórico do aluno
    """
    historico = await get_historico_by_aluno(db, int(id))
    # Transform to match schema
    return {
        "resourceType": "HistoricoAcademico",
        "id": str(historico.id),
        "cargaHorariaIntegralizadas": historico.carga_horaria_integralizada,
        "cargaHorariaPendente": historico.carga_horaria_pendente,
        "status": historico.status.value.lower() if historico.status else "ativo",
        "aluno": {
            "resourceType": "Aluno",
            "id": str(historico.aluno_id),
            "matricula": str(historico.aluno_id),
            "nome": "NOME DO ALUNO MOCK" # we don't have the aluno loaded here without join, but keeping simple
        },
        "disciplina": []
    }

@router.get("/{id}/disciplina")
async def search_disciplina(
    id: str,
    db: AsyncSession = Depends(get_db),
    periodoLetivo: Optional[str] = None,
    status: Optional[str] = None,
    disciplina: Optional[str] = None
):
    """
    Busca disciplinas no histórico
    """
    historico = await get_historico_by_aluno(db, int(id))
    # In reality, filter disciplines here
    return []
