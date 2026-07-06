"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Curso — modelo SIGAA (SIGAA_CURSO).

O curso usa o código natural de 4 caracteres como identificador (ex.: '6351').
No SIGAA o coordenador é apenas o nome do docente (não há entidade Docente).
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CursoCreate(BaseModel):
    """Schema para criação de um curso (SIGAA_CURSO)."""
    id: str = Field(..., max_length=4, description="Código do curso (ex.: '6351')")
    nome: str = Field(..., max_length=100, description="Nome do curso")
    grau_academico: str = Field(..., max_length=15, description="Grau acadêmico (ex.: 'BACHAREL')")
    turno: str = Field(..., max_length=10, description="Turno (ex.: 'DIURNO')")
    modalidade: str = Field(..., max_length=25, description="Modalidade (ex.: 'PRESENCIAL')")
    coordenador: Optional[str] = Field(None, max_length=100, description="Nome do coordenador")


class CursoResponse(BaseModel):
    """Schema de resposta detalhada do curso."""
    id: str
    nome: str
    grau_academico: Optional[str] = None
    turno: Optional[str] = None
    modalidade: Optional[str] = None
    coordenador: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
