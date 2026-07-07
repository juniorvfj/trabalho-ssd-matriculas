# Sistema de Matrícula de Alunos de Graduação — Roteiro de Apresentação

**Autores:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
**Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018) — UnB
**Professor:** Ricardo Staciarini Puttini

---

## 1. Problema e Objetivo

O trabalho implementa as fases de **matrícula e processamento** de alunos de graduação, com o
objetivo de **demonstrar Arquitetura Orientada a Serviços (SOA)** e boas práticas de sistemas
distribuídos: modelos de dados canônicos, contratos padronizados (OpenAPI), serviços RESTful e
governança de APIs.

## 2. Decisões Arquiteturais

- **Monólito Modular** em **Python 3.12 + FastAPI**: cada domínio (Aluno, Curso, Disciplina,
  Currículo, Turma, Unidade, Histórico, Matrícula) é um módulo independente com camadas
  `api/` (rotas + schemas), `application/` (regras) e `infrastructure/` (ORM), pronto para uma
  eventual separação em microsserviços.
- **Contract-first:** os schemas Pydantic geram automaticamente os contratos **OpenAPI 3.1**;
  nada entra ou sai sem validação de tipos/formatos.
- **Padronização de respostas:** listagens usam o envelope **`SearchSet`** (paginação `_count`/`_offset`
  + links HATEOAS) e cada recurso carrega a chave **`resourceType`**.

## 3. Modelo de Dados — Schema SIGAA (do professor)

O ponto central desta versão: o projeto **adota nativamente o schema SIGAA** fornecido pelo
professor (`professor_material/database/`). As tabelas são as `sigaa_*` com **chaves naturais de
negócio**:

| Conceito | Chave (exemplo) |
|----------|-----------------|
| Aluno | matrícula `'180012345'` |
| Curso | `'6351'` (Eng. de Redes de Comunicação) |
| Disciplina | `'CIC0007'` |
| Unidade Organizacional | `'CIC'` |
| Currículo | `'6351/2'` |

**Benefício:** como as tabelas do projeto **são** as tabelas SIGAA, o **DML do professor é carregado
verbatim** (sem transformação/ETL). No boot do container o `docker-compose` roda
`alembic upgrade head → python -m scripts.seed → uvicorn`, populando **433 registros** de forma
idempotente e perene (14 unidades, 2 cursos, 8 currículos, 79 disciplinas, 95 pré-requisitos,
20 alunos etc.).

## 4. Serviços Implementados

**Serviços de Entidade (CRUD/consulta):** Aluno, Curso, Disciplina, Currículo, Turma,
Unidade Organizacional e Histórico Acadêmico — base paths `/api/<Recurso>`.

**Serviço de Tarefa:** `verificarElegibilidade` em `/api/Tarefa/verificar-elegibilidade` (§5.2).

**Processamento de Matrícula:** pedidos em lote, processamento batch (Fases 3 e 5),
matrícula extraordinária, comprovante e trilha de auditoria — sob `/api/Matricula`.

### Regras de negócio (§7)
- **Elegibilidade (§7.1):** a disciplina pertence ao currículo do aluno; o aluno ainda não foi
  aprovado nela (menção `SS`/`MS`/`MM`); possui todos os pré-requisitos.
- **Processamento batch (§7.2–7.4):** ordena os pedidos elegíveis por **IRA desc → data de registro
  asc → desempate aleatório** e rejeita por carga horária máxima do período, disciplina duplicada,
  conflito de horário ou falta de vagas — gravando o **código de status** (`MAT`, `NEL`, `CEX`, `JMD`,
  `CON`, `FUL`) e a trilha em `sigaa_matricula_historico`.
- **Extraordinária (§7.5):** processamento imediato, sem concorrência por prioridade.

## 5. Segurança e Governança

- **Sem autenticação/RBAC nesta entrega**, conforme orientação do professor (endpoints abertos).
- **Governança via Kong Gateway** (DB-less): proxy reverso para a API e **rate limiting**
  (100 req/min). Proxy na **porta 80** do host; admin na 8001.
- Validação forte de entrada (Pydantic), tratamento de erros padronizado (Modelo Canônico de Erro)
  e contratos versionados.

## 6. Infraestrutura

- **Docker Compose** sobe tudo com um comando: PostgreSQL 16, API (FastAPI/Uvicorn) e Kong.
- O professor **não precisa** instalar Python nem PostgreSQL — o ambiente é isolado e reproduzível.

## 7. Como Demonstrar (passo a passo)

> Todos os dados abaixo **já vêm carregados** do DML do professor — não é preciso cadastrar nada
> para demonstrar as consultas.

1. **Subir o ambiente** (mostra portabilidade):
   ```bash
   docker compose up --build -d
   docker compose logs api   # mostra: alembic upgrade → seed (433 INSERTs) → uvicorn
   ```

2. **Abrir o Swagger:** <http://localhost:8000/docs> — documentação OpenAPI 3.1 gerada dos contratos.
   *(Sem tela de login: a entrega não usa autenticação.)*

3. **Serviços de Entidade (consultas sobre os dados reais):**
   - `GET /api/UnidadeOrganizacional/` → 14 unidades (SearchSet).
   - `GET /api/Curso/6351` → Engenharia de Redes de Comunicação, unidade `ENE`.
   - `GET /api/Aluno/180012345` → **ADA LOVELACE**, curso 6351, IRA 4.76, ingresso 2018/2.
   - `GET /api/Disciplina/?nome=redes` → filtro por nome.
   - `GET /api/Curriculo/63512/disciplinas` → componentes do currículo `6351/2`.

4. **Serviço de Tarefa — verificarElegibilidade (§7.1):**
   - `POST /api/Tarefa/verificar-elegibilidade` com `{"aluno":"180012345","disciplina":"<código do currículo>"}`
     → `elegivel: true`.
   - Repita com uma disciplina fora do currículo → `elegivel: false` com o motivo.

5. **Fluxo de Matrícula (§7.2–7.4):**
   - `POST /api/Turma/` cria uma turma (período `20182`, uma disciplina do currículo, `vagas`).
   - `POST /api/Matricula/` envia o pedido em **lote** (status inicial `PND`).
   - `POST /api/Matricula/processamento/fase-3` com `{"periodo_letivo":"20182"}`
     → resumo `{aprovadas, rejeitadas}`; o pedido vira `MAT`.
   - `GET /api/Matricula/alunos/180012345/comprovante-matricula?periodoLetivo=20182` → comprovante.
   - `GET /api/Matricula/alunos/180012345/historico-processamento` → trilha de auditoria.

6. **Governança (Kong):** repita qualquer chamada via gateway em <http://localhost/> (ex.:
   <http://localhost/docs>) para mostrar o proxy e o rate limiting.

## 8. Conclusões

O sistema demonstra os princípios de SOA sobre o **modelo de dados oficial do professor (SIGAA)**:
contratos OpenAPI padronizados por serviço, separação entre serviços de entidade e de tarefa,
o motor de elegibilidade e o processamento batch de matrículas — tudo validado de ponta a ponta em
**PostgreSQL via Docker** e acessível também pelo **gateway Kong**.

> Contratos por serviço em `docs/openapi/*.yml` (OpenAPI 3.1, validados) e o consolidado em
> `docs/openapi/openapi_sigaa.v1.json`. Detalhes da migração em `docs/RELATORIO_MIGRACAO_SIGAA.md`.
