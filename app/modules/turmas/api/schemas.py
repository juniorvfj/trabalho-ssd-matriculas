from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from datetime import date
from typing import List, Optional

class PeriodoLetivoBase(BaseModel):
    codigo: str = Field(..., max_length=20, description="Código do período (Ex: 2026.1)")
    descricao: str = Field(..., max_length=150, description="Descrição do período")
    data_inicio: date = Field(..., description="Data de início do período letivo")
    data_fim: date = Field(..., description="Data de fim do período letivo")
    ativo: bool = Field(default=True, description="Indica se o período está ativo")

class PeriodoLetivoCreate(PeriodoLetivoBase):
    pass

class PeriodoLetivoResponse(PeriodoLetivoBase):
    id: int
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)

class TurmaBase(BaseModel):
    disciplina_id: int = Field(..., description="ID da disciplina")
    periodo_letivo_id: int = Field(..., description="ID do período letivo")
    codigo_turma: str = Field(..., max_length=10, description="Código da turma (Ex: A, T01)")
    vagas_totais: int = Field(..., gt=0, description="Total de vagas oferecidas")
    horario_serializado: str = Field(..., max_length=200, description="Horário no formato acadêmico (Ex: 24M34)")
    ativa: bool = Field(default=True, description="Indica se a turma está ativa")

class TurmaCreate(TurmaBase):
    pass

class TurmaResponse(TurmaBase):
    id: int
    vagas_ocupadas: int
    
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
