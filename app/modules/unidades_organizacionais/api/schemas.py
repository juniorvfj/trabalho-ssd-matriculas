"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Unidade Organizacional — modelo SIGAA (SIGAA_UNIDADE).

A unidade usa o código natural de 3 caracteres como identificador (ex.: 'CIC').
"""
from pydantic import BaseModel, ConfigDict, Field


class UnidadeOrganizacionalCreate(BaseModel):
    """Schema para criação de uma unidade organizacional (SIGAA_UNIDADE)."""
    id: str = Field(..., max_length=3, description="Código da unidade (ex.: 'CIC')")
    nome: str = Field(..., max_length=100, description="Nome da unidade (ex.: 'DEPARTAMENTO DE CIÊNCIA DA COMPUTAÇÃO')")


class UnidadeOrganizacionalResponse(BaseModel):
    """Schema de resposta da unidade organizacional."""
    id: str
    nome: str

    model_config = ConfigDict(from_attributes=True)
