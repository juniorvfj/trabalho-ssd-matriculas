"""
Módulo de Processamento Batch de Matrículas (Application Layer)

Implementa o motor de processamento das Fases 3 e 5 do fluxo de matrícula (§7.2–§7.4).
O processamento é executado em lote (batch), avaliando todas as solicitações pendentes
de um período letivo e aplicando as 4 regras de negócio na seguinte ordem:

  R1 — Elegibilidade: o aluno é elegível para cursar a disciplina? (§7.1)
  R2 — Ordenação por turma: IRA desc → data_admissao asc → random tiebreak (§7.2)
  R3 — Validação por aluno: limite de créditos, disciplina duplicada, conflito de horário (§7.3)
  R4 — Rejeição por falta de vagas: turma com vagas_ocupadas >= vagas_totais (§7.4)

Cada decisão é registrada na tabela de auditoria para rastreabilidade completa.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict
from datetime import datetime, timezone
import random

from ..infrastructure.orm_models import (
    SolicitacaoMatricula, Matricula, AuditoriaProcessamento,
    StatusSolicitacao, StatusMatricula,
)
from .elegibilidade import verificar_elegibilidade

from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.turmas.infrastructure.orm_models import Turma
from app.modules.disciplinas.infrastructure.orm_models import Disciplina


async def _registrar_auditoria(
    db: AsyncSession, aluno_id: int, turma_id: int,
    fase: str, regra: str, decisao: str, mensagem: str
) -> None:
    """
    Registra um evento de auditoria na tabela auditoria_processamento (§6.12).

    Cada chamada cria um registro imutável que documenta qual regra foi aplicada,
    para qual par (aluno, turma), e qual foi a decisão tomada.
    """
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


async def _efetivar_matricula(
    db: AsyncSession, solicitacao: SolicitacaoMatricula,
    turma: Turma, fase: str
) -> Matricula:
    """
    Cria o registro de Matrícula efetivada e incrementa as vagas ocupadas da turma.

    É chamada apenas quando todas as regras (R1–R4) foram aprovadas para a solicitação.
    """
    # Atualizar status da solicitação para APROVADA
    solicitacao.status = StatusSolicitacao.APROVADA

    # Incrementar vagas ocupadas na turma
    turma.vagas_ocupadas += 1

    # Criar matrícula efetivada
    matricula = Matricula(
        aluno_id=solicitacao.aluno_id,
        turma_id=solicitacao.turma_id,
        periodo_letivo_id=turma.periodo_letivo_id,
        status=StatusMatricula.ATIVA,
        origem=fase,
        data_efetivacao=datetime.now(timezone.utc),
    )
    db.add(matricula)
    return matricula


async def _rejeitar_solicitacao(
    db: AsyncSession, solicitacao: SolicitacaoMatricula,
    turma_id: int, fase: str, regra: str, motivo: str
) -> None:
    """
    Marca uma solicitação como REJEITADA e registra a auditoria correspondente.
    """
    solicitacao.status = StatusSolicitacao.REJEITADA
    solicitacao.resultado = motivo

    await _registrar_auditoria(
        db, solicitacao.aluno_id, turma_id, fase, regra, "REJEITADO", motivo
    )


def _verificar_conflito_horario(horario_novo: str, horarios_ocupados: List[str]) -> bool:
    """
    Verifica se há conflito de horário entre a turma candidata e as turmas
    já alocadas ao aluno neste período.

    Utiliza o formato serializado de horário acadêmico (ex: '24T34' = terça e quarta,
    horários 3 e 4 do turno Tarde). Dois horários conflitam se compartilham
    pelo menos uma combinação dia+turno+slot.

    :param horario_novo: Horário da turma candidata
    :param horarios_ocupados: Lista de horários das turmas já alocadas
    :return: True se houver conflito, False se estiver livre
    """
    def parse_horario(h: str) -> set:
        """Decompõe '24T34' em slots individuais como {('2','T','3'), ('2','T','4'), ...}"""
        slots = set()
        dias = []
        turno = None
        horas = []

        for char in h:
            if char.isdigit() and turno is None:
                dias.append(char)
            elif char.isalpha():
                turno = char
            elif char.isdigit() and turno is not None:
                horas.append(char)

        for dia in dias:
            for hora in horas:
                slots.add((dia, turno, hora))
        return slots

    slots_novo = parse_horario(horario_novo)
    for horario in horarios_ocupados:
        slots_existente = parse_horario(horario)
        if slots_novo & slots_existente:
            return True
    return False


async def processar_fase(db: AsyncSession, periodo_letivo_id: int, fase: str = "FASE_3") -> dict:
    """
    Motor de Processamento Batch — Fases 3 e 5 (§7.2, §7.3, §7.4)

    Executa o processamento completo de matrículas para um período letivo,
    aplicando as 4 regras de negócio em ordem:

      1. Buscar todas as solicitações PENDENTES do período
      2. Agrupar solicitações por turma
      3. Para cada turma:
         R1 — Verificar elegibilidade de cada aluno
         R2 — Ordenar por IRA desc, data_admissao asc, random tiebreak
         R3 — Validar por aluno (créditos, duplicata, horário)
         R4 — Verificar disponibilidade de vagas
      4. Efetivar matrículas aprovadas e registrar auditoria

    :param periodo_letivo_id: ID do período letivo a processar
    :param fase: Identificador da fase ("FASE_3" ou "FASE_5")
    :return: Resumo com contadores de aprovações, rejeições e erros
    """
    resumo = {"fase": fase, "periodo_letivo_id": periodo_letivo_id,
              "aprovadas": 0, "rejeitadas": 0, "total_solicitacoes": 0}

    # ═════════════════════════════════════════════════════════════════════
    # PASSO 1 — Buscar todas as solicitações PENDENTES do período (§7.2)
    # ═════════════════════════════════════════════════════════════════════
    stmt = (
        select(SolicitacaoMatricula)
        .join(Turma, SolicitacaoMatricula.turma_id == Turma.id)
        .where(
            Turma.periodo_letivo_id == periodo_letivo_id,
            SolicitacaoMatricula.status == StatusSolicitacao.PENDENTE,
            SolicitacaoMatricula.fase == fase,
        )
    )
    result = await db.execute(stmt)
    solicitacoes = result.scalars().all()
    resumo["total_solicitacoes"] = len(solicitacoes)

    if not solicitacoes:
        return resumo

    # ═════════════════════════════════════════════════════════════════════
    # PASSO 2 — Agrupar solicitações por turma
    # ═════════════════════════════════════════════════════════════════════
    por_turma: Dict[int, List[SolicitacaoMatricula]] = {}
    for sol in solicitacoes:
        por_turma.setdefault(sol.turma_id, []).append(sol)

    # Cache de alunos e turmas para evitar N+1 queries
    aluno_ids = {sol.aluno_id for sol in solicitacoes}
    turma_ids = set(por_turma.keys())

    alunos_result = await db.execute(select(Aluno).where(Aluno.id.in_(aluno_ids)))
    alunos_map = {a.id: a for a in alunos_result.scalars().all()}

    turmas_result = await db.execute(
        select(Turma).options(selectinload(Turma.disciplina)).where(Turma.id.in_(turma_ids))
    )
    turmas_map = {t.id: t for t in turmas_result.scalars().all()}

    # Rastreia créditos e horários acumulados por aluno durante o processamento
    creditos_acumulados: Dict[int, int] = {}
    horarios_acumulados: Dict[int, List[str]] = {}
    disciplinas_alocadas: Dict[int, set] = {}

    # ═════════════════════════════════════════════════════════════════════
    # PASSO 3 — Processar cada turma
    # ═════════════════════════════════════════════════════════════════════
    for turma_id, sols in por_turma.items():
        turma = turmas_map.get(turma_id)
        if not turma:
            continue

        disciplina = turma.disciplina

        # ─────────────────────────────────────────────────────────────────
        # R1 — Elegibilidade (§7.1): filtrar alunos inelegíveis
        # ─────────────────────────────────────────────────────────────────
        sols_elegiveis = []
        for sol in sols:
            eleg = await verificar_elegibilidade(db, sol.aluno_id, disciplina.id)
            if eleg["elegivel"]:
                sols_elegiveis.append(sol)
                await _registrar_auditoria(
                    db, sol.aluno_id, turma_id, fase,
                    "R1_ELEGIBILIDADE", "APROVADO",
                    f"Aluno elegível para '{disciplina.nome}'."
                )
            else:
                motivo = "; ".join(eleg["motivos"])
                await _rejeitar_solicitacao(
                    db, sol, turma_id, fase, "R1_ELEGIBILIDADE", motivo
                )
                resumo["rejeitadas"] += 1

        if not sols_elegiveis:
            continue

        # ─────────────────────────────────────────────────────────────────
        # R2 — Ordenação por turma (§7.2): IRA desc → data_admissao asc
        # ─────────────────────────────────────────────────────────────────
        random.shuffle(sols_elegiveis)  # Tiebreak aleatório antes da ordenação estável
        sols_elegiveis.sort(
            key=lambda s: (
                -(alunos_map.get(s.aluno_id, Aluno()).ira or 0),
                alunos_map.get(s.aluno_id, Aluno()).data_admissao or datetime.min.date(),
            )
        )

        # ─────────────────────────────────────────────────────────────────
        # R3 + R4 — Validação por aluno + Vagas (§7.3, §7.4)
        # ─────────────────────────────────────────────────────────────────
        for sol in sols_elegiveis:
            aluno = alunos_map.get(sol.aluno_id)
            if not aluno:
                continue

            # Inicializar rastreadores se primeiro processamento do aluno
            if aluno.id not in creditos_acumulados:
                creditos_acumulados[aluno.id] = 0
                horarios_acumulados[aluno.id] = []
                disciplinas_alocadas[aluno.id] = set()

            # R3a — Disciplina duplicada no período (§7.3)
            if disciplina.id in disciplinas_alocadas[aluno.id]:
                await _rejeitar_solicitacao(
                    db, sol, turma_id, fase, "R3_DISCIPLINA_DUPLICADA",
                    f"Aluno já alocado na disciplina '{disciplina.nome}' neste período."
                )
                resumo["rejeitadas"] += 1
                continue

            # R3b — Limite de créditos no período (§7.3)
            creditos_futuros = creditos_acumulados[aluno.id] + disciplina.creditos
            if creditos_futuros > aluno.limite_creditos_periodo:
                await _rejeitar_solicitacao(
                    db, sol, turma_id, fase, "R3_LIMITE_CREDITOS",
                    f"Limite de créditos excedido ({creditos_futuros}/{aluno.limite_creditos_periodo})."
                )
                resumo["rejeitadas"] += 1
                continue

            # R3c — Conflito de horário (§7.3)
            if _verificar_conflito_horario(turma.horario_serializado, horarios_acumulados[aluno.id]):
                await _rejeitar_solicitacao(
                    db, sol, turma_id, fase, "R3_CONFLITO_HORARIO",
                    f"Conflito de horário com turma já alocada (horário: {turma.horario_serializado})."
                )
                resumo["rejeitadas"] += 1
                continue

            # R4 — Disponibilidade de vagas (§7.4)
            if turma.vagas_ocupadas >= turma.vagas_totais:
                await _rejeitar_solicitacao(
                    db, sol, turma_id, fase, "R4_SEM_VAGAS",
                    f"Turma lotada ({turma.vagas_ocupadas}/{turma.vagas_totais})."
                )
                resumo["rejeitadas"] += 1
                continue

            # ═══════════════════════════════════════════════════════════════
            # APROVAÇÃO — todas as regras passaram
            # ═══════════════════════════════════════════════════════════════
            await _efetivar_matricula(db, sol, turma, fase)

            # Atualizar rastreadores do aluno
            creditos_acumulados[aluno.id] += disciplina.creditos
            horarios_acumulados[aluno.id].append(turma.horario_serializado)
            disciplinas_alocadas[aluno.id].add(disciplina.id)

            await _registrar_auditoria(
                db, aluno.id, turma_id, fase,
                "APROVACAO_FINAL", "APROVADO",
                f"Matrícula efetivada em '{disciplina.nome}' (turma {turma.codigo_turma})."
            )
            resumo["aprovadas"] += 1

    # Persistir todas as alterações em uma única transação
    await db.commit()
    return resumo
