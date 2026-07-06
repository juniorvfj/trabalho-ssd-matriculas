"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Turma e Horário de Aula

Mapeia as tabelas SIGAA_TURMA, SIGAA_TURMA_HORARIOAULA e
SIGAA_RL_TURMA_HORARIOAULA do modelo do professor.

No schema SIGAA o período letivo é um 'character varying(5)' inline (ex.: '20182'),
não uma tabela; por isso NÃO existe mais a entidade PeriodoLetivo. O horário de aula
é normalizado em SIGAA_TURMA_HORARIOAULA (slots dia/hora) e associado às turmas
pela tabela SIGAA_RL_TURMA_HORARIOAULA.
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class HorarioAula(Base):
    """Entidade que mapeia a tabela SIGAA_TURMA_HORARIOAULA (slot de horário)."""
    __tablename__ = "sigaa_turma_horarioaula"

    # Código do slot (PK) — ex.: '208' (SEG 08:00-09:50)
    id = Column(String(3), primary_key=True)
    dia = Column(String(3), nullable=False)         # SEG, TER, ...
    hora_inicio = Column(String(5), nullable=False)  # '08:00'
    hora_fim = Column(String(5), nullable=False)     # '09:50'

    __table_args__ = (
        UniqueConstraint("dia", "hora_inicio", "hora_fim", name="horarioaula_unique"),
    )


class Turma(Base):
    """Entidade que mapeia a tabela SIGAA_TURMA (oferta de uma disciplina num período)."""
    __tablename__ = "sigaa_turma"

    # PK serial (inteiro autoincrementável), como no SIGAA
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(2), nullable=False)          # ex.: '01'
    periodo_letivo = Column(String(5), nullable=False)  # ex.: '20182'
    disciplina = Column(String(7), ForeignKey("sigaa_disciplina.id"), nullable=False)
    vagas = Column(Numeric(3, 0), nullable=True)
    sede = Column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint("codigo", "periodo_letivo", "disciplina", name="turma_unique"),
    )

    disciplina_rel = relationship("Disciplina")
    horarios = relationship("TurmaHorarioAula", back_populates="turma_rel")


class TurmaHorarioAula(Base):
    """
    Tabela associativa SIGAA_RL_TURMA_HORARIOAULA (M:N Turma ↔ Horário).

    Observação de fidelidade: no DDL do professor a coluna HORARIOAULA é
    'character varying(2)', embora os códigos de slot tenham 3 dígitos. O tamanho
    é replicado como no original; não há DML de carga para esta tabela nos scripts.
    """
    __tablename__ = "sigaa_rl_turma_horarioaula"

    turma = Column(Integer, ForeignKey("sigaa_turma.id"), primary_key=True)
    horarioaula = Column(String(2), ForeignKey("sigaa_turma_horarioaula.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint("horarioaula", "turma", name="turma_haula_unique"),
    )

    turma_rel = relationship("Turma", back_populates="horarios")
    horario_rel = relationship("HorarioAula")
