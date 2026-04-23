from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake

class CursoBase(BaseModel):
    codigo: str = Field(..., max_length=10, description="Código da instituição para o curso (Ex: CC01)")
    nome: str = Field(..., max_length=100, description="Nome completo do curso")
    ativo: bool = Field(default=True, description="Indica se o curso ainda aceita ingresso de alunos")

class CursoCreate(CursoBase):
    pass

class CursoUpdate(CursoBase):
    pass

class CursoResponse(CursoBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
