"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Aluno e Vínculo Aluno-Curso

Mapeia as tabelas SIGAA_ALUNO e SIGAA_RL_ALUNO_CURSO do modelo do professor.

No schema SIGAA o aluno guarda apenas matrícula e nome; os dados acadêmicos do
vínculo (curso, currículo, período de ingresso, status e IRA) ficam em
SIGAA_RL_ALUNO_CURSO. A PK do aluno é a própria matrícula (character varying(9)).
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Aluno(Base):
    """Entidade que mapeia a tabela SIGAA_ALUNO."""
    __tablename__ = "sigaa_aluno"

    # Matrícula do aluno (PK natural) — ex.: '180012345'
    matricula = Column(String(9), primary_key=True)
    nome = Column(String(80), nullable=False)

    # Vínculos aluno-curso (um aluno pode ter mais de um vínculo)
    vinculos = relationship("AlunoCurso", back_populates="aluno_rel")


class AlunoCurso(Base):
    """
    Tabela SIGAA_RL_ALUNO_CURSO: vínculo do aluno com um curso/currículo.
    Concentra o IRA, o período letivo de ingresso, a data de registro e o status.
    """
    __tablename__ = "sigaa_rl_aluno_curso"

    # PK serial (inteiro autoincrementável), como no SIGAA
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno = Column(String(9), ForeignKey("sigaa_aluno.matricula"), nullable=False)
    curso = Column(String(4), ForeignKey("sigaa_curso.id"), nullable=False)
    curriculo = Column(String(7), ForeignKey("sigaa_curriculo.id"), nullable=False)
    data_registro = Column(Date, nullable=False)
    periodo_letivo_registro = Column(String(5), nullable=False)  # ex.: '20182'
    status = Column(String(1), nullable=True)  # ex.: 'A'
    ira = Column(Float, nullable=True)         # REAL no SIGAA

    __table_args__ = (
        UniqueConstraint("aluno", "curso", "periodo_letivo_registro", name="aluno_curso_unique"),
    )

    aluno_rel = relationship("Aluno", back_populates="vinculos")
    curso_rel = relationship("Curso")
    curriculo_rel = relationship("Curriculo")
