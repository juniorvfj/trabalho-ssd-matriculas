"""
Módulo de Schemas (DTOs) de Docentes

Define os modelos Pydantic para entrada e saída da entidade Docente
e da tabela associativa TurmaDocente.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional, List


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de Docente
# ═══════════════════════════════════════════════════════════════════════════════

class DocenteBase(BaseModel):
    """Atributos compartilhados entre criação e resposta de Docente."""
    matricula: str = Field(..., max_length=20, description="Matrícula funcional do docente")
    nome: str = Field(..., max_length=150, description="Nome completo do docente")
    ativo: bool = Field(default=True, description="Indica se o docente está ativo")


class DocenteCreate(DocenteBase):
    """Schema para criação de um novo docente."""
    pass


class DocenteResponse(DocenteBase):
    """Schema de resposta, incluindo o ID gerado pelo banco."""
    id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de TurmaDocente (vinculação de docente a turma)
# ═══════════════════════════════════════════════════════════════════════════════

class TurmaDocenteBase(BaseModel):
    """Atributos para vincular um docente a uma turma."""
    turma_id: int = Field(..., gt=0, description="ID da turma")
    docente_id: int = Field(..., gt=0, description="ID do docente")


class TurmaDocenteCreate(TurmaDocenteBase):
    """Schema para vincular um docente a uma turma."""
    pass


class TurmaDocenteResponse(TurmaDocenteBase):
    """Schema de resposta da vinculação docente-turma."""
    id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
