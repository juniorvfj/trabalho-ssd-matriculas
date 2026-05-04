"""
Módulo de Modelos ORM (Infrastructure Layer) para Currículos

Define as tabelas de Currículo e a tabela associativa com Disciplinas.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

class Curriculo(Base):
    """
    Entidade representando o Currículo de um Curso.
    """
    __tablename__ = "curriculos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(String(20), default="ativo", nullable=False) # "ativo" ou "inativo"
    data_validade = Column(Date, nullable=True)
    
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    periodo_letivo_vigor_id = Column(Integer, ForeignKey("periodos_letivos.id"), nullable=False)

    # Atributos achatados de Carga Horária (Value Object no modelo)
    carga_horaria_total_minima = Column(Integer, default=0, nullable=False)
    carga_horaria_obrigatoria_aula = Column(Integer, default=0, nullable=False)
    carga_horaria_obrigatoria_orientacao = Column(Integer, default=0, nullable=False)
    carga_horaria_obrigatoria_total = Column(Integer, default=0, nullable=False)
    carga_horaria_optativa_minima = Column(Integer, default=0, nullable=False)
    carga_horaria_maxima_eletivos = Column(Integer, default=0, nullable=False)
    carga_horaria_maxima_periodo = Column(Integer, default=0, nullable=False)
    carga_horaria_minima_periodo = Column(Integer, default=0, nullable=False)

    # Atributos achatados de Prazo (Value Object no modelo)
    prazo_minimo = Column(Integer, default=0, nullable=False)
    prazo_medio = Column(Integer, default=0, nullable=False)
    prazo_maximo = Column(Integer, default=0, nullable=False)

    # Relacionamentos
    curso = relationship("Curso", back_populates="curriculos")
    periodo_letivo_vigor = relationship("PeriodoLetivo", foreign_keys=[periodo_letivo_vigor_id])
    
    # Relacionamento com disciplinas (Tabela Associativa)
    disciplinas = relationship("CurriculoDisciplina", back_populates="curriculo")


class CurriculoDisciplina(Base):
    """
    Tabela Associativa para mapear os componentes curriculares (Disciplinas de um Currículo).
    Resolve o relacionamento M:N entre Curriculo e Disciplina, com atributos adicionais.
    """
    __tablename__ = "curriculo_disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    curriculo_id = Column(Integer, ForeignKey("curriculos.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    
    tipo = Column(String(50), nullable=False) # Ex: "Obrigatória", "Optativa", "Módulo Livre"
    nivel = Column(Integer, nullable=False)   # Ex: 1 (1º semestre), 2 (2º semestre)

    # Relacionamentos
    curriculo = relationship("Curriculo", back_populates="disciplinas")
    disciplina = relationship("Disciplina")
