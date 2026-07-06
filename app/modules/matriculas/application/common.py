"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Utilidades compartilhadas do processamento de matrículas — modelo SIGAA.

Concentra os códigos de status (SIGAA_MATRICULA_STATUS), o registro da trilha de
auditoria (SIGAA_MATRICULA_HISTORICO) e funções de apoio usadas tanto pelo
processamento batch quanto pela matrícula extraordinária.
"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.disciplinas.infrastructure.orm_models import Disciplina
from app.modules.turmas.infrastructure.orm_models import Turma, TurmaHorarioAula
from ..infrastructure.orm_models import Matricula, MatriculaHistorico

# Códigos de status (carregados via DML do professor em SIGAA_MATRICULA_STATUS)
STATUS_PEDIDO = "PND"          # Pedido
STATUS_MATRICULADO = "MAT"     # Matriculado
STATUS_NAO_ELEGIVEL = "NEL"    # Não elegível
STATUS_CREDITOS = "CEX"        # Créditos excedidos
STATUS_JA_MATRICULADO = "JMD"  # Já matriculado na disciplina
STATUS_CONFLITO = "CON"        # Conflito de horário
STATUS_SEM_VAGA = "FUL"        # Vagas excedidas


def carga_horaria(disc: Disciplina) -> int:
    """Carga horária total de uma disciplina (teórica + prática)."""
    teorica = int(disc.carga_horaria_teorica) if disc.carga_horaria_teorica is not None else 0
    pratica = int(disc.carga_horaria_pratica) if disc.carga_horaria_pratica is not None else 0
    return teorica + pratica


async def vagas_ocupadas(db: AsyncSession, turma_id: int) -> int:
    """Quantidade de matrículas efetivadas (status 'MAT') numa turma."""
    return (
        await db.execute(
            select(func.count())
            .select_from(Matricula)
            .where(Matricula.turma == turma_id, Matricula.status == STATUS_MATRICULADO)
        )
    ).scalar_one()


async def horarios_da_turma(db: AsyncSession, turma_id: int) -> set[str]:
    """Conjunto de códigos de horário de aula alocados a uma turma (SIGAA_RL_TURMA_HORARIOAULA)."""
    result = await db.execute(
        select(TurmaHorarioAula.horarioaula).where(TurmaHorarioAula.turma == turma_id)
    )
    return {row[0] for row in result.all()}


def ha_conflito(slots_a: set[str], slots_b: set[str]) -> bool:
    """Há conflito se os dois conjuntos de slots de horário compartilham algum código."""
    return bool(slots_a & slots_b)


async def get_turma(db: AsyncSession, turma_id: int) -> Turma | None:
    """Busca uma turma pelo ID (helper compartilhado)."""
    return (await db.execute(select(Turma).where(Turma.id == turma_id))).scalar_one_or_none()


async def registrar_historico(
    db: AsyncSession, aluno_curso: int, status: str, turma: int, prioridade: int | None
) -> None:
    """Registra uma transição de estado na trilha de auditoria (SIGAA_MATRICULA_HISTORICO)."""
    db.add(
        MatriculaHistorico(
            aluno_curso=aluno_curso,
            status=status,
            turma=turma,
            prioridade=prioridade,
            data_hora=datetime.now(timezone.utc),
        )
    )
