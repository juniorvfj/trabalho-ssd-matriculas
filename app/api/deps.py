"""
Módulo de Dependências de Autenticação (API)

Este arquivo define dependências (Dependencies) do FastAPI que serão injetadas
nos roteadores. A principal dependência aqui verifica a validade do token JWT 
enviado no cabeçalho Authorization das requisições HTTP.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.config import settings
from app.core.database import get_db
from app.modules.usuarios.application.services import UsuarioService
from app.modules.usuarios.infrastructure.orm_models import Usuario, RoleEnum

# OAuth2PasswordBearer extrai automaticamente o token do header 'Authorization: Bearer <token>'
# O parâmetro tokenUrl avisa ao Swagger UI para onde enviar o login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Função de Injeção de Dependência que protege as rotas.
    Qualquer rota que precise de autenticação receberá o retorno desta função.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Tenta decodificar o token com a mesma chave e algoritmo que geraram
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # Se expirar ou a assinatura estiver incorreta, a lib `jose` lança erro
        raise credentials_exception
    
    # Buscar o usuário real no banco de dados
    usuario_service = UsuarioService(db)
    user = await usuario_service.get_by_username(username=username)
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

class RoleChecker:
    """
    Dependência de validação RBAC.
    Garante que o usuário atual possua um dos papéis (roles) permitidos.
    """
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Usuario = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operação não permitida para o seu perfil"
            )
        return user
