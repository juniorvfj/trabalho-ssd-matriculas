"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Matrículas
Descrição: Exposição dos serviços REST para solicitação, efetivação, consulta e
cancelamento de matrículas. Integra o serviço de tarefa 'verificarElegibilidade'
(§5.2, §7.1), o processamento batch (Fases 3 e 5, §7.2–§7.4), a matrícula
extraordinária (§7.5) e os endpoints de comprovante e auditoria.
"""
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import (
    SolicitacaoMatriculaCreate, SolicitacaoMatriculaResponse,
    MatriculaCreate, MatriculaResponse,
    AuditoriaProcessamentoResponse,
    ElegibilidadeRequest, ElegibilidadeResponse,
    ProcessamentoRequest, ProcessamentoResponse,
    ExtraordinariaRequest,
    ComprovanteMatriculaResponse, ComprovanteMatriculaItem,
)
from ..application.services import (
    create_solicitacao, list_solicitacoes, get_solicitacao_by_id,
    create_matricula, list_matriculas, get_matricula_by_id, delete_matricula,
    list_auditoria_by_aluno,
)
from ..application.elegibilidade import verificar_elegibilidade
from ..application.processamento import processar_fase
from ..application.extraordinaria import processar_extraordinaria

from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.turmas.infrastructure.orm_models import Turma
from app.modules.matriculas.infrastructure.orm_models import Matricula, StatusMatricula
from sqlalchemy import select
from sqlalchemy.orm import selectinload


# Requisito de segurança: todas as rotas de Matrículas exigem token JWT válido
router = APIRouter(tags=["Matrículas"], dependencies=[Depends(get_current_user)])

# Router separado para o serviço de tarefa, com tag própria para melhor organização no Swagger
tarefas_router = APIRouter(tags=["Serviço de Tarefa"], dependencies=[Depends(get_current_user)])


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints de Solicitação de Matrícula
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/solicitacoes", response_model=List[SolicitacaoMatriculaResponse])
async def get_all_solicitacoes(db: AsyncSession = Depends(get_db)):
    """
    Retorna todas as solicitações de matrícula registradas no sistema.
    Útil para visão administrativa e monitoramento do pipeline de processamento.
    """
    return await list_solicitacoes(db)


@router.get("/solicitacoes/{id}", response_model=SolicitacaoMatriculaResponse)
async def get_solicitacao(id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca os dados de uma solicitação de matrícula específica pelo ID.
    Caso não exista, retorna HTTP 404.
    """
    return await get_solicitacao_by_id(db, id)


@router.post("/solicitacoes", response_model=SolicitacaoMatriculaResponse, status_code=status.HTTP_201_CREATED)
async def post_solicitacao(solicitacao: SolicitacaoMatriculaCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra uma nova solicitação de matrícula de um aluno em uma turma.

    Validações aplicadas:
    - O aluno referenciado deve existir
    - A turma referenciada deve existir e estar ativa
    - Os dados de entrada são validados automaticamente pelo Pydantic
    """
    return await create_solicitacao(db, solicitacao)


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints de Matrícula (efetivada)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[MatriculaResponse])
async def get_all_matriculas(db: AsyncSession = Depends(get_db)):
    """
    Retorna a lista completa de matrículas efetivadas no sistema.
    Inclui matrículas ativas, canceladas e trancadas.
    """
    return await list_matriculas(db)


@router.get("/{id}", response_model=MatriculaResponse)
async def get_matricula(id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca os dados de uma matrícula específica pelo seu identificador.
    Caso não exista, retorna HTTP 404.
    """
    return await get_matricula_by_id(db, id)


@router.delete("/{id}")
async def cancel_matricula(id: int, db: AsyncSession = Depends(get_db)):
    """
    Cancela uma matrícula existente (soft delete via alteração de status).

    Ao cancelar, a vaga correspondente na turma é liberada automaticamente,
    permitindo que outro aluno possa ocupá-la em processamentos futuros.
    """
    return await delete_matricula(db, id)


# ═══════════════════════════════════════════════════════════════════════════════
# Serviço de Tarefa — verificarElegibilidade (§5.2, §7.1)
# ═══════════════════════════════════════════════════════════════════════════════

@tarefas_router.post("/verificar-elegibilidade", response_model=ElegibilidadeResponse)
async def post_verificar_elegibilidade(request: ElegibilidadeRequest, db: AsyncSession = Depends(get_db)):
    """
    Serviço de Tarefa — verificarElegibilidade (§5.2, §7.1)

    Avalia se um aluno está apto a cursar uma determinada disciplina,
    verificando três regras obrigatórias:
    1. A disciplina pertence ao currículo do curso do aluno
    2. O aluno ainda não foi aprovado nessa disciplina
    3. O aluno possui todos os pré-requisitos cumpridos

    Retorna um resultado detalhado com 'elegivel' (bool), 'motivos' (lista
    de impedimentos quando inelegível) e 'detalhes' (informações para depuração).
    """
    return await verificar_elegibilidade(db, request.aluno_id, request.disciplina_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Processamento Batch — Fases 3 e 5 (§7.2–§7.4)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/processamento/fase-3", response_model=ProcessamentoResponse)
async def post_processamento_fase_3(request: ProcessamentoRequest, db: AsyncSession = Depends(get_db)):
    """
    Dispara o processamento batch da Fase 3 para um período letivo (§7.2–§7.4).

    Avalia todas as solicitações PENDENTES da FASE_3, aplicando as 4 regras
    de negócio (R1–R4) e efetivando as matrículas aprovadas.
    """
    return await processar_fase(db, request.periodo_letivo_id, "FASE_3")


@router.post("/processamento/fase-5", response_model=ProcessamentoResponse)
async def post_processamento_fase_5(request: ProcessamentoRequest, db: AsyncSession = Depends(get_db)):
    """
    Dispara o reprocessamento da Fase 5 para um período letivo (§7.4).

    Funciona de forma idêntica à Fase 3, mas processa apenas as solicitações
    marcadas como FASE_5, tipicamente usadas para rematrículas e ajustes.
    """
    return await processar_fase(db, request.periodo_letivo_id, "FASE_5")


# ═══════════════════════════════════════════════════════════════════════════════
# Matrícula Extraordinária (§7.5)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/extraordinaria")
async def post_extraordinaria(request: ExtraordinariaRequest, db: AsyncSession = Depends(get_db)):
    """
    Processa uma matrícula extraordinária de forma imediata (§7.5).

    Diferentemente do batch, não há concorrência: o aluno solicita e a matrícula
    é efetivada imediatamente se todas as regras (R1, R3, R4) forem aprovadas.
    """
    return await processar_extraordinaria(db, request.aluno_id, request.turma_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Comprovante de Matrícula e Histórico de Processamento
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/alunos/{aluno_id}/comprovante-matricula", response_model=ComprovanteMatriculaResponse)
async def get_comprovante_matricula(aluno_id: int, periodo_letivo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Gera o comprovante de matrícula de um aluno para um período letivo.

    Lista todas as disciplinas/turmas em que o aluno está matriculado,
    incluindo horários, créditos e status de cada matrícula.
    """
    # Buscar aluno
    aluno = (await db.execute(select(Aluno).where(Aluno.id == aluno_id))).scalar_one_or_none()
    if not aluno:
        from app.core.exceptions import BaseAPIException
        raise BaseAPIException(message="Aluno não encontrado.", code="ALUNO_NOT_FOUND", status_code=404)

    # Buscar matrículas ativas do aluno no período
    matriculas = (await db.execute(
        select(Matricula)
        .where(
            Matricula.aluno_id == aluno_id,
            Matricula.periodo_letivo_id == periodo_letivo_id,
        )
    )).scalars().all()

    # Montar lista de disciplinas com detalhes
    disciplinas = []
    total_creditos = 0
    for mat in matriculas:
        turma = (await db.execute(
            select(Turma).options(selectinload(Turma.disciplina)).where(Turma.id == mat.turma_id)
        )).scalar_one_or_none()
        if turma and turma.disciplina:
            creditos = turma.disciplina.creditos
            if mat.status.value == "ATIVA":
                total_creditos += creditos
            disciplinas.append(ComprovanteMatriculaItem(
                matricula_id=mat.id,
                disciplina_nome=turma.disciplina.nome,
                turma_codigo=turma.codigo_turma,
                horario=turma.horario_serializado,
                creditos=creditos,
                status=mat.status.value,
            ))

    return ComprovanteMatriculaResponse(
        aluno_id=aluno.id,
        aluno_nome=aluno.nome,
        aluno_matricula=aluno.matricula,
        periodo_letivo_id=periodo_letivo_id,
        total_creditos=total_creditos,
        disciplinas=disciplinas,
    )


@router.get("/alunos/{aluno_id}/historico-processamento", response_model=List[AuditoriaProcessamentoResponse])
async def get_historico_processamento(aluno_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna a trilha de auditoria de processamento de um aluno.

    Permite ao coordenador rastrear todas as decisões tomadas sobre
    as solicitações de matrícula do aluno, incluindo qual regra foi
    aplicada (R1–R4) e se o resultado foi aprovação ou rejeição.
    """
    return await list_auditoria_by_aluno(db, aluno_id)
