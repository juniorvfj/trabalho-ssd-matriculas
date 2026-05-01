"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Testes Unitários de Elegibilidade de Matrícula
Descrição: Valida o motor de regras de negócio responsável por garantir
que alunos só se matriculem em disciplinas pertencentes ao seu currículo, 
que não tenham sido previamente aprovadas e que tenham seus pré-requisitos cumpridos.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.matriculas.application.elegibilidade import verificar_elegibilidade
from app.modules.matriculas.infrastructure.orm_models import SolicitacaoMatricula
from app.modules.turmas.infrastructure.orm_models import Turma, PeriodoLetivo
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.disciplinas.infrastructure.orm_models import Disciplina
from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.historicos.infrastructure.orm_models import HistoricoAcademico, StatusHistorico
from datetime import date

@pytest.mark.asyncio
async def test_verificar_elegibilidade_sem_restricao(db_session: AsyncSession):
    """
    Testa o caminho feliz: Aluno apto a cursar uma disciplina (MATA01)
    pois não tem histórico prévio de aprovação nem há pré-requisitos não cumpridos.
    O retorno deve ser elegivel=True.
    """
    # Setup Data
    curso = Curso(codigo="BCC_TEST", nome="Ciência da Computação")
    db_session.add(curso)
    await db_session.flush()

    aluno = Aluno(nome="Aluno CC 1", email="aluno.cc.test@ufba.br", matricula="12345678", data_admissao=date(2025, 1, 1), curso_id=curso.id, ira=9.0)
    db_session.add(aluno)
    await db_session.flush()

    disciplina = Disciplina(codigo="MATA01_TEST", nome="MATA01", curso_id=curso.id, carga_horaria=60, creditos=4)
    db_session.add(disciplina)
    await db_session.flush()

    periodo = PeriodoLetivo(codigo="2026.1_TEST", descricao="Semestre Atual", data_inicio=date(2026,3,1), data_fim=date(2026,7,1), ativo=True)
    db_session.add(periodo)
    await db_session.flush()

    turma = Turma(codigo_turma="T01_TEST", disciplina_id=disciplina.id, horario_serializado="24T34", vagas_totais=30, periodo_letivo_id=periodo.id)
    db_session.add(turma)
    await db_session.flush()

    # Test
    # The student has no history, but the course has no prerequisites, so should be eligible
    resultado = await verificar_elegibilidade(db_session, aluno.id, disciplina.id)
    assert resultado["elegivel"] is True

@pytest.mark.asyncio
async def test_verificar_elegibilidade_ja_aprovado(db_session: AsyncSession):
    """
    Testa o bloqueio de elegibilidade: O aluno tenta cursar uma disciplina (MATA02)
    na qual ele já foi aprovado em um semestre anterior.
    O retorno deve ser elegivel=False.
    """
    # Setup Data
    curso = Curso(codigo="BCC2_TEST", nome="Ciência da Computação")
    db_session.add(curso)
    await db_session.flush()

    aluno = Aluno(nome="Aluno CC 2", email="aluno.cc2.test@ufba.br", matricula="87654321", data_admissao=date(2025, 1, 1), curso_id=curso.id, ira=9.0)
    db_session.add(aluno)
    
    disciplina = Disciplina(codigo="MATA02_TEST", nome="MATA02", curso_id=curso.id, carga_horaria=60, creditos=4)
    db_session.add(disciplina)
    
    periodo_antigo = PeriodoLetivo(codigo="2025.1_TEST", descricao="Semestre Passado", data_inicio=date(2025,3,1), data_fim=date(2025,7,1), ativo=False)
    db_session.add(periodo_antigo)

    periodo_atual = PeriodoLetivo(codigo="2026.2_TEST", descricao="Semestre Atual", data_inicio=date(2026,3,1), data_fim=date(2026,7,1), ativo=True)
    db_session.add(periodo_atual)
    
    await db_session.flush()

    historico = HistoricoAcademico(aluno_id=aluno.id, disciplina_id=disciplina.id, periodo_letivo_id=periodo_antigo.id, status=StatusHistorico.APROVADO, aprovado=True, nota_final=9.0)
    db_session.add(historico)
    
    turma = Turma(codigo_turma="T02_TEST", disciplina_id=disciplina.id, horario_serializado="24T34", vagas_totais=30, periodo_letivo_id=periodo_atual.id)
    db_session.add(turma)
    await db_session.flush()

    # Test
    # The student is already approved in MATA02, should NOT be eligible to take it again
    resultado = await verificar_elegibilidade(db_session, aluno.id, disciplina.id)
    assert resultado["elegivel"] is False
