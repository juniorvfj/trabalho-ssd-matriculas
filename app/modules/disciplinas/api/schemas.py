"""
Módulo de Schemas (DTOs) de Disciplinas

Responsável pela definição das estruturas de dados (Pydantic) de entrada e saída esperadas pela API
referentes à entidade Disciplina e aos seus Pré-requisitos.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import List, Optional

class DisciplinaPrerequisitoBase(BaseModel):
    """Schema para validação do vínculo de pré-requisito entre duas disciplinas."""
    prerequisito_id: int = Field(..., description="ID da disciplina que é pré-requisito")

class DisciplinaPrerequisitoResponse(DisciplinaPrerequisitoBase):
    id: int
    disciplina_id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)

class DisciplinaBase(BaseModel):
    """Atributos em comum compartilhados por operações envolvendo Disciplina."""
    codigo: str = Field(..., max_length=20, description="Código da disciplina (Ex: CIC0001)")
    nome: str = Field(..., max_length=150, description="Nome da disciplina")
    creditos: int = Field(..., gt=0, description="Quantidade de créditos")
    carga_horaria: int = Field(..., gt=0, description="Carga horária total da disciplina")
    curso_id: int = Field(..., description="ID do curso ao qual a disciplina pertence")
    ativa: bool = Field(default=True, description="Indica se a disciplina está ativa")

class DisciplinaCreate(DisciplinaBase):
    """Schema para a criação de uma Disciplina."""
    pass

class DisciplinaUpdate(DisciplinaBase):
    """Schema para atualização de uma Disciplina."""
    pass

class DisciplinaResponse(DisciplinaBase):
    """Schema de resposta, contendo o ID auto-gerado."""
    id: int
    
    # Habilita suporte ao SQLAlchemy no retorno
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
