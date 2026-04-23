# trabalho_ssd_vicente.md

## 1. Contexto do trabalho

**Disciplina:** Segurança em Sistemas Distribuídos  
**Código:** PPEE2018  
**Professor:** Ricardo Staciarini Puttini  

### Objetivo geral do trabalho
Projetar e implementar serviços e aplicação usando o paradigma e tecnologia de orientação a serviço (SOA), com foco em:

- modelos de dados canônicos
- contratos de serviços padronizados
- serviços RESTful
- governança/publicação de APIs (opcional, mas desejável)
- documentação de referência da disciplina na pasta /docs caso você precise consultar ou tirar alguma dúvida.
- o projeto e as implementações devem ser documentadas (comentadas) de modo que o professor possa identificar que eu, Vicente Jr. fiz o trabalho

### Caso de negócio
Sistema de **Matrícula de Alunos de Graduação**, com foco nas fases de matrícula e processamento das solicitações.

### Entregas previstas
1. **Contratos padronizados** dos serviços de entidade  
2. **Implementação dos Web Services REST**  
3. **Publicação e governança de APIs** (API Manager)

---

## 2. Decisão tecnológica

### Linguagem escolhida
**Python 3.12**

### Framework principal
**FastAPI**

### Justificativa
A escolha por Python com FastAPI foi feita porque:
- oferece alta produtividade
- gera documentação OpenAPI 3 automaticamente
- facilita modelagem de contratos, schemas e validações
- possui boa aderência ao estilo contract-first / API-first
- simplifica a implementação de regras de negócio complexas
- integra bem com ferramentas de assistência de código

---

## 3. Stack tecnológica

### Backend
- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- SQLAlchemy 2.x
- Alembic

### Banco de dados
- PostgreSQL 16

### Testes
- Pytest
- httpx
- pytest-asyncio

### Qualidade
- Ruff
- Black
- MyPy

### Segurança
- FastAPI security utilities
- JWT para autenticação
- Passlib/Bcrypt para hashing de senhas
- controle de perfis de acesso

### Documentação e contratos
- OpenAPI 3
- JSON Schema
- Mermaid para diagramas textuais
- Markdown para documentação

### Infraestrutura local
- Docker
- Docker Compose

### Governança de APIs
Preferencialmente uma destas opções:
- Kong
- APISIX
- Tyk
- ou outra solução leve para demonstração

---

## 4. Estratégia arquitetural

## 4.1 Abordagem
Adotar **monólito modular**, e não microserviços distribuídos reais.

### Motivos
- menor complexidade operacional
- maior foco nas regras do domínio
- atende bem ao objetivo acadêmico
- permite demonstrar princípios SOA sem sobrecarga de infraestrutura

## 4.2 Princípios arquiteturais
- contract-first / API-first
- separação entre serviços de entidade e serviços de tarefa
- baixo acoplamento
- padronização de contratos
- validação forte de entrada e saída
- rastreabilidade de decisões
- segurança desde o desenho

## 4.3 Estilo interno
Arquitetura em camadas com organização por domínio:
- `api`
- `application`
- `domain`
- `infrastructure`

---

## 5. Escopo funcional

## 5.1 Entidades principais
- Aluno
- Curso
- Disciplina
- Turma
- Matrícula
- Histórico Acadêmico

## 5.2 Serviço de tarefa obrigatório
- `verificarElegibilidade`

## 5.3 Fases do negócio a contemplar
### Fase 1
Pré-matrícula automática  
**Observação:** pode ser simulada ou parcialmente representada, se o professor permitir.

### Fase 2
Confirmação da matrícula pelo aluno e solicitação de turmas adicionais.

### Fase 3
Processamento batch da matrícula:
- R1: elegibilidade
- R2: alocação por turma
- R3: alocação por aluno
- R4: rejeição por falta de vagas

### Fase 4
Rematrícula

### Fase 5
Novo processamento batch

### Fase 6
Matrícula extraordinária

### Fase 7
Comprovante de matrícula e histórico de processamento

---

## 6. Modelo de domínio inicial

## 6.1 Curso
Campos sugeridos:
- id
- codigo
- nome
- ativo

## 6.2 Aluno
Campos sugeridos:
- id
- matricula
- nome
- email
- data_admissao
- ira
- limite_creditos_periodo
- curso_id
- ativo

## 6.3 Disciplina
Campos sugeridos:
- id
- codigo
- nome
- creditos
- carga_horaria
- curso_id
- ativa

## 6.4 DisciplinaPrerequisito
Campos sugeridos:
- id
- disciplina_id
- prerequisito_id

## 6.5 PeriodoLetivo
Campos sugeridos:
- id
- codigo
- descricao
- data_inicio
- data_fim
- ativo

## 6.6 Turma
Campos sugeridos:
- id
- disciplina_id
- periodo_letivo_id
- codigo_turma
- vagas_totais
- vagas_ocupadas
- horario_serializado
- ativa

## 6.7 Professor
Campos sugeridos:
- id
- nome
- email

## 6.8 TurmaProfessor
Campos sugeridos:
- id
- turma_id
- professor_id

## 6.9 HistoricoAcademico
Campos sugeridos:
- id
- aluno_id
- disciplina_id
- periodo_letivo_id
- status
- nota_final
- aprovado

## 6.10 SolicitacaoMatricula
Campos sugeridos:
- id
- aluno_id
- turma_id
- prioridade
- fase
- status
- resultado
- timestamp_solicitacao

## 6.11 Matricula
Campos sugeridos:
- id
- aluno_id
- turma_id
- periodo_letivo_id
- status
- origem
- data_efetivacao

## 6.12 AuditoriaProcessamento
Campos sugeridos:
- id
- aluno_id
- turma_id
- fase
- regra_aplicada
- decisao
- mensagem
- timestamp_evento

---

## 7. Regras de negócio prioritárias

## 7.1 Elegibilidade
Uma solicitação só é elegível se:
- a disciplina pertence ao currículo do curso do aluno
- o aluno ainda não foi aprovado nela
- o aluno possui todos os pré-requisitos

## 7.2 Ordenação por turma
As solicitações elegíveis de uma turma devem ser ordenadas por:
1. maior IRA
2. data de admissão mais antiga
3. desempate aleatório

## 7.3 Regras por aluno
Para cada solicitação, rejeitar quando:
- exceder o limite máximo de créditos no período
- o aluno já estiver matriculado na disciplina no período
- houver conflito de horário com turma já matriculada

## 7.4 Rejeição final
Solicitações restantes após o processamento devem ser rejeitadas por indisponibilidade de vagas.

## 7.5 Matrícula extraordinária
Processamento imediato, sem concorrência por prioridade entre alunos.

---

## 8. Serviços e contratos

## 8.1 Serviços de entidade
Devem existir contratos OpenAPI para:

- Aluno
- Curso
- Disciplina
- Turma
- Matrícula
- Histórico Acadêmico

## 8.2 Serviço de tarefa
- verificarElegibilidade

## 8.3 Endpoints sugeridos

### Curso
- `GET /api/v1/cursos`
- `GET /api/v1/cursos/{curso_id}`
- `POST /api/v1/cursos`
- `PUT /api/v1/cursos/{curso_id}`

### Aluno
- `GET /api/v1/alunos`
- `GET /api/v1/alunos/{aluno_id}`
- `POST /api/v1/alunos`
- `PUT /api/v1/alunos/{aluno_id}`

### Disciplina
- `GET /api/v1/disciplinas`
- `GET /api/v1/disciplinas/{disciplina_id}`
- `POST /api/v1/disciplinas`
- `PUT /api/v1/disciplinas/{disciplina_id}`

### Turma
- `GET /api/v1/turmas`
- `GET /api/v1/turmas/{turma_id}`
- `POST /api/v1/turmas`
- `PUT /api/v1/turmas/{turma_id}`
- `GET /api/v1/turmas/disponiveis?periodo=2026.1`

### Matrícula
- `GET /api/v1/matriculas`
- `GET /api/v1/matriculas/{matricula_id}`
- `POST /api/v1/matriculas/solicitacoes`
- `POST /api/v1/matriculas/processamento/fase-3`
- `POST /api/v1/matriculas/processamento/fase-5`
- `POST /api/v1/matriculas/extraordinaria`
- `DELETE /api/v1/matriculas/{matricula_id}`

### Histórico acadêmico
- `GET /api/v1/historicos/{aluno_id}`

### Serviço de tarefa
- `POST /api/v1/tarefas/verificar-elegibilidade`

### Comprovante
- `GET /api/v1/alunos/{aluno_id}/comprovante-matricula`

### Auditoria
- `GET /api/v1/alunos/{aluno_id}/historico-processamento`

---

## 9. Modelos canônicos

Todos os contratos devem utilizar modelos canônicos padronizados.

## 9.1 Padrões gerais
- UUID ou inteiro consistente por toda a API
- datas em ISO 8601
- nomes de campos em `snake_case` no backend e `camelCase` apenas se houver decisão explícita
- mensagens de erro padronizadas
- paginação consistente
- envelopes de resposta padronizados quando necessário

## 9.2 Schemas canônicos obrigatórios
Criar schemas separados para:
- curso
- aluno
- disciplina
- turma
- matricula
- historico_academico
- solicitacao_matricula
- elegibilidade_resultado
- erro_api

## 9.3 Exemplo de padrão de erro
```json
{
  "code": "ALUNO_SEM_PREREQUISITO",
  "message": "Aluno não possui todos os pré-requisitos da disciplina.",
  "details": {
    "aluno_id": 10,
    "disciplina_id": 20
  }
}
```

---

## 10. Segurança

## 10.1 Objetivos mínimos
- autenticação
- autorização por papel
- validação de entrada
- tratamento seguro de erros
- logs de auditoria
- proteção de rotas administrativas

## 10.2 Papéis sugeridos
- `ADMIN`
- `ALUNO`
- `COORDENACAO`
- `PROCESSAMENTO`

## 10.3 Regras de acesso sugeridas
- aluno consulta apenas suas próprias informações sensíveis
- administração gerencia cadastros
- processamento executa rotinas batch
- auditoria registra operações sensíveis

## 10.4 Controles desejáveis
- JWT com expiração curta
- hashing de senha
- CORS controlado
- rate limiting no gateway
- logs estruturados
- mascaramento de erros internos

---

## 11. Estrutura do repositório

```text
ssd_vicente-matricula/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ security.py
│  │  ├─ database.py
│  │  ├─ logging.py
│  │  └─ exceptions.py
│  ├─ shared/
│  │  ├─ schemas/
│  │  ├─ enums/
│  │  ├─ utils/
│  │  └─ responses/
│  ├─ modules/
│  │  ├─ cursos/
│  │  │  ├─ api/
│  │  │  ├─ application/
│  │  │  ├─ domain/
│  │  │  └─ infrastructure/
│  │  ├─ alunos/
│  │  ├─ disciplinas/
│  │  ├─ turmas/
│  │  ├─ matriculas/
│  │  ├─ historicos/
│  │  ├─ elegibilidade/
│  │  └─ processamento/
│  └─ workers/
│     └─ batch_processor.py
├─ docs/
│  ├─ openapi/
│  ├─ schemas/
│  ├─ diagrams/
│  ├─ decisions/
│  └─ apim/
├─ migrations/
├─ scripts/
│  ├─ seed.py
│  ├─ import_sigaa.py
│  └─ run_batch.py
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ contract/
├─ docker/
├─ .env.example
├─ docker-compose.yml
├─ pyproject.toml
├─ README.md
└─ trabalho_essd.md
```

---

## 12. Organização interna dos módulos

Cada módulo deve seguir aproximadamente esta estrutura:

```text
modules/alunos/
├─ api/
│  ├─ router.py
│  ├─ request_models.py
│  └─ response_models.py
├─ application/
│  ├─ services.py
│  └─ use_cases.py
├─ domain/
│  ├─ entities.py
│  ├─ rules.py
│  └─ repository_interfaces.py
└─ infrastructure/
   ├─ orm_models.py
   ├─ repositories.py
   └─ mappers.py
```

---

## 13. Estratégia de implementação

## 13.1 Fase 0 - Preparação
- criar repositório
- configurar ambiente
- definir padrão de branches
- subir banco local
- configurar FastAPI
- configurar lint, format e testes

## 13.2 Fase 1 - Contratos e modelos
- definir modelo canônico das entidades
- escrever JSON Schemas
- consolidar contratos OpenAPI
- revisar nomes, tipos e padrões de erro

## 13.3 Fase 2 - Persistência e cadastros
- modelagem relacional
- migrations
- seeds
- CRUD básico dos serviços de entidade

## 13.4 Fase 3 - Regras de negócio
- verificar elegibilidade
- matrícula e solicitação
- conflito de horário
- limite de créditos
- validação de currículo

## 13.5 Fase 4 - Processamento batch
- ordenação por turma
- avaliação por aluno
- rejeições com motivo
- auditoria do processamento

## 13.6 Fase 5 - Segurança e governança
- autenticação
- autorização
- gateway ou API manager
- publicação de APIs

## 13.7 Fase 6 - Finalização
- testes de integração
- documentação
- roteiro de apresentação
- refinamento visual da API docs

---

## 14. Backlog sugerido

## 14.1 Épico A - Fundação do projeto
- inicializar projeto FastAPI
- configurar SQLAlchemy
- configurar Alembic
- configurar Docker Compose
- configurar Ruff, Black, MyPy e Pytest

## 14.2 Épico B - Domínio acadêmico
- modelar curso
- modelar aluno
- modelar disciplina
- modelar turma
- modelar histórico
- modelar matrícula e solicitação

## 14.3 Épico C - Contratos
- criar OpenAPI Aluno
- criar OpenAPI Curso
- criar OpenAPI Disciplina
- criar OpenAPI Turma
- criar OpenAPI Matrícula
- criar OpenAPI Histórico
- criar contrato do serviço verificarElegibilidade

## 14.4 Épico D - Regras
- validar pré-requisitos
- validar aprovação prévia
- validar disciplina no currículo
- validar conflito de horários
- validar limite de créditos

## 14.5 Épico E - Processamento
- implementar ranking por turma
- implementar ranking por aluno
- implementar rejeição final
- registrar trilha de auditoria

## 14.6 Épico F - Segurança
- login
- emissão de token
- proteção por perfil
- trilha de auditoria
- tratamento de erro padronizado

## 14.7 Épico G - Governança
- publicar APIs
- documentar versionamento
- documentar políticas básicas
- demonstrar uso com gateway

---

## 15. Critérios de pronto

Uma funcionalidade só é considerada pronta quando:
- possui contrato definido
- possui validação de entrada
- possui resposta padronizada
- possui teste unitário ou de integração
- possui tratamento de erro
- está documentada
- passou no lint/format

---

## 16. Testes

## 16.1 Testes unitários
Cobrir:
- elegibilidade
- pré-requisitos
- conflito de horário
- limite de créditos
- ordenação por IRA
- desempate

## 16.2 Testes de integração
Cobrir:
- criação de entidades
- solicitação de matrícula
- processamento batch
- matrícula extraordinária
- emissão de comprovante

## 16.3 Testes de contrato
Garantir aderência das respostas ao OpenAPI definido.

---

## 17. Dados de exemplo

Criar massa inicial de dados contendo:
- 2 ou 3 cursos
- 10 a 20 disciplinas
- pré-requisitos entre algumas disciplinas
- 20 alunos
- 10 turmas
- históricos variados
- casos de:
  - aluno elegível
  - aluno sem pré-requisito
  - aluno já aprovado
  - aluno com conflito de horário
  - aluno acima do limite de créditos
  - turma sem vagas

---

## 18. Documentação obrigatória

A pasta `docs/` deve conter:

### `docs/openapi/`
Contratos OpenAPI separados por serviço.

### `docs/schemas/`
Modelos canônicos em JSON Schema.

### `docs/diagrams/`
- diagrama de contexto
- diagrama de módulos
- diagrama do fluxo de processamento da matrícula
- diagrama da verificação de elegibilidade

### `docs/decisions/`
ADRs, por exemplo:
- ADR-001 - escolha por Python/FastAPI
- ADR-002 - escolha por monólito modular
- ADR-003 - estratégia de autenticação JWT

### `docs/apim/`
Material da publicação/governança de APIs.

---

## 19. Roteiro de apresentação final

A apresentação deve demonstrar:
1. problema e objetivo do trabalho
2. arquitetura escolhida
3. contratos OpenAPI
4. entidades e modelo canônico
5. serviço de tarefa verificarElegibilidade
6. fluxo de solicitação de matrícula
7. processamento batch
8. controles de segurança
9. publicação/governança de APIs
10. conclusões e limitações

---

## 20. Limitações assumidas

Para manter o escopo viável, assumir:
- autenticação simplificada
- integração com SIGAA apenas simulada ou via base local espelhada
- batch executado manualmente por endpoint ou script
- foco nas regras principais do enunciado, e não em todo o universo acadêmico real

---

## 21. Prompt-base para o Google Antigravity

Use as instruções abaixo como contexto principal do agente:

### Papel
Você é um agente de engenharia de software responsável por planejar, especificar e implementar um sistema acadêmico de matrícula usando Python com FastAPI, seguindo princípios de SOA, contratos padronizados e boas práticas de segurança em sistemas distribuídos.

### Objetivo
Construir um projeto chamado `ssd_vicente-matricula` que implemente:
- serviços de entidade: Aluno, Curso, Disciplina, Turma, Matrícula e Histórico Acadêmico
- serviço de tarefa: verificarElegibilidade
- contratos OpenAPI 3
- modelos canônicos JSON Schema
- regras de negócio de matrícula por fases
- autenticação/autorização básicas
- documentação e testes

### Restrições
- usar Python 3.12
- usar FastAPI
- usar PostgreSQL
- usar SQLAlchemy 2
- usar Alembic
- usar Pytest
- manter arquitetura de monólito modular
- priorizar contract-first
- criar documentação em Markdown
- usar nomenclatura consistente
- registrar decisões arquiteturais
- não introduzir complexidade desnecessária de microserviços

### Diretrizes de implementação
- começar pelos contratos OpenAPI e schemas canônicos
- depois implementar entidades e persistência
- depois implementar regras de elegibilidade e processamento
- depois segurança e governança
- criar código limpo, modular e testável
- sempre propor testes junto da implementação
- manter compatibilidade entre contratos e responses
- usar mensagens de erro padronizadas

### Resultado esperado
Entregar uma base de projeto funcional, organizada e pronta para evolução acadêmica, com foco em clareza arquitetural, aderência ao enunciado e demonstração de conceitos de SOA e segurança distribuída.

---

## 22. Tarefas iniciais recomendadas para o Antigravity

1. Criar a estrutura de diretórios do projeto  
2. Gerar `pyproject.toml` com dependências principais  
3. Criar `docker-compose.yml` com app + postgres  
4. Criar `app/main.py` com bootstrap FastAPI  
5. Criar configuração central em `app/core/config.py`  
6. Definir schemas canônicos iniciais  
7. Escrever contratos OpenAPI dos serviços de entidade  
8. Implementar módulo `alunos`  
9. Implementar módulo `cursos`  
10. Implementar módulo `disciplinas`  
11. Implementar módulo `turmas`  
12. Implementar serviço `verificarElegibilidade`  
13. Implementar processamento batch da fase 3  
14. Criar testes principais  
15. Documentar arquitetura

---

## 23. Tarefas imediatas para primeira sprint

### Sprint 1
- bootstrap do projeto
- banco de dados
- migrations iniciais
- entidades principais
- schemas Pydantic
- rotas básicas de leitura
- OpenAPI inicial

### Meta da sprint
Ter uma aplicação FastAPI subindo localmente, conectada ao banco e com endpoints básicos de leitura para Curso, Aluno, Disciplina e Turma, além da documentação automática funcionando.

---

## 24. Definição de sucesso

O projeto será considerado bem-sucedido se:
- refletir corretamente o enunciado do trabalho
- demonstrar separação entre serviços de entidade e tarefa
- possuir contratos padronizados
- implementar as principais regras da matrícula
- incluir aspectos visíveis de segurança
- estar organizado o suficiente para demonstração acadêmica e evolução incremental
