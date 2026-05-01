"""
Módulo de Rotas de Autenticação (API)

Expõe o endpoint de Login para geração do Token JWT que autenticará 
as demais chamadas da API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.core.database import get_db
from app.modules.usuarios.application.services import UsuarioService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

auth_router = APIRouter()

class Token(BaseModel):
    """Schema de resposta esperado pelo protocolo OAuth2 quando o token é emitido."""
    access_token: str
    token_type: str
    role: str

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de autenticação utilizando banco de dados e bcrypt.
    """
    usuario_service = UsuarioService(db)
    user = await usuario_service.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário, senha incorretos ou inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # A autenticação obteve sucesso. Incluímos o id do usuário no token
    # e retornamos a role
    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.value
    }
