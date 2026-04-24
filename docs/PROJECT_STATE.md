# Estado do Projeto - Sistema de Matrícula (Trabalho SSD)

*Data/Hora de atualização: 24/04/2026 — Sessão de Vicente.*

## 1. O que foi construído até o momento?
A fundação do nosso **Monólito Modular** está consolidada e as bases de Arquitetura Orientada a Serviço (SOA) estão operando localmente via Docker:
- **Infraestrutura**: Configurada com `pyproject.toml` (Poetry, FastAPI, SQLAlchemy 2), `docker-compose.yml` e suporte a variáveis de ambiente (`.env`).
- **Automação de Banco de Dados**: PostgreSQL configurado com Alembic assíncrono. O `docker-compose` executa as migrações automaticamente (`alembic upgrade head`) na inicialização da API.
- **Camada Central e Segurança (JWT)**: Fluxo de autenticação implementado em `app/api/auth.py` (OAuth2 Password Bearer). Sistema de exceções globais padronizado (Modelo Canônico de Erro com `code`, `message` e `details`).
- **Módulos de Domínio Implementados (5 de 6)**:
  - ✅ **Alunos**: Schemas, ORM, Services, Router (GET all, GET by id, POST)
  - ✅ **Cursos**: Schemas, ORM, Services, Router (GET all, GET by id, POST)
  - ✅ **Disciplinas**: Schemas, ORM, Services, Router (GET all, GET by id, POST). Inclui pré-requisitos (M:N).
  - ✅ **Turmas**: Schemas, ORM, Services, Router (GET all, POST turma, GET/POST períodos letivos).
  - ✅ **Histórico Acadêmico**: Implementado nesta sessão. Schemas com enum de status (APROVADO, REPROVADO, TRANCADO, CURSANDO), validação de nota (0-10), ORM com FKs para aluno/disciplina/período. Router (GET all, GET by aluno_id, POST). **Pré-requisito para verificarElegibilidade.**
  - ❌ **Matrículas**: Pasta existe mas está vazia.
- **Documentação Educativa**: Todo o código possui comentários detalhados e docstrings estruturadas.
- **Testes**: Criado roteiro de orientação em `tests/README.md` (Padrão AAA).

## 2. Migrations Alembic
3 migrations aplicadas com sucesso:
1. `793f3fd0acbb` — Tabelas de cursos e alunos
2. `7b67b775421e` — Tabelas de disciplinas e turmas
3. `004401650ca4` — Tabela de históricos acadêmicos

## 3. Decisões Arquiteturais Consolidadas
- **Padronização de Contratos**: Uso estrito de Pydantic para validação de entrada/saída (DTOs).
- **Relacionamentos**: Pré-requisitos M:N em Disciplinas, Turmas vinculadas a Períodos Letivos, Histórico vinculado a Aluno/Disciplina/Período.
- **Ambiente**: `docker-compose up -d --build`. Swagger em `http://localhost:8000/docs`.

## 4. Próximos Passos Imediatos
Com 5 das 6 entidades prontas, o foco agora deve ser:

### Prioridade Alta
1. **Módulo Matrículas** — ORM (SolicitacaoMatricula, Matricula, AuditoriaProcessamento), Schemas, Services, Router com ~7 endpoints
2. **Serviço verificarElegibilidade** — Verifica currículo, aprovação prévia e pré-requisitos
3. **Processamento Batch (Fase 3)** — Ranking por IRA, validação por aluno, rejeição por vagas

### Prioridade Média
4. **Endpoints PUT** faltantes em todos os módulos
5. **Endpoint turmas disponíveis** (`GET /turmas/disponiveis?periodo=...`)
6. **Comprovante de matrícula** (`GET /alunos/{id}/comprovante-matricula`)
7. **Seed de dados** para demonstração

### Prioridade Baixa
8. **Documentação técnica** (schemas JSON, OpenAPI, ADRs, diagramas)
9. **Testes automatizados** (unitários, integração, contrato)
10. **Segurança avançada** (RBAC, CORS, logs estruturados)

*Instrução para a próxima sessão: "Leia o arquivo docs/PROJECT_STATE.md e implemente o módulo de Matrículas seguido do serviço verificarElegibilidade".*
