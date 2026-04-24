"""
Módulo de Schemas (DTOs) de Histórico Acadêmico

Define os modelos Pydantic para entrada (criação) e saída (resposta) de registros
do histórico acadêmico de um aluno. O campo 'status' é validado pelo Enum
StatusHistorico, impedindo que valores inválidos sejam aceitos pela API.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional
from enum import Enum


class StatusHistoricoEnum(str, Enum):
    """Enum espelhado no Pydantic para validação de entrada na API."""
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    TRANCADO = "TRANCADO"
    CURSANDO = "CURSANDO"


class HistoricoAcademicoBase(BaseModel):
    """Atributos compartilhados entre criação e resposta de Histórico."""
    aluno_id: int = Field(..., description="ID do aluno")
    disciplina_id: int = Field(..., description="ID da disciplina cursada")
    periodo_letivo_id: int = Field(..., description="ID do período letivo")
    status: StatusHistoricoEnum = Field(..., description="Status na disciplina (APROVADO, REPROVADO, TRANCADO, CURSANDO)")
    nota_final: Optional[float] = Field(None, ge=0.0, le=10.0, description="Nota final obtida (0.0 a 10.0)")
    aprovado: bool = Field(default=False, description="Indica se o aluno foi aprovado")


class HistoricoAcademicoCreate(HistoricoAcademicoBase):
    """Schema para criação de um registro no histórico acadêmico."""
    pass


class HistoricoAcademicoResponse(HistoricoAcademicoBase):
    """Schema de resposta, incluindo o ID gerado pelo banco."""
    id: int

    # Habilita a conversão automática de objetos SQLAlchemy para Pydantic
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
