"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Matrícula

Mapeia as tabelas SIGAA_MATRICULA_STATUS, SIGAA_MATRICULA e
SIGAA_MATRICULA_HISTORICO do modelo do professor.

Diferenças conceituais em relação ao modelo antigo do projeto:
- Não há tabelas separadas de "solicitação" e "matrícula efetivada": há uma única
  tabela SIGAA_MATRICULA cujo estágio é indicado pelo STATUS (código de 3 letras).
- O STATUS é uma tabela de domínio (SIGAA_MATRICULA_STATUS) com 14 códigos
  (PRE, PND, REJ, REA, REC, MAT, TRA, CAN, NEL, CEX, JMD, CON, FUL, CFM),
  carregados via DML do professor — substitui o antigo Enum Python.
- A trilha de mudanças de estado fica em SIGAA_MATRICULA_HISTORICO.
- A matrícula referencia o vínculo aluno-curso (SIGAA_RL_ALUNO_CURSO), não o aluno.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class MatriculaStatus(Base):
    """Tabela de domínio SIGAA_MATRICULA_STATUS (códigos de estado da matrícula)."""
    __tablename__ = "sigaa_matricula_status"

    # Código de 3 letras (PK) — ex.: 'MAT', 'PND', 'NEL'
    id = Column(String(3), primary_key=True)
    status = Column(String(30), nullable=False)  # descrição legível


class Matricula(Base):
    """
    Entidade que mapeia a tabela SIGAA_MATRICULA.

    Representa o vínculo (em qualquer estágio) entre um vínculo aluno-curso e uma
    turma. O estágio no fluxo de matrícula é dado pela FK 'status'.
    """
    __tablename__ = "sigaa_matricula"

    # PK serial (inteiro autoincrementável), como no SIGAA
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_curso = Column(Integer, ForeignKey("sigaa_rl_aluno_curso.id"), nullable=False)
    turma = Column(Integer, ForeignKey("sigaa_turma.id"), nullable=False)
    status = Column(String(3), ForeignKey("sigaa_matricula_status.id"), nullable=False)
    prioridade = Column(Numeric(2, 0), nullable=True)

    # --- Relacionamentos ORM ---
    vinculo = relationship("AlunoCurso")
    turma_rel = relationship("Turma")
    status_rel = relationship("MatriculaStatus")


class MatriculaHistorico(Base):
    """
    Entidade que mapeia a tabela SIGAA_MATRICULA_HISTORICO.

    Registra cada transição de estado de uma matrícula (trilha de auditoria do
    processamento), com data/hora do evento. Fidelidade ao SIGAA: a coluna 'turma'
    é um inteiro sem constraint de FK (assim como no DDL do professor).
    """
    __tablename__ = "sigaa_matricula_historico"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_curso = Column(Integer, ForeignKey("sigaa_rl_aluno_curso.id"), nullable=False)
    status = Column(String(3), ForeignKey("sigaa_matricula_status.id"), nullable=False)
    turma = Column(Integer, nullable=False)
    prioridade = Column(Numeric(2, 0), nullable=True)
    data_hora = Column(DateTime(timezone=True), nullable=True)

    # --- Relacionamentos ORM ---
    vinculo = relationship("AlunoCurso")
    status_rel = relationship("MatriculaStatus")
