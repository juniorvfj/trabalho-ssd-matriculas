"""
Módulo de Segurança (Core)

Contém as rotinas utilitárias para lidar com segurança: geração de hashes de senhas, 
verificação de senhas e criação do JSON Web Token (JWT).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
import bcrypt
from app.core.config import settings

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Gera um novo JSON Web Token (JWT) assinado digitalmente.
    
    :param subject: O assunto (sub) do token, geralmente o identificador único do usuário (ex: matrícula).
    :param expires_delta: Tempo de vida opcional do token.
    :return: A string contendo o JWT codificado.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload do token contendo a data de expiração (exp) e o usuário (sub)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Assinatura do JWT com a chave simétrica SECRET_KEY (algoritmo HS256)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano (digitada pelo usuário) corresponde ao hash armazenado no banco."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Gera o hash da senha em texto plano para ser guardado no banco de dados com segurança."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
