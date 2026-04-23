from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    creditos = Column(Integer, nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)

    curso = relationship("Curso")
    prerequisitos = relationship(
        "DisciplinaPrerequisito",
        foreign_keys="[DisciplinaPrerequisito.disciplina_id]",
        back_populates="disciplina"
    )

class DisciplinaPrerequisito(Base):
    __tablename__ = "disciplinas_prerequisitos"

    id = Column(Integer, primary_key=True, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    prerequisito_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    disciplina = relationship("Disciplina", foreign_keys=[disciplina_id], back_populates="prerequisitos")
    prerequisito = relationship("Disciplina", foreign_keys=[prerequisito_id])
