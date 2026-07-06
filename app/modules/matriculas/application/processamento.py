"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Processamento Batch de Matrículas (Application Layer) — modelo SIGAA.

Motor das Fases 3 e 5 (§7.2–§7.4). Avalia todos os pedidos (SIGAA_MATRICULA com
status 'PND') de um período letivo e aplica as 4 regras:

  R1 — Elegibilidade (§7.1)
  R2 — Ordenação por turma: IRA desc → data_registro asc → desempate aleatório (§7.2)
  R3 — Validação por aluno: carga horária máx. do período, disciplina duplicada,
       conflito de horário (§7.3)
  R4 — Rejeição por falta de vagas (§7.4)

O limite de "créditos" do enunciado é representado, no SIGAA, pela carga horária
máxima por período do currículo do aluno (SIGAA_CURRICULO.CARGA_HORARIA_MAX_PERIODO).
Cada decisão altera o status da matrícula e registra a trilha em SIGAA_MATRICULA_HISTORICO.
"""
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alunos.infrastructure.orm_models import AlunoCurso
from app.modules.curriculos.infrastructure.orm_models import Curriculo
from app.modules.disciplinas.infrastructure.orm_models import Disciplina
from app.modules.turmas.infrastructure.orm_models import Turma
from ..infrastructure.orm_models import Matricula
from .common import (
    STATUS_CONFLITO,
    STATUS_CREDITOS,
    STATUS_JA_MATRICULADO,
    STATUS_MATRICULADO,
    STATUS_NAO_ELEGIVEL,
    STATUS_PEDIDO,
    STATUS_SEM_VAGA,
    carga_horaria,
    ha_conflito,
    horarios_da_turma,
    registrar_historico,
    vagas_ocupadas,
)
from .elegibilidade import verificar_elegibilidade


async def processar_fase(db: AsyncSession, periodo_letivo: str, fase: str = "FASE_3") -> dict:
    """Executa o processamento batch de um período letivo (§7.2–§7.4)."""
    resumo = {"fase": fase, "periodo_letivo": periodo_letivo, "total_pedidos": 0, "aprovadas": 0, "rejeitadas": 0}

    # PASSO 1 — pedidos (status 'PND') das turmas do período
    result = await db.execute(
        select(Matricula, Turma, AlunoCurso)
        .join(Turma, Turma.id == Matricula.turma)
        .join(AlunoCurso, AlunoCurso.id == Matricula.aluno_curso)
        .where(Matricula.status == STATUS_PEDIDO, Turma.periodo_letivo == periodo_letivo)
    )
    pedidos = result.all()
    resumo["total_pedidos"] = len(pedidos)
    if not pedidos:
        return resumo

    # Caches: disciplinas (por código) e capacidade máxima de carga horária por currículo
    disc_codes = {t.disciplina for _, t, _ in pedidos}
    disc_map = {
        d.id: d
        for d in (await db.execute(select(Disciplina).where(Disciplina.id.in_(disc_codes)))).scalars().all()
    }
    curr_codes = {ac.curriculo for _, _, ac in pedidos}
    curr_map = {
        c.id: c
        for c in (await db.execute(select(Curriculo).where(Curriculo.id.in_(curr_codes)))).scalars().all()
    }
    horarios_turma = {t.id: await horarios_da_turma(db, t.id) for _, t, _ in pedidos}

    # Agrupar por turma
    por_turma: dict[int, list] = {}
    for mat, turma, vinc in pedidos:
        por_turma.setdefault(turma.id, []).append((mat, turma, vinc))

    # Rastreadores por vínculo aluno-curso, durante o batch
    carga_acumulada: dict[int, int] = {}
    horarios_acumulados: dict[int, set[str]] = {}
    disciplinas_alocadas: dict[int, set[str]] = {}
    vagas_cache: dict[int, int] = {}

    for turma_id, grupo in por_turma.items():
        turma = grupo[0][1]
        disciplina = disc_map.get(turma.disciplina)
        if disciplina is None:
            continue

        # R1 — elegibilidade
        elegiveis = []
        for mat, _t, vinc in grupo:
            eleg = await verificar_elegibilidade(db, vinc.aluno, turma.disciplina)
            if eleg["elegivel"]:
                elegiveis.append((mat, vinc))
            else:
                mat.status = STATUS_NAO_ELEGIVEL
                await registrar_historico(db, vinc.id, STATUS_NAO_ELEGIVEL, turma_id, mat.prioridade)
                resumo["rejeitadas"] += 1
        if not elegiveis:
            continue

        # R2 — ordenação: IRA desc, data_registro asc, desempate aleatório
        random.shuffle(elegiveis)
        elegiveis.sort(key=lambda item: (-(item[1].ira or 0.0), item[1].data_registro))

        # R3 + R4
        vagas_cache.setdefault(turma_id, await vagas_ocupadas(db, turma_id))
        vagas_totais = int(turma.vagas) if turma.vagas is not None else 0

        for mat, vinc in elegiveis:
            carga_acumulada.setdefault(vinc.id, 0)
            horarios_acumulados.setdefault(vinc.id, set())
            disciplinas_alocadas.setdefault(vinc.id, set())

            # R3a — disciplina duplicada no período
            if turma.disciplina in disciplinas_alocadas[vinc.id]:
                mat.status = STATUS_JA_MATRICULADO
                await registrar_historico(db, vinc.id, STATUS_JA_MATRICULADO, turma_id, mat.prioridade)
                resumo["rejeitadas"] += 1
                continue

            # R3b — carga horária máxima do período (limite de créditos)
            ch = carga_horaria(disciplina)
            limite = 0
            curr = curr_map.get(vinc.curriculo)
            if curr is not None and curr.carga_horaria_max_periodo is not None:
                limite = int(curr.carga_horaria_max_periodo)
            if limite and carga_acumulada[vinc.id] + ch > limite:
                mat.status = STATUS_CREDITOS
                await registrar_historico(db, vinc.id, STATUS_CREDITOS, turma_id, mat.prioridade)
                resumo["rejeitadas"] += 1
                continue

            # R3c — conflito de horário
            if ha_conflito(horarios_turma.get(turma_id, set()), horarios_acumulados[vinc.id]):
                mat.status = STATUS_CONFLITO
                await registrar_historico(db, vinc.id, STATUS_CONFLITO, turma_id, mat.prioridade)
                resumo["rejeitadas"] += 1
                continue

            # R4 — vagas
            if vagas_cache[turma_id] >= vagas_totais:
                mat.status = STATUS_SEM_VAGA
                await registrar_historico(db, vinc.id, STATUS_SEM_VAGA, turma_id, mat.prioridade)
                resumo["rejeitadas"] += 1
                continue

            # Aprovação
            mat.status = STATUS_MATRICULADO
            vagas_cache[turma_id] += 1
            carga_acumulada[vinc.id] += ch
            horarios_acumulados[vinc.id] |= horarios_turma.get(turma_id, set())
            disciplinas_alocadas[vinc.id].add(turma.disciplina)
            await registrar_historico(db, vinc.id, STATUS_MATRICULADO, turma_id, mat.prioridade)
            resumo["aprovadas"] += 1

    await db.commit()
    return resumo
