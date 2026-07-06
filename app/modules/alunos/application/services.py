"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Serviços (Application Layer) de Aluno — modelo SIGAA.

Consultas sobre SIGAA_ALUNO e SIGAA_RL_ALUNO_CURSO (com junção a SIGAA_CURSO),
reproduzindo as consultas de detalhe e busca do arquivo SIGAA-API.sql do professor.
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BaseAPIException
from app.modules.alunos.api.schemas import AlunoCreate
from app.modules.alunos.infrastructure.orm_models import Aluno, AlunoCurso
from app.modules.cursos.infrastructure.orm_models import Curso


async def search_alunos(
    db: AsyncSession,
    nome: Optional[str],
    curso: Optional[str],
    periodo_ingresso: Optional[str],
    offset: int,
    count: int,
) -> tuple[list[Aluno], int]:
    """
    Pesquisa alunos por nome, curso e/ou período de ingresso, com paginação.
    A junção com SIGAA_RL_ALUNO_CURSO reproduz a consulta de busca do professor.
    """
    stmt = select(Aluno).join(AlunoCurso, AlunoCurso.aluno == Aluno.matricula)
    count_stmt = select(func.count(func.distinct(Aluno.matricula))).select_from(Aluno).join(
        AlunoCurso, AlunoCurso.aluno == Aluno.matricula
    )
    filtros = []
    if nome:
        filtros.append(Aluno.nome.ilike(f"%{nome}%"))
    if curso:
        filtros.append(AlunoCurso.curso == curso)
    if periodo_ingresso:
        filtros.append(AlunoCurso.periodo_letivo_registro == periodo_ingresso)

    total = (await db.execute(count_stmt.where(*filtros))).scalar_one()
    result = await db.execute(stmt.where(*filtros).order_by(Aluno.nome).offset(offset).limit(count))
    return list(result.scalars().all()), total


async def get_aluno_by_matricula(db: AsyncSession, matricula: str) -> Aluno:
    """Busca um aluno pela matrícula (PK). Dispara 404 caso não exista."""
    aluno = (await db.execute(select(Aluno).where(Aluno.matricula == matricula))).scalar_one_or_none()
    if not aluno:
        raise BaseAPIException(message="Aluno não encontrado", code="ALUNO_NOT_FOUND", status_code=404)
    return aluno


async def get_vinculo_com_curso(db: AsyncSession, matricula: str) -> Optional[tuple[AlunoCurso, Curso]]:
    """Retorna o vínculo aluno-curso mais recente (com o curso) para um aluno, se houver."""
    result = await db.execute(
        select(AlunoCurso, Curso)
        .join(Curso, Curso.id == AlunoCurso.curso)
        .where(AlunoCurso.aluno == matricula)
        .order_by(AlunoCurso.periodo_letivo_registro.desc())
    )
    return result.first()


async def create_aluno(db: AsyncSession, aluno_in: AlunoCreate) -> Aluno:
    """
    Cadastra um aluno e o vínculo com seu curso/currículo.
    Valida existência do curso e unicidade da matrícula.
    """
    if not (await db.execute(select(Curso).where(Curso.id == aluno_in.curso))).scalar_one_or_none():
        raise BaseAPIException(message="O curso referenciado não existe.", code="CURSO_INVALIDO", status_code=400)
    if (await db.execute(select(Aluno).where(Aluno.matricula == aluno_in.matricula))).scalar_one_or_none():
        raise BaseAPIException(message="Matrícula já existente.", code="MATRICULA_DUPLICADA", status_code=400)

    db_aluno = Aluno(matricula=aluno_in.matricula, nome=aluno_in.nome)
    db_vinculo = AlunoCurso(
        aluno=aluno_in.matricula,
        curso=aluno_in.curso,
        curriculo=aluno_in.curriculo,
        data_registro=aluno_in.data_registro,
        periodo_letivo_registro=aluno_in.periodo_letivo_registro,
        status=aluno_in.status,
        ira=aluno_in.ira,
    )
    db.add(db_aluno)
    db.add(db_vinculo)
    await db.commit()
    await db.refresh(db_aluno)
    return db_aluno
