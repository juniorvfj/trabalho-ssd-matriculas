"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços de Matrícula (Application Layer) — modelo SIGAA.

CRUD e consultas sobre SIGAA_MATRICULA e a trilha SIGAA_MATRICULA_HISTORICO.
Um "pedido" é uma matrícula com status 'PND'; a alteração de status (ex.: retirada)
é feita via PATCH. A matrícula referencia o vínculo aluno-curso (SIGAA_RL_ALUNO_CURSO).
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BaseAPIException
from app.modules.alunos.infrastructure.orm_models import AlunoCurso
from app.modules.disciplinas.infrastructure.orm_models import Disciplina
from app.modules.turmas.infrastructure.orm_models import Turma
from ..api.schemas import MatriculaCreate
from ..infrastructure.orm_models import Matricula, MatriculaHistorico, MatriculaStatus
from .common import STATUS_PEDIDO, carga_horaria, registrar_historico


async def descricoes_status(db: AsyncSession) -> dict[str, str]:
    """
    Mapa código → descrição legível de SIGAA_MATRICULA_STATUS (ex.: 'NEL' → 'Não elegível').

    É a tabela de domínio do professor (14 linhas, carregada via DML). Usada para expor o
    motivo do indeferimento, que no modelo SIGAA não é uma coluna: é o próprio status.
    """
    result = await db.execute(select(MatriculaStatus.id, MatriculaStatus.status))
    return {codigo: descricao for codigo, descricao in result.all()}


async def _vinculo_do_aluno(db: AsyncSession, aluno: str) -> AlunoCurso:
    """Resolve o vínculo aluno-curso mais recente a partir da matrícula do aluno."""
    vinculo = (
        await db.execute(
            select(AlunoCurso)
            .where(AlunoCurso.aluno == aluno)
            .order_by(AlunoCurso.periodo_letivo_registro.desc())
        )
    ).scalars().first()
    if not vinculo:
        raise BaseAPIException(message=f"Vínculo do aluno '{aluno}' não encontrado.", code="ALUNO_NOT_FOUND", status_code=404)
    return vinculo


async def create_matriculas(db: AsyncSession, pedidos: list[MatriculaCreate]) -> list[Matricula]:
    """Cria um lote de pedidos de matrícula (status 'PND')."""
    criadas: list[Matricula] = []
    for item in pedidos:
        vinculo = await _vinculo_do_aluno(db, item.aluno)
        turma = (await db.execute(select(Turma).where(Turma.id == item.turma))).scalar_one_or_none()
        if not turma:
            raise BaseAPIException(message=f"Turma {item.turma} não encontrada.", code="TURMA_NOT_FOUND", status_code=404)
        matricula = Matricula(
            aluno_curso=vinculo.id, turma=item.turma, status=STATUS_PEDIDO, prioridade=item.prioridade
        )
        db.add(matricula)
        await registrar_historico(db, vinculo.id, STATUS_PEDIDO, item.turma, item.prioridade)
        criadas.append(matricula)
    await db.commit()
    for m in criadas:
        await db.refresh(m)
    return criadas


async def search_matriculas(
    db: AsyncSession,
    periodo_letivo: str,
    aluno: Optional[str],
    turma: Optional[int],
    status: Optional[str],
    offset: int,
    count: int,
) -> tuple[list[Matricula], int]:
    """Pesquisa matrículas de um período letivo (obrigatório) com filtros opcionais."""
    base = (
        select(Matricula)
        .join(Turma, Turma.id == Matricula.turma)
        .join(AlunoCurso, AlunoCurso.id == Matricula.aluno_curso)
    )
    filtros = [Turma.periodo_letivo == periodo_letivo]
    if aluno:
        filtros.append(AlunoCurso.aluno == aluno)
    if turma:
        filtros.append(Matricula.turma == turma)
    if status:
        filtros.append(Matricula.status == status)

    count_stmt = (
        select(func.count())
        .select_from(Matricula)
        .join(Turma, Turma.id == Matricula.turma)
        .join(AlunoCurso, AlunoCurso.id == Matricula.aluno_curso)
        .where(*filtros)
    )
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(base.where(*filtros).order_by(Matricula.id).offset(offset).limit(count))
    return list(result.scalars().all()), total


async def get_matricula_by_id(db: AsyncSession, matricula_id: int) -> Matricula:
    """Busca uma matrícula pelo ID."""
    matricula = (await db.execute(select(Matricula).where(Matricula.id == matricula_id))).scalar_one_or_none()
    if not matricula:
        raise BaseAPIException(message="Matrícula não encontrada.", code="MATRICULA_NOT_FOUND", status_code=404)
    return matricula


async def alterar_status(db: AsyncSession, matricula_id: int, novo_status: str) -> Matricula:
    """Altera o status de uma matrícula (valida contra SIGAA_MATRICULA_STATUS) e registra auditoria."""
    matricula = await get_matricula_by_id(db, matricula_id)
    valido = (await db.execute(select(MatriculaStatus).where(MatriculaStatus.id == novo_status))).scalar_one_or_none()
    if not valido:
        raise BaseAPIException(message=f"Status '{novo_status}' inválido.", code="STATUS_INVALIDO", status_code=400)
    matricula.status = novo_status
    await registrar_historico(db, matricula.aluno_curso, novo_status, matricula.turma, matricula.prioridade)
    await db.commit()
    await db.refresh(matricula)
    return matricula


async def comprovante_matricula(db: AsyncSession, aluno: str, periodo_letivo: str) -> dict:
    """Gera o comprovante de matrícula do aluno num período (matrículas com status 'MAT')."""
    vinculo = await _vinculo_do_aluno(db, aluno)
    result = await db.execute(
        select(Matricula, Turma, Disciplina)
        .join(Turma, Turma.id == Matricula.turma)
        .join(Disciplina, Disciplina.id == Turma.disciplina)
        .where(
            Matricula.aluno_curso == vinculo.id,
            Matricula.status == "MAT",
            Turma.periodo_letivo == periodo_letivo,
        )
    )
    itens = []
    carga_total = 0
    for mat, turma, disc in result.all():
        ch = carga_horaria(disc)
        carga_total += ch
        itens.append(
            {
                "matriculaId": mat.id,
                "disciplina": {"id": disc.id, "nome": disc.nome},
                "turma": turma.codigo,
                "cargaHoraria": ch,
                "status": mat.status,
            }
        )
    return {
        "resourceType": "ComprovanteMatricula",
        "aluno": aluno,
        "periodoLetivo": periodo_letivo,
        "cargaHorariaTotal": carga_total,
        "disciplinas": itens,
    }


async def historico_processamento(db: AsyncSession, aluno: str) -> list[MatriculaHistorico]:
    """Trilha de auditoria de processamento (SIGAA_MATRICULA_HISTORICO) de um aluno."""
    result = await db.execute(
        select(MatriculaHistorico)
        .join(AlunoCurso, AlunoCurso.id == MatriculaHistorico.aluno_curso)
        .where(AlunoCurso.aluno == aluno)
        .order_by(MatriculaHistorico.data_hora.desc())
    )
    return list(result.scalars().all())
