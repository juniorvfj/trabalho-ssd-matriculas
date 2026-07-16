# Sistema de Matrícula de Alunos de Graduação

> **Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018)
> **Professor:** Ricardo Staciarini Puttini
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
> **Instituição:** Universidade de Brasília (UnB)

API RESTful construída com arquitetura de **Monólito Modular** (princípios SOA), cobrindo os
serviços de entidade Aluno, Curso, Disciplina, Currículo, Turma, Unidade Organizacional e
Histórico Acadêmico, além do serviço de tarefa `verificarElegibilidade` e do processamento de
matrícula (Fases 3/5 e extraordinária). Governança via **Kong Gateway** (DB-less).

> ℹ️ **Modelo de dados SIGAA (do professor).** O projeto adota **nativamente o schema SIGAA**
> disponibilizado pelo professor em `professor_material/database/`: tabelas `sigaa_*` com **chaves
> naturais de negócio** (aluno = matrícula `'180012345'`, curso `'6351'`, disciplina `'CIC0007'`,
> unidade `'CIC'`, currículo `'6351/2'`). Assim, o **DML do professor é carregado como seed
> verbatim**, sem transformação. As rotas seguem os base paths `/api/<Recurso>` e as listagens
> usam o envelope **`SearchSet`** com a chave **`resourceType`**.

> 🧩 **Banco físico × API conceitual.** As respostas da API expõem o **modelo conceitual** do
> diagrama de entidades (`docs/diagrams/`), derivado das colunas físicas em tempo de consulta:
> objetos de valor `CargaHoraria`, `Prazo` e `PeriodoLetivo {ano, periodo}`, e **herança**
> `Disciplina` → `Disciplina_Curriculo` / `Disciplina_HistoricoAcademico` (padrão `allOf` dos
> contratos de referência do professor). O de-para completo campo a campo está em
> [`docs/mapeamento-conceitual-fisico.md`](docs/mapeamento-conceitual-fisico.md). Na API, o id
> público do currículo usa a convenção do professor: **`6351.2`** (banco: `'6351/2'`).

> 🔓 **Sem autenticação.** Conforme orientação do professor, esta entrega **não** implementa
> autenticação/RBAC. Todos os endpoints são abertos.

---

## 📋 Pré-requisitos

| Ferramenta | Versão mínima | Observação |
|------------|--------------|------------|
| **Docker Desktop** | 24.x+ | Inclui o Docker Compose v2 (forma recomendada) |
| **Git** | 2.x+ | |
| Python | 3.12+ | Apenas para execução local sem Docker |
| PostgreSQL | 16.x+ | Apenas para execução local sem Docker |

## 📦 Principais dependências (Python)

`fastapi`, `uvicorn[standard]`, `pydantic` v2, `sqlalchemy` 2 (async), `alembic`, `asyncpg`.
Dev: `pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`, `ruff`, `black`, `mypy`.

---

## 🚀 Como Executar

### Opção 1 — Docker (recomendado)

```bash
git clone https://github.com/juniorvfj/trabalho-ssd-matriculas.git
cd trabalho-ssd-matriculas
cp .env.example .env          # Windows: Copy-Item .env.example .env
docker compose up --build -d
```

Ao subir, o container da API executa automaticamente, nesta ordem:
1. `alembic upgrade head` — cria as 17 tabelas do schema SIGAA;
2. `python -m scripts.seed` — carrega o **DML do professor** (idempotente);
3. `uvicorn` — sobe a API.

Serviços (`docker compose ps`): `ssd_vicente_db` (PostgreSQL 16), `ssd_vicente_api` (porta 8000)
e `ssd_vicente_kong` (gateway — proxy na porta 80 do host, admin na 8001).

Documentação interativa: <http://localhost:8000/docs> (direto) ou <http://localhost/docs> (via Kong)

### Opção 2 — Local (Python + PostgreSQL)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d db            # sobe apenas o banco
cp .env.example .env
alembic upgrade head               # cria o schema SIGAA
python -m scripts.seed             # carrega os dados do professor
uvicorn app.main:app --reload
```

---

## 🗄️ Banco de Dados (schema SIGAA)

- **SGBD:** PostgreSQL 16 · **ORM:** SQLAlchemy 2 (async/asyncpg) · **Migrations:** Alembic
- **Credenciais dev:** host `localhost:5432`, banco `matricula_db`, usuário `postgres`, senha `password`
- **Fonte da verdade do schema:** os modelos ORM (que espelham o DDL do professor). O Alembic cria
  as tabelas; o **seed carrega os dados** a partir de `professor_material/database/`.

### Carga de dados do professor

A massa de dados é carregada por [scripts/seed.py](scripts/seed.py) diretamente dos scripts DML do
professor, respeitando a ordem de chaves estrangeiras:

| Arquivo (professor) | Tabelas carregadas |
|---------------------|--------------------|
| `SIGAA-DDL - novo.sql` (INSERTs) | `sigaa_turma_horarioaula`, `sigaa_matricula_status` |
| `SIGAA-DML-DisciplinaCurso - novo.sql` | `sigaa_unidade`, `sigaa_curso`, `sigaa_rl_curso_unidade`, `sigaa_curriculo`, `sigaa_rl_curriculo_curso`, `sigaa_disciplina`, `sigaa_prereq`, `sigaa_rl_curriculo_disciplina` |
| `SIGAA-DatabaseDML_Alunos - novo.sql` | `sigaa_aluno`, `sigaa_rl_aluno_curso` |

O seed é **idempotente** (se `sigaa_unidade` já tem dados, não recarrega) e **perene** (roda a cada
boot do container). Total carregado: **433 INSERTs** (14 unidades, 2 cursos, 8 currículos, 79
disciplinas, 95 pré-requisitos, 117 vínculos currículo↔disciplina, 54 horários, 14 status de
matrícula, 20 alunos e 20 vínculos aluno↔curso).

### Tabelas (`sigaa_*`)

| Tabela | Descrição |
|--------|-----------|
| `sigaa_unidade` | Unidades organizacionais (PK código, ex.: `'CIC'`) |
| `sigaa_disciplina` | Disciplinas (PK código, ex.: `'CIC0007'`) + carga horária teórica/prática |
| `sigaa_prereq` | Pré-requisitos entre disciplinas (PK composta) |
| `sigaa_curso` | Cursos (PK código, ex.: `'6351'`); `coordenador` é texto |
| `sigaa_rl_curso_unidade` | Vínculo M:N curso ↔ unidade |
| `sigaa_curriculo` | Estrutura curricular (PK ex.: `'6351/2'`) + cargas/períodos |
| `sigaa_rl_curriculo_curso` | Vínculo M:N currículo ↔ curso |
| `sigaa_rl_curriculo_disciplina` | Disciplinas do currículo (período, tipo `OBR`/`OPT`) |
| `sigaa_turma_horarioaula` | Slots de horário (dia/hora) |
| `sigaa_turma` | Turmas (PK serial); período letivo é texto (`'20182'`) |
| `sigaa_rl_turma_horarioaula` | Vínculo M:N turma ↔ horário |
| `sigaa_aluno` | Alunos (PK matrícula) |
| `sigaa_rl_aluno_curso` | Vínculo aluno↔curso: currículo, IRA, ingresso, status |
| `sigaa_rl_aluno_curso_disciplina` | Histórico: disciplinas cursadas + menção |
| `sigaa_matricula_status` | Domínio de status (`PND`, `MAT`, `NEL`, `CEX`, `JMD`, `CON`, `FUL`, …) |
| `sigaa_matricula` | Matrícula (vínculo aluno-curso ↔ turma) com código de status |
| `sigaa_matricula_historico` | Trilha de auditoria das transições de status |

---

## 🌐 Endpoints

| Recurso | URL |
|---------|-----|
| Swagger UI | <http://localhost:8000/docs> |
| ReDoc | <http://localhost:8000/redoc> |
| OpenAPI JSON | <http://localhost:8000/api/v1/openapi.json> |
| Healthcheck | <http://localhost:8000/health> |

> As listagens (`GET /`) retornam o envelope **`SearchSet`** (`total`, `count`, `offset`, `link`
> com `self`/`next`/`previous`, `items`); cada recurso carrega `resourceType`. O prefixo `/api/v1`
> permanece **apenas** no caminho do documento OpenAPI.

### Serviços de Entidade

| Entidade | Base path | Operações |
|----------|-----------|-----------|
| 🧑‍🎓 Aluno | `/api/Aluno` | `GET /` (filtros `nome`, `curso`, `periodoIngresso`), `GET /{matricula}`, `POST /` |
| 🎓 Curso | `/api/Curso` | `GET /` (filtros `nome`, `unidade`), `GET /{id}`, `POST /` |
| 📚 Disciplina | `/api/Disciplina` | `GET /` (filtros `nome`, `modalidade`, `unidade`), `GET /{id}` (cargas horárias como objetos + pré-requisitos), `POST /`, `POST /{id}/prerequisitos` |
| 📊 Currículo | `/api/Curriculo` | `GET /` (filtro `curso`), `GET /{id}` (`cargaHoraria` e `prazo` como objetos; id `6351.2`), `GET /{id}/disciplina` (filtros `nivel`, `tipo`; itens `Disciplina_Curriculo`), `GET /{id}/disciplina/{disciplina}`, `POST /`, `POST /{id}/disciplina` |
| 🏫 Turma | `/api/Turma` | `GET /` (filtros `periodoLetivo`, `disciplina`), `GET /{id}`, `POST /`, `GET /horarios`, `POST /horarios` |
| 📜 Histórico | `/api/HistoricoAcademico` | `GET /{matricula}` (consolidado: `cargaHorariaIntegralizadas`/`Pendente` derivadas), `GET /{matricula}/disciplina` (filtros `periodoLetivo`, `status`, `disciplina`; array de `Disciplina_HistoricoAcademico`), `POST /disciplina` |
| 🏛️ Unidade Organizacional | `/api/UnidadeOrganizacional` | `GET /` (filtro `nome`), `GET /{id}`, `POST /` |
| 📝 Matrícula | `/api/Matricula` | `GET /` (`periodoLetivo` obrigatório + `aluno` ou `turma`), `GET /{id}`, `POST /` (lote de pedidos, status `PND`), `PATCH /{id}` (JSON Patch de status) |

### Serviços de Tarefa e Processamento

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/Tarefa/verificar-elegibilidade` | Verifica elegibilidade aluno↔disciplina (§5.2, §7.1) |
| `POST` | `/api/Matricula/processamento/fase-3` | Processamento batch da Fase 3 (§7.2–§7.4) |
| `POST` | `/api/Matricula/processamento/fase-5` | Reprocessamento batch (Fase 5) |
| `POST` | `/api/Matricula/extraordinaria` | Matrícula extraordinária imediata (§7.5) |
| `GET` | `/api/Matricula/alunos/{matricula}/comprovante-matricula?periodoLetivo=<p>` | Comprovante de matrícula |
| `GET` | `/api/Matricula/alunos/{matricula}/historico-processamento` | Trilha de auditoria do processamento |

### Regras de elegibilidade (§7.1)

O serviço `verificarElegibilidade` aplica três regras sobre o modelo SIGAA:
1. a disciplina pertence ao **currículo** do vínculo do aluno (`sigaa_rl_curriculo_disciplina`);
2. o aluno **ainda não foi aprovado** nela (menção `SS`/`MS`/`MM` em `sigaa_rl_aluno_curso_disciplina`);
3. o aluno possui todos os **pré-requisitos** (`sigaa_prereq`).

O processamento batch (Fases 3/5) ordena os pedidos elegíveis por **IRA desc → data de registro asc →
desempate aleatório** (§7.2) e rejeita por limite de carga horária do período, disciplina duplicada,
conflito de horário (§7.3) ou falta de vagas (§7.4), gravando o resultado no código de status da
matrícula e na trilha `sigaa_matricula_historico`.

---

## 📁 Estrutura do Projeto

```
app/
├── main.py                     # Factory FastAPI e registro dos routers
├── core/                       # config, database, exceptions, logging
├── shared/responses/           # Envelope SearchSet
├── shared/schemas/             # Modelo conceitual: Resource, PeriodoLetivo, CargaHoraria, Prazo,
│                               #   Disciplina → DisciplinaCurriculo/DisciplinaHistoricoAcademico (herança)
└── modules/                    # Um pacote por domínio (api/ application/ infrastructure/)
    ├── alunos/  cursos/  disciplinas/  curriculos/  turmas/
    ├── historicos/  unidades_organizacionais/
    └── matriculas/             # elegibilidade, processamento, extraordinária, services
docs/
├── mapeamento-conceitual-fisico.md  # De-para diagrama ↔ banco ↔ API (campo a campo)
├── openapi/                    # Contratos por serviço (allOf/Resource) + openapi_sigaa.v1.json exportado
├── diagrams/                   # Modelo de Entidades (contrato conceitual da API)
professor_material/             # Material de referência do professor
├── database/                   # DDL/DML SIGAA (fonte do seed)
└── *.yml                       # Contratos de exemplo (Aluno, Matricula, HistoricoAcademico)
migrations/versions/            # baseline_sigaa_schema (Alembic)
scripts/seed.py                 # Carga do DML do professor (idempotente)
tests/                          # conftest (SQLite + dados do professor) + test_sigaa_api
```

Cada módulo segue a arquitetura em camadas: `api/` (router + schemas), `application/` (services),
`infrastructure/` (orm_models).

---

## 🧪 Testes

Os testes rodam em **SQLite temporário** com os dados do professor carregados pelo `conftest`
(portável, sem exigir PostgreSQL):

```bash
pytest -v
# ou dentro do container:
docker compose exec api python -m pytest -v
```

[tests/test_sigaa_api.py](tests/test_sigaa_api.py) — **13 testes** — valida os serviços de
entidade (SearchSet, detalhes de curso/aluno), as regras de elegibilidade (§7.1) e o modelo
conceitual nas respostas: `cargaHorariaPresencial`/`cargaHorariaTotal` da Disciplina, objetos
`cargaHoraria`/`prazo` do Currículo, herança `Disciplina_Curriculo`/`Disciplina_HistoricoAcademico`
e campos derivados (`vagasPreenchidas`, `motivoIndeferimento`, status do histórico).

---

## 🏗️ Decisões Arquiteturais

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Arquitetura | Monólito Modular | Menor complexidade; foco no domínio |
| Framework | Python 3.12 + FastAPI | OpenAPI automático, tipagem forte |
| Banco | PostgreSQL 16 + SQLAlchemy 2 async | Integridade referencial, suporte assíncrono |
| **Modelo de dados** | **Schema SIGAA do professor** | Máxima fidelidade; DML carregado verbatim |
| Autenticação | **Removida** | Não exigida nesta entrega (orientação do professor) |
| Gateway | Kong DB-less | Leve, adequado para demonstração |
| Migrations | Alembic (baseline único SIGAA) | DDL versionado |

---

## 🗺️ Estado atual

- [x] Adoção nativa do schema SIGAA (17 tabelas `sigaa_*`) via baseline Alembic
- [x] Carga perene e idempotente do DML do professor no boot do container
- [x] Serviços de entidade e de tarefa (`verificarElegibilidade`) sobre o modelo SIGAA
- [x] Processamento batch (Fases 3/5) e matrícula extraordinária (§7.5)
- [x] Respostas no **modelo conceitual do diagrama**: objetos `CargaHoraria`/`Prazo`/`PeriodoLetivo`
      e herança de `Disciplina` (ajustes solicitados na apresentação; ver
      [`docs/mapeamento-conceitual-fisico.md`](docs/mapeamento-conceitual-fisico.md))
- [x] Contratos OpenAPI por serviço no padrão de referência (`allOf` + `Resource`/discriminator)
- [x] Testes de integração portáveis (SQLite + dados do professor) — 13 testes
- [x] Autenticação/RBAC removida conforme orientação do professor
