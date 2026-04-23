"""
Módulo de Modelos ORM (Infrastructure Layer) para Cursos

Este modelo mapeia a classe Python `Curso` para a tabela `cursos` no SGBD Relacional.
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Curso(Base):
    """
    Entidade representando os cursos oferecidos.
    Possui uma relação de Um-para-Muitos (1:N) com a tabela Alunos.
    """
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # Estabelece a ligação bidirecional com a classe Aluno
    alunos = relationship("app.modules.alunos.infrastructure.orm_models.Aluno", back_populates="curso")
