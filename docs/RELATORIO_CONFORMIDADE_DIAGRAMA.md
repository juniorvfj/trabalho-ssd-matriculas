# Relatório — Conformidade entre o Modelo de Entidades e a Implementação

> **Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018) — UnB
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
> **Data:** 2026-07-14 (Seção 2 revisada em 2026-07-15)
> **Fonte da verdade:** `professor_material/database/` — o DDL/DML do professor, que cria e carrega
> o PostgreSQL do container. O diagrama `docs/diagrams/Modelo de Entidades` é o modelo **conceitual**.
> **Alvos verificados:** ORM (`app/modules/*/infrastructure/orm_models.py`), schemas
> (`app/modules/*/api/schemas.py`) e contratos OpenAPI (`docs/openapi/*.json` e `*.yml`).

## 1. Contexto e conclusão executiva

Este relatório nasceu comparando a implementação com o **diagrama**. Essa premissa estava errada:
a fonte da verdade são os **scripts do professor**. Reavaliada a Seção 2 contra o
`SIGAA-DDL - novo.sql`, a conclusão se inverteu — na maior parte dos casos **o diagrama é que
diverge do SIGAA**, não o código.

### 1.1 O padrão de projeto do professor (chave de leitura)

O arquivo `professor_material/database/SIGAA-API.sql` (consultas dos data services WSO2) mostra que
o professor **separa deliberadamente** as duas camadas:

- **Banco** = schema físico SIGAA (normalizado, códigos, `varchar` inline);
- **API** = modelo conceitual do diagrama, **derivado** do banco em tempo de consulta.

Evidências no próprio SQL do professor:

| No `SIGAA-API.sql` | Efeito |
|--------------------|--------|
| `CARGA_HORARIA_TEORICA + CARGA_HORARIA_PRATICA as CARGA_HORARIA_TOTAL` | `cargaHorariaTotal` do diagrama é **derivado**, não é coluna |
| `substring(PERIODO_LETIVO_REGISTRO ...) as PERIODO_INGRESSO_ANO / _NUMERO` | a entidade `PeriodoLetivo (ano, periodo)` é **derivada** do `varchar(5)` |
| `case when TIPO = 'OBR' then 'Obrigatória'` | o código armazenado vira **rótulo legível** na API |
| `where (srcd.PERIODO = :nivel ...)` | a coluna `PERIODO` é exposta como **`nivel`** |

**Conclusão:** o diagrama **não** está obsoleto — ele é o contrato conceitual da API. A pergunta
correta para cada item não é *"existe como coluna?"*, e sim ***"é derivável do schema do professor?"***

## 2. Grupo B — Reavaliado contra o DDL do professor

### 2.1 Itens derivávies → **implementados** (sem alterar o banco)

| # | Campo do diagrama | Como foi resolvido | Status |
|---|-------------------|--------------------|--------|
| B1 | `Matricula.motivoIndeferimento` | Não é coluna — no SIGAA o motivo **é o próprio status**. `SIGAA_MATRICULA_STATUS` traz a descrição legível (`NEL`=Não elegível, `CEX`=Créditos excedidos, `JMD`=Já matriculado, `CON`=Conflito de horário, `FUL`=Vagas excedidas). Exposto em `/api/Matricula` apenas quando o status é de indeferimento | ✅ |
| B3 | `Turma.vagasOfertadas` + `vagasPreenchidas` | O DDL só tem `VAGAS` (= `vagasOfertadas`). `vagasPreenchidas` é **derivado** da contagem de matrículas com status `MAT` | ✅ |
| B9a | `HistoricoAcademico.status` (disciplina cursada) | Derivado da **menção**: `SS`/`MS`/`MM` → "Aprovado", demais → "Reprovado", sem menção → em curso. É a mesma regra já usada por `verificarElegibilidade` | ✅ |

### 2.2 Itens sem contrapartida no SIGAA → ~~corrigir o diagrama~~ **DECISÃO REVISTA em 2026-07-15**

> **Revisão pós-apresentação:** a banca tratou o diagrama como **contrato conceitual da API** e
> cobrou os objetos de carga horária/prazo e a herança de `Disciplina`. A ação "remover do
> diagrama" foi substituída por: **a API implementa a estrutura do diagrama** (objetos compostos e
> `allOf`/herança) e expõe como `null` os campos sem contrapartida física. O de-para completo e a
> decisão por campo estão em [`docs/mapeamento-conceitual-fisico.md`](mapeamento-conceitual-fisico.md)
> (Seção 6), que passa a prevalecer sobre a coluna "Ação" da tabela abaixo.

Os campos abaixo **não existem** no DDL do professor e **não são derivávies** de nenhuma coluna.
Implementá-los exigiria inventar colunas fora do schema do professor — o que quebraria a fidelidade
adotada como premissa do projeto. **Decisão: remover/ajustar no diagrama (Astah).**

| # | Campo do diagrama | Constatação no DDL | Ação |
|---|-------------------|--------------------|------|
| B2 | `Curso.sede` | `SIGAA_CURSO` **não tem** `SEDE`; a coluna `SEDE` existe em `SIGAA_TURMA`. **A implementação está correta** — o diagrama é que põe o campo na entidade errada | Mover `sede` de `Curso` → `Turma` no diagrama |
| B4 | `Turma.status` | Não existe em `SIGAA_TURMA` | Remover do diagrama |
| B5 | `CargaHoraria.extensionista` (Disciplina) | `SIGAA_DISCIPLINA` só tem `CARGA_HORARIA_TEORICA` e `_PRATICA` | Remover do diagrama |
| B6 | `cargaHorariaPresencial` × `cargaHorariaEad` | Não existem; há uma única coluna `MODALIDADE` | Remover a divisão do diagrama |
| B7 | `Curriculo.dataValidade` | Não existe em `SIGAA_CURRICULO` | Remover do diagrama |
| B8 | `obrigatoriaAula`, `obrigatoriaOrientacao`, `minimaPeriodo` | Não existem. O DDL tem `CARGA_HORARIA_OBR` (= `obrigatoriaTotal`) e `CARGA_HORARIA_MAX_PERIODO` (= `maximaPeriodo`) | Remover os 3 campos do diagrama |
| B9b | `HistoricoAcademico.frequencia` | `SIGAA_RL_ALUNO_CURSO_DISCIPLINA` só tem `MENCAO` | Remover do diagrama |

> **Nota sobre a coluna `carga_horaria`:** ela foi acrescentada a `SIGAA_DISCIPLINA` pelo projeto e
> **não existe** no DDL do professor. É um **exemplo didático** deliberado de evolução de schema
> ponta a ponta (branch `feature/exemplo-carga-horaria`, ver `docs/GUIA_DEMO_E_ADD_COLUNA.md`), e não
> uma desconformidade. O `cargaHorariaTotal` do diagrama continua sendo derivado (teórica + prática),
> exatamente como no `SIGAA-API.sql`.

### 2.3 Alinhamentos extras ao `SIGAA-API.sql` (fora do Grupo B original)

Identificados ao ler o contrato de referência do professor e **também implementados**:

| Ponto | Antes | Agora |
|-------|-------|-------|
| `nivel` | expúnhamos só `periodo` | expõe `nivel` (nome do professor) e aceita `?nivel=` como filtro; `periodo` mantido por compatibilidade |
| `tipo` legível | devolvíamos o código cru (`OBR`) | devolve `'Obrigatória'`/`'Optativa'` e aceita ambos no filtro; código cru em `tipoCodigo` |

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
  **26 arquivos válidos, 0 erros** — incluindo o `disciplina_api.v1.yml` alterado. *(Contagem de
  2026-07-14; passou a 11 após a reorganização de `docs/schemas/` descrita na Seção 7.1.)*
- **Round-trip funcional:** `POST /api/Disciplina/` com `carga_horaria` → `201`; `GET /{id}` devolve
  o valor persistido. A view de detalhe expõe também `cargaHorariaTotal` (camelCase), alinhada ao
  nome do diagrama.
- **Suíte de testes:** `pytest` → **8 passed** (inclui `test_disciplina_carga_horaria_persistida`
  e `test_disciplina_detalhe_carga_total`). Um erro de sintaxe pré-existente em
  `tests/test_sigaa_api.py` (linha órfã) foi corrigido para destravar a coleta.

> Os demais `.yml` por serviço permanecem **coerentes com o código SIGAA atual**. Ou seja, os
> contratos refletem a implementação.

## 5. Recomendações

1. ✅ **Fonte da verdade definida:** os scripts do professor (`professor_material/database/`).
   O diagrama é o contrato **conceitual** da API, derivado do banco — não um espelho das tabelas.
2. **Ajustar o diagrama no Astah** conforme a Seção 2.2 (7 correções). O diagrama é um binário
   (`.png`/`.pdf` exportados do Astah) e não pôde ser editado aqui; a Seção 2.2 é a lista de
   trabalho para essa correção.
3. ~~**Reexportar os contratos** (C1/C2) após consolidar as colunas de Disciplina.~~
   ✅ **Concluído** (ver Seção 4). Recomenda-se reexportar sempre a partir do container/app implantado
   para evitar divergências de versão de bibliotecas.
4. **Não adicionar colunas fora do DDL do professor.** A única exceção existente (`carga_horaria`)
   é um exemplo didático assumido e documentado.

## 6. Metodologia

Comparação campo a campo entre: os atributos das entidades do diagrama; o **DDL/DML do professor**
(`SIGAA-DDL - novo.sql`) e seu contrato de referência (`SIGAA-API.sql`); as colunas dos
`orm_models.py`; os campos dos `schemas.py` (Pydantic); e os `components/schemas` dos contratos
OpenAPI. Renomeações de estilo (`camelCase` → `snake_case`) foram consideradas conformes.

Para a Seção 2, cada campo do diagrama foi classificado por dois critérios, nesta ordem:
**(1)** existe como coluna no DDL do professor? **(2)** se não, é **derivável** de colunas existentes
(à maneira do `SIGAA-API.sql`)? Só quando ambas as respostas são "não" o campo é considerado um erro
do diagrama.

## 7. Validação da Seção 2 (2026-07-15)

Ambiente: Docker + PostgreSQL 16, com a carga real do professor.

- **`pytest` → 12 passed** (8 anteriores + 4 novos, cobrindo B1, B3, B9a e o alinhamento
  `nivel`/`tipo`).
- **Round-trip ao vivo:** turma com 40 vagas → `vagasOfertadas=40`, `vagasPreenchidas=0`; após
  efetivar uma matrícula → `vagasPreenchidas=1`. Pedido `PND` → `motivoIndeferimento: null`;
  ao mudar para `FUL` → `motivoIndeferimento: "Vagas excedidas"`.
- **Dados reais do currículo `6351/2`:** 60 componentes = **49 `Obrigatória` + 11 `Optativa`**;
  filtros `?nivel=1` (7 itens) e `?tipo=Obrigatória` funcionando, com o código cru (`OBR`) aceito
  por compatibilidade.
- **`validate_contracts.py` → 11 arquivos válidos, 0 erros.** OpenAPI reexportado do container e
  **idêntico** ao contrato ao vivo; `curriculo_api.v1.yml` atualizado com os filtros `nivel`/`tipo`.
- **Zero alteração de schema:** nenhuma migration nova; o banco continua fiel ao DDL do professor.

### 7.1 Auditoria dos artefatos de `docs/` e reorganização de `docs/schemas/`

Antes do commit, todos os `.json` e `.yml` de `docs/` foram auditados.

**Contratos de API — em dia:**
- `openapi_sigaa.v1.json` é **idêntico** ao `GET /api/v1/openapi.json` do container (comparação
  semântica).
- Os 9 `.yml` por serviço foram comparados com o app **operação a operação** (casando por
  `operationId`): **zero divergência** de operações e parâmetros. A única operação do app sem
  cobertura em `.yml` é `health_check_health_get` (endpoint de sistema, não é serviço de negócio).

**`docs/schemas/` — defasagem pré-existente, resolvida por arquivamento:**
Dos 17 "modelos canônicos" JSON Schema, **15 descreviam o modelo anterior à migração SIGAA**
(datados de abril/maio; a migração de 2026-07-06 atualizou o OpenAPI mas não esta pasta). Nenhum
`.yml` faz `$ref` para eles — eram artefatos órfãos da 1ª entrega.

Como o modelo que descrevem não existe mais, foram **movidos para `docs/schemas/entrega1/`**
(mesma convenção já usada em `docs/openapi/entrega1/`), com um `README.md` explicando o contexto —
em vez de reescritos, o que seria fabricar documentação de um modelo que a equipe não usa.

Permanecem vigentes em `docs/schemas/` apenas os 2 modelos ainda fiéis ao código:

| Arquivo | Corresponde a |
|---------|---------------|
| `erro_api.v1.json` | `app/core/exceptions.py` (`code`, `message`, `details`) |
| `elegibilidade_resultado.v1.json` | `ElegibilidadeResponse` (`elegivel`, `motivos`, `detalhes`) |

> Os campos derivados criados nesta seção (`motivoIndeferimento`, `vagasPreenchidas`, `status` do
> histórico, `nivel`, `tipo`) **não aparecem** nos contratos OpenAPI porque os endpoints que os
> devolvem não usam `response_model` — as respostas são `SearchSet` (itens livres) ou `schema: {}`.
> É o mesmo tratamento que `cargaHorariaTotal` já recebia; documentá-los exigiria criar
> `response_model` para essas rotas, o que fica registrado como possível evolução.