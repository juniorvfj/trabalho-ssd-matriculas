from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    alunos = relationship("Aluno", back_populates="curso")
