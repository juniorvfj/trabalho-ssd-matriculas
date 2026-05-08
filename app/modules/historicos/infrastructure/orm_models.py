"""
Módulo de Modelos ORM (Infrastructure Layer) para Histórico Acadêmico

Define as tabelas 'historicos_academicos' (visão consolidada 1:1 com Aluno)
e 'historico_disciplinas' (itens individuais de disciplinas cursadas).

O HistoricoAcademico agrega dados resumidos como carga horária integralizada/pendente
e status geral (ATIVO, INATIVO, CONCLUIDO).

Cada HistoricoDisciplina registra o desempenho do aluno em uma disciplina
cursada em um determinado período letivo, incluindo menção, frequência e status.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class StatusHistoricoAcademico(str, enum.Enum):
    """
    Enum que representa os possíveis estados do histórico acadêmico
    consolidado do aluno (1:1 com Aluno).
    """
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    CONCLUIDO = "CONCLUIDO"


class StatusDisciplinaHistorico(str, enum.Enum):
    """
    Enum que representa os possíveis estados de conclusão de uma disciplina
    no histórico acadêmico do aluno.
    """
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    TRANCADO = "TRANCADO"
    CURSANDO = "CURSANDO"


class HistoricoAcademico(Base):
    """
    Entidade consolidada que representa o histórico acadêmico de um aluno.

    Mantém relação 1:1 com Aluno e agrega informações de resumo como
    carga horária integralizada, pendente e status geral do vínculo acadêmico.
    Possui uma coleção de HistoricoDisciplina com os itens individuais.
    """
    __tablename__ = "historicos_academicos"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o aluno (relação 1:1)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False, unique=True)

    # Carga horária já cumprida pelo aluno
    carga_horaria_integralizada = Column(Integer, default=0, nullable=False)

    # Carga horária ainda pendente para conclusão do curso
    carga_horaria_pendente = Column(Integer, default=0, nullable=False)

    # Status geral do histórico (ATIVO, INATIVO, CONCLUIDO)
    status = Column(SAEnum(StatusHistoricoAcademico), default=StatusHistoricoAcademico.ATIVO, nullable=False)

    # --- Relacionamentos ORM ---
    aluno = relationship("Aluno")
    disciplinas = relationship("HistoricoDisciplina", back_populates="historico_academico", lazy="selectin")


class HistoricoDisciplina(Base):
    """
    Entidade que registra o desempenho do aluno em cada disciplina cursada.

    Cada registro representa uma disciplina cursada pelo aluno num dado período,
    com menção obtida, frequência e status individual.
    É a base de dados utilizada pelo serviço 'verificarElegibilidade'.
    """
    __tablename__ = "historico_disciplinas"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o histórico acadêmico consolidado
    historico_academico_id = Column(Integer, ForeignKey("historicos_academicos.id"), nullable=False)

    # FK para a disciplina cursada
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    # FK para o período letivo em que foi cursada (ex: 2025.1)
    periodo_letivo_id = Column(Integer, ForeignKey("periodos_letivos.id"), nullable=False)

    # Menção obtida (ex: SS, MS, MM, MI, II, SR)
    mencao = Column(String(10), nullable=True)

    # Frequência do aluno na disciplina (percentual 0-100)
    frequencia = Column(Integer, nullable=True)

    # Status do aluno naquela disciplina (APROVADO, REPROVADO, TRANCADO, CURSANDO)
    status = Column(SAEnum(StatusDisciplinaHistorico), nullable=False)

    # --- Relacionamentos ORM ---
    historico_academico = relationship("HistoricoAcademico", back_populates="disciplinas")
    disciplina = relationship("Disciplina")
    periodo_letivo = relationship("PeriodoLetivo")
