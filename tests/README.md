# Diretrizes de Testes (Testing Guidelines)

Este diretório é reservado para a suíte de testes automatizados do sistema.
A arquitetura de testes está dividida em 3 categorias principais para garantir a qualidade do software:

## 1. Testes Unitários (`/unit`)
Focam em testar funções, classes e métodos de forma isolada.
* **O que testar:** Lógicas de cálculo de IRA, validações do Pydantic (schemas), funções utilitárias e regras de negócio puras (services) fazendo *mock* do banco de dados.
* **Ferramentas:** `pytest`, `unittest.mock`.

## 2. Testes de Integração (`/integration`)
Focam em testar a interação entre diferentes módulos do sistema, principalmente a integração com o Banco de Dados.
* **O que testar:** As queries do SQLAlchemy, checando se a gravação e leitura no PostgreSQL (via asyncpg) funcionam perfeitamente juntas.

## 3. Testes de Contrato / E2E (`/contract`)
Focam em testar a API REST como uma "caixa preta", simulando um cliente real chamando as rotas HTTP.
* **O que testar:** Os endpoints expostos pelo FastAPI (rotas). Garante que a resposta JSON tem o formato correto e o Status HTTP esperado.
* **Ferramentas:** `pytest`, `httpx.AsyncClient` (para invocar as rotas do FastAPI assincronamente).

### Dica para os alunos
Ao escrever novos testes, sempre sigam o padrão **AAA (Arrange, Act, Assert)**:
1. **Arrange (Preparar):** Configure o ambiente e crie os objetos necessários.
2. **Act (Agir):** Chame a função ou rota que deseja testar.
3. **Assert (Afirmar):** Verifique se o resultado obtido é igual ao resultado esperado.
