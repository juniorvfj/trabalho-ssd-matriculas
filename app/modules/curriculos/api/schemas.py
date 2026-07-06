"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Currículo (Estrutura Curricular) — modelo SIGAA.

O currículo usa código natural de 7 caracteres (ex.: '6351/2'). As cargas horárias
e a quantidade de períodos seguem exatamente as colunas de SIGAA_CURRICULO.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CurriculoCreate(BaseModel):
    """Schema para criação de um currículo (SIGAA_CURRICULO)."""
    id: str = Field(..., max_length=7, description="Código do currículo (ex.: '6351/2')")
    status: Optional[str] = Field("A", max_length=1, description="Status (ex.: 'A')")
    periodo_letivo_vigor: str = Field(..., max_length=5, description="Período de vigor (ex.: '20182')")
    carga_horaria_minima_total: int = Field(..., ge=0)
    carga_horaria_minima_opt: int = Field(..., ge=0)
    carga_horaria_obr: int = Field(..., ge=0)
    carga_horaria_eletiva_max: int = Field(..., ge=0)
    carga_horaria_max_periodo: int = Field(..., ge=0)
    num_periodos: int = Field(..., ge=0)
    min_periodos: int = Field(..., ge=0)
    max_periodos: int = Field(..., ge=0)
    curso: Optional[str] = Field(None, max_length=4, description="Curso a vincular (SIGAA_RL_CURRICULO_CURSO)")


class CurriculoResponse(BaseModel):
    """Schema de resposta do currículo."""
    id: str
    status: Optional[str] = None
    periodo_letivo_vigor: str

    model_config = ConfigDict(from_attributes=True)


class CurriculoDisciplinaCreate(BaseModel):
    """Schema para vincular uma disciplina ao currículo (SIGAA_RL_CURRICULO_DISCIPLINA)."""
    disciplina: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")
    periodo: Optional[int] = Field(None, ge=0, description="Nível/semestre sugerido")
    tipo: str = Field(..., max_length=15, description="'OBR' (obrigatória) ou 'OPT' (optativa)")
