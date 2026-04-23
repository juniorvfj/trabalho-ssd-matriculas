# Sistema de Matrícula - Segurança em Sistemas Distribuídos

Trabalho da disciplina Segurança em Sistemas Distribuídos (Prof. Ricardo Staciarini Puttini).
Aluno: Vicente Jr.

## Como iniciar o projeto

### Usando Docker
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
2. Inicialize os contêineres:
   ```bash
   docker-compose up -d --build
   ```
3. A API estará disponível em: `http://localhost:8000`
4. Documentação OpenAPI: `http://localhost:8000/docs`

### Rodando Localmente com Poetry
1. Instale o [Poetry](https://python-poetry.org/)
2. Instale as dependências:
   ```bash
   poetry install
   ```
3. Suba apenas o banco de dados via docker:
   ```bash
   docker-compose up -d db
   ```
4. Rode a aplicação:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
