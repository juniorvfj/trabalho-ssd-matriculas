# Modelos canônicos — Entrega 1 (artefatos históricos)

> ⚠️ **Estes arquivos NÃO descrevem o sistema atual.** Estão preservados apenas como registro
> da primeira entrega, na mesma convenção de `docs/openapi/entrega1/`.

## Por quê

Estes JSON Schemas foram escritos antes da **migração para o schema SIGAA** do professor
(ver `docs/RELATORIO_MIGRACAO_SIGAA.md`, 2026-07-06). A migração reescreveu ORM, schemas Pydantic,
services, routers e os contratos OpenAPI — mas esta pasta não foi atualizada na época.

Como descrevem o **modelo antigo**, foram movidos para cá em 2026-07-15 em vez de atualizados,
para não passarem por documentação vigente. Marcas do modelo antigo presentes aqui:

| Marca | Realidade no SIGAA |
|-------|--------------------|
| `*_id : integer` (surrogate keys) | chaves naturais em texto (`'6351'`, `'CIC0007'`, `'6351/2'`, matrícula) |
| `periodo_letivo_id` (entidade) | `varchar(5)` inline (ex.: `'20182'`) |
| `turma.horario_serializado` | tabela normalizada `SIGAA_TURMA_HORARIOAULA` |
| `matricula.status` = `ATIVA`/`CANCELADA`/`TRANCADA` | domínio `SIGAA_MATRICULA_STATUS` com 14 códigos de 3 letras (`PND`, `MAT`, `NEL`, …) |
| `historico_academico` consolidado, `frequencia` | não existem: o histórico é o conjunto de linhas de `SIGAA_RL_ALUNO_CURSO_DISCIPLINA`, que só tem `MENCAO` |
| `curriculo.data_validade`, `obrigatoria_aula`, `obrigatoria_orientacao`, `minima_periodo` | não existem em `SIGAA_CURRICULO` |
| `docente.v1.json` | entidade **removida** — no SIGAA o coordenador é um texto em `SIGAA_CURSO` |
| `usuario.v1.json` | autenticação/RBAC **removida** por orientação do professor |
| `ativa` / `ativo` / `creditos` / `email` | colunas inexistentes no DDL do professor |

Ver a análise campo a campo em `docs/RELATORIO_CONFORMIDADE_DIAGRAMA.md` (Seção 2).

## O que continua vigente

Permanecem em `docs/schemas/` apenas os modelos ainda fiéis à implementação:

- `erro_api.v1.json` — corresponde a `app/core/exceptions.py` (`code`, `message`, `details`)
- `elegibilidade_resultado.v1.json` — corresponde a `ElegibilidadeResponse` (`elegivel`, `motivos`, `detalhes`)

Os contratos de API vigentes são os de `docs/openapi/` (o `openapi_sigaa.v1.json` é exportado do
app em execução).
