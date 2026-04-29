"""
Módulo de Modelos ORM (Infrastructure Layer) para Matrículas

Define as tabelas 'solicitacoes_matricula', 'matriculas' e 'auditoria_processamento',
que suportam o fluxo completo de matrícula: desde a solicitação do aluno até o registro
de auditoria das decisões tomadas no processamento batch (Fases 3 e 5).

A entidade SolicitacaoMatricula representa a intenção do aluno (§5.3).
A entidade Matricula representa a efetivação da matrícula aprovada (§6.11).
A entidade AuditoriaProcessamento registra cada decisão do processamento (§6.12).
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
import enum


class StatusSolicitacao(str, enum.Enum):
    """
    Enum que representa os possíveis estados de uma solicitação de matrícula.
    Utilizar um Enum garante integridade referencial no banco e evita
    strings arbitrárias (princípio de validação forte).
    """
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"


class StatusMatricula(str, enum.Enum):
    """
    Enum que representa os possíveis estados de uma matrícula efetivada.
    Uma matrícula nasce ATIVA e pode ser CANCELADA (pelo aluno) ou TRANCADA.
    """
    ATIVA = "ATIVA"
    CANCELADA = "CANCELADA"
    TRANCADA = "TRANCADA"


class SolicitacaoMatricula(Base):
    """
    Entidade que registra a intenção de matrícula de um aluno em uma turma.

    Cada solicitação passa pelas fases de processamento (Fase 3, Fase 5) e pode ser
    APROVADA (gerando uma Matrícula) ou REJEITADA (com motivo registrado no campo 'resultado').
    Relaciona-se com as tabelas 'alunos' e 'turmas' via chaves estrangeiras.
    """
    __tablename__ = "solicitacoes_matricula"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o aluno que solicita a matrícula
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)

    # FK para a turma desejada pelo aluno
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)

    # Prioridade numérica da solicitação (menor = mais prioritária para o aluno)
    prioridade = Column(Integer, default=0, nullable=False)

    # Fase do processamento em que a solicitação foi criada (ex: FASE_3, FASE_5, EXTRAORDINARIA)
    fase = Column(String(30), nullable=False, default="FASE_3")

    # Estado atual da solicitação no pipeline de processamento
    status = Column(SAEnum(StatusSolicitacao), default=StatusSolicitacao.PENDENTE, nullable=False)

    # Motivo da rejeição, preenchido apenas quando status = REJEITADA
    resultado = Column(String(500), nullable=True)

    # Registro temporal para ordenação e rastreabilidade
    timestamp_solicitacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relacionamentos ORM ---
    aluno = relationship("Aluno")
    turma = relationship("Turma")


class Matricula(Base):
    """
    Entidade que representa uma matrícula efetivada — o vínculo confirmado
    entre um aluno e uma turma num determinado período letivo.

    Criada automaticamente pelo processamento batch quando a solicitação é aprovada,
    ou de forma imediata no caso de matrícula extraordinária (§7.5).
    """
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o aluno matriculado
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)

    # FK para a turma em que o aluno está matriculado
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)

    # FK para o período letivo da matrícula
    periodo_letivo_id = Column(Integer, ForeignKey("periodos_letivos.id"), nullable=False)

    # Estado atual da matrícula (ATIVA, CANCELADA, TRANCADA)
    status = Column(SAEnum(StatusMatricula), default=StatusMatricula.ATIVA, nullable=False)

    # Origem indica como a matrícula foi criada (rastreabilidade do processo)
    origem = Column(String(30), nullable=False, default="FASE_3")

    # Data em que a matrícula foi efetivamente registrada no sistema
    data_efetivacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relacionamentos ORM ---
    aluno = relationship("Aluno")
    turma = relationship("Turma")
    periodo_letivo = relationship("PeriodoLetivo")


class AuditoriaProcessamento(Base):
    """
    Entidade de auditoria que registra cada decisão tomada durante o processamento
    batch de matrículas (§6.12).

    Cada registro representa uma regra avaliada para um par (aluno, turma), com a
    decisão resultante e a mensagem explicativa. Isso permite ao coordenador rastrear
    exatamente por que uma solicitação foi aprovada ou rejeitada.
    """
    __tablename__ = "auditoria_processamento"

    id = Column(Integer, primary_key=True, index=True)

    # FK para o aluno avaliado
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)

    # FK para a turma avaliada
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)

    # Fase em que a auditoria ocorreu (ex: FASE_3, FASE_5)
    fase = Column(String(30), nullable=False)

    # Identificador da regra que foi aplicada (ex: R1_ELEGIBILIDADE, R2_ORDENACAO, R3_CREDITOS)
    regra_aplicada = Column(String(50), nullable=False)

    # Resultado da aplicação da regra
    decisao = Column(String(20), nullable=False)  # "APROVADO" ou "REJEITADO"

    # Mensagem descritiva da decisão para rastreabilidade
    mensagem = Column(String(500), nullable=False)

    # Timestamp automático para trilha de auditoria cronológica
    timestamp_evento = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # --- Relacionamentos ORM ---
    aluno = relationship("Aluno")
    turma = relationship("Turma")
