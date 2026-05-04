from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CargaHorariaSchema(BaseModel):
    total_minima: int = Field(0, description="Carga horária total mínima")
    obrigatoria_aula: int = Field(0)
    obrigatoria_orientacao: int = Field(0)
    obrigatoria_total: int = Field(0)
    optativa_minima: int = Field(0)
    maxima_eletivos: int = Field(0)
    maxima_periodo: int = Field(0)
    minima_periodo: int = Field(0)

class PrazoSchema(BaseModel):
    minimo: int = Field(0, description="Prazo mínimo em semestres")
    medio: int = Field(0)
    maximo: int = Field(0)

class CurriculoBase(BaseModel):
    codigo: str = Field(..., max_length=50, description="Código do currículo")
    status: str = Field("ativo", pattern="^(ativo|inativo)$")
    data_validade: Optional[date] = None
    curso_id: int
    periodo_letivo_vigor_id: int
    
    carga_horaria: CargaHorariaSchema
    prazo: PrazoSchema

class CurriculoCreate(CurriculoBase):
    pass

class CurriculoUpdate(BaseModel):
    codigo: Optional[str] = None
    status: Optional[str] = None
    data_validade: Optional[date] = None
    carga_horaria: Optional[CargaHorariaSchema] = None
    prazo: Optional[PrazoSchema] = None

class CurriculoResponse(CurriculoBase):
    id: int

    class Config:
        from_attributes = True

# Schemas para a tabela associativa (Componentes / Disciplinas do Currículo)
class CurriculoDisciplinaBase(BaseModel):
    disciplina_id: int
    tipo: str = Field(..., description="Obrigatória, Optativa, etc.")
    nivel: int = Field(..., description="Semestre ou nível recomendado")

class CurriculoDisciplinaCreate(CurriculoDisciplinaBase):
    pass

class CurriculoDisciplinaResponse(CurriculoDisciplinaBase):
    id: int
    curriculo_id: int

    class Config:
        from_attributes = True
