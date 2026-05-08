"""
Módulo de Schemas (DTOs) de Unidades Organizacionais

Define os modelos Pydantic para entrada e saída da entidade UnidadeOrganizacional.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional


class UnidadeOrganizacionalBase(BaseModel):
    """Atributos compartilhados entre criação e resposta de Unidade Organizacional."""
    codigo: str = Field(..., max_length=20, description="Código da unidade (Ex: CIC, MAT, EST)")
    nome: str = Field(..., max_length=150, description="Nome completo (Ex: Departamento de Ciência da Computação)")
    ativo: bool = Field(default=True, description="Indica se a unidade está ativa")


class UnidadeOrganizacionalCreate(UnidadeOrganizacionalBase):
    """Schema para criação de uma nova unidade organizacional."""
    pass


class UnidadeOrganizacionalResponse(UnidadeOrganizacionalBase):
    """Schema de resposta, incluindo o ID gerado pelo banco."""
    id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
