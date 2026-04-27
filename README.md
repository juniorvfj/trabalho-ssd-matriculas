# Sistema de Matrícula de Alunos de Graduação

> **Disciplina:** Segurança em Sistemas Distribuídos  
> **Professor:** Ricardo Staciarini Puttini  
> **Equipe:** Vicente Jr., Breno Ribeiro e Rosane  
> **Instituição:** Universidade de Brasília (UnB)

API RESTful construída com arquitetura de **Monólito Modular**, cobrindo os módulos de Autenticação, Alunos, Cursos, Disciplinas, Turmas e Histórico Acadêmico.

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

### Opção 2 — Execução Local com Poetry

Use esta opção se quiser desenvolver sem Docker para a API (mas ainda requer o banco via Docker ou PostgreSQL local).

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
| 🏫 Turmas | `/api/v1/turmas` |
| 📜 Histórico Acadêmico | `/api/v1/historicos` |

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
│   ├── api/            # Roteadores globais (auth)
│   ├── core/           # Configurações, segurança, exceções
│   ├── modules/        # Módulos de domínio (alunos, cursos, etc.)
│   └── shared/         # Modelos e utilitários compartilhados
├── migrations/         # Scripts de migration do Alembic
├── tests/              # Testes automatizados
├── docker-compose.yml  # Orquestração dos containers
├── Dockerfile          # Imagem da API
├── pyproject.toml      # Dependências e configuração do projeto
└── .env.example        # Modelo de variáveis de ambiente
```
