"""
Módulo de Modelos ORM (Infrastructure Layer) para Histórico Acadêmico

Define a tabela 'historicos_academicos', que registra o desempenho do aluno
em cada disciplina cursada ao longo dos períodos letivos. É a base de dados
utilizada pelo serviço 'verificarElegibilidade' para checar se o aluno já
foi aprovado numa disciplina ou se cumpriu seus pré-requisitos.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class StatusHistorico(str, enum.Enum):
    """
    Enum que representa os possíveis estados de conclusão de uma disciplina.
    Utilizar um Enum garante integridade referencial no banco e evita
    strings arbitrárias (princípio de validação forte).
    """
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    TRANCADO = "TRANCADO"
    CURSANDO = "CURSANDO"


class HistoricoAcademico(Base):
    """
    Entidade que mapeia a tabela de histórico acadêmico.

    Cada registro representa uma disciplina cursada por um aluno num dado período.
    Relaciona-se com as tabelas 'alunos', 'disciplinas' e 'periodos_letivos'
    via chaves estrangeiras (Foreign Keys).
    """
    __tablename__ = "historicos_academicos"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o aluno que cursou a disciplina
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)

    # FK para a disciplina cursada
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    # FK para o período letivo em que foi cursada (ex: 2025.1)
    periodo_letivo_id = Column(Integer, ForeignKey("periodos_letivos.id"), nullable=False)

    # Status do aluno naquela disciplina (APROVADO, REPROVADO, etc.)
    status = Column(SAEnum(StatusHistorico), nullable=False)

    # Nota final obtida (0.0 a 10.0). Pode ser nula se o aluno trancou.
    nota_final = Column(Float, nullable=True)

    # Flag de aprovação calculada para consultas rápidas
    aprovado = Column(Boolean, default=False, nullable=False)

    # --- Relacionamentos ORM ---
    # Permitem navegar do histórico até o aluno, disciplina e período facilmente.
    aluno = relationship("Aluno")
    disciplina = relationship("Disciplina")
    periodo_letivo = relationship("PeriodoLetivo")
