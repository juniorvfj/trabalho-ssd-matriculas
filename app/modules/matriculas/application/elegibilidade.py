"""
Módulo do Serviço de Tarefa — verificarElegibilidade (Application Layer)

Este é o serviço de tarefa obrigatório do trabalho (§5.2). Diferentemente dos
serviços de entidade (CRUD), o serviço de tarefa implementa lógica de negócio
complexa que cruza dados de múltiplas entidades para tomar uma decisão.

A elegibilidade é verificada segundo três regras definidas no enunciado (§7.1):
  1. A disciplina pertence ao currículo do curso do aluno
  2. O aluno ainda não foi aprovado nessa disciplina
  3. O aluno possui todos os pré-requisitos cumpridos

Cada regra é avaliada independentemente e os motivos de impedimento são
acumulados, permitindo ao aluno saber todos os problemas de uma vez.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.disciplinas.infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from app.modules.historicos.infrastructure.orm_models import HistoricoAcademico, StatusHistorico


async def verificar_elegibilidade(
    db: AsyncSession, aluno_id: int, disciplina_id: int
) -> dict:
    """
    Serviço de Tarefa — verificarElegibilidade (§5.2, §7.1)

    Avalia se um aluno está apto a cursar uma determinada disciplina,
    verificando três regras obrigatórias do enunciado:
      1. A disciplina pertence ao currículo do curso do aluno
      2. O aluno ainda não foi aprovado nessa disciplina
      3. O aluno possui todos os pré-requisitos cumpridos

    :param db: Sessão assíncrona do banco de dados
    :param aluno_id: ID do aluno a ser verificado
    :param disciplina_id: ID da disciplina pretendida
    :return: Dicionário com 'elegivel' (bool), 'motivos' (lista) e 'detalhes' (dict)
    """
    motivos: List[str] = []
    detalhes: Dict[str, Any] = {"aluno_id": aluno_id, "disciplina_id": disciplina_id}

    # --- Buscar o aluno ---
    aluno = (await db.execute(select(Aluno).where(Aluno.id == aluno_id))).scalar_one_or_none()
    if not aluno:
        return {
            "elegivel": False,
            "motivos": ["Aluno não encontrado no sistema."],
            "detalhes": detalhes,
        }
    detalhes["aluno_nome"] = aluno.nome
    detalhes["aluno_curso_id"] = aluno.curso_id

    # --- Buscar a disciplina ---
    disciplina = (await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )).scalar_one_or_none()
    if not disciplina:
        return {
            "elegivel": False,
            "motivos": ["Disciplina não encontrada no sistema."],
            "detalhes": detalhes,
        }
    detalhes["disciplina_nome"] = disciplina.nome
    detalhes["disciplina_curso_id"] = disciplina.curso_id

    # ═══════════════════════════════════════════════════════════════════════
    # REGRA 1 — A disciplina pertence ao currículo do curso do aluno? (§7.1)
    # ═══════════════════════════════════════════════════════════════════════
    if disciplina.curso_id != aluno.curso_id:
        motivos.append(
            f"A disciplina '{disciplina.nome}' não pertence ao currículo "
            f"do curso do aluno (curso_id do aluno: {aluno.curso_id}, "
            f"curso_id da disciplina: {disciplina.curso_id})."
        )

    # ═══════════════════════════════════════════════════════════════════════
    # REGRA 2 — O aluno já foi aprovado nessa disciplina? (§7.1)
    # ═══════════════════════════════════════════════════════════════════════
    # Consultar o histórico acadêmico do aluno para esta disciplina
    historicos = (await db.execute(
        select(HistoricoAcademico).where(
            HistoricoAcademico.aluno_id == aluno_id,
            HistoricoAcademico.disciplina_id == disciplina_id,
        )
    )).scalars().all()

    # Verificar se há registro com status APROVADO
    ja_aprovado = any(h.status == StatusHistorico.APROVADO for h in historicos)
    if ja_aprovado:
        motivos.append(
            f"O aluno já foi aprovado na disciplina '{disciplina.nome}'."
        )
    detalhes["ja_aprovado"] = ja_aprovado

    # ═══════════════════════════════════════════════════════════════════════
    # REGRA 3 — O aluno possui todos os pré-requisitos? (§7.1)
    # ═══════════════════════════════════════════════════════════════════════
    # Buscar pré-requisitos da disciplina na tabela associativa
    prerequisitos_result = await db.execute(
        select(DisciplinaPrerequisito).where(
            DisciplinaPrerequisito.disciplina_id == disciplina_id
        )
    )
    prerequisitos = prerequisitos_result.scalars().all()

    if prerequisitos:
        # Buscar todas as disciplinas em que o aluno foi aprovado
        historico_completo = (await db.execute(
            select(HistoricoAcademico).where(
                HistoricoAcademico.aluno_id == aluno_id,
                HistoricoAcademico.status == StatusHistorico.APROVADO,
            )
        )).scalars().all()

        # IDs das disciplinas em que o aluno foi aprovado
        disciplinas_aprovadas = {h.disciplina_id for h in historico_completo}

        # Verificar cada pré-requisito individualmente
        prerequisitos_faltantes = []
        for prereq in prerequisitos:
            if prereq.prerequisito_id not in disciplinas_aprovadas:
                # Buscar nome do pré-requisito para mensagem descritiva
                disc_prereq = (await db.execute(
                    select(Disciplina).where(Disciplina.id == prereq.prerequisito_id)
                )).scalar_one_or_none()

                nome_prereq = disc_prereq.nome if disc_prereq else f"ID {prereq.prerequisito_id}"
                prerequisitos_faltantes.append(nome_prereq)

        if prerequisitos_faltantes:
            motivos.append(
                f"Pré-requisitos não cumpridos: {', '.join(prerequisitos_faltantes)}."
            )
            detalhes["prerequisitos_faltantes"] = prerequisitos_faltantes

    detalhes["total_prerequisitos"] = len(prerequisitos)

    # ═══════════════════════════════════════════════════════════════════════
    # Resultado final da elegibilidade
    # ═══════════════════════════════════════════════════════════════════════
    elegivel = len(motivos) == 0
    detalhes["elegivel"] = elegivel

    return {
        "elegivel": elegivel,
        "motivos": motivos,
        "detalhes": detalhes,
    }
