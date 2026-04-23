# Dependências e Fundamentos Tecnológicos

Este documento foi gerado durante a inicialização do repositório para justificar as tecnologias adotadas para atender aos requisitos de Segurança em Sistemas Distribuídos e Monólito Modular, usando Python 3.12.

## Tecnologias Base

### FastAPI
- **Por que?** Excelente suporte e aderência nativa a contratos OpenAPI e "Contract-First", permitindo modelar `Request`/`Response` robustos. Exibe documentação interativa nativamente e tem ótima performance por ser assíncrono.
- **Versão:** `^0.111.0`

### Pydantic (v2) e Pydantic-Settings
- **Por que?** A validação forte de dados suporta perfeitamente a elaboração de Modelos Canônicos. Usado para criar Data Transfer Objects (DTOs) que servirão de esquema padrão para respostas e validações de erro (`Schema` First).
- **Versão:** `^2.7.4`

### SQLAlchemy (2.x) e Alembic
- **Por que?** ORM e Gestor de Migrações necessários para interagir com o PostgreSQL e aplicar uma persistência consistente de dados e controle das tabelas de domínio. O uso de `asyncpg` permite tirar máximo proveito da assincronicidade do FastAPI.
- **Versão:** `^2.0.31`

### Segurança: python-jose e passlib (bcrypt)
- **Por que?** Implementação do suporte a Autenticação usando JSON Web Tokens (JWT) e hash robusto de senhas, seguindo os preceitos de defesas ativas de SI.

### Ferramentas de Qualidade (Ruff, Mypy, Pytest)
- **Por que?** Promovem análise estática rigorosa para Python. Testes unificados por `pytest-asyncio` suportam TDD nos serviços de negócio, e HTTPX simula envios em testes de contrato.
