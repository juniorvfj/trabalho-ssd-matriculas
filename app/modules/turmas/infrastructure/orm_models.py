"""
Módulo de Modelos ORM (Infrastructure Layer) para Turmas

Define as tabelas de Período Letivo e Turma (instância de oferta de uma Disciplina num Período).
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

class PeriodoLetivo(Base):
    """Representa um semestre ou ciclo acadêmico (ex: 2026.1)."""
    __tablename__ = "periodos_letivos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False) # Ex: 2026.1
    descricao = Column(String(150), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    turmas = relationship("Turma", back_populates="periodo_letivo")

class Turma(Base):
    """
    Representa a oferta de uma disciplina.
    Tem chaves estrangeiras tanto para 'disciplinas' quanto para 'periodos_letivos'.
    """
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    periodo_letivo_id = Column(Integer, ForeignKey("periodos_letivos.id"), nullable=False)
    codigo_turma = Column(String(10), nullable=False) # Ex: A, B, T01
    
    # Controle de vagas que poderá sofrer concorrência em sistemas distribuídos
    vagas_totais = Column(Integer, nullable=False)
    vagas_ocupadas = Column(Integer, default=0, nullable=False)
    
    horario_serializado = Column(String(200), nullable=False) # Ex: 24T34
    ativa = Column(Boolean, default=True, nullable=False)

    disciplina = relationship("Disciplina")
    periodo_letivo = relationship("PeriodoLetivo", back_populates="turmas")
