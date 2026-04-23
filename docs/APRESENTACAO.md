# Sistema de Matrícula de Alunos de Graduação
**Autores:** Vicente Jr., Breno Ribeiro e Rosane
**Disciplina:** Segurança em Sistemas Distribuídos
**Professor:** Ricardo Staciarini Puttini

---

## 1. O Problema e o Objetivo
Este projeto foi desenvolvido para resolver as fases críticas de matrícula e processamento acadêmico. O principal foco deste trabalho não é apenas o cadastro de alunos, mas sim **demonstrar o conhecimento em Segurança de Sistemas Distribuídos e Arquitetura Orientada a Serviços (SOA)**.

## 2. Decisões Arquiteturais

### 2.1 Monólito Modular
Foi escolhido o estilo de **Monólito Modular** com **Python 3.12** e **FastAPI**. 
- **Por que não microsserviços?** Em vez de dividir o código em pequenos servidores espalhados (o que geraria uma complexidade enorme de infraestrutura que fugiria do escopo da disciplina), optamos por dividir a aplicação internamente.
- Cada entidade do sistema (Cursos, Alunos, Disciplinas e Turmas) funciona de forma independente em suas próprias pastas, com seus próprios modelos de roteamento (APIs) e validação (Pydantic), facilitando uma futura separação para microsserviços caso necessário.

### 2.2 Contract-First e Modelos Canônicos
Todo o sistema foi construído pensando primeiramente na comunicação. Usamos o Pydantic para criar os schemas (contratos de API). Ou seja, nenhuma informação entra ou sai do banco de dados sem antes passar por uma validação estrita que define formatos (JSON), tipos de dados e limites (ex: código do curso com máximo de 10 caracteres).

## 3. Segurança Distribuída

A segurança do sistema é implementada desde a porta de entrada.
- Nenhuma rota pode ser acessada de forma anônima (com exceção do `healthcheck`).
- A aplicação exige um token **JWT (JSON Web Token)** no cabeçalho (*Authorization: Bearer <token>*).
- **Mock de Autenticação:** Como o objetivo atual é demonstrar a blindagem da API, desenvolvi um mock na rota `/auth/login` que exige a senha exata `admin` para emitir o token. Sem este token válido, o servidor bloqueia requisições com `401 Unauthorized`.

## 4. Estrutura do Banco de Dados
A persistência foi feita com **PostgreSQL** executando em contêineres Docker, e todo o esquema é gerenciado via **Alembic**. A vantagem do Alembic é que nós versionamos o banco de dados como código (Migrations). 

**Entidades Implementadas até o Momento:**
- `cursos`: Árvore base do sistema.
- `alunos`: Vinculados aos cursos, contêm informações sensíveis acadêmicas.
- `disciplinas`: Vinculadas a um curso, controlam créditos e carga horária.
- `periodos_letivos` e `turmas`: A fundação para a fase 3 (Processamento Batch) de matrículas.

## 5. Infraestrutura e Requisitos Locais

Para que a aplicação rode corretamente na máquina de qualquer pessoa, adotamos o Docker para criar um ambiente isolado e previsível.

**Stack e Versões Utilizadas:**
- **Linguagem:** Python 3.12+ (caso rode localmente com Poetry)
- **Framework Web:** FastAPI v0.111.1
- **Servidor ASGI:** Uvicorn
- **Banco de Dados:** PostgreSQL 16 (imagem Alpine via Docker)
- **Infraestrutura:** Docker Desktop (Engine v24+) e Docker Compose (v2)

**Vantagens da Abordagem:**
- O professor e os alunos não precisam instalar o PostgreSQL na própria máquina.
- Não há risco de conflito de portas ou versões de bibliotecas Python globais, pois o `docker-compose.yml` e o `Dockerfile` isolam todas as dependências em um contêiner Linux.

## 6. Como Demonstrar este Projeto

Para apresentar a aplicação aos alunos e ao professor, siga estes passos:

1. **Mostre a Inicialização (Docker):**
   Explique que toda a infraestrutura sobe em apenas um comando (`docker-compose up -d --build`). Isso demonstra portabilidade e controle de ambiente.

2. **Acesse o Swagger UI:**
   Abra o navegador em `http://localhost:8000`. Graças ao FastAPI, a documentação OpenAPI 3.0 é gerada em tempo real com base nos nossos Contratos (Pydantic). Mostre o design da interface da API.

3. **Demonstre o Bloqueio de Segurança:**
   - Tente usar a rota `GET /api/v1/cursos` diretamente (clique em *Try it out* -> *Execute*).
   - Mostre ao professor que a resposta é `401 Unauthorized`. Explique a obrigatoriedade do JWT.

4. **Faça o Login:**
   - Clique no botão verde **Authorize** (no topo à direita).
   - No campo username pode colocar qualquer coisa, mas no campo password coloque exatamente `admin`.
   - Clique em Authorize. Agora você está "logado".

5. **Execute os Serviços de Entidade (CRUD):**
   - Repita a chamada no `GET /api/v1/cursos`. Agora retornará `200 OK` (uma lista vazia `[]` se for a primeira vez).
   - Use os métodos `POST` para criar dados fictícios na ordem: Cursos -> Alunos -> Disciplinas -> Períodos Letivos -> Turmas.
   - Mostre como o sistema valida e bloqueia se você tentar enviar uma *string* no lugar de um *inteiro*.

## 7. Conclusões Parciais e Próximos Passos
O núcleo do sistema e a malha de segurança base já estão validados e funcionando conforme o planejado. A estrutura de dados já sustenta a próxima e mais complexa fase: a implementação do motor de regras de negócio em lote (Elegibilidade e Processamento Fase 3).
