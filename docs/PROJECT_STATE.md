# Estado do Projeto - Sistema de Matrícula (Trabalho SSD)

*Data/Hora de salvamento de contexto: Última sessão de Vicente com o assistente (Antigravity).*

## 1. O que foi construído até o momento?
A fundação do nosso **Monólito Modular** está de pé e as bases de Arquitetura Orientada a Serviço (SOA) estão operando localmente no Docker:
- **Repositório**: Inicializado com `pyproject.toml` (Poetry, FastAPI 0.111, SQLAlchemy 2), `docker-compose.yml`, etc.
- **Camada Central e Segurança (JWT)**: Rota simulada em `app/api/auth.py` garantindo suporte seguro (OAuth2 Password Bearer) utilizando secret-key em ambiente de desenvolvimento. O framework de excessões globais também opera (ex: retorno padronizado `code`, `message`, `details`).
- **Banco de Dados (ORM)**: PostgreSQL configurado. Alembic assíncrono perfeitamente implementado. As migrações automáticas já se comunicam e as tabelas reais de `cursos` e `alunos` estão no Postgres (`alembic upgrade head`).
- **Modelagem Contract-First**:
  - `docs/schemas/`: Contém os JSON schemas canônicos com restrições claras (ex: IRA indo de 0.0 a 5.0, matrículas estritas de 9 números, limites de créditos, ID em inteiro).
  - `docs/openapi/`: Os primeiros contratos de Entidades Base.
  - O código reflete estritamente essas regras por meio de Models e Repositories (`app.modules.cursos` e `app.modules.alunos`).

## 2. Decisões Arquiteturais Consolidadas
- **Padrão de ID:** Adotamos Inteiros Sequenciais (`integer`) e descartamos UUID por simplicidade, aderindo as simulações em testes de contrato.
- **Testes Práticos:** Tudo sobe utilizando `docker-compose up -d --build`. O acesso livre ocorre na rota `http://localhost:8000/docs`, contudo, exige o token em `Authorize` digitando senha `admin`.

## 3. Próximos Passos Imediatos (Para o próximo agente iniciar)
As entidades Raiz já foram materializadas, restando:
- **Fase de Cadastros (Restante):** Implementar e modelar os mesmos passos (Schemas, ORM, API, Auth) para:
  - **Disciplina**
  - **Turma**
  - **Histórico Acadêmico**
- **Fase Crítica e Foco do Trabalho:** Criar e isolar a lógica e testes sobre `verificarElegibilidade`, as `Solicitacoes de Matricula` e os processamentos e rankings da chamada de "Fase 3" de matrícula descritos no escopo pai em `trabalho_ssd_vicente.md`.

*Instrução para a próxima sessão: "Leia o arquivo docs/PROJECT_STATE.md e a especificação trabalho_ssd_vicente.md, e inicie os trabalhos modelando os Schemas e Contract-First para Disciplina e Turma".*
