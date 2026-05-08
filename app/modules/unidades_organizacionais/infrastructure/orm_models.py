"""
Módulo de Modelos ORM (Infrastructure Layer) para Unidades Organizacionais

Define a tabela 'unidades_organizacionais' que representa departamentos,
institutos e faculdades da universidade.
Conforme o diagrama de entidades:
- Curso → unidadeOrganizacional (0..*) — Um curso pertence a uma UO
- Disciplina → unidadeOrganizacional (0..1) — Uma disciplina pode pertencer a uma UO
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class UnidadeOrganizacional(Base):
    """
    Entidade representando uma unidade organizacional (departamento/instituto/faculdade).
    Possui codigo e nome conforme o diagrama de entidades.
    """
    __tablename__ = "unidades_organizacionais"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos bidirecionais
    cursos = relationship("app.modules.cursos.infrastructure.orm_models.Curso", back_populates="unidade_organizacional")
    disciplinas = relationship("app.modules.disciplinas.infrastructure.orm_models.Disciplina", back_populates="unidade_organizacional")
