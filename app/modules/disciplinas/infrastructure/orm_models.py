"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Disciplina

Mapeia as tabelas SIGAA_DISCIPLINA e SIGAA_PREREQ do modelo de dados do professor.
A disciplina usa como PK o código natural de 7 caracteres (ex.: 'CIC0007') e
pertence a uma unidade organizacional (SIGAA_UNIDADE). Os pré-requisitos são
modelados por SIGAA_PREREQ, com PK composta (disciplina_requer, disciplina_requerido).
"""
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Disciplina(Base):
    """Entidade que mapeia a tabela SIGAA_DISCIPLINA."""
    __tablename__ = "sigaa_disciplina"

    # Código natural da disciplina (PK) — ex.: 'CIC0007'
    id = Column(String(7), primary_key=True)
    nome = Column(String(100), nullable=True)
    modalidade = Column(String(50), nullable=True)
    carga_horaria_teorica = Column(Numeric(3, 0), nullable=True)
    carga_horaria_pratica = Column(Numeric(3, 0), nullable=True)
    # Carga horária total da disciplina (coluna de exemplo — acréscimo pós-baseline).
    # Nullable para não conflitar com o DML do professor (que não a informa).
    carga_horaria = Column(Numeric(4, 0), nullable=True)

    # FK para a unidade organizacional responsável (SIGAA_UNIDADE)
    unidade = Column(String(3), ForeignKey("sigaa_unidade.id"), nullable=False)

    # --- Relacionamentos ORM ---
    unidade_organizacional = relationship("UnidadeOrganizacional", back_populates="disciplinas")

    # Pré-requisitos exigidos por esta disciplina (lado 'requer')
    prerequisitos = relationship(
        "DisciplinaPrerequisito",
        foreign_keys="[DisciplinaPrerequisito.disciplina_requer]",
        back_populates="disciplina",
    )


class DisciplinaPrerequisito(Base):
    """
    Tabela associativa SIGAA_PREREQ: mapeia quais disciplinas são pré-requisito
    de outras. 'disciplina_requer' é a disciplina que exige; 'disciplina_requerido'
    é a que precisa ter sido cursada antes.
    """
    __tablename__ = "sigaa_prereq"

    disciplina_requer = Column(String(7), ForeignKey("sigaa_disciplina.id"), primary_key=True)
    disciplina_requerido = Column(String(7), ForeignKey("sigaa_disciplina.id"), primary_key=True)

    disciplina = relationship("Disciplina", foreign_keys=[disciplina_requer], back_populates="prerequisitos")
    requerido = relationship("Disciplina", foreign_keys=[disciplina_requerido])
