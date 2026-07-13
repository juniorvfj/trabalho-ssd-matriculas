# Guia de Apresentação — Demonstração das APIs e Alterações ao Vivo

> **Projeto:** Sistema de Matrícula de Alunos de Graduação (schema SIGAA)
> **Disciplina:** Segurança em Sistemas Distribuídos — UnB · **Prof.:** Ricardo Staciarini Puttini
> **Equipe:** Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
>
> Material de bolso para a defesa: como subir o ambiente, roteiro de demonstração,
> perguntas prováveis do professor com respostas e a **receita de "adicionar uma coluna
> no banco e na API"** — já implementada de verdade na branch `feature/exemplo-carga-horaria`.

---

## 1. Antes de começar (checklist de 5 minutos)

1. **Docker Desktop aberto e rodando.**
2. Na pasta do projeto:
   ```bash
   docker compose up --build -d
   docker compose ps          # os 3 conteineres devem estar "Up"/"healthy"
   docker compose logs api     # confirme: alembic upgrade -> seed (433 INSERTs) -> uvicorn
   ```
3. Abra o **Swagger**: <http://localhost:8000/docs> (e via Kong: <http://localhost/docs>).
4. Deixe abertas, em abas: Swagger, o terminal com `docker compose logs -f api`, e o VS Code no projeto.

**Se algo falhar:**
- Porta 8000/80/5432 ocupada → `docker compose down` e suba de novo, ou ajuste a porta no `docker-compose.yml`.
- API subiu antes do banco → o `depends_on: condition: service_healthy` já cobre; se necessário `docker compose restart api`.
- Quer zerar tudo (schema + dados) → `docker compose down -v` (apaga o volume) e `docker compose up --build -d`.

---

## 2. Roteiro de demonstração das APIs (8–10 min)

> Todos os dados já vêm carregados do DML do professor — não precisa cadastrar nada para as consultas.

**a) Arquitetura na prática — Swagger.** Mostre que o OpenAPI 3.1 é gerado dos schemas Pydantic
(contract-first). Aponte os grupos de tags: Aluno, Curso, Disciplina, Currículo, Turma,
Unidade Organizacional, Histórico, Tarefa (elegibilidade) e Matrícula.

**b) Serviços de Entidade (consultas sobre dados reais):**
- `GET /api/UnidadeOrganizacional/` → 14 unidades no envelope **SearchSet**.
- `GET /api/Curso/6351` → Engenharia de Redes de Comunicação (unidade ENE).
- `GET /api/Aluno/180012345` → **ADA LOVELACE**, curso 6351, currículo 6351/2, IRA 4.76, ingresso 2018/2.
- `GET /api/Disciplina/?nome=redes` → filtro por nome.
- `GET /api/Disciplina/CIC0007` → detalhe com cargas horárias (teórica, prática, total) e pré-requisitos.
- `GET /api/Curriculo/63512/disciplinas` → componentes do currículo 6351/2 (note o path `63512`, sem a barra do `6351/2`).

**c) Serviço de Tarefa — verificarElegibilidade (§7.1):**
- `POST /api/Tarefa/verificar-elegibilidade` com `{"aluno":"180012345","disciplina":"<código do currículo>"}` → `elegivel: true`.
- Repita com uma disciplina fora do currículo → `elegivel: false` + o motivo.

**d) Fluxo de Matrícula (§7.2–7.4):**
- `POST /api/Turma/` cria uma turma (período `20182`, uma disciplina do currículo, com `vagas`).
- `POST /api/Matricula/` envia o pedido em lote (status inicial `PND`).
- `POST /api/Matricula/processamento/fase-3` com `{"periodo_letivo":"20182"}` → resumo `{aprovadas, rejeitadas}`; o pedido vira `MAT`.
- `GET /api/Matricula/alunos/180012345/comprovante-matricula?periodoLetivo=20182` → comprovante.
- `GET /api/Matricula/alunos/180012345/historico-processamento` → trilha de auditoria.

**e) Governança (Kong):** repita qualquer chamada via <http://localhost/> para mostrar o proxy reverso
e o rate limiting (100 req/min).

---

## 3. Perguntas prováveis do professor (com respostas)

**"Por que monólito modular e não microsserviços?"**
Cada domínio é um módulo isolado com três camadas (`api/`, `application/`, `infrastructure/`), sem
acoplamento entre módulos além de FKs no banco. Isso entrega os benefícios de SOA (contratos claros,
separação de responsabilidades) com simplicidade de operação, e está **pronto para extrair um módulo
em microsserviço** sem reescrever regra de negócio.

**"O que é essa arquitetura em camadas?"**
- `api/` → `router.py` (rotas HTTP) + `schemas.py` (DTOs Pydantic, validação e contrato OpenAPI).
- `application/` → `services.py` (regras de negócio e consultas; não conhece HTTP).
- `infrastructure/` → `orm_models.py` (mapeamento SQLAlchemy das tabelas SIGAA).
A rota chama o service, que usa o ORM. Trocar o banco ou o transporte não contamina a regra.

**"Como vocês usam o modelo de dados que forneci?"**
Adotamos o schema SIGAA **nativamente**: as tabelas do projeto **são** as `sigaa_*` com chaves naturais.
Por isso o **DML do professor é carregado verbatim** pelo `scripts/seed.py` (sem ETL). No boot o container
roda `alembic upgrade head` → `python -m scripts.seed` → `uvicorn`, populando 433 registros de forma idempotente.

**"O que é o SearchSet e o resourceType?"**
Padronização das respostas: listagens usam o envelope `SearchSet` (paginação `_count`/`_offset` + links) e
cada recurso carrega `resourceType`, deixando as respostas autoexplicativas e consistentes entre serviços.

**"Cadê a autenticação/segurança?"**
Conforme sua orientação, esta entrega **não** implementa auth/RBAC — endpoints abertos. A camada de
**governança** fica no **Kong** (proxy + rate limiting). A segurança de entrada é feita por validação
forte no Pydantic e tratamento de erros padronizado.

**"O que é migration? Por que Alembic e não criar tabela na mão?"**
Migration é o versionamento do schema do banco: cada alteração vira um script com `upgrade()`/`downgrade()`,
aplicável de forma reproduzível em qualquer ambiente. O Alembic mantém o histórico e a ordem
(`down_revision`), garantindo que qualquer pessoa suba o banco no mesmo estado.

**"E se der problema em produção depois de uma migration?"**
Cada migration tem `downgrade()`. `alembic downgrade -1` reverte a última. Por isso a coluna nova entra
como **nullable** — não quebra os dados existentes nem o seed.

---

## 4. Receita: "Como adicionar uma coluna no banco E na API?"

> Esta é a pergunta que o professor sinalizou. Abaixo, a resposta em 6 passos, **já implementada de
> verdade** na branch `feature/exemplo-carga-horaria` como exemplo: a coluna **`carga_horaria`** (total)
> na tabela **`sigaa_disciplina`**. Os mesmos 6 passos valem para qualquer coluna em qualquer módulo.

**Regra de ouro:** o schema tem uma única fonte da verdade — o **modelo ORM**. A partir dele, a mudança
"desce" para o banco (migration) e "sobe" para a API (schema Pydantic → service → router).

### Passo 1 — ORM (a coluna existe para o código)
`app/modules/disciplinas/infrastructure/orm_models.py`, na classe `Disciplina`:
```python
# Carga horária total (nullable para não conflitar com o DML do professor)
carga_horaria = Column(Numeric(4, 0), nullable=True)
```

### Passo 2 — Migration Alembic (a coluna existe no banco)
Gera-se o script comparando o ORM com o banco:
```bash
alembic revision --autogenerate -m "add carga_horaria em sigaa_disciplina"
```
Isso cria `migrations/versions/<hash>_add_carga_horaria_disciplina.py`. Revise o conteúdo — deve conter:
```python
def upgrade() -> None:
    op.add_column("sigaa_disciplina",
                  sa.Column("carga_horaria", sa.Numeric(precision=4, scale=0), nullable=True))

def downgrade() -> None:
    op.drop_column("sigaa_disciplina", "carga_horaria")
```
Aplica no banco:
```bash
alembic upgrade head
```
> Sem Docker autogenerando? Dá para escrever o script à mão (foi o que fizemos neste exemplo): basta
> `op.add_column`/`op.drop_column` e o `down_revision` apontando para a migration anterior.

### Passo 3 — Schema Pydantic de entrada (a API aceita o campo)
`app/modules/disciplinas/api/schemas.py`, em `DisciplinaCreate`:
```python
carga_horaria: Optional[int] = Field(None, ge=0, description="Carga horária total da disciplina")
```

### Passo 4 — Schema Pydantic de saída (a API devolve o campo)
No mesmo arquivo, em `DisciplinaResponse`:
```python
carga_horaria: Optional[int] = None
```

### Passo 5 — Service (regra de negócio, se houver)
Neste projeto o `create_disciplina` já faz `Disciplina(**disciplina_in.model_dump())`, então o novo
campo **flui automaticamente** para o banco — nada a mudar. Se a coluna exigisse cálculo/validação,
seria aqui (`app/modules/disciplinas/application/services.py`).

### Passo 6 — Router (expor no detalhe/consulta)
`app/modules/disciplinas/api/router.py`, no `GET /{id}`, incluímos a carga informada e um total com fallback:
```python
carga_total = _int(d.carga_horaria)
if carga_total is None:
    carga_total = teorica + pratica
# ... no dict de resposta:
"cargaHoraria": _int(d.carga_horaria),
"cargaHorariaTotal": carga_total,
```

### Verificação
```bash
# testes (SQLite, sem precisar de Postgres):
pytest -q
# no Swagger: POST /api/Disciplina/ com "carga_horaria": 90  ->  GET /api/Disciplina/{id} devolve cargaHoraria: 90
```
Há um teste dedicado: `tests/test_sigaa_api.py::test_disciplina_carga_horaria_persistida`.

### Resumo (o que muda em cada camada)
| Passo | Arquivo | Papel |
|------|---------|-------|
| 1 | `infrastructure/orm_models.py` | Define a coluna (fonte da verdade do schema) |
| 2 | `migrations/versions/*.py` | Aplica a mudança no banco (upgrade/downgrade) |
| 3 | `api/schemas.py` (Create) | A API passa a **aceitar** o campo |
| 4 | `api/schemas.py` (Response) | A API passa a **devolver** o campo |
| 5 | `application/services.py` | Regra/validação (aqui: automático) |
| 6 | `api/router.py` | Expõe no detalhe/consulta |

---

## 5. Como demonstrar essa alteração ao vivo (se ele pedir)

```bash
git checkout feature/exemplo-carga-horaria      # branch com a coluna de exemplo
docker compose up --build -d                     # aplica a migration no boot (alembic upgrade head)
pytest -q                                        # 8 testes verdes (inclui o da carga_horaria)
```
No Swagger:
1. `POST /api/Disciplina/` com corpo incluindo `"carga_horaria": 90`.
2. `GET /api/Disciplina/{id}` → mostra `cargaHoraria: 90` e `cargaHorariaTotal: 90`.

Para voltar ao estado entregue: `git checkout main`.

---

## 6. Comandos de referência rápida

```bash
docker compose up --build -d          # sobe tudo (db + api + kong)
docker compose logs -f api            # acompanha migration + seed + uvicorn
docker compose ps                     # status dos conteineres
docker compose down                   # derruba (mantém dados)
docker compose down -v                # derruba e ZERA o banco

alembic upgrade head                  # aplica migrations pendentes
alembic downgrade -1                  # reverte a última migration
alembic history                       # histórico de migrations
pytest -q                             # roda a suíte de testes
```
