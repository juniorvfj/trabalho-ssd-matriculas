"""
Módulo de Dependências de Autenticação (API)

Este arquivo define dependências (Dependencies) do FastAPI que serão injetadas
nos roteadores. A principal dependência aqui verifica a validade do token JWT 
enviado no cabeçalho Authorization das requisições HTTP.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from pydantic import BaseModel

# OAuth2PasswordBearer extrai automaticamente o token do header 'Authorization: Bearer <token>'
# O parâmetro tokenUrl avisa ao Swagger UI para onde enviar o login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class TokenData(BaseModel):
    """Schema para os dados extraídos de dentro do JWT."""
    username: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Função de Injeção de Dependência que protege as rotas.
    Qualquer rota que precise de autenticação receberá o retorno desta função.
    
    O fluxo é:
    1. O cliente manda a requisição.
    2. O FastAPI executa o `oauth2_scheme` para extrair a string do token.
    3. Esta função tenta decodificar e validar a assinatura do token.
    4. Se inválido, lança 401 Unauthorized. Se válido, deixa a rota prosseguir.
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
        token_data = TokenData(username=username)
    except JWTError:
        # Se expirar ou a assinatura estiver incorreta, a lib `jose` lança erro
        raise credentials_exception
    
    # Retorna os dados provisórios. Futuramente isso buscará no Banco o Model Usuario real.
    return token_data
