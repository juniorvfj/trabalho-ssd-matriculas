"""
Módulo de Schemas (DTOs) de Cursos

Responsável pela definição das estruturas de dados de entrada e saída esperadas pela API
referentes à entidade Curso. A validação destes dados pelo Pydantic ocorre antes que a lógica 
da aplicação seja acionada, protegendo contra inputs malformados.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake

class CursoBase(BaseModel):
    """Atributos em comum compartilhados por todas as operações envolvendo Curso."""
    codigo: str = Field(..., max_length=10, description="Código da instituição para o curso (Ex: CC01)")
    nome: str = Field(..., max_length=100, description="Nome completo do curso")
    ativo: bool = Field(default=True, description="Indica se o curso ainda aceita ingresso de alunos")

class CursoCreate(CursoBase):
    """Schema para a rota POST (Criação de Curso)."""
    pass

class CursoUpdate(CursoBase):
    """Schema para a rota PUT/PATCH (Atualização de Curso)."""
    pass

class CursoResponse(CursoBase):
    """Schema para retornar os dados formatados do Curso nas requisições."""
    id: int
    
    # Permite mapeamento direto das instâncias do SQLAlchemy
    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
