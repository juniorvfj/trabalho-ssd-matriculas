"""
Módulo de Configuração (Core)

Este arquivo é responsável por gerenciar todas as variáveis de ambiente e configurações
globais da aplicação utilizando o `pydantic_settings`.
A vantagem de usar o Pydantic para configurações é a tipagem forte e a validação
automática de dados no momento em que a aplicação é iniciada.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe que define o esquema de configurações.
    Os valores padrão aqui podem ser sobrescritos por um arquivo `.env` na raiz do projeto.
    """
    PROJECT_NAME: str = "SSD Vicente - Matrícula"
    API_V1_STR: str = "/api/v1"
    
    # Chave secreta usada para criptografia e geração de JWTs. Em produção, NUNCA usar valores fixos.
    SECRET_KEY: str = "supersecretkey-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENVIRONMENT: str = "development"
    
    # URL de conexão com o banco de dados. Usamos 'asyncpg' pois o SQLAlchemy está configurado para ser assíncrono.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/matricula_db"

    # Configuração que orienta o Pydantic a buscar os valores no arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instância única (Singleton) de configuração que será importada em toda a aplicação.
settings = Settings()
