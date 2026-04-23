# Estado do Projeto - Sistema de Matrícula (Trabalho SSD)

*Data/Hora de atualização: Última revisão técnica de Vicente.*

## 1. O que foi construído até o momento?
A fundação do nosso **Monólito Modular** está consolidada e as bases de Arquitetura Orientada a Serviço (SOA) estão operando localmente via Docker:
- **Infraestrutura**: Configurada com `pyproject.toml` (Poetry, FastAPI, SQLAlchemy 2), `docker-compose.yml` e suporte a variáveis de ambiente (`.env`).
- **Automação de Banco de Dados**: PostgreSQL configurado com Alembic assíncrono. O `docker-compose` foi atualizado para executar as migrações automaticamente (`alembic upgrade head`) na inicialização da API, garantindo que as tabelas estejam sempre prontas.
- **Camada Central e Segurança (JWT)**: Fluxo de autenticação robusto implementado em `app/api/auth.py` (OAuth2 Password Bearer). Sistema de exceções globais padronizado (Modelo Canônico de Erro com `code`, `message` e `details`).
- **Módulos de Domínio Implementados**:
  - **Alunos & Cursos**: Modelagem completa de schemas, ORM e serviços.
  - **Disciplinas & Turmas**: Recentemente concluídos. Incluem suporte a pré-requisitos (M:N em Disciplinas) e controle de oferta semestral.
- **Documentação Educativa**: Todo o código foi revisado e recebeu comentários detalhados e docstrings estruturadas, visando facilitar a avaliação docente e o estudo dos padrões (Injeção de Dependência, Camadas, ORM).
- **Testes**: Criado roteiro de orientação em `tests/README.md` definindo os padrões de testes Unitários, Integração e de Contrato (Padrão AAA).

## 2. Decisões Arquiteturais Consolidadas
- **Padronização de Contratos**: Uso estrito de Pydantic para validação de entrada/saída (DTOs), garantindo que a API siga os modelos canônicos definidos em `docs/schemas/`.
- **Relacionamentos**: Implementada lógica de pré-requisitos para disciplinas e vínculo de turmas a períodos letivos específicos.
- **Ambiente**: O projeto é agnóstico ao host, rodando inteiramente via `docker-compose up -d --build`. A documentação Swagger está ativa em `http://localhost:8000/docs`.

## 3. Próximos Passos Imediatos
Com as entidades base (Alunos, Cursos, Disciplinas, Turmas) prontas, o foco agora deve ser:
- **Histórico Acadêmico**: Implementar o módulo para registrar o desempenho passado dos alunos (necessário para validação de elegibilidade).
- **Lógica de Matrícula (Fase Crítica)**: 
  - Implementar o serviço de tarefa `verificarElegibilidade`.
  - Desenvolver o fluxo de `Solicitacoes de Matricula`.
  - Implementar os algoritmos de processamento batch (Fase 3), incluindo rankings por IRA e desempates conforme as regras de negócio.

*Instrução para a próxima sessão: "Revisar os schemas de Histórico Acadêmico e iniciar a implementação do módulo de Matrículas e Processamento Batch".*
