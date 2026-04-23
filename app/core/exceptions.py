"""
Módulo de Exceções Globais (Core)

Implementa a padronização das respostas de erro (Modelo Canônico de Erro).
Em sistemas distribuídos, padronizar as mensagens de erro ajuda os clientes (frontend, outras APIs)
a entenderem e tratarem as falhas de forma previsível e unificada.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Dict

class BaseAPIException(Exception):
    """
    Classe base para todas as exceções personalizadas da nossa aplicação.
    Permite definir uma mensagem, um código interno (ex: ALUNO_NOT_FOUND) e o status HTTP.
    """
    def __init__(self, message: str, code: str, details: Dict[str, Any] = None, status_code: int = 400):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

def api_exception_handler(request: Request, exc: BaseAPIException):
    """
    Handler para exceções de regra de negócio. Intercepta qualquer BaseAPIException
    levantada no código e a transforma em um JSONResponse padronizado.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )

def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para exceções de validação estrutural do FastAPI/Pydantic.
    Se o cliente envia um JSON malformado (ex: string no lugar de int), 
    o FastAPI gera um RequestValidationError, que nós interceptamos e formatamos.
    """
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Erro de validação nos dados enviados.",
            "details": exc.errors()
        }
    )
