"""
Módulo de Modelos ORM (Infrastructure Layer)

Define o modelo de banco de dados para a entidade Aluno utilizando SQLAlchemy.
O mapeamento Objeto-Relacional (ORM) traduz esta classe Python para uma tabela SQL.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Aluno(Base):
    """
    Representação da tabela 'alunos' no banco de dados.
    """
    __tablename__ = "alunos"

    # Chave primária (ID autoincrementável)
    id = Column(Integer, primary_key=True, index=True)
    
    matricula = Column(String(9), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    data_admissao = Column(Date, nullable=False)
    ira = Column(Float, default=0.0, nullable=False)
    limite_creditos_periodo = Column(Integer, default=32, nullable=False)
    
    # Chave estrangeira ligando o Aluno a um Curso
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    
    ativo = Column(Boolean, default=True, nullable=False)

    # O relationship permite acessar os dados do curso do aluno como um objeto (aluno.curso)
    curso = relationship("app.modules.cursos.infrastructure.orm_models.Curso", back_populates="alunos")
