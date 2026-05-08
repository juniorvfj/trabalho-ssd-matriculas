"""
Módulo de Modelos ORM (Infrastructure Layer) para Cursos

Este modelo mapeia a classe Python `Curso` para a tabela `cursos` no SGBD Relacional.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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
    turno = Column(String(50), nullable=True)        # Ex: Diurno, Noturno, Integral
    grau = Column(String(50), nullable=True)          # Ex: Bacharelado, Licenciatura
    modalidade = Column(String(50), nullable=True)    # Ex: Presencial, EAD
    sede = Column(String(100), nullable=True)         # Ex: Campus Darcy Ribeiro

    # FK para o coordenador do curso (relação 0..1 com Docente no diagrama)
    coordenador_id = Column(Integer, ForeignKey("docentes.id"), nullable=True)

    # FK para a unidade organizacional (departamento/instituto)
    unidade_organizacional_id = Column(Integer, ForeignKey("unidades_organizacionais.id"), nullable=True)

    ativo = Column(Boolean, default=True, nullable=False)

    # Estabelece a ligação bidirecional com a classe Aluno
    alunos = relationship("app.modules.alunos.infrastructure.orm_models.Aluno", back_populates="curso")

    # Ligação bidirecional com Curriculo
    curriculos = relationship("app.modules.curriculos.infrastructure.orm_models.Curriculo", back_populates="curso")

    # Relacionamento com o coordenador (Docente)
    coordenador = relationship("app.modules.docentes.infrastructure.orm_models.Docente")

    # Relacionamento com a unidade organizacional
    unidade_organizacional = relationship("app.modules.unidades_organizacionais.infrastructure.orm_models.UnidadeOrganizacional", back_populates="cursos")

