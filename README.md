# Sistema de Matrícula de Alunos de Graduação

> **Disciplina:** Segurança em Sistemas Distribuídos  
> **Professor:** Ricardo Staciarini Puttini  
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro  
> **Instituição:** Universidade de Brasília (UnB)

API RESTful construída com arquitetura de **Monólito Modular**, cobrindo os módulos de Autenticação, Alunos, Cursos, Disciplinas, Turmas, Docentes, Unidades Organizacionais, Histórico Acadêmico, Matrícula e Elegibilidade. Inclui governança via **Kong Gateway** (DB-less) e autenticação **JWT com RBAC** (bcrypt).

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

Os três serviços devem aparecer como `running`:
- `ssd_vicente_db` — PostgreSQL 16
- `ssd_vicente_api` — API FastAPI (porta 8000)
- `ssd_vicente_kong` — API Gateway Kong (porta 8080)

**5. Acesse a documentação interativa:**

Abra no navegador: http://localhost:8000/docs

**6. Para encerrar:**
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

**7. (Opcional) Popule o banco com dados de teste:**
```bash
python scripts/seed.py
```

**8. Inicie a API:**
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

**6. (Opcional) Popule o banco com dados de teste:**
```bash
poetry run python scripts/seed.py
```

**7. Inicie a API:**
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

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/login` | Obter token JWT (OAuth2 Password Flow) |

### Serviços de Entidade (CRUD)

| Entidade | Prefixo | Operações |
|----------|---------|-----------|
| 🧑‍🎓 Alunos | `/api/v1/alunos` | GET (listar/detalhar), POST |
| 🎓 Cursos | `/api/v1/cursos` | GET (listar/detalhar), POST |
| 📚 Disciplinas | `/api/v1/disciplinas` | GET (listar/detalhar), POST |
| 🏫 Turmas e Períodos | `/api/v1/turmas` | GET (listar turmas e períodos), POST |
| 📜 Histórico Acadêmico | `/api/v1/historicos` | GET (listar/por aluno), POST |
| 📝 Matrículas | `/api/v1/matriculas` | GET (listar/detalhar), POST |
| 📊 Currículos | `/api/v1/curriculos` | GET (listar/detalhar), POST (vincular disciplina) |
| 👨‍🏫 Docentes | `/api/v1/docentes` | GET (listar/detalhar), POST, vincular turma |
| 🏛️ Unidades Organizacionais | `/api/v1/unidades-organizacionais` | GET (listar/detalhar), POST |

### Serviços de Tarefa

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/tarefas/verificar-elegibilidade` | Verificar elegibilidade de aluno para disciplina (§5.2, §7.1) |
| `POST` | `/api/v1/matriculas/processamento/fase-3` | Processamento batch de matrículas (§7.2, §7.3, §7.4) |
| `POST` | `/api/v1/matriculas/extraordinaria` | Matrícula extraordinária com processamento imediato (§7.5) |

### Consultas Especiais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/alunos/{id}/comprovante-matricula` | Comprovante de matrícula do aluno |
| `GET` | `/api/v1/alunos/{id}/historico-processamento` | Histórico de processamento de matrículas |

---

## 🗄️ Banco de Dados

- **SGBD:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0 (assíncrono com asyncpg)
- **Migrations:** Alembic (executadas automaticamente ao subir via Docker)
- **Credenciais padrão (dev):**
  - Host: `localhost:5432`
  - Banco: `matricula_db`
  - Usuário: `postgres`
  - Senha: `password`

> ⚠️ Nunca use as credenciais padrão em produção. Atualize o `.env` com valores seguros.

### Modelo de Dados

O diagrama de entidades completo está disponível em [`docs/diagrams/Modelo de Entidades.png`](docs/diagrams/Modelo%20de%20Entidades.png).

**Tabelas do sistema:**

| Tabela | Módulo | Descrição |
|--------|--------|-----------|
| `usuarios` | Autenticação | Usuários do sistema com hash bcrypt e papéis RBAC |
| `alunos` | Alunos | Dados cadastrais dos alunos de graduação |
| `cursos` | Cursos | Cursos oferecidos (com FK para coordenador e UO) |
| `disciplinas` | Disciplinas | Componentes curriculares (com FK para UO) |
| `disciplina_prerequisitos` | Disciplinas | Tabela associativa de pré-requisitos (N:M) |
| `periodos_letivos` | Turmas | Semestres acadêmicos (datas de início/fim) |
| `turmas` | Turmas | Turmas oferecidas por disciplina e período |
| `docentes` | Docentes | Professores e coordenadores |
| `turma_docentes` | Docentes | Tabela associativa Turma ↔ Docente (N:M) |
| `unidades_organizacionais` | Unidades Org. | Departamentos, institutos e faculdades |
| `historico_academico` | Históricos | Histórico consolidado do aluno (1:1) |
| `historico_disciplinas` | Históricos | Disciplinas cursadas (itens do histórico) |
| `solicitacoes_matricula` | Matrículas | Solicitações de matrícula pendentes |
| `matriculas` | Matrículas | Matrículas efetivadas |
| `auditoria_processamento` | Matrículas | Log de auditoria do processamento batch |
| `curriculos` | Currículos | Grade curricular do curso |
| `curriculo_disciplinas` | Currículos | Disciplinas da grade (tabela associativa) |

---

## 🧪 Executando os Testes

### Dentro do container (recomendado)

```bash
# Rodar toda a suite de testes
docker compose exec api python -m pytest -v

# Rodar apenas os testes dos novos módulos (Docentes e UO)
docker compose exec api python -m pytest tests/test_docentes_e_unidades.py -v

# Rodar testes de autenticação RBAC
docker compose exec api python -m pytest tests/test_api_auth.py -v

# Rodar testes de currículos
docker compose exec api python -m pytest tests/test_api_curriculos.py -v
```

### Com Poetry (local)

```bash
poetry run pytest -v
```

### Cobertura de Testes

| Arquivo de Testes | Testes | O que valida |
|-------------------|--------|-------------|
| `test_api_auth.py` | 1 | Autenticação JWT e controle RBAC (403 Forbidden vs 200 OK) |
| `test_api_curriculos.py` | 1 | CRUD de currículos e vinculação de disciplinas |
| `test_docentes_e_unidades.py` | 7 | CRUD Docente, UO, matrícula duplicada, código duplicado, vinculação N:M turma-docente, relações Curso↔Coordenador e Disciplina↔UO |
| `test_elegibilidade.py` | 4 | Regras de elegibilidade (§7.1): currículo, aprovação prévia, pré-requisitos |

---

## 📁 Estrutura do Projeto

```
.
├── app/                          # Código-fonte principal da aplicação
│   ├── __init__.py               # Docstring do pacote raiz
│   ├── main.py                   # Entrypoint — factory do FastAPI com registro de routers
│   ├── api/                      # Camada de API global
│   │   ├── auth.py               # Endpoint de login (geração de JWT)
│   │   └── deps.py               # Dependências: get_current_user, RoleChecker (RBAC)
│   ├── core/                     # Infraestrutura transversal
│   │   ├── config.py             # Variáveis de ambiente via Pydantic Settings
│   │   ├── database.py           # Engine assíncrona, SessionLocal e Base do SQLAlchemy
│   │   ├── security.py           # JWT (python-jose) + bcrypt (hash de senhas)
│   │   ├── exceptions.py         # Modelo Canônico de Erro + handlers globais
│   │   └── logging.py            # Logger centralizado
│   ├── modules/                  # Módulos de domínio (monólito modular)
│   │   ├── alunos/               # Serviço de Entidade — Aluno
│   │   ├── cursos/               # Serviço de Entidade — Curso
│   │   ├── disciplinas/          # Serviço de Entidade — Disciplina (com pré-requisitos)
│   │   ├── turmas/               # Serviço de Entidade — Turma + Período Letivo
│   │   ├── historicos/           # Serviço de Entidade — Histórico Acadêmico
│   │   ├── matriculas/           # Matrícula, Solicitação, Elegibilidade, Processamento Batch
│   │   ├── curriculos/           # Serviço de Entidade — Currículo (grade curricular)
│   │   ├── docentes/             # Serviço de Entidade — Docente (professor/coordenador)
│   │   ├── unidades_organizacionais/  # Serviço de Entidade — Departamento/Instituto
│   │   └── usuarios/             # Serviço de Entidade — Usuário (autenticação RBAC)
│   └── shared/                   # Utilitários compartilhados entre módulos
├── docs/
│   ├── openapi/                  # Contratos OpenAPI (YML) por serviço
│   ├── schemas/                  # Modelos canônicos em JSON Schema
│   ├── decisions/                # ADRs (Architectural Decision Records)
│   ├── diagrams/                 # Diagramas de Entidades e Arquitetura (PNG)
│   └── apim/                     # Documentação do API Gateway (Kong)
├── docker/
│   └── kong/                     # Configuração declarativa do Kong Gateway (kong.yml)
├── migrations/
│   ├── env.py                    # Configuração do Alembic (imports de todos os ORM models)
│   └── versions/                 # Scripts de migration (DDL versionado)
├── scripts/
│   └── seed.py                   # Script para popular o banco com dados de teste
├── tests/                        # Suite de testes automatizados
│   ├── conftest.py               # Fixtures globais (engine, db_session, client HTTP)
│   ├── test_api_auth.py          # Testes de autenticação e RBAC
│   ├── test_api_curriculos.py    # Testes de currículos
│   ├── test_docentes_e_unidades.py # Testes de Docentes, UO e relacionamentos
│   └── test_elegibilidade.py     # Testes do serviço de tarefa verificarElegibilidade
├── docker-compose.yml            # Orquestração: API + PostgreSQL + Kong Gateway
├── Dockerfile                    # Imagem da API (Python 3.12-slim)
├── pyproject.toml                # Dependências e metadados (Poetry)
├── requirements.txt              # Dependências (pip, alternativa ao Poetry)
├── alembic.ini                   # Configuração do Alembic
├── pytest.ini                    # Configuração do Pytest
└── .env.example                  # Modelo de variáveis de ambiente
```

### Estrutura de cada Módulo

Todos os módulos de domínio seguem a mesma **Layered Architecture**:

```
módulo/
├── __init__.py               # Docstring descritiva do módulo
├── api/
│   ├── router.py             # Endpoints REST (FastAPI APIRouter)
│   └── schemas.py            # DTOs de entrada/saída (Pydantic BaseModel)
├── application/
│   └── services.py           # Regras de negócio e orquestração
└── infrastructure/
    └── orm_models.py         # Modelos ORM (SQLAlchemy declarative_base)
```

---

## 🔐 Segurança e Autenticação

### Fluxo de Autenticação

1. **Login:** O cliente envia `username` e `password` para `POST /api/v1/auth/login`
2. **Validação:** O servidor verifica as credenciais contra o hash bcrypt no banco
3. **Token:** Se válido, o servidor retorna um JWT assinado com HS256
4. **Uso:** O cliente inclui o token no header `Authorization: Bearer <token>`
5. **Verificação:** Cada endpoint protegido decodifica e valida o JWT

### Papéis (RBAC)

| Papel | Descrição | Permissões |
|-------|-----------|------------|
| `ADMIN` | Administrador do sistema | Acesso total |
| `COORDENACAO` | Coordenação acadêmica | Gestão de cursos, disciplinas, turmas |
| `PROCESSAMENTO` | Setor de processamento | Execução de processamento batch |
| `CONSULTA` | Consulta | Leitura de dados |
| `ALUNO` | Aluno | Acesso ao próprio perfil |

### API Gateway (Kong)

O Kong opera em modo DB-less (declarativo) via `docker/kong/kong.yml`:
- **Rate Limiting:** Proteção contra abuso (requisições por minuto)
- **Roteamento:** Proxy reverso para a API interna na porta 8000
- **Porta de acesso:** `http://localhost:8080`

---

## 📄 Contratos e Documentação

### OpenAPI Specifications (YML)

| Arquivo | Serviço |
|---------|---------|
| `docs/openapi/aluno_api.v1.yml` | API de Alunos |
| `docs/openapi/curso_api.v1.yml` | API de Cursos |
| `docs/openapi/disciplina_api.v1.yml` | API de Disciplinas |
| `docs/openapi/turma_api.v1.yml` | API de Turmas e Períodos |
| `docs/openapi/historico_api.v1.yml` | API de Histórico Acadêmico |
| `docs/openapi/matricula_api.v1.yml` | API de Matrículas |
| `docs/openapi/curriculo_api.v1.yml` | API de Currículos |
| `docs/openapi/docente_api.v1.yml` | API de Docentes |
| `docs/openapi/unidade_organizacional_api.v1.yml` | API de Unidades Organizacionais |

### JSON Schemas (Modelos Canônicos)

| Arquivo | Entidade |
|---------|----------|
| `docs/schemas/aluno.v1.json` | Aluno |
| `docs/schemas/curso.v1.json` | Curso |
| `docs/schemas/disciplina.v1.json` | Disciplina |
| `docs/schemas/turma.v1.json` | Turma |
| `docs/schemas/docente.v1.json` | Docente |
| `docs/schemas/unidade_organizacional.v1.json` | Unidade Organizacional |

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
| Migrations | Alembic (manual + autogenerate) | DDL versionado, rollback seguro, compatível com async |
| Testes | pytest + pytest-asyncio + httpx | Stack moderna para testes assíncronos de integração |

> 📄 ADRs detalhados disponíveis em `docs/decisions/`

---

## 🗺️ Roadmap e Pendências

### ✅ Sprint 1 — Fundação
- [x] Estrutura do projeto (FastAPI, SQLAlchemy, Alembic, Docker Compose)
- [x] Módulos de Entidade: Aluno, Curso, Disciplina, Turma, Período Letivo
- [x] Autenticação JWT básica (OAuth2 Password Flow)
- [x] Contratos OpenAPI e JSON Schemas base

### ✅ Sprint 2 — Regras de Negócio
- [x] Serviço de Tarefa `verificarElegibilidade` (§5.2, §7.1) — 3 regras obrigatórias
- [x] Módulo Matrícula (Solicitação, Matrícula, Auditoria)
- [x] Processamento Batch — Fases 3 e 5 (§7.2, §7.3, §7.4) — Motor com regras R1-R4
- [x] Matrícula Extraordinária (§7.5)
- [x] Comprovante de Matrícula e Histórico de Processamento

### ✅ Sprint 3 — Segurança RBAC + API Gateway
- [x] Modelo `Usuario` com hash bcrypt e 5 papéis RBAC
- [x] Middleware RoleChecker para controle de acesso por papel
- [x] Kong Gateway em modo DB-less (declarativo)

### ✅ Sprint 4 — Testes, ADRs e Seed Data
- [x] Testes de integração (pytest + pytest-asyncio + httpx)
- [x] Testes de segurança RBAC e validação de contratos
- [x] ADRs (Architectural Decision Records)
- [x] Script de seed data (`scripts/seed.py`)

### ✅ Sprint 5 — Modelo de Entidades Completo
- [x] Entidade `Docente` (professor/coordenador) com CRUD e vinculação N:M com Turma
- [x] Entidade `UnidadeOrganizacional` (departamento/instituto) com CRUD
- [x] Relações: `Curso.coordenador_id → Docente`, `Curso.unidade_organizacional_id → UO`, `Disciplina.unidade_organizacional_id → UO`
- [x] Contratos OpenAPI e JSON Schemas para Docente e UO
- [x] 7 novos testes de integração validando CRUD e relacionamentos
- [x] Documentação completa com docstrings em todos os módulos
