# Relatório — Migração para o Schema SIGAA e Carga de Dados do Professor

> **Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018) — UnB
> **Professor:** Ricardo Staciarini Puttini
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
> **Data:** 2026-07-06

## 1. Objetivo

Analisar a compatibilidade dos scripts de banco de dados do projeto com os scripts SIGAA
disponibilizados pelo professor em `professor_material/database/`, corrigir as divergências e
carregar a massa de dados do professor de forma perene no banco do projeto.

## 2. Arquivos analisados

**Professor (`professor_material/database/`):**
- `SIGAA-CreateDB.sql` — role/database `SIGAA`
- `SIGAA-DDL - novo.sql` — DDL de 17 tabelas + DML de horários e status
- `SIGAA-DML-DisciplinaCurso - novo.sql` — 325 INSERTs (unidade, curso, currículo, disciplina, pré-req)
- `SIGAA-DatabaseDML_Alunos - novo.sql` — 40 INSERTs (20 alunos + 20 vínculos)
- `SIGAA-API.sql` — consultas dos data services WSO2 (referência de contrato)

**Projeto (antes da migração):** 8 migrations Alembic + 17 tabelas ORM (`alunos`, `cursos`,
`disciplinas`, `periodos_letivos`, `turmas`, `curriculos`, `matriculas`, `usuarios`, `docentes`, …).

## 3. Incompatibilidades encontradas (diagnóstico)

O schema do projeto e o schema SIGAA eram **dois modelos de dados diferentes** para o mesmo
domínio — a carga direta do DML era impossível:

| Dimensão | Projeto (antigo) | SIGAA (professor) |
|----------|------------------|-------------------|
| Nomenclatura | `snake_case` (`alunos`) | `sigaa_*` (`SIGAA_ALUNO`) |
| Chaves primárias | `serial` inteiro (surrogate) | naturais em texto (matrícula, `'6351'`, `'CIC0007'`, `'6351/2'`) |
| Relacionamentos | FKs diretas | tabelas de ligação M:N (`RL_*`) |
| Período letivo | tabela `periodos_letivos` | `varchar(5)` inline (`'20182'`) |
| Horário | string `horario_serializado` | tabela normalizada `SIGAA_TURMA_HORARIOAULA` |
| Status de matrícula | enum Python | tabela lookup `SIGAA_MATRICULA_STATUS` |
| Matrícula | 2 tabelas (solicitação + matrícula) | 1 tabela diferenciada por status |
| Colunas NOT NULL | exigia `email`, `data_admissao`, `creditos`, … | ausentes no DML do professor |

**Conclusão do diagnóstico:** nenhum ajuste no script do professor o tornaria carregável nas tabelas
antigas; a correção teria de ser no schema do projeto. O usuário optou por **refatorar o projeto para
adotar nativamente o schema SIGAA** (fidelidade máxima; sem fabricar dados).

## 4. Ajustes realizados

### 4.1 Modelagem (ORM) — Fase A
- Reescritos todos os `orm_models.py` para as 17 tabelas `sigaa_*`, com chaves naturais de texto,
  tabelas de ligação M:N e tipos fiéis ao DDL (`Numeric`, `varchar`, `serial`).
- **Removidos:** entidade `PeriodoLetivo` (período virou texto), módulos `docentes`/`turma_docentes`
  (SIGAA não tem docente — coordenador é texto em `sigaa_curso`).
- **Removida toda a autenticação/RBAC** (por orientação do professor): `app/api/auth.py`,
  `app/api/deps.py`, `app/core/security.py` e o módulo `usuarios`.
- `migrations/env.py` atualizado.

### 4.2 Migrations (Alembic) — Fase B
- Descartadas as 8 migrations antigas; criado **baseline único** `baseline_sigaa_schema`
  (`migrations/versions/a4cb4bb91965_*.py`) que gera exatamente as 17 tabelas SIGAA.
- Validado `alembic upgrade head` (17 tabelas criadas).

### 4.3 Carga de dados (seed) — Fase C
- `scripts/seed.py` reescrito para executar o **DML do professor verbatim**, na ordem de FK,
  de forma **idempotente** (se `sigaa_unidade` já tem dados, não recarrega).
- Ligado ao boot do container: o `docker-compose.yml` agora roda
  `alembic upgrade head && python -m scripts.seed && uvicorn …` — carga **perene** a cada subida.

### 4.4 Aplicação (schemas/services/routers) — Fase D
- Reescritos schemas Pydantic, services e routers de todos os módulos para as chaves SIGAA.
- `verificarElegibilidade` reimplementado sobre o modelo SIGAA (currículo, aprovação por menção,
  pré-requisitos). Processamento batch (Fases 3/5) e extraordinária adaptados: status por código
  (`MAT`/`NEL`/`CEX`/`JMD`/`CON`/`FUL`), auditoria em `sigaa_matricula_historico`, limite de
  "créditos" mapeado para a carga horária máxima do período do currículo.

### 4.5 Testes, contratos e docs — Fase E
- `tests/conftest.py` reescrito (SQLite + carga dos dados do professor); testes obsoletos removidos;
  novo `tests/test_sigaa_api.py` (7 testes) exercitando entidades e elegibilidade.
- OpenAPI atual exportado para `docs/openapi/openapi_sigaa.v1.json` (27 paths).
- README reescrito para o modelo SIGAA (sem auth).

## 5. Ordem de inserção respeitada (dependências de FK)

```
sigaa_turma_horarioaula, sigaa_matricula_status        (sem FK)
→ sigaa_unidade → sigaa_curso → sigaa_rl_curso_unidade
→ sigaa_curriculo → sigaa_rl_curriculo_curso
→ sigaa_disciplina → sigaa_prereq → sigaa_rl_curriculo_disciplina
→ sigaa_aluno → sigaa_rl_aluno_curso
```

## 6. Comandos executados (validação)

- `alembic revision --autogenerate` / `alembic upgrade head` → 17 tabelas criadas
- Carga dos **433 INSERTs** do professor com FK ativado → **0 erros**
- `python -m scripts.seed` (2×) → 1ª carrega, 2ª detecta base populada (idempotência)
- `pytest` → **7 passed**
- Smoke test via TestClient contra os dados reais → endpoints e elegibilidade OK

## 7. Status final da carga

| Tabela | Linhas |
|--------|-------:|
| sigaa_unidade | 14 |
| sigaa_curso | 2 |
| sigaa_curriculo | 8 |
| sigaa_disciplina | 79 |
| sigaa_prereq | 95 |
| sigaa_rl_curriculo_disciplina | 117 |
| sigaa_turma_horarioaula | 54 |
| sigaa_matricula_status | 14 |
| sigaa_aluno | 20 |
| sigaa_rl_aluno_curso | 20 |

**Carregado com sucesso e verbatim** (validado em SQLite com FK on e via aplicação).

## 8. Pendências e recomendações

1. **Validar no PostgreSQL 16 (Docker).** A validação de carga foi feita em SQLite porque o daemon
   do Docker estava parado. Recomenda-se subir `docker compose up --build` e confirmar. Ponto de
   atenção único: `sigaa_turma_horarioaula.id` é `varchar(3)` no DDL do professor, mas o DML insere
   literais inteiros (`208`). Em SQLite passa (tipagem tolerante); no PostgreSQL, caso rejeite a
   conversão implícita `integer→varchar`, a correção mínima é citar os valores no seed
   (`'208'`) — sem alterar o schema. A carga roda em transação única (atômica/segura).
2. **`professor_material/`** precisa estar versionado/presente para o seed encontrar os `.sql`.
3. **Dependências de auth** (`python-jose`, `passlib`, `python-multipart`) removidas do
   `requirements.txt`; conferir se o `pyproject.toml`/lock precisam do mesmo ajuste antes de gerar
   nova imagem por Poetry.
4. **Kong (`docker/kong/kong.yml`)** ainda referencia as rotas — revisar as políticas do gateway.
