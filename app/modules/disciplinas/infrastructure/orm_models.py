"""
Módulo de Modelos ORM (Infrastructure Layer) para Disciplinas

Define a tabela de disciplinas e a tabela de associação para resolver o relacionamento
muitos-para-muitos (M:N) dos pré-requisitos entre as próprias disciplinas.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ModalidadeDisciplina(str, enum.Enum):
    """Enum que representa as modalidades possíveis de uma disciplina."""
    PRESENCIAL = "Presencial"
    EAD = "EAD"
    HIBRIDA = "Híbrida"

class Disciplina(Base):
    """Entidade que mapeia a tabela de disciplinas."""
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    nome = Column(String(150), nullable=False)
    modalidade = Column(SAEnum(ModalidadeDisciplina), nullable=True)  # Presencial, EAD, Híbrida
    creditos = Column(Integer, nullable=False)
    carga_horaria = Column(Integer, nullable=False)   # cargaHorariaTotal no diagrama

    # Detalhamento da carga horária (CargaHoraria no diagrama)
    carga_horaria_teorica = Column(Integer, default=0, nullable=False)
    carga_horaria_pratica = Column(Integer, default=0, nullable=False)
    carga_horaria_extensionista = Column(Integer, default=0, nullable=False)

    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)

    # FK para a unidade organizacional (departamento responsável) — diagrama: 0..1
    unidade_organizacional_id = Column(Integer, ForeignKey("unidades_organizacionais.id"), nullable=True)

    ativa = Column(Boolean, default=True, nullable=False)

    # Relacionamento simples com Curso
    curso = relationship("Curso")

    # Relacionamento com a unidade organizacional
    unidade_organizacional = relationship("app.modules.unidades_organizacionais.infrastructure.orm_models.UnidadeOrganizacional", back_populates="disciplinas")
    
    # Relacionamento com a tabela associativa de pré-requisitos
    prerequisitos = relationship(
        "DisciplinaPrerequisito",
        foreign_keys="[DisciplinaPrerequisito.disciplina_id]",
        back_populates="disciplina"
    )

class DisciplinaPrerequisito(Base):
    """
    Tabela Associativa (Join Table) para mapear quais disciplinas são pré-requisitos de outras.
    Resolve o relacionamento M:N onde uma Disciplina A requer que a Disciplina B tenha sido cursada.
    """
    __tablename__ = "disciplinas_prerequisitos"

    id = Column(Integer, primary_key=True, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    prerequisito_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    disciplina = relationship("Disciplina", foreign_keys=[disciplina_id], back_populates="prerequisitos")
    
    # Disciplina que deve ser concluída antes da 'disciplina'
    prerequisito = relationship("Disciplina", foreign_keys=[prerequisito_id])
