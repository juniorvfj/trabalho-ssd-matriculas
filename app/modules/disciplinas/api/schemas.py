"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Disciplina — modelo SIGAA (SIGAA_DISCIPLINA).

A disciplina usa o código natural de 7 caracteres como identificador (ex.: 'CIC0007')
e pertence a uma unidade organizacional. A carga horária é informada em duas parcelas
(teórica e prática), como no schema SIGAA.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DisciplinaCreate(BaseModel):
    """Schema para criação de uma disciplina (SIGAA_DISCIPLINA)."""
    id: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")
    nome: Optional[str] = Field(None, max_length=100, description="Nome da disciplina")
    modalidade: Optional[str] = Field(None, max_length=50, description="Modalidade")
    carga_horaria_teorica: Optional[int] = Field(None, ge=0, description="Carga horária teórica")
    carga_horaria_pratica: Optional[int] = Field(None, ge=0, description="Carga horária prática")
    unidade: str = Field(..., max_length=3, description="Código da unidade organizacional responsável (ex.: 'CIC')")


class DisciplinaResponse(BaseModel):
    """Schema de resposta da disciplina."""
    id: str
    nome: Optional[str] = None
    modalidade: Optional[str] = None
    carga_horaria_teorica: Optional[int] = None
    carga_horaria_pratica: Optional[int] = None
    unidade: str

    model_config = ConfigDict(from_attributes=True)


class PrerequisitoCreate(BaseModel):
    """Schema para vincular um pré-requisito (SIGAA_PREREQ)."""
    disciplina_requerido: str = Field(..., max_length=7, description="Código da disciplina exigida como pré-requisito")
