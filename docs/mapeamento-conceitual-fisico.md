# Mapeamento — Modelo Conceitual (diagrama) ↔ Banco Físico (SIGAA) ↔ API

> **Disciplina:** Segurança em Sistemas Distribuídos (PPEE2018) — UnB
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
> **Data:** 2026-07-15
> **Motivação:** feedback da banca (menção MS): (1) não havia um documento com o de-para entre os
> nomes do modelo conceitual (`docs/diagrams/Modelo de Entidades`) e as colunas do banco
> (`professor_material/database/`); (2) os retornos das APIs — em especial os campos de **carga
> horária** e **prazo** — não seguiam o diagrama nem os conceitos de **orientação a objetos e
> herança** dos exemplos de referência (`professor_material/*.yml`).

## 1. Como ler este documento

Cada tabela tem três colunas, uma por camada:

| Camada | Fonte | Convenção |
|--------|-------|-----------|
| **Modelo conceitual** | Diagrama de entidades (Astah) | `camelCase`, objetos compostos (`CargaHoraria`, `Prazo`, `PeriodoLetivo`), herança |
| **Banco físico** | `SIGAA-DDL - novo.sql` (DDL do professor) | Colunas planas `SNAKE_CASE`, códigos curtos, `varchar` inline |
| **API (JSON)** | Retornos dos serviços em `app/modules/*/api/` | Espelha o **modelo conceitual**, derivando os valores do banco |

A regra de projeto — extraída do próprio `SIGAA-API.sql` do professor — é: **a API expõe o modelo
conceitual; o banco permanece fiel ao DDL**. Campos do diagrama que não existem como coluna são
**derivados** em tempo de consulta (ex.: `CARGA_HORARIA_TEORICA + CARGA_HORARIA_PRATICA as
CARGA_HORARIA_TOTAL`, linha 10 do `SIGAA-API.sql`). A pergunta certa para cada campo nunca é
*"existe como coluna?"*, e sim *"é derivável do schema físico?"*.

Legenda da coluna "Banco físico / derivação":

- `TABELA.COLUNA` — mapeamento direto;
- **ƒ(...)** — campo **derivado** (a expressão está indicada);
- **∅** — não existe nem é derivável do schema físico; a API o expõe como `null`/omitido
  (ver Seção 6).

## 2. Objetos de valor (classes sem tabela própria)

O diagrama modela quatro classes de valor que **não têm tabela** no banco — elas são materializadas
pela API a partir de colunas planas. São o cerne da crítica sobre "carga horária e prazo".

### 2.1 `PeriodoLetivo { ano: int, periodo: int }`

No banco, todo período letivo é um `varchar(5)` no formato `AAAAP` (ex.: `'20182'`). A derivação é
a mesma do `SIGAA-API.sql` (linhas 54–55 e 115–116): `ano = substring(1,4)`,
`periodo = substring(5)`.

| Onde aparece no diagrama | Coluna física de origem |
|--------------------------|-------------------------|
| `Aluno.periodoIngresso` | `SIGAA_RL_ALUNO_CURSO.PERIODO_LETIVO_REGISTRO` |
| `Curriculo.periodoLetivoVigor` | `SIGAA_CURRICULO.PERIODO_LETIVO_VIGOR` |
| `Turma.periodoLetivo` | `SIGAA_TURMA.PERIODO_LETIVO` |
| `Disciplina_HistoricoAcademico.periodoLetivo` | `SIGAA_RL_ALUNO_CURSO_DISCIPLINA.PERIODO_LETIVO` |

Formato JSON (idêntico ao `PeriodoLetivo` dos YML de referência do professor):

```json
{ "ano": 2018, "periodo": 2 }
```

### 2.2 `CargaHoraria` da **Disciplina** `{ teorica, pratica, extensionista }`

O diagrama associa a Disciplina a **duas** instâncias de `CargaHoraria`
(`cargaHorariaPresencial` e `cargaHorariaEad`, ambas `0..1`). O banco tem apenas duas colunas
planas e a modalidade:

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `cargaHorariaPresencial.teorica` | `SIGAA_DISCIPLINA.CARGA_HORARIA_TEORICA` | `cargaHorariaPresencial.teorica` |
| `cargaHorariaPresencial.pratica` | `SIGAA_DISCIPLINA.CARGA_HORARIA_PRATICA` | `cargaHorariaPresencial.pratica` |
| `cargaHorariaPresencial.extensionista` | **∅** (sem coluna no DDL) | `extensionista: null` |
| `cargaHorariaEad.*` | **ƒ(MODALIDADE)** — as mesmas colunas, quando `MODALIDADE` indica EAD | `cargaHorariaEad` |

**Regra de derivação:** o objeto informado depende de `MODALIDADE` — `'Presencial'` preenche
`cargaHorariaPresencial` (e `cargaHorariaEad` fica `null`); modalidade a distância preenche
`cargaHorariaEad`. Na massa de referência do professor, **as 79 disciplinas são 'Presencial'**,
portanto `cargaHorariaEad` nunca vem preenchido com esses dados — mas o contrato o prevê, como
no diagrama (associações `0..1`).

### 2.3 `CargaHoraria` do **Currículo** `{ totalMinima, obrigatoriaAula, obrigatoriaOrientacao, obrigatoriaTotal, optativaMinima, maximaEletivos, maximaPeriodo, minimaPeriodo }`

| Conceitual (`Curriculo.cargaHoraria`) | Banco físico / derivação | API (JSON) |
|---------------------------------------|--------------------------|------------|
| `totalMinima` | `SIGAA_CURRICULO.CARGA_HORARIA_MINIMA_TOTAL` | `cargaHoraria.totalMinima` |
| `obrigatoriaTotal` | `SIGAA_CURRICULO.CARGA_HORARIA_OBR` | `cargaHoraria.obrigatoriaTotal` |
| `optativaMinima` | `SIGAA_CURRICULO.CARGA_HORARIA_MINIMA_OPT` | `cargaHoraria.optativaMinima` |
| `maximaEletivos` | `SIGAA_CURRICULO.CARGA_HORARIA_ELETIVA_MAX` | `cargaHoraria.maximaEletivos` |
| `maximaPeriodo` | `SIGAA_CURRICULO.CARGA_HORARIA_MAX_PERIODO` | `cargaHoraria.maximaPeriodo` |
| `obrigatoriaAula` | **∅** | `null` |
| `obrigatoriaOrientacao` | **∅** | `null` |
| `minimaPeriodo` | **∅** (só existe o máximo por período) | `null` |

### 2.4 `Prazo { minimo, medio, maximo }` (do Currículo)

| Conceitual (`Curriculo.prazo`) | Banco físico / derivação | API (JSON) |
|--------------------------------|--------------------------|------------|
| `minimo` | `SIGAA_CURRICULO.MIN_PERIODOS` | `prazo.minimo` |
| `medio` | `SIGAA_CURRICULO.NUM_PERIODOS` (nº de períodos previsto = prazo médio) | `prazo.medio` |
| `maximo` | `SIGAA_CURRICULO.MAX_PERIODOS` | `prazo.maximo` |

## 3. Herança (orientação a objetos)

O diagrama especializa a entidade `Disciplina` em dois contextos, e os YML de referência do
professor materializam isso em OpenAPI com **`allOf`** (herança de schema). A implementação usa
**herança de classes Pydantic** (`app/shared/schemas/`), que gera exatamente o `allOf` no contrato:

```text
Disciplina                       ← entidade base (id, codigo, nome, modalidade,
   │                               cargaHorariaTotal, cargaHorariaPresencial, cargaHorariaEad)
   ├── Disciplina_Curriculo             + tipo, nivel
   └── Disciplina_HistoricoAcademico    + mencao, frequencia, status, periodoLetivo
```

Consequência prática: a disciplina retornada dentro de um currículo ou de um histórico carrega
**todos os campos da base** (nome, modalidade, cargas horárias...) **mais** os campos da
especialização — em vez de um objeto avulso com meia dúzia de campos, como era antes.

### 3.1 `Disciplina_Curriculo` (componente curricular)

Origem: `SIGAA_RL_CURRICULO_DISCIPLINA` ⋈ `SIGAA_DISCIPLINA`.

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| *(herdados)* | colunas de `SIGAA_DISCIPLINA` (Seção 4.1) | todos os campos de `Disciplina` |
| `tipo` | **ƒ**(`RL.TIPO`): `'OBR'` → `'Obrigatória'`, `'OPT'` → `'Optativa'` (case do `SIGAA-API.sql`, l. 145–148) | `tipo` |
| `nivel` | `RL.PERIODO` (o professor expõe a coluna como `nivel`) | `nivel` |

### 3.2 `Disciplina_HistoricoAcademico` (disciplina cursada)

Origem: `SIGAA_RL_ALUNO_CURSO_DISCIPLINA` ⋈ `SIGAA_DISCIPLINA`.

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| *(herdados)* | colunas de `SIGAA_DISCIPLINA` | todos os campos de `Disciplina` |
| `mencao` | `RL.MENCAO` | `mencao` |
| `status` | **ƒ**(`MENCAO`): `SS/MS/MM` → `aprovado`; `MI/II/SR` → `reprovado`; sem menção → `cursando` (enum do `HistoricoAcademico.yml` do professor) | `status` |
| `frequencia` | **∅** (a tabela só tem a menção) | `null` |
| `periodoLetivo` | `RL.PERIODO_LETIVO` → `PeriodoLetivo` (Seção 2.1) | `periodoLetivo` |

## 4. Entidades

### 4.1 `Disciplina` ← `SIGAA_DISCIPLINA`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `codigo` | `ID` (código natural, ex.: `'CIC0007'`) | `id` e `codigo` |
| `nome` | `NOME` | `nome` |
| `modalidade` | `MODALIDADE` | `modalidade` |
| `cargaHorariaTotal` | **ƒ**: `CARGA_HORARIA_TEORICA + CARGA_HORARIA_PRATICA` (`SIGAA-API.sql`, l. 10). Exceção didática: a coluna extra `CARGA_HORARIA` (acréscimo do projeto, ver nota) prevalece quando preenchida | `cargaHorariaTotal` |
| `cargaHorariaPresencial` / `cargaHorariaEad` | Seção 2.2 | objetos aninhados |
| `unidadeOrganizacional` | `UNIDADE` ⋈ `SIGAA_UNIDADE` | `unidadeOrganizacional { id, nome }` |
| `preRequisito` (0..*) | `SIGAA_PREREQ` (auto-associação) | `preRequisito[]` (lista de `Disciplina` resumida) |

> **Nota:** a coluna `CARGA_HORARIA` não existe no DDL do professor — é o exemplo didático de
> evolução de schema desta branch (`docs/GUIA_DEMO_E_ADD_COLUNA.md`). Ela **não é mais exposta como
> campo plano**; participa apenas da derivação de `cargaHorariaTotal`.

### 4.2 `Curriculo` ← `SIGAA_CURRICULO`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `codigo` | `ID` (`'6351/2'`) — na URL e no `id` da API usa-se `'6351.2'`, a convenção do professor (`SIGAA-API.sql` l. 139 reconstrói a barra a partir do id com ponto) | `id` e `codigo` |
| `status` | **ƒ**(`STATUS`): `'A'` → `ativo`, `'I'` → `inativo` (domínio do diagrama) | `status` |
| `dataValidade` | **∅** | omitido |
| `periodoLetivoVigor` | `PERIODO_LETIVO_VIGOR` → `PeriodoLetivo` | `periodoLetivoVigor { ano, periodo }` |
| `cargaHoraria` | Seção 2.3 | `cargaHoraria { ... }` |
| `prazo` | Seção 2.4 | `prazo { minimo, medio, maximo }` |
| `disciplina` (0..*) | `SIGAA_RL_CURRICULO_DISCIPLINA` → `Disciplina_Curriculo` (Seção 3.1) | `GET /Curriculo/{id}/disciplina` |
| `curso` | `SIGAA_RL_CURRICULO_CURSO` ⋈ `SIGAA_CURSO` | `curso { id, nome }` |

### 4.3 `HistoricoAcademico` — entidade **inteiramente derivada** (sem tabela própria)

O histórico consolidado do diagrama não existe como tabela: é a agregação das linhas de
`SIGAA_RL_ALUNO_CURSO_DISCIPLINA` do vínculo (`SIGAA_RL_ALUNO_CURSO`) do aluno.

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `id` | matrícula do aluno (`SIGAA_ALUNO.MATRICULA`) | `id` |
| `cargaHorariaIntegralizada` | **ƒ**: Σ `(CARGA_HORARIA_TEORICA + CARGA_HORARIA_PRATICA)` das disciplinas do histórico com menção de aprovação (`SS/MS/MM`) | `cargaHorariaIntegralizadas` (grafia do `HistoricoAcademico.yml` do professor) |
| `cargaHorariaPendente` | **ƒ**: `CARGA_HORARIA_MINIMA_TOTAL` (do currículo do vínculo) − `cargaHorariaIntegralizadas` | `cargaHorariaPendente` |
| `status` | **ƒ**(`SIGAA_RL_ALUNO_CURSO.STATUS`): `'A'` → `ativo`, `'I'` → `inativo`, `'C'` → `concluido` | `status` |
| `aluno` | `SIGAA_ALUNO` ⋈ `SIGAA_RL_ALUNO_CURSO` | `aluno { id, matricula, nome, curso }` (padrão `Aluno_Short`) |
| `disciplina` (0..*) | Seção 3.2 | `disciplina[]` |
| `componentesPendentes` | **ƒ**: disciplinas do currículo do aluno sem aprovação no histórico | *(usado por `verificarElegibilidade`)* |

### 4.4 `Aluno` ← `SIGAA_ALUNO` (+ vínculo `SIGAA_RL_ALUNO_CURSO`)

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `matricula` | `MATRICULA` | `id` e `matricula` |
| `nome` | `NOME` | `nome` |
| `ira` | `SIGAA_RL_ALUNO_CURSO.IRA` | `ira` |
| `periodoIngresso` | `SIGAA_RL_ALUNO_CURSO.PERIODO_LETIVO_REGISTRO` → `PeriodoLetivo` | `periodoIngresso { ano, periodo }` |
| `curso` | `SIGAA_RL_ALUNO_CURSO.CURSO` ⋈ `SIGAA_CURSO` | `curso { id, nome }` |
| `curriculo` | `SIGAA_RL_ALUNO_CURSO.CURRICULO` | `curriculo` |

### 4.5 `Curso` ← `SIGAA_CURSO`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `codigo` | `ID` | `id` |
| `nome` | `NOME` | `nome` |
| `grau` | `GRAU_ACADEMICO` | `grauAcademico` |
| `turno` | `TURNO` | `turno` |
| `modalidade` | `MODALIDADE` | `modalidade` |
| `sede` | **∅** em `SIGAA_CURSO` (a coluna `SEDE` está em `SIGAA_TURMA`; o diagrama a posiciona na entidade errada — ver relatório de conformidade, item B2) | — |
| `coordenador` (→ `Docente`) | `COORDENADOR` (`varchar(100)` — o físico não tem entidade Docente; guarda só o nome) | `coordenador` |
| `unidadeOrganizacional` (0..*) | `SIGAA_RL_CURSO_UNIDADE` ⋈ `SIGAA_UNIDADE` | `unidades[]` |

### 4.6 `Turma` ← `SIGAA_TURMA`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `codigo` | `CODIGO` | `codigo` |
| `vagasOfertadas` | `VAGAS` | `vagasOfertadas` |
| `vagasPreenchidas` | **ƒ**: `count(*)` das matrículas da turma com status `'MAT'` | `vagasPreenchidas` |
| `status` | **∅** | — |
| `periodoLetivo` | `PERIODO_LETIVO` → `PeriodoLetivo` | `periodoLetivo { ano, periodo }` |
| `disciplina` | `DISCIPLINA` ⋈ `SIGAA_DISCIPLINA` | `disciplina { id, nome }` |
| `horario` (0..*) → `Horario { dia, hora }` | `SIGAA_RL_TURMA_HORARIOAULA` ⋈ `SIGAA_TURMA_HORARIOAULA` (`DIA`, `HORA_INICIO`/`HORA_FIM` — o físico é mais granular que o diagrama) | `horarios[] { dia, horaInicio, horaFim }` |
| `local` (→ `Local`) | `SEDE` (`varchar` — não há entidade Local no físico) | `sede` |

### 4.7 `Matricula` ← `SIGAA_MATRICULA`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `status` | `STATUS` (código de 3 letras) ⋈ `SIGAA_MATRICULA_STATUS` (descrição legível) | `status` + `statusDescricao` |
| `motivoIndeferimento` | **ƒ**: no SIGAA o motivo **é o próprio status** (`NEL`, `CEX`, `JMD`, `CON`, `FUL`); a descrição vem de `SIGAA_MATRICULA_STATUS` e só é exposta em status de indeferimento | `motivoIndeferimento` |
| `prioridade` | `PRIORIDADE` | `prioridade` |
| `aluno` | `ALUNO_CURSO` → `SIGAA_RL_ALUNO_CURSO` ⋈ `SIGAA_ALUNO` | `aluno`/`alunoCurso` |
| `turma` | `TURMA` ⋈ `SIGAA_TURMA` | `turma { id }` |

### 4.8 `UnidadeOrganizacional` ← `SIGAA_UNIDADE`

| Conceitual | Banco físico / derivação | API (JSON) |
|------------|--------------------------|------------|
| `codigo` | `ID` (sigla de 3 letras, ex.: `'ENE'`) | `id` |
| `nome` | `NOME` | `nome` |

### 4.9 Entidades do diagrama sem contrapartida física

| Entidade | Situação no banco | Tratamento na API |
|----------|-------------------|-------------------|
| `Docente` | Não existe; só o texto `SIGAA_CURSO.COORDENADOR` | `coordenador` como string |
| `Local` | Não existe; só `SIGAA_TURMA.SEDE` | `sede` como string |
| `PeriodoLetivo` | `varchar(5)` inline nas tabelas que o usam | derivado (Seção 2.1) |
| `CargaHoraria` / `Prazo` | colunas planas em `SIGAA_DISCIPLINA` / `SIGAA_CURRICULO` | derivados (Seções 2.2–2.4) |

## 5. Padrões transversais da API (dos YML de referência)

- **`Resource` base:** todo recurso retornado carrega `resourceType` (discriminador) e `id`,
  como no schema `Resource` dos YML do professor.
- **Variantes `_Short`:** referências entre recursos usam versões resumidas (`Aluno_Short`,
  `Curso_Short`, `Turma_Short`) — só identificação, sem os agregados.
- **`SearchSet`:** pesquisas retornam o envelope `{ total, count, offset, link, items[] }`.
- **Nomes:** a API usa exclusivamente os nomes `camelCase` do diagrama; `snake_case` cru do banco
  não vaza para o JSON.

## 6. Campos não deriváveis — decisão

Os campos abaixo constam no diagrama, mas **não existem nem são deriváveis** do DDL do professor.
A decisão anterior (relatório de conformidade, Seção 2.2) era removê-los do diagrama; após o
feedback da banca — que tratou o diagrama como contrato da API e cobrou os objetos de carga
horária/prazo — a decisão foi **revista**: a API implementa a **estrutura** do diagrama
(objetos compostos e herança) e expõe esses campos como `null`, documentando aqui a lacuna física.

| Campo | Entidade | Motivo |
|-------|----------|--------|
| `extensionista` | `CargaHoraria` (Disciplina) | `SIGAA_DISCIPLINA` só tem teórica e prática |
| `obrigatoriaAula`, `obrigatoriaOrientacao`, `minimaPeriodo` | `CargaHoraria` (Currículo) | sem colunas correspondentes |
| `frequencia` | `Disciplina_HistoricoAcademico` | a tabela de histórico só registra a menção |
| `dataValidade` | `Curriculo` | sem coluna correspondente (omitido) |
| `status` | `Turma` | sem coluna correspondente (omitido) |
| `sede` | `Curso` | a coluna existe em `SIGAA_TURMA` (item B2 do relatório) |

## 7. Referências

- `professor_material/database/SIGAA-DDL - novo.sql` — schema físico (fonte da verdade do banco);
- `professor_material/database/SIGAA-API.sql` — consultas de referência do professor (fonte da
  verdade das **derivações**);
- `professor_material/HistoricoAcademico.yml`, `Matricula.yml`, `Aluno.yml` — contratos de
  referência (fonte da verdade do **estilo OO/herança** da API);
- `docs/RELATORIO_CONFORMIDADE_DIAGRAMA.md` — análise campo a campo que precedeu este documento;
- `app/shared/schemas/` — implementação dos schemas conceituais (herança Pydantic → `allOf`).
