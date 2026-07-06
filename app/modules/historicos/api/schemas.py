"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Histórico Acadêmico — modelo SIGAA.

No SIGAA o histórico do aluno é o conjunto de linhas de SIGAA_RL_ALUNO_CURSO_DISCIPLINA
(disciplina cursada por um vínculo aluno-curso, com a menção obtida). Não há uma
entidade "histórico consolidado".
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HistoricoDisciplinaCreate(BaseModel):
    """Schema para lançar uma disciplina cursada no histórico de um vínculo aluno-curso."""
    aluno_curso: int = Field(..., description="ID do vínculo aluno-curso (SIGAA_RL_ALUNO_CURSO.id)")
    disciplina: str = Field(..., max_length=7, description="Código da disciplina cursada")
    periodo_letivo: str = Field(..., max_length=5, description="Período letivo (ex.: '20182')")
    mencao: Optional[str] = Field(None, max_length=2, description="Menção obtida (ex.: 'SS', 'MM', 'SR')")


class HistoricoDisciplinaResponse(BaseModel):
    """Schema de resposta de um item do histórico."""
    aluno_curso: int
    disciplina: str
    periodo_letivo: str
    mencao: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
