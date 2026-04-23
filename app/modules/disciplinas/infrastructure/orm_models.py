"""
Módulo de Modelos ORM (Infrastructure Layer) para Disciplinas

Define a tabela de disciplinas e a tabela de associação para resolver o relacionamento
muitos-para-muitos (M:N) dos pré-requisitos entre as próprias disciplinas.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Disciplina(Base):
    """Entidade que mapeia a tabela de disciplinas."""
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    creditos = Column(Integer, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)

    # Relacionamento simples com Curso
    curso = relationship("Curso")
    
    # Relacionamento com a tabela associativa de pré-requisitos
    prerequisitos = relationship(
        "DisciplinaPrerequisito",
        foreign_keys="[DisciplinaPrerequisito.disciplina_id]",
        back_populates="disciplina"
    )

class DisciplinaPrerequisito(Base):
    """
    Tabela Associativa (Join Table) para mapear quais disciplinas são pré-requisitos de outras.
    Resolve o relacionamento M:N onde uma Disciplina A requer que a Disciplina B tenha sido cursada.
    """
    __tablename__ = "disciplinas_prerequisitos"

    id = Column(Integer, primary_key=True, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    prerequisito_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    disciplina = relationship("Disciplina", foreign_keys=[disciplina_id], back_populates="prerequisitos")
    
    # Disciplina que deve ser concluída antes da 'disciplina'
    prerequisito = relationship("Disciplina", foreign_keys=[prerequisito_id])
