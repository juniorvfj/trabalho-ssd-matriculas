# Modelo de Domínio — Matrícula (schema SIGAA)

O projeto adota **nativamente o schema SIGAA** fornecido pelo professor
(`professor_material/database/`). As tabelas são as `sigaa_*`, com **chaves naturais de negócio**
(texto), não surrogate keys inteiras. Abaixo, as entidades e seus relacionamentos.

## Entidades e Relacionamentos

1. **Unidade Organizacional** (`sigaa_unidade`)
   - `id` (varchar(3), PK natural — ex.: `'CIC'`), `nome`.
   - Uma unidade oferece várias disciplinas.

2. **Curso** (`sigaa_curso`)
   - `id` (varchar(4), PK — ex.: `'6351'`), `nome`, `grau_academico`, `turno`, `modalidade`,
     `coordenador` (nome em texto — no SIGAA não há entidade Docente).
   - Vínculo M:N com Unidade via `sigaa_rl_curso_unidade`.

3. **Disciplina** (`sigaa_disciplina`)
   - `id` (varchar(7), PK — ex.: `'CIC0007'`), `nome`, `modalidade`,
     `carga_horaria_teorica`, `carga_horaria_pratica`, `unidade` (FK → `sigaa_unidade`).
   - Pré-requisitos em `sigaa_prereq` (PK composta: `disciplina_requer`, `disciplina_requerido`).

4. **Currículo / Estrutura Curricular** (`sigaa_curriculo`)
   - `id` (varchar(7), PK — ex.: `'6351/2'`), `status`, `periodo_letivo_vigor` (varchar(5)),
     cargas horárias (mínima total, obrigatória, optativa, máxima por período…) e
     quantidade de períodos (num/min/max).
   - M:N com Curso (`sigaa_rl_curriculo_curso`) e com Disciplina
     (`sigaa_rl_curriculo_disciplina`, com `periodo` e `tipo` = `OBR`/`OPT`).

5. **Turma** (`sigaa_turma`)
   - `id` (serial, PK), `codigo`, `periodo_letivo` (varchar(5) inline — ex.: `'20182'`),
     `disciplina` (FK), `vagas`, `sede`.
   - Horário normalizado em `sigaa_turma_horarioaula` (slot dia/hora), associado por
     `sigaa_rl_turma_horarioaula`.

6. **Aluno** (`sigaa_aluno`) e **Vínculo Aluno-Curso** (`sigaa_rl_aluno_curso`)
   - Aluno: `matricula` (varchar(9), PK), `nome`.
   - Vínculo: `id` (serial), `aluno` (FK), `curso` (FK), `curriculo` (FK), `data_registro`,
     `periodo_letivo_registro` (período de ingresso), `status`, `ira`.
   - O **IRA e o período de ingresso** ficam no vínculo, não no aluno.

7. **Histórico Acadêmico** (`sigaa_rl_aluno_curso_disciplina`)
   - PK composta (`aluno_curso`, `disciplina`, `periodo_letivo`), `mencao`.
   - Não há tabela "histórico consolidado": o histórico é o conjunto dessas linhas.

8. **Matrícula** (`sigaa_matricula`) e **Trilha** (`sigaa_matricula_historico`)
   - Matrícula única diferenciada por **código de status** (`sigaa_matricula_status`):
     `PND` (pedido), `MAT` (matriculado), `NEL`, `CEX`, `JMD`, `CON`, `FUL`, etc.
   - Referencia o **vínculo aluno-curso** e a turma. As transições de estado são gravadas em
     `sigaa_matricula_historico` (auditoria do processamento).

## Regras Core de Negócio

**Elegibilidade (§7.1)** — uma disciplina é elegível quando:
- pertence ao **currículo** do vínculo do aluno (`sigaa_rl_curriculo_disciplina`);
- o aluno **ainda não foi aprovado** nela (menção `SS`/`MS`/`MM` em `sigaa_rl_aluno_curso_disciplina`);
- o aluno possui **todos os pré-requisitos** (`sigaa_prereq`).

**Processamento batch (§7.2–7.4)** — pedidos (`PND`) elegíveis são ordenados por
**IRA desc → data de registro asc → desempate aleatório** e rejeitados por:
- exceder a **carga horária máxima do período** do currículo (limite de créditos);
- **disciplina duplicada** no período;
- **conflito de horário** (interseção dos slots das turmas);
- **falta de vagas**.

**Matrícula extraordinária (§7.5)** — processamento imediato, sem concorrência por prioridade.
