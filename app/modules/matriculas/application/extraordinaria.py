"""
Módulo de Matrícula Extraordinária (Application Layer)

Implementa o fluxo de matrícula extraordinária (§7.5), que é processado
de forma imediata (não batch). O aluno solicita a matrícula em uma turma
com vagas disponíveis, sem concorrência com outros alunos.

As regras de elegibilidade (R1) e validação por aluno (R3) são aplicadas,
mas não há ordenação por IRA (R2) — o processamento é first-come-first-served.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from ..infrastructure.orm_models import (
    SolicitacaoMatricula, Matricula, AuditoriaProcessamento,
    StatusSolicitacao, StatusMatricula,
)
from .elegibilidade import verificar_elegibilidade

from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.turmas.infrastructure.orm_models import Turma
from app.core.exceptions import BaseAPIException


async def processar_extraordinaria(
    db: AsyncSession, aluno_id: int, turma_id: int
) -> dict:
    """
    Processa uma matrícula extraordinária (§7.5) de forma imediata.

    Diferentemente do processamento batch (Fases 3/5), a matrícula extraordinária:
    - Não passa por ordenação por IRA (R2)
    - É processada imediatamente (first-come-first-served)
    - Requer que a turma tenha vagas disponíveis

    Regras aplicadas:
    - R1: Elegibilidade (pré-requisitos, currículo, aprovação prévia)
    - R3: Limite de créditos, disciplina duplicada, conflito de horário
    - R4: Disponibilidade de vagas

    :param aluno_id: ID do aluno solicitante
    :param turma_id: ID da turma desejada
    :return: Dicionário com resultado do processamento e matrícula criada
    """
    fase = "EXTRAORDINARIA"

    # ─── Validar existência do aluno ───
    aluno = (await db.execute(select(Aluno).where(Aluno.id == aluno_id))).scalar_one_or_none()
    if not aluno:
        raise BaseAPIException(message="Aluno não encontrado.", code="ALUNO_NOT_FOUND", status_code=404)

    # ─── Validar existência e status da turma ───
    turma = (await db.execute(
        select(Turma).options(selectinload(Turma.disciplina)).where(Turma.id == turma_id)
    )).scalar_one_or_none()
    if not turma:
        raise BaseAPIException(message="Turma não encontrada.", code="TURMA_NOT_FOUND", status_code=404)
    if not turma.ativa:
        raise BaseAPIException(message="A turma não está ativa.", code="TURMA_INATIVA", status_code=400)

    disciplina = turma.disciplina

    # ═══════════════════════════════════════════════════════════════════
    # R1 — Elegibilidade (§7.1)
    # ═══════════════════════════════════════════════════════════════════
    eleg = await verificar_elegibilidade(db, aluno_id, disciplina.id)
    if not eleg["elegivel"]:
        motivo = "; ".join(eleg["motivos"])
        _registrar_auditoria_sync(db, aluno_id, turma_id, fase, "R1_ELEGIBILIDADE", "REJEITADO", motivo)
        await db.commit()
        raise BaseAPIException(
            message=f"Aluno inelegível: {motivo}",
            code="INELEGIVEL",
            details=eleg,
            status_code=400,
        )

    # ═══════════════════════════════════════════════════════════════════
    # R3a — Verificar se aluno já está matriculado nesta disciplina no período (§7.3)
    # ═══════════════════════════════════════════════════════════════════
    matriculas_existentes = (await db.execute(
        select(Matricula)
        .join(Turma, Matricula.turma_id == Turma.id)
        .where(
            Matricula.aluno_id == aluno_id,
            Matricula.periodo_letivo_id == turma.periodo_letivo_id,
            Matricula.status == StatusMatricula.ATIVA,
        )
    )).scalars().all()

    # Buscar turmas para verificar disciplinas e horários
    turmas_alocadas_ids = [m.turma_id for m in matriculas_existentes]
    turmas_alocadas = []
    if turmas_alocadas_ids:
        turmas_alocadas = (await db.execute(
            select(Turma).options(selectinload(Turma.disciplina)).where(Turma.id.in_(turmas_alocadas_ids))
        )).scalars().all()

    # Verificar disciplina duplicada
    for ta in turmas_alocadas:
        if ta.disciplina_id == disciplina.id:
            msg = f"Aluno já matriculado na disciplina '{disciplina.nome}' neste período."
            _registrar_auditoria_sync(db, aluno_id, turma_id, fase, "R3_DISCIPLINA_DUPLICADA", "REJEITADO", msg)
            await db.commit()
            raise BaseAPIException(message=msg, code="DISCIPLINA_DUPLICADA", status_code=400)

    # ═══════════════════════════════════════════════════════════════════
    # R3b — Limite de créditos (§7.3)
    # ═══════════════════════════════════════════════════════════════════
    creditos_atuais = sum(ta.disciplina.creditos for ta in turmas_alocadas if ta.disciplina)
    creditos_futuros = creditos_atuais + disciplina.creditos
    if creditos_futuros > aluno.limite_creditos_periodo:
        msg = f"Limite de créditos excedido ({creditos_futuros}/{aluno.limite_creditos_periodo})."
        _registrar_auditoria_sync(db, aluno_id, turma_id, fase, "R3_LIMITE_CREDITOS", "REJEITADO", msg)
        await db.commit()
        raise BaseAPIException(message=msg, code="LIMITE_CREDITOS", status_code=400)

    # ═══════════════════════════════════════════════════════════════════
    # R3c — Conflito de horário (§7.3)
    # ═══════════════════════════════════════════════════════════════════
    from .processamento import _verificar_conflito_horario
    horarios_ocupados = [ta.horario_serializado for ta in turmas_alocadas]
    if _verificar_conflito_horario(turma.horario_serializado, horarios_ocupados):
        msg = f"Conflito de horário com turma já alocada (horário: {turma.horario_serializado})."
        _registrar_auditoria_sync(db, aluno_id, turma_id, fase, "R3_CONFLITO_HORARIO", "REJEITADO", msg)
        await db.commit()
        raise BaseAPIException(message=msg, code="CONFLITO_HORARIO", status_code=400)

    # ═══════════════════════════════════════════════════════════════════
    # R4 — Disponibilidade de vagas (§7.4)
    # ═══════════════════════════════════════════════════════════════════
    if turma.vagas_ocupadas >= turma.vagas_totais:
        msg = f"Turma lotada ({turma.vagas_ocupadas}/{turma.vagas_totais})."
        _registrar_auditoria_sync(db, aluno_id, turma_id, fase, "R4_SEM_VAGAS", "REJEITADO", msg)
        await db.commit()
        raise BaseAPIException(message=msg, code="SEM_VAGAS", status_code=400)

    # ═══════════════════════════════════════════════════════════════════
    # APROVAÇÃO — Efetivar matrícula extraordinária
    # ═══════════════════════════════════════════════════════════════════
    # Criar solicitação registrada como APROVADA diretamente
    solicitacao = SolicitacaoMatricula(
        aluno_id=aluno_id,
        turma_id=turma_id,
        prioridade=0,
        fase=fase,
        status=StatusSolicitacao.APROVADA,
        timestamp_solicitacao=datetime.now(timezone.utc),
    )
    db.add(solicitacao)

    # Incrementar vagas ocupadas
    turma.vagas_ocupadas += 1

    # Criar matrícula efetivada
    matricula = Matricula(
        aluno_id=aluno_id,
        turma_id=turma_id,
        periodo_letivo_id=turma.periodo_letivo_id,
        status=StatusMatricula.ATIVA,
        origem=fase,
        data_efetivacao=datetime.now(timezone.utc),
    )
    db.add(matricula)

    # Registrar auditoria de aprovação
    _registrar_auditoria_sync(
        db, aluno_id, turma_id, fase, "APROVACAO_EXTRAORDINARIA", "APROVADO",
        f"Matrícula extraordinária efetivada em '{disciplina.nome}' (turma {turma.codigo_turma})."
    )

    await db.commit()
    await db.refresh(matricula)

    return {
        "message": "Matrícula extraordinária efetivada com sucesso.",
        "matricula_id": matricula.id,
        "aluno_id": aluno_id,
        "turma_id": turma_id,
        "disciplina": disciplina.nome,
        "origem": fase,
    }


def _registrar_auditoria_sync(
    db: AsyncSession, aluno_id: int, turma_id: int,
    fase: str, regra: str, decisao: str, mensagem: str
) -> None:
    """Versão síncrona (add sem await) para registrar auditoria antes do commit."""
    registro = AuditoriaProcessamento(
        aluno_id=aluno_id,
        turma_id=turma_id,
        fase=fase,
        regra_aplicada=regra,
        decisao=decisao,
        mensagem=mensagem,
        timestamp_evento=datetime.now(timezone.utc),
    )
    db.add(registro)
