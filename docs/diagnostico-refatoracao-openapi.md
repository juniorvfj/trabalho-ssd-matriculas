# Diagnóstico de Refatoração OpenAPI

## Status do Git
- **Branch original identificada:** `main`
- **Branch de trabalho criada:** `refatoracao-openapi-professor`
- **Status inicial do Git:** Não havia alterações tracked pendentes (apenas a pasta `professor_material/` como untracked). Criada branch nova com sucesso.

## Arquivos OpenAPI Existentes Hoje
Foram identificados 11 arquivos na pasta `docs/openapi/`, sendo os principais para esta refatoração:
- `aluno_api.v1.yml`
- `historico_api.v1.yml`
- `matricula_api.v1.yml`

## Endpoints Existentes Hoje
- **Alunos:** `GET /api/v1/alunos`, `GET /api/v1/alunos/{id}`
- **Histórico Acadêmico:** `GET /api/v1/historicos/`, `POST /api/v1/historicos/`, `GET /api/v1/historicos/{aluno_id}`, `POST /api/v1/historicos/{aluno_id}/disciplinas`
- **Matrículas:** `GET /api/v1/matriculas/`, `GET /api/v1/matriculas/{id}`, `DELETE /api/v1/matriculas/{id}`, `GET /api/v1/matriculas/solicitacoes`, `POST /api/v1/matriculas/solicitacoes`

## Diferenças Principais em Relação ao Material do Professor
1. **Base Paths:** O prefixo atual `/api/v1/` e as rotas no plural mudarão para `/api/Aluno`, `/api/HistoricoAcademico` e `/api/Matricula`.
2. **Matrícula - Search:** Passa a ter o parâmetro `periodoLetivo` como obrigatório e a necessidade de incluir `aluno` ou `turma`.
3. **Matrícula - Create:** O POST de matrícula (`/api/Matricula`) passará a receber um array de itens. As referências para `aluno` e `turma` devem ser objetos contendo apenas o campo `id`.
4. **Matrícula - Patch:** Em vez de usar DELETE, a alteração de status/motivo_indeferimento usará PATCH com formato JSON Patch ou array de objetos especificando as operações.
5. **Histórico Acadêmico:** Necessário adaptar a listagem de disciplinas do histórico para a nova rota `/api/HistoricoAcademico/{id}/disciplina`.
6. **Schemas e Estruturas:** Padrões de retorno (`SearchSet`, referências `_Short`, hierarquias de herança) serão ajustados aos YAMLs originais do professor, consolidando definições sem duplicação.

## Arquivos que Precisarão ser Modificados
- **Docs:** Substituição dos YAMLs de Aluno, Histórico e Matrícula na pasta `docs/openapi`.
- **Rotas:** `app/api/routers/aluno_router.py`, `app/api/routers/historico_router.py`, `app/api/routers/matricula_router.py` (e remoção das versões incompatíveis).
- **Schemas:** `app/schemas/aluno_schema.py`, `app/schemas/historico_schema.py`, `app/schemas/matricula_schema.py` (inclusão de `Matricula_Create`, `Matricula_Patch`, etc.).
- **Serviços:** Validações de negócio no `app/services/matricula_service.py` (regras do search, criação via array e patch restrito).
- **Main:** Registros de APIRouter em `app/main.py`.
