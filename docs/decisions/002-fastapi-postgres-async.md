# ADR 002: Escolha de FastAPI, PostgreSQL e Padrão Assíncrono

## Status
Aceito

## Contexto
O projeto requer alto desempenho na validação de regras de negócio de matrículas e no processamento em batch de milhares de solicitações simultâneas. Havia necessidade de utilizar frameworks modernos de Python e um banco de dados relacional robusto para garantir consistência ACID durante transações complexas de matrícula.

## Decisão
A stack tecnológica escolhida foi:
- **FastAPI**: Framework web pela sua velocidade, tipagem estática através do Pydantic, e geração nativa de contratos OpenAPI (Swagger), o que atende perfeitamente ao requisito de Contract-First API.
- **PostgreSQL**: Banco de dados relacional, utilizando transações assíncronas nativas.
- **SQLAlchemy (Async)** com motor **asyncpg**: Utilizado como ORM (Object-Relational Mapping). Toda a comunicação de entrada/saída com o banco de dados ocorre de forma não bloqueante (`async/await`).

## Consequências
**Positivas:**
- Alta concorrência no processamento de matrículas usando I/O assíncrono.
- A auto-documentação das rotas REST através do OpenAPI permite a fácil visualização dos contratos.
- Forte integridade transacional garantida pelo PostgreSQL.

**Negativas:**
- A curva de aprendizado do SQLAlchemy em modo assíncrono é maior, e exige cuidado na injeção de dependência das sessões (`db: AsyncSession`) e ao evitar *Lazy Loading* explícito fora do fluxo da requisição HTTP (o que exigiu o ajuste fino em testes para gerenciar *Event Loops*).
