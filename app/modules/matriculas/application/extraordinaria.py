"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Matrícula Extraordinária (Application Layer) — modelo SIGAA.

Fluxo imediato (§7.5), sem concorrência por prioridade. Resolve o vínculo
aluno-curso a partir da matrícula, aplica R1 (elegibilidade), R3 (duplicidade,
carga horária, conflito) e R4 (vagas), e efetiva a matrícula (status 'MAT') criando
uma nova linha em SIGAA_MATRICULA e a trilha em SIGAA_MATRICULA_HISTORICO.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BaseAPIException
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
    STATUS_SEM_VAGA,
    carga_horaria,
    get_turma,
    ha_conflito,
    horarios_da_turma,
    registrar_historico,
    vagas_ocupadas,
)
from .elegibilidade import verificar_elegibilidade

FASE = "EXTRAORDINARIA"


async def processar_extraordinaria(db: AsyncSession, aluno: str, turma_id: int) -> dict:
    """Processa uma matrícula extraordinária imediata (§7.5)."""
    vinculo = (
        await db.execute(
            select(AlunoCurso)
            .where(AlunoCurso.aluno == aluno)
            .order_by(AlunoCurso.periodo_letivo_registro.desc())
        )
    ).scalars().first()
    if not vinculo:
        raise BaseAPIException(message="Aluno ou vínculo não encontrado.", code="ALUNO_NOT_FOUND", status_code=404)

    turma = await get_turma(db, turma_id)
    if not turma:
        raise BaseAPIException(message="Turma não encontrada.", code="TURMA_NOT_FOUND", status_code=404)

    disciplina = (await db.execute(select(Disciplina).where(Disciplina.id == turma.disciplina))).scalar_one_or_none()
    if not disciplina:
        raise BaseAPIException(message="Disciplina da turma não encontrada.", code="DISCIPLINA_NOT_FOUND", status_code=404)

    async def rejeitar(status_code: str, codigo: str, msg: str):
        await registrar_historico(db, vinculo.id, status_code, turma_id, None)
        await db.commit()
        raise BaseAPIException(message=msg, code=codigo, status_code=400)

    # R1 — elegibilidade
    eleg = await verificar_elegibilidade(db, aluno, turma.disciplina)
    if not eleg["elegivel"]:
        await rejeitar(STATUS_NAO_ELEGIVEL, "INELEGIVEL", f"Aluno inelegível: {'; '.join(eleg['motivos'])}")

    # Matrículas já efetivadas do aluno no mesmo período (mesmo vínculo)
    efetivadas = (
        await db.execute(
            select(Matricula, Turma)
            .join(Turma, Turma.id == Matricula.turma)
            .where(
                Matricula.aluno_curso == vinculo.id,
                Matricula.status == STATUS_MATRICULADO,
                Turma.periodo_letivo == turma.periodo_letivo,
            )
        )
    ).all()

    # R3a — disciplina duplicada
    if any(t.disciplina == turma.disciplina for _m, t in efetivadas):
        await rejeitar(STATUS_JA_MATRICULADO, "DISCIPLINA_DUPLICADA",
                       f"Aluno já matriculado na disciplina '{turma.disciplina}' neste período.")

    # R3b — carga horária máxima do período
    disc_ids = {t.disciplina for _m, t in efetivadas}
    disc_map = {
        d.id: d for d in (await db.execute(select(Disciplina).where(Disciplina.id.in_(disc_ids or {""})))).scalars().all()
    }
    carga_atual = sum(carga_horaria(disc_map[cid]) for cid in disc_ids if cid in disc_map)
    curr = (await db.execute(select(Curriculo).where(Curriculo.id == vinculo.curriculo))).scalar_one_or_none()
    limite = int(curr.carga_horaria_max_periodo) if curr and curr.carga_horaria_max_periodo is not None else 0
    if limite and carga_atual + carga_horaria(disciplina) > limite:
        await rejeitar(STATUS_CREDITOS, "LIMITE_CREDITOS",
                       f"Carga horária máxima do período excedida ({carga_atual + carga_horaria(disciplina)}/{limite}).")

    # R3c — conflito de horário
    slots_novo = await horarios_da_turma(db, turma_id)
    slots_ocupados: set[str] = set()
    for _m, t in efetivadas:
        slots_ocupados |= await horarios_da_turma(db, t.id)
    if ha_conflito(slots_novo, slots_ocupados):
        await rejeitar(STATUS_CONFLITO, "CONFLITO_HORARIO", "Conflito de horário com turma já matriculada.")

    # R4 — vagas
    vagas_totais = int(turma.vagas) if turma.vagas is not None else 0
    if await vagas_ocupadas(db, turma_id) >= vagas_totais:
        await rejeitar(STATUS_SEM_VAGA, "SEM_VAGAS", "Turma lotada.")

    # Aprovação — cria a matrícula efetivada
    matricula = Matricula(aluno_curso=vinculo.id, turma=turma_id, status=STATUS_MATRICULADO, prioridade=None)
    db.add(matricula)
    await registrar_historico(db, vinculo.id, STATUS_MATRICULADO, turma_id, None)
    await db.commit()
    await db.refresh(matricula)

    return {
        "message": "Matrícula extraordinária efetivada com sucesso.",
        "matricula_id": matricula.id,
        "aluno": aluno,
        "turma": turma_id,
        "disciplina": turma.disciplina,
        "origem": FASE,
    }
