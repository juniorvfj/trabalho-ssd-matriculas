"""
Módulo de Schemas (DTOs) de Cursos

Responsável pela definição das estruturas de dados de entrada e saída esperadas pela API
referentes à entidade Curso. A validação destes dados pelo Pydantic ocorre antes que a lógica 
da aplicação seja acionada, protegendo contra inputs malformados.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional

class CursoBase(BaseModel):
    """Atributos em comum compartilhados por todas as operações envolvendo Curso."""
    codigo: str = Field(..., max_length=10, description="Código da instituição para o curso (Ex: CC01)")
    nome: str = Field(..., max_length=100, description="Nome completo do curso")
    turno: Optional[str] = Field(None, max_length=50, description="Turno do curso (Ex: Diurno, Noturno, Integral)")
    grau: Optional[str] = Field(None, max_length=50, description="Grau acadêmico (Ex: Bacharelado, Licenciatura)")
    modalidade: Optional[str] = Field(None, max_length=50, description="Modalidade de ensino (Ex: Presencial, EAD)")
    sede: Optional[str] = Field(None, max_length=100, description="Campus ou sede (Ex: Campus Darcy Ribeiro)")
    coordenador_id: Optional[int] = Field(None, gt=0, description="ID do docente coordenador do curso")
    unidade_organizacional_id: Optional[int] = Field(None, gt=0, description="ID da unidade organizacional (departamento/instituto)")
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
