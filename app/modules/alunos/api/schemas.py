from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import date
from pydantic.alias_generators import to_snake

class AlunoBase(BaseModel):
    matricula: str = Field(..., pattern=r"^[0-9]{9}$", description="Número de matrícula universitária (9 caracteres)")
    nome: str = Field(..., max_length=150, description="Nome completo do aluno")
    email: EmailStr = Field(..., description="E-mail institucional do aluno")
    data_admissao: date = Field(..., description="Data de ingresso no curso (YYYY-MM-DD)")
    ira: float = Field(default=0.0, ge=0.0, le=5.0, description="Índice de Rendimento Acadêmico (0.0 a 5.0)")
    limite_creditos_periodo: int = Field(default=32, ge=1, le=40, description="Máximo de créditos por período")
    curso_id: int = Field(..., gt=0, description="ID do curso o qual o aluno está associado")
    ativo: bool = Field(default=True, description="Sinaliza matrícula ativa")

class AlunoCreate(AlunoBase):
    pass

class AlunoUpdate(AlunoBase):
    pass

class AlunoResponse(AlunoBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
