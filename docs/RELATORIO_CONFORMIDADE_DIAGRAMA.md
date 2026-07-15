# Relatório — Conformidade entre o Modelo de Entidades e a Implementação

> **Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018) — UnB
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
> **Data:** 2026-07-14
> **Fonte de referência:** `docs/diagrams/Modelo de Entidades.png` (modelo conceitual)
> **Alvos verificados:** ORM (`app/modules/*/infrastructure/orm_models.py`), schemas
> (`app/modules/*/api/schemas.py`) e contratos OpenAPI (`docs/openapi/*.json` e `*.yml`).

## 1. Contexto e conclusão executiva

O diagrama em `docs/diagrams/` é o **modelo conceitual original** do projeto. Posteriormente o
projeto foi **deliberadamente migrado para o schema físico SIGAA** do professor (ver
`docs/RELATORIO_MIGRACAO_SIGAA.md`), mas **o diagrama não foi atualizado**. Consequentemente, ele
está globalmente dessincronizado do código e dos contratos.

As divergências se classificam em dois grupos:

- **Grupo A — Intencionais/documentadas:** consequência direta da migração SIGAA (renomeações,
  entidades transformadas em texto/varchar, tabelas de ligação M:N). Não são defeitos.
- **Grupo B — Lacunas reais:** campos do diagrama que desapareceram sem contrapartida ou foram
  deslocados de entidade. **São os pontos que exigem decisão da equipe.**

> Nota: no schema SIGAA os campos usam `snake_case` e chaves naturais em texto; no diagrama usam
> `camelCase` e surrogate keys. Renomeações de estilo não são listadas como defeito por si só.

## 2. Grupo B — Desconformidades que exigem decisão

| # | Entidade | Campo no diagrama | Situação atual | Severidade |
|---|----------|-------------------|----------------|------------|
| B1 | Matricula | `motivoIndeferimento : string` | **Ausente** em ORM, schema e contratos. Não há onde registrar o motivo da rejeição de um pedido | 🔴 Alta |
| B2 | Curso | `sede : string` | **Removido de Curso**; um campo `sede` aparece agora em **Turma**. Campo deslocado de entidade | 🔴 Alta |
| B3 | Turma | `vagasOfertadas` + `vagasPreenchidas` | Colapsados em um único `vagas`. **`vagasPreenchidas` inexiste** → sem controle de ocupação/lotação | 🔴 Alta |
| B4 | Turma | `status : string` | **Ausente**. Status só existe em Matrícula | 🔴 Alta |
| B5 | Disciplina (CargaHoraria) | `extensionista : int` | ORM tem apenas `carga_horaria_teorica`/`_pratica`. **`extensionista` inexiste** | 🟠 Média |
| B6 | Disciplina | `cargaHorariaPresencial` × `cargaHorariaEad` | O diagrama prevê dois blocos de carga horária (presencial e EAD); a impl tem só um par teórica/prática, sem essa distinção | 🟠 Média |
| B7 | Curriculo | `dataValidade : string` | **Ausente** no ORM/schema | 🟠 Média |
| B8 | Curriculo (CargaHoraria) | `obrigatoriaAula`, `obrigatoriaOrientacao`, `minimaPeriodo` | Sem contrapartida. A impl mapeia só um subconjunto das 8 cargas horárias do diagrama | 🟠 Média |
| B9 | HistoricoAcademico (Disciplina cursada) | `frequencia : int`, `status : string` | `HistoricoDisciplina` tem apenas `mencao` (+ `periodo_letivo`). **`frequencia` e `status` faltam** | 🟠 Média |

## 3. Grupo A — Divergências intencionais (documentadas na migração SIGAA)

| Diagrama | Implementação | Natureza |
|----------|---------------|----------|
| `Curso.grau` | `grau_academico` | Renomeação |
| `Aluno.periodoIngresso` | `periodo_letivo_registro` (em `AlunoCurso`) | Renome + movido para o vínculo aluno-curso |
| `CurriculoDisciplina.nivel` | `periodo` | Renomeação |
| `Turma.vagasOfertadas` | `vagas` | Renomeação (ver também B3) |
| `Horario.hora` | `hora_inicio` + `hora_fim` | Maior granularidade |
| Entidade **PeriodoLetivo** (`ano`, `periodo`) | `varchar(5)` inline (`'20182'`) | Entidade removida (SIGAA) |
| Entidade **Docente** (`matricula`, `nome`) | texto `coordenador` em `sigaa_curso` | Entidade removida (SIGAA) |
| Entidade **Local** | — | Removida |
| **HistoricoAcademico** consolidado (`cargaHorariaIntegralizada`, `cargaHorariaPendente`, `status`) | Conjunto de linhas de `sigaa_rl_aluno_curso_disciplina` | Entidade dissolvida; os 3 campos consolidados não existem |
| Entidade **Prazo** (`minimo`/`medio`/`maximo`) | `min_periodos` / `num_periodos` / `max_periodos` no Currículo | Achatada no Currículo |
| Chaves surrogate + FKs diretas | Chaves naturais de texto + tabelas de ligação `RL_*` | Migração SIGAA |

## 4. Desconformidades nos contratos OpenAPI (independentes do diagrama) — ✅ RESOLVIDO

> **Status:** Corrigido e validado em 2026-07-14 (execução local com Docker + PostgreSQL 16).

| # | Arquivo | Problema original | Correção aplicada | Status |
|---|---------|-------------------|-------------------|--------|
| C1 | `docs/openapi/openapi_sigaa.v1.json` | **Desatualizado:** não continha o campo `carga_horaria` (total) de Disciplina | **Reexportado de dentro do container** (fiel ao app em execução); `carga_horaria` presente em `DisciplinaCreate` e `DisciplinaResponse` | ✅ |
| C2 | `docs/openapi/disciplina_api.v1.yml` | Também não incluía `carga_horaria` (só teórica/prática) | Campo `carga_horaria` adicionado aos dois schemas, no mesmo estilo dos demais | ✅ |

### 4.1 Evidências de validação

- **Contrato ao vivo × commitado:** `GET /api/v1/openapi.json` do container é **idêntico** ao
  `openapi_sigaa.v1.json` versionado (comparação semântica). A reexportação a partir do container
  eliminou campos espúrios (`input`/`ctx` no `ValidationError`) que uma versão local mais nova do
  FastAPI/Pydantic injetava e que **não existem no app implantado**.
- **Validador de contratos** (`scripts/validate_contracts.py`, com PyYAML no container):
  **26 arquivos válidos, 0 erros** — incluindo o `disciplina_api.v1.yml` alterado.
- **Round-trip funcional:** `POST /api/Disciplina/` com `carga_horaria` → `201`; `GET /{id}` devolve
  o valor persistido. A view de detalhe expõe também `cargaHorariaTotal` (camelCase), alinhada ao
  nome do diagrama.
- **Suíte de testes:** `pytest` → **8 passed** (inclui `test_disciplina_carga_horaria_persistida`
  e `test_disciplina_detalhe_carga_total`). Um erro de sintaxe pré-existente em
  `tests/test_sigaa_api.py` (linha órfã) foi corrigido para destravar a coleta.

> Os demais `.yml` por serviço permanecem **coerentes com o código SIGAA atual** (ex.: `turma` tem
> `sede`/`vagas`; `curso` não tem `sede`; `matricula` não tem `motivoIndeferimento`). Ou seja, os
> contratos refletem a implementação, e não o diagrama.

## 5. Recomendações

1. **Definir a fonte da verdade.** Como o código já adota o schema SIGAA por decisão de projeto,
   o caminho de menor risco é **atualizar o diagrama de entidades** para refletir a implementação
   (Grupo A deixa de ser divergência).
2. **Avaliar caso a caso os itens do Grupo B.** Verificar se cada campo ausente tem cobertura no
   DDL/DML do professor (`professor_material/database/`). Se não existir no SIGAA, o campo deve ser
   **removido do diagrama**; se for requisito funcional (ex.: `motivoIndeferimento`,
   `vagasPreenchidas`, `status` de Turma), deve ser **implementado**.
3. ~~**Reexportar os contratos** (C1/C2) após consolidar as colunas de Disciplina.~~
   ✅ **Concluído** (ver Seção 4). Recomenda-se reexportar sempre a partir do container/app implantado
   para evitar divergências de versão de bibliotecas.

## 6. Metodologia

Comparação campo a campo entre: os atributos das entidades do diagrama; as colunas dos
`orm_models.py`; os campos dos `schemas.py` (Pydantic); e os `components/schemas` dos contratos
OpenAPI (`openapi_sigaa.v1.json` e os `*_api.v1.yml`). Renomeações de estilo (`camelCase` →
`snake_case`) foram consideradas conformes; ausências e deslocamentos de campo foram classificados
como desconformidade.