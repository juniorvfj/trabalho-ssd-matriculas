# ADR 001: Adoção da Arquitetura de Monolito Modular

## Status
Aceito

## Contexto
O sistema de matrículas acadêmicas foi inicialmente proposto para seguir princípios de Service-Oriented Architecture (SOA). No entanto, dadas as restrições de tempo, o escopo da disciplina "Segurança de Sistemas Distribuídos", e a necessidade de uma entrega coesa que simplificasse o deployment (deploy único em um contêiner Docker), era necessário definir um estilo arquitetural que oferecesse alta manutenibilidade e baixo acoplamento sem a complexidade de infraestrutura de microsserviços.

## Decisão
Decidimos implementar o sistema seguindo a arquitetura de **Monolito Modular** com **Design Contract-First**. O código está estruturado em módulos independentes (`alunos`, `cursos`, `disciplinas`, `turmas`, `matriculas`, `usuarios`), cada um contendo suas próprias camadas de:
- `api` (Endpoints e Schemas/Contratos)
- `application` (Regras de negócio e Serviços)
- `infrastructure` (Modelos ORM e persistência)

## Consequências
**Positivas:**
- Baixo acoplamento: As regras de negócio de cada entidade são encapsuladas.
- Agilidade: Simplifica a orquestração e testes automatizados. O pipeline inteiro pode rodar em um único banco de dados.
- Escalabilidade futura: Facilita a transição para microsserviços no futuro, se necessário, já que os contratos de API (OpenAPI) e camadas lógicas já estão desacoplados.

**Negativas:**
- Não oferece escalabilidade horizontal por módulo de forma independente (por exemplo, escalar apenas o serviço de matrículas), dependendo da escalabilidade de todo o monolito.
