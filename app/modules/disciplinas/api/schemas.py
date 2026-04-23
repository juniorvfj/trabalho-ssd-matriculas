from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import List, Optional

class DisciplinaPrerequisitoBase(BaseModel):
    prerequisito_id: int = Field(..., description="ID da disciplina que é pré-requisito")

class DisciplinaPrerequisitoResponse(DisciplinaPrerequisitoBase):
    id: int
    disciplina_id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)

class DisciplinaBase(BaseModel):
    codigo: str = Field(..., max_length=20, description="Código da disciplina (Ex: CIC0001)")
    nome: str = Field(..., max_length=150, description="Nome da disciplina")
    creditos: int = Field(..., gt=0, description="Quantidade de créditos")
    carga_horaria: int = Field(..., gt=0, description="Carga horária total da disciplina")
    curso_id: int = Field(..., description="ID do curso ao qual a disciplina pertence")
    ativa: bool = Field(default=True, description="Indica se a disciplina está ativa")

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaUpdate(DisciplinaBase):
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
