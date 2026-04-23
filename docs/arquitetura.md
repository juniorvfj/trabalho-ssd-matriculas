# Arquitetura do Sistema de Matrícula (Monólito Modular)

O sistema foi desenhado sob o paradigma de Orientação a Serviço (SOA) e "Contract-First", consolidado em um **Monólito Modular** usando **FastAPI**.

## Por que Monólito Modular?
1. **Baixo Acoplamento, Alta Coesão**: Reduz o acoplamento de código ao separar regras de negócio de diferentes entidades (ex: Cursos vs Alunos), sem a complexidade operacional da gestão de microserviços (network falhas, orquestração Kubernetes, etc).
2. **Camadas Claras**: Cada módulo tem sua própria divisão em `api/`, `application/`, `domain/`, `infrastructure/`.
3. **Escopo Acadêmico**: É mais que suficiente para simular SOA, pois garantimos que as interações entre os módulos ocorram por meio de interfaces (serviços de aplicação/tarefas) e não acessando banco de dados diretamente de outro domínio.

## Camadas Internas de Cada Módulo

- **`api/`**: Camada de roteamento (FastAPI) e Models Pydantic de Request/Response. Só se comunica com a camada de `application`.
- **`application/`**: Regras de orquestração ("Use Cases"). Recebe dados da `api`, busca regras no `domain` e salva na `infrastructure`.
- **`domain/`**: Entidades core do negócio e regras que independem de framework. Nenhum acesso a banco acontece aqui. Regras de elegibilidade pura.
- **`infrastructure/`**: ORM SQLAlchemy (Models e Repositories). Onde o acesso ao PostgreSQL acontece efetivamente.

## Padrões de SOA e Contract-First
- Todos os endpoints respeitarão os contratos OpenAPI 3, definidos previamente e materializados via **Pydantic** e **FastAPI**.
- O modelo canônico de erro é global na API (implementado via global exception handler em `app/core/exceptions.py`).
