"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Aluno — modelo SIGAA (SIGAA_ALUNO + SIGAA_RL_ALUNO_CURSO).

O aluno tem como identificador a matrícula (9 dígitos). Os dados acadêmicos do
vínculo (curso, currículo, IRA, período de ingresso) vêm de SIGAA_RL_ALUNO_CURSO.
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlunoCreate(BaseModel):
    """
    Schema para criação de um aluno já com seu vínculo de curso.
    Cria uma linha em SIGAA_ALUNO e outra em SIGAA_RL_ALUNO_CURSO.
    """
    matricula: str = Field(..., pattern=r"^[0-9]{9}$", description="Matrícula (9 dígitos)")
    nome: str = Field(..., max_length=80, description="Nome do aluno")
    curso: str = Field(..., max_length=4, description="Código do curso (ex.: '6351')")
    curriculo: str = Field(..., max_length=7, description="Código do currículo (ex.: '6351/2')")
    data_registro: date = Field(..., description="Data de registro no curso (YYYY-MM-DD)")
    periodo_letivo_registro: str = Field(..., max_length=5, description="Período de ingresso (ex.: '20182')")
    status: Optional[str] = Field("A", max_length=1, description="Status do vínculo (ex.: 'A')")
    ira: Optional[float] = Field(None, ge=0.0, le=5.0, description="Índice de Rendimento Acadêmico")


class AlunoResponse(BaseModel):
    """Schema de resposta resumida do aluno."""
    matricula: str
    nome: str

    model_config = ConfigDict(from_attributes=True)
