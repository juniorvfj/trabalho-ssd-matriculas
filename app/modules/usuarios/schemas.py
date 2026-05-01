from pydantic import BaseModel, Field
from typing import Optional
from app.modules.usuarios.infrastructure.orm_models import RoleEnum

class UsuarioBase(BaseModel):
    username: str = Field(..., description="Nome de usuário para login")
    role: RoleEnum = Field(..., description="Papel (role) de autorização do usuário")
    is_active: bool = Field(True, description="Indica se a conta está ativa")

class UsuarioCreate(UsuarioBase):
    id: str = Field(..., description="Identificador único (geralmente matrícula para alunos)")
    password: str = Field(..., description="Senha em texto plano (será feito o hash)")

class UsuarioUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: str
    
    class Config:
        from_attributes = True
