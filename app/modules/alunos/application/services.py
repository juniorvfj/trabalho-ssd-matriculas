"""
Módulo de Serviços de Alunos (Application Layer)

Concentra todas as regras de negócio da entidade Aluno.
A camada de rotas (router) apenas recebe as requisições e as repassa para estes serviços.
Isso facilita o reuso de código e a criação de testes unitários sem precisar simular requisições HTTP.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.cursos.infrastructure.orm_models import Curso
from ..api.schemas import AlunoCreate, AlunoUpdate
from app.core.exceptions import BaseAPIException

async def get_aluno_by_id(db: AsyncSession, aluno_id: int) -> Aluno:
    """Busca um aluno específico no banco. Se não encontrar, levanta a exceção customizada."""
    stmt = select(Aluno).where(Aluno.id == aluno_id)
    result = await db.execute(stmt)
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise BaseAPIException(message="Aluno não encontrado", code="ALUNO_NOT_FOUND", status_code=404)
    return aluno

async def list_alunos(db: AsyncSession):
    """Retorna todos os alunos ativos."""
    stmt = select(Aluno)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_aluno(db: AsyncSession, aluno_in: AlunoCreate) -> Aluno:
    """
    Cadastra um novo aluno aplicando regras de negócio:
    - O curso referenciado deve existir.
    - A matrícula não pode estar duplicada.
    - O e-mail não pode estar duplicado.
    """
    # Validações de negócio
    # 1. Curso existe?
    stmt_curso = select(Curso).where(Curso.id == aluno_in.curso_id)
    res_curso = await db.execute(stmt_curso)
    if not res_curso.scalar_one_or_none():
        raise BaseAPIException(message="O curso referenciado não existe.", code="CURSO_INVALIDO", status_code=400)
        
    # 2. Matrícula ou email já existe?
    stmt_mat = select(Aluno).where(Aluno.matricula == aluno_in.matricula)
    if (await db.execute(stmt_mat)).scalar_one_or_none():
        raise BaseAPIException(message="Matrícula já existente.", code="MATRICULA_DUPLICADA", status_code=400)

    stmt_email = select(Aluno).where(Aluno.email == aluno_in.email)
    if (await db.execute(stmt_email)).scalar_one_or_none():
        raise BaseAPIException(message="Email já existente.", code="EMAIL_DUPLICADO", status_code=400)

    # Criação do objeto ORM a partir do schema validado
    db_obj = Aluno(**aluno_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
