"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Turma e Horário de Aula — modelo SIGAA.

No SIGAA o período letivo é um 'character varying(5)' inline (ex.: '20182'), não
uma entidade; por isso não há mais schemas de PeriodoLetivo. O horário de aula é
normalizado em SIGAA_TURMA_HORARIOAULA.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TurmaCreate(BaseModel):
    """Schema para criação de uma turma (SIGAA_TURMA)."""
    codigo: str = Field(..., max_length=2, description="Código da turma (ex.: '01')")
    periodo_letivo: str = Field(..., max_length=5, description="Período letivo (ex.: '20182')")
    disciplina: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")
    vagas: Optional[int] = Field(None, ge=0, description="Quantidade de vagas")
    sede: Optional[str] = Field(None, max_length=50, description="Sede/campus")


class TurmaResponse(BaseModel):
    """Schema de resposta da turma."""
    id: int
    codigo: str
    periodo_letivo: str
    disciplina: str
    vagas: Optional[int] = None
    sede: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HorarioAulaCreate(BaseModel):
    """Schema para criação de um slot de horário (SIGAA_TURMA_HORARIOAULA)."""
    id: str = Field(..., max_length=3, description="Código do slot (ex.: '208')")
    dia: str = Field(..., max_length=3, description="Dia (SEG, TER, ...)")
    hora_inicio: str = Field(..., max_length=5, description="Hora de início (ex.: '08:00')")
    hora_fim: str = Field(..., max_length=5, description="Hora de fim (ex.: '09:50')")


class HorarioAulaResponse(HorarioAulaCreate):
    """Schema de resposta de um slot de horário."""
    model_config = ConfigDict(from_attributes=True)
