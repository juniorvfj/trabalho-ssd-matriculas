"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Curso

Mapeia as tabelas SIGAA_CURSO e SIGAA_RL_CURSO_UNIDADE do modelo do professor.
O curso usa como PK o código natural de 4 caracteres (ex.: '6351'). No schema SIGAA
o coordenador é apenas um nome-texto (não há entidade Docente), e o vínculo com a
unidade organizacional é feito pela tabela associativa SIGAA_RL_CURSO_UNIDADE (M:N).
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Curso(Base):
    """Entidade que mapeia a tabela SIGAA_CURSO."""
    __tablename__ = "sigaa_curso"

    # Código natural do curso (PK) — ex.: '6351'
    id = Column(String(4), primary_key=True)
    nome = Column(String(100), nullable=False)
    grau_academico = Column(String(15), nullable=False)  # ex.: 'BACHAREL'
    turno = Column(String(10), nullable=False)           # ex.: 'DIURNO'
    modalidade = Column(String(25), nullable=False)      # ex.: 'PRESENCIAL'
    # No SIGAA o coordenador é o nome do docente (não há entidade Docente)
    coordenador = Column(String(100), nullable=True)

    # Unidades organizacionais vinculadas (via tabela associativa)
    unidades = relationship("CursoUnidade", back_populates="curso_rel")


class CursoUnidade(Base):
    """Tabela associativa SIGAA_RL_CURSO_UNIDADE (M:N Curso ↔ Unidade)."""
    __tablename__ = "sigaa_rl_curso_unidade"

    curso = Column(String(4), ForeignKey("sigaa_curso.id"), primary_key=True)
    unidade = Column(String(3), ForeignKey("sigaa_unidade.id"), primary_key=True)

    curso_rel = relationship("Curso", back_populates="unidades")
    unidade_rel = relationship("UnidadeOrganizacional")
