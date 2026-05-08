"""
Módulo de Modelos ORM (Infrastructure Layer) para Docentes

Define a tabela 'docentes' que representa professores e coordenadores.
Conforme o diagrama de entidades, um Docente pode atuar como:
- Coordenador de um Curso (relação 0..1 via FK em cursos)
- Professor de uma ou mais Turmas (relação N:M via tabela associativa turma_docentes)
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Docente(Base):
    """
    Entidade representando um docente (professor/coordenador).
    Possui matricula e nome conforme o diagrama de entidades.
    """
    __tablename__ = "docentes"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamento com turmas via tabela associativa
    turma_docentes = relationship("TurmaDocente", back_populates="docente")


class TurmaDocente(Base):
    """
    Tabela Associativa para mapear a relação N:M entre Turma e Docente.
    No diagrama: Turma → docente 0..* → Docente.
    Uma turma pode ter vários docentes e um docente pode lecionar em várias turmas.
    """
    __tablename__ = "turma_docentes"

    id = Column(Integer, primary_key=True, index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    docente_id = Column(Integer, ForeignKey("docentes.id"), nullable=False)

    docente = relationship("Docente", back_populates="turma_docentes")
    turma = relationship("app.modules.turmas.infrastructure.orm_models.Turma")
