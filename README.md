# Sistema de Matrícula de Alunos de Graduação

> **Disciplina:** Segurança em Sistemas Distribuídos  
> **Professor:** Ricardo Staciarini Puttini  
> **Equipe:** Vicente Jr., Breno Ribeiro e Rosane  
> **Instituição:** Universidade de Brasília (UnB)

API RESTful construída com arquitetura de **Monólito Modular**, cobrindo os módulos de Autenticação, Alunos, Cursos, Disciplinas, Turmas, Histórico Acadêmico, Matrícula e Elegibilidade. Inclui governança via **Kong Gateway** (DB-less) e autenticação **JWT com RBAC** (bcrypt).

---

## 📋 Pré-requisitos

Antes de executar o projeto, instale as seguintes ferramentas no seu sistema operacional:

### ✅ Obrigatórias (via Docker — recomendado)

| Ferramenta | Versão mínima | Download |
|------------|--------------|----------|
| **Docker Desktop** | 24.x ou superior | https://www.docker.com/products/docker-desktop |
| **Git** | 2.x ou superior | https://git-scm.com/downloads |

> O Docker já inclui o Docker Compose v2. Nenhuma outra instalação é necessária para rodar via Docker.

---

### ⚙️ Alternativa: Execução local sem Docker

Caso prefira rodar sem Docker, instale também:

| Ferramenta | Versão mínima | Download |
|------------|--------------|----------|
| **Python** | 3.12 ou superior | https://www.python.org/downloads |
| **Poetry** | 1.8.3 ou superior | https://python-poetry.org/docs/#installation |
| **PostgreSQL** | 16.x ou superior | https://www.postgresql.org/download |

---

## 📦 Dependências da Aplicação (Python)

Gerenciadas automaticamente pelo **Poetry** via `pyproject.toml`.

### Produção

| Pacote | Versão | Função |
|--------|--------|--------|
| `fastapi` | ^0.111.0 | Framework web principal |
| `uvicorn[standard]` | ^0.30.1 | Servidor ASGI com hot-reload |
| `pydantic` | ^2.7.4 | Validação e serialização de dados |
| `pydantic-settings` | ^2.3.4 | Configuração via variáveis de ambiente |
| `sqlalchemy` | ^2.0.31 | ORM assíncrono para acesso ao banco |
| `alembic` | ^1.13.1 | Migrations de banco de dados |
| `asyncpg` | ^0.29.0 | Driver PostgreSQL assíncrono |
| `python-jose[cryptography]` | ^3.3.0 | Geração e validação de tokens JWT |
| `passlib[bcrypt]` | ^1.7.4 | Hash seguro de senhas (bcrypt) |
| `python-multipart` | ^0.0.9 | Suporte a formulários HTTP (login OAuth2) |

### Desenvolvimento

| Pacote | Versão | Função |
|--------|--------|--------|
| `pytest` | ^8.2.2 | Framework de testes |
| `pytest-asyncio` | ^0.23.7 | Suporte a testes assíncronos |
| `httpx` | ^0.27.0 | Cliente HTTP para testes de integração |
| `ruff` | ^0.4.9 | Linter e formatador rápido |
| `black` | ^24.4.2 | Formatador de código |
| `mypy` | ^1.10.0 | Checagem estática de tipos |

---

## 🚀 Como Executar

### Opção 1 — Docker (Recomendado)

É a forma mais simples. Não requer Python nem PostgreSQL instalados localmente.

**1. Clone o repositório:**
```bash
git clone https://github.com/juniorvfj/trabalho-ssd-matriculas.git
cd trabalho-ssd-matriculas
```

**2. Configure o arquivo de ambiente:**
```bash
# Linux/macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

**3. Suba os containers:**
```bash
docker compose up --build -d
```

> O comando irá: baixar as imagens, instalar dependências, rodar as migrations e iniciar a API automaticamente.

**4. Verifique se está rodando:**
```bash
docker compose ps
```

**5. Para encerrar:**
```bash
docker compose down
```

---

### Opção 2 — Execução Local com pip + requirements.txt

Use esta opção se **não quiser instalar o Poetry**. Requer Python 3.12+ e PostgreSQL (ou Docker só para o banco).

**1. Clone e entre na pasta:**
```bash
git clone https://github.com/juniorvfj/trabalho-ssd-matriculas.git
cd trabalho-ssd-matriculas
```

**2. Crie e ative um ambiente virtual:**
```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**3. Instale as dependências via requirements.txt:**
```bash
pip install -r requirements.txt
```

**4. Suba apenas o banco de dados:**
```bash
docker compose up -d db
```

**5. Configure o `.env`:**
```bash
# Linux/macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

**6. Execute as migrations:**
```bash
alembic upgrade head
```

**7. Inicie a API:**
```bash
uvicorn app.main:app --reload
```

---

### Opção 3 — Execução Local com Poetry

Use esta opção se preferir o gerenciador de dependências Poetry (mais robusto que pip para projetos com `pyproject.toml`).

**1. Clone e entre na pasta:**
```bash
git clone https://github.com/juniorvfj/trabalho-ssd-matriculas.git
cd trabalho-ssd-matriculas
```

**2. Instale as dependências Python:**
```bash
poetry install
```

**3. Suba apenas o banco de dados:**
```bash
docker compose up -d db
```

**4. Configure o `.env`:**
```bash
cp .env.example .env
```

**5. Execute as migrations:**
```bash
poetry run alembic upgrade head
```

**6. Inicie a API:**
```bash
poetry run uvicorn app.main:app --reload
```

---

## 🌐 Endpoints Disponíveis

Após subir o projeto, acesse:

| Recurso | URL |
|---------|-----|
| 📖 Swagger UI (documentação interativa) | http://localhost:8000/docs |
| 📋 ReDoc | http://localhost:8000/redoc |
| ❤️ Healthcheck | http://localhost:8000/health |
| 🔐 Autenticação | `POST /api/v1/auth/login` |
| 🧑‍🎓 Alunos | `/api/v1/alunos` |
| 🎓 Cursos | `/api/v1/cursos` |
| 📚 Disciplinas | `/api/v1/disciplinas` |
| 🏫 Turmas e Períodos Letivos | `/api/v1/turmas` |
| 📜 Histórico Acadêmico | `/api/v1/historicos` |
| 📝 Matrículas e Solicitações | `/api/v1/matriculas` |
| ✅ Verificar Elegibilidade (Serviço de Tarefa) | `POST /api/v1/tarefas/verificar-elegibilidade` |
| ⚙️ Processamento Batch | `POST /api/v1/matriculas/processamento/fase-3` |
| 🚀 Matrícula Extraordinária | `POST /api/v1/matriculas/extraordinaria` |
| 🧾 Comprovante de Matrícula | `GET /api/v1/alunos/{id}/comprovante-matricula` |
| 📊 Histórico de Processamento | `GET /api/v1/alunos/{id}/historico-processamento` |

---

## 🗄️ Banco de Dados

- **SGBD:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (assíncrono)
- **Migrations:** Alembic (executadas automaticamente ao subir via Docker)
- **Credenciais padrão (dev):**
  - Host: `localhost:5432`
  - Banco: `matricula_db`
  - Usuário: `postgres`
  - Senha: `password`

> ⚠️ Nunca use as credenciais padrão em produção. Atualize o `.env` com valores seguros.

---

## 🧪 Executando os Testes

```bash
# Com Poetry
poetry run pytest

# Dentro do container
docker compose exec api pytest
```

---

## 📁 Estrutura do Projeto

```
.
├── app/
│   ├── api/            # Roteadores globais (auth, deps)
│   ├── core/           # Configurações, segurança, exceções, banco
│   ├── modules/        # Módulos de domínio
│   │   ├── alunos/     # Serviço de Entidade — Aluno
│   │   ├── cursos/     # Serviço de Entidade — Curso
│   │   ├── disciplinas/# Serviço de Entidade — Disciplina
│   │   ├── turmas/     # Serviço de Entidade — Turma + Período Letivo
│   │   ├── historicos/ # Serviço de Entidade — Histórico Acadêmico
│   │   └── matriculas/ # Matrículas, Solicitações, Elegibilidade, Processamento Batch
│   └── shared/         # Modelos e utilitários compartilhados
├── docs/
│   ├── openapi/        # Contratos OpenAPI por serviço
│   ├── schemas/        # Modelos canônicos em JSON Schema
│   ├── decisions/      # ADRs (Architectural Decision Records)
│   ├── diagrams/       # Diagramas (Mermaid, PNG)
│   └── apim/           # Documentação do API Gateway (Kong)
├── docker/
│   └── kong/           # Configuração declarativa do Kong Gateway
├── migrations/         # Scripts de migration do Alembic
├── scripts/            # Scripts auxiliares (seed, batch)
├── tests/              # Testes (unit, integration, contract)
├── docker-compose.yml  # Orquestração: API + PostgreSQL + Kong Gateway
├── Dockerfile          # Imagem da API
├── pyproject.toml      # Dependências (Poetry)
├── requirements.txt    # Dependências (pip)
└── .env.example        # Modelo de variáveis de ambiente
```

---

## 🏗️ Decisões Arquiteturais

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Arquitetura | Monólito Modular | Menor complexidade operacional; foco no domínio acadêmico |
| Framework | Python 3.12 + FastAPI | Geração automática de OpenAPI 3, alta produtividade, tipagem forte |
| Banco de Dados | PostgreSQL 16 + SQLAlchemy 2 (async) | Robustez, integridade referencial, suporte assíncrono |
| Autenticação | JWT com bcrypt (modelo Usuario) | Hash seguro de senhas, papéis RBAC no token |
| API Gateway | Kong DB-less (declarativo) | Leve, sem necessidade de banco adicional, adequado para demonstração |
| Contratos | OpenAPI 3.1 + JSON Schema | Contract-first, validação automática, documentação gerada |

> 📄 ADRs detalhados disponíveis em `docs/decisions/`

---

## 🗺️ Roadmap e Pendências

### ✅ Implementado (Sprint 1 + Sprint 2)
- [x] Fundação (FastAPI, SQLAlchemy, Alembic, Docker Compose)
- [x] Módulos de Entidade: Aluno, Curso, Disciplina, Turma, Período Letivo, Histórico Acadêmico
- [x] Autenticação JWT básica (OAuth2 Password Flow)
- [x] Contratos OpenAPI e JSON Schemas base
- [x] Tratamento padronizado de erros (Modelo Canônico)
- [x] Serviço de Tarefa `verificarElegibilidade` (§5.2, §7.1) — 3 regras obrigatórias
- [x] Módulo Matrícula (Solicitação, Matrícula, Auditoria) — ORM, Schemas, Services, Router
- [x] Processamento Batch — Fases 3 e 5 (§7.2, §7.3, §7.4) — Motor com regras R1-R4
- [x] Matrícula Extraordinária (§7.5) — processamento imediato
- [x] Comprovante de Matrícula e Histórico de Processamento
- [x] Padronização de metadados (contact, license, version) em todos os contratos

### ✅ Implementado: Sprint 3 — Segurança RBAC + API Gateway
- [x] Modelo `Usuario` no banco com hash bcrypt e papéis (ADMIN, ALUNO, COORDENACAO, PROCESSAMENTO, CONSULTA)
- [x] Middleware RBAC para controle de acesso por papel nos endpoints
- [x] API Gateway Kong em modo DB-less (docker-compose declarativo)
- [x] Configuração `kong.yml` com rotas, rate-limiting e autenticação

### ✅ Implementado: Sprint 4 — Testes, ADRs e Seed Data
- [x] Testes unitários e de integração (pytest + pytest-asyncio)
- [x] Testes de segurança de autorização RBAC e validação de contratos (JSON Schemas extraídos)
- [x] ADRs (Architectural Decision Records) finalizados em `docs/decisions/`
- [x] Script de seed data (`scripts/seed.py`) para popular o banco com usuários (e suas roles), cursos, alunos, disciplinas e turmas
- [x] Correção do isolamento do pool do banco em ambiente de teste assíncrono

### Pendências futuras (fora do escopo atual)
- [ ] Entidade `Professor` (§6.7) — não impacta regras de negócio obrigatórias
- [ ] Entidade `TurmaProfessor` (§6.8) — depende de Professor
- [ ] `PUT /api/v1/disciplinas/{id}` — endpoint de atualização
- [ ] `PUT /api/v1/turmas/{id}` — endpoint de atualização

