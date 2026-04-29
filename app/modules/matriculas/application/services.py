"""
Módulo de Serviços de Matrícula (Application Layer)

Concentra as regras de negócio para criação, consulta e cancelamento de matrículas
e solicitações de matrícula. A camada de rotas (router) apenas recebe as requisições
e as repassa para estes serviços, facilitando reuso e testes unitários isolados.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..infrastructure.orm_models import (
    SolicitacaoMatricula, Matricula, AuditoriaProcessamento, StatusMatricula
)
from ..api.schemas import SolicitacaoMatriculaCreate, MatriculaCreate
from app.core.exceptions import BaseAPIException

from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.turmas.infrastructure.orm_models import Turma


# ═══════════════════════════════════════════════════════════════════════════════
# Serviços de SolicitacaoMatricula
# ═══════════════════════════════════════════════════════════════════════════════

async def create_solicitacao(db: AsyncSession, solicitacao_in: SolicitacaoMatriculaCreate) -> SolicitacaoMatricula:
    """
    Registra uma nova solicitação de matrícula para um aluno em uma turma.

    Validações de negócio aplicadas:
    - O aluno referenciado deve existir no banco de dados
    - A turma referenciada deve existir e estar ativa

    :param solicitacao_in: Dados da solicitação validados pelo Pydantic
    :return: Objeto SolicitacaoMatricula persistido com ID gerado
    """
    # Validar existência do aluno
    aluno = (await db.execute(select(Aluno).where(Aluno.id == solicitacao_in.aluno_id))).scalar_one_or_none()
    if not aluno:
        raise BaseAPIException(message="Aluno não encontrado.", code="ALUNO_NOT_FOUND", status_code=404)

    # Validar existência e status da turma
    turma = (await db.execute(select(Turma).where(Turma.id == solicitacao_in.turma_id))).scalar_one_or_none()
    if not turma:
        raise BaseAPIException(message="Turma não encontrada.", code="TURMA_NOT_FOUND", status_code=404)
    if not turma.ativa:
        raise BaseAPIException(message="A turma não está ativa.", code="TURMA_INATIVA", status_code=400)

    db_obj = SolicitacaoMatricula(**solicitacao_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def list_solicitacoes(db: AsyncSession) -> List[SolicitacaoMatricula]:
    """Retorna todas as solicitações de matrícula registradas no sistema."""
    result = await db.execute(select(SolicitacaoMatricula))
    return result.scalars().all()


async def get_solicitacao_by_id(db: AsyncSession, solicitacao_id: int) -> SolicitacaoMatricula:
    """Busca uma solicitação pelo ID. Lança 404 se não existir."""
    stmt = select(SolicitacaoMatricula).where(SolicitacaoMatricula.id == solicitacao_id)
    result = await db.execute(stmt)
    solicitacao = result.scalar_one_or_none()
    if not solicitacao:
        raise BaseAPIException(
            message="Solicitação de matrícula não encontrada.",
            code="SOLICITACAO_NOT_FOUND",
            status_code=404
        )
    return solicitacao


# ═══════════════════════════════════════════════════════════════════════════════
# Serviços de Matricula
# ═══════════════════════════════════════════════════════════════════════════════

async def create_matricula(db: AsyncSession, matricula_in: MatriculaCreate) -> Matricula:
    """
    Efetiva uma matrícula de aluno em uma turma.

    Normalmente chamada pelo motor de processamento batch (Fases 3/5) ou pelo
    fluxo de matrícula extraordinária. Incrementa as vagas_ocupadas da turma.

    :param matricula_in: Dados da matrícula validados pelo Pydantic
    :return: Objeto Matricula persistido com ID e data de efetivação
    """
    db_obj = Matricula(**matricula_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def list_matriculas(db: AsyncSession) -> List[Matricula]:
    """Retorna todas as matrículas efetivadas no sistema."""
    result = await db.execute(select(Matricula))
    return result.scalars().all()


async def get_matricula_by_id(db: AsyncSession, matricula_id: int) -> Matricula:
    """Busca uma matrícula pelo ID. Lança 404 se não existir."""
    stmt = select(Matricula).where(Matricula.id == matricula_id)
    result = await db.execute(stmt)
    matricula = result.scalar_one_or_none()
    if not matricula:
        raise BaseAPIException(
            message="Matrícula não encontrada.",
            code="MATRICULA_NOT_FOUND",
            status_code=404
        )
    return matricula


async def delete_matricula(db: AsyncSession, matricula_id: int) -> dict:
    """
    Cancela uma matrícula existente (soft delete via alteração de status).

    Ao cancelar, decrementa as vagas_ocupadas da turma associada,
    liberando a vaga para eventuais rematrículas ou processamentos futuros.

    :param matricula_id: ID da matrícula a ser cancelada
    :return: Dicionário de confirmação com o ID cancelado
    """
    matricula = await get_matricula_by_id(db, matricula_id)

    if matricula.status == StatusMatricula.CANCELADA:
        raise BaseAPIException(
            message="Esta matrícula já foi cancelada anteriormente.",
            code="MATRICULA_JA_CANCELADA",
            status_code=400
        )

    # Atualizar status da matrícula para CANCELADA
    matricula.status = StatusMatricula.CANCELADA

    # Liberar a vaga na turma correspondente
    turma = (await db.execute(select(Turma).where(Turma.id == matricula.turma_id))).scalar_one_or_none()
    if turma and turma.vagas_ocupadas > 0:
        turma.vagas_ocupadas -= 1

    await db.commit()
    return {"message": "Matrícula cancelada com sucesso.", "matricula_id": matricula_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Serviços de Auditoria
# ═══════════════════════════════════════════════════════════════════════════════

async def list_auditoria_by_aluno(db: AsyncSession, aluno_id: int) -> List[AuditoriaProcessamento]:
    """
    Retorna o histórico de processamento (trilha de auditoria) de um aluno.

    Permite ao coordenador rastrear todas as decisões tomadas sobre as
    solicitações de matrícula de um aluno específico, incluindo qual regra
    foi aplicada e se o resultado foi aprovação ou rejeição.
    """
    stmt = select(AuditoriaProcessamento).where(
        AuditoriaProcessamento.aluno_id == aluno_id
    ).order_by(AuditoriaProcessamento.timestamp_evento.desc())
    result = await db.execute(stmt)
    return result.scalars().all()
