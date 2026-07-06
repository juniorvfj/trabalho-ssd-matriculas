"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviço de Tarefa — verificarElegibilidade (Application Layer) — modelo SIGAA.

Serviço de tarefa obrigatório (§5.2). Avalia o par (aluno, disciplina) segundo as
três regras do enunciado (§7.1), agora sobre o modelo de dados do professor:

  1. A disciplina pertence ao currículo do vínculo do aluno
     (SIGAA_RL_CURRICULO_DISCIPLINA para o currículo em SIGAA_RL_ALUNO_CURSO).
  2. O aluno ainda não foi aprovado nessa disciplina
     (menção de aprovação em SIGAA_RL_ALUNO_CURSO_DISCIPLINA).
  3. O aluno possui todos os pré-requisitos cumpridos (SIGAA_PREREQ).
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alunos.infrastructure.orm_models import AlunoCurso
from app.modules.curriculos.infrastructure.orm_models import CurriculoDisciplina
from app.modules.disciplinas.infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from app.modules.historicos.application.services import disciplinas_aprovadas


async def verificar_elegibilidade(db: AsyncSession, aluno: str, disciplina: str) -> dict:
    """
    Verifica a elegibilidade de um aluno (matrícula) para uma disciplina (código).

    Retorna {'elegivel': bool, 'motivos': [...], 'detalhes': {...}}.
    """
    motivos: list[str] = []
    detalhes: dict[str, Any] = {"aluno": aluno, "disciplina": disciplina}

    # Aluno e seu vínculo de curso/currículo (pega o mais recente)
    vinculo = (
        await db.execute(
            select(AlunoCurso)
            .where(AlunoCurso.aluno == aluno)
            .order_by(AlunoCurso.periodo_letivo_registro.desc())
        )
    ).scalars().first()
    if not vinculo:
        return {"elegivel": False, "motivos": ["Aluno ou vínculo de curso não encontrado."], "detalhes": detalhes}
    detalhes["curriculo"] = vinculo.curriculo

    disc = (await db.execute(select(Disciplina).where(Disciplina.id == disciplina))).scalar_one_or_none()
    if not disc:
        return {"elegivel": False, "motivos": ["Disciplina não encontrada."], "detalhes": detalhes}
    detalhes["disciplina_nome"] = disc.nome

    # REGRA 1 — disciplina pertence ao currículo do aluno? (§7.1)
    no_curriculo = (
        await db.execute(
            select(CurriculoDisciplina).where(
                CurriculoDisciplina.curriculo == vinculo.curriculo,
                CurriculoDisciplina.disciplina == disciplina,
            )
        )
    ).scalar_one_or_none()
    if not no_curriculo:
        motivos.append(f"A disciplina '{disciplina}' não pertence ao currículo {vinculo.curriculo} do aluno.")

    # REGRA 2 — aluno já aprovado na disciplina? (§7.1)
    aprovadas = await disciplinas_aprovadas(db, aluno)
    detalhes["disciplinas_aprovadas"] = sorted(aprovadas)
    if disciplina in aprovadas:
        motivos.append(f"O aluno já foi aprovado na disciplina '{disciplina}'.")

    # REGRA 3 — pré-requisitos cumpridos? (§7.1)
    prereqs = (
        await db.execute(
            select(DisciplinaPrerequisito.disciplina_requerido).where(
                DisciplinaPrerequisito.disciplina_requer == disciplina
            )
        )
    ).scalars().all()
    faltantes = [p for p in prereqs if p not in aprovadas]
    if faltantes:
        motivos.append(f"Pré-requisitos não cumpridos: {', '.join(faltantes)}.")
        detalhes["prerequisitos_faltantes"] = faltantes
    detalhes["total_prerequisitos"] = len(prereqs)

    elegivel = len(motivos) == 0
    detalhes["elegivel"] = elegivel
    return {"elegivel": elegivel, "motivos": motivos, "detalhes": detalhes}
