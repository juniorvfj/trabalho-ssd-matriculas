# Plano de Execução - Sistema de Matrícula (Trabalho SSD - Vicente Jr)

Este documento detalha o plano de estruturação do repositório baseado no arquivo de especificação `trabalho_ssd_vicente.md`. O objetivo é construir a base do projeto garantindo SOA, design "Contract-First", segurança e uma arquitetura em Monólito Modular.

## 1. Diagnóstico Inicial
- **Status do Repositório**: Atualmente contém apenas a pasta `docs/` e a especificação `trabalho_ssd_vicente.md`. Nenhum código base, repositório completamente vazio.
- **Pendências/Decisões**: A implementação do batch/processamento real ficará como script pontual para facilitar demonstração acadêmica. Integração com SIGAA está fora do escopo funcional inicial, assumindo banco em branco.
- **Risco Técnico**: Versão exata de bibliotecas podem entrar em conflito (ex: Pydantic v2 x FastAPI dependendo do ecosistema). Faremos pinning en branch segura no `pyproject.toml`.

## 2. Inicialização do Repositório (Etapa 3 & 4)
### Mapeamento de Dependências
Será gerado o arquivo `docs/dependencias.md` contendo um levantamento justificado de bibliotecas que suportem Python 3.12:
- **FastAPI / Uvicorn / Pydantic v2**
- **SQLAlchemy 2.0 / Alembic / asyncpg** (Driver Assíncrono PostgreSQL)
- **Pytest** com **pytest-asyncio** e **httpx**
- Segurança: **python-jose**, **passlib**, **bcrypt**
- Qualidade: **ruff**, **black**, **mypy**

### Estrutura de Arquivos Base
Criaremos os arquivos de manifesto inicial:
- `pyproject.toml`
- `.env.example`
- `docker-compose.yml`
- `.gitignore`
- `README.md`
- `docs/plano_execucao.md` (Este mesmo documento)

## 3. Arquitetura e Documentação (Etapa 5)
Criar e detalhar a pasta `docs/`:
- `docs/arquitetura.md` (Visão geral Monólito Modular).
- `docs/modelo_dominio.md` (Baseado nas especificações contidas no markdown inicial).
- `docs/decisions/` com `ADR-001`, `ADR-002`, `ADR-003`.

## 4. Bootstrap do Projeto (Etapa 7)
Estruturação da pasta `app/` para que o FastAPI rode sem problemas e exponha um Health Check:
- `app/main.py`
- `app/core/config.py` (BaseSettings do Pydantic)
- `app/core/database.py` (Conexão assíncrona SQLAlchemy)
- `app/core/exceptions.py` (Tratamento global para formato de erro padronizado)
- `app/core/security.py`
- `app/core/logging.py`

## 5. Contratos e Modelos Canônicos (Etapa 9)
Modelagem "Contract First". Serão criados arquivos na pasta `docs/schemas/` e `docs/openapi/`:
- Respostas e requisições padronizadas ("envelopes", formato de erros UUID/ISO 8601).

## 6. Primeiros Módulos e Serviço de Tarefa (Etapas 8 & 10)
Criação dos esqueletos dos domínios Alunos, Cursos, Disciplinas, Turmas, sob a pasta `app/modules/`.
- Estrutura base de `api/`, `application/`, `domain/`, `infrastructure/` para cada módulo citado.
- Implementação da rota e estrutura base para o Serviço de Tarefa `verificarElegibilidade`, preparando para as regras de negócio de fases futuras.
