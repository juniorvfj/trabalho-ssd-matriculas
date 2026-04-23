"""
Módulo de Rotas de Autenticação (API)

Expõe o endpoint de Login para geração do Token JWT que autenticará 
as demais chamadas da API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from pydantic import BaseModel

auth_router = APIRouter()

class Token(BaseModel):
    """Schema de resposta esperado pelo protocolo OAuth2 quando o token é emitido."""
    access_token: str
    token_type: str

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint (Rota) de autenticação provisória.
    
    O FastAPI preenche automaticamente o `form_data` a partir de um envio do tipo
    'application/x-www-form-urlencoded' (padrão do OAuth2).
    
    Atualmente, aceita qualquer nome de usuário desde que a senha seja 'admin'.
    Na implementação real, isso consultaria o banco de dados e faria verificação de Hash.
    """
    if form_data.password != "admin":
        # Retorna o erro padronizado para credencial incorreta (HTTP 401)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta. Use 'admin'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # A autenticação obteve sucesso. Geramos o Token usando a função auxiliar de segurança.
    access_token = create_access_token(subject=form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}
