# Dependências e Fundamentos Tecnológicos

Justificativa das tecnologias adotadas para atender aos requisitos de Segurança em Sistemas
Distribuídos e Monólito Modular, usando Python 3.12.

## Tecnologias Base

### FastAPI
- **Por que?** Excelente aderência nativa a contratos OpenAPI e "Contract-First", permitindo
  modelar `Request`/`Response` robustos. Gera documentação interativa (Swagger) e tem ótima
  performance por ser assíncrono.
- **Versão:** `^0.111.0`

### Pydantic (v2) e Pydantic-Settings
- **Por que?** Validação forte de dados que sustenta os Modelos Canônicos. Usado para os DTOs
  (schemas de entrada/saída) e para o envelope padronizado `SearchSet` das listagens.
- **Versão:** `^2.7.4`

### SQLAlchemy (2.x) e Alembic
- **Por que?** ORM e gestor de migrações para o PostgreSQL. O ORM mapeia **as tabelas `sigaa_*`
  do professor** (chaves naturais); o Alembic versiona o schema (baseline único `baseline_sigaa_schema`).
  O driver `asyncpg` aproveita a assincronicidade do FastAPI. Nos testes, `aiosqlite` permite rodar
  a suíte em SQLite temporário, sem exigir um PostgreSQL.
- **Versões:** SQLAlchemy `^2.0.31`, Alembic `^1.13.1`.

### Carga de dados (seed)
- O DML de referência do professor (`professor_material/database/`) é carregado **verbatim** por
  `scripts/seed.py` no boot do container (após `alembic upgrade head`), de forma idempotente e perene.

### Segurança e Governança
- **Sem autenticação/RBAC nesta entrega**, conforme orientação do professor — as bibliotecas de
  JWT/hash (`python-jose`, `passlib`) foram **removidas**. Os endpoints são abertos.
- Governança de APIs via **Kong Gateway** (DB-less): proxy reverso e rate limiting.
- Segurança de dados via **validação forte de entrada** (Pydantic) e **tratamento de erros
  padronizado** (Modelo Canônico de Erro).

### Ferramentas de Qualidade (Ruff, Black, Mypy, Pytest)
- **Por que?** Análise estática e formatação rigorosas para Python. Testes com
  `pytest`/`pytest-asyncio` e `httpx` cobrem os serviços e os contratos de forma assíncrona.
